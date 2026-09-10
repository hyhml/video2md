---
name: video2md
description: Orchestrate a local video-to-Markdown workflow through transcription, spoken-language revision, and document structuring. Use when the user asks to turn a local video or audio recording into an editable, structured document.
---

# video2md workflow

Route work through the adjacent skills in this order:

1. Use `video2md-asr` to create `<input>.asr/transcript.json`.
2. Use `video2md-revise` to create `<input>.asr/revised.json`.
3. Use `video2md-structure` to create `<input>.asr/document.md`.

Honor a narrower request: if the user asks only for a transcript, stop after ASR; if they supply a transcript and ask for cleanup, begin at revision; if they ask only for Markdown organization, begin at structure. Say which stage is being skipped and preserve every earlier artifact.

Default to Paraformer-zh for ASR speed. Use Nano only when quality is explicitly preferred or the user accepts the resource tradeoff. Before each mutating stage, avoid overwriting existing output unless the user explicitly requests it; write a distinct named artifact instead.

The controller must not claim ASR text is verified. Surface ambiguous audio, names, numbers, and source-dependent claims for review. The final handoff is `document.md` together with the retained ASR and revision JSON artifacts.
