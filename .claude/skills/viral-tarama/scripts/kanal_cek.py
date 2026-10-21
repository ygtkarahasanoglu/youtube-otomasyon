#!/usr/bin/env python3
"""Bir veya daha fazla YouTube kanalinin video listesini (baslik, izlenme, sure) JSON olarak ceker.

Yalnizca herkese acik listeyi okur, video indirmez. yt-dlp gerekir:  pip install -U yt-dlp

Ornek:
  python kanal_cek.py https://www.youtube.com/@kanal --limit 60 --out arastirma/veri/kanal.json
  python kanal_cek.py @kanal1 @kanal2 --shorts --out arastirma/veri/shorts.json
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def kanal_url(girdi: str, sekme: str) -> str:
    u = girdi.strip()
    if u.startswith("@"):
        u = "https://www.youtube.com/" + u
    if not u.startswith("http"):
        u = "https://www.youtube.com/@" + u
    u = u.rstrip("/")
    for son in ("/videos", "/shorts", "/streams", "/featured"):
        if u.endswith(son):
            u = u[: -len(son)]
    return f"{u}/{sekme}"


def cek(url: str, limit: int) -> dict:
    komut = [sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--playlist-end", str(limit), "--no-warnings", url]
    try:
        sonuc = subprocess.run(komut, capture_output=True, text=True, encoding="utf-8", timeout=300)
    except FileNotFoundError:
        sys.exit("Python bulunamadi.")
    if sonuc.returncode != 0:
        if "No module named yt_dlp" in sonuc.stderr:
            sys.exit("yt-dlp kurulu degil. Kur:  pip install -U yt-dlp")
        sys.exit(f"yt-dlp hatasi ({url}):\n{sonuc.stderr.strip()[:800]}")
    return json.loads(sonuc.stdout)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kanallar", nargs="+", help="Kanal linki veya @kullaniciadi")
    ap.add_argument("--limit", type=int, default=50, help="Kanal basina en yeni N video (varsayilan 50)")
    ap.add_argument("--shorts", action="store_true", help="Videolar yerine Shorts sekmesini oku")
    ap.add_argument("--out", help="JSON cikti dosyasi (yoksa ekrana yazar)")
    a = ap.parse_args()

    sekme = "shorts" if a.shorts else "videos"
    satirlar = []
    for k in a.kanallar:
        veri = cek(kanal_url(k, sekme), a.limit)
        kanal_adi = veri.get("channel") or veri.get("uploader") or veri.get("title") or k
        for e in veri.get("entries") or []:
            if not e:
                continue
            vid = e.get("id")
            satirlar.append({
                "kanal": kanal_adi,
                "baslik": e.get("title"),
                "url": e.get("url") or (f"https://www.youtube.com/watch?v={vid}" if vid else None),
                "izlenme": e.get("view_count"),
                "sure_sn": e.get("duration"),
                "format": "shorts" if a.shorts else "uzun",
            })
        print(f"{kanal_adi}: {sum(1 for s in satirlar if s['kanal'] == kanal_adi)} video", file=sys.stderr)

    cikti = json.dumps(satirlar, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(cikti, encoding="utf-8")
        print(f"Yazildi: {a.out} ({len(satirlar)} satir)", file=sys.stderr)
    else:
        print(cikti)


if __name__ == "__main__":
    main()
