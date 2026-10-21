#!/usr/bin/env python3
"""Transkript cikarici.

1) YouTube linki  -> videonun altyazisini (once Turkce, yoksa Ingilizce; elle yazilmis yoksa otomatik) indirir.
   Video indirmez. Gerekli:  pip install -U yt-dlp
2) Yerel dosya (kendi cekimin: mp4, mov, wav, mp3) -> faster-whisper ile konusmayi yaziya doker.
   Gerekli:  pip install -U faster-whisper   (ilk calismada model indirilir)

Her iki durumda da <ad>.srt (zaman kodlu) ve <ad>.txt (duz metin) yazar.

Ornek:
  python transkript.py https://www.youtube.com/watch?v=XXXX --out-dir arastirma/transkript
  python transkript.py videolar/2610-03-x/ham/cekim1.mp4 --model small
"""
import argparse
import glob
import html
import re
import subprocess
import sys
from pathlib import Path


def zaman(sn: float) -> str:
    ms = int(round(sn * 1000))
    s, ms = divmod(ms, 1000)
    d, s = divmod(s, 60)
    h, d = divmod(d, 60)
    return f"{h:02d}:{d:02d}:{s:02d},{ms:03d}"


def vtt_saniye(t: str) -> float:
    p = t.replace(",", ".").split(":")
    p = [float(x) for x in p]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def vtt_oku(yol: Path) -> list:
    """VTT'yi (sn_bas, sn_bit, metin) listesine cevirir; otomatik altyazidaki tekrar eden satirlari ayiklar."""
    bloklar = re.split(r"\n\s*\n", yol.read_text(encoding="utf-8", errors="ignore").replace("\r", ""))
    sonuc, onceki = [], set()
    for b in bloklar:
        satirlar = b.strip("\n").splitlines()
        i = next((k for k, s in enumerate(satirlar) if "-->" in s), None)
        if i is None:
            continue
        m = re.search(r"([\d:.,]+)\s*-->\s*([\d:.,]+)", satirlar[i])  # satirin geri kalani (align:, position:) atilir
        metinler = []
        for s in satirlar[i + 1:]:
            s = html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
            if s and s not in metinler:
                metinler.append(s)
        # Otomatik altyazi "kayan" yazilir: bir onceki ipucunun satirlari tekrar gelir; yalnizca yenileri al.
        yeni = [s for s in metinler if s not in onceki]
        onceki = set(metinler)
        if yeni:
            sonuc.append((vtt_saniye(m.group(1)), vtt_saniye(m.group(2)), " ".join(yeni)))
    return sonuc


def yaz(parcalar: list, hedef: Path) -> None:
    hedef.parent.mkdir(parents=True, exist_ok=True)
    srt = [f"{i}\n{zaman(a)} --> {zaman(b)}\n{t}\n" for i, (a, b, t) in enumerate(parcalar, 1)]
    hedef.with_suffix(".srt").write_text("\n".join(srt), encoding="utf-8")
    hedef.with_suffix(".txt").write_text(" ".join(t for _, _, t in parcalar), encoding="utf-8")
    print(f"Yazildi: {hedef.with_suffix('.srt')} ve .txt ({len(parcalar)} parca)")


def youtube(url: str, out_dir: Path, diller: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    komut = [sys.executable, "-m", "yt_dlp", "--skip-download", "--write-subs", "--write-auto-subs",
             "--sub-langs", diller, "--sub-format", "vtt", "--no-warnings",
             "-o", str(out_dir / "%(id)s.%(ext)s"), url]
    r = subprocess.run(komut, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        if "No module named yt_dlp" in r.stderr:
            sys.exit("yt-dlp kurulu degil:  pip install -U yt-dlp")
        sys.exit(f"yt-dlp hatasi:\n{r.stderr.strip()[:800]}")
    vid = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", url)
    desen = f"{vid.group(1)}*.vtt" if vid else "*.vtt"
    vttler = sorted(glob.glob(str(out_dir / desen)))
    if not vttler:
        sys.exit("Bu video icin altyazi bulunamadi. Videonun altyazisi kapali olabilir.")
    # Turkce elle yazilmis > Turkce otomatik > diger
    vttler.sort(key=lambda p: (0 if ".tr." in p and "-orig" not in p else 1 if ".tr" in p else 2))
    secilen = Path(vttler[0])
    yaz(vtt_oku(secilen), out_dir / secilen.name.split(".")[0])
    for v in vttler:
        Path(v).unlink(missing_ok=True)


def yerel(dosya: Path, out_dir: Path, model_adi: str, dil: str) -> None:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper kurulu degil:  pip install -U faster-whisper")
    print(f"Model yukleniyor ({model_adi})... ilk seferde indirilir.", file=sys.stderr)
    model = WhisperModel(model_adi, device="auto", compute_type="int8")
    segmentler, bilgi = model.transcribe(str(dosya), language=dil or None, vad_filter=False)
    parcalar = []
    for s in segmentler:
        parcalar.append((s.start, s.end, s.text.strip()))
        print(f"\r{zaman(s.end)} / {zaman(bilgi.duration)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    yaz(parcalar, out_dir / dosya.stem)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kaynak", help="YouTube linki veya yerel video/ses dosyasi")
    ap.add_argument("--out-dir", help="Cikti klasoru (varsayilan: link icin arastirma/transkript, dosya icin dosyanin klasoru)")
    ap.add_argument("--diller", default="en.*,en", help="YouTube altyazi dilleri (yt-dlp bicimi)")
    ap.add_argument("--model", default="small", help="Whisper modeli: tiny, base, small, medium, large-v3 (varsayilan small)")
    ap.add_argument("--dil", default="tr", help="Yerel dosyanin dili (varsayilan tr; bos birakirsan otomatik)")
    a = ap.parse_args()

    if a.kaynak.startswith("http"):
        youtube(a.kaynak, Path(a.out_dir or "arastirma/transkript"), a.diller)
    else:
        p = Path(a.kaynak)
        if not p.exists():
            sys.exit(f"Dosya yok: {p}")
        yerel(p, Path(a.out_dir) if a.out_dir else p.parent, a.model, a.dil)


if __name__ == "__main__":
    main()
