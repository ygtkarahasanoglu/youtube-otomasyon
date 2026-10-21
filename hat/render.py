"""Videoyu birlestirir: sahne klipleri + seslendirme + muzik -> son.mp4, altyazi.srt, bolumler.txt, onizleme.jpg"""
import random
import re
from pathlib import Path

from PIL import Image, ImageDraw

from . import grafik
from .ayar import KOK, ffmpeg, json_yaz, log, sure

W, H, FPS = 1920, 1080, 30
VIDEO_UZANTI = {".mp4", ".mov", ".webm", ".mkv"}


def _sahne_klibi(kaynak: Path, hedef: Path, dur: float, sira: int, ekran: Path = None, sabit: bool = False, w=W, h=H) -> None:
    kaynak = Path(kaynak)
    girdiler, vf = [], ""
    if kaynak.suffix.lower() in VIDEO_UZANTI:
        girdiler = ["-stream_loop", "-1", "-i", kaynak]
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS},setsar=1"
    elif sabit:  # grafik/yazi karti: sahte kamera hareketi yok, duragan ve net kalsin
        girdiler = ["-loop", "1", "-framerate", str(FPS), "-i", kaynak]
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS},setsar=1"
    else:
        girdiler = ["-loop", "1", "-framerate", str(FPS), "-i", kaynak]
        kare = max(int(dur * FPS), 1)
        buyut = 4  # genis on-olcekleme: ffmpeg zoompan'in piksel yuvarlama kaynakli titremesini onler
        if sira % 2 == 0:  # yavas yakinlasma
            vf = (f"scale={int(w * buyut)}:{int(h * buyut)}:force_original_aspect_ratio=increase,crop={int(w * buyut)}:{int(h * buyut)},"
                  f"zoompan=z='1+0.10*on/{kare}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}:fps={FPS},setsar=1")
        else:  # yatay kaydirma (yon sahneye gore degisir)
            yon = "(iw-ow)*t/{d}" if sira % 4 == 1 else "(iw-ow)*(1-t/{d})"
            vf = (f"scale={int(w * 2.2)}:{int(h * 2.2)}:force_original_aspect_ratio=increase,"
                  f"crop={w}:{h}:x='{yon.format(d=max(dur, 0.1))}':y='(ih-oh)/2',fps={FPS},setsar=1")
    if ekran:
        girdiler += ["-i", ekran]
        filtre = f"[0:v]{vf}[v];[v][1:v]overlay=0:0:enable='gte(t,0.35)'[o]"
        cikis = ["-filter_complex", filtre, "-map", "[o]"]
    else:
        cikis = ["-vf", vf]
    ffmpeg(*girdiler, *cikis, "-t", f"{dur:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
           "-pix_fmt", "yuv420p", "-r", FPS, hedef)


def _cumleler(metin: str) -> list:
    parcalar = re.findall(r"[^.!?]+[.!?]+[\"'’”]*|[^.!?]+$", metin.strip())
    return [p.strip() for p in parcalar if p.strip()]


def _sar_coklu(metin: str, max_kr: int = 42) -> str:
    satirlar, sat = [], ""
    for k in metin.split():
        deneme = f"{sat} {k}".strip()
        if sat and len(deneme) > max_kr:
            satirlar.append(sat)
            sat = k
        else:
            sat = deneme
    if sat:
        satirlar.append(sat)
    return "\n".join(satirlar)


def cift_dil_altyazi(klasor: Path, senaryo: dict, cizelge: list) -> bool:
    """sahnede 'metin_tr' varsa cumle bazli EN+TR SRT uretir (ikisi de ayni zamanlamayi paylasir). Yoksa False doner."""
    sahne_map = {s["id"]: s for s in senaryo["sahneler"]}
    if not any(sahne_map[c["id"]].get("metin_tr") for c in cizelge):
        return False
    en_srt, tr_srt, n = [], [], 1
    for c in cizelge:
        s = sahne_map[c["id"]]
        en_cumleler = _cumleler(s.get("metin", ""))
        tr_cumleler = _cumleler(s.get("metin_tr", "")) if s.get("metin_tr") else []
        if not en_cumleler or len(tr_cumleler) != len(en_cumleler):
            en_cumleler = [s.get("metin", "")]
            tr_cumleler = [s.get("metin_tr") or s.get("metin", "")]
        toplam_kr = sum(len(x) for x in en_cumleler) or 1
        t, bit = c["bas"], c["bit"]
        for en, tr in zip(en_cumleler, tr_cumleler):
            pay = len(en) / toplam_kr
            d = max((bit - c["bas"]) * pay, 0.8)
            a, b = t, min(t + d, bit)
            en_srt.append(f"{n}\n{_srt_zaman(a)} --> {_srt_zaman(b)}\n{_sar_coklu(en)}\n")
            tr_srt.append(f"{n}\n{_srt_zaman(a)} --> {_srt_zaman(b)}\n{_sar_coklu(tr)}\n")
            n += 1
            t = b
    (klasor / "altyazi-en.srt").write_text("\n".join(en_srt), encoding="utf-8")
    (klasor / "altyazi-tr.srt").write_text("\n".join(tr_srt), encoding="utf-8")
    return True


def _srt_zaman(t: float) -> str:
    ms = int(round(t * 1000))
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def altyazi_satirlari(kelimeler: list, max_kr: int = 42, max_sn: float = 3.2) -> list:
    satirlar, sat = [], []
    for k in kelimeler:
        if sat:
            metin = " ".join(x["kelime"] for x in sat + [k])
            if len(metin) > max_kr or k["bit"] - sat[0]["bas"] > max_sn:
                satirlar.append(sat)
                sat = []
        sat.append(k)
        if k["kelime"][-1:] in ".?!" and len(sat) >= 3:
            satirlar.append(sat)
            sat = []
    if sat:
        satirlar.append(sat)
    return [(s[0]["bas"], s[-1]["bit"], " ".join(x["kelime"] for x in s)) for s in satirlar]


def uret(klasor: Path, senaryo: dict, ayar: dict, sesler: dict, gorseller: dict) -> Path:
    klasor = Path(klasor)
    tmp = klasor / "_render"
    tmp.mkdir(exist_ok=True)
    bosluk = float(ayar["video"].get("sahne_arasi_sn", 0.25))
    cizelge, t = [], 0.0
    vlist, alist = [], []
    for i, s in enumerate(senaryo["sahneler"]):
        sid = s["id"]
        ses_sure = sesler[sid]["sure"]
        dur = ses_sure + bosluk
        log(f"  render {sid} ({dur:.1f} sn)")
        wav = tmp / f"{sid}.wav"
        ffmpeg("-i", klasor / "ses" / f"{sid}.mp3", "-af", f"apad=pad_dur={bosluk}", "-ar", 44100, "-ac", 2, "-t", f"{dur:.3f}", wav)
        ekran = None
        if s.get("ekran_yazisi"):
            ekran = grafik.ekran_yazisi(s["ekran_yazisi"], tmp / f"{sid}_yazi.png")
        klip = tmp / f"{sid}.mp4"
        sabit = s.get("gorsel", {}).get("tur") in ("yazi", "grafik")
        _sahne_klibi(Path(gorseller[sid]["dosya"]), klip, dur, i, ekran, sabit)
        vlist.append(klip)
        alist.append(wav)
        cizelge.append({"id": sid, "bas": round(t, 3), "bit": round(t + dur, 3), "bolum": s.get("bolum")})
        t += dur

    def liste(dosyalar, ad):
        yol = tmp / ad
        yol.write_text("".join(f"file '{Path(d).resolve().as_posix()}'\n" for d in dosyalar), encoding="utf-8")
        return yol

    ffmpeg("-f", "concat", "-safe", 0, "-i", liste(vlist, "v.txt"), "-c", "copy", tmp / "video.mp4")
    ffmpeg("-f", "concat", "-safe", 0, "-i", liste(alist, "a.txt"), "-c", "copy", tmp / "anlatim.wav")

    muzikler = [p for p in (KOK / "kanal" / "muzik").glob("*") if p.suffix.lower() in (".mp3", ".m4a", ".wav", ".ogg")]
    son = klasor / "son.mp4"
    ses_ayar = ayar["video"]
    loud = f"loudnorm=I={ses_ayar.get('lufs', -14)}:TP=-1.5:LRA=11"
    if muzikler:
        muzik = random.choice(muzikler)
        log(f"  muzik: {muzik.name}")
        filtre = (f"[1:a]asplit=2[n1][n2];[2:a]volume={ses_ayar.get('muzik_seviye', 0.22)},aformat=channel_layouts=stereo[m];"
                  f"[m][n1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=500[d];"
                  f"[n2][d]amix=inputs=2:duration=first:normalize=0,{loud}[a]")
        ffmpeg("-i", tmp / "video.mp4", "-i", tmp / "anlatim.wav", "-stream_loop", "-1", "-i", muzik,
               "-filter_complex", filtre, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
               "-shortest", "-movflags", "+faststart", son)
    else:
        log("  muzik yok (kanal/muzik klasorune telifsiz muzik koyabilirsin)")
        ffmpeg("-i", tmp / "video.mp4", "-i", tmp / "anlatim.wav", "-map", "0:v", "-map", "1:a", "-af", loud,
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", son)

    # altyazi (kelime zamanlarindan, Whisper gerekmez)
    srt, n = [], 1
    for c in cizelge:
        for a, b, m in altyazi_satirlari(sesler[c["id"]]["kelimeler"]):
            srt.append(f"{n}\n{_srt_zaman(c['bas'] + a)} --> {_srt_zaman(c['bas'] + b)}\n{m}\n")
            n += 1
    (klasor / "altyazi.srt").write_text("\n".join(srt), encoding="utf-8")

    if cift_dil_altyazi(klasor, senaryo, cizelge):
        gomulu = tmp / "son_altyazili.mp4"
        ffmpeg("-i", son, "-i", klasor / "altyazi-en.srt", "-i", klasor / "altyazi-tr.srt",
               "-map", "0:v", "-map", "0:a", "-map", "1", "-map", "2",
               "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
               "-metadata:s:s:0", "language=eng", "-metadata:s:s:0", "title=English",
               "-metadata:s:s:1", "language=tur", "-metadata:s:s:1", "title=Turkce",
               "-disposition:s:0", "default", "-disposition:s:1", "0",
               "-movflags", "+faststart", gomulu)
        gomulu.replace(son)
        log("  altyazi: EN + TR gomuldu (oynaticida secilebilir)")

    # bolumler (chapters): ardisik ayni-bolum sahnelerini tek bir baslangic noktasina indir
    bolumler = []
    for c in cizelge:
        b = c.get("bolum")
        if b and (not bolumler or bolumler[-1][1] != b):
            bolumler.append((c["bas"], b))
    if bolumler and bolumler[0][0] > 0:
        bolumler[0] = (0.0, bolumler[0][1])
    satir = [f"{int(b // 60):02d}:{int(b % 60):02d} {ad}" for b, ad in bolumler]
    gecerli = len(bolumler) >= 3 and all(y - x >= 10 for (x, _), (y, _) in zip(bolumler, bolumler[1:] + [(t, "")]))
    (klasor / "bolumler.txt").write_text("\n".join(satir) + "\n", encoding="utf-8")
    json_yaz(klasor / "zaman_cizelgesi.json", {"sure": round(t, 2), "sahneler": cizelge, "bolumler_gecerli": gecerli})
    if not gecerli:
        log("  UYARI: bolumler YouTube kuralina uymuyor (en az 3, her biri 10+ sn, ilki 00:00)")

    onizleme(son, cizelge, klasor / "onizleme.jpg")
    log(f"  video tamam: {son} ({t / 60:.1f} dk)")
    return son


def onizleme(video: Path, cizelge: list, hedef: Path, sutun: int = 4) -> Path:
    """Her sahnenin ortasindan bir kare: kalite kontrolu icin tek gorsel."""
    tmp = Path(hedef).parent / "_render"
    kareler = []
    for c in cizelge:
        k = tmp / f"kare_{c['id']}.jpg"
        ffmpeg("-ss", f"{(c['bas'] + c['bit']) / 2:.2f}", "-i", video, "-frames:v", "1", "-vf", "scale=480:-2", k)
        kareler.append((c["id"], k))
    satir = (len(kareler) + sutun - 1) // sutun
    im = Image.new("RGB", (480 * sutun, 300 * satir), "#000")
    d = ImageDraw.Draw(im)
    for i, (sid, k) in enumerate(kareler):
        x, y = (i % sutun) * 480, (i // sutun) * 300
        im.paste(Image.open(k), (x, y))
        d.rectangle((x, y + 270, x + 480, y + 300), fill="#000")
        d.text((x + 8, y + 276), sid, fill="#FFB703", font=grafik.font(20))
    im.save(hedef, quality=85)
    return hedef
