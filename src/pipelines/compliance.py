import yaml, regex as re, sys, json, pathlib

rules_yml = pathlib.Path("src/rules.yml")
rules = yaml.safe_load(rules_yml.read_text()) if rules_yml.exists() else {"profanity": []}

txt   = pathlib.Path(sys.argv[1]).read_text().lower()
flags = []

if "this call is recorded" not in txt:
    flags.append("disclosure_missing")

for bad in rules.get("profanity", []):
    if re.search(fr"\b{bad}\b", txt):
        flags.append("profanity_detected")

print(json.dumps({"flags": flags}))
