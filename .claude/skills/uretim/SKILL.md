---
name: uretim
description: Runs and troubleshoots the automated production pipeline (python -m hat) — voice, visuals, video, thumbnails, Shorts — checks budget, inspects the preview and replaces weak visuals cheaply. Use after the script passes pre-production QC.
allowed-tools: Bash(python *) Bash(py *) Bash(ffmpeg *) Bash(ffprobe *)
---

# Production

1. **Preflight:** `python -m hat kontrol` (fix anything EKSIK first). Estimate cost from `senaryo.json` (ai_gorsel×0.03 + ai_video×0.35 + voice chars/1000×0.22). If above `ayarlar.json → butce.video_basina_max_usd`, reduce AI scenes or ask the user.
2. **Run:** `python -m hat uret "videolar/<folder>"` (5-20 min). Steps can be run alone: `--adim ses`, `--adim gorsel`, `--adim video`, `--adim thumbnail`, `--adim shorts`. Free test: `--ses edge`.
3. **Inspect:** Read `onizleme.jpg` (one frame per scene) and `thumbnail-a.jpg`, `-b`, `-c` and their `_mini.png`. Look for: visual not matching the narration, low-quality/odd AI image, same-looking clips back to back, text cut off, fallback text cards (`*_yedek.png` means the source failed).
4. **Fix cheaply:** edit only the affected scene's `gorsel` in `senaryo.json` (new `arama`, better `prompt`, or switch `stok` ↔ `ai_gorsel`) and re-run `python -m hat uret ...`. Unchanged voice and visuals are cached — no extra cost. Changing `metin` re-voices only that scene.
5. **Report:** duration (`zaman_cizelgesi.json`), cost (`python -m hat maliyet <folder>`), files.

## Common errors
| Message | Fix |
| --- | --- |
| `... tanimli degil` | key missing in `.env` → run `/kurulum` step for that service |
| ElevenLabs 401/402 | wrong key or quota exhausted → tell the user; fallback `--ses edge` (free) only if the user agrees (voice changes) |
| fal.ai 401/403 | key or credit balance; fal.ai → Billing |
| `kaynak bulunamadi` | stock search returned nothing new → change `arama` to simpler/more common words |
| ffmpeg not found | `winget install Gyan.FFmpeg`, restart terminal |
| Unicode/path errors | project path contains Turkish characters → move folder to `C:\kanal\` |
