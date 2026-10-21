---
name: dagitim
description: Bir videonun Instagram + Facebook Reels paylaşım paketini hazırlar (3 dikey klip, İngilizce açıklamalar, kapaklar, paylaşım takvimi). Kendisi paylaşmaz; kullanıcı Meta Business Suite'te planlar.
argument-hint: "[video klasörü (isteğe bağlı; boşsa son yüklenen video)]"
disable-model-invocation: true
---

# /dagitim $ARGUMENTS

Kanal Yöneticisi olarak yürüt. Kullanıcıyla Türkçe ve kısa konuş.

1. **Video:** $ARGUMENTS boşsa `videolar/` içinde `yukleme.json` dosyası olan en yeni klasörü seç. `shorts/short-1.mp4` yoksa önce `python -m hat uret "<klasör>" --adim shorts` çalıştır.
2. **Paket:** `dagitim-direktoru` ajanını çalıştır; ona klasör yolunu ve okuması gereken dosyaları açıkça ver (`senaryo.json`, `ses/zamanlar.json`, `yukleme.json`, `kanal/kimlik.md`, `ayarlar.json`).
3. **Teslim (Türkçe, en fazla 8 satır):**
   - 3 Reels: her biri tek satır (konu + süre) ve paylaşım günü
   - Klasör: `videolar\<klasör>\dagitim` (Dosya Gezgini'nde açmak için: `explorer videolar\<klasör>\dagitim`)
   - Nasıl paylaşılır: "Meta Business Suite → Oluştur → Reel → Instagram ve Facebook'u seç → N-reel.mp4'ü yükle → N-instagram.txt'deki metni yapıştır → kapak: N-kapak.jpg → Yapay zekâ etiketi AÇIK → Planla. Hepsi PAYLAS.txt dosyasında yazıyor."
   - Kullanıcının karar vermesi gereken tek şey varsa onu sor.
