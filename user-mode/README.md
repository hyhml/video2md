# video2md ASR（用户模式）

把本地视频/音频转为中文初稿。默认 **Paraformer-zh**，适合速度优先；`--model nano` 使用 **Fun-ASR-Nano-2512**，适合质量优先。

## 安装

需要 Python 3.10+ 与 `ffmpeg`。建议使用独立虚拟环境；NVIDIA GPU 用户请先按 [PyTorch 官方安装页](https://pytorch.org/get-started/locally/) 安装与驱动匹配的 PyTorch。

```bash
python -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -e .
```

## 使用

```bash
# 默认：Paraformer-zh（速度最快）
video2md-asr /absolute/path/video.mp4

# 高质量：Fun-ASR-Nano-2512
video2md-asr /absolute/path/video.mp4 --model nano
```

默认在视频同级创建 `<文件名>.asr/`，其中包含 `transcript.txt`、`transcript.srt`、`transcript.json` 和 `metadata.json`。`srt` 为固定切片的粗时间轴，适合初步回看，非逐词精确字幕。

## 注意事项

- 首次运行会下载模型，需网络、磁盘空间和较长等待；模型权重不在本仓库内。
- 本版固定 Paraformer 到模型库 `v2.0.4`，Nano 使用其当前 `master`；实际模型标识会写入 `metadata.json`。升级模型前请先查看开发者模式中的新基准结论。
- `nano` 在本项目测试中质量更好，但约需 4 GiB 显存；默认 `paraformer` 约需 1.2 GiB。没有 GPU 时会退回 CPU，速度会明显下降。
- 识别结果是初稿。人名、缩写、数字和专有术语应回听核对；不要把它当作已经修订、分段或 Markdown 化的成稿。
- 默认不上传视频内容；仅在首次下载模型时访问模型仓库。

更多测试依据、版本记录和新模型接入规则在开发者模式的 `main` 分支中。
