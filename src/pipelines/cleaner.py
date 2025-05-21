# cleaner.py  (full overwrite is fine)
import sys, pathlib, subprocess, shutil, os, json
wav_in  = pathlib.Path(sys.argv[1])
wav_out = wav_in.with_suffix(".clean.wav")

# -- 1) ensure WAV 16 kHz mono
tmp = wav_in.with_suffix(".tmp.wav")
if wav_in.suffix.lower() in {".flac", ".m4a", ".mp3"}:
    subprocess.run(["ffmpeg", "-y", "-i", str(wav_in), str(tmp)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    src = tmp
else:
    src = wav_in

# -- 2) high-pass + resample via SoX (if available)
if shutil.which("sox"):
    subprocess.run(
        ["sox", str(src), str(wav_out), "rate", "16k", "highpass", "300"],
        check=True)
else:
    wav_out.write_bytes(src.read_bytes())

print(json.dumps({"clean": str(wav_out)}))
