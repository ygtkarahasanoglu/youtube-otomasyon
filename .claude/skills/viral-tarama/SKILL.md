---
name: viral-tarama
description: Lists videos of niche channels and finds outliers (views ≥ 3x the channel's own median) to learn which topics and angles work. Reads public listings only, downloads no video. Use for competitive research and topic ideas.
argument-hint: "[channel links]"
allowed-tools: Bash(python *) Bash(py *)
---

# Outlier scan

Reference channels to start with (business explainers): Company Man, Modern MBA, Wendover Productions, Business Insider, CNBC Make It, Logically Answered, The Hustle-style channels. Add smaller channels too (outlier logic works at any size).

```bash
python "${CLAUDE_SKILL_DIR}/scripts/kanal_cek.py" @CompanyMan @ModernMBA --limit 60 --out arastirma/veri/kanallar.json
python "${CLAUDE_SKILL_DIR}/scripts/outlier.py" "arastirma/veri/*.json" --min 3 --out arastirma/outlier.md
```
Requires `yt-dlp`. If it fails, use web search for the channels' popular videos instead; never invent view counts.
Use outliers for **ideas and angles**, never to copy scripts, structure verbatim, footage or thumbnails.
