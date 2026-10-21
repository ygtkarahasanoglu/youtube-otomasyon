"""Instagram + Facebook Reels paylasim paketi. Paylasmaz; kullanici Meta Business Suite'te planlar.

senaryo.json -> "dagitim": {"klipler": [
    {"short": 1, "gun": 1, "kapak_sn": 1.0,
     "instagram": {"aciklama": "...", "hashtagler": ["#..."]},
     "facebook": {"aciklama": "...", "hashtagler": ["#..."]}}]}
Klipler, uretim hattinin zaten urettigi shorts/short-N.mp4 dosyalaridir (ek maliyet yok).
Cikti: videolar/<klasor>/dagitim/  N-reel.mp4, N-kapak.jpg, N-instagram.txt, N-facebook.txt, PAYLAS.txt
"""
import shutil
import sys
from pathlib import Path

from .ayar import ffmpeg, json_oku, log, sure


def _metin(aciklama: str, hashtagler: list) -> str:
    aciklama = (aciklama or "").strip()
    etiket = " ".join(h if h.startswith("#") else f"#{h}" for h in (hashtagler or []) if h)
    return (aciklama + ("\n\n" + etiket if etiket else "")).strip() + "\n"


def uret(klasor: Path, senaryo: dict, ayar: dict) -> list:
    klasor = Path(klasor).resolve()
    klipler = (senaryo.get("dagitim") or {}).get("klipler") or []
    if not klipler:
        sys.exit("senaryo.json -> dagitim.klipler bos. Once dagitim-direktoru ajanini calistir (/dagitim).")
    shorts = senaryo.get("shorts") or []
    uzun = json_oku(klasor / "yukleme.json", {}).get("uzun")
    d = ayar.get("dagitim", {})
    hedef = klasor / "dagitim"
    hedef.mkdir(exist_ok=True)

    rehber = [
        f"REELS PAYLASIM PAKETI - {senaryo.get('baslik', klasor.name)}",
        "=" * 60,
        "",
        "Nasil paylasilir (her Reel icin bir kez, toplam 2-3 dk):",
        "  1. business.facebook.com (Meta Business Suite) -> Olustur -> Reel",
        "  2. Paylasilacak yer: Instagram VE Facebook ikisini de sec",
        "  3. N-reel.mp4 dosyasini yukle",
        "  4. Aciklama: N-instagram.txt icindeki metni yapistir",
        "     (Facebook icin ayri metin istenirse N-facebook.txt)",
        "  5. Kapak: N-kapak.jpg",
        "  6. Yapay zeka etiketi: " + ("ACIK (anlatici sesi yapay zeka)" if d.get("ai_etiketi", True) else "kapali"),
        "  7. Muzik EKLEME (ses hazir). -> Planla",
        "",
        "Sira: once uzun video YouTube'da herkese acik olur (gun 0), sonra Reels.",
        f"Saat: ABD Dogu {d.get('paylasim_saati_et', '12:00')} = Turkiye 19:00 (Mart-Kasim basi) / 20:00 (Kasim-Mart).",
        "",
    ]
    if not uzun:
        rehber += ["NOT: Uzun video henuz yuklenmemis; Facebook metinlerine YouTube linki eklenmedi.",
                   "     Yukledikten sonra 'python -m hat dagitim' komutunu tekrar calistir.", ""]

    cikti = []
    for n, k in enumerate(klipler, 1):
        i = int(k["short"])
        if not 1 <= i <= len(shorts):
            sys.exit(f"dagitim.klipler[{n}]: short={i} gecersiz (senaryo.json'da {len(shorts)} shorts var).")
        kaynak = klasor / "shorts" / f"short-{i}.mp4"
        if not kaynak.exists():
            sys.exit(f"{kaynak} yok. Once: python -m hat uret \"{klasor}\" --adim shorts")
        reel = hedef / f"{n}-reel.mp4"
        shutil.copy2(kaynak, reel)
        sn = float(k.get("kapak_sn", 1.0))
        ffmpeg("-ss", f"{sn:.2f}", "-i", reel, "-frames:v", 1, "-q:v", 2, hedef / f"{n}-kapak.jpg")

        ig = k.get("instagram") or {}
        fb = k.get("facebook") or {}
        fb_ac = (fb.get("aciklama") or ig.get("aciklama") or "").strip()
        if uzun and "youtu" not in fb_ac:
            fb_ac += f"\n\nFull video: https://youtu.be/{uzun}"
        (hedef / f"{n}-instagram.txt").write_text(_metin(ig.get("aciklama", ""), ig.get("hashtagler")), encoding="utf-8")
        (hedef / f"{n}-facebook.txt").write_text(_metin(fb_ac, fb.get("hashtagler") or ig.get("hashtagler", [])[:3]),
                                                 encoding="utf-8")

        saniye = sure(reel)
        gun = int(k.get("gun", [1, 3, 5][min(n - 1, 2)]))
        satirlar = (ig.get("aciklama") or "").strip().splitlines()
        ilk = satirlar[0] if satirlar else shorts[i - 1].get("baslik", "")
        rehber.append(f"Reel {n}  ->  gun {gun} (uzun video yayinlandiktan {gun} gun sonra), {saniye:.0f} sn")
        rehber.append(f"   {ilk[:110]}")
        if saniye > 60:
            rehber.append("   UYARI: 60 sn ustu; kisaltmak icin Claude'a soyle.")
        rehber.append("")
        cikti.append({"reel": str(reel), "sure": round(saniye, 1), "gun": gun})
        log(f"  reel-{n}: {saniye:.0f} sn, gun {gun}")

    (hedef / "PAYLAS.txt").write_text("\n".join(rehber), encoding="utf-8")
    log(f"Paket hazir: {hedef}")
    return cikti
