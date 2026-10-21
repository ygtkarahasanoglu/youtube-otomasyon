#!/usr/bin/env python3
"""English YouTube title + thumbnail text linter.

Checks: length/truncation, ALL CAPS, punctuation spam, clickbait words, vague words,
title/thumbnail duplication, thumbnail word count. A writing check, not a CTR predictor.

  python baslik_lint.py --title "How IKEA Really Makes Money" --thumb "IT'S NOT FURNITURE"
  python baslik_lint.py --file titles.txt --thumb "ONLY $0.30"
"""
import argparse
import re
import sys
from pathlib import Path

CLICKBAIT = {"shocking", "you won't believe", "insane", "mind-blowing", "gone wrong", "must watch", "exposed", "destroyed"}
VAGUE = {"things", "stuff", "some", "interesting", "amazing", "everything", "about"}
FILLER = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "it", "its", "it's", "how", "why", "what", "this", "that", "with", "you", "your"}


def words(s):
    return re.findall(r"[a-z0-9$%']+", s.lower())


def stem(w):
    return w[:5]


def check(title, thumb):
    out = []
    n = len(title)
    if n > 100:
        out.append(("ERROR", f"{n} chars; YouTube limit is 100"))
    elif n > 60:
        out.append(("WARN", f"{n} chars; gets truncated in search/suggested (aim ≤ 60)"))
    out.append(("INFO", f"Mobile shows roughly: \"{title[:45].rstrip()}…\"" if n > 45 else "Fits on mobile"))
    caps = [w for w in re.findall(r"\b[A-Z]{3,}\b", title) if w not in {"CEO", "USA", "IKEA", "AI", "NASA", "BMW", "IBM", "TSMC", "UPS", "DHL"}]
    if len(caps) > 1:
        out.append(("WARN", f"{len(caps)} ALL-CAPS words ({', '.join(caps)}); max 1"))
    if re.search(r"[!?]{2,}", title):
        out.append(("WARN", "Repeated !/?"))
    low = title.lower()
    for c in CLICKBAIT:
        if c in low:
            out.append(("WARN", f"Clickbait phrase \"{c}\" — hurts trust if not delivered"))
    vague = [w for w in VAGUE if re.search(rf"\b{re.escape(w)}\b", low)]
    if vague:
        out.append(("WARN", f"Vague words: {', '.join(vague)}"))
    if not re.search(r"\d|\$", title):
        out.append(("INFO", "No number; a sourced number often increases specificity"))
    if thumb:
        tw = words(thumb)
        if len(tw) > 4:
            out.append(("WARN", f"Thumbnail text has {len(tw)} words; max 4"))
        tst = {stem(w) for w in words(title) if w not in FILLER}
        meaningful = [w for w in tw if w not in FILLER]
        dup = [w for w in meaningful if stem(w) in tst]
        if meaningful and len(dup) / len(meaningful) >= 0.5:
            out.append(("WARN", f"Thumbnail repeats the title ({', '.join(dup)}); it should add a NEW hook"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--title", action="append", default=[])
    ap.add_argument("--file")
    ap.add_argument("--thumb", default="")
    a = ap.parse_args()
    titles = list(a.title)
    if a.file:
        titles += [s.strip() for s in Path(a.file).read_text(encoding="utf-8").splitlines() if s.strip()]
    if not titles:
        sys.exit("Give --title or --file")
    for i, t in enumerate(titles, 1):
        res = check(t, a.thumb)
        errs = sum(1 for r in res if r[0] == "ERROR")
        warns = sum(1 for r in res if r[0] == "WARN")
        print(f"\n{i}. [{'ERROR' if errs else ('CLEAN' if not warns else f'{warns} warn')}] {t} ({len(t)} chars)")
        for lvl, msg in res:
            print(f"   {lvl}: {msg}")


if __name__ == "__main__":
    main()
