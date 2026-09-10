"""Build a self-contained prompt so a revision worker needs no tool reads."""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    text = """你是一次离线评测中的中文 ASR 修订执行器。不得调用工具、不得读取任何文件、不得访问网页；唯一允许的依据是以下指令与原始转写。完成阅读后直接输出 JSON，绝不输出计划、占位内容或解释。输出必须保留所有原始段落的 id、start、end，且 id 顺序不得变化。\n\n## 修订指令\n\n"""
    text += args.prompt.read_text(encoding="utf-8")
    text += "\n\n## 唯一允许的原始转写\n\n"
    text += args.input.read_text(encoding="utf-8")
    args.output.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
