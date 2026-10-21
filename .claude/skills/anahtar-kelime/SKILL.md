---
name: anahtar-kelime
description: Collects YouTube search autocomplete suggestions (English, US) to see how viewers phrase a topic; finds the main search phrase and related phrases for title and description. Use during topic selection and packaging.
allowed-tools: Bash(python *) Bash(py *)
---

# Search phrases

```bash
python "${CLAUDE_SKILL_DIR}/scripts/oneri_cek.py" "<topic>" --out "arastirma/anahtar-<topic>.md"
```
"Görülme" = how many expansion queries returned the phrase — a demand signal, **not** search volume. Never state volumes as numbers. If the tool fails (network), proceed with judgment and say so.
Pick 1 main phrase (goes into the title or first description line) and 3-5 related phrases (description, chapter names).
