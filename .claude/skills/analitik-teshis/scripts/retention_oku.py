#!/usr/bin/env python3
"""Kitle tutma (audience retention) okuyucu.

Girdi: YouTube Studio > Analytics > Gelismis mod'dan disa aktarilan kitle tutma CSV'si
(veya iki sutunlu basit CSV: konum, tutma%). Sutun adlari Turkce/Ingilizce olabilir:
konum sutunu yuzde (0-100) veya saniye; tutma sutunu yuzde.

Cikti: 30. saniyedeki kayip (hook sizintisi), en sert dususler (ucurumlar), yukselisler
(tekrar izlenen yerler), orta bolum egimi. --srt verilirse her noktada ne soylendigini gosterir.

Ornek:
  python retention_oku.py videolar/2610-03-x/analiz/retention.csv --sure 12:41 --srt videolar/2610-03-x/altyazi.srt
"""
import argparse
import csv
import re
import sys
from pathlib import Path


def sayi(x: str):
    x = (x or "").strip().replace("%", "").replace(" ", "")
    if x.count(",") == 1 and "." not in x:
        x = x.replace(",", ".")
    try:
        return float(x)
    except ValueError:
        return None


def sure_sn(t: str) -> float:
    p = [float(v) for v in t.split(":")]
    return sum(v * 60 ** i for i, v in enumerate(reversed(p)))


def mmss(s: float) -> str:
    return f"{int(s // 60):02d}:{int(s % 60):02d}"


def srt_metin(yol: Path, t: float) -> str:
    for b in re.split(r"\n\s*\n", yol.read_text(encoding="utf-8-sig").strip()):
        m = re.search(r"(\d+):(\d+):(\d+)[,.]\d+\s*-->\s*(\d+):(\d+):(\d+)[,.]\d+", b)
        if m and int(m[4]) * 3600 + int(m[5]) * 60 + int(m[6]) > t:
            return " ".join(b[m.end():].split())[:80]
    return ""


def oku(yol: Path):
    with yol.open(encoding="utf-8-sig", newline="") as f:
        orn = f.read(4096)
        f.seek(0)
        ayrac = ";" if orn.count(";") > orn.count(",") else ("\t" if "\t" in orn else ",")
        satirlar = [r for r in csv.reader(f, delimiter=ayrac) if r]
    baslik = satirlar[0]
    veri = [r for r in satirlar[1:] if sum(sayi(c) is not None for c in r) >= 2]
    sayisal = [i for i in range(len(baslik)) if veri and all(sayi(r[i]) is not None for r in veri if i < len(r))]
    if len(sayisal) < 2:
        sys.exit(f"En az iki sayisal sutun bulunamadi. Basliklar: {baslik}")
    adlar = [h.lower() for h in baslik]
    poz = next((i for i in sayisal if any(k in adlar[i] for k in ("position", "konum", "zaman", "saniye", "time"))), sayisal[0])
    tut = next((i for i in sayisal if i != poz and any(k in adlar[i] for k in ("absolute", "mutlak"))), None)
    if tut is None:
        tut = next((i for i in sayisal if i != poz and any(k in adlar[i] for k in ("retention", "tutma", "izleyici", "audience"))), None)
    if tut is None:
        tut = next(i for i in sayisal if i != poz)
    noktalar = sorted((sayi(r[poz]), sayi(r[tut])) for r in veri)
    return noktalar, baslik[poz], baslik[tut]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--sure", help="Video suresi MM:SS (konum yuzde ise gerekli)")
    ap.add_argument("--srt", help="Altyazi; dususlerde ne soylendigini gosterir")
    ap.add_argument("--en", type=int, default=5, help="Kac ucurum listelensin (varsayilan 5)")
    a = ap.parse_args()

    noktalar, pad, tad = oku(Path(a.csv))
    yuzde_konum = max(p for p, _ in noktalar) <= 100.5 and a.sure
    toplam = sure_sn(a.sure) if a.sure else max(p for p, _ in noktalar)
    if max(p for p, _ in noktalar) <= 100.5 and not a.sure:
        print("Uyari: konum yuzde gibi; saniye icin --sure ver. Simdilik konum = yuzde.", file=sys.stderr)
    pts = [((p / 100 * toplam) if yuzde_konum else p, r) for p, r in noktalar]
    olcek = 100 if max(r for _, r in pts) <= 1.5 else 1  # 0-1 araligindaysa yuzdeye cevir
    pts = [(t, r * olcek) for t, r in pts]

    def deger(t):
        for (t0, r0), (t1, r1) in zip(pts, pts[1:]):
            if t0 <= t <= t1:
                return r0 + (r1 - r0) * ((t - t0) / (t1 - t0) if t1 > t0 else 0)
        return pts[-1][1]

    def metin(t):
        return f"  «{srt_metin(Path(a.srt), t)}»" if a.srt else ""

    print(f"Sutunlar: konum='{pad}', tutma='{tad}', {len(pts)} nokta, sure {mmss(toplam)}\n")
    bas = pts[0][1]
    r30 = deger(min(30, toplam))
    print(f"Baslangic: %{bas:.0f} · 30. saniye: %{r30:.0f} · Hook sizintisi: {bas - r30:.0f} puan")
    print(f"Ortada (%50): %{deger(toplam / 2):.0f} · Sonda: %{pts[-1][1]:.0f}")
    print(f"Ortalama izlenme (egri alani, yaklasik): %{sum(deger(toplam * i / 100) for i in range(101)) / 101:.0f}\n")

    pencere = max(toplam * 0.03, 5)
    dususler, yukselisler = [], []
    t = 30.0
    while t + pencere <= toplam * 0.97:
        fark = deger(t + pencere) - deger(t)
        (dususler if fark < 0 else yukselisler).append((fark, t))
        t += pencere / 2
    dususler.sort()
    secilen = []
    for fark, t in dususler:
        if all(abs(t - s) > pencere * 2 for _, s in secilen):
            secilen.append((fark, t))
        if len(secilen) >= a.en:
            break
    print(f"En sert dususler (30. saniyeden sonra, {pencere:.0f} sn pencere):")
    for fark, t in sorted(secilen, key=lambda x: x[1]):
        print(f"  {mmss(t)}-{mmss(t + pencere)}: {fark:.1f} puan{metin(t)}")
    yuk = sorted(yukselisler, reverse=True)[:3]
    if yuk and yuk[0][0] > 0.5:
        print("\nYukselisler (geri sarilan / tekrar izlenen yerler):")
        for fark, t in sorted(yuk, key=lambda x: x[1]):
            if fark > 0.5:
                print(f"  {mmss(t)}: +{fark:.1f} puan{metin(t)}")


if __name__ == "__main__":
    main()
