# -*- coding: utf-8 -*-
"""
boldsea_cli.py — простой CLI:
- compile <in> -o <out>
- validate <in>
"""
import argparse, json, io, os, sys

# локальный импорт onto_build из соседнего файла
sys.path.insert(0, os.path.dirname(__file__))
import onto_build

def _read_json(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_ir(ir):
    """
    Лёгкая проверка структуры IR без jsonschema:
    - наличие разделов;
    - уникальность id в entities/properties/acts по месту.
    Возвращает список проблем (пусто, если всё ок).
    """
    problems = []
    if "entities" not in ir:
        problems.append("Отсутствует ключ 'entities'")
    # уникальность id
    for key in ("entities","properties","acts"):
        seen = set()
        for idx, item in enumerate(ir.get(key,[])):
            _id = (item or {}).get("id")
            if not _id:
                problems.append(f"[{key}][{idx}] пустой или отсутствует id")
                continue
            if _id in seen:
                problems.append(f"[{key}] дубликат id: '{_id}'")
            seen.add(_id)
    return problems

def main(argv=None):
    p = argparse.ArgumentParser(description="boldsea CLI")
    sub = p.add_subparsers(dest="cmd")

    p_compile = sub.add_parser("compile", help="Скомпилировать авторинг → IR")
    p_compile.add_argument("input", help="Путь к авторингу (YAML/JSON)")
    p_compile.add_argument("-o","--out", required=True, help="Файл IR (JSON)")

    p_validate = sub.add_parser("validate", help="Проверить IR (базовая проверка)")
    p_validate.add_argument("input", help="IR (JSON)")

    args = p.parse_args(argv)

    if args.cmd == "compile":
        onto = onto_build.load_authoring(args.input)
        ir = onto_build.compile_ir(onto)
        onto_build.save_ir(ir, args.out)
        print(f"OK: сгенерирован IR → {args.out}")
        return 0

    elif args.cmd == "validate":
        ir = _read_json(args.input)
        problems = validate_ir(ir)
        if problems:
            print("Проблемы:")
            for pr in problems:
                print(" -", pr)
            return 2
        print("OK: IR выглядит корректно")
        return 0

    else:
        p.print_help()
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
