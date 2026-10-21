---
name: kalite-kontrol
description: Independent two-stage quality control — before production (facts vs sources, originality, YouTube policy, promise fit, structure) and after production (preview frames, captions, thumbnails, chapters, duration). Writes denetim.md and ends with KARAR HAZIR or DÜZELT.
allowed-tools: Bash(python *) Bash(py *)
---

# Quality control

## Stage A — before production (`senaryo.json` + `arastirma.md`)
1. **Facts:** every number in `metin`, `grafik`, `kule` exists in `arastirma.md` with a source; estimates are spoken as estimates ("about", "roughly") and charts say "estimate".
2. **Promise:** title + thumbnail promise is confirmed in the first 20 s and fully delivered.
3. **Originality / inauthentic-content risk:** not a reworded competitor script; has an insider note and at least one own analysis visual (cost tower or chart); structure differs from the last 3 videos (compare their `senaryo.json`); no templated filler lines.
4. **Policy & legal:** no investment/health advice, no defamation (claims attributed), no real-person deepfakes, AI realism → `yapay_icerik_beyani` set correctly, no logos as main visual.
5. **Craft:** 1,300-1,800 words, 30-55 scenes, every open loop closed, ≥ 3 chapters, visual mix per `senaryo-json` rules, no repeated `arama`.

## Stage B — after production
1. Read `onizleme.jpg`: each frame matches its scene's narration; no fallback text cards (`_yedek`) left; no watermarks or odd AI artifacts.
2. Read `altyazi.srt` start and a middle part: no garbage; names spelled correctly.
3. `zaman_cizelgesi.json`: duration 8-12 min; `bolumler_gecerli: true`.
4. Thumbnails `_mini.png` readable; text doesn't duplicate the title.
5. Shorts exist, ≤ 60 s.
6. If `dagitim/` exists: 3 Reels 20-60 s, covers readable, Instagram captions have no URLs, no engagement bait, 3-5 hashtags, every number is in the script.

Write `videolar/<folder>/denetim.md`: table (check | PASS/FIX | evidence), max 5 concrete fixes (scene id + what to change). Last line exactly `KARAR: HAZIR` or `KARAR: DÜZELT`.
