"""Create the audited minimal-edit revision used by this evaluation only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# Each change is a clear local ASR error identifiable from immediate context.
# This is a controlled evaluation fixture, not a general-purpose reviser.
CHANGES = {
    23: [("DFS 存在被伪装的间接信贷", "BFS 存在被伪装的间接信贷")],
    24: [("格瓦拉拉则指出", "格瓦拉则指出"), ("方特提下放", "方特提出下放")],
    26: [("实施监控生产成本", "实时监控生产成本")],
    28: [("它与A F S派系", "他与 AFS 派系"), ("格瓦吉高的声望", "格瓦拉极高的声望")],
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    for segment in payload["segments"]:
        for old, new in CHANGES.get(segment["id"], []):
            if old not in segment["text"]:
                raise SystemExit(f"Expected text not found in segment {segment['id']}: {old}")
            segment["text"] = segment["text"].replace(old, new)
    payload["source"] = "Fun-ASR-Nano-2512 v0.2.0 transcript; controlled minimal-edit revision evaluation"
    payload["evaluation_changes"] = CHANGES
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
