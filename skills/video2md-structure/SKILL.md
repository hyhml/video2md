---
name: video2md-structure
description: Turn a revised video2md transcript into a well-segmented Markdown document. Use after ASR revision when the user wants paragraphs, headings, readable flow, or Markdown output.
---

# video2md Structure

Read `revised.json` (or an explicitly user-approved raw `transcript.json` when revision is intentionally skipped). Create a separate `document.md`; do not overwrite ASR or revision artifacts.

Group adjacent segments by topic and argument flow. Add concise headings only where the source establishes a real topic transition. Preserve chronology, qualifications, quotations, names, numbers, and controversial/political wording. Do not turn a transcript into a summary unless the user requests a summary.

Use ordinary Markdown paragraphs. If timestamps are requested, add them at paragraph boundaries using the first segment's start time; otherwise omit them for readability. Flag passages whose meaning remains uncertain rather than smoothing them into invented prose.

Return the document path plus a short note on whether headings and timestamps were added.
