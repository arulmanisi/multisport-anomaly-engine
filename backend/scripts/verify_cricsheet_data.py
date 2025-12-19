#!/usr/bin/env python
"""Verify local Cricsheet data presence and counts."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict


def count_matches(root: Path) -> Dict[str, int]:
    """Return counts of files per format under data/raw/cricsheet."""
    counts: Dict[str, int] = {}
    if not root.exists():
        return counts
    for fmt_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        fmt = fmt_dir.name
        files = [p for p in fmt_dir.iterdir() if p.is_file()]
        counts[fmt] = len(files)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Cricsheet data availability.")
    parser.add_argument(
        "--min",
        type=int,
        default=1,
        help="Minimum total files expected across formats (default: 1)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/raw/cricsheet"),
        help="Root folder for Cricsheet raw data.",
    )
    args = parser.parse_args()

    counts = count_matches(args.root)
    total = sum(counts.values())

    if not counts or total < args.min:
        print(f"No sufficient Cricsheet data found under {args.root}. Total files: {total}.")
        print("Ensure you have unzipped the JSON archives into data/raw/cricsheet/<format>/")
        raise SystemExit(1)

    print(f"Cricsheet data check OK. Total files: {total}")
    for fmt, cnt in counts.items():
        print(f"  {fmt}: {cnt} files")


if __name__ == "__main__":
    main()
