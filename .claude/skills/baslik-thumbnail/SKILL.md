---
name: baslik-thumbnail
description: Writes the English packaging for a video — 10 title candidates linted and scored, 3 faceless thumbnail variants (text, accent word, price tag, background prompt) that differ in one variable for YouTube Test & Compare, description, tags, hashtags and Shorts titles — into senaryo.json. Use after the script is drafted.
allowed-tools: Bash(python *) Bash(py *)
---

# Title + thumbnail package

## Titles
1. Write 10 candidates from different angles: question, number, contrarian, comparison, "how X really makes money", "what it actually costs", "why X is so cheap/expensive".
2. Rules: ≤ 60 chars, key words in the first 40, sentence case or Title Case (no ALL CAPS sentences), a sourced number if possible, the video must fully deliver it.
3. Lint: write them to `videolar/<folder>/basliklar.txt` and run
   `python "${CLAUDE_SKILL_DIR}/scripts/baslik_lint.py" --file "videolar/<folder>/basliklar.txt" --thumb "<thumbnail text A>"`
4. Score 1-5: Curiosity · Clarity · Specificity · Search fit (main phrase from `anahtar-kelime`) · Honesty. Pick the best → `baslik`; next 2 → `baslik_alternatifleri`.

## Thumbnails (faceless; the pipeline renders them)
- `thumbnail.prompt`: ONE strong subject for the AI background, no text/logos/people's faces (e.g. "a single paper coffee cup on a dark counter, dramatic side light, close-up").
- `thumbnail.varyantlar` (3): `yazi` ≤ 4 words that ADD to the title (never repeat it), `vurgu` = the amber word, `etiket` = short price-tag text ("$5", "0.3%") or empty. The 3 variants differ in ONE variable only (e.g. same image, different text).
- After rendering, open `thumbnail-*_mini.png` with Read: if the text is unreadable at small size, shorten it.

## Description, tags
- `aciklama`: line 1-2 = the promise + main search phrase; then 3-4 sentence summary. (Chapters, sources and stock credits are appended automatically.)
- `etiketler`: 6-12 (main phrase, related phrases, company/product names). `hashtagler`: max 3.
- Shorts titles (`shorts[].baslik`): ≤ 70 chars, curiosity + topic.
