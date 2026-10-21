---
name: video
description: Tek komutla bir İngilizce video üretir; konu seçimi, araştırma, senaryo, paket, iki aşamalı kalite denetimi, ses/görsel/video/thumbnail/Shorts üretimi ve YouTube'a ÖZEL yükleme. Kullanıcıya yalnızca konu onayı ve son izleme kalır.
argument-hint: "[konu (isteğe bağlı)]"
disable-model-invocation: true
---

# /video $ARGUMENTS

Kanal Yöneticisi olarak yürüt. Kullanıcıyla Türkçe ve kısa konuş. Ajanlara her seferinde video klasörünün yolunu ve okumaları gereken dosyaları açıkça ver (senin sohbetini görmezler).

0. **Hazırlık:** `python -m hat kontrol` hata veriyorsa dur ve `/kurulum` öner.
1. **Konu:** $ARGUMENTS boşsa `strateji-direktoru` konu seçsin. Kullanıcıya tek satırla göster: "Konu: … (sütun). Devam edeyim mi?" — kullanıcı daha önce "sormadan devam" dediyse sorma.
2. **Klasör:** `python -m hat yeni <kisa-ad-ingilizce>` (ör. `panama-canal-locks`).
3. **Araştırma:** `arastirmaci` → `arastirma.md`.
3b. **Uzman kontrolü (CLAUDE.md kural 8):** En önemli 5-8 rakamı Yiğit'e Türkçe kısa liste olarak göster, "sahaya uygun mu, eklemek istediğin bir satın almacı notu var mı?" diye sor; cevabı `arastirma.md` → "Owner review" bölümüne yaz. Yiğit "sormadan devam" dediyse bu adımı atla ama rakamları teslim mesajında listele.
4. **Senaryo:** `senarist` → `senaryo.json`.
5. **Paket:** `paketleme-direktoru` → başlık, thumbnail varyantları, açıklama, etiketler (`senaryo.json` içinde).
6. **Denetim A:** `kalite-denetcisi` (Aşama A). `KARAR: DÜZELT` ise ilgili ajana düzelttir, tekrar denetle (en fazla 2 tur).
7. **Üretim:** `produksiyon` → `python -m hat uret`, önizleme kontrolü, zayıf görselleri değiştir.
8. **Denetim B:** `kalite-denetcisi` (Aşama B). Gerekirse `produksiyon` düzeltsin.
9. **Yükleme:** `python -m hat yukle "videolar/<klasör>"` → videolar ÖZEL olarak yüklenir.
9b. **Reels paketi:** `dagitim-direktoru` → 3 dikey klip + İngilizce açıklamalar + `python -m hat dagitim` → `videolar/<klasör>/dagitim/` (Instagram + Facebook). Paylaşmaz.
10. **Teslim (Türkçe, en fazla 8 satır):**
    - Başlık ve linkler (uzun + Shorts), hepsi ÖZEL
    - 1 cümle özet, süre, bu videonun harcaması ve bu ayın toplamı (`python -m hat maliyet`)
    - "YouTube Studio'da izle. Beğenirsen: Görünürlük → Planla (öneri: Salı veya Perşembe, ABD Doğu saatiyle 17:00 = Türkiye saatiyle gece 00:00-01:00). Thumbnail için Test et ve karşılaştır'a b ve c'yi ekle."
    - "Instagram + Facebook: 3 Reels hazır (`videolar\<klasör>\dagitim`). Uzun video yayınlandıktan sonra Meta Business Suite'te 1., 3. ve 5. güne planla; adımlar PAYLAS.txt'de."
    - Kullanıcının karar vermesi gereken tek şey varsa onu sor.
