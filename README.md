# EDI Editor — Web

macOS/SwiftUI **Editor** projesinin web'e 1:1 taşınmış hali.
Sıfır bağımlılık: saf HTML + CSS + ES modülleri (JavaScript). Derleme adımı yok.

## Çalıştırma

ES modülleri ve `fetch` ile dil dosyaları yüklendiği için `file://` üzerinden değil,
bir HTTP sunucusu üzerinden açılmalıdır. Projeyle birlikte gelen mini sunucu:

```bash
python3 serve.py
```

Ardından tarayıcıda: <http://localhost:5599>

Farklı port için: `python3 serve.py 8080`

## Yayınlama (GitHub Pages)

Proje tamamen statik: derleme adımı, sunucu tarafı kod veya harici bağımlılık yok.
Tüm yollar göreli olduğu için `kullaniciadi.github.io/repo-adi/` gibi bir alt dizinde
de sorunsuz çalışır.

1. GitHub'da boş bir repo açıp push edin.
2. **Settings → Pages → Source: Deploy from a branch**, branch `main`, klasör `/ (root)`.
3. Bir dakika içinde `https://kullaniciadi.github.io/repo-adi/` adresinde yayında olur.

Kökteki boş `.nojekyll` dosyası, GitHub'ın içeriği Jekyll'den geçirmesini engeller —
dağıtım hem hızlanır hem de dosyalar olduğu gibi servis edilir.

Özel alan adı sonradan **Settings → Pages → Custom domain** üzerinden eklenebilir;
mevcut adres çalışmaya devam eder.

> HTTPS gereklidir: "Kaydet" özelliği File System Access API kullanır ve bu API yalnızca
> güvenli bağlamda çalışır. `*.github.io` adreslerinde HTTPS varsayılan olarak açıktır.

### Açılış davranışı

Uygulama, boş bir hoşgeldin ekranı yerine **örnek bir EDIFACT siparişi yüklü sekmeyle** açılır
(`js/sampleData.js` içinde gömülü; ek istek gerektirmez). İlk segment seçili gelir, böylece
detay paneli ilk karede doludur. Tüm sekmeler kapatılırsa hoşgeldin ekranı görünür ve oradaki
**Örnek Dosya** butonu aynı dosyayı yeniden açar.

`samples/` klasöründe ORDERS, INVOIC ve SLSRPT örnek dosyaları var
(dosyayı editöre sürükleyip bırakabilir veya **Dosya Aç** ile seçebilirsiniz).

### Editör özellikleri

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
| `tr/en/de/fr/es/it/zh-Hans.json` | `locales/*.json` | Swift'teki 954 anahtar birebir + web'e özel 2 anahtar (`sample_file`, `welcome_hint`) |
| — | `js/sampleData.js` | Açılışta yüklenen gömülü örnek EDIFACT dosyası |

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
