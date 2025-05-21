import sys, json, pathlib, yaml, regex as re

rules = yaml.safe_load(pathlib.Path("rules.yml").read_text())
txt    = pathlib.Path(sys.argv[1]).read_text().lower()

hits, total, detail = 0, 0, {}
for section, phrases in rules.items():
    total += 1
    found = any(re.search(re.escape(p), txt) for p in phrases)
    detail[section] = found
    if found:
        hits += 1

coverage = round(100 * hits / total, 1) if total else 0.0
print(json.dumps({"coverage": coverage, "detail": detail}))
