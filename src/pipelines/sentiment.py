from transformers import pipeline
import sys, json, pathlib

txt = pathlib.Path(sys.argv[1]).read_text()[:512]  # clip long calls
clf = pipeline("sentiment-analysis",
               model="distilbert-base-uncased-finetuned-sst-2-english",
               device=-1)
  # CPU; change to 0 for GPU

pred   = clf(txt)[0]
score  =  pred["score"] if pred["label"] == "POSITIVE" else -pred["score"]
print(json.dumps({"sentiment": score}))
