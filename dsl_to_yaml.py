# -*- coding: utf-8 -*-
"""
dsl_to_yaml.py — конвертация очень простого DSL → авторинг (JSON/YAML совместим).
Пример DSL:

entity Person
  attr name: string
  relation spouse: Person

entity Document
  attr status: string

action Approve
  actor_role: manager
  condition: exists(Document)
  effect: set(Document.status,'approved')

Запуск:
  python dsl_to_yaml.py --in examples/example.dsl --out examples/generated.onto.yaml
"""
import io, json, argparse, re

def parse_dsl(text):
    entities = []
    properties = []
    acts = []

    cur_entity = None
    cur_action = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        m = re.match(r"entity\s+([A-Za-z_][A-Za-z0-9_]*)$", line, flags=re.I)
        if m:
            name = m.group(1)
            entities.append({"id": name, "label": name, "kind":"Entity"})
            cur_entity, cur_action = name, None
            continue

        m = re.match(r"action\s+([A-Za-z_][A-Za-z0-9_]*)$", line, flags=re.I)
        if m:
            name = m.group(1)
            entities.append({"id": f"Action_{name}", "label": name, "kind":"Action"})
            acts.append({"id": name, "label": name, "actor_role":"", "conditions":[], "effects":[]})
            cur_action, cur_entity = name, None
            continue

        if cur_entity:
            m = re.match(r"attr\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z_][A-Za-z0-9_]*)", line, flags=re.I)
            if m:
                pid, ptype = m.group(1), m.group(2)
                properties.append({"id": pid, "label": pid, "type": "Attribute", "domain": cur_entity, "datatype": ptype})
                continue
            m = re.match(r"relation\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z_][A-Za-z0-9_]*)", line, flags=re.I)
            if m:
                pid, rng = m.group(1), m.group(2)
                properties.append({"id": pid, "label": pid, "type": "Relation", "domain": cur_entity, "range": rng})
                continue

        if cur_action:
            m = re.match(r"actor_role\s*:\s*([A-Za-z_][A-Za-z0-9_-]*)", line, flags=re.I)
            if m:
                role = m.group(1)
                for a in acts:
                    if a["id"] == cur_action:
                        a["actor_role"] = role
                continue
            m = re.match(r"condition\s*:\s*(.+)$", line, flags=re.I)
            if m:
                cond = m.group(1).strip()
                for a in acts:
                    if a["id"] == cur_action:
                        a.setdefault("conditions", []).append(cond)
                continue
            m = re.match(r"effect\s*:\s*(.+)$", line, flags=re.I)
            if m:
                eff = m.group(1).strip()
                for a in acts:
                    if a["id"] == cur_action:
                        a.setdefault("effects", []).append(eff)
                continue

    return {
        "entities": entities,
        "properties": properties,
        "acts": acts,
        "authoring": {
            "Definition": [],
            "Comparison": [],
            "ArchitecturalComponent": [],
            "base_terms": []
        }
    }

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Входной файл DSL")
    ap.add_argument("--out", dest="out", required=True, help="Выходной YAML/JSON (JSON совместим с YAML)")
    args = ap.parse_args(argv)

    text = io.open(args.inp, "r", encoding="utf-8").read()
    data = parse_dsl(text)
    with io.open(args.out, "w", encoding="utf-8") as f:
        # Пишем JSON (валидный YAML)
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"OK: сгенерирован авторинг → {args.out}")

if __name__ == "__main__":
    main()
