"""Local Chinese ASR command used by the video2md user package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

import numpy as np

from . import __version__

SAMPLE_RATE = 16_000
MODEL_SPECS = {
    "paraformer": {
        "display_name": "Paraformer-zh large",
        "repository": "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
        "revision": "v2.0.4",
        "purpose": "speed",
    },
    "nano": {
        "display_name": "Fun-ASR-Nano-2512",
        "repository": "FunAudioLLM/Fun-ASR-Nano-2512",
        "revision": "master",
        "purpose": "quality",
    },
}


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1_000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def clean_text(text: str) -> str:
    return re.sub(r"<\|[^|]+\|>", "", str(text)).strip()


def clean_paraformer_text(text: str) -> str:
    text = clean_text(text)
    compact = text.replace(" ", "")
    cjk_count = len(re.findall(r"[\u3400-\u9fff]", compact))
    # The model can expose its character-token separator as literal spaces.
    return compact if compact and cjk_count / len(compact) > 0.7 else text


def decode_media(source: Path) -> np.ndarray:
    if not shutil.which("ffmpeg"):
        if source.suffix.lower() != ".wav":
            raise RuntimeError("找不到 ffmpeg。视频及非 WAV 音频需要 ffmpeg；请先安装并确保它在 PATH 中。")
        # Keep simple WAV-only use possible on minimal installations.  Video
        # decoding remains deliberately dependent on ffmpeg for predictability.
        import soundfile as sf
        import torch
        import torchaudio
        waveform, source_rate = sf.read(str(source), dtype="float32", always_2d=True)
        waveform = torch.from_numpy(waveform.T).mean(dim=0, keepdim=True)
        if source_rate != SAMPLE_RATE:
            waveform = torchaudio.functional.resample(waveform, source_rate, SAMPLE_RATE)
        return waveform.squeeze(0).to(dtype=torch.float32).numpy()
    process = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(source), "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "f32le", "pipe:1"],
        capture_output=True,
    )
    if process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"ffmpeg 无法读取输入：{detail}")
    audio = np.frombuffer(process.stdout, dtype=np.float32)
    if not len(audio):
        raise RuntimeError("输入中没有可识别的音频。")
    return audio


def select_device(requested: str) -> str:
    if requested != "auto":
        return requested
    import torch
    return "cuda:0" if torch.cuda.is_available() else "cpu"


def load_model(model_id: str, device: str, model_dir: Path | None):
    from funasr import AutoModel

    source = str(model_dir) if model_dir else MODEL_SPECS[model_id]["repository"]
    options = {"model": source, "device": device, "disable_update": True}
    if not model_dir:
        options["model_revision"] = MODEL_SPECS[model_id]["revision"]
    return AutoModel(**options)


def infer(model: Any, model_id: str, audio: np.ndarray) -> str:
    if model_id == "nano":
        import torch
        # Nano treats NumPy input ambiguously; a torch tensor is unambiguous.
        result = model.generate(
            input=torch.from_numpy(audio.copy()), cache={}, language="中文", itn=True,
            hotwords=[], batch_size=1, disable_pbar=True,
        )
        return clean_text(result[0]["text"])
    result = model.generate(input=audio, cache={}, batch_size_s=30, disable_pbar=True)
    return clean_paraformer_text(result[0]["text"])


def write_outputs(output: Path, records: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
    (output / "transcript.txt").write_text(
        "\n".join(record["text"] for record in records) + "\n", encoding="utf-8"
    )
    (output / "transcript.srt").write_text("\n\n".join(
        f"{record['id']}\n{timestamp(record['start'])} --> {timestamp(record['end'])}\n{record['text']}"
        for record in records
    ) + "\n", encoding="utf-8")
    (output / "transcript.json").write_text(
        json.dumps({"language": "zh", "segments": records}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Chinese ASR for video2md")
    parser.add_argument("input", type=Path, help="本地视频或音频文件")
    parser.add_argument("--model", choices=MODEL_SPECS, default="paraformer", help="默认 paraformer（速度）；nano（质量）")
    parser.add_argument("--output", type=Path, help="输出目录，默认 <输入名>.asr")
    parser.add_argument("--device", default="auto", help="auto、cuda:0 或 cpu")
    parser.add_argument("--model-dir", type=Path, help="已下载模型的本地目录，用于离线运行")
    parser.add_argument("--chunk-seconds", type=float, default=30, help="粗时间轴的固定切片秒数，默认 30")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已有输出目录中的同名文件")
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"找不到输入文件：{source}")
    if args.model_dir and not args.model_dir.expanduser().resolve().is_dir():
        raise SystemExit(f"找不到模型目录：{args.model_dir}")
    if args.chunk_seconds <= 0:
        raise SystemExit("--chunk-seconds 必须大于 0")

    output = args.output.expanduser().resolve() if args.output else source.with_name(source.stem + ".asr")
    output.mkdir(parents=True, exist_ok=True)
    protected = [output / name for name in ("transcript.txt", "transcript.srt", "transcript.json", "metadata.json")]
    if not args.overwrite and any(path.exists() for path in protected):
        raise SystemExit(f"输出已存在：{output}；如确认覆盖，请添加 --overwrite")

    device = select_device(args.device)
    print(f"解码：{source.name}", flush=True)
    audio = decode_media(source)
    print(f"加载模型：{MODEL_SPECS[args.model]['display_name']}（{device}）", flush=True)
    model_dir = args.model_dir.expanduser().resolve() if args.model_dir else None
    model = load_model(args.model, device, model_dir)
    chunk_samples = round(args.chunk_seconds * SAMPLE_RATE)
    records = []
    with (output / "segments.jsonl").open("w", encoding="utf-8") as progress:
        for index, start_sample in enumerate(range(0, len(audio), chunk_samples), 1):
            chunk = audio[start_sample:start_sample + chunk_samples]
            end_sample = start_sample + len(chunk)
            text = infer(model, args.model, chunk)
            record = {"id": index, "start": start_sample / SAMPLE_RATE, "end": end_sample / SAMPLE_RATE, "text": text}
            records.append(record)
            progress.write(json.dumps(record, ensure_ascii=False) + "\n")
            progress.flush()
            print(f"已完成 {index}：{record['end']:.1f}s", flush=True)

    metadata = {
        "tool": "video2md-asr",
        "tool_version": __version__,
        "input": str(source),
        "model_id": args.model,
        "model": MODEL_SPECS[args.model],
        "device": device,
        "sample_rate": SAMPLE_RATE,
        "chunk_seconds": args.chunk_seconds,
        "segment_count": len(records),
    }
    write_outputs(output, records, metadata)
    print(f"完成：{output}", flush=True)


if __name__ == "__main__":
    main()
