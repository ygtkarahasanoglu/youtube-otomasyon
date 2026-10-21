#!/usr/bin/env python3
"""YouTube arama kutusunun otomatik tamamlama onerilerini toplar (Turkce, Turkiye).

Ana ifadeyi; harf ekleriyle (a-z, c, g, i, o, s, u) ve soru kaliplariyla (nasil, neden, en iyi...) genisletir.
Cikan liste "insanlar bunu yaziyor" sinyalidir; ARAMA HACMI DEGILDIR.
Not: Bu, YouTube/Google'in herkese acik ama resmi olmayan oneri adresidir; degisebilir veya engellenebilir.

Ornek:
  python oneri_cek.py "tekne bakımı" --out arastirma/anahtar-tekne-bakimi.md
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ADRES = "https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=en&gl=US&q="
HARFLER = list("abcdefghijklmnopqrstuvwxyz")
ON_EKLER = ["how", "why", "what", "how much", "best", "cheapest", "is"]
SON_EKLER = ["explained", "cost", "price", "business model", "worth it", "2026", "vs"]


def oner(sorgu: str) -> list:
    istek = urllib.request.Request(ADRES + urllib.parse.quote(sorgu), headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(istek, timeout=10) as y:
            ham = y.read().decode("utf-8", errors="ignore")
        return json.loads(ham)[1]
    except Exception as e:  # noqa: BLE001
        print(f"  ({sorgu}: {e})", file=sys.stderr)
        return []


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ifade")
    ap.add_argument("--hizli", action="store_true", help="Harf genislemesini atla")
    ap.add_argument("--out", help="Markdown cikti")
    a = ap.parse_args()

    sorgular = [a.ifade] + [f"{o} {a.ifade}" for o in ON_EKLER] + [f"{a.ifade} {s}" for s in SON_EKLER]
    if not a.hizli:
        sorgular += [f"{a.ifade} {h}" for h in HARFLER]
    sayac, kaynak = {}, {}
    for i, s in enumerate(sorgular, 1):
        for o in oner(s):
            sayac[o] = sayac.get(o, 0) + 1
            kaynak.setdefault(o, s)
        print(f"\r{i}/{len(sorgular)}", end="", file=sys.stderr)
        time.sleep(0.25)
    print(file=sys.stderr)
    if not sayac:
        sys.exit("Hic oneri alinamadi (ag engeli veya adres degismis olabilir). Kullanicidan YouTube arama kutusuna yazip onerileri yapistirmasini iste.")
    sirali = sorted(sayac.items(), key=lambda kv: (-kv[1], kv[0]))
    md = [f"# YouTube önerileri: \"{a.ifade}\"", "",
          f"{len(sirali)} benzersiz öneri, {len(sorgular)} sorgu. 'Görülme' = kaç farklı sorguda çıktığı (hacim değildir).", "",
          "| # | Öneri | Görülme | İlk çıktığı sorgu |", "| --- | --- | --- | --- |"]
    md += [f"| {i} | {o} | {n} | {kaynak[o]} |" for i, (o, n) in enumerate(sirali, 1)]
    metin = "\n".join(md)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(metin + "\n", encoding="utf-8")
        print(f"Yazildi: {a.out}", file=sys.stderr)
    print(metin)


if __name__ == "__main__":
    main()
