---
name: video2md-revise
description: Revise a video2md ASR draft into readable Chinese while retaining factual meaning and segment timing. Use after transcription when the user asks to fix spoken-language issues, typos, disfluencies, or punctuation.
---

# video2md Revise

Read `transcript.json` from the ASR stage and produce a separate `revised.json`. Keep the segment schema `id`, `start`, `end`, `text`; only replace `text` and add an optional `notes` field for unresolved audio or editorial uncertainty.

Correct clear ASR errors, false starts, filler words, punctuation, and spoken-language constructions when the intended wording is evident. Preserve claims, uncertainty, proper nouns, numbers, quotations, political terms, and the speaker's stance. Do not invent missing content or silently "correct" facts that need source/audio verification.

When a phrase is ambiguous, retain the closest audible wording and mark it in `notes` rather than guessing. Do not merge segments merely to improve prose: the structure stage owns document-level grouping.

Report the output path and any unresolved passages. This skill produces an editable transcript, not the final Markdown document.
