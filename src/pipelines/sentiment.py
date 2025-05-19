from transformers import pipeline
import sys, json
txt = pathlib.Path(sys.argv[1]).read_text()[:512]
clf = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2")
pred = clf(txt)[0]
score = pred["score"] if pred["label"] == "POSITIVE" else -pred["score"]
print(json.dumps({"sentiment": score}))
