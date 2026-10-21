"""Thumbnail: AI veya stok arka plan + buyuk yazi + vurgu etiketi. 3 varyant (YouTube Test & Compare icin).

senaryo.json -> "thumbnail": {
  "prompt": "AI gorsel promptu (yazi icermeyen sahne)",   veya "arama": "stok foto aramasi"
  "varyantlar": [{"yazi": "IT COSTS $4", "vurgu": "$4", "etiket": "REALLY?"}, ...]   (en fazla 3)
}
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from . import gorsel
from .ayar import FONT_BASLIK, log

W, H = 1280, 720


def _satirla(kelimeler, f, genislik, max_satir):
    satirlar, sat = [], []
    for k in kelimeler:
        if sat and f.getlength(" ".join(sat + [k])) > genislik:
            satirlar.append(sat)
            sat = [k]
        else:
            sat.append(k)
    if sat:
        satirlar.append(sat)
    return len(satirlar) <= max_satir and all(f.getlength(" ".join(s)) <= genislik for s in satirlar), satirlar


def _etiket(metin, boy, renk):
    f = ImageFont.truetype(str(FONT_BASLIK), boy)
    tw = int(f.getlength(metin))
    h = int(boy * 1.5)
    uc = int(h * 0.45)
    w = tw + uc + int(boy * 0.9)
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(8 + uc, 8), (8 + w, 8), (8 + w, 8 + h), (8 + uc, 8 + h), (8, 8 + h // 2)], fill=renk, outline="#000", width=max(3, boy // 18))
    r = max(5, boy // 9)
    d.ellipse((8 + uc * 0.75 - r, 8 + h // 2 - r, 8 + uc * 0.75 + r, 8 + h // 2 + r), fill="#0B1220")
    d.text((8 + uc + (w - uc) / 2, 8 + h / 2), metin, font=f, fill="#0B1220", anchor="mm")
    return im.rotate(7, expand=True, resample=Image.BICUBIC)


def ciz(arka: Path, yazi: str, hedef: Path, vurgu: str = "", etiket: str = "", renkler: dict = None, dikey=False) -> Path:
    renkler = renkler or {"arka": "#0B1220", "vurgu": "#FFB703", "yazi": "#FFFFFF"}
    w, h = (1080, 1920) if dikey else (W, H)
    tuval = Image.new("RGBA", (w, h), renkler["arka"])
    if arka and Path(arka).exists():
        bg = ImageOps.fit(Image.open(arka).convert("RGBA"), (w, h), Image.LANCZOS)
        tuval.alpha_composite(bg)
        # yazinin okunmasi icin sol tarafa (dikeyde ust) koyu gecis
        maske = Image.new("L", (w, h), 0)
        md = ImageDraw.Draw(maske)
        if dikey:
            for y in range(int(h * 0.55)):
                md.line([(0, y), (w, y)], fill=int(220 * (1 - y / (h * 0.55))))
        else:
            for x in range(int(w * 0.62)):
                md.line([(x, 0), (x, h)], fill=int(225 * (1 - (x / (w * 0.62)) ** 1.6)))
        tuval.paste(Image.new("RGBA", (w, h), renkler["arka"]), (0, 0), maske)
    kelimeler = yazi.upper().split()
    vurgular = {v.strip().upper() for v in vurgu.split(",") if v.strip()}
    kx0, ky0, kx1, ky1 = (int(w * .06), int(h * .06), int(w * .94), int(h * .48)) if dikey else (int(w * .05), int(h * .1), int(w * .58), int(h * .9))
    boy = int(h * 0.3)
    while boy > 20:
        f = ImageFont.truetype(str(FONT_BASLIK), boy)
        sigdi, satirlar = _satirla(kelimeler, f, kx1 - kx0, 3 if not dikey else 4)
        if sigdi and int(boy * 1.18) * len(satirlar) <= ky1 - ky0:
            break
        boy -= 4
    d = ImageDraw.Draw(tuval)
    y = ky0 + (ky1 - ky0 - int(boy * 1.18) * len(satirlar)) // 2
    for sat in satirlar:
        x = kx0 + ((kx1 - kx0 - f.getlength(" ".join(sat))) / 2 if dikey else 0)
        for k in sat:
            d.text((x, y), k, font=f, fill=renkler["vurgu"] if k.strip(".,!?") in vurgular else renkler["yazi"],
                   stroke_width=max(4, boy // 14), stroke_fill="#000")
            x += f.getlength(k + " ")
        y += int(boy * 1.18)
    if etiket:
        et = _etiket(etiket.upper(), int(h * (0.05 if dikey else 0.1)), renkler["vurgu"])
        ex, ey = (w - et.width - int(w * .05), int(h * .52)) if dikey else (w - et.width - int(w * .04), int(h * .06))
        tuval.alpha_composite(et, (ex, ey))
    son = tuval.convert("RGB")
    hedef = Path(hedef)
    son.save(hedef, quality=92)
    son.resize((168, 94) if not dikey else (94, 168), Image.LANCZOS).save(hedef.with_name(hedef.stem + "_mini.png"))
    return hedef


def uret(klasor: Path, senaryo: dict, ayar: dict, sahte: bool = False) -> list:
    klasor = Path(klasor)
    t = senaryo.get("thumbnail", {})
    varyantlar = (t.get("varyantlar") or [{"yazi": senaryo.get("baslik", "")[:30]}])[:3]
    arka = klasor / "gorseller" / "thumbnail_arka.jpg"
    if not arka.exists() and not sahte:
        try:
            if t.get("prompt") and gorsel.anahtar("FAL_KEY", zorunlu=False):
                gorsel.ai_gorsel(t["prompt"] + ". no text, no letters, no logos, strong single subject, high contrast",
                                 arka, ayar, klasor)
            elif t.get("arama") or t.get("prompt"):
                r = gorsel.foto_zinciri(t.get("arama") or gorsel._prompttan_arama(t["prompt"]), klasor / "gorseller", senaryo.get("kod", ""))
                if r:
                    Path(r[0]).replace(arka)
        except Exception as e:  # noqa: BLE001
            log(f"  thumbnail arka plani alinamadi: {e}")
    renk = ayar["marka"]["renkler"]
    dosyalar = []
    for i, v in enumerate(varyantlar):
        harf = "abc"[i]
        dosyalar.append(ciz(arka, v.get("yazi", ""), klasor / f"thumbnail-{harf}.jpg", v.get("vurgu", ""), v.get("etiket", ""), renk))
    log(f"  thumbnail: {len(dosyalar)} varyant")
    return dosyalar
