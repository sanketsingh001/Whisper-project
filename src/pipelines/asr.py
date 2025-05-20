from faster_whisper import WhisperModel
import sys, pathlib, json, datetime as dt
import torch

wav = pathlib.Path(sys.argv[1])

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # float16 only on GPU; use int8 on CPU to save RAM
    compute_type = "float16" if device == "cuda" else "int8"
    return WhisperModel("large-v3", device=device, compute_type=compute_type)

def transcribe_and_save(wav_path: pathlib.Path):
    model = load_model()
    segments, _ = model.transcribe(str(wav_path), beam_size=5, word_timestamps=False)

    txt_path = wav_path.with_suffix(".txt")
    with open(txt_path, "w", encoding="utf-8") as out_f:
        for seg in segments:
            # Universal access (Segment object or dict)
            if hasattr(seg, "text"):
                text = seg.text.strip()
            elif isinstance(seg, dict) and "text" in seg:
                text = seg["text"].strip()
            else:
                text = ""
            if text:
                out_f.write(text + "\n")

    print(json.dumps({"txt": str(txt_path),
                      "time": dt.datetime.utcnow().isoformat()}))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.pipelines.asr <file.wav>")
        sys.exit(1)
    transcribe_and_save(wav)
