"""Kanal stilinde grafikler: yazi karti, cubuk grafik, Maliyet Kulesi (hareketli), ekran yazisi bandi."""
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .ayar import FONT_BASLIK, FONT_METIN, ayarlar

W, H = 1920, 1080


def renkler() -> dict:
    try:
        return ayarlar()["marka"]["renkler"]
    except Exception:  # noqa: BLE001
        return {"arka": "#0B1220", "vurgu": "#FFB703", "yazi": "#FFFFFF", "kar": "#2BB673", "zarar": "#E63946", "gri": "#8A96A8"}


PALET = ["#FFB703", "#4EA8DE", "#2BB673", "#E63946", "#9B5DE5", "#F4A261", "#56CFE1", "#C9ADA7"]


def font(boy: int, baslik: bool = False, kalinlik: str = "Bold"):
    yol = FONT_BASLIK if baslik else FONT_METIN
    if not Path(yol).exists():
        return ImageFont.load_default()
    f = ImageFont.truetype(str(yol), boy)
    if not baslik:
        try:
            f.set_variation_by_name(kalinlik)
        except Exception:  # noqa: BLE001
            pass
    return f


def sar(metin: str, f, genislik: int) -> list:
    satirlar, sat = [], ""
    for k in metin.split():
        deneme = f"{sat} {k}".strip()
        if sat and f.getlength(deneme) > genislik:
            satirlar.append(sat)
            sat = k
        else:
            sat = deneme
    if sat:
        satirlar.append(sat)
    return satirlar


def yazi_karti(baslik: str, alt: str, hedef: Path, renk_tohum: str = None, w: int = W, h: int = H) -> Path:
    r = renkler()
    im = Image.new("RGB", (w, h), r["arka"])
    d = ImageDraw.Draw(im)
    for i in range(0, w, 80):  # hafif doku
        d.line([(i, 0), (i - h // 3, h)], fill="#111a2e", width=2)
    m = int(w * 0.08)
    y = int(h * 0.30)
    if baslik:
        boy = int(h * 0.12)
        fb = font(boy, baslik=True)
        while boy > 30 and len(sar(baslik.upper(), fb, w - 2 * m)) > 2:
            boy -= 6
            fb = font(boy, baslik=True)
        for s in sar(baslik.upper(), fb, w - 2 * m):
            d.text((m, y), s, font=fb, fill=r["vurgu"])
            y += int(boy * 1.1)
        y += int(h * 0.03)
    if alt:
        fa = font(int(h * 0.045), kalinlik="Medium")
        for s in sar(alt, fa, w - 2 * m)[:5]:
            d.text((m, y), s, font=fa, fill=r["yazi"])
            y += int(h * 0.062)
    hedef = Path(hedef)
    im.save(hedef)
    return hedef


def grafik(spec: dict, hedef: Path) -> Path:
    """spec: {"tip":"bar","baslik":..,"etiketler":[..],"degerler":[..],"birim":"$","vurgu":idx,"kaynak":..}"""
    r = renkler()
    im = Image.new("RGB", (W, H), r["arka"])
    d = ImageDraw.Draw(im)
    m = 140
    d.text((m, 80), spec.get("baslik", ""), font=font(64), fill=r["yazi"])
    et, de = spec["etiketler"], [float(x) for x in spec["degerler"]]
    birim = spec.get("birim", "")
    mx = max(de) or 1
    n = len(et)
    x0, x1, y0, y1 = m, W - m, 240, H - 170
    bw = (x1 - x0) / n
    fe, fd = font(34, kalinlik="Medium"), font(44)
    for i, (e, v) in enumerate(zip(et, de)):
        hgt = (y1 - y0) * v / mx
        renk = r["vurgu"] if spec.get("vurgu") == i else "#4EA8DE"
        bx0, bx1 = x0 + i * bw + bw * 0.18, x0 + (i + 1) * bw - bw * 0.18
        d.rectangle((bx0, y1 - hgt, bx1, y1), fill=renk)
        etiket = f"{birim}{v:,.0f}" if v >= 100 else f"{birim}{v:,.2f}".rstrip("0").rstrip(".")
        d.text(((bx0 + bx1) / 2, y1 - hgt - 14), etiket, font=fd, fill=r["yazi"], anchor="ms")
        for j, s in enumerate(sar(e, fe, int(bw * 0.95))[:2]):
            d.text(((bx0 + bx1) / 2, y1 + 20 + j * 40), s, font=fe, fill=r["gri"], anchor="ma")
    d.line((x0, y1, x1, y1), fill=r["gri"], width=3)
    if spec.get("kaynak"):
        d.text((m, H - 60), f"Source: {spec['kaynak']}", font=font(26, kalinlik="Medium"), fill=r["gri"])
    hedef = Path(hedef)
    im.save(hedef)
    return hedef


# ---------- Maliyet Kulesi ----------
def _para(x: float, birim: str) -> str:
    return f"{birim}{x:,.2f}" if x < 100 else f"{birim}{x:,.0f}"


def _kule_kare(v: dict, ilerleme: float) -> Image.Image:
    r = renkler()
    im = Image.new("RGB", (W, H), r["arka"])
    d = ImageDraw.Draw(im)
    kal, birim = v["kalemler"], v.get("birim", "$")
    toplam = sum(k["tutar"] for k in kal) or 1
    fk, fn = font(36), font(30, kalinlik="Medium")
    d.text((120, 60), v.get("baslik", ""), font=font(62), fill=r["yazi"])
    kx0, kx1, ky0, ky1, lx = 200, 580, 230, 930, 720
    yuk = ky1 - ky0
    d.rectangle((kx0 - 4, ky0 - 4, kx1 + 4, ky1 + 4), outline="#24344D", width=3)
    sinir, y = [], float(ky1)
    for k in kal:
        hh = yuk * k["tutar"] / toplam
        sinir.append((y - hh, y))
        y -= hh
    sira = sorted(range(len(kal)), key=lambda i: sum(sinir[i]) / 2)
    ara = 84
    ys = [sum(sinir[i]) / 2 for i in sira]
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i - 1] + ara)
    if ys and ys[-1] > ky1 - 20:
        ys[-1] = ky1 - 20
        for i in range(len(ys) - 2, -1, -1):
            ys[i] = min(ys[i], ys[i + 1] - ara)
    ey = {i: ys[j] for j, i in enumerate(sira)}
    for i, k in enumerate(kal):
        o = min(max(ilerleme - i, 0), 1)
        if o <= 0:
            break
        y0, y1 = sinir[i]
        renk = k.get("renk") or PALET[i % len(PALET)]
        d.rectangle((kx0, y1 - (y1 - y0) * (1 - (1 - o) ** 3), kx1, y1), fill=renk)
        if o > 0.6:
            orta, ly = (y0 + y1) / 2, ey[i]
            d.line([(kx1 + 8, orta), (650, orta), (670, ly), (lx - 12, ly)], fill=renk, width=3)
            d.text((lx, ly - 2), k["ad"], font=fk, fill=r["yazi"], anchor="ls")
            pay = 100 * k["tutar"] / toplam
            d.text((lx, ly + 4), f"{_para(k['tutar'], birim)}  ·  {pay:.0f}%", font=fn, fill=renk, anchor="lt")
    if ilerleme >= len(kal) + 0.3:
        d.text((kx0, ky0 - 16), f"TOTAL {_para(toplam, birim)}", font=fk, fill=r["vurgu"], anchor="ls")
    if v.get("kaynak"):
        d.text((120, H - 55), f"Source: {v['kaynak']}", font=font(26, kalinlik="Medium"), fill=r["gri"])
    return im


def kule_video(v: dict, hedef: Path, sure_sn: float, fps: int = 30) -> Path:
    """Kalemleri sahne suresine yayarak tek tek yukselten MP4."""
    hedef = Path(hedef)
    n = len(v["kalemler"])
    toplam_kare = max(int(sure_sn * fps), fps)
    animasyon = max(toplam_kare - int(1.5 * fps), n * 10)
    komut = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
             "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(hedef)]
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg yok")
    p = subprocess.Popen(komut, stdin=subprocess.PIPE)
    son = None
    for f in range(toplam_kare):
        ilerleme = min(f / animasyon * (n + 0.5), n + 1)
        if son is None or ilerleme <= n + 0.5:
            son = _kule_kare(v, ilerleme).tobytes()
        p.stdin.write(son)
    p.stdin.close()
    p.wait()
    _kule_kare(v, n + 1).save(hedef.with_suffix(".png"))
    return hedef


def ekran_yazisi(metin: str, hedef: Path, w: int = W, h: int = H, dikey: bool = False) -> Path:
    """Alt ucte yarim saydam bant + yazi (seffaf PNG), videonun ustune bindirilir."""
    r = renkler()
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    boy = int(h * (0.035 if dikey else 0.055))
    f = font(boy)
    satirlar = sar(metin, f, int(w * 0.8))[:2]
    bant_h = int(len(satirlar) * boy * 1.3 + boy * 0.8)
    y0 = int(h * (0.62 if dikey else 0.78))
    genis = max(f.getlength(s) for s in satirlar) + boy * 1.2
    x0 = (w - genis) / 2
    d.rounded_rectangle((x0, y0, x0 + genis, y0 + bant_h), radius=int(boy * 0.4), fill=(11, 18, 32, 215))
    d.rectangle((x0, y0, x0 + 10, y0 + bant_h), fill=r["vurgu"])
    yy = y0 + boy * 0.4
    for s in satirlar:
        d.text((w / 2, yy), s, font=f, fill=r["yazi"], anchor="ma")
        yy += boy * 1.3
    hedef = Path(hedef)
    im.save(hedef)
    return hedef
