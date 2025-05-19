import subprocess, sys, pathlib
wav = pathlib.Path(sys.argv[1])
clean = wav.with_suffix('.clean.wav')
subprocess.run(["sox", wav, clean, "highpass", "300"], check=True)

from rnnoise_wrapper import RNNoise
rn = RNNoise()
clean.write_bytes(rn.filter_wav(str(clean)))
print({"clean": str(clean)})
