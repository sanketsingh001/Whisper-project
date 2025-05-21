# src/pipelines/compliance.py
import sys, json, pathlib, yaml, regex as re
from rapidfuzz import fuzz      # pip install rapidfuzz

THRESH = 85                     # fuzzy match score

def fuzzy_in(needle: str, hay: str) -> bool:
    return fuzz.token_set_ratio(needle, hay) >= THRESH

txt_path = pathlib.Path(sys.argv[1])
txt      = txt_path.read_text().lower()

rules = yaml.safe_load(pathlib.Path("rules.yml").read_text())

missing = {}
for section, phrases in rules.items():
    not_found = [p for p in phrases if not fuzzy_in(p, txt)]
    if not_found:
        missing[section] = not_found

flags = []
if "disclaimer" in missing:
    flags.append("disclosure_missing")
if any(section == "overdue_amount" for section in missing):
    flags.append("amount_not_quoted")
if any(section == "closing" for section in missing):
    flags.append("no_closing_greeting")

print(json.dumps({"flags": flags, "missing": missing}))
