---
name: video2md-revise
description: Revise a video2md ASR draft into readable Chinese while retaining factual meaning and segment timing. Use after transcription when the user asks to fix spoken-language issues, typos, disfluencies, or punctuation.
---

# video2md Revise

Read `transcript.json` from the ASR stage and produce a separate `revised.json`. Keep the segment schema `id`, `start`, `end`, `text`; only replace `text` and add an optional `notes` field for unresolved audio or editorial uncertainty.

Use **evidence-gated minimal edits by default**. Make a textual change only when both conditions hold: (1) it preserves the stated facts, causality, stance, names, numbers, quotations and political wording; and (2) the correction is independently determined by adjacent context, a fixed expression, or a mechanical repetition. Do not rewrite a grammatical sentence merely for a more literary style. Do not invent missing content or silently "correct" facts that need source/audio verification.

When a phrase is ambiguous, retain the closest audible wording and mark it in `notes` rather than guessing. Do not delete a non-adjacent repetition merely because it sounds redundant; it may be emphasis or part of the source wording. Do not use video subtitles, a reference transcript, or later segments as hidden ground truth for a rewrite. Do not merge segments merely to improve prose: the structure stage owns document-level grouping.

Report the output path and any unresolved passages. This skill produces an editable transcript, not the final Markdown document.
