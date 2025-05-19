from faster_whisper import WhisperModel
import sys, pathlib, json, datetime as dt
wav = pathlib.Path(sys.argv[1])
model = WhisperModel("large-v3", compute_type="float16")
text = " ".join(seg.text for seg, _ in model.transcribe(str(wav)))
txt = wav.with_suffix('.txt'); txt.write_text(text)
print(json.dumps({"txt": str(txt), "time": dt.datetime.utcnow().isoformat()}))
