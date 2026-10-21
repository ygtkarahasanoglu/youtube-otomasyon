---
name: reels-paketi
description: Builds the Instagram Reels + Facebook Reels package for one finished video — picks 3 vertical clips (the YouTube Shorts plus at most one Reels-only clip), writes platform-specific English captions and hashtags into senaryo.json → dagitim, renders extra clips, runs python -m hat dagitim and checks the result. Use after the long video and its Shorts exist.
allowed-tools: Bash(python *) Bash(py *) Bash(ffmpeg *) Bash(ffprobe *)
---

# Reels package (Instagram + Facebook)

Goal: every long video → 3 Reels on Instagram and Facebook that send viewers to the YouTube video. Settings: `ayarlar.json → dagitim`.

## 0. First time only (`dagitim.kurulum_tamam` is false)
Tell the user in Turkish, one step at a time, and wait for "tamam" after each:
1. Facebook Sayfası aç: facebook.com/pages/create → ad **Colossal Builds**, kategori "Media/News Company" ya da "Education".
2. Instagram hesabı aç: kullanıcı adı `@colossalbuilds` (doluysa kimlikteki yedekler) → Ayarlar → Hesap türü → **Profesyonel hesap → İçerik üreticisi**.
3. business.facebook.com (Meta Business Suite) → Ayarlar → Instagram hesabını Facebook Sayfasına bağla.
4. Instagram biyografisi: kimlikteki tagline + YouTube kanal linki (Biyografiyi düzenle → Bağlantı ekle).
5. Para kazanma: Facebook Sayfası → Profesyonel pano → **Para kazanma** bölümüne bak. "Content Monetization" görünüyorsa başvur; görünmüyorsa şimdilik sorun değil, takipçi arttıkça açılır.
Then set `dagitim.kurulum_tamam: true` (and the real handle/page name if different).

## 1. Pick 3 clips
- Start from `senaryo.json → shorts` (the YouTube Shorts, usually 2). They are already rendered in `shorts/short-N.mp4`.
- If there are fewer than `dagitim.reels_video_basina` clips, add Reels-only clips to `shorts` with `"youtube": false` (the uploader skips them; nothing else changes).
- Clip length = sum of the scenes' `sure` in `ses/zamanlar.json` + 0.1 s each. Target 20-45 s, never over 60 s.
- The 3 clips must have 3 different jobs:
  1. **Hook number** — the most surprising sourced number of the video.
  2. **From the buyer's desk** — the procurement insider note (the channel's originality signal; best for trust and follows).
  3. **Payoff or myth-buster** — the final answer or a common belief the video proves wrong.
- Scenes must make sense without the long video (no "as we saw", no "in this video"). Prefer `stok`/`arsiv`/`ai_*` scenes; a `grafik`/`kule` scene is fine only if it has ≤ 5 items (it gets small in vertical).
- `kanca` (first 2.5 s overlay, ≤ 6 words) must be different from the YouTube title.
- After adding clips render only the Shorts step (cached, free): `python -m hat uret "videolar/<folder>" --adim shorts`.

## 2. Write `senaryo.json → dagitim`
```json
"dagitim": {
 "klipler": [
  {"short": 1, "gun": 1, "kapak_sn": 1.0,
   "instagram": {"aciklama": "Hook line ≤ 125 chars\n\n2-4 short lines of value.\n\nFull breakdown on YouTube — link in bio.", "hashtagler": ["#superyacht", "#yachtbuilding", "#BelowTheWaterline"]},
   "facebook": {"aciklama": "Hook line\n\n1-3 short lines.", "hashtagler": ["#superyacht"]}}
 ]
}
```
- `short`: 1-based index in `shorts`. `gun`: days after the long video goes public (default 1, 3, 5). `kapak_sn`: second of the frame used as cover (default 1.0 — shows the `kanca` overlay).
- **Instagram caption:** line 1 = the hook in ≤ 125 characters (visible before "more"), with the main search words (Instagram search reads captions). Then 2-4 short lines. End with one genuine question OR "Full breakdown on YouTube — link in bio." No URLs. 3-5 hashtags: 1-2 topic (#superyacht, #shipping), 1-2 niche (#yachtrefit, #suezcanal), always `#BelowTheWaterline`. Never `#shorts`, `#fyp`, `#viral`.
- **Facebook caption:** same hook, shorter body, 1-3 hashtags. The pipeline appends "Full video: https://youtu.be/…" automatically once the long video is uploaded.
- English, channel voice (`kanal/kimlik.md`): calm, concrete, no hype words. Every number must already be in the script/`arastirma.md`.
- The three captions must not repeat the same sentences.

## 3. Build the package
`python -m hat dagitim "videolar/<folder>"` → `videolar/<folder>/dagitim/`:
`1-reel.mp4`, `1-kapak.jpg`, `1-instagram.txt`, `1-facebook.txt`, … and `PAYLAS.txt` (Turkish posting guide with dates).

## 4. Check
- Read every `N-kapak.jpg`: hook text readable, nothing cut off, not a black/transition frame. Otherwise change `kapak_sn` and re-run step 3.
- Durations in `PAYLAS.txt` are 20-60 s.
- Captions: no links on Instagram, no engagement bait, hashtags 3-5, no number that isn't in the script.

## Posting rules (for the report to the user)
- Order: YouTube long video goes public first (day 0). Reels on days 1, 3, 5.
- Time: US Eastern 12:00 → Türkiye 19:00 (EDT, March–early November) / 20:00 (EST, November–March).
- Meta Business Suite → **Oluştur → Reel** → choose both Instagram and Facebook → upload `N-reel.mp4` → paste caption → cover = `N-kapak.jpg` → AI label ON ("Yapay zekâ etiketi ekle") → **Planla**.
- Do not add music in Instagram (narration is already mixed; most popular songs aren't licensed for business accounts).
- After 7 days the user can screenshot Meta Business Suite → Insights for the `analist`.
