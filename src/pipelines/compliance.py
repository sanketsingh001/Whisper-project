import yaml, regex as re, sys, json, pathlib
rules = yaml.safe_load(pathlib.Path("src/rules.yml").read_text())
txt = pathlib.Path(sys.argv[1]).read_text().lower()
flags = []
if "this call is recorded" not in txt:
    flags.append("disclosure_missing")
for bad in rules["profanity"]:
    if re.search(fr"\b{bad}\b", txt):
        flags.append("profanity_detected")
print(json.dumps({"flags": flags}))
