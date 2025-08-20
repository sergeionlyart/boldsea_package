#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boldsea Semantic Segmenter
--------------------------
Скрипт принимает .md и разбивает его на семантические фрагменты согласно онтологии Boldsea.
Выход: fragments.jsonl + annotated.md
Особенности:
- Эксклюзивно семантическое разбиение (структура файла — только подсказка).
- Поддержка активных схем из конфига.
- Окна (sliding window) + объединение перекрытий.
- Логи LLM-вызовов, идемпотентность (хеш входа).
- Режим --mock для офлайн-проверки без LLM.

Требования:
- Python 3.9+
- Для LLM: openai>=1.0.0 (или совместимый SDK). Можно заменить реализацию клиента.

Автор: GPT-5 Pro (ассистент)
Лицензия: MIT
"""
from __future__ import annotations

import argparse
import dataclasses
from dataclasses import dataclass, field, asdict
import json
import os
import re
import sys
import time
import math
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple, Iterable

# --------- Утилиты загрузки YAML/JSON-конфига ---------
def load_config(path: str) -> Dict[str, Any]:
    """
    Загружает YAML или JSON. Возвращает dict.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    # Пытаемся YAML, потом JSON
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except Exception:
        pass
    try:
        return json.loads(text)
    except Exception as e:
        raise RuntimeError(f"Не удалось распарсить {path} как YAML/JSON: {e}")


# --------- Библиотека схем (встроенная) ---------
@dataclass(frozen=True)
class SchemaDef:
    id: str
    display_name: str
    llm_prompt_template: str
    extraction_fields: Dict[str, str]


SCHEMA_LIBRARY: Dict[str, SchemaDef] = {
    # Базовые универсальные
    "Definition": SchemaDef(
        id="Definition",
        display_name="Определение",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Definition.\n"
            "Извлеки: term (определяемый термин), includes (термины, упомянутые в определении)."
        ),
        extraction_fields={"term": "Range: Term", "includes": "Range: Term, Multiple: 1"},
    ),
    "Comparison": SchemaDef(
        id="Comparison",
        display_name="Сравнение",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Comparison.\n"
            "Извлеки: target, comparator, criterion[], advantage."
        ),
        extraction_fields={
            "target": "Range: Term",
            "comparator": "Range: Term",
            "criterion": "Range: Term, Multiple: 1",
            "advantage": "SetRange: [target, comparator]",
        },
    ),
    "Causal Relation": SchemaDef(
        id="Causal Relation",
        display_name="Причинно-следственная связь",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Causal Relation.\n"
            "Извлеки: cause[], effect[]."
        ),
        extraction_fields={"cause": "Range: Term, Multiple: 1", "effect": "Range: Term, Multiple: 1"},
    ),
    "Application Context": SchemaDef(
        id="Application Context",
        display_name="Контекст применения",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Application Context.\n"
            "Извлеки: domain[]."
        ),
        extraction_fields={"domain": "Range: Term, Multiple: 1"},
    ),
    "Example": SchemaDef(
        id="Example",
        display_name="Пример",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Example.\n"
            "Извлеки: illustrates[], type in [code, scenario, analogy, counter-example]."
        ),
        extraction_fields={"illustrates": "Range: Term, Multiple: 1", "type": "DataType: EnumType"},
    ),
    # Архитектурно-технические
    "Architectural Component": SchemaDef(
        id="Architectural Component",
        display_name="Архитектурный компонент",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Architectural Component.\n"
            "Извлеки: system_terms[], purpose_terms[], interfaces_terms[], pattern_terms[]."
        ),
        extraction_fields={
            "system_terms": "Range: Term, Multiple: 1",
            "purpose_terms": "Range: Term, Multiple: 1",
            "interfaces_terms": "Range: Term, Multiple: 1",
            "pattern_terms": "Range: Term, Multiple: 1",
        },
    ),
    "Technical Process": SchemaDef(
        id="Technical Process",
        display_name="Технический процесс",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Technical Process.\n"
            "Извлеки: input_types[], output_types[], process_category, involves_components[]."
        ),
        extraction_fields={
            "input_types": "Range: Term, Multiple: 1",
            "output_types": "Range: Term, Multiple: 1",
            "process_category": "Range: Term",
            "involves_components": "Range: Term, Multiple: 1",
        },
    ),
    "Algorithm": SchemaDef(
        id="Algorithm",
        display_name="Алгоритм/Метод",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Algorithm.\n"
            "Извлеки: input_types[], output_types[], involves_components[], process_category."
        ),
        extraction_fields={
            "input_types": "Range: Term, Multiple: 1",
            "output_types": "Range: Term, Multiple: 1",
            "involves_components": "Range: Term, Multiple: 1",
            "process_category": "Range: Term",
        },
    ),
    # Концептуальные
    "Conceptual Model": SchemaDef(
        id="Conceptual Model",
        display_name="Концептуальная модель",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Conceptual Model.\n"
            "Извлеки: target, involves_components[]."
        ),
        extraction_fields={"target": "Range: Term", "involves_components": "Range: Term, Multiple: 1"},
    ),
    "Principle": SchemaDef(
        id="Principle",
        display_name="Принцип/Подход",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Principle.\n"
            "Извлеки: target, domain[], comparator[], demonstrates[]."
        ),
        extraction_fields={
            "target": "Range: Term",
            "domain": "Range: Term, Multiple: 1",
            "comparator": "Range: Term, Multiple: 1",
            "demonstrates": "Range: Term, Multiple: 1",
        },
    ),
    # Проблемно-ориентированные
    "Problem Solution": SchemaDef(
        id="Problem Solution",
        display_name="Проблема и решение",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Problem Solution.\n"
            "Извлеки: problem_domain[], solution_components[]."
        ),
        extraction_fields={
            "problem_domain": "Range: Term, Multiple: 1",
            "solution_components": "Range: Term, Multiple: 1",
        },
    ),
    "Limitations And Challenges": SchemaDef(
        id="Limitations And Challenges",
        display_name="Ограничения и вызовы",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Limitations And Challenges.\n"
            "Извлеки: target, problem_domain[]."
        ),
        extraction_fields={
            "target": "Range: Term",
            "problem_domain": "Range: Term, Multiple: 1",
        },
    ),
    # Функциональные
    "Functionality": SchemaDef(
        id="Functionality",
        display_name="Функциональность",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Functionality.\n"
            "Извлеки: system_terms, purpose_terms[], involves_components[]."
        ),
        extraction_fields={
            "system_terms": "Range: Term",
            "purpose_terms": "Range: Term, Multiple: 1",
            "involves_components": "Range: Term, Multiple: 1",
        },
    ),
    "Capabilities": SchemaDef(
        id="Capabilities",
        display_name="Возможности",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Capabilities.\n"
            "Извлеки: target, purpose_terms[], demonstrates[]."
        ),
        extraction_fields={
            "target": "Range: Term",
            "purpose_terms": "Range: Term, Multiple: 1",
            "demonstrates": "Range: Term, Multiple: 1",
        },
    ),
    # Интеграционные
    "System Integration": SchemaDef(
        id="System Integration",
        display_name="Интеграция систем",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа System Integration.\n"
            "Извлеки: target, comparator, interfaces_terms[], process_category."
        ),
        extraction_fields={
            "target": "Range: Term",
            "comparator": "Range: Term",
            "interfaces_terms": "Range: Term, Multiple: 1",
            "process_category": "Range: Term",
        },
    ),
    "Component Interaction": SchemaDef(
        id="Component Interaction",
        display_name="Взаимодействие компонентов",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Component Interaction.\n"
            "Извлеки: target, comparator, process_category, involves_components[]."
        ),
        extraction_fields={
            "target": "Range: Term",
            "comparator": "Range: Term",
            "process_category": "Range: Term",
            "involves_components": "Range: Term, Multiple: 1",
        },
    ),
    # Прикладные
    "Use Case": SchemaDef(
        id="Use Case",
        display_name="Сценарий использования",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Use Case.\n"
            "Извлеки: domain, actors[], demonstrates[]."
        ),
        extraction_fields={
            "domain": "Range: Term",
            "actors": "Range: Term, Multiple: 1",
            "demonstrates": "Range: Term, Multiple: 1",
        },
    ),
    "Concept Implementation": SchemaDef(
        id="Concept Implementation",
        display_name="Реализация концепции",
        llm_prompt_template=(
            "Классифицируй и извлеки фрагменты типа Concept Implementation.\n"
            "Извлеки: concept_ref, technologies[], key_features[]."
        ),
        extraction_fields={
            "concept_ref": "Range: Term",
            "technologies": "Range: Term, Multiple: 1",
            "key_features": "Range: Term, Multiple: 1",
        },
    ),
    # Дополнительно
    "Code Snippet": SchemaDef(
        id="Code Snippet",
        display_name="Фрагмент кода",
        llm_prompt_template=(
            "Классифицируй фрагменты, содержащие фактический код/скрипт/грамматику.\n"
            "Извлеки: language, illustrates[], input_types[], output_types[], keywords[]."
        ),
        extraction_fields={
            "language": "Range: Term",
            "illustrates": "Range: Term, Multiple: 1",
            "input_types": "Range: Term, Multiple: 1",
            "output_types": "Range: Term, Multiple: 1",
            "keywords": "Range: Term, Multiple: 1",
        },
    ),
    "Enumeration": SchemaDef(
        id="Enumeration",
        display_name="Перечисление/Список",
        llm_prompt_template=(
            "Классифицируй явные списки/перечисления (семантические, не структурные).\n"
            "Извлеки: category, items[], keywords[]."
        ),
        extraction_fields={
            "category": "Range: Term",
            "items": "Range: Term, Multiple: 1",
            "keywords": "Range: Term, Multiple: 1",
        },
    ),
    "Table Analysis": SchemaDef(
        id="Table Analysis",
        display_name="Таблица/Матрица",
        llm_prompt_template=(
            "Классифицируй структурированные таблицы/матрицы (смысловые).\n"
            "Извлеки: rows[], columns[], values[], keywords[]."
        ),
        extraction_fields={
            "rows": "Range: Term, Multiple: 1",
            "columns": "Range: Term, Multiple: 1",
            "values": "Range: Term, Multiple: 1",
            "keywords": "Range: Term, Multiple: 1",
        },
    ),
    "Advantage Disadvantage": SchemaDef(
        id="Advantage Disadvantage",
        display_name="Преимущества и недостатки",
        llm_prompt_template=(
            "Классифицируй фрагменты, явно перечисляющие достоинства/недостатки.\n"
            "Извлеки: target, advantages[], disadvantages[], keywords[]."
        ),
        extraction_fields={
            "target": "Range: Term",
            "advantages": "Range: Term, Multiple: 1",
            "disadvantages": "Range: Term, Multiple: 1",
            "keywords": "Range: Term, Multiple: 1",
        },
    ),
}


# --------- Датаклассы ---------
@dataclass
class Fragment:
    id: str
    start_char: int
    end_char: int
    text: str
    schema_id: str
    schema_type: str
    entity_refs: List[str] = field(default_factory=list)
    actors: List[str] = field(default_factory=list)
    acts: List[str] = field(default_factory=list)
    causals: List[str] = field(default_factory=list)  # IDs после пост-обработки
    confidence: float = 0.0
    rationale: str = ""
    overlaps: List[str] = field(default_factory=list)  # IDs фрагментов
    # Доп. поля (не в JSONL, но полезны в пайплайне)
    _chunk_index: int = -1
    _source_window: Tuple[int, int] = field(default_factory=lambda: (0, 0))
    _local_causal_spans: List[Tuple[int, int]] = field(default_factory=list)  # относит. к chunk


@dataclass
class LLMResponse:
    fragments: List[Fragment]
    raw: Dict[str, Any]


# --------- Идемпотентность/хеши ---------
def content_hash(*parts: str) -> str:
    h = hashlib.blake2b(digest_size=16)
    for p in parts:
        h.update(p.encode("utf-8"))
    return h.hexdigest()


# --------- Оконный разбор ---------
def window_iter(text: str, window_chars: int, overlap_chars: int) -> Iterable[Tuple[int, int, str, int]]:
    """
    Возвращает последовательность (start_offset, end_offset, chunk_text, chunk_index)
    """
    n = len(text)
    if window_chars <= 0:
        raise ValueError("window_chars must be > 0")
    if overlap_chars < 0 or overlap_chars >= window_chars:
        raise ValueError("0 <= overlap < window_chars")
    idx = 0
    chunk_idx = 0
    while idx < n:
        end = min(n, idx + window_chars)
        yield (idx, end, text[idx:end], chunk_idx)
        if end == n:
            break
        idx = end - overlap_chars
        chunk_idx += 1


# --------- Сборка промптов ---------
ONT_BRIEF = (
    "Ты выполняешь СЕМАНТИЧЕСКОЕ разбиение текста на фрагменты согласно онтологии Boldsea.\n"
    "- Строго не допускай выдачу сегментов, не соответствующих выбранным семантическим схемам.\n"
    "- Заголовки/списки — только подсказка; решение о границах = по смыслу.\n"
    "- Фрагмент должен быть минимально достаточен для инстанцирования выбранной схемы.\n"
    "- При неоднозначности возвращай альтернативы с вероятностями.\n"
    "- Ответ ТОЛЬКО в JSON. Без комментариев/объяснений вне JSON.\n"
)

def build_system_prompt(active_schemas: List[str]) -> str:
    lines = [ONT_BRIEF, "Доступные схемы:"]
    for sid in active_schemas:
        s = SCHEMA_LIBRARY.get(sid)
        if not s:
            continue
        lines.append(f"* {s.id}: {s.display_name}. {s.llm_prompt_template}")
    lines.append(
        "Схема JSON ответа:\n"
        "{\n"
        '  "fragments": [\n'
        "    {\n"
        '      "start": int,                 // позиция в символах в рамках ЭТОГО куска\n'
        '      "end": int,                   // позиция-исключающее окончание в рамках ЭТОГО куска\n'
        '      "schema_id": "Definition|..."\n'
        '      "schema_type": "Fragment",\n'
        '      "entity_refs": [string],      // термины/сущности\n'
        '      "actors": [string],           // участники (если есть)\n'
        '      "acts": [string],             // действия (если есть)\n'
        '      "causal_spans": [[int,int]],  // локальные ссылки на причины в пределах куска\n'
        '      "confidence": 0.0..1.0,\n'
        '      "rationale": "≤300 символов"\n'
        "    }\n"
        "  ],\n"
        '  "alternatives": [\n'
        "    {\"start\": int, \"end\": int, \"schema_id\": string, \"prob\": 0.0..1.0}\n"
        "  ]\n"
        "}"
    )
    return "\n".join(lines)


def build_user_prompt(chunk_text: str, offset: int) -> str:
    return (
        f"Разметь следующий фрагмент Markdown (смещения относительно этого куска; базовый offset={offset}).\n"
        "Верни JSON строго по схеме выше.\n"
        "```\n" + chunk_text + "\n```"
    )


# --------- LLM-клиент (OpenAI) ---------
class LLMClient:
    def __init__(self, model: str, temperature: float, max_tokens: int, log_path: Optional[str] = None):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.log_path = log_path

        # Ленивая инициализация openai
        self._openai = None

    def _ensure_openai(self):
        if self._openai is None:
            try:
                from openai import OpenAI  # type: ignore
            except Exception as e:
                raise RuntimeError("Нужен пакет openai>=1.0.0 для LLM-режима. Установите: pip install openai") from e
            self._openai = OpenAI()

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        self._ensure_openai()
        assert self._openai is not None
        started = time.time()
        # Build base kwargs, dropping sampling params for models that don't support them (e.g., GPT-5*)
        supports_sampling = not str(self.model).startswith("gpt-5")
        base_kwargs = {
            "model": self.model,
            # Chat Completions used max_tokens; Responses uses max_output_tokens
            "max_output_tokens": self.max_tokens,
            # Responses API uses `input` instead of `messages`
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            # We prefer not to persist responses
            "store": False,
        }
        if supports_sampling:
            base_kwargs["temperature"] = self.temperature
        else:
            try:
                logging.getLogger(__name__).info(
                    "Model %s does not support temperature; dropping it.", self.model
                )
            except Exception:
                pass
        # 1) Prefer new Responses shape: text.format (object form)
        try:
            kwargs = dict(base_kwargs)
            # Newer SDKs expect an object for text.format, not a bare string
            # https://platform.openai.com/docs/guides/structured-outputs
            kwargs["text"] = {"format": {"type": "json_object"}}
            resp = self._openai.responses.create(**kwargs)
        except Exception:
            # 2) Fallback: older Responses accepting response_format
            try:
                kwargs = dict(base_kwargs)
                kwargs["response_format"] = {"type": "json_object"}
                resp = self._openai.responses.create(**kwargs)
            except Exception:
                # 3) Last resort: remove hints; also drop `store` if unsupported
                try:
                    resp = self._openai.responses.create(**base_kwargs)
                except Exception:
                    kwargs2 = dict(base_kwargs)
                    kwargs2.pop("store", None)
                    resp = self._openai.responses.create(**kwargs2)
        latency = time.time() - started
        # Official SDKs expose a convenience aggregator for text outputs
        content = getattr(resp, "output_text", None)
        if not content:
            try:
                # Fallback to raw structure if needed
                content = resp.output[0].content[0].text
            except Exception:
                content = "{}"

        # Логируем
        if self.log_path:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as f:
                rec = {
                    "ts": time.time(),
                    "latency_sec": latency,
                    "model": self.model,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "system": system_prompt,
                    "user": user_prompt[:5000],  # не храним очень длинный
                    "response": content[:100000],
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        return content


# --------- Парсер JSON из LLM ---------
def parse_llm_json(payload: str) -> Dict[str, Any]:
    """
    Бескомпромиссно ожидаем корректный JSON-объект.
    Если прилетело что-то лишнее, пытаемся вырезать первое { ... }.
    """
    payload = payload.strip()
    if payload.startswith("{") and payload.endswith("}"):
        return json.loads(payload)
    # попытаемся найти первый валидный json-объект
    start = payload.find("{")
    end = payload.rfind("}")
    if start != -1 and end != -1 and end > start:
        sub = payload[start : end + 1]
        try:
            return json.loads(sub)
        except Exception:
            pass
    # как есть
    return json.loads(payload)


# --------- Обработка ответа LLM в фрагменты ---------
def to_fragments_from_chunk(
    chunk_json: Dict[str, Any],
    chunk_index: int,
    global_offset: int,
    full_text: str,
) -> List[Fragment]:
    frags: List[Fragment] = []
    objects = chunk_json.get("fragments", [])
    if not isinstance(objects, list):
        return frags
    for obj in objects:
        try:
            start_local = int(obj["start"])
            end_local = int(obj["end"])
            schema_id = str(obj["schema_id"])
            schema_type = str(obj.get("schema_type", "Fragment"))
            if schema_id not in SCHEMA_LIBRARY:
                # игнорируем неизвестные схемы
                continue
            abs_start = global_offset + start_local
            abs_end = global_offset + end_local
            if abs_start < 0 or abs_end > len(full_text) or abs_end <= abs_start:
                continue
            text = full_text[abs_start:abs_end]

            entity_refs = list(map(str, obj.get("entity_refs", []))) if obj.get("entity_refs") else []
            actors = list(map(str, obj.get("actors", []))) if obj.get("actors") else []
            acts = list(map(str, obj.get("acts", []))) if obj.get("acts") else []
            causal_spans = obj.get("causal_spans", [])
            loc_causals: List[Tuple[int, int]] = []
            if isinstance(causal_spans, list):
                for it in causal_spans:
                    try:
                        s = int(it[0])
                        e = int(it[1])
                        loc_causals.append((s, e))
                    except Exception:
                        continue

            confidence = float(obj.get("confidence", 0.0))
            confidence = max(0.0, min(1.0, confidence))
            rationale = str(obj.get("rationale", ""))[:300]

            fid = make_fragment_id(abs_start, abs_end, schema_id, text)
            f = Fragment(
                id=fid,
                start_char=abs_start,
                end_char=abs_end,
                text=text,
                schema_id=schema_id,
                schema_type=schema_type,
                entity_refs=entity_refs,
                actors=actors,
                acts=acts,
                causals=[],
                confidence=confidence,
                rationale=rationale,
                overlaps=[],
                _chunk_index=chunk_index,
                _source_window=(global_offset, global_offset + (abs_end - abs_start)),
                _local_causal_spans=loc_causals,
            )
            frags.append(f)
        except Exception:
            continue
    return frags


def make_fragment_id(start: int, end: int, schema_id: str, text: str) -> str:
    h = hashlib.blake2b(digest_size=12)
    h.update(f"{start}:{end}:{schema_id}".encode("utf-8"))
    h.update(text.encode("utf-8"))
    return "f_" + h.hexdigest()


# --------- Слияние/дедупликация ---------
def iou_1d(a_start: int, a_end: int, b_start: int, b_end: int) -> float:
    inter = max(0, min(a_end, b_end) - max(a_start, b_start))
    union = max(a_end, b_end) - min(a_start, b_start)
    if union == 0:
        return 0.0
    return inter / union


def merge_fragments(frags: List[Fragment], iou_threshold: float = 0.66) -> List[Fragment]:
    """
    Сливает близкие/дублирующие фрагменты по IoU и схеме.
    Политика: оставляем фрагмент с большей confidence, накапливаем overlaps.
    """
    frags = sorted(frags, key=lambda x: (x.start_char, x.end_char))
    kept: List[Fragment] = []
    for f in frags:
        merged = False
        for k in kept:
            if f.schema_id != k.schema_id:
                continue
            if iou_1d(f.start_char, f.end_char, k.start_char, k.end_char) >= iou_threshold:
                # сливаем в k
                if f.confidence > k.confidence:
                    # заменяем содержимое, но сохраняем overlaps
                    old_id = k.id
                    k.id = f.id
                    k.start_char = f.start_char
                    k.end_char = f.end_char
                    k.text = f.text
                    k.entity_refs = f.entity_refs or k.entity_refs
                    k.actors = f.actors or k.actors
                    k.acts = f.acts or k.acts
                    k.confidence = f.confidence
                    k.rationale = f.rationale or k.rationale
                # отмечаем перекрытие
                if f.id not in k.overlaps:
                    k.overlaps.append(f.id)
                if k.id not in f.overlaps:
                    f.overlaps.append(k.id)
                merged = True
                break
        if not merged:
            kept.append(f)
    # Пост-обработка overlaps на всех
    id_map = {f.id: f for f in kept}
    for f in kept:
        f.overlaps = [oid for oid in f.overlaps if oid in id_map and oid != f.id]
    return kept


# --------- Пост-линковка причинно-следственных связей ---------
def link_causals_by_spans(frags: List[Fragment]) -> None:
    """
    Для каждого фрагмента сопоставляет его локальные causal_spans (переведённые в абсолютные координаты)
    с id фрагментов, перекрывающихся этими span'ами. Добавляет в f.causals список ID.
    """
    # Индексация по диапазонам
    for f in frags:
        abs_causals: List[Tuple[int, int]] = []
        base_offset = f._source_window[0]  # глобальный offset окна
        for (s_rel, e_rel) in f._local_causal_spans:
            abs_s = base_offset + s_rel
            abs_e = base_offset + e_rel
            if abs_s < abs_e:
                abs_causals.append((abs_s, abs_e))

        causals_ids: List[str] = []
        for (cs, ce) in abs_causals:
            for g in frags:
                if g is f:
                    continue
                # причину ищем раньше по тексту
                if g.end_char <= f.start_char and iou_1d(cs, ce, g.start_char, g.end_char) > 0.2:
                    causals_ids.append(g.id)
        # дедуп
        f.causals = sorted(list(set(causals_ids)), key=lambda x: x)


# --------- Экспорт ---------
def save_jsonl(path: str, frags: List[Fragment]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for fr in frags:
            rec = {
                "id": fr.id,
                "start_char": fr.start_char,
                "end_char": fr.end_char,
                "text": fr.text,
                "schema_id": fr.schema_id,
                "schema_type": fr.schema_type,
                "entity_refs": fr.entity_refs,
                "actors": fr.actors,
                "acts": fr.acts,
                "causals": fr.causals,
                "confidence": float(f"{fr.confidence:.3f}"),
                "rationale": fr.rationale[:300],
                "overlaps": fr.overlaps,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def annotate_markdown(text: str, frags: List[Fragment]) -> str:
    """
    Вставляет невидимые маркеры (HTML-комментарии), чтобы не ломать Markdown.
    Предпочитаем упорядочивание по start_char DESC, чтобы не сдвигать позиции.
    """
    markers = []
    for fr in frags:
        start_tag = (
            f"<!-- FRAG id={fr.id} schema={fr.schema_id} conf={fr.confidence:.2f} "
            f"start={fr.start_char} end={fr.end_char} -->"
        )
        end_tag = f"<!-- /FRAG id={fr.id} -->"
        markers.append((fr.start_char, True, start_tag))
        markers.append((fr.end_char, False, end_tag))

    markers.sort(key=lambda x: (x[0], 0 if x[1] else 1), reverse=True)
    buf = text
    for pos, is_start, tag in markers:
        buf = buf[:pos] + tag + buf[pos:]
    return buf


# --------- MOCK-режим (без LLM) ---------
def mock_segment(text: str, active_schemas: List[str]) -> List[Fragment]:
    """
    Упрощённая эвристика для офлайн-проверки пайплайна.
    Ищет определения и каузальные связи по ключевым словам.
    """
    frags: List[Fragment] = []
    # Definition: строка "X — ..." или "X: ..."
    definition_pattern = re.compile(r"(?P<term>^[A-Za-zА-Яа-я0-9_ \-/]{3,50})\s*[—:-]\s*(?P<body>.+)$", re.M)
    if "Definition" in active_schemas:
        for m in definition_pattern.finditer(text):
            start = m.start()
            end = m.end()
            snippet = text[start:end]
            term = m.group("term").strip()
            fid = make_fragment_id(start, end, "Definition", snippet)
            frags.append(
                Fragment(
                    id=fid,
                    start_char=start,
                    end_char=end,
                    text=snippet,
                    schema_id="Definition",
                    schema_type="Fragment",
                    entity_refs=[term],
                    confidence=0.55,
                    rationale="эвристика: паттерн терм—определение",
                )
            )

    # Causal Relation: предложения с "потому что|приводит к|обусловливает"
    if "Causal Relation" in active_schemas:
        causal_pattern = re.compile(r"(.+?)(потому что|приводит к|обусловливает)(.+?)[\.\n]", re.I | re.S)
        for m in causal_pattern.finditer(text):
            start = m.start()
            end = m.end()
            snippet = text[start:end]
            fid = make_fragment_id(start, end, "Causal Relation", snippet)
            frags.append(
                Fragment(
                    id=fid,
                    start_char=start,
                    end_char=end,
                    text=snippet,
                    schema_id="Causal Relation",
                    schema_type="Fragment",
                    confidence=0.5,
                    rationale="эвристика: причинная связка",
                    _local_causal_spans=[(0, end - start)],
                )
            )

    return merge_fragments(frags)


# --------- Основной пайплайн ---------
def run_pipeline(
    md_path: str,
    outdir: str,
    active_schemas: List[str],
    model: str,
    temperature: float,
    max_tokens: int,
    window_chars: int,
    overlap_chars: int,
    mock: bool,
) -> str:
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    run_id = content_hash(text, json.dumps(active_schemas, ensure_ascii=False), model, str(temperature), str(max_tokens))
    run_dir = os.path.join(outdir, run_id[:12])
    os.makedirs(run_dir, exist_ok=True)

    log_path = os.path.join(run_dir, "llm_calls.jsonl")
    system_prompt = build_system_prompt(active_schemas)

    all_frags: List[Fragment] = []
    if mock:
        # офлайн
        all_frags = mock_segment(text, active_schemas)
    else:
        client = LLMClient(model=model, temperature=temperature, max_tokens=max_tokens, log_path=log_path)
        for start, end, chunk, idx in window_iter(text, window_chars, overlap_chars):
            user_prompt = build_user_prompt(chunk, start)
            raw = client.chat(system_prompt, user_prompt)
            try:
                obj = parse_llm_json(raw)
            except Exception as e:
                # логируем и продолжаем
                with open(os.path.join(run_dir, "errors.log"), "a", encoding="utf-8") as ef:
                    ef.write(f"[chunk {idx} offset {start}] JSON parse error: {e}\n{raw[:2000]}\n\n")
                obj = {"fragments": []}

            frs = to_fragments_from_chunk(obj, idx, start, text)
            all_frags.extend(frs)

    # Слияние/дедуп
    all_frags = merge_fragments(all_frags)

    # Пост-линковка причинностей
    link_causals_by_spans(all_frags)

    # Экспорт
    jsonl_path = os.path.join(run_dir, "fragments.jsonl")
    save_jsonl(jsonl_path, all_frags)

    annotated_md = annotate_markdown(text, all_frags)
    annotated_path = os.path.join(run_dir, "annotated.md")
    with open(annotated_path, "w", encoding="utf-8") as f:
        f.write(annotated_md)

    # Метаданные запуска
    meta = {
        "input_file": os.path.abspath(md_path),
        "active_schemas": active_schemas,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "window_chars": window_chars,
        "overlap_chars": overlap_chars,
        "mock": mock,
        "fragments_count": len(all_frags),
        "run_dir": os.path.abspath(run_dir),
        "run_id": run_id,
        "ts": time.time(),
    }
    with open(os.path.join(run_dir, "run.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(meta, ensure_ascii=False, indent=2))

    print(f"[OK] Saved fragments to {jsonl_path} and annotated markdown to {annotated_path}")
    return run_dir


# --------- CLI ---------
def main():
    parser = argparse.ArgumentParser(description="Boldsea Semantic Segmenter")
    parser.add_argument("md", help="Путь к входному .md")
    parser.add_argument("--config", help="YAML/JSON с активными схемами и параметрами LLM", default=None)
    parser.add_argument("--active-schemas", help="Через запятую: Definition,Comparison,...", default=None)
    parser.add_argument("--model", default="gpt-5-pro", help="Имя модели LLM")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=1800)
    parser.add_argument("--window-chars", type=int, default=6000)
    parser.add_argument("--overlap-chars", type=int, default=600)
    parser.add_argument("--outdir", default="out")
    parser.add_argument("--mock", action="store_true", help="Офлайн эвристики вместо LLM")
    args = parser.parse_args()

    active_schemas: List[str] = [
        "Definition",
        "Causal Relation",
        "Application Context",
        "Example",
        "Architectural Component",
        "Technical Process",
        "Algorithm",
        "Conceptual Model",
        "Principle",
        "Problem Solution",
        "Limitations And Challenges",
        "Functionality",
        "Capabilities",
        "System Integration",
        "Component Interaction",
        "Use Case",
        "Concept Implementation",
        "Code Snippet",
        "Enumeration",
        "Table Analysis",
        "Advantage Disadvantage",
    ]

    model = args.model
    temperature = args.temperature
    max_tokens = args.max_tokens
    window_chars = args.window_chars
    overlap_chars = args.overlap_chars

    if args.config:
        cfg = load_config(args.config) or {}
        active_schemas = cfg.get("active_schemas", active_schemas)
        llm_cfg = cfg.get("llm", {})
        model = llm_cfg.get("model", model)
        temperature = float(llm_cfg.get("temperature", temperature))
        max_tokens = int(llm_cfg.get("max_tokens", max_tokens))
        win_cfg = cfg.get("windows", {})
        window_chars = int(win_cfg.get("window_chars", window_chars))
        overlap_chars = int(win_cfg.get("overlap_chars", overlap_chars))

    if args.active_schemas:
        active_schemas = [s.strip() for s in args.active_schemas.split(",") if s.strip()]

    # Валидация схем
    for s in active_schemas:
        if s not in SCHEMA_LIBRARY:
            print(f"[WARN] Неизвестная схема '{s}' — будет проигнорирована LLM-ом.", file=sys.stderr)

    run_pipeline(
        md_path=args.md,
        outdir=args.outdir,
        active_schemas=active_schemas,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        window_chars=window_chars,
        overlap_chars=overlap_chars,
        mock=args.mock,
    )


if __name__ == "__main__":
    main()
