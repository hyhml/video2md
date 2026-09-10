# 工作流架构

```text
本地视频/音频
    │
    ▼
[01 asr] 语音转文字 ──► transcript.txt / transcript.srt / transcript.json
    │
    ▼
[02 revise] 口语修订（后续独立模块）
    │
    ▼
[03 structure] 合理分段与 Markdown 组织（后续独立模块）
```

## 01 asr 的稳定接口

输入：本地媒体文件；可选模型、设备、本地模型目录、切片秒数。

输出：

- `transcript.txt`：按粗切片换行的原始转写；不进行文案润色。
- `transcript.srt`：同一文本的粗时间轴，不能作为逐词对齐字幕。
- `transcript.json`：供下一环节消费的 `language` 与 `segments[{id,start,end,text}]`。
- `metadata.json`：模型、设备、版本、输入路径和输出参数。

后续环节应读取 `transcript.json`，保留 `id/start/end`，并把修订后的文本写到新的工件目录，不能静默覆盖 ASR 原文。

## 当前模型策略

- `paraformer`（默认）：低显存、极快，适合批量初稿和快速预览。
- `nano`：质量优先，适合正式文稿前的首轮转写；对 6 GiB 显存可运行，但更接近资源上限。

不在用户包中保留 Whisper、Qwen 等基线。它们的评测结果在基准目录中，以免把用户安装和研发试验耦合。
