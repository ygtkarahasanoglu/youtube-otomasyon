---
name: senaryo-json
description: Writes the full English narration script directly as videolar/<folder>/senaryo.json for the automated pipeline — scene-by-scene narration, visual type per scene, on-screen text, chapters, Shorts selection and AI budget rules. Use whenever a script or senaryo.json is written or revised.
---

# senaryo.json — script for the automated pipeline

Template: `kanal/senaryo-sablonu.json`. Write valid JSON (UTF-8). Narration and all viewer-facing text in **English**.

## Length and rhythm
- Long video: **1,300-1,800 words** (≈ 8.5-12 min at ~150 wpm), **30-55 scenes**.
- Each scene `metin`: 1-3 sentences, **8-22 seconds** of speech (20-55 words). One idea per scene. The visual changes every scene, so short scenes = dynamic video.
- Spoken style: contractions, short sentences, numbers written as they should be spoken ("about thirty cents", "$4.2 billion" → "four point two billion dollars"). No headings or bullet points inside `metin`. No stage directions.

## Structure (use `bolum` on the first scene of each chapter; ≥3 chapters, each ≥ 30 s; first chapter starts at s01)
1. **Hook** (s01-s03, ≤ 20 s): a hook formula from `hook-21` + the money question + one surprising sourced number. No greeting, no channel intro.
2. **Context** (≤ 45 s): why it matters + an open loop ("but the biggest cost isn't the one you think").
3. **3-5 sections**: mini hook → numbers → visual explainer (chart / cost tower) → transition loop.
4. **Insider note**: one procurement/supply-chain insight that most explainers miss.
5. **Payoff**: the full answer (e.g. the complete Cost Tower). Close every open loop.
6. **Close** (≤ 15 s): one-line takeaway + "Which company should we break down next?" No "like and subscribe" begging; one short subscribe line allowed after the payoff.

## Visuals (`gorsel.tur`) — choose per scene
| tur | when | fields | cost |
| --- | --- | --- | --- |
| `stok` | real-world footage: stores, factories, ports, people working (no recognizable faces needed) | `arama`: 2-5 concrete English words, e.g. "container ship port crane" | free |
| `stok_foto` | when footage is unlikely to exist | `arama` | free |
| `arsiv` | a REAL specific place/building/product/historic scene (e.g. "Feadship shipyard Aalsmeer", "Ever Given Suez Canal") from Wikimedia/Flickr via Openverse (CC0, public domain, CC BY — credited automatically) | `arama`: proper nouns + object | free |
| `nasa` | satellite / from-space views: canals, ports, shipping lanes, night lights, crops (NASA public domain) | `arama`, e.g. "Suez Canal satellite" | free |
| `ai_gorsel` | specific scenes stock can't show, concepts, historical moments (illustration style) | `prompt`: subject, setting, light, camera; no text/logos/real people | ~$0.03 |
| `ai_video` | the 3-6 most important moments (hook, payoff) | `prompt` as above + motion ("slow dolly in") | ~$0.35 |
| `grafik` | comparisons, trends | `grafik`: {"tip":"bar","baslik","etiketler","degerler","birim","vurgu":index,"kaynak"} | free |
| `kule` | cost breakdown (signature) | `kule`: {"baslik","birim":"$","kaynak","kalemler":[{"ad","tutar","renk"?}]} bottom→top; profit green #2BB673 | free |
| `yazi` | key statement, question card | `yazi` (≤6 words), `alt` (≤20 words) | free |

Rules:
- **No `FAL_KEY` in `.env` (current free test phase):** use 0 `ai_video` and at most 10% `ai_gorsel`; every `ai_*` scene must ALSO carry `arama` (2-5 concrete words) because the pipeline replaces it with stock when there is no key. Lean on `grafik`/`kule` and `arsiv`/`nasa` for originality instead.
- Mix (with FAL_KEY): ≥ 50% `stok`/`stok_foto`/`arsiv`/`nasa`, 15-30% `ai_gorsel`, ≤ 6 `ai_video`, ≥ 2 `grafik`/`kule`, ≤ 3 `yazi`. Never two `yazi` in a row.
- Stock search words must match what is said in that scene. Vary them; never reuse the same `arama` twice in a video.
- AI prompts: no real people, no brand logos, no readable text. Use "illustration" or "cinematic photo" consistently within a video.
- Realistic AI depiction of a real event/person → set `yapay_icerik_beyani: true` (better: avoid).
- `ekran_yazisi`: ≤ 8 words, only for key numbers or terms (every 3-5 scenes), e.g. "$0.30 of beans".

## Shorts (`shorts`)
1-2 Shorts per video, each 3-5 consecutive or related scenes, **25-55 s total**, self-contained (no "as we saw"). Prefer scenes with `stok`/`ai_*` visuals (charts get small in vertical). `kanca`: ≤ 6 words shown in the first 2.5 s. `baslik`: ≤ 70 chars.
These are also posted as Instagram/Facebook Reels. The `dagitim-direktoru` may later add one Reels-only clip with `"youtube": false` and writes `dagitim`; the senarist leaves `dagitim` empty. Make at least one Short from the "from the buyer's desk" note.

## Sources (`kaynaklar`)
Every number in `metin`, `grafik`, `kule` must trace to an entry in `arastirma.md`; list the sources used: [{"ad": "Company 10-K 2025", "url": "..."}].

## Self-check before saving
- Word count and scene count in range; JSON parses (`python -c "import json;json.load(open('...','r',encoding='utf-8'))"`).
- First 20 s states the promise of the title.
- Every open loop closes. Chapters ≥ 3.
- Estimated AI cost = ai_gorsel×0.03 + ai_video×0.35 + thumbnail 0.03 (≤ `ayarlar.json` budget).
