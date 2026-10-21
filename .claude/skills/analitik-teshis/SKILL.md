---
name: analitik-teshis
description: Diagnoses a published video from YouTube Studio exports (impressions, CTR, average view duration, audience retention CSV, traffic sources) at 48 hours, 7 days and 28 days; finds where viewers leave and why using the script timeline, and updates the learning log.
allowed-tools: Bash(python *) Bash(py *)
---

# Analytics diagnosis

Ask the user (in Turkish, step by step) for: YouTube Studio → Content → the video → Analytics → "Advanced mode" → Audience retention → Export (CSV), plus a screenshot of the Reach tab (impressions, CTR). Files go to `videolar/<folder>/analiz/`.

```bash
python "${CLAUDE_SKILL_DIR}/scripts/retention_oku.py" "videolar/<folder>/analiz/<file>.csv" --sure <MM:SS> --srt "videolar/<folder>/altyazi.srt"
```
Map each drop to the scene in `zaman_cizelgesi.json` and its visual.

| Symptom | Likely cause | Owner |
| --- | --- | --- |
| Low impressions | topic demand / packaging | strateji-direktoru |
| CTR below channel average | title/thumbnail | paketleme-direktoru (start Test & Compare) |
| Big drop in first 30 s | hook doesn't confirm the promise | senarist |
| Steady slide mid-video | pacing, weak visuals, repetition | senarist + produksiyon |
| Spikes (rewatches) | strong moment → do more of it | senarist |

Write `analiz.md`; at day 28 add a row to `kanal/ogrenme-kaydi.md`. Compare with channel averages first; no conclusions from fewer than 5 videos ("early signal").
