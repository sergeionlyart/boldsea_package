# Boldsea Semantic Segmenter

Скрипт для **семантического разбиения Markdown** на фрагменты по онтологии Boldsea.  
Подходит как первый шаг пайплайна **KG для RAG**, где фрагменты — атомы графа, связанные со схемами/терминами.

## Что делает
- Читает `.md`, режет на окна (по символам).
- Запрашивает LLM (или запускает офлайн-эвристику `--mock`) с **шаблонами схем**.
- Возвращает **минимально достаточные** фрагменты с полями:
  `id, start_char, end_char, text, schema_id, schema_type, entity_refs[], actors[], acts[], causals[], confidence, rationale<=300, overlaps[]`.
- Склеивает дубликаты (IoU), достраивает причинно-следственные ссылки `causals` по локальным span’ам.
- Экспортирует:
  - `fragments.jsonl`
  - `annotated.md` (невидимые HTML-комментарии с метками фрагментов)
  - логи LLM (`llm_calls.jsonl`), `run.json`

## Быстрый старт

```bash
# 1) Скачайте скрипт
python3 boldsea_segmenter.py path/to/input.md --mock

# 2) LLM-режим (нужен openai SDK и переменная OPENAI_API_KEY)
pip install openai
python3 boldsea_segmenter.py path/to/input.md --model gpt-5-pro
```

Выход сохраняется в `out/<run_hash>/` с учётом идемпотентности.

## Конфиг (опционально)

Пример `config.example.yaml`:

```yaml
active_schemas:
  - Definition
  - Causal Relation
  - Technical Process
  - Algorithm
  - Conceptual Model
  - Principle
  - Functionality
  - Capabilities
  - System Integration
  - Component Interaction
  - Use Case
  - Concept Implementation
  - Code Snippet
  - Enumeration
  - Table Analysis
  - Advantage Disadvantage

llm:
  model: gpt-5-pro
  temperature: 0.2
  max_tokens: 1800

windows:
  window_chars: 6000
  overlap_chars: 600
```

Запуск с конфигом:
```bash
python3 boldsea_segmenter.py input.md --config config.example.yaml
```

Или явным списком схем:
```bash
python3 boldsea_segmenter.py input.md \
  --active-schemas "Definition,Causal Relation,Algorithm,Use Case" \
  --mock
```

## Гарантии качества и правила
- **Строго семантические фрагменты**: заголовки/списки — только подсказка.
- **Минимально достаточные** границы (не шире, чем нужно для инстанцирования схемы).
- **Альтернативы** допускаются (в JSON-ответе LLM `alternatives`), но в текущей версии не записываются в JSONL — при желании добавьте экспорт.
- **Confidence ∈ [0,1]**, `rationale` усечён до 300 символов.
- **Структурные** сегменты без семантической сущности — **запрещены**.

## Как это подключить к Boldsea
- `fragments.jsonl` можно прогонять через загрузчик, создающий индивиды `Fragment` и реляции к `Term`/`Category` согласно вашим моделям.
- `schema_id` => сопоставляйте с Model: Fragment схемами (Definition, Comparison, ...).
- `causals` => рёбра DAG между фрагментами (рекомендуется валидировать, что причина идёт раньше результата).

## Примечания по реализации
- LLM промпт генерируется из **встроенной библиотеки схем**: `SCHEMA_LIBRARY` (см. код). При необходимости расширяйте/редактируйте.
- Для больших файлов используйте значения `--window-chars` 6–12k и `--overlap-chars` 10%.
- Если модель возвращает некорректный JSON, в `errors.log` остаётся сырой ответ; пайплайн продолжит работу.

## Лицензия
MIT
