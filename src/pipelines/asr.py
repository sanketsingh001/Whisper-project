from faster_whisper import WhisperModel
import sys, pathlib, json, datetime as dt
import torch
import time, soundfile as sf

def load_model():
    device = "cuda"
    compute_type = "float16"
    return WhisperModel("large-v3", device=device, compute_type=compute_type)

def transcribe_and_save(wav_path: pathlib.Path):
    audio_sec = sf.info(wav_path).duration
    model = load_model()
    t0 = time.perf_counter()
    segments, _ = model.transcribe(
        str(wav_path),
        beam_size=5,
        task="translate",     # English output (Hinglish)
        language=None,
        word_timestamps=False
    )
    elapsed = time.perf_counter() - t0
    rtf = round(elapsed / audio_sec, 2)

    txt_path = wav_path.with_suffix(".txt")
    with open(txt_path, "w", encoding="utf-8") as out_f:
        for seg in segments:
            text = getattr(seg, "text", None) or (seg.get("text") if isinstance(seg, dict) else "")
            if text:
                out_f.write(text.strip() + "\n")
    # Improved confidence handling
    scores = []
    for seg in segments:
        val = getattr(seg, "avg_logprob", None)
        if val is None and isinstance(seg, dict):
            val = seg.get("avg_logprob")
        if val is not None:
            scores.append(val)
    confidence = sum(scores) / len(scores) if scores else None

    print(json.dumps({
        "txt": str(txt_path),
        "avg_logprob": confidence if confidence is not None else "null",
        "sec": round(elapsed, 2),
        "rtf": rtf,
        "time": dt.datetime.utcnow().isoformat()
    }))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.pipelines.asr <file.wav>")
        sys.exit(1)
    wav = pathlib.Path(sys.argv[1])
    transcribe_and_save(wav)
