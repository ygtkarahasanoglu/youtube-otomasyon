# Colossal Builds — YouTube otomasyonu

Yüzsüz, İngilizce, yapay zekâ ile üretilen bir mega projeler ve mühendislik kanalı (dev yapılar, dev gemiler ve makineler, geleceğin projeleri; denizcilik ağırlıklı) için uçtan uca sistem.
Claude Code içinde çalışan 9 uzman ajan + 19 skill + Python üretim hattı (`hat/`). Her video ayrıca Instagram ve Facebook Reels paylaşım paketiyle gelir.

**Başlamak için:** `BASLA-BURADAN.txt` dosyasını aç. Özetle:

1. `1-KURULUM.bat` → çift tıkla (bir kez)
2. `2-KANAL-YONETICISI.bat` → çift tıkla, `/kurulum` yaz
3. Sonra her video için `3-YENI-VIDEO.bat` (veya Claude içinde `/video`)

Video hazır olunca YouTube'a **özel** olarak yüklenir; sen izleyip YouTube Studio'da yayınlarsın.

## Ne yapar
| Adım | Araç |
| --- | --- |
| Konu seçimi, rakip analizi | YouTube otomatik tamamlama, kanal outlier taraması |
| Senaryo (21 hook formülü) | Claude → `senaryo.json` |
| Seslendirme | Kokoro (ücretsiz, ticari kullanım serbest); para kazanınca ElevenLabs |
| Görseller | Pixabay + Coverr stok video, Openverse (Wikimedia/Flickr) ve NASA arşiv fotoğrafları, fal.ai yapay zekâ görsel ve video, kendi grafiklerimiz |
| Kurgu | ffmpeg: 1080p, müzik, ses seviyesi -14 LUFS, altyazı, bölümler |
| Thumbnail | 3 varyant (YouTube "Test & Compare" için) |
| Shorts | Her videodan 2 dikey Shorts, yanan altyazılı |
| Yükleme | YouTube Data API, her zaman ÖZEL |
| Instagram + Facebook | Her videodan 3 Reels: klip, İngilizce açıklama, kapak, takvim (`videolar/<video>/dagitim/`); sen Meta Business Suite'te planlarsın |

## Maliyet (tahmini, ayda 8 video)
Test dönemi (ilk 90 gün): **0 $** (Kokoro ses + ücretsiz stok). Sonra: ElevenLabs 5-22 $ + fal.ai 10-20 $ kredi. Limitler `ayarlar.json` → `butce`.

## Güvenlik
API anahtarları yalnızca `.env` dosyasında durur; `.gitignore` sayesinde GitHub'a gönderilmez.
YouTube giriş dosyaları (`kanal/youtube_*.json`) da gönderilmez.

## Klasörler
- `hat/` — üretim hattı kodu (`python -m hat kontrol | yeni | uret | yukle | dagitim | maliyet`)
- `.claude/agents/` — 9 uzman ajan, `.claude/skills/` — skill'ler ve komutlar
- `kanal/` — kanal kimliği, fontlar, müzik, senaryo şablonu, öğrenme kaydı
- `arastirma/` — niş değerlendirmesi ve video fikir havuzu
- `videolar/` — üretilen her video kendi klasöründe (GitHub'a gönderilmez)
