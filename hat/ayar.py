"""Ortak ayarlar ve yardimcilar."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
FONT_BASLIK = KOK / "kanal" / "fontlar" / "Anton-Regular.ttf"
FONT_METIN = KOK / "kanal" / "fontlar" / "Montserrat-VF.ttf"

try:
    from dotenv import load_dotenv
    load_dotenv(KOK / ".env")
except ImportError:  # dotenv yoksa ortam degiskenleri yine okunur
    pass


def ayarlar() -> dict:
    yol = KOK / "ayarlar.json"
    if not yol.exists():
        sys.exit("ayarlar.json bulunamadi.")
    return json.loads(yol.read_text(encoding="utf-8"))


def anahtar(ad: str, zorunlu: bool = True) -> str:
    v = os.environ.get(ad, "").strip()
    if zorunlu and not v:
        sys.exit(f"{ad} tanimli degil. .env dosyasina ekle (Claude Code'da /kurulum komutu yardim eder).")
    return v


def log(mesaj: str) -> None:
    print(mesaj, flush=True)


def ffmpeg_var() -> bool:
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def ffmpeg(*argumanlar, sessiz: bool = True) -> None:
    if not ffmpeg_var():
        sys.exit("ffmpeg bulunamadi. Kur: winget install Gyan.FFmpeg (sonra terminali yeniden ac)")
    komut = ["ffmpeg", "-y", "-hide_banner"] + (["-loglevel", "error"] if sessiz else []) + [str(a) for a in argumanlar]
    r = subprocess.run(komut, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if r.returncode != 0:
        raise RuntimeError("ffmpeg hatasi:\n" + " ".join(komut[:12]) + " ...\n" + r.stderr[-2000:])


def sure(dosya) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(dosya)],
                       capture_output=True, text=True, encoding="utf-8", errors="ignore")
    try:
        return float(r.stdout.strip())
    except ValueError:
        raise RuntimeError(f"Sure okunamadi: {dosya}\n{r.stderr[-500:]}")


def json_oku(yol: Path, varsayilan=None):
    yol = Path(yol)
    if not yol.exists():
        return varsayilan
    return json.loads(yol.read_text(encoding="utf-8"))


def json_yaz(yol: Path, veri) -> None:
    yol = Path(yol)
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps(veri, ensure_ascii=False, indent=1), encoding="utf-8")


def maliyet_ekle(klasor: Path, kalem: str, dolar: float, not_: str = "") -> None:
    """Tahmini harcamayi videonun maliyet.json dosyasina ekler."""
    yol = Path(klasor) / "maliyet.json"
    v = json_oku(yol, {"kalemler": [], "toplam_usd": 0.0})
    v["kalemler"].append({"kalem": kalem, "usd": round(dolar, 4), "not": not_})
    v["toplam_usd"] = round(sum(k["usd"] for k in v["kalemler"]), 3)
    json_yaz(yol, v)


def senaryo_oku(klasor: Path) -> dict:
    s = json_oku(Path(klasor) / "senaryo.json")
    if not s:
        sys.exit(f"{klasor}/senaryo.json yok. Once senaryoyu yazdir (/video komutu).")
    if not s.get("sahneler"):
        sys.exit("senaryo.json icinde 'sahneler' bos.")
    return s
