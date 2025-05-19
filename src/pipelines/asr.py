from faster_whisper import WhisperModel
import sys, pathlib
model = WhisperModel('large-v3', compute_type='float16')
wav = sys.argv[1]
segments, _ = model.transcribe(wav, language='en')
text = " ".join([s.text for s in segments])
path = pathlib.Path(wav).with_suffix('.txt')
path.write_text(text)
print("Transcribed ->", path)
