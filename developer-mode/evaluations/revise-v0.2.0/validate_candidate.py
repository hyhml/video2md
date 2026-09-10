"""Reject revision candidates that do not preserve the input segment identity."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))["segments"]
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))["segments"]
    if len(source) != len(candidate):
        raise SystemExit("segment count changed")
    for original, revised in zip(source, candidate):
        if any(original[key] != revised[key] for key in ("id", "start", "end")):
            raise SystemExit(f"identity changed at segment {original['id']}")
        if not revised["text"].strip():
            raise SystemExit(f"empty revised text at segment {original['id']}")
    print(f"valid candidate: {len(candidate)} segments")


if __name__ == "__main__":
    main()
