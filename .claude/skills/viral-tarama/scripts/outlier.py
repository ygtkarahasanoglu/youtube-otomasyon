#!/usr/bin/env python3
"""Outlier bulucu: her videonun izlenmesini KENDI kanalinin medyan izlenmesine boler.

Buyuk kanal = cok izlenme degildir; onemli olan videonun kendi kanalini ne kadar astigidir.
Girdi: kanal_cek.py JSON dosyalari veya kanal,baslik,izlenme[,url] sutunlu CSV.

Ornek:
  python outlier.py arastirma/veri/*.json --min 3 --out arastirma/outlier.md
"""
import argparse
import csv
import glob
import json
import statistics
import sys
from pathlib import Path


def oku(yol: str) -> list:
    p = Path(yol)
    if p.suffix.lower() == ".json":
        return json.loads(p.read_text(encoding="utf-8"))
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sayi(x):
    if x in (None, ""):
        return None
    if isinstance(x, (int, float)):
        return int(x)
    try:
        return int(str(x).replace(".", "").replace(",", "").replace(" ", ""))
    except ValueError:
        return None


def binlik(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dosyalar", nargs="+")
    ap.add_argument("--min", type=float, default=3.0, help="En az kac kat (varsayilan 3)")
    ap.add_argument("--en-az-video", type=int, default=8, help="Medyan icin kanal basina en az video (varsayilan 8)")
    ap.add_argument("--out", help="Markdown cikti dosyasi")
    a = ap.parse_args()

    yollar = [y for d in a.dosyalar for y in (glob.glob(d) or [d])]
    satirlar = [s for y in yollar for s in oku(y)]
    kanallar = {}
    for s in satirlar:
        v = sayi(s.get("izlenme"))
        if v is not None:
            s["izlenme"] = v
            kanallar.setdefault(s.get("kanal", "?"), []).append(s)

    sonuc, atlanan = [], []
    for kanal, vs in kanallar.items():
        if len(vs) < a.en_az_video:
            atlanan.append(f"{kanal} ({len(vs)} video)")
            continue
        med = statistics.median(x["izlenme"] for x in vs) or 1
        for x in vs:
            kat = x["izlenme"] / med
            if kat >= a.min:
                sonuc.append((kat, kanal, x, med))
    sonuc.sort(key=lambda t: -t[0])

    out = [f"# Outlier listesi (en az {a.min}x kendi kanal medyanı)", "",
           "| # | Kat | Video | Kanal | İzlenme | Kanal medyanı | Format |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for i, (kat, kanal, x, med) in enumerate(sonuc, 1):
        bas = (x.get("baslik") or "").replace("|", "/")
        link = f"[{bas}]({x['url']})" if x.get("url") else bas
        out.append(f"| {i} | {kat:.1f}x | {link} | {kanal} | {binlik(x['izlenme'])} | {binlik(med)} | {x.get('format', '')} |")
    if not sonuc:
        out.append("| - | - | Eşiği geçen video yok; --min değerini düşür veya daha çok kanal ekle | | | | |")
    if atlanan:
        out += ["", f"Az videosu olduğu için medyanı güvenilmez, atlanan kanallar: {', '.join(atlanan)}"]
    metin = "\n".join(out)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(metin + "\n", encoding="utf-8")
        print(f"Yazildi: {a.out} ({len(sonuc)} outlier)", file=sys.stderr)
    print(metin)


if __name__ == "__main__":
    main()
