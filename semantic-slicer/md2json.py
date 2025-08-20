#!/usr/bin/env python3
# md2json.py

"""
pip install --upgrade openai
export OPENAI_API_KEY=sk-...   # или set в Windows PowerShell
python md2json.py path/to/input.md
# опционально:
python md2json.py teksty.md --max-o3-output 100000 --max-gpt41-output 16000
    
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from openai import OpenAI

ANSWER_DIR_NAME = "answer"


def _clip_max_tokens(model: str, requested: int | None) -> int | None:
    """Клиппинг max_output_tokens до безопасных значений на практике.
    Возвращает исходное значение, если None или в пределах лимита.
    Печатает предупреждение, если значение было уменьшено.
    """
    if requested is None:
        return None
    limits = {
        "o3-mini": 100000,   # практический потолок для вывода
        "gpt-4.1": 32768,    # типичный потолок вывода для 4.1
    }
    limit = limits.get(model)
    if limit is None:
        return requested
    if requested > limit:
        print(f"[warn] max_output_tokens for {model} clipped from {requested} to {limit}")
        return limit
    return requested


@dataclass
class Prompts:
    content_system: str
    json_system: str


def load_prompts(project_root: Path) -> Prompts:
    """
    Импортируем prompt.py из корня проекта и забираем prompt_doc, prompt_json_doc.
    """
    sys.path.insert(0, str(project_root))
    try:
        prompt_mod = importlib.import_module("prompt")
    except ModuleNotFoundError as e:
        raise SystemExit(
            f"Не найден prompt.py в корне проекта: {project_root}. Ошибка: {e}"
        ) from e

    content_system = getattr(prompt_mod, "prompt_doc", None)
    json_system = getattr(prompt_mod, "prompt_json_doc", None)

    if not isinstance(content_system, str) or not isinstance(json_system, str):
        raise SystemExit(
            "В prompt.py должны быть строки prompt_doc и prompt_json_doc."
        )

    return Prompts(content_system=content_system, json_system=json_system)


def read_markdown(md_path: Path) -> str:
    if not md_path.exists() or md_path.suffix.lower() != ".md":
        raise SystemExit(f"Укажите путь к существующему .md файлу: {md_path}")
    try:
        return md_path.read_text(encoding="utf-8")
    except Exception as e:
        raise SystemExit(f"Не удалось прочитать {md_path}: {e}") from e


def extract_output_text(resp: Any) -> str:
    """
    Нормальный путь — через resp.output_text (см. доку).
    На случай нестандартных ответов делаем осторожный фолбэк.
    """
    # Официальный SDK агрегирует текст в output_text
    # https://platform.openai.com/docs/guides/text
    text = getattr(resp, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    # Фолбэк: пройдёмся по output[*].content[*] и склеим куски type=="output_text"
    output = getattr(resp, "output", None)
    parts: list[str] = []
    if isinstance(output, list):
        for item in output:
            content = item.get("content") if isinstance(item, dict) else getattr(item, "content", None)
            if isinstance(content, list):
                for c in content:
                    ctype = c.get("type") if isinstance(c, dict) else getattr(c, "type", None)
                    if ctype == "output_text":
                        text_piece = c.get("text") if isinstance(c, dict) else getattr(c, "text", None)
                        if isinstance(text_piece, str):
                            parts.append(text_piece)
    if parts:
        return "".join(parts).strip()

    raise RuntimeError("Не удалось извлечь текст из ответа модели.")


def call_o3_mini(
    client: OpenAI,
    system_instruction: str,
    plain_text: str,
    max_output_tokens: int | None,
) -> str:
    """
    Шаг 1: контентная обработка через o3-mini (reasoning, Responses API).
    """
    mo = _clip_max_tokens("o3-mini", max_output_tokens)
    resp = client.responses.create(
        model="o3-mini",
        instructions=system_instruction,
        input=f"###\n{plain_text}",
        reasoning={"effort": "medium"},  # https://platform.openai.com/docs/guides/reasoning
        **({"max_output_tokens": mo} if mo else {}),
    )
    return extract_output_text(resp)


def call_gpt41_json(
    client: OpenAI,
    system_instruction: str,
    previous_answer_text: str,
    max_output_tokens: int | None,
) -> Dict[str, Any]:
    """
    Шаг 2: преобразование ответа в строгий JSON-объект через gpt-4.1 (JSON mode).
    """
    # Требование API: в input должно явно встречаться слово 'json'/'JSON'.
    json_input = (
        "ТРЕБОВАНИЕ: верни СТРОГО один валидный JSON-объект. "
        "Никакого текста/Markdown, только JSON.\n\n" 
        "### Входные данные:\n" + previous_answer_text
    )
    mo = _clip_max_tokens("gpt-4.1", max_output_tokens)
    try:
        resp = client.responses.create(
            model="gpt-4.1",
            instructions=system_instruction,
            input=json_input,
            # JSON mode для Responses API через text.format
            text={"format": {"type": "json_object"}},
            **({"max_output_tokens": mo} if mo else {}),
        )
    except TypeError:
        # Фолбэк для старых версий SDK: передаём поле через extra_body
        resp = client.responses.create(
            model="gpt-4.1",
            instructions=system_instruction,
            input=json_input,
            extra_body={"text": {"format": {"type": "json_object"}}},
            **({"max_output_tokens": mo} if mo else {}),
        )
    text = extract_output_text(resp)

    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Ответ не является JSON-объектом.")
        return data
    except json.JSONDecodeError as e:
        raise SystemExit(
            f"gpt-4.1 вернул текст, который не удалось распарсить как JSON: {e}\nТекст:\n{text}"
        ) from e


def ensure_answer_dir(project_root: Path) -> Path:
    ans_dir = project_root / ANSWER_DIR_NAME
    ans_dir.mkdir(parents=True, exist_ok=True)
    return ans_dir


def write_outputs(ans_dir: Path, stem: str, obj: Dict[str, Any]) -> tuple[Path, Path]:
    json_path = ans_dir / f"{stem}.json"
    md_path = ans_dir / f"{stem}.md"

    pretty = json.dumps(obj, ensure_ascii=False, indent=2)

    json_path.write_text(pretty + "\n", encoding="utf-8")
    md_path.write_text("```json\n" + pretty + "\n```\n", encoding="utf-8")

    return json_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Обработать .md через o3-mini и преобразовать результат в JSON через gpt-4.1."
    )
    parser.add_argument("md_path", type=str, help="Путь к входному .md файлу")
    parser.add_argument(
        "--max-o3-output",
        type=int,
        default=None,
        help="max_output_tokens для o3-mini (опционально)",
    )
    parser.add_argument(
        "--max-gpt41-output",
        type=int,
        default=None,
        help="max_output_tokens для gpt-4.1 (опционально)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    prompts = load_prompts(project_root)
    md_text = read_markdown(Path(args.md_path))

    # Ключ берётся из OPENAI_API_KEY (официально)
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Переменная окружения OPENAI_API_KEY не установлена.")

    client = OpenAI()

    # Шаг 1: o3-mini
    content_text = call_o3_mini(
        client=client,
        system_instruction=prompts.content_system,
        plain_text=md_text,
        max_output_tokens=args.max_o3_output,
    )

    # Шаг 2: gpt-4.1 → JSON
    json_obj = call_gpt41_json(
        client=client,
        system_instruction=prompts.json_system,
        previous_answer_text=content_text,
        max_output_tokens=args.max_gpt41_output,
    )

    # Сохранение результатов
    ans_dir = ensure_answer_dir(project_root)
    stem = Path(args.md_path).stem
    json_path, md_path = write_outputs(ans_dir, stem, json_obj)

    print(f"Готово.\nJSON: {json_path}\nMD:   {md_path}")


if __name__ == "__main__":
    main()