import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'services' / 'api'))
from engine import Core
c=Core(str(ROOT / 'data' / 'state.db'))
out=c.proof()
assert out['ok'] is True, out
print('PASS', list(out.keys()))
