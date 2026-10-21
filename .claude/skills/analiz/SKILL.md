---
name: analiz
description: Yayındaki videoların performans teşhisi; kullanıcıdan hangi Studio verisini indireceğini adım adım ister, analist ajanıyla teşhis eder ve öğrenme kaydını günceller.
argument-hint: "[video klasörü veya boş]"
disable-model-invocation: true
---

# /analiz $ARGUMENTS

1. Hangi videolar yayında: `videolar/*/yukleme.json` dosyalarına bak; kullanıcıya hangilerini yayınladığını sor (özel olanlar analiz edilmez).
2. Veri yoksa Türkçe 4 adımla tarif et: Studio → İçerik → video → Analizler → "Gelişmiş mod" → Kitle tutma → Dışa aktar (CSV) → dosyayı `videolar\<klasör>\analiz\` içine koy; Erişim sekmesinin ekran görüntüsünü de koy.
3. `analist` teşhis etsin. Kullanıcıya 3 satır: en önemli bulgu, bir sonraki videoda değişecek tek şey, ilgili ajan.
