import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS = os.path.join(ROOT, 'harness')
EXAMPLE = os.path.join(ROOT, 'examples', 'larchwick-secondary')
DATA_ROOM = os.path.join(EXAMPLE, 'data-room')
EXPECTED = os.path.join(EXAMPLE, 'expected')
CAP_TABLE = os.path.join(EXAMPLE, 'cap-table.json')

if HARNESS not in sys.path:
    sys.path.insert(0, HARNESS)


def run_tool(script, *args):
    """Run a harness script the way a user would, from the repo root. Returns (code, stdout)."""
    proc = subprocess.run(
        [sys.executable, os.path.join('harness', script)] + list(args),
        cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, proc.stdout


def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()
