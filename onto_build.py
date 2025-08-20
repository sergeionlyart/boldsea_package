# -*- coding: utf-8 -*-
"""
onto_build.py — минимальная сборка IR (BOP) из авторского YAML/JSON (JSON совместим с YAML).
Без внешних зависимостей: сначала пробует JSON, затем (если доступен) PyYAML.
"""

import json, io

def _read_text(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_authoring(path):
    """
    Загружает авторинг из файла. Порядок:
    1) JSON
    2) YAML (если установлен модуль `yaml`)
    """
    raw = _read_text(path)
    # сначала пробуем JSON (файл examples/boldsea.onto.yaml содержит JSON, валидный как YAML)
    try:
        return json.loads(raw)
    except Exception:
        pass
    # пробуем YAML, если доступен
    try:
        import yaml  # type: ignore
        return yaml.safe_load(raw)
    except Exception as e:
        raise RuntimeError("Не удалось разобрать файл как JSON или YAML: %s" % e)

def compile_ir(onto):
    """
    Сборка простого IR (Boldsea Operational Profile).
    - Копирует сущности/свойства/акты 'как есть' (нормализует недостающие поля).
    - Добавляет простую статистику meta.counts.
    """
    entities = []
    for e in onto.get("entities", []):
        entities.append({
            "id": e.get("id"),
            "label": e.get("label", e.get("id")),
            "kind": e.get("kind", "Entity"),
            "notes": e.get("notes","")
        })

    props = []
    for p in onto.get("properties", []):
        props.append({
            "id": p.get("id"),
            "label": p.get("label", p.get("id")),
            "type": p.get("type","Attribute"),
            "domain": p.get("domain"),
            "range": p.get("range"),
            "datatype": p.get("datatype"),
            "cardinality": p.get("cardinality"),
            "constraints": p.get("constraints",{})
        })

    acts = []
    for a in onto.get("acts", []):
        acts.append({
            "id": a.get("id"),
            "label": a.get("label", a.get("id")),
            "actor_role": a.get("actor_role",""),
            "conditions": list(a.get("conditions",[])),
            "effects": list(a.get("effects",[])),
        })

    ir = {
        "version": "0.1",
        "entities": entities,
        "properties": props,
        "acts": acts,
        "authoring": onto.get("authoring",{}),
        "meta": {
            "counts": {
                "entities": len(entities),
                "properties": len(props),
                "acts": len(acts)
            }
        }
    }
    return ir

def save_ir(ir_dict, path):
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(ir_dict, f, ensure_ascii=False, indent=2)
