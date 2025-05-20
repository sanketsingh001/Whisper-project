from faster_whisper import WhisperModel
import sys, pathlib, json, datetime as dt

wav = pathlib.Path(sys.argv[1])
model = WhisperModel("large-v3", device="cuda", compute_type="float16")  # use GPU!

segments = model.transcribe(str(wav))  # returns an iterator of segments
text = " ".join(segment.text for segment in segments)

txt = wav.with_suffix('.txt')
txt.write_text(text)
print(json.dumps({"txt": str(txt), "time": dt.datetime.utcnow().isoformat()}))
