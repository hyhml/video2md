"""Extract a fixed, representative ASR revision prompt test set."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = Path("/home/hyhml/codex/biancheng/whisper-benchmark/runs/v0.2.0/fun-asr-nano-2512/transcript.json")
REFERENCE = Path("/home/hyhml/codex/biancheng/whisper-benchmark/reference.json")
SEGMENT_IDS = {1, 7, 11, 18, 23, 24, 26, 28}
TIMES = {15.0, 194.99, 314.98, 524.96, 674.95, 704.95, 764.95, 824.94}


def main() -> None:
    transcript = json.loads(SOURCE.read_text(encoding="utf-8"))
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    sample = {
        "language": "zh",
        "segments": [item for item in transcript["segments"] if item["id"] in SEGMENT_IDS],
    }
    captions = [item for item in reference["captions"] if item["time"] in TIMES]
    (ROOT / "stress-input.json").write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "stress-reference.json").write_text(json.dumps({"captions": captions}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
