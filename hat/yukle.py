"""YouTube'a yukleme (her zaman OZEL / private). Yayina alma karari kullanicida.

Kurulum (bir kez): Google Cloud'da OAuth istemcisi (Masaustu uygulamasi) olustur,
JSON dosyasini kanal/youtube_client_secret.json olarak kaydet, sonra:
    python -m hat youtube-giris
Tarayici acilir, kanal hesabinla izin verirsin; kanal/youtube_token.json olusur.
"""
from pathlib import Path

from .ayar import KOK, json_oku, json_yaz, log

KAPSAM = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
SIR = KOK / "kanal" / "youtube_client_secret.json"
TOKEN = KOK / "kanal" / "youtube_token.json"


def _kutuphane():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        return Request, Credentials, InstalledAppFlow, build, MediaFileUpload
    except ImportError:
        raise SystemExit("Google kutuphaneleri yok: pip install -U google-api-python-client google-auth-oauthlib")


def giris(yeniden: bool = False):
    Request, Credentials, InstalledAppFlow, build, _ = _kutuphane()
    kimlik = None
    if TOKEN.exists() and not yeniden:
        kimlik = Credentials.from_authorized_user_file(str(TOKEN), KAPSAM)
    if kimlik and kimlik.expired and kimlik.refresh_token:
        try:
            kimlik.refresh(Request())
        except Exception:  # noqa: BLE001  test modundaki uygulamalarda token 7 gunde dolar
            kimlik = None
    if not kimlik or not kimlik.valid:
        if not SIR.exists():
            raise SystemExit(f"{SIR} yok. Google Cloud'dan OAuth istemci JSON'unu indirip bu adla kaydet (/kurulum anlatir).")
        akis = InstalledAppFlow.from_client_secrets_file(str(SIR), KAPSAM)
        kimlik = akis.run_local_server(port=0, prompt="consent", access_type="offline")
        TOKEN.write_text(kimlik.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=kimlik, cache_discovery=False)


def aciklama_olustur(klasor: Path, senaryo: dict) -> str:
    parcalar = [senaryo.get("aciklama", "").strip()]
    bolum = (klasor / "bolumler.txt")
    if bolum.exists() and json_oku(klasor / "zaman_cizelgesi.json", {}).get("bolumler_gecerli"):
        parcalar.append("Chapters:\n" + bolum.read_text(encoding="utf-8").strip())
    if senaryo.get("kaynaklar"):
        parcalar.append("Sources:\n" + "\n".join(f"- {k.get('ad', '')}: {k.get('url', '')}" for k in senaryo["kaynaklar"]))
    lis = klasor / "lisanslar.txt"
    if lis.exists():
        parcalar.append(lis.read_text(encoding="utf-8").strip())
    if senaryo.get("hashtagler"):
        parcalar.append(" ".join(senaryo["hashtagler"][:3]))
    metin = "\n\n".join(p for p in parcalar if p)
    return metin[:4900]


def yukle(klasor: Path, senaryo: dict, ayar: dict, shorts_dahil: bool = True) -> dict:
    klasor = Path(klasor)
    _, _, _, _, MediaFileUpload = _kutuphane()
    yt = giris()
    kayit = json_oku(klasor / "yukleme.json", {})
    yap = ayar.get("youtube", {})

    def bir_video(dosya: Path, baslik: str, aciklama: str, anahtar: str, thumb: Path = None, srt: Path = None):
        if kayit.get(anahtar):
            log(f"  zaten yuklendi: {anahtar} -> https://youtu.be/{kayit[anahtar]}")
            return kayit[anahtar]
        govde = {
            "snippet": {"title": baslik[:100], "description": aciklama, "tags": senaryo.get("etiketler", [])[:15],
                        "categoryId": str(yap.get("kategori", "27")), "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": bool(senaryo.get("yapay_icerik_beyani", False))},
        }
        log(f"  yukleniyor: {dosya.name} ...")
        istek = yt.videos().insert(part="snippet,status", body=govde, media_body=MediaFileUpload(str(dosya), chunksize=-1, resumable=True))
        yanit = None
        while yanit is None:
            durum, yanit = istek.next_chunk()
            if durum:
                log(f"    %{int(durum.progress() * 100)}")
        vid = yanit["id"]
        kayit[anahtar] = vid
        json_yaz(klasor / "yukleme.json", kayit)
        if thumb and thumb.exists():
            try:
                yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb))).execute()
            except Exception as e:  # noqa: BLE001
                log(f"    thumbnail ayarlanamadi (telefon dogrulamasi gerekebilir): {e}")
        if srt and srt.exists():
            try:
                yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "en", "name": "English"}},
                                     media_body=MediaFileUpload(str(srt))).execute()
            except Exception as e:  # noqa: BLE001
                log(f"    altyazi yuklenemedi: {e}")
        log(f"    tamam (OZEL): https://youtu.be/{vid}")
        return vid

    bir_video(klasor / "son.mp4", senaryo["baslik"], aciklama_olustur(klasor, senaryo), "uzun",
              klasor / "thumbnail-a.jpg", klasor / "altyazi.srt")
    if shorts_dahil:
        for i, s in enumerate(senaryo.get("shorts") or [], 1):
            if s.get("youtube", True) is False:
                continue  # yalnizca Instagram/Facebook Reels icin uretilmis klip
            dosya = klasor / "shorts" / f"short-{i}.mp4"
            if dosya.exists():
                uzun = kayit.get("uzun")
                ac = (s.get("aciklama") or senaryo.get("aciklama", "")[:300]) + (f"\n\nFull video: https://youtu.be/{uzun}" if uzun else "")
                bir_video(dosya, s.get("baslik", senaryo["baslik"])[:95], ac + "\n#shorts", f"short-{i}")
    return kayit
