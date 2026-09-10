---
name: video2md-asr
description: Transcribe a local video or audio file into a Chinese draft with video2md. Use when the user wants speech-to-text, a transcript, or coarse subtitles; do not use for prose revision or Markdown structuring alone.
---

# video2md ASR

Use the local `video2md-asr` command to create the first-stage transcript. The default model is Paraformer-zh for speed. Switch to `--model nano` only when the user asks for higher transcription quality or the material has enough GPU memory (about 4 GiB in the recorded benchmark).

Before running, confirm that the input is a local media file and that `ffmpeg` is available for video/non-WAV input. Do not upload the media or substitute a cloud ASR service unless the user asks.

Run without `--overwrite` by default. Its output directory is `<input-stem>.asr/` unless the user specifies `--output`.

```bash
video2md-asr /absolute/path/video.mp4
video2md-asr /absolute/path/video.mp4 --model nano
```

The handoff artifact is `transcript.json`, whose segments have `id`, `start`, `end`, and `text`. Treat it as an ASR draft: preserve the original output and use a new artifact for later revision or structure work. `transcript.srt` has fixed-chunk coarse timing, not word-level alignment.

If the command is unavailable, locate the `video2md` user package and install it in an isolated environment; do not assume model weights are committed to the repository. State any unmet local prerequisite plainly rather than silently changing models.
