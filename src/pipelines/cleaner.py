import subprocess, sys, pathlib
inp = pathlib.Path(sys.argv[1])
outp = inp.with_suffix('.clean.wav')
subprocess.run(['sox', inp, outp, 'highpass', '300'], check=True)
