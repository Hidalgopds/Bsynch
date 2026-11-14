"""Runs every test file and says if anything failed.  Run:  python tests/run_all.py"""
import glob
import os
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
failed = []
for f in sorted(glob.glob(os.path.join(here, "test_*.py"))):
    r = subprocess.run([sys.executable, "-W", "ignore", f], capture_output=True, text=True, cwd=here)
    lines = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip() and "Warning" not in ln and "warnings.warn" not in ln]
    print("\n".join(lines[-15:]) if r.returncode else (lines[-1] if lines else os.path.basename(f) + ": no output"))
    if r.returncode:
        failed.append(os.path.basename(f))
print("ALL PASSED" if not failed else "FAILED: " + ", ".join(failed))
sys.exit(1 if failed else 0)
