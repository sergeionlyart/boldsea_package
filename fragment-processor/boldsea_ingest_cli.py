#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boldsea KG Ingest CLI
=====================

Назначение
----------
CLI-скрипт, который получает JSON с фрагментами текста, извлекает из них
структурированные значения согласно указанным семантическим схемам и заносит
их в событийно-семантический граф Boldsea через REST API.

Возможности
-----------
- Создание индивида документа (Model Document) и установка атрибута `title`.
- Обработка фрагментов: создание индивидов (Concept: Fragment) по конкретным моделям
  (например, Definition, Comparison и т.д.), установка базовых атрибутов (text, fragment_anchor, confidence),
  привязка к документу (relation: document).
- Извлечение значений полей по схеме:
  * режим LLM (провайдер: openai) — JSON-ответ в строгом формате;
  * режим "rules" — наивные правила/заглушки (для отладки без LLM).
- Обеспечение наличия терминов (Concept: Term, Model: Model Term) и установка
  семантических связей фрагмента к терминам согласно схеме.
- Создание темпоральной последовательности через relation: previous между "первичными" фрагментами.
- Ведение локального реестра id (hash) индивидов в файле (чтобы повторно не создавать термины/документы),
  формат JSON: { "<Concept>|<label>": "<#hash>", ... }.
- Dry-run режим (ничего не пишет в API, лишь показывает план действий).
- Ретраи на сетевые/временные ошибки, таймауты.

Требования
----------
- Python 3.9+
- pip install requests openai (если используется провайдер openai)
- Переменная окружения OPENAI_API_KEY (для провайдера openai)
- (опционально) переменная BOLDSEA_API_TOKEN (если сервер требует авторизации Bearer)

Пример запуска
--------------
python boldsea_ingest_cli.py \
  --input ./fragments.json \
  --document-title "Boldsea Specification" \
  --registry ./boldsea_registry.json \
  --provider openai --model gpt-4o-mini \
  --api-url https://srv.boldsea.top/api/v1/semantic \
  --verbose

Формат входного файла
---------------------
{
  "fragments": [
    { "fragment_id": 1, "schema": ["Definition"], "text": "..." },
    { "fragment_id": 2, "schema": ["Architectural Component"], "text": "..." },
    { "fragment_id": 3, "schema": ["Comparison"], "text": "..." }
  ]
}



python boldsea_ingest_cli.py \
  --input ./fragments.json \
  --document-title "Boldsea Specification" \
  --registry ./boldsea_registry.json \
  --api-url https://srv.boldsea.top/api/v1/semantic \
  --provider openai --model gpt-4o-mini \
  --verbose

"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import time
import logging
import traceback

import requests

# --------- Утилиты -----------------------------------------------------------------


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9\-._:]", "", value)
    return value[:160]


def is_truthy(v: Optional[str]) -> bool:
    if v is None:
        return False
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}


# --- Валидация Boldsea-хэша ---
def is_boldsea_hash(value: Optional[str]) -> bool:
    """Проверка, что строка выглядит как валидный Boldsea-хэш (например, "#2aa5...")."""
    if not isinstance(value, str):
        return False
    return re.fullmatch(r"#[0-9a-f]{40}", value) is not None


# --------- Модели данных -----------------------------------------------------------


@dataclass
class FieldSpec:
    """Описание одного поля извлечения из схемы."""
    name: str
    kind: str  # "relation" | "attribute" | "setrange"
    datatype: Optional[str] = None  # "Term" | "EnumType" | None
    multiple: bool = False
    set_range_refs: Optional[List[str]] = None  # e.g. ["target", "comparator"]


@dataclass
class SchemaDefinition:
    name: str  # "Definition"
    model_identifier: str  # тот же, что name в большинстве случаев
    llm_prompt_template: str
    # "extraction_fields" в исходнике задан как JSON-строка с пометками Range/Multiple/SetRange
    extraction_fields_raw: str

    def parse_fields(self) -> Dict[str, FieldSpec]:
        """Парсит extraction_fields_raw в структуру FieldSpec."""
        try:
            raw = json.loads(self.extraction_fields_raw)
        except Exception as e:
            raise ValueError(f"Invalid extraction_fields JSON for schema '{self.name}': {e}")

        fields: Dict[str, FieldSpec] = {}
        for fname, desc in raw.items():
            desc_s = str(desc)

            # По умолчанию атрибут одиночный
            kind = "attribute"
            datatype = None
            multiple = False
            set_range_refs: Optional[List[str]] = None

            # Heuristics:
            if "SetRange" in desc_s:
                # Пример: "SetRange: [target, comparator]"
                kind = "setrange"
                m = re.search(r"SetRange\s*:\s*\[([^\]]+)\]", desc_s)
                if m:
                    set_range_refs = [x.strip() for x in m.group(1).split(",")]
                else:
                    set_range_refs = []
            elif "Range:" in desc_s:
                # Пример: "Range: Term, Multiple: 1"
                kind = "relation"
                m = re.search(r"Range\s*:\s*([A-Za-z]+)", desc_s)
                if m:
                    datatype = m.group(1).strip()
                if "Multiple" in desc_s:
                    mm = re.search(r"Multiple\s*:\s*1", desc_s)
                    multiple = bool(mm)
            elif "DataType:" in desc_s:
                # Пример: "DataType: EnumType"
                kind = "attribute"
                m = re.search(r"DataType\s*:\s*([A-Za-z]+)", desc_s)
                if m:
                    datatype = m.group(1).strip()

            fields[fname] = FieldSpec(
                name=fname, kind=kind, datatype=datatype, multiple=multiple, set_range_refs=set_range_refs
            )
        return fields


# --------- Реестр схем (шаблоны LLM-подсказок и поля) ------------------------------

# Взято из предоставленного словаря "Schema Instruction".
# Если нужно — можно расширить список.
SCHEMA_REGISTRY: Dict[str, SchemaDefinition] = {
    "Definition": SchemaDefinition(
        name="Definition",
        model_identifier="Definition",
        llm_prompt_template="Извлеки из определения: term (определяемый термин), includes (термины, упомянутые в определении)",
        extraction_fields_raw='{"term": "Range: Term", "includes": "Range: Term, Multiple: 1"}',
    ),
    "Comparison": SchemaDefinition(
        name="Comparison",
        model_identifier="Comparison",
        llm_prompt_template=(
            "Извлеки из сравнения: target (основной объект сравнения), comparator (с чем сравнивается), "
            "criterion (критерии сравнения), advantage (у кого преимущество по каждому критерию)"
        ),
        extraction_fields_raw=(
            '{"target":"Range: Term","comparator":"Range: Term","criterion":"Range: Term, Multiple: 1",'
            '"advantage":"SetRange: [target, comparator]"}'
        ),
    ),
    "Causal Relation": SchemaDefinition(
        name="Causal Relation",
        model_identifier="Causal Relation",
        llm_prompt_template="Извлеки причинно-следственные связи: cause (причины, факторы влияния), effect (следствия, результаты)",
        extraction_fields_raw='{"cause":"Range: Term, Multiple: 1","effect":"Range: Term, Multiple: 1"}',
    ),
    "Application Context": SchemaDefinition(
        name="Application Context",
        model_identifier="Application Context",
        llm_prompt_template="Извлеки контекст применения: domain (область применения)",
        extraction_fields_raw='{"domain":"Range: Term, Multiple: 1"}',
    ),
    "Example": SchemaDefinition(
        name="Example",
        model_identifier="Example",
        llm_prompt_template=(
            "Извлеки из примера: illustrates (что иллюстрирует), type (тип примера: code/scenario/analogy/counter-example)"
        ),
        extraction_fields_raw='{"illustrates":"Range: Term, Multiple: 1","type":"DataType: EnumType"}',
    ),
    "Architectural Component": SchemaDefinition(
        name="Architectural Component",
        model_identifier="Architectural Component",
        llm_prompt_template=(
            "Извлеки компонент системы: system_terms (к какой системе относится), purpose_terms (назначение), "
            "interfaces_terms (с чем взаимодействует), pattern_terms (архитектурные паттерны)"
        ),
        extraction_fields_raw=(
            '{"system_terms":"Range: Term, Multiple: 1","purpose_terms":"Range: Term, Multiple: 1",'
            '"interfaces_terms":"Range: Term, Multiple: 1","pattern_terms":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Technical Process": SchemaDefinition(
        name="Technical Process",
        model_identifier="Technical Process",
        llm_prompt_template=(
            "Извлеки технический процесс: input_types (типы входных данных), output_types (типы выходных данных), "
            "process_category (категория процесса), involves_components (задействованные компоненты)"
        ),
        extraction_fields_raw=(
            '{"input_types":"Range: Term, Multiple: 1","output_types":"Range: Term, Multiple: 1",'
            '"process_category":"Range: Term","involves_components":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Algorithm": SchemaDefinition(
        name="Algorithm",
        model_identifier="Algorithm",
        llm_prompt_template=(
            "Извлеки алгоритм: input_types (типы входных данных), output_types (результаты), "
            "involves_components (используемые концепты), process_category (тип алгоритма)"
        ),
        extraction_fields_raw=(
            '{"input_types":"Range: Term, Multiple: 1","output_types":"Range: Term, Multiple: 1",'
            '"involves_components":"Range: Term, Multiple: 1","process_category":"Range: Term"}'
        ),
    ),
    "Conceptual Model": SchemaDefinition(
        name="Conceptual Model",
        model_identifier="Conceptual Model",
        llm_prompt_template="Извлеки концептуальную модель: target (центральный концепт), involves_components (связанные концепты)",
        extraction_fields_raw='{"target":"Range: Term","involves_components":"Range: Term, Multiple: 1"}',
    ),
    "Principle": SchemaDefinition(
        name="Principle",
        model_identifier="Principle",
        llm_prompt_template=(
            "Извлеки принцип: target (принцип/подход), domain (к чему применяется), comparator (с чем контрастирует), "
            "demonstrates (что обеспечивает)"
        ),
        extraction_fields_raw=(
            '{"target":"Range: Term","domain":"Range: Term, Multiple: 1",'
            '"comparator":"Range: Term, Multiple: 1","demonstrates":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Problem Solution": SchemaDefinition(
        name="Problem Solution",
        model_identifier="Problem Solution",
        llm_prompt_template=(
            "Извлеки проблему и решение: problem_domain (область проблемы), solution_components (компоненты решения)"
        ),
        extraction_fields_raw=(
            '{"problem_domain":"Range: Term, Multiple: 1","solution_components":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Limitations And Challenges": SchemaDefinition(
        name="Limitations And Challenges",
        model_identifier="Limitations And Challenges",
        llm_prompt_template=(
            "Извлеки ограничения: target (к чему относится), problem_domain (тип ограничения/проблемы)"
        ),
        extraction_fields_raw='{"target":"Range: Term","problem_domain":"Range: Term, Multiple: 1"}',
    ),
    "Functionality": SchemaDefinition(
        name="Functionality",
        model_identifier="Functionality",
        llm_prompt_template=(
            "Извлеки функциональность: system_terms (система/компонент), purpose_terms (функции), involves_components (зависимости)"
        ),
        extraction_fields_raw=(
            '{"system_terms":"Range: Term","purpose_terms":"Range: Term, Multiple: 1",'
            '"involves_components":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Capabilities": SchemaDefinition(
        name="Capabilities",
        model_identifier="Capabilities",
        llm_prompt_template=(
            "Извлеки возможности: target (что обладает возможностями), purpose_terms (типы возможностей), "
            "demonstrates (какие сценарии обеспечивает)"
        ),
        extraction_fields_raw=(
            '{"target":"Range: Term","purpose_terms":"Range: Term, Multiple: 1","demonstrates":"Range: Term, Multiple: 1"}'
        ),
    ),
    "System Integration": SchemaDefinition(
        name="System Integration",
        model_identifier="System Integration",
        llm_prompt_template=(
            "Извлеки интеграцию: target (основная система), comparator (интегрируемая система), "
            "interfaces_terms (точки интеграции), process_category (метод интеграции)"
        ),
        extraction_fields_raw=(
            '{"target":"Range: Term","comparator":"Range: Term","interfaces_terms":"Range: Term, Multiple: 1",'
            '"process_category":"Range: Term"}'
        ),
    ),
    "Component Interaction": SchemaDefinition(
        name="Component Interaction",
        model_identifier="Component Interaction",
        llm_prompt_template=(
            "Извлеки взаимодействие: target (инициатор), comparator (цель взаимодействия), "
            "process_category (тип взаимодействия), involves_components (посредники)"
        ),
        extraction_fields_raw=(
            '{"target":"Range: Term","comparator":"Range: Term","process_category":"Range: Term",'
            '"involves_components":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Use Case": SchemaDefinition(
        name="Use Case",
        model_identifier="Use Case",
        llm_prompt_template="Извлеки сценарий: domain (предметная область), actors (участники), demonstrates (что демонстрирует)",
        extraction_fields_raw=(
            '{"domain":"Range: Term","actors":"Range: Term, Multiple: 1","demonstrates":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Concept Implementation": SchemaDefinition(
        name="Concept Implementation",
        model_identifier="Concept Implementation",
        llm_prompt_template=(
            "Извлеки реализацию: concept_ref (реализуемый концепт), technologies (используемые технологии), "
            "key_features (ключевые особенности)"
        ),
        extraction_fields_raw=(
            '{"concept_ref":"Range: Term","technologies":"Range: Term, Multiple: 1","key_features":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Code Snippet": SchemaDefinition(
        name="Code Snippet",
        model_identifier="Code Snippet",
        llm_prompt_template=(
            "Extract only if fragment contains actual code/script/grammar. Извлеки код: language (язык программирования/формат), "
            "illustrates (что демонстрирует), input_types (входные параметры), output_types (выходные значения), keywords (ключевые термины)"
        ),
        extraction_fields_raw=(
            '{"language":"Range: Term","illustrates":"Range: Term, Multiple: 1","input_types":"Range: Term, Multiple: 1",'
            '"output_types":"Range: Term, Multiple: 1","keywords":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Enumeration": SchemaDefinition(
        name="Enumeration",
        model_identifier="Enumeration",
        llm_prompt_template=(
            "Extract only if fragment is a clear list/enumeration. Извлеки список: category (тип/тема списка), "
            "items (элементы списка как термины), keywords (ключевые термины)"
        ),
        extraction_fields_raw=(
            '{"category":"Range: Term","items":"Range: Term, Multiple: 1","keywords":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Table Analysis": SchemaDefinition(
        name="Table Analysis",
        model_identifier="Table Analysis",
        llm_prompt_template=(
            "Extract only if fragment contains structured table/matrix. Извлеки таблицу: rows (строки как термины), "
            "columns (столбцы как термины), values (значения на пересечениях), keywords (ключевые термины)"
        ),
        extraction_fields_raw=(
            '{"rows":"Range: Term, Multiple: 1","columns":"Range: Term, Multiple: 1","values":"Range: Term, Multiple: 1",'
            '"keywords":"Range: Term, Multiple: 1"}'
        ),
    ),
    "Advantage Disadvantage": SchemaDefinition(
        name="Advantage Disadvantage",
        model_identifier="Advantage Disadvantage",
        llm_prompt_template=(
            "Extract only if fragment clearly lists pros/cons. Извлеки: target (объект анализа), "
            "advantages (преимущества как термины), disadvantages (недостатки как термины), keywords (ключевые термины)"
        ),
        extraction_fields_raw=(
            '{"target":"Range: Term","advantages":"Range: Term, Multiple: 1","disadvantages":"Range: Term, Multiple: 1",'
            '"keywords":"Range: Term, Multiple: 1"}'
        ),
    ),
}


# --------- Клиент Boldsea API ------------------------------------------------------


class BoldseaClient:
    def __init__(self, api_url: str, auth_token: Optional[str] = None, timeout: int = 20, retries: int = 3):
        self.api_url = api_url.rstrip("/")
        self.session = requests.Session()
        self.timeout = timeout
        self.retries = retries
        self.headers = {"Content-Type": "application/json"}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"

    def _request(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        last_err = None
        for attempt in range(1, self.retries + 1):
            try:
                resp = self.session.request(
                    method=method.upper(),
                    url=self.api_url,
                    headers=self.headers,
                    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                    timeout=self.timeout,
                )
                if resp.status_code >= 400:
                    # Пытаемся прочитать сообщение об ошибке
                    try:
                        data = resp.json()
                    except Exception:
                        data = {"error": resp.text}
                    raise RuntimeError(f"HTTP {resp.status_code}: {data}")
                return resp.json()
            except Exception as e:
                last_err = e
                if attempt < self.retries:
                    time.sleep(0.8 * attempt)
                else:
                    raise
        # теоретически недостижимо
        raise RuntimeError(f"Request failed: {last_err}")

    # --- High-level API ---

    def create_individual(self, concept: str, individual_label: str, model: str) -> str:
        payload = {"Concept": concept, "Individual": individual_label, "Model": model}
        data = self._request("POST", payload)
        result = data.get("result", [])
        if not result:
            raise RuntimeError(f"Empty result for create_individual: {data}")
        return result[0]["id"]

    def set_property(self, individual_hash: str, prop: str, value: Any) -> Dict[str, Any]:
        payload = {"Individual": individual_hash, "Property": prop, "Value": value}
        return self._request("PUT", payload)


# --------- Реестр ID (локальный файл) ---------------------------------------------


class IdRegistry:
    """
    Простое key->hash хранилище.
    Ключ рекомендуем формировать как "<Concept>|<Label>"  (например, "Term|boldsea").
    """
    def __init__(self, path: str):
        self.path = path
        self._data: Dict[str, str] = {}
        self._dirty = False
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}
        else:
            self._data = {}

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def put(self, key: str, value: str) -> None:
        if self._data.get(key) != value:
            self._data[key] = value
            self._dirty = True

    def save(self) -> None:
        if not self._dirty:
            return
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)
        self._dirty = False


# --------- Извлечение по LLM -------------------------------------------------------


class BaseExtractor:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def extract(self, schema: SchemaDefinition, text: str) -> Dict[str, Any]:
        raise NotImplementedError


class RulesExtractor(BaseExtractor):
    """
    Наивные эвристики. Для прототипа/отладки без LLM. Возвращает очень ограниченные результаты.
    """
    def extract(self, schema: SchemaDefinition, text: str) -> Dict[str, Any]:
        fields = schema.parse_fields()
        out: Dict[str, Any] = {}
        # Простейшие заглушки: попытка вытащить первое слово в кавычках как term, остальное пусто.
        if schema.name == "Definition":
            # ищем в тексте '... <термин> —' или '... <термин> -' или '(...) boldsea ...'
            m = re.search(r"([A-Za-zА-Яа-яёЁ\- ]+)\s*(—|-)\s", text)
            if m:
                candidate = m.group(1).strip()
            else:
                # fallback: первое слово
                candidate = text.strip().split()[0] if text.strip() else ""
            out["term"] = [candidate] if candidate else []
            out["includes"] = []
        elif schema.name == "Comparison":
            # Ищем "X vs Y" или "X и Y"
            m = re.search(r"([A-Za-zА-Яа-яёЁ\- ]+)\s+(?:vs|и|contra|против)\s+([A-Za-zА-Яа-яёЁ\- ]+)", text, re.IGNORECASE)
            if m:
                out["target"] = [m.group(1).strip()]
                out["comparator"] = [m.group(2).strip()]
            else:
                out["target"] = []
                out["comparator"] = []
            out["criterion"] = []
            out["advantage"] = "target"
        else:
            # Для остальных схем — пустые значения
            for fname, fs in fields.items():
                if fs.kind in ("relation",):
                    out[fname] = []
                elif fs.kind in ("attribute",):
                    out[fname] = ""
                elif fs.kind == "setrange":
                    out[fname] = ""
        out["confidence"] = 0.3
        return out


class OpenAIExtractor(BaseExtractor):
    def __init__(self, logger: logging.Logger, model: str = "gpt-4o-mini"):
        super().__init__(logger)
        try:
            # type: ignore
            import openai  # noqa: F401
        except Exception as e:
            raise RuntimeError("Для провайдера 'openai' установите пакет 'openai' (pip install openai).") from e
        self.model = model

    def extract(self, schema: SchemaDefinition, text: str) -> Dict[str, Any]:
        # lazy import to avoid hard dependency
        # type: ignore
        from openai import OpenAI  # noqa

        client = OpenAI()
        fields = schema.parse_fields()

        # Конструируем требования к формату JSON
        # Для простоты: все relation-поля требуем как массив строк (даже если они не multiple).
        # attribute-поля — строка; setrange — строка (одно из имён референсных полей).
        json_fields_desc = {
            fname: (
                "array[string]" if fs.kind == "relation"
                else "string"
            )
            for fname, fs in fields.items()
        }
        # Дополнительно: просим вернуть "confidence" от 0 до 1
        json_fields_desc["confidence"] = "number (0..1)"

        sys_prompt = (
            "You are a precise information extraction engine for the Boldsea semantic platform. "
            "Extract ONLY the requested fields from the fragment according to the schema. "
            "Return STRICT JSON with the exact keys listed. "
            "For fields of type 'array[string]', return an array of distinct canonical term labels. "
            "If nothing is found for a field, return an empty array ('[]') or an empty string (''). "
            "Do NOT add commentary."
        )

        user_prompt = (
            f"Schema name: {schema.name}\n"
            f"Instruction: {schema.llm_prompt_template}\n"
            f"Extraction fields (output types): {json.dumps(json_fields_desc, ensure_ascii=False)}\n\n"
            f"Fragment text:\n{text}\n"
        )

        # JSON-режим
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        raw = response.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
        except Exception:
            self.logger.warning("LLM returned non-JSON, fallback to empty.")
            data = {}

        # Нормализация типов
        for fname, fs in fields.items():
            if fs.kind == "relation":
                v = data.get(fname, [])
                if isinstance(v, str):
                    v = [v] if v.strip() else []
                elif not isinstance(v, list):
                    v = []
                # фильтрация пустых
                v = [str(x).strip() for x in v if str(x).strip()]
                data[fname] = v
            elif fs.kind in ("attribute", "setrange"):
                v = data.get(fname, "")
                if isinstance(v, list):
                    v = v[0] if v else ""
                v = str(v).strip()
                data[fname] = v
        # confidence
        conf = data.get("confidence", 0.7)
        try:
            conf_f = float(conf)
            if conf_f < 0 or conf_f > 1:
                conf_f = 0.7
        except Exception:
            conf_f = 0.7
        data["confidence"] = conf_f
        return data


# --------- Процессор инжеста -------------------------------------------------------


@dataclass
class IngestConfig:
    input_path: str
    api_url: str
    auth_token: Optional[str]
    provider: str  # "openai" | "rules"
    model: str
    document_title: str
    registry_path: str
    dry_run: bool
    verbose: bool
    log_file: str


@dataclass
class CreatedFragment:
    fragment_hash: str
    schema_name: str
    is_primary_for_id: bool  # первичный для данного fragment_id (для связи previous)
    fragment_id: int
    label: str


class BoldseaIngestor:
    def __init__(self, cfg: IngestConfig, logger: logging.Logger):
        self.cfg = cfg
        self.logger = logger
        self.client = BoldseaClient(cfg.api_url, auth_token=cfg.auth_token)
        self.registry = IdRegistry(cfg.registry_path)
        # Выбираем экстрактор
        if cfg.provider == "openai":
            self.extractor = OpenAIExtractor(logger, model=cfg.model)
        elif cfg.provider == "rules":
            self.extractor = RulesExtractor(logger)
        else:
            raise ValueError(f"Unsupported provider: {cfg.provider}")

    # --- helpers ---

    def _ensure_document(self, title: str) -> Tuple[str, str]:
        """
        Возвращает (label, hash) документа. Если нет — создаёт.
        """
        label = f"doc:{slugify(title)}"
        key = f"Document|{label}"
        doc_hash = self.registry.get(key)
        if doc_hash and is_boldsea_hash(doc_hash):
            return label, doc_hash

        if self.cfg.dry_run:
            # Не сохраняем DRYRUN-хэши в реестр, чтобы не ломать реальные запуски
            return label, "#DRYRUN_DOCUMENT_HASH"

        # Создаём индивид документа
        doc_hash = self.client.create_individual("Document", label, "Model Document")
        # Ставим title
        self.client.set_property(doc_hash, "title", title)
        self.registry.put(key, doc_hash)
        self.logger.info("Created Document: %s -> %s", label, doc_hash)
        return label, doc_hash

    def _ensure_term(self, term_label: str) -> str:
        """
        Убеждаемся, что термин существует. Если нет — создаём.
        """
        clean = term_label.strip()
        if not clean:
            raise ValueError("Empty term label.")
        key = f"Term|{clean}"
        term_hash = self.registry.get(key)
        if term_hash and is_boldsea_hash(term_hash):
            return term_hash

        if self.cfg.dry_run:
            # Не сохраняем DRYRUN-хэши в реестр
            return f"#DRYRUN_TERM_{slugify(clean)}"

        term_hash = self.client.create_individual("Term", clean, "Model Term")
        self.registry.put(key, term_hash)
        self.logger.debug("Created Term: %s -> %s", clean, term_hash)
        return term_hash

    def _create_fragment(self, fragment_label: str, model: str) -> str:
        if self.cfg.dry_run:
            return f"#DRYRUN_FRAGMENT_{slugify(fragment_label)}"
        return self.client.create_individual("Fragment", fragment_label, model)

    def _set_prop(self, subject_hash: str, prop: str, value: Any) -> None:
        if self.cfg.dry_run:
            self.logger.debug("[DRY RUN] set %s %s -> %s", subject_hash, prop, value)
            return
        self.client.set_property(subject_hash, prop, value)

    # --- main ---

    def process(self, input_data: Dict[str, Any]) -> None:
        # Документ
        doc_label, doc_hash = self._ensure_document(self.cfg.document_title)

        fragments = input_data.get("fragments", [])
        # Сортируем по fragment_id
        try:
            fragments = sorted(fragments, key=lambda x: int(x.get("fragment_id", 0)))
        except Exception:
            pass

        created: List[CreatedFragment] = []

        for frag in fragments:
            frag_id = int(frag.get("fragment_id"))
            schemas: List[str] = frag.get("schema", [])
            text: str = frag.get("text", "")

            if not schemas:
                self.logger.warning("Fragment %s has no schemas, skipping.", frag_id)
                continue

            primary_done = False
            primary_hash_for_prev: Optional[str] = None
            primary_label: Optional[str] = None

            for idx, schema_name in enumerate(schemas):
                if schema_name not in SCHEMA_REGISTRY:
                    self.logger.warning("Schema '%s' is not supported, skipping.", schema_name)
                    continue
                schema = SCHEMA_REGISTRY[schema_name]
                fields = schema.parse_fields()

                # Извлекаем поля
                try:
                    extracted = self.extractor.extract(schema, text)
                except Exception as e:
                    self.logger.error("Extraction failed for fragment %s schema %s: %s", frag_id, schema_name, e)
                    self.logger.debug(traceback.format_exc())
                    extracted = {"confidence": 0.5}

                # Создаём фрагмент
                frag_label = f"{doc_label}:frag:{frag_id}:{slugify(schema_name)}"
                frag_hash = self._create_fragment(frag_label, schema.model_identifier)

                # Базовые атрибуты
                self._set_prop(frag_hash, "text", text)
                self._set_prop(frag_hash, "fragment_anchor", f"frag:{frag_id}")
                try:
                    conf_val = float(extracted.get("confidence", 0.7))
                except Exception:
                    conf_val = 0.7
                self._set_prop(frag_hash, "confidence", conf_val)
                # Привязка к документу
                self._set_prop(frag_hash, "document", doc_hash)

                # Установка полей по схеме
                # Сначала соберём контекст для возможных setrange (ссылки на target/comparator и т.п.)
                ctx_term_hashes: Dict[str, List[str]] = {}
                for fname, fs in fields.items():
                    if fs.kind == "relation":
                        values = extracted.get(fname, [])
                        if isinstance(values, str):
                            values = [values] if values.strip() else []
                        hashes: List[str] = []
                        for label in values:
                            try:
                                th = self._ensure_term(label)
                                hashes.append(th)
                                # Ставим отношение (может быть multiple)
                                self._set_prop(frag_hash, fname, th)
                            except Exception as e:
                                self.logger.error("Term ensure failed for '%s' in field '%s': %s", label, fname, e)
                        ctx_term_hashes[fname] = hashes
                    elif fs.kind == "attribute":
                        v = str(extracted.get(fname, "")).strip()
                        if v:
                            self._set_prop(frag_hash, fname, v)
                    elif fs.kind == "setrange":
                        # Значение — имя одного из референсных полей (например, "target" или "comparator").
                        ref_choice = str(extracted.get(fname, "")).strip()
                        if ref_choice and fs.set_range_refs:
                            if ref_choice not in fs.set_range_refs:
                                self.logger.warning(
                                    "Field '%s' value '%s' not in SetRange %s; skipping.",
                                    fname, ref_choice, fs.set_range_refs
                                )
                            else:
                                # Берём первый hash из соответствующего списка. (Упрощение.)
                                ref_hashes = ctx_term_hashes.get(ref_choice, [])
                                if ref_hashes:
                                    self._set_prop(frag_hash, fname, ref_hashes[0])
                                else:
                                    self.logger.warning(
                                        "Field '%s' refers to '%s' but that list is empty.", fname, ref_choice
                                    )

                created.append(
                    CreatedFragment(
                        fragment_hash=frag_hash,
                        schema_name=schema_name,
                        is_primary_for_id=(not primary_done),
                        fragment_id=frag_id,
                        label=frag_label,
                    )
                )

                if not primary_done:
                    primary_done = True
                    primary_hash_for_prev = frag_hash
                    primary_label = frag_label
                else:
                    # Для дополнительных схем того же fragment_id сошлёмся на "whole" — на первичный
                    if primary_hash_for_prev:
                        self._set_prop(frag_hash, "whole", primary_hash_for_prev)

        # Простановка связей previous по первичным фрагментам (по возрастанию fragment_id)
        primaries = [c for c in created if c.is_primary_for_id]
        primaries_sorted = sorted(primaries, key=lambda x: (x.fragment_id, x.schema_name))
        for i in range(1, len(primaries_sorted)):
            cur = primaries_sorted[i]
            prev = primaries_sorted[i - 1]
            try:
                self._set_prop(cur.fragment_hash, "previous", prev.fragment_hash)
            except Exception as e:
                self.logger.error("Failed to set 'previous' for %s -> %s: %s", cur.label, prev.label, e)

        # Сохраняем реестр
        try:
            self.registry.save()
        except Exception as e:
            self.logger.error("Failed to save registry: %s", e)

        # Итог
        self.logger.info("Done. Created/updated %d fragment individuals (including secondary).", len(created))


# --------- CLI --------------------------------------------------------------------


def load_json_from_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_logger(verbose: bool, log_file: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger("boldsea_ingest")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Avoid duplicate handlers on repeated runs
    logger.handlers.clear()

    fmt = logging.Formatter("[%(levelname)s] %(message)s")

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler (optional)
    if log_file:
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(logging.DEBUG if verbose else logging.INFO)
            fh.setFormatter(fmt)
            logger.addHandler(fh)
        except Exception as e:
            logger.warning("Не удалось открыть файл лога '%s': %s", log_file, e)

    return logger


def parse_args(argv: Optional[List[str]] = None) -> IngestConfig:
    parser = argparse.ArgumentParser(description="Boldsea KG Ingest CLI")
    parser.add_argument("--input", required=True, help="Путь к JSON файлу с фрагментами.")
    parser.add_argument("--document-title", required=True, help="Заголовок (title) документа в Boldsea.")
    parser.add_argument("--registry", default="./boldsea_registry.json", help="Файл локального реестра id/hash.")
    parser.add_argument("--api-url", default="https://srv.boldsea.top/api/v1/semantic", help="URL Boldsea Semantic API.")
    parser.add_argument("--provider", choices=["openai", "rules"], default="openai",
                        help="Провайдер извлечения: 'openai' (LLM) или 'rules' (наивные правила).")
    parser.add_argument("--model", default="gpt-4o-mini", help="Имя LLM модели (для провайдера 'openai').")
    parser.add_argument("--dry-run", action="store_true", help="Не делать запросы в API, только печатать шаги.")
    parser.add_argument("--verbose", action="store_true", help="Подробный лог.")
    parser.add_argument("--auth-token", default=os.environ.get("BOLDSEA_API_TOKEN", None),
                        help="Bearer-токен для Boldsea API (если требуется). Можно задать через BOLDSEA_API_TOKEN.")
    parser.add_argument("--log-file", default="./boldsea_ingest_output.log",
                        help="Путь к файлу для записи детальных логов выполнения.")
    args = parser.parse_args(argv)

    cfg = IngestConfig(
        input_path=args.input,
        api_url=args.api_url,
        auth_token=args.auth_token,
        provider=args.provider,
        model=args.model,
        document_title=args.document_title,
        registry_path=args.registry,
        dry_run=bool(args.dry_run),
        verbose=bool(args.verbose),
        log_file=args.log_file,
    )
    return cfg


def main(argv: Optional[List[str]] = None) -> None:
    cfg = parse_args(argv)
    logger = build_logger(cfg.verbose, cfg.log_file)
    logger.info("Подробные логи пишутся в файл: %s", cfg.log_file)

    # Проверка ключа OpenAI
    if cfg.provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY не найден в окружении, но выбран провайдер 'openai'. "
                     "Установите ключ или используйте '--provider rules'.")
        sys.exit(2)

    if not os.path.exists(cfg.input_path):
        logger.error("Входной файл не найден: %s", cfg.input_path)
        sys.exit(2)

    try:
        input_data = load_json_from_file(cfg.input_path)
    except Exception as e:
        logger.error("Не удалось прочитать JSON '%s': %s", cfg.input_path, e)
        sys.exit(2)

    try:
        ingestor = BoldseaIngestor(cfg, logger)
        ingestor.process(input_data)
    except Exception as e:
        logger.error("Ошибка выполнения: %s", e)
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
