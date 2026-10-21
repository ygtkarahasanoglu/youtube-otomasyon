---
name: yorum-yanit
description: Pulls public comments of a video (no API key), classifies them, drafts short English replies in the channel voice, flags spam, and summarizes in Turkish for the user with video ideas. Never posts replies.
allowed-tools: Bash(python *) Bash(py *)
---

```bash
python "${CLAUDE_SKILL_DIR}/scripts/yorum_cek.py" "<video link>" --max 300 --out "videolar/<folder>/yorumlar/<date>"
```
(Private videos have no public comments; run after the user publishes.)

Classify: question · praise · correction · disagreement · video idea · spam/scam · abuse. Reply priority: corrections and questions first. Replies: 1-2 sentences, friendly, factual (check `arastirma.md`); thank corrections and fix in pinned comment if valid. Spam/scam/abuse: recommend remove/hide, no reply.

Output `videolar/<folder>/yorumlar.md`: table (comment, type, action, reply draft). Turkish summary to the user: 3 main themes, top 3 replies to post, new ideas (added to `arastirma/video-havuzu.md`).
