"""
Architecture boundary checker.
Enforces:
1. Core layer cannot import API layer.
2. No legacy CAE imports.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

VIOLATIONS = []

def check_file(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(path))
        except SyntaxError:
            return

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # Helper to get module name
            module = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    check_import(path, alias.name, node.lineno)
            elif isinstance(node, ast.ImportFrom):
                check_import(path, node.module, node.lineno)

def check_import(path: Path, module: str, lineno: int):
    if not module:
        return

    # Rule: No CAE imports
    if "cae" in module.split("."):
        VIOLATIONS.append(f"{path}:{lineno} imports legacy 'cae': {module}")

    # Rule: Core cannot import API
    if "core" in path.parts and ("plaix.api" in module or "fastapi" in module):
        # Allow typing.TYPE_CHECKING guards if needed, but for now strict.
        VIOLATIONS.append(f"{path}:{lineno} (Core Layer) imports API/Framework: {module}")

def main():
    root = Path(__file__).resolve().parents[1]  # backend/
    
    # Scan plaix/
    for py_file in (root / "plaix").rglob("*.py"):
        check_file(py_file)

    if VIOLATIONS:
        print("Architecture violations found:")
        for v in VIOLATIONS:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print("Architecture check passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
