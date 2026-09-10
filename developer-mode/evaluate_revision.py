"""Compare an ASR transcript and its revision against fixed timed captions."""
from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
import re
import unicodedata

try:
    from opencc import OpenCC
    CC = OpenCC("t2s")
except ImportError:
    CC = None


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    if CC:
        text = CC.convert(text)
    return "".join(char for char in text if char.isalnum())


def best_substring(reference: str, hypothesis: str) -> tuple[int, str]:
    if not reference or not hypothesis:
        return max(len(reference), len(hypothesis)), hypothesis
    # Dynamic programming with zero-cost hypothesis prefix/suffix, matching
    # the v0.2 ASR benchmark rather than comparing against a whole window.
    m, n = len(reference), len(hypothesis)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        dp[i][0] = i
        for j in range(1, n + 1):
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + (reference[i - 1] != hypothesis[j - 1]),
            )
    end = min(range(n + 1), key=lambda j: dp[m][j])
    edits = dp[m][end]
    i, j = m, end
    while i:
        if j and dp[i][j] == dp[i - 1][j - 1] + (reference[i - 1] != hypothesis[j - 1]):
            i, j = i - 1, j - 1
        elif dp[i][j] == dp[i - 1][j] + 1:
            i -= 1
        else:
            j -= 1
    return edits, hypothesis[j:end]


def score(transcript: dict, captions: list[dict]) -> dict:
    rows = []
    for sample in captions:
        second = sample["time"]
        context = "".join(
            segment["text"] for segment in transcript["segments"]
            if segment["end"] >= second - 15 and segment["start"] <= second + 15
        )
        reference = normalize(sample["text"])
        edits, match = best_substring(reference, normalize(context))
        rows.append({
            "time": second, "reference": sample["text"], "edits": edits,
            "exact": edits == 0, "matched_normalized_text": match,
        })
    characters = sum(len(normalize(row["reference"])) for row in rows)
    edits = sum(row["edits"] for row in rows)
    return {
        "exact_caption_matches": sum(row["exact"] for row in rows),
        "caption_alignment_edits": edits,
        "caption_reference_characters": characters,
        "caption_sample_disagreement_ratio": edits / characters,
        "samples": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    before = json.loads(args.before.read_text(encoding="utf-8"))
    after = json.loads(args.after.read_text(encoding="utf-8"))
    captions = json.loads(args.reference.read_text(encoding="utf-8"))["captions"]
    result = {"before": score(before, captions), "after": score(after, captions)}
    result["delta"] = {
        "exact_caption_matches": result["after"]["exact_caption_matches"] - result["before"]["exact_caption_matches"],
        "caption_alignment_edits": result["after"]["caption_alignment_edits"] - result["before"]["caption_alignment_edits"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value if key == "delta" else {
        "exact_caption_matches": value["exact_caption_matches"],
        "caption_alignment_edits": value["caption_alignment_edits"],
        "caption_sample_disagreement_ratio": value["caption_sample_disagreement_ratio"],
    } for key, value in result.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
