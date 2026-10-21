"""Seslendirme: her sahne icin ses dosyasi + kelime zamanlari.

Saglayicilar:
  kokoro     : ucretsiz, bilgisayarda calisan acik kaynak ses (Apache 2.0, ticari kullanim serbest) - VARSAYILAN
  elevenlabs : en dogal ses (ucretli, ELEVENLABS_API_KEY + ses_id)
  edge       : Microsoft Edge sesleri (ucretsiz ama ticari lisansi yok; yalniz deneme icin)
  sessiz     : test modu; sessiz ses ve tahmini zamanlar (internet gerekmez)
"""
import asyncio
import base64
import json
import re
from pathlib import Path

import requests

from .ayar import anahtar, ffmpeg, json_oku, json_yaz, log, maliyet_ekle, sure

KELIME_HIZI = 2.6  # sessiz modda saniyedeki kelime


def _kelimeler_karakterden(metin: str, baslar: list, bitisler: list) -> list:
    """ElevenLabs karakter zamanlarindan kelime zamanlari."""
    sonuc, i = [], 0
    for m in re.finditer(r"\S+", metin):
        a, b = m.start(), m.end() - 1
        if a < len(baslar) and b < len(bitisler):
            sonuc.append({"kelime": m.group(), "bas": round(baslar[a], 3), "bit": round(bitisler[b], 3)})
        i += 1
    return sonuc


def elevenlabs(metin: str, hedef: Path, ayar: dict, onceki: str = "", sonraki: str = "") -> list:
    ses_id = ayar.get("ses_id") or anahtar("ELEVENLABS_VOICE_ID")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ses_id}/with-timestamps?output_format=mp3_44100_128"
    govde = {
        "text": metin,
        "model_id": ayar.get("model", "eleven_multilingual_v2"),
        "voice_settings": ayar.get("voice_settings", {"stability": 0.45, "similarity_boost": 0.8, "style": 0.15}),
    }
    if onceki:
        govde["previous_text"] = onceki[-300:]
    if sonraki:
        govde["next_text"] = sonraki[:300]
    r = requests.post(url, json=govde, headers={"xi-api-key": anahtar("ELEVENLABS_API_KEY")}, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs hatasi {r.status_code}: {r.text[:400]}")
    v = r.json()
    hedef.write_bytes(base64.b64decode(v["audio_base64"]))
    al = v.get("alignment") or v.get("normalized_alignment") or {}
    return _kelimeler_karakterden(metin, al.get("character_start_times_seconds", []),
                                  al.get("character_end_times_seconds", []))


def edge(metin: str, hedef: Path, ayar: dict) -> list:
    try:
        import edge_tts
    except ImportError:
        raise RuntimeError("edge-tts kurulu degil: pip install -U edge-tts")

    async def calis():
        kelimeler = []
        iletisim = edge_tts.Communicate(metin, ayar.get("edge_ses", "en-US-AndrewMultilingualNeural"),
                                        rate=ayar.get("edge_hiz", "+0%"), boundary="WordBoundary")
        with open(hedef, "wb") as f:
            async for parca in iletisim.stream():
                if parca["type"] == "audio":
                    f.write(parca["data"])
                elif parca["type"] == "WordBoundary":
                    bas = parca["offset"] / 1e7
                    kelimeler.append({"kelime": parca["text"], "bas": round(bas, 3),
                                      "bit": round(bas + parca["duration"] / 1e7, 3)})
        return kelimeler

    return asyncio.run(calis())


_KOKORO = {}


def kokoro(metin: str, hedef: Path, ayar: dict) -> list:
    """Kokoro-82M: ilk calismada modeli (~330 MB) indirir, sonra internetsiz calisir."""
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline
    except ImportError:
        raise RuntimeError("kokoro kurulu degil: python -m pip install -U kokoro soundfile")
    dil = ayar.get("kokoro_dil", "a")  # a = Amerikan Ingilizcesi, b = Ingiliz
    if dil not in _KOKORO:
        _KOKORO[dil] = KPipeline(lang_code=dil, repo_id="hexgrad/Kokoro-82M")
    pipe = _KOKORO[dil]
    parcalar, kelimeler, t, bosluk = [], [], 0.0, " "
    for r in pipe(metin, voice=ayar.get("kokoro_ses", "am_michael"), speed=ayar.get("kokoro_hiz", 1.0), split_pattern=None):
        if r.audio is None:
            continue
        ses = r.audio.detach().cpu().numpy() if hasattr(r.audio, "detach") else np.asarray(r.audio)
        for tk in (r.tokens or []):
            if tk.start_ts is None or tk.end_ts is None:
                bosluk = tk.whitespace
                continue
            bas, bit = round(t + tk.start_ts, 3), round(t + tk.end_ts, 3)
            if kelimeler and bosluk == "":  # "Costco" + "'s" veya "money" + "," -> tek kelime
                kelimeler[-1]["kelime"] += tk.text
                kelimeler[-1]["bit"] = max(kelimeler[-1]["bit"], bit)
            elif re.search(r"\w", tk.text):
                kelimeler.append({"kelime": tk.text, "bas": bas, "bit": bit})
            bosluk = tk.whitespace
        parcalar.append(ses)
        t += len(ses) / 24000
    if not parcalar:
        raise RuntimeError("Kokoro ses uretmedi")
    wav = hedef.with_suffix(".wav")
    sf.write(str(wav), np.concatenate(parcalar), 24000)
    ffmpeg("-i", wav, "-c:a", "libmp3lame", "-b:a", "160k", hedef)
    wav.unlink(missing_ok=True)
    return kelimeler


def sessiz(metin: str, hedef: Path) -> list:
    kel = metin.split()
    toplam = max(1.5, len(kel) / KELIME_HIZI)
    ffmpeg("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{toplam:.2f}", "-c:a", "libmp3lame", "-q:a", "6", hedef)
    adim = toplam / max(len(kel), 1)
    return [{"kelime": w, "bas": round(i * adim, 3), "bit": round((i + 0.9) * adim, 3)} for i, w in enumerate(kel)]


def uret(klasor: Path, senaryo: dict, ayar: dict, saglayici: str = None) -> dict:
    """Her sahneyi seslendirir; ses/sahne-XX.mp3 ve ses/zamanlar.json yazar."""
    sa = ayar["ses"]
    saglayici = saglayici or senaryo.get("ses_saglayici") or sa.get("saglayici", "kokoro")
    hedef_dir = Path(klasor) / "ses"
    hedef_dir.mkdir(parents=True, exist_ok=True)
    kayit = json_oku(hedef_dir / "zamanlar.json", {})
    sahneler = senaryo["sahneler"]
    karakter = 0
    for i, s in enumerate(sahneler):
        sid, metin = s["id"], s["metin"].strip()
        mp3 = hedef_dir / f"{sid}.mp3"
        onceki = kayit.get(sid)
        if onceki and onceki.get("metin") == metin and onceki.get("saglayici") == saglayici and mp3.exists():
            continue  # degismemis sahneyi tekrar uretme (para ve zaman tasarrufu)
        log(f"  ses {sid} ({saglayici}) ...")
        if saglayici == "elevenlabs":
            kel = elevenlabs(metin, mp3, sa, sahneler[i - 1]["metin"] if i else "",
                             sahneler[i + 1]["metin"] if i + 1 < len(sahneler) else "")
            karakter += len(metin)
        elif saglayici == "kokoro":
            kel = kokoro(metin, mp3, sa)
        elif saglayici == "edge":
            kel = edge(metin, mp3, sa)
        elif saglayici == "sessiz":
            kel = sessiz(metin, mp3)
        else:
            raise ValueError(f"Bilinmeyen ses saglayici: {saglayici}")
        kayit[sid] = {"metin": metin, "saglayici": saglayici, "sure": round(sure(mp3), 3), "kelimeler": kel}
        json_yaz(hedef_dir / "zamanlar.json", kayit)
    if karakter:
        maliyet_ekle(klasor, "ElevenLabs ses", karakter / 1000 * sa.get("usd_1000_karakter", 0.22), f"{karakter} karakter")
    toplam = sum(kayit[s["id"]]["sure"] for s in sahneler)
    log(f"  ses tamam: {len(sahneler)} sahne, {toplam / 60:.1f} dk")
    return kayit
