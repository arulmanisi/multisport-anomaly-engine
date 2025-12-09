"""Test configuration: ensure src/ is on sys.path for imports."""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = BACKEND_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
