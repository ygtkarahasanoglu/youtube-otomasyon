---
name: transkript-cek
description: Downloads the subtitles of a public YouTube video (no video download) as SRT/text to study how a successful video is structured. Use for competitor analysis only; never reuse their sentences.
argument-hint: "[youtube link]"
allowed-tools: Bash(python *) Bash(py *)
---

```bash
python "${CLAUDE_SKILL_DIR}/scripts/transkript.py" "<link>" --out-dir arastirma/transkript
```
Study: hook type, section order, where numbers appear, how loops open/close. Summarize the structure in your own words in `arastirma.md`. Do not paste their text into our script.
