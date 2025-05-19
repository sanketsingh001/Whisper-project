import regex as re, pathlib, sys
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

text = pathlib.Path(sys.argv[1]).read_text()
custom = {
    "AADHAAR": r"\b\d{4}\s\d{4}\s\d{4}\b",
    "PAN": r"\b[A-Z]{5}\d{4}[A-Z]\b",
}
for patt in custom.values():
    text = re.sub(patt, "XXXX", text)

ae, an = AnalyzerEngine(), AnonymizerEngine()
entities = ae.analyze(text=text, language="en")
redacted = an.anonymize(text, entities).text
out = pathlib.Path(sys.argv[1]).with_suffix('.redacted.txt')
out.write_text(redacted)
print({"redacted": str(out)})
