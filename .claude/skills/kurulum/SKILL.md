---
name: kurulum
description: İlk kurulum sihirbazı; kullanıcıyı (Türkçe, adım adım) Pixabay, Coverr, ücretsiz Kokoro sesi ve YouTube (Google Cloud OAuth) hesaplarından anahtar almaya yönlendirir, .env dosyasını kendisi yazar, sesi seçtirir, müziği kurdurur ve bir deneme videosu üretir.
disable-model-invocation: true
---

# /kurulum

Kullanıcıyla Türkçe konuş. **Her seferinde tek adım** ver, "tamam" deyince sonrakine geç. Anahtarları kullanıcı sohbete yapıştırır; sen `.env` dosyasına yazarsın (dosya yoksa `.env.ornek`'ten oluştur). Anahtarları başka yere yazma, ekrana tekrar basma.

Önce `python -m hat kontrol` çalıştır ve neyin eksik olduğunu gör. Eksik olmayan adımları atla.

## 1. Pixabay (ücretsiz stok video + fotoğraf, ANA kaynak) — 2 dk
1. https://pixabay.com/api/docs/ adresine git → sağ üstten **Giriş yap / Kayıt ol** (Google ile olur).
2. Giriş yaptıktan sonra aynı sayfayı yenile → "Parameters" bölümünde **key** satırında yeşil kutuda anahtar yazar (`12345678-abc...`).
3. Anahtarı buraya yapıştır. → `PIXABAY_API_KEY`

## 2. Coverr (ek ücretsiz stok video) — 3 dk
1. https://coverr.co → **Sign up** (Google ile olur).
2. https://coverr.co/developers (veya profil → **API**) → **Create application** → ad: `behind-the-margin`, açıklama: "Personal YouTube channel video production" → anahtar hemen görünür.
3. Anahtarı yapıştır. → `COVERR_API_KEY`
   (Ücretsiz "Demo" seviyesi saatte 50 arama verir; yeterli. Kotaya takılırsa hat Pixabay'e geçer.)

**Pexels:** Pexels şu an yeni API anahtarı vermiyor ("New API key issuance is currently paused"). Kullanıcı daha önce aldıysa `PEXELS_API_KEY` olarak eklenir, yoksa bu adımı atla. Openverse ve NASA arşivleri anahtarsız çalışır, kurulum gerekmez.

## 3. Anlatıcı sesi: Kokoro (ücretsiz, test dönemi) — 5 dk
Kurulum paketi Kokoro'yu yükler (ücretsiz, bilgisayarda çalışır, Apache 2.0, ticari kullanım serbest). `.env`'de anahtar gerekmez.
1. `python -m hat kontrol --canli` çalıştır → ilk seferde model iner (~330 MB) ve `kokoro_deneme.mp3` oluşur. Kullanıcıya dinlet: `start kokoro_deneme.mp3`.
2. Beğenmezse `ayarlar.json` → `ses.kokoro_ses` değerini değiştirip tekrar dinlet. Erkek anlatıcı adayları: `am_michael` (varsayılan), `am_fenrir`, `am_puck`, `am_onyx`; İngiliz aksanı için `kokoro_dil: "b"` + `bm_george` / `bm_fable`. Hız: `kokoro_hiz` (0.9-1.1).
3. Kokoro hata verirse (ör. kullanıcı klasör yolundaki Türkçe karakter), `python -m pip install -U kokoro soundfile` dene; olmazsa projeyi `C:\kanal` gibi bir yere taşımayı öner. Geçici çözüm `--ses edge` yalnızca deneme içindir (Microsoft ticari lisans vermiyor), yayınlanacak videoda kullanma.

**ElevenLabs ve fal.ai bu aşamada YOK.** Kullanıcı ücretli üyelik istemiyor; 90 günlük test ölçütleri tutunca (ayrıntı: Claude Docs'taki "YouTube Kanal Kararı" belgesi) önerilir: ElevenLabs Starter (5 $/ay, ticari hak dahil) → `ses.saglayici: "elevenlabs"`; fal.ai (10-20 $ kredi) → `FAL_KEY`. O zamana kadar `ai_gorsel`/`ai_video` sahneleri otomatik olarak stok görsele düşer.

## 5. Arka plan müziği (ücretsiz) — 5 dk
YouTube Studio → sol menü **Ses Kütüphanesi (Audio Library)** → filtre: Tür "Cinematic" veya "Ambient", Ruh hali "Calm", **Atıf gerekmez** → 6-10 parça indir → `kanal\muzik\` klasörüne koy (Dosya Gezgini'nde aç: `explorer kanal\muzik`).

## 6. YouTube bağlantısı (Google Cloud) — 15 dk, ücretsiz
Önce kanal: YouTube'da **Colossal Builds** adıyla kanal (tercihen marka hesabı) açılmış olmalı; tutamak `@colossalbuilds` (doluysa kimlikteki yedekler). Telefon doğrulaması: Studio → Ayarlar → Kanal → Özellik uygunluğu.
1. https://console.cloud.google.com → üstte proje seç → **Yeni Proje** → ad: `youtube-otomasyon` → Oluştur.
2. Sol menü **API'ler ve Hizmetler → Kitaplık** → "YouTube Data API v3" → **Etkinleştir**.
3. **Google Auth Platform / OAuth izin ekranı** → Başlayın → Uygulama adı `youtube-otomasyon`, destek e-postası kendi Gmail'in → Kitle: **Harici (External)** → iletişim e-postası → Oluştur.
4. **Kitle (Audience)** sekmesi → "Test kullanıcıları"na kanalın bağlı olduğu Gmail'i ekle. Ardından **Uygulamayı yayınla (Publish app)** → "Üretimde". (Test modunda giriş 7 günde bir düşer; yayınlamak bunu önler. Google doğrulaması gerekmez, giriş ekranında "doğrulanmamış uygulama" uyarısı çıkar: Gelişmiş → Devam et.)
5. **İstemciler (Clients)** → İstemci oluştur → Uygulama türü **Masaüstü uygulaması** → Oluştur → **JSON'u indir**.
6. İnen dosyayı `kanal\youtube_client_secret.json` adıyla proje klasörüne koy (kullanıcı yapamazsa İndirilenler'den sen kopyala).
7. Çalıştır: `python -m hat youtube-giris` → tarayıcı açılır → kanal hesabını (ve marka kanalını) seç → izin ver.

## 7. Son kontrol ve deneme videosu
1. `python -m hat kontrol --canli` → hepsi TAMAM olmalı.
2. Kısa bir deneme: `arastirma/video-havuzu.md`'den en kolay konuyla **3 dakikalık** bir deneme senaryosu yaz (12-15 sahne), `python -m hat uret` ile üret, `onizleme.jpg`'ye bak, kullanıcıya `son.mp4` dosyasının yerini söyle ("Dosya Gezgini'nde aç: explorer videolar\\...").
3. Kullanıcı beğenirse `/video` ile gerçek ilk videoya geç. Beğenmediği şeyi (ses, renk, tempo) sor ve `ayarlar.json`/`.env`'de düzelt.

## 8. Instagram + Facebook (isteğe bağlı, 10 dk)
Kullanıcı isterse şimdi, istemezse ilk `/dagitim` sırasında: `reels-paketi` skill'indeki "First time only" adımlarını (Facebook Sayfası, Instagram profesyonel hesap, Meta Business Suite bağlantısı, biyografi linki) tek tek yaptır, sonra `ayarlar.json → dagitim.kurulum_tamam: true`. API anahtarı gerekmez; paylaşımı kullanıcı Meta Business Suite'te planlar.
