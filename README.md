# boldsea demo kit (v0.1)

Минимальный рабочий комплект **код + артефакты** для демонстрации подхода *boldsea*:
- событийная семантика,
- темпоральный DAG,
- простая сборка IR (BOP — Boldsea Operational Profile) из авторского описания,
- CLI для компиляции и базовой валидации.

> Примечание: файл `examples/boldsea.onto.yaml` записан в виде **JSON, который является валидным YAML**.  
> Это позволяет запускать комплект без внешних зависимостей (без `PyYAML`).

## Состав

```
boldsea_package/
├── README.md
├── boldsea_cli.py
├── dsl_to_yaml.py
├── onto_build.py
├── bop/
│   └── bop.schema.json
└── examples/
    ├── boldsea.onto.yaml          # авторинг (сабсет Definition/Comparison/Architectural Component + базовые термины)
    ├── boldsea.ir.json            # собранный IR (результат компиляции)
    ├── fragments.demo.json
    └── fragments.from_pdf.json
```

## Быстрый старт

1) Скомпилировать авторинг → IR (BOP):
```bash
python boldsea_cli.py compile examples/boldsea.onto.yaml -o examples/boldsea.ir.json
```

2) Проверить структуру IR (простая встроенная проверка):
```bash
python boldsea_cli.py validate examples/boldsea.ir.json
```

3) (Опционально) Конвертировать простейший DSL → onto.yaml:
```bash
# пример: читаем из файла и пишем YAML/JSON
python dsl_to_yaml.py --in examples/example.dsl --out examples/generated.onto.yaml
```

## Что такое BOP (Boldsea Operational Profile)

IR фиксирует:
- `entities` — ключевые сущности предметной области и действий;
- `properties` — атрибуты/отношения/акты с доменом/ранжом/кардинальностями;
- `acts` — исполняемые шаги (упрощённо), с `actor_role`, `conditions`, `effects`;
- `authoring` — разделы *Definition / Comparison / ArchitecturalComponent / base_terms* (как есть).

Формальное описание — в `bop/bop.schema.json` (JSON Schema, облегчённая).

## Лицензия и назначение

Комплект предназначен для **демо/прототипирования** и свободной адаптации.  
Код написан без внешних зависимостей (стандартная библиотека Python 3.8+).

