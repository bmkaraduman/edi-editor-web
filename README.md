# ediviewer

**Canlı: <https://ediviewer.net>**

EDIFACT ve ANSI X12 dosyalarını tarayıcıda görüntüleyin, düzenleyin, PDF ve Excel'e aktarın.

macOS/SwiftUI **Editor** projesinin web'e 1:1 taşınmış hali.
Saf HTML + CSS + ES modülleri (JavaScript). Derleme adımı ve paket bağımlılığı yok;
uygulama mantığının tamamı yereldir.

Harici istekler yalnızca Google Analytics ve AdSense'ten ibarettir. Rıza yönetimi
Google Consent Mode v2 ile yapılır (`js/consent.js`): AEA / Birleşik Krallık / İsviçre
ziyaretçileri için ölçüm ve reklam izinleri **varsayılan olarak reddedilmiş** başlar ve
rıza ekranını Google'ın sertifikalı CMP'si gösterir. Çerezlere izin verilmese dahi
uygulamanın tüm işlevleri eksiksiz çalışır.

## Çalıştırma

ES modülleri ve `fetch` ile dil dosyaları yüklendiği için `file://` üzerinden değil,
bir HTTP sunucusu üzerinden açılmalıdır. Projeyle birlikte gelen mini sunucu:

```bash
python3 serve.py
```

Ardından tarayıcıda: <http://localhost:5599>

Farklı port için: `python3 serve.py 8080`

## Yayınlama

Proje tamamen statik: derleme adımı veya sunucu tarafı kod yok. Tüm yollar göreli
olduğu için hem kök dizinde hem `kullaniciadi.github.io/repo-adi/` gibi bir alt
dizinde sorunsuz çalışır.

### Mevcut kurulum

| Katman | Ayar |
|---|---|
| Hosting | GitHub Pages — `main` branch, `/ (root)` |
| Alan adı | `ediviewer.net`, kökteki `CNAME` dosyasıyla tanımlı |
| DNS / TLS | Cloudflare (proxy açık), sertifikayı Cloudflare sağlar |
| HTTPS | Cloudflare → **Always Use HTTPS** açık |

`main` dalına yapılan her push bir dakika içinde otomatik yayına girer.

Bütün giriş yolları tek adrese toplanır:

```
http://ediviewer.net       ─┐
http://www.ediviewer.net   ─┼──►  https://ediviewer.net/
https://www.ediviewer.net  ─┤
github.io/edi-editor-web/  ─┘
```

`www`'nin apex'e yönlenmesi bilinçlidir: `localStorage` origin başına ayrı tutulduğu
için iki ayrı hostname, kullanıcının tema/dil/logo ayarlarının bölünmesine yol açardı.

### Sıfırdan kurmak isterseniz

1. GitHub'da boş bir repo açıp push edin.
2. **Settings → Pages → Source: Deploy from a branch**, branch `main`, klasör `/ (root)`.
3. Özel alan adı için **Settings → Pages → Custom domain**; GitHub repoya bir `CNAME`
   dosyası commit'ler, sonrasında yerelde `git pull` yapmayı unutmayın.
4. DNS: apex için GitHub'ın dört A kaydı, `www` için `kullaniciadi.github.io` CNAME'i.

Kökteki boş `.nojekyll` dosyası, GitHub'ın içeriği Jekyll'den geçirmesini engeller —
dağıtım hem hızlanır hem de dosyalar olduğu gibi servis edilir.

> **HTTPS zorunludur.** "Kaydet" özelliği File System Access API kullanır ve bu API
> yalnızca güvenli bağlamda çalışır; düz HTTP'de kaydetme sessizce devre dışı kalır.

> **Cloudflare notu:** proxy (turuncu bulut) açıkken şifreleme modu `Full` olmalıdır.
> `Flexible` modda Cloudflare ile GitHub arasındaki trafik şifresiz akar. GitHub
> tarafındaki "Enforce HTTPS" kutusuna ise gerek yoktur; TLS'i Cloudflare sonlandırır.

### Dağıtım önbelleği

GitHub Pages statik dosyalara 10 dakikalık önbellek verir (`max-age=600`). Yeni
ziyaretçiler güncel sürümü alır; siteyi daha önce açmış olanlar bir deploy sonrası
kısa süre eski CSS/JS görebilir. Hemen görmek için sabit yenileme (`Cmd/Ctrl+Shift+R`).

## EDI Referansı

`edi/` altındaki referans bölümü, `tools/build_reference.py` tarafından üretilir.
Elle düzenlenmez — kaynaklar şunlardır:

- `locales/*.json` — segment, eleman ve kod açıklamaları (uygulamayla ortak sözlük)
- `tools/content.py` — elle yazılmış segment açıklamaları, örnekler ve rehber yazıları

Yeniden üretmek için:

```bash
python3 tools/build_reference.py
```

Komut `edi/` klasörünü silip yeniden kurar, ayrıca `sitemap.xml` ve `robots.txt`
dosyalarını günceller. Üretilen sayfalar repoya commit edilir; GitHub Pages'te
derleme adımı olmadığı için hazır HTML gerekir.

Çeviri dosyalarına yeni bir segment ya da kod eklendiğinde komutu tekrar çalıştırmak
yeterlidir; sayfalar kendiliğinden oluşur.

## Açılış davranışı

Uygulama, boş bir hoşgeldin ekranı yerine **örnek bir EDIFACT siparişi yüklü sekmeyle** açılır
(`js/sampleData.js` içinde gömülü; ek istek gerektirmez). İlk segment seçili gelir, böylece
detay paneli ilk karede doludur. Tüm sekmeler kapatılırsa hoşgeldin ekranı görünür ve oradaki
**Örnek Dosya** butonu aynı dosyayı yeniden açar.

`samples/` klasöründe ORDERS, INVOIC ve SLSRPT örnek dosyaları var
(dosyayı editöre sürükleyip bırakabilir veya **Dosya Aç** ile seçebilirsiniz).

## Editör özellikleri

Satır numarası cetveli, aktif satır vurgusu (hem cetvelde hem metinde), segment etiketi
renklendirme, sürüklenebilir bölme çizgisi ve dar ekranlarda ikon moduna geçen toolbar.

## Swift ↔ Web dosya eşlemesi

| Swift | Web | İçerik |
|---|---|---|
| `EditorApp.swift`, `ContentView.swift`, `CustomTabBar.swift`, `WelcomeView.swift` | `js/app.js` | Uygulama kabuğu, toolbar, sekmeler, hoşgeldin ekranı, menüler, diyaloglar, kısayollar |
| `EdiSegment.swift` (`EDIParser`) | `js/parser.js` | Mesaj tipi tespiti, segment parse, akıllı açıklamalar, EDI doğrulama |
| `SegmentDetailView.swift` | `js/segmentDetail.js` | `analyzeElement` motoru (tüm segment/element kuralları) + detay paneli |
| `PDFExportManager.swift` | `js/pdfExport.js` | ORDERS / ORDRSP / ORDCHG / DESADV / RECADV / IFTMIN / INVOIC / REMADV / DELJIT / SLSRPT + generic HTML üreticiler |
| `CSVExportManager.swift` | `js/csvExport.js` | SLSRPT / PRICAT / generic CSV motorları |
| `DocumentManager.swift`, `EDIDocumentModel.swift`, `EDIDocument.swift` | `js/documentManager.js` | Sekme yönetimi, aç/kaydet/farklı kaydet, dışa aktarma tetikleyicileri |
| `LanguageManager.swift` | `js/i18n.js` | 7 dilli JSON sözlük + İngilizce fallback (merge mantığı aynı) |
| `LogoManager.swift` | `js/logoManager.js` | Şirket logosu seçimi ve kalıcı saklama |
| `SyntaxHighlightEditor.swift` | `js/editor.js` | Söz dizimi vurgulu editör, seçili satır tespiti |
| `windowsclosehandler.swift` | `js/app.js` (`beforeunload`) | Kaydedilmemiş değişiklik uyarısı |
| `tr/en/de/fr/es/it/zh-Hans.json` | `locales/*.json` | Swift'teki 954 anahtar birebir + web'e özel 4 anahtar (örnek dosya, sürükle-bırak ipucu, gizlilik/çerez bağlantıları) = 958 |
| — | `js/sampleData.js` | Açılışta yüklenen gömülü örnek EDIFACT dosyası |
| — | `js/consent.js` | Consent Mode v2 varsayılanları; GA ve AdSense yükleyicileri |
| — | `gizlilik.html` / `privacy.html` | Gizlilik politikası (TR / EN) |

## Platform karşılıkları

| macOS / AppKit | Web |
|---|---|
| `NSOpenPanel` / `NSSavePanel` | File System Access API (`showOpenFilePicker` / `showSaveFilePicker`) — desteklenmiyorsa `<input type=file>` + indirme |
| `WKWebView.createPDF` | Aynı HTML, tarayıcının yazdırma motoruna verilir → **Hedef: PDF olarak kaydet** |
| `@AppStorage` | `localStorage` |
| `NSTextView` + `textStorage` renkleri | Şeffaf `<textarea>` + altında birebir hizalı `<pre>` vurgu katmanı |
| `VSplitView` | Sürüklenebilir yatay ayırıcı |
| `.alert` / `.confirmationDialog` | Kendi modal diyalog bileşeni (aynı butonlar, aynı roller) |
| Documents klasörüne `company_logo.png` | Logo, data URL olarak `localStorage`'da |
| `NSImage` toolbar logosu | `<img>` |

### Klavye kısayolları
`⌘N` yeni sekme · `⌘O` aç · `⌘S` kaydet · `⇧⌘S` farklı kaydet · `⌘W` sekmeyi kapat ·
`⌘Z` / `⇧⌘Z` / `⌘X` / `⌘C` / `⌘V` / `⌘A` tarayıcının kendi metin komutları

### Tarayıcı desteği
Tümü modern tarayıcılarda çalışır. **Dosyayı yerinde kaydetme** (aynı dosyanın üzerine yazma)
File System Access API gerektirir — Chrome / Edge / Opera'da desteklidir.
Safari ve Firefox'ta kaydetme işlemi indirme olarak yapılır.

## Davranıştaki bilinçli iki fark

1. **Generic CSV'deki segment açıklaması.** Swift tarafında `NSLocalizedString` kullanılıyor,
   ancak projede `Localizable.strings` bulunmadığı için bu alan her zaman `-` dönüyor.
   Web sürümü, uygulamanın kendi JSON sözlüğünü kullanır; sütun artık gerçekten dolu gelir.
2. **Kaydedilmemiş sekme kapatılırken "Kaydet".** Swift tarafında kaydetme iptal edilse bile
   sekme kapanıyor (veri kaybı). Web sürümünde sekme yalnızca kayıt başarılıysa kapanır.

Bunun dışındaki tüm çıktı ve etiket mantığı Swift kaynağıyla birebirdir; PDF/CSV üreticilerinin
HTML ve sütun yapısı satır satır aynıdır.
