"""Komutlar (proje klasorunde):
  python -m hat kontrol [--canli]        kurulum ve API anahtarlarini kontrol et (--canli: kucuk gercek deneme)
  python -m hat yeni <kod-kisa-ad>        videolar/ altinda yeni video klasoru + bos senaryo.json
  python -m hat uret <klasor> [--sahte]   ses -> gorsel -> video -> altyazi -> thumbnail -> shorts
         [--adim ses,gorsel,video,thumbnail,shorts] [--ses kokoro|edge|elevenlabs|sessiz]
  python -m hat yukle <klasor>            YouTube'a OZEL olarak yukle (uzun + shorts)
  python -m hat dagitim <klasor>          Instagram + Facebook Reels paylasim paketi (paylasmaz)
  python -m hat youtube-giris             YouTube hesabina bir kez giris (token olusturur)
  python -m hat maliyet [klasor]          video(lar)in tahmini maliyeti
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

from .ayar import KOK, anahtar, ayarlar, ffmpeg_var, json_oku, json_yaz, log, senaryo_oku

ADIMLAR = ["ses", "gorsel", "video", "thumbnail", "shorts"]


def kontrol(canli: bool) -> int:
    sorun = 0

    def satir(ok, ad, cozum=""):
        nonlocal sorun
        print(f"[{'TAMAM' if ok else 'EKSIK'}] {ad}" + ("" if ok else f"\n        -> {cozum}"))
        sorun += 0 if ok else 1

    satir(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]}", "Python 3.10+ kur")
    satir(ffmpeg_var(), "ffmpeg", "winget install Gyan.FFmpeg  (sonra terminali kapat-ac)")
    for paket, kur in [("requests", "requests"), ("PIL", "pillow"), ("dotenv", "python-dotenv"), ("edge_tts", "edge-tts"),
                       ("kokoro", "kokoro"), ("soundfile", "soundfile"),
                       ("googleapiclient", "google-api-python-client"), ("google_auth_oauthlib", "google-auth-oauthlib")]:
        try:
            __import__(paket)
            satir(True, f"python paketi: {kur}")
        except ImportError:
            ipucu = f"python -m pip install -U {kur}"
            if kur in ("kokoro", "soundfile"):
                ipucu += "   (kurulamazsa deneme icin ucretsiz yedek ses: --ses edge)"
            satir(False, f"python paketi: {kur}", ipucu)
    satir((KOK / "kanal" / "fontlar" / "Anton-Regular.ttf").exists(), "yazi tipleri", "kanal/fontlar klasoru eksik")
    satir((KOK / ".env").exists(), ".env dosyasi", "Claude Code'da /kurulum yaz")
    a = ayarlar()
    ses = a["ses"]["saglayici"]
    if ses == "elevenlabs":
        satir(bool(os.environ.get("ELEVENLABS_API_KEY")), "ELEVENLABS_API_KEY", ".env'e ekle")
        satir(bool(os.environ.get("ELEVENLABS_VOICE_ID") or a["ses"].get("ses_id")), "ELEVENLABS_VOICE_ID", ".env'e ekle")
    satir(bool(os.environ.get("PIXABAY_API_KEY")), "PIXABAY_API_KEY (ucretsiz stok video + foto, ANA kaynak)", "pixabay.com/api/docs adresinde giris yap, anahtari .env'e ekle")
    print(f"[{'TAMAM' if os.environ.get('FAL_KEY') else 'ISTEGE'}] FAL_KEY (AI gorsel/video; yoksa stok fotograf kullanilir)")
    print(f"[{'TAMAM' if os.environ.get('COVERR_API_KEY') else 'ISTEGE'}] COVERR_API_KEY (ek ucretsiz stok video)")
    print(f"[{'TAMAM' if os.environ.get('PEXELS_API_KEY') else 'ISTEGE'}] PEXELS_API_KEY (Pexels su an yeni anahtar vermiyor; varsa kullanilir)")
    print("[TAMAM] Openverse + NASA arsiv fotograflari (anahtar gerekmez)")
    if a.get("youtube", {}).get("yukleme_acik", True):
        satir((KOK / "kanal" / "youtube_client_secret.json").exists(), "YouTube OAuth istemcisi", "/kurulum adim 6")
        satir((KOK / "kanal" / "youtube_token.json").exists(), "YouTube girisi", "python -m hat youtube-giris")
    else:
        print("[ISTEGE] YouTube baglantisi: DENEME MODU (ayarlar.json -> youtube.yukleme_acik: false). "
              "Videolar yalnizca bilgisayarda uretilir, yuklenmez.")
    muzik = list((KOK / "kanal" / "muzik").glob("*.mp3")) + list((KOK / "kanal" / "muzik").glob("*.m4a"))
    print(f"[{'TAMAM' if muzik else 'ISTEGE'}] arka plan muzigi: {len(muzik)} dosya (YouTube Ses Kutuphanesi'nden indir, kanal/muzik'e koy)")
    try:
        str(KOK).encode("ascii")
    except UnicodeEncodeError:
        print(f"[BILGI] Proje yolunda Turkce karakter var ({KOK}). Sorun cikarsa klasoru C:\\kanal gibi bir yere tasi.")

    if canli:
        import requests
        print("\nCanli deneme:")
        if os.environ.get("ELEVENLABS_API_KEY"):
            r = requests.get("https://api.elevenlabs.io/v1/user/subscription", headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}, timeout=20)
            if r.ok:
                j = r.json()
                print(f"  ElevenLabs: {j.get('tier')} plani, kalan karakter {j.get('character_limit', 0) - j.get('character_count', 0):,}")
            else:
                print(f"  ElevenLabs HATA {r.status_code}: {r.text[:200]}")
                sorun += 1
        denemeler = []
        if os.environ.get("PIXABAY_API_KEY"):
            denemeler.append(("Pixabay", "https://pixabay.com/api/videos/", {"key": os.environ["PIXABAY_API_KEY"], "q": "cargo ship", "per_page": 3}, {}))
        if os.environ.get("COVERR_API_KEY"):
            denemeler.append(("Coverr", "https://api.coverr.co/videos", {"query": "cargo ship", "page_size": 1},
                              {"Authorization": f"Bearer {os.environ['COVERR_API_KEY']}"}))
        if os.environ.get("PEXELS_API_KEY"):
            denemeler.append(("Pexels", "https://api.pexels.com/videos/search", {"query": "cargo ship", "per_page": 1},
                              {"Authorization": os.environ["PEXELS_API_KEY"]}))
        denemeler.append(("Openverse", "https://api.openverse.org/v1/images/", {"q": "cargo ship", "license": "cc0,pdm,by", "page_size": 1}, {}))
        denemeler.append(("NASA", "https://images-api.nasa.gov/search", {"q": "port", "media_type": "image", "page_size": 1}, {}))
        for ad, url, prm, bas in denemeler:
            try:
                r = requests.get(url, params=prm, headers={"User-Agent": "BehindTheMargin-video-pipeline/1.0", **bas}, timeout=20)
                print(f"  {ad}: calisiyor" if r.ok else f"  {ad} HATA {r.status_code}: {r.text[:120]}")
                sorun += 0 if r.ok else 1
            except Exception as e:  # noqa: BLE001
                print(f"  {ad} HATA: {e}")
                sorun += 1
        if ses == "kokoro":
            try:
                from .ses import kokoro
                tmp = KOK / "kokoro_deneme.mp3"
                print("  Kokoro ses deneniyor (ilk seferde model indirilir, 1-3 dk)...")
                k = kokoro("This is a quick test of the narrator voice.", tmp, a["ses"])
                print(f"  Kokoro ses: calisiyor ({len(k)} kelime zamani) -> dinlemek icin: {tmp}")
            except Exception as e:  # noqa: BLE001
                print(f"  Kokoro ses HATA: {e}")
                sorun += 1
        try:
            from .ses import edge
            tmp = KOK / "_deneme.mp3"
            k = edge("This is a quick test.", tmp, a["ses"])
            print(f"  Edge ses: calisiyor ({len(k)} kelime zamani)")
            tmp.unlink(missing_ok=True)
        except Exception as e:  # noqa: BLE001
            print(f"  Edge ses HATA: {e}")
    print(f"\n{sorun} eksik." if sorun else "\nHer sey hazir.")
    return sorun


def yeni(ad: str) -> Path:
    kod = time.strftime("%y%m")
    mevcut = sorted(p.name for p in (KOK / "videolar").glob(f"{kod}-*"))
    sira = len(mevcut) + 1
    klasor = KOK / "videolar" / f"{kod}-{sira:02d}-{ad}"
    klasor.mkdir(parents=True, exist_ok=False)
    sablon = json_oku(KOK / "kanal" / "senaryo-sablonu.json")
    sablon["kod"] = klasor.name
    json_yaz(klasor / "senaryo.json", sablon)
    print(klasor)
    return klasor


def uret(klasor: Path, adimlar: list, sahte: bool, ses_saglayici: str) -> None:
    from . import gorsel, render, ses, shorts, thumbnail
    a = ayarlar()
    s = senaryo_oku(klasor)
    t0 = time.time()
    if sahte:
        ses_saglayici = ses_saglayici or "sessiz"
    sesler = gorseller = None
    if "ses" in adimlar:
        log("1/5 Seslendirme")
        sesler = ses.uret(klasor, s, a, ses_saglayici)
    sesler = sesler or json_oku(klasor / "ses" / "zamanlar.json")
    if "gorsel" in adimlar:
        log("2/5 Gorseller")
        gorseller = gorsel.uret(klasor, s, a, sesler, sahte=sahte)
    gorseller = gorseller or json_oku(klasor / "gorseller" / "gorseller.json")
    if "video" in adimlar:
        log("3/5 Video, altyazi, bolumler, onizleme")
        render.uret(klasor, s, a, sesler, gorseller)
    if "thumbnail" in adimlar:
        log("4/5 Thumbnail")
        thumbnail.uret(klasor, s, a, sahte=sahte)
    if "shorts" in adimlar:
        log("5/5 Shorts")
        shorts.uret(klasor, s, a, sesler, gorseller)
    m = json_oku(klasor / "maliyet.json", {}).get("toplam_usd", 0)
    log(f"\nBITTI ({(time.time() - t0) / 60:.1f} dk) · tahmini harcama: ${m:.2f}")
    log(f"Kontrol et: {klasor / 'son.mp4'}  ·  onizleme: {klasor / 'onizleme.jpg'}")


def maliyet(klasor: Path = None) -> None:
    klasorler = [klasor] if klasor else sorted((KOK / "videolar").glob("*/"))
    toplam = 0
    for k in klasorler:
        v = json_oku(Path(k) / "maliyet.json", {})
        if v:
            print(f"{Path(k).name}: ${v.get('toplam_usd', 0):.2f}")
            toplam += v.get("toplam_usd", 0)
    print(f"TOPLAM: ${toplam:.2f}")


def main() -> None:
    ap = argparse.ArgumentParser(prog="python -m hat", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    alt = ap.add_subparsers(dest="komut", required=True)
    k = alt.add_parser("kontrol")
    k.add_argument("--canli", action="store_true")
    y = alt.add_parser("yeni")
    y.add_argument("ad")
    u = alt.add_parser("uret")
    u.add_argument("klasor")
    u.add_argument("--adim", default=",".join(ADIMLAR))
    u.add_argument("--sahte", action="store_true", help="internet/API olmadan test")
    u.add_argument("--ses", choices=["kokoro", "edge", "elevenlabs", "sessiz"])
    yk = alt.add_parser("yukle")
    yk.add_argument("klasor")
    yk.add_argument("--shorts-yok", action="store_true")
    dg = alt.add_parser("dagitim")
    dg.add_argument("klasor")
    g = alt.add_parser("youtube-giris")
    g.add_argument("--yeniden", action="store_true")
    m = alt.add_parser("maliyet")
    m.add_argument("klasor", nargs="?")
    a = ap.parse_args()

    if a.komut == "kontrol":
        sys.exit(1 if kontrol(a.canli) else 0)
    if a.komut == "yeni":
        yeni(a.ad)
    elif a.komut == "uret":
        adimlar = [x.strip() for x in a.adim.split(",") if x.strip()]
        bilinmeyen = set(adimlar) - set(ADIMLAR)
        if bilinmeyen:
            sys.exit(f"Bilinmeyen adim: {bilinmeyen}")
        uret(Path(a.klasor).resolve(), adimlar, a.sahte, a.ses)
    elif a.komut == "yukle":
        if not ayarlar().get("youtube", {}).get("yukleme_acik", True):
            print("DENEME MODU: YouTube yuklemesi kapali (ayarlar.json -> youtube.yukleme_acik: false). "
                  "Video bilgisayarda hazir: son.mp4. Yuklemeye hazir olunca /kurulum adim 6 + yukleme_acik: true.")
            return
        from .yukle import yukle
        kl = Path(a.klasor).resolve()
        sonuc = yukle(kl, senaryo_oku(kl), ayarlar(), not a.shorts_yok)
        print(json.dumps(sonuc, indent=1))
        print("Videolar OZEL yuklendi. YouTube Studio'da izle, begendiysen Gorunurluk > Herkese acik / Planla.")
    elif a.komut == "dagitim":
        from .dagitim import uret as dagitim_uret
        kl = Path(a.klasor).resolve()
        dagitim_uret(kl, senaryo_oku(kl), ayarlar())
        print(f"Instagram/Facebook paketi: {kl / 'dagitim'}  (adimlar PAYLAS.txt icinde)")
    elif a.komut == "youtube-giris":
        from .yukle import giris
        giris(a.yeniden)
        print("YouTube girisi tamam.")
    elif a.komut == "maliyet":
        maliyet(Path(a.klasor) if a.klasor else None)


if __name__ == "__main__":
    main()
