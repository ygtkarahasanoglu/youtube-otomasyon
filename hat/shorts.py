"""Shorts: uzun videonun 'shorts' isaretli sahnelerinden dikey (1080x1920) video, kelime kelime altyazili.

senaryo.json -> "shorts": [{"baslik": "...", "sahneler": ["s03","s04","s05"], "kanca": "opsiyonel ilk ekran yazisi"}]
Her Shorts, ayni seslendirme ve gorselleri yeniden kullanir (ek maliyet yok).
"""
from pathlib import Path

from . import grafik
from .ayar import FONT_BASLIK, ffmpeg, log

W, H, FPS = 1080, 1920, 30
VIDEO_UZANTI = {".mp4", ".mov", ".webm", ".mkv"}


def _ass_zaman(t: float) -> str:
    cs = int(round(t * 100))
    s, cs = divmod(cs, 100)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _ass(kelimeler: list, hedef: Path, renk_vurgu="&H0003B7FF") -> Path:
    """2-3 kelimelik buyuk, ortada altyazi parcalari (ASS)."""
    bas = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
           "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           f"Style: K,Anton,110,&H00FFFFFF,{renk_vurgu},&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,7,2,5,60,60,0,1\n\n"
           "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    olaylar, grup = [], []
    for k in kelimeler:
        grup.append(k)
        if len(grup) == 3 or k["kelime"][-1:] in ".,?!":
            olaylar.append(grup)
            grup = []
    if grup:
        olaylar.append(grup)
    satirlar = []
    for g in olaylar:
        metin = " ".join(x["kelime"] for x in g).upper().replace("{", "(").replace("}", ")")
        satirlar.append(f"Dialogue: 0,{_ass_zaman(g[0]['bas'])},{_ass_zaman(g[-1]['bit'] + 0.05)},K,,0,0,0,,{{\\pos(540,1180)}}{metin}")
    hedef.write_text(bas + "\n".join(satirlar) + "\n", encoding="utf-8")
    return hedef


def uret(klasor: Path, senaryo: dict, ayar: dict, sesler: dict, gorseller: dict) -> list:
    klasor = Path(klasor).resolve()
    tanimlar = senaryo.get("shorts") or []
    if not tanimlar:
        log("  shorts tanimi yok, atlandi")
        return []
    sdir = klasor / "shorts"
    tmp = sdir / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    import shutil
    if FONT_BASLIK.exists():
        shutil.copy(FONT_BASLIK, tmp / FONT_BASLIK.name)  # altyazi fontu ffmpeg'in calisma klasorunde
    cikti = []
    for n, tanim in enumerate(tanimlar, 1):
        kliper, wavlar, kelimeler, t = [], [], [], 0.0
        for sid in tanim["sahneler"]:
            dur = sesler[sid]["sure"] + 0.1
            src = Path(gorseller[sid]["dosya"])
            klip = tmp / f"{n}_{sid}.mp4"
            if src.suffix.lower() in VIDEO_UZANTI:
                gir = ["-stream_loop", "-1", "-i", src]
            else:
                gir = ["-loop", "1", "-framerate", FPS, "-i", src]
            # tum kare ortada, ust/alt ayni goruntunun bulanik hali (infografik kirpilmasin)
            vf = (f"[0:v]split=2[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,"
                  f"eq=brightness=-0.2[bg];[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-180,fps={FPS},setsar=1[v]")
            ffmpeg(*gir, "-filter_complex", vf, "-map", "[v]", "-t", f"{dur:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast",
                   "-crf", "21", "-pix_fmt", "yuv420p", "-r", FPS, klip)
            wav = tmp / f"{n}_{sid}.wav"
            ffmpeg("-i", klasor / "ses" / f"{sid}.mp3", "-af", "apad=pad_dur=0.1", "-ar", 44100, "-ac", 2, "-t", f"{dur:.3f}", wav)
            kliper.append(klip)
            wavlar.append(wav)
            kelimeler += [{**k, "bas": k["bas"] + t, "bit": k["bit"] + t} for k in sesler[sid]["kelimeler"]]
            t += dur
        if t > 60:
            log(f"  UYARI shorts {n}: {t:.0f} sn (60 sn ustu Shorts olarak sayilmayabilir)")
        for ad, liste in (("v", kliper), ("a", wavlar)):
            (tmp / f"{n}_{ad}.txt").write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in liste), encoding="utf-8")
        ffmpeg("-f", "concat", "-safe", 0, "-i", tmp / f"{n}_v.txt", "-c", "copy", tmp / f"{n}_v.mp4")
        ffmpeg("-f", "concat", "-safe", 0, "-i", tmp / f"{n}_a.txt", "-c", "copy", tmp / f"{n}_a.wav")
        ass = _ass(kelimeler, tmp / f"{n}.ass")
        ust = None
        if tanim.get("kanca"):
            ust = grafik.ekran_yazisi(tanim["kanca"], tmp / f"{n}_kanca.png", W, H, dikey=True)
        hedef = (sdir / f"short-{n}.mp4").resolve()
        filtre = f"subtitles={ass.name}:fontsdir=."  # calisma klasoru tmp; surucu harfi kacis sorunu yok
        if ust:
            _yaz_ust(tmp, n, ust, filtre, hedef)
        else:
            _yaz(tmp, n, filtre, hedef)
        cikti.append({"dosya": str(hedef), "baslik": tanim.get("baslik", ""), "sure": round(t, 1)})
        log(f"  short-{n}: {t:.0f} sn")
    shutil.rmtree(tmp, ignore_errors=True)
    return cikti


def _yaz(tmp: Path, n: int, filtre: str, hedef: Path) -> None:
    import os
    eski = os.getcwd()
    os.chdir(tmp)  # ASS dosya yolu goreli kalsin (Windows surucu harfi kacis sorunu olmasin)
    try:
        ffmpeg("-i", f"{n}_v.mp4", "-i", f"{n}_a.wav", "-vf", filtre, "-af", "loudnorm=I=-14:TP=-1.5",
               "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
               "-movflags", "+faststart", hedef.resolve())
    finally:
        os.chdir(eski)


def _yaz_ust(tmp: Path, n: int, ust: Path, filtre: str, hedef: Path) -> None:
    import os
    eski = os.getcwd()
    os.chdir(tmp)
    try:
        ffmpeg("-i", f"{n}_v.mp4", "-i", f"{n}_a.wav", "-i", ust.name, "-filter_complex",
               f"[0:v][2:v]overlay=0:0:enable='lt(t,2.5)',{filtre}[v]", "-map", "[v]", "-map", "1:a",
               "-af", "loudnorm=I=-14:TP=-1.5", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
               "-b:a", "160k", "-shortest", "-movflags", "+faststart", hedef.resolve())
    finally:
        os.chdir(eski)
