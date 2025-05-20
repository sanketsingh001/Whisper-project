import subprocess, sys, pathlib, shutil

wav   = pathlib.Path(sys.argv[1])
clean = wav.with_suffix(".clean.wav")

def sox_available() -> bool:
    return shutil.which("sox") is not None

if sox_available():
    try:
        subprocess.run(["sox", str(wav), str(clean), "highpass", "300"], check=True)
    except subprocess.CalledProcessError:
        # fall-back: copy original
        clean.write_bytes(wav.read_bytes())
else:
    # SoX absent – just copy and continue
    clean.write_bytes(wav.read_bytes())

print({"clean": str(clean)})
