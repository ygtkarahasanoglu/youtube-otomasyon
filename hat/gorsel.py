"""Gorseller: her sahne icin bir gorsel dosyasi bulur veya uretir.

Sahne gorsel turleri (senaryo.json -> sahneler[].gorsel.tur):
  stok      : {"arama": "container ship aerial"}       stok video: Pexels* -> Coverr* -> Pixabay -> foto zinciri
  stok_foto : {"arama": "..."}                          stok foto: Pexels* -> Pixabay -> Openverse (CC0/PD/CC BY)
  arsiv     : {"arama": "Port of Rotterdam aerial"}           gercek yer/sirket fotografi: Openverse (Wikimedia, Flickr; CC0/PD/CC BY)
  nasa      : {"arama": "Suez Canal from space"}         NASA uydu/uzay fotografi (kamu mali, anahtar gerekmez)
  (* anahtar varsa; Pexels yeni anahtar vermiyor, Coverr ucretsiz anahtar verir)
  ai_gorsel : {"prompt": "..."}                          fal.ai gorsel (ucretli, kucuk)
  ai_video  : {"prompt": "..."}                          fal.ai video klip (ucretli; video basina sinirli)
  grafik    : {"grafik": {...}}                          cubuk/karsilastirma grafigi (grafik.py)
  kule      : {"kule": {...}}                            Maliyet Kulesi (grafik.py)
  yazi      : {"yazi": "...", "alt": "..."}              buyuk yazi karti
  dosya     : {"yol": "..."}                             elle eklenen gorsel/video
Test modu (sahte=True): internet olmadan yer tutucu gorsel uretir.
"""
import hashlib
import random
import re
import time
from pathlib import Path

import requests

from . import grafik
from .ayar import KOK, anahtar, json_oku, json_yaz, log, maliyet_ekle

KULLANILAN = KOK / "kanal" / "kullanilan_stok.json"  # kanal genelinde tekrar onleme


def _indir(url: str, hedef: Path, basliklar=None) -> Path:
    with requests.get(url, headers=basliklar or {}, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(hedef, "wb") as f:
            for parca in r.iter_content(1 << 16):
                f.write(parca)
    return hedef


def _kullanilan() -> dict:
    return json_oku(KULLANILAN, {})


def _isaretle(kimlik: str, video_kodu: str) -> None:
    v = _kullanilan()
    v[kimlik] = video_kodu
    json_yaz(KULLANILAN, v)


# ---------- stok ----------
UA = {"User-Agent": "BehindTheMargin-video-pipeline/1.0 (personal YouTube channel)"}


def pexels_video(arama: str, hedef_dir: Path, min_sure: float, video_kodu: str) -> tuple:
    if not anahtar("PEXELS_API_KEY", zorunlu=False):
        return None
    r = requests.get("https://api.pexels.com/videos/search",
                     params={"query": arama, "orientation": "landscape", "per_page": 30},
                     headers={"Authorization": anahtar("PEXELS_API_KEY")}, timeout=30)
    r.raise_for_status()
    kullanilan = _kullanilan()
    adaylar = []
    for v in r.json().get("videos", []):
        kimlik = f"pexels-v-{v['id']}"
        if kimlik in kullanilan:
            continue
        dosyalar = [f for f in v.get("video_files", []) if f.get("width") and f["width"] >= 1280 and f.get("file_type") == "video/mp4"]
        if not dosyalar:
            continue
        en_iyi = min(dosyalar, key=lambda f: abs(f["width"] - 1920))
        puan = (v.get("duration", 0) >= min_sure) * 2 + (en_iyi["width"] >= 1920)
        adaylar.append((puan, kimlik, en_iyi["link"], v.get("url"), v.get("user", {}).get("name", "")))
    if not adaylar:
        return None
    adaylar.sort(key=lambda a: -a[0])
    _, kimlik, link, sayfa, yazar = random.choice(adaylar[:3])
    hedef = _indir(link, hedef_dir / f"{kimlik}.mp4")
    _isaretle(kimlik, video_kodu)
    return hedef, {"kaynak": "Pexels", "sayfa": sayfa, "yazar": yazar}


def pixabay_video(arama: str, hedef_dir: Path, min_sure: float, video_kodu: str) -> tuple:
    k = anahtar("PIXABAY_API_KEY", zorunlu=False)
    if not k:
        return None
    r = requests.get("https://pixabay.com/api/videos/", params={"key": k, "q": arama[:100], "per_page": 30, "safesearch": "true"}, timeout=30)
    r.raise_for_status()
    kullanilan = _kullanilan()
    hits = sorted(r.json().get("hits", []), key=lambda h: h.get("duration", 0) < min_sure)  # yeterince uzun olanlar once
    for h in hits:
        kimlik = f"pixabay-v-{h['id']}"
        if kimlik in kullanilan:
            continue
        dosya = h.get("videos", {}).get("large") or h.get("videos", {}).get("medium")
        if not dosya or not dosya.get("url") or dosya.get("width", 0) < 1280:
            continue
        hedef = _indir(dosya["url"], hedef_dir / f"{kimlik}.mp4")
        _isaretle(kimlik, video_kodu)
        return hedef, {"kaynak": "Pixabay", "sayfa": h.get("pageURL"), "yazar": h.get("user", "")}
    return None


def pexels_foto(arama: str, hedef_dir: Path, video_kodu: str) -> tuple:
    if not anahtar("PEXELS_API_KEY", zorunlu=False):
        return None
    r = requests.get("https://api.pexels.com/v1/search", params={"query": arama, "orientation": "landscape", "per_page": 20},
                     headers={"Authorization": anahtar("PEXELS_API_KEY")}, timeout=30)
    r.raise_for_status()
    kullanilan = _kullanilan()
    for p in r.json().get("photos", []):
        kimlik = f"pexels-f-{p['id']}"
        if kimlik in kullanilan:
            continue
        hedef = _indir(p["src"]["large2x"], hedef_dir / f"{kimlik}.jpg")
        _isaretle(kimlik, video_kodu)
        return hedef, {"kaynak": "Pexels", "sayfa": p.get("url"), "yazar": p.get("photographer", "")}
    return None


def coverr_video(arama: str, hedef_dir: Path, min_sure: float, video_kodu: str) -> tuple:
    k = anahtar("COVERR_API_KEY", zorunlu=False)
    if not k:
        return None
    bas = {"Authorization": f"Bearer {k}", **UA}
    r = requests.get("https://api.coverr.co/videos", params={"query": arama[:100], "page_size": 20, "urls": "true"},
                     headers=bas, timeout=30)
    r.raise_for_status()
    kullanilan = _kullanilan()
    hits = sorted(r.json().get("hits", []), key=lambda h: float(h.get("duration") or 0) < min_sure)
    for h in hits:
        kimlik = f"coverr-v-{h['id']}"
        url = (h.get("urls") or {}).get("mp4_download") or (h.get("urls") or {}).get("mp4")
        if kimlik in kullanilan or not url:
            continue
        hedef = _indir(url, hedef_dir / f"{kimlik}.mp4")
        try:  # Coverr kurali: indirme bildirimi zorunlu
            requests.patch(f"https://api.coverr.co/videos/{h['id']}/stats/downloads", headers=bas, timeout=15)
        except Exception:  # noqa: BLE001
            pass
        _isaretle(kimlik, video_kodu)
        return hedef, {"kaynak": "Coverr", "sayfa": f"https://coverr.co/videos/{h.get('slug') or h['id']}", "yazar": h.get("title", "")}
    return None


def pixabay_foto(arama: str, hedef_dir: Path, video_kodu: str) -> tuple:
    k = anahtar("PIXABAY_API_KEY", zorunlu=False)
    if not k:
        return None
    r = requests.get("https://pixabay.com/api/", params={"key": k, "q": arama[:100], "image_type": "photo", "orientation": "horizontal",
                                                         "min_width": 1280, "safesearch": "true", "per_page": 30}, timeout=30)
    r.raise_for_status()
    kullanilan = _kullanilan()
    for h in r.json().get("hits", []):
        kimlik = f"pixabay-f-{h['id']}"
        url = h.get("fullHDURL") or h.get("largeImageURL")
        if kimlik in kullanilan or not url:
            continue
        hedef = _indir(url, hedef_dir / f"{kimlik}.jpg")
        _isaretle(kimlik, video_kodu)
        return hedef, {"kaynak": "Pixabay", "sayfa": h.get("pageURL"), "yazar": h.get("user", "")}
    return None


OPENVERSE_LISANS = {"cc0": "CC0", "pdm": "Public Domain", "by": "CC BY"}


def openverse_foto(arama: str, hedef_dir: Path, video_kodu: str) -> tuple:
    """Openverse: Wikimedia Commons, Flickr ve muzelerden yalniz CC0 / kamu mali / CC BY (atifla) fotograflar. Anahtar gerekmez."""
    r = requests.get("https://api.openverse.org/v1/images/", params={"q": arama[:200], "license": "cc0,pdm,by", "aspect_ratio": "wide",
                                                                    "size": "large", "mature": "false", "page_size": 20},
                     headers=UA, timeout=30)
    r.raise_for_status()
    kullanilan = _kullanilan()
    for h in r.json().get("results", []):
        kimlik = f"openverse-{h['id']}"
        if kimlik in kullanilan or not h.get("url") or (h.get("width") or 0) < 1000:
            continue
        lisans = OPENVERSE_LISANS.get(h.get("license", ""), "")
        if not lisans:
            continue
        uzanti = ".png" if str(h["url"]).lower().endswith(".png") else ".jpg"
        try:
            hedef = _indir(h["url"], hedef_dir / f"{kimlik}{uzanti}", UA)
        except Exception:  # noqa: BLE001  kaynak site kapali olabilir, siradakini dene
            continue
        _isaretle(kimlik, video_kodu)
        surum = f" {h['license_version']}" if h.get("license_version") and lisans == "CC BY" else ""
        return hedef, {"kaynak": "Openverse", "sayfa": h.get("foreign_landing_url"), "yazar": h.get("creator") or "",
                       "lisans": lisans + surum, "baslik": h.get("title", "")}
    return None


def nasa_foto(arama: str, hedef_dir: Path, video_kodu: str) -> tuple:
    """NASA Image and Video Library: uydu ve uzay fotograflari (kamu mali; NASA logosu kullanilmaz). Anahtar gerekmez."""
    r = requests.get("https://images-api.nasa.gov/search", params={"q": arama[:200], "media_type": "image", "page_size": 20},
                     headers=UA, timeout=30)
    r.raise_for_status()
    kullanilan = _kullanilan()
    for it in r.json().get("collection", {}).get("items", []):
        d = (it.get("data") or [{}])[0]
        kimlik = f"nasa-{d.get('nasa_id')}"
        if kimlik in kullanilan or not it.get("href"):
            continue
        dosyalar = requests.get(it["href"], headers=UA, timeout=30).json()
        secim = next((u for tip in ("~large.jpg", "~orig.jpg", "~medium.jpg") for u in dosyalar if u.lower().endswith(tip)), None)
        if not secim:
            continue
        hedef = _indir(secim.replace("http://", "https://"), hedef_dir / f"{kimlik}.jpg", UA)
        _isaretle(kimlik, video_kodu)
        return hedef, {"kaynak": "NASA", "sayfa": f"https://images.nasa.gov/details/{d.get('nasa_id')}",
                       "yazar": d.get("photographer") or d.get("center") or "NASA", "lisans": "Public Domain"}
    return None


_DOLGU = {"a", "an", "the", "of", "in", "on", "with", "and", "at", "to", "for", "from", "by", "its", "is", "are",
          "cinematic", "photo", "photograph", "realistic", "close-up", "closeup", "shot", "view", "image", "style",
          "documentary", "detailed", "high", "quality", "lighting", "light", "natural", "dramatic", "wide", "angle"}


def _prompttan_arama(prompt: str) -> str:
    """AI promptundan stok arama ifadesi: ilk cumlenin anlamli 4 kelimesi."""
    ilk = re.split(r"[.,;:]", prompt)[0].lower()
    kel = [w for w in re.findall(r"[a-z0-9'-]+", ilk) if w not in _DOLGU]
    return " ".join(kel[:4]) or "business"


def foto_zinciri(arama: str, hedef_dir: Path, video_kodu: str) -> tuple:
    for f in (pexels_foto, pixabay_foto, openverse_foto):
        try:
            sonuc = f(arama, hedef_dir, video_kodu)
        except Exception as e:  # noqa: BLE001
            log(f"    {f.__name__}: {e}")
            sonuc = None
        if sonuc:
            return sonuc
    return None


def video_zinciri(arama: str, hedef_dir: Path, min_sure: float, video_kodu: str) -> tuple:
    for f in (pexels_video, coverr_video, pixabay_video):
        try:
            sonuc = f(arama, hedef_dir, min_sure, video_kodu)
        except Exception as e:  # noqa: BLE001
            log(f"    {f.__name__}: {e}")
            sonuc = None
        if sonuc:
            return sonuc
    return foto_zinciri(arama, hedef_dir, video_kodu)


# ---------- fal.ai ----------
def fal(model: str, girdi: dict, bekleme: int = 900) -> dict:
    """fal.ai kuyruk API: is gonder, bitene kadar bekle, sonucu dondur."""
    bas = {"Authorization": f"Key {anahtar('FAL_KEY')}"}
    r = requests.post(f"https://queue.fal.run/{model}", json=girdi, headers=bas, timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(f"fal.ai hatasi {r.status_code}: {r.text[:400]}")
    is_ = r.json()
    durum_url, sonuc_url = is_["status_url"], is_["response_url"]
    t0 = time.time()
    while time.time() - t0 < bekleme:
        d = requests.get(durum_url, headers=bas, timeout=30).json()
        if d.get("status") == "COMPLETED":
            return requests.get(sonuc_url, headers=bas, timeout=60).json()
        if d.get("status") in ("FAILED", "ERROR"):
            raise RuntimeError(f"fal.ai isi basarisiz: {d}")
        time.sleep(4)
    raise RuntimeError("fal.ai zaman asimi")


def ai_gorsel(prompt: str, hedef: Path, ayar: dict, klasor: Path, oran: str = "landscape_16_9") -> tuple:
    fa = ayar["fal"]
    tam = f"{prompt}. {fa.get('gorsel_stil', '')}".strip()
    v = fal(fa["gorsel_model"], {"prompt": tam, "image_size": oran, "num_images": 1})
    url = (v.get("images") or [{}])[0].get("url")
    if not url:
        raise RuntimeError(f"fal.ai gorsel donmedi: {str(v)[:300]}")
    _indir(url, hedef)
    maliyet_ekle(klasor, "AI gorsel", fa.get("gorsel_usd", 0.03), prompt[:60])
    return hedef, {"kaynak": "AI (fal.ai)", "model": fa["gorsel_model"], "prompt": tam}


def ai_video(prompt: str, hedef: Path, ayar: dict, klasor: Path) -> tuple:
    fa = ayar["fal"]
    sn = int(fa.get("video_sn", 5))
    v = fal(fa["video_model"], {"prompt": f"{prompt}. {fa.get('video_stil', '')}".strip(), "duration": str(sn), "aspect_ratio": "16:9"})
    url = (v.get("video") or {}).get("url")
    if not url:
        raise RuntimeError(f"fal.ai video donmedi: {str(v)[:300]}")
    _indir(url, hedef)
    maliyet_ekle(klasor, "AI video", fa.get("video_usd_sn", 0.07) * sn, prompt[:60])
    return hedef, {"kaynak": "AI (fal.ai)", "model": fa["video_model"], "prompt": prompt}


# ---------- ana ----------
def _sahte(sahne: dict, hedef: Path) -> tuple:
    g = sahne.get("gorsel", {})
    metin = g.get("arama") or g.get("prompt") or g.get("yazi") or sahne["id"]
    grafik.yazi_karti(f"[{g.get('tur', '?')}]", metin, hedef, renk_tohum=sahne["id"])
    return hedef, {"kaynak": "test"}


def uret(klasor: Path, senaryo: dict, ayar: dict, sesler: dict, sahte: bool = False) -> dict:
    klasor = Path(klasor)
    gdir = klasor / "gorseller"
    gdir.mkdir(parents=True, exist_ok=True)
    kayit = json_oku(gdir / "gorseller.json", {})
    kod = senaryo.get("kod", klasor.name)
    ai_video_hak = ayar["fal"].get("video_basina_max_ai_video", 4)
    ai_video_sayi = sum(1 for v in kayit.values() if v.get("bilgi", {}).get("kaynak", "").startswith("AI") and str(v.get("dosya", "")).endswith(".mp4"))
    for s in senaryo["sahneler"]:
        sid, g = s["id"], s.get("gorsel", {"tur": "yazi", "yazi": s["metin"][:60]})
        imza = hashlib.md5(json_dumps(g).encode()).hexdigest()[:10]
        eski = kayit.get(sid)
        if eski and eski.get("imza") == imza and Path(eski["dosya"]).exists():
            continue
        tur = g.get("tur", "stok")
        sure_ = sesler[sid]["sure"]
        log(f"  gorsel {sid} [{tur}] ...")
        sonuc = None
        try:
            if sahte and tur in ("stok", "stok_foto", "arsiv", "nasa", "ai_gorsel", "ai_video"):
                sonuc = _sahte(s, gdir / f"{sid}.png")
            elif tur == "stok":
                sonuc = video_zinciri(g["arama"], gdir, sure_, kod)
            elif tur == "stok_foto":
                sonuc = foto_zinciri(g["arama"], gdir, kod)
            elif tur == "arsiv":
                sonuc = openverse_foto(g["arama"], gdir, kod) or foto_zinciri(g["arama"], gdir, kod)
            elif tur == "nasa":
                sonuc = nasa_foto(g["arama"], gdir, kod) or foto_zinciri(g["arama"], gdir, kod)
            elif tur in ("ai_gorsel", "ai_video") and not anahtar("FAL_KEY", zorunlu=False):
                arama = g.get("arama") or _prompttan_arama(g.get("prompt", ""))
                log(f"    fal.ai anahtari yok; stok araniyor: \"{arama}\"")
                sonuc = (video_zinciri(arama, gdir, sure_, kod) if tur == "ai_video" else None) or foto_zinciri(arama, gdir, kod)
            elif tur == "ai_gorsel":
                sonuc = ai_gorsel(g["prompt"], gdir / f"{sid}.jpg", ayar, klasor)
            elif tur == "ai_video":
                if ai_video_sayi >= ai_video_hak:
                    log(f"    AI video hakki doldu ({ai_video_hak}); yerine AI gorsel uretiliyor")
                    sonuc = ai_gorsel(g["prompt"], gdir / f"{sid}.jpg", ayar, klasor)
                else:
                    sonuc = ai_video(g["prompt"], gdir / f"{sid}.mp4", ayar, klasor)
                    ai_video_sayi += 1
            elif tur == "grafik":
                sonuc = grafik.grafik(g["grafik"], gdir / f"{sid}.png"), {"kaynak": "grafik"}
            elif tur == "kule":
                sonuc = grafik.kule_video(g["kule"], gdir / f"{sid}.mp4", sure_), {"kaynak": "grafik"}
            elif tur == "yazi":
                sonuc = grafik.yazi_karti(g.get("yazi", ""), g.get("alt", ""), gdir / f"{sid}.png"), {"kaynak": "grafik"}
            elif tur == "dosya":
                yol = Path(g["yol"])
                sonuc = (yol if yol.is_absolute() else KOK / yol), {"kaynak": "kullanici"}
        except Exception as e:  # noqa: BLE001  tek sahne yuzunden hat durmasin
            log(f"    UYARI {sid}: {e}")
        if not sonuc:
            yedek = g.get("prompt") or g.get("arama") or s["metin"][:80]
            log(f"    {sid}: kaynak bulunamadi, yazi karti kullaniliyor (sonra degistirilebilir)")
            sonuc = grafik.yazi_karti(s.get("ekran_yazisi") or "", yedek, gdir / f"{sid}_yedek.png"), {"kaynak": "yedek"}
        dosya, bilgi = sonuc
        kayit[sid] = {"dosya": str(dosya), "bilgi": bilgi, "imza": imza, "tur": tur}
        json_yaz(gdir / "gorseller.json", kayit)
    _lisans_dosyasi(klasor, kayit)
    return kayit


def json_dumps(v) -> str:
    import json
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def _lisans_dosyasi(klasor: Path, kayit: dict) -> None:
    satirlar = ["Stock footage / images:"]
    for sid, v in sorted(kayit.items()):
        b = v.get("bilgi", {})
        if b.get("kaynak") in ("Pexels", "Pixabay", "Coverr", "Openverse", "NASA"):
            lisans = f" ({b['lisans']})" if b.get("lisans") else ""
            baslik = f"\"{b['baslik']}\" " if b.get("baslik") else ""
            satirlar.append(f"- {sid}: {baslik}by {b.get('yazar') or 'unknown'} via {b['kaynak']}{lisans} — {b.get('sayfa', '')}")
    ai = [sid for sid, v in kayit.items() if str(v.get("bilgi", {}).get("kaynak", "")).startswith("AI")]
    if ai:
        satirlar.append(f"AI-generated visuals: {', '.join(sorted(ai))}")
    (klasor / "lisanslar.txt").write_text("\n".join(satirlar) + "\n", encoding="utf-8")
