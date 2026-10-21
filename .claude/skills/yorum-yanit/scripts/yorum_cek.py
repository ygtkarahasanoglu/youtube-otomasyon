#!/usr/bin/env python3
"""Bir videonun herkese acik yorumlarini ceker (API anahtari gerekmez, yt-dlp ile).

Cikti: Markdown tablo (en cok begenilen once) + JSON. Yanitlar ana yorumun altinda girintili.
Gerekli:  pip install -U yt-dlp

Ornek:
  python yorum_cek.py https://www.youtube.com/watch?v=XXXX --max 300 --out videolar/2610-03-x/yorumlar
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--max", type=int, default=300, help="En fazla yorum sayisi (varsayilan 300)")
    ap.add_argument("--siralama", choices=["top", "new"], default="top")
    ap.add_argument("--out", required=True, help="Cikti yolu (uzantisiz): .md ve .json yazilir")
    a = ap.parse_args()

    komut = [sys.executable, "-m", "yt_dlp", "--skip-download", "--write-comments", "-J", "--no-warnings",
             "--extractor-args", f"youtube:max_comments={a.max},all,100;comment_sort={a.siralama}", a.url]
    r = subprocess.run(komut, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        if "No module named yt_dlp" in r.stderr:
            sys.exit("yt-dlp kurulu degil:  pip install -U yt-dlp")
        sys.exit("yt-dlp hatasi:\n" + r.stderr[-800:])
    veri = json.loads(r.stdout)
    yorumlar = veri.get("comments") or []
    ana = [y for y in yorumlar if y.get("parent") in (None, "root")]
    yanit = {}
    for y in yorumlar:
        if y.get("parent") not in (None, "root"):
            yanit.setdefault(y["parent"], []).append(y)
    ana.sort(key=lambda y: -(y.get("like_count") or 0))

    def tarih(y):
        ts = y.get("timestamp")
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""

    def temiz(s):
        return " ".join((s or "").split()).replace("|", "/")

    md = [f"# Yorumlar — {veri.get('title', '')}", "",
          f"Toplam çekilen: {len(yorumlar)} (ana: {len(ana)}) · Video yorum sayısı: {veri.get('comment_count', '?')}", "",
          "| # | Beğeni | Tarih | Yazan | Yorum | Kanal yanıtladı mı |", "| --- | --- | --- | --- | --- | --- |"]
    for i, y in enumerate(ana, 1):
        cevaplar = yanit.get(y.get("id"), [])
        sahip = any(c.get("author_is_uploader") for c in cevaplar)
        md.append(f"| {i} | {y.get('like_count') or 0} | {tarih(y)} | {temiz(y.get('author'))} | {temiz(y.get('text'))} | {'evet' if sahip else ''} |")
        for c in cevaplar:
            md.append(f"| ↳ | {c.get('like_count') or 0} | {tarih(c)} | {temiz(c.get('author'))} | {temiz(c.get('text'))} | |")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    sade = [{k: y.get(k) for k in ("id", "parent", "author", "text", "like_count", "timestamp", "author_is_uploader")} for y in yorumlar]
    out.with_suffix(".json").write_text(json.dumps(sade, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Yazildi: {out.with_suffix('.md')} ve .json ({len(yorumlar)} yorum)")


if __name__ == "__main__":
    main()
