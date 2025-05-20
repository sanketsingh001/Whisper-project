import subprocess, sys, pathlib

wav = pathlib.Path(sys.argv[1])
clean = wav.with_suffix('.clean.wav')

# Clean audio using SoX
subprocess.run(["sox", str(wav), str(clean), "highpass", "300"], check=True)

# If you want to use rnnoise_wrapper in the future, add here:
# from rnnoise_wrapper import RNNoise
# rn = RNNoise()
# clean.write_bytes(rn.filter_wav(str(clean)))
# print({"clean": str(clean)})

print({"clean": str(clean)})
