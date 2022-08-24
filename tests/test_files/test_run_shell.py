import sys
print("python stdout")
sys.stdout.flush()
print("python stderr", file=sys.stderr)