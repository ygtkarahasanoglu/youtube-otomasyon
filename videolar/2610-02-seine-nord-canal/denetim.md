# Denetim — Stage A (Pre-Production) — 2610-02-seine-nord-canal — ROUND 2

Scope: re-check only the 3 fixes required in round 1, plus a scan for any newly introduced issue. Re-read `senaryo.json` and `arastirma.md` in full. Confirmed: 42 scenes, 1,627 words (within 1,300-1,800), no duplicate `arama` strings.

| Check | Result | Evidence |
|---|---|---|
| Fix 1 — "Illustration" label on AI scenes | PASS | `s13.ekran_yazisi` = "Illustration — 25 m deep lock", `s14.ekran_yazisi` = "Illustration — 1.33 km viaduct", `s34.ekran_yazisi` = "Illustration — lock gate install". All three `ai_gorsel` scenes now carry the on-screen label per CLAUDE.md rule 6. |
| Fix 2 — s02 bridge-count overclaim | PASS | s02 now reads "...with seven locks lifting barges across the terrain. It's the biggest canal Europe has built in more than a hundred years" — the false "one bridge" framing is removed entirely. The accurate single-viaduct claim ("longest canal viaduct in Europe") is kept isolated to s14, where it's correct (SCSNE confirms 3 canal bridges total, Somme is the signature one). No longer contradicts `arastirma.md` §2/§4. |
| Fix 3 — s11/s12 lock-count direction contradiction | PASS | s11 still states "seven locks in total, including one junction lock." s12 now says only "Earlier versions of the design used a different lock count, until engineers reused part of the old Canal du Nord and lowered the summit level by eighteen and a half meters, around 2012" — the unverifiable backwards "6→7, lock removed" causal claim is gone. This matches `arastirma.md` §8's own caution that the lock-count discrepancy (7 current vs. 6 older sources) is unresolved; the script no longer asserts a specific, unsupported direction. |
| New-issue scan — facts vs. `arastirma.md` | PASS | Spot-checked all other numeric claims unchanged from round 1 (€5.1B→€7.3B, EU €2.1B/French State €1.097B/Nord €217M, Montmacq €96M/Oisy-le-Verger €315M/Somme viaduct €440M, cost-tower residual €6.389B, 2032 opening, Rotterdam-Antwerp-not-Hamburg) — no edits were made to these scenes beyond s02/s12/s13/s14/s34, all still trace correctly to sourced rows. |
| New-issue scan — policy / originality / craft | PASS | No new AI-image, defamation, investment-advice, or structural problems introduced by the edits. `yapay_icerik_beyani: false` remains defensible (generic, non-identifiable illustrations, "no text/no people" in prompts) — still worth a final look at the rendered frames in Stage B, as flagged previously, but not a Stage A blocker. |
| Carry-over minor note (not blocking) | — | s15's `arsiv` search term "Bouygues construction bridge France" still risks pulling a frame with a prominent logo (kimlik.md: no logos as main visual). This is a production-stage frame-selection note, not a script defect — flag again for `produksiyon`. |

## Fixes required
None blocking. One carry-over production note: when selecting the archive frame for s15, avoid any shot with a dominant Bouygues logo.

KARAR: HAZIR

---

# Denetim — Stage B (Post-Production) — 2610-02-seine-nord-canal

Scope: reviewed `son.mp4` runtime/metadata, `onizleme.jpg` frame grid (all 42 scenes), `altyazi.srt` (start/middle/end), `zaman_cizelgesi.json`, `thumbnail-a/b/c.jpg`, `shorts/short-1.mp4` and `short-2.mp4`, `gorseller/gorseller.json`, `lisanslar.txt`. Audio is edge-tts (known/accepted substitute for Kokoro) — not flagged as an issue, only checked for timing/clarity.

| Check | Result | Evidence |
|---|---|---|
| Duration | PASS | `zaman_cizelgesi.json` → `sure: 621.08` (10:21), within the 8-12 min range. |
| Chapters | PASS | `bolumler_gecerli: true`, 9 chapters in `bolumler.txt` (Hook 00:00 → Close 09:47), matches the on-screen `bolum` tags in `zaman_cizelgesi.json`. |
| Subtitles — timing | PASS | 258 cues; first cue starts 0:00.087, last cue ends 10:20.483 vs. total 10:21.08 — consistent, no runaway drift at start/middle/end. |
| Subtitles — content | PASS | Spot-checked start, middle, end: no garbled text. Proper nouns correct: "Bouygues-led", "Montmacq", "Oisy-le-Verger", "Merovingian", "Somme". |
| Thumbnails — readability | PASS | All 3 variants (Cost Overrun / Audit Warning / Delayed Again) have large, high-contrast text with a distinct number/date tag; text does not duplicate any of the candidate titles in `basliklar.txt`. |
| Thumbnails — content match | **FIX** | All 3 variants share the same background (`thumbnail_arka.jpg`): a generic modern glass/concrete building facade reflected in a canal, with two cyclists visible. The intended prompt was "a massive concrete canal lock chamber under construction, towering cranes overhead" (`senaryo.json → thumbnail.prompt`) — because `FAL_KEY` is absent, it fell back to a stock search that returned an unrelated urban/architecture photo with no lock, canal construction, crane, or any visual tie to the video's subject. This breaks the "thumbnail promise confirmed by the video" check and risks looking like generic/non-representative clickbait. It also contains two identifiable bystanders who did not consent to being on a thumbnail. |
| Thumbnails — attribution | **FIX** | `thumbnail_arka.jpg` is not listed anywhere in `lisanslar.txt` or `gorseller.json` (unlike every other scene asset), so its source/license/attribution is untracked. Must either source a properly attributed, on-topic canal/construction image and add it to `lisanslar.txt`, or build a graphic-card thumbnail instead. |
| AI-fallback scenes s13/s14/s34 — "Illustration" label | **FIX** | Per task brief: these three scenes fell back to real stock photography (not `fal.ai` renders) — confirmed via `lisanslar.txt` (s13 = Pixabay "cranes-construction-load-crane" photo by analogicus; s14 = Pixabay "arches-architecture-bridge-columns" photo; s34 = Pixabay "crane-load-crane-lift-loads" photo). The rendered frames still carry on-screen text "Illustration — 25 m deep lock" / "Illustration — 1.33 km viaduct" / "Illustration — lock gate install". Labeling real documentary stock photos as "Illustration" is factually wrong on screen and should be removed/relabeled now that `ai_gorsel` didn't actually run. (Note: visually s13 and s14 are strong, legitimate matches for the narration — cranes and a low concrete viaduct respectively — so this is a label-text fix only, not a re-shoot.) |
| Visual-narration match — s19 | **FIX (higher severity)** | s19 narration: "a dig near the Somme uncovered graves from the Merovingian era" (`arama`: "medieval archaeological dig excavation"). The delivered frame (`lisanslar.txt`: Pixabay "excavator-construction-site-build" by 652234) is a generic modern orange excavator with the fabricator's brand clearly readable on the machine body ("KLIEMT" / "kliemt-gruppe.de"). This is a double problem: (1) the image has nothing to do with an archaeological dig — it's a construction excavator, a keyword collision on "excavation/excavator"; (2) a real third-party company logo is the dominant subject of the frame, which CLAUDE.md rule 5 explicitly prohibits ("logos not used as main visual"). Needs a new search term, e.g. "archaeological excavation trench field France" (reusing the style of s18's genuine dig photo) and a logo-free frame. |
| Visual-narration match — s17 | minor note | s17 ("6,000 workers at peak", `arama`: "construction workers infrastructure site") returned a residential apartment tower under scaffolding rather than a civil-engineering/canal site — generic enough not to misrepresent a specific fact, but worth tightening the search term (e.g. "civil engineering construction site aerial workers") for a better visual fit; not blocking. |
| Shorts — duration | PASS | `short-1.mp4` = 41.4 s, `short-2.mp4` = 51.2 s — both ≤ 60 s. |
| Shorts — existence | PASS | Both files present in `shorts/`. |
| CGI / render-tell scan (rest of `onizleme.jpg` grid) | PASS | Remaining 39 frames (bridges, canal barges, ports, cranes, EU flag, cost-tower/bar charts, aerial construction sites, gravestones, Bordeaux bridge at night, etc.) read as genuine photography/video stills with plausible reflections and shadows — no obvious CGI/render artifacts or watermarks spotted. |
| `_yedek` fallback text cards | PASS | No leftover `_yedek` placeholder cards visible in the frame grid. |

## Fixes required (max 5)
1. **Thumbnail background** (`thumbnail-a/b/c.jpg`, shared `gorseller/thumbnail_arka.jpg`): replace the generic office-building/cyclists photo with an on-topic canal/lock/construction image (or a graphic card), and add its source to `lisanslar.txt`.
2. **s19 image**: replace the branded excavator photo (visible "KLIEMT" logo, wrong subject) with a genuine archaeological-dig frame; re-run `python -m hat uret videolar\2610-02-seine-nord-canal` for this scene only.
3. **s13 / s14 / s34 on-screen text**: remove or change the "Illustration — ..." label since these scenes rendered as real stock photos, not AI images (e.g. plain caption "25 m deep lock" / "1.33 km viaduct" / "Lock gate install" without the "Illustration" prefix).
4. (Minor, non-blocking) s17: tighten `arama` to pull a civil-engineering/canal-site frame instead of a residential tower, if an easy re-search is available.
5. (Minor, non-blocking) s15: still flagged from Stage A — confirm the final frame used for "Bouygues-led group" doesn't show a dominant Bouygues logo (checked frame in `onizleme.jpg` shows a lit stone bridge at night, no logo visible — looks resolved, but double-check in the full-res render since the preview grid is downsampled).

KARAR: DÜZELT

---

# Denetim — Stage B (Post-Production) — ROUND 2

Scope: re-check only the 3 fixes required after round-1 Stage B, plus a scan for anything newly broken. Re-read `thumbnail-a/b/c.jpg`, `gorseller/thumbnail_arka.jpg`, `gorseller/pixabay-f-59150.jpg` (s19), `senaryo.json` (s13/s14/s34 `ekran_yazisi`), `lisanslar.txt`, `gorseller/gorseller.json`, and the full `onizleme.jpg` frame grid.

| Check | Result | Evidence |
|---|---|---|
| Fix 1 — Thumbnail background | PASS | `gorseller/thumbnail_arka.jpg` is now a genuine construction-site crane photo (two tower cranes over a building under scaffolding), on-topic for a cost-overrun/construction video. Licensed and tracked: `lisanslar.txt` line 37 — "by rhythmuswege via Pixabay — construction-site-crane-285645". All three variants (`thumbnail-a/b/c.jpg`) use it consistently with readable text and correct price/date tags (+€2.2B, €7.3B, 2032). No identifiable bystanders in the frame (tiny distant figures near scaffolding only, not a focal point). No dominant third-party logo — crane cab markings are illegible at thumbnail scale. |
| Fix 2 — s19 visual | PASS | `gorseller/gorseller.json` → s19 now points to `pixabay-f-59150.jpg`, matching `lisanslar.txt` line 18 ("JamesDeMers via Pixabay — archaeology-archaeological-dig-59150"). Viewed the file directly: a real archaeologist seated at a dig site writing on a clipboard, buckets, trowels, excavation pit — genuine match for the s19 narration ("a dig near the Somme uncovered graves from the Merovingian era"). The previous "KLIEMT"-branded excavator is gone. No company logo visible; a cap reads "Monticello" (a historic-site name, not a commercial brand) and is small/incidental, not a blocking concern. |
| Fix 3 — s13/s14/s34 "Illustration" label | PASS | `senaryo.json`: s13 `ekran_yazisi` = "25 m deep lock", s14 = "1.33 km viaduct", s34 = "Lock gate install" — the "Illustration — " prefix is gone from all three. Confirmed in the actual rendered output via `onizleme.jpg`: all three frames show the clean captions burned in, matching the script. |
| New-issue scan — `onizleme.jpg` full grid | PASS | Re-reviewed all 42 frames. No new watermarks, no `_yedek` fallback cards, no CGI/render tells. Charts, cost-tower, and photo/video frames otherwise unchanged from round 1. |
| New-issue scan — `lisanslar.txt` completeness | PASS | Thumbnail background and s19 image are now both present with source/author/URL, consistent with every other tracked asset. |
| Carry-over note (non-blocking) | — | s15 Bouygues-viaduct frame and s17 workers frame were only minor notes in round 1 (not part of this round's required fixes) — re-checked in the current `onizleme.jpg` grid: s15 shows a stone arch bridge (no logo), s17 shows an aerial excavation/earthworks shot (on-topic, better than the round-1 residential-tower frame). Both look fine now; no action needed. |

## Fixes required
None. All 3 required fixes verified correct in both the script (`senaryo.json`/`lisanslar.txt`) and the actual rendered assets (thumbnails, `onizleme.jpg`).

KARAR: HAZIR
