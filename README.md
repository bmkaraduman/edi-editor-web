# ediviewer

**Canlı: <https://ediviewer.net>**

EDIFACT ve ANSI X12 dosyalarını tarayıcıda görüntüleyin, düzenleyin, PDF ve Excel'e
aktarın, JSON ve XML'e çevirin.

macOS/SwiftUI **Editor** projesinin web'e 1:1 taşınmış hali.
Saf HTML + CSS + ES modülleri (JavaScript). Derleme adımı ve paket bağımlılığı yok;
uygulama mantığının tamamı yereldir.

Reklamlar **Auto Ads** ile tüm sayfalarda çalışır (editör dahil).

Rıza yönetimi Google Consent Mode v2 ile yapılır (`js/consent.js`): AEA / Birleşik
Krallık / İsviçre ziyaretçileri için ölçüm ve reklam izinleri **varsayılan olarak
reddedilmiş** başlar. Rıza ekranını normalde Google'ın sertifikalı CMP'si gösterir.

CMP birkaç saniye içinde yüklenmezse **yedek bir bant** devreye girer ve yalnızca
**ölçüm** izni ister. Reklam izinleri bilerek dışarıda bırakılmıştır: Google, AEA'da
reklam için sertifikalı bir CMP şartı koşar ve elle yazılmış bir bant bunu karşılamaz.
Bölge tespiti Cloudflare'in `/cdn-cgi/trace` ucundan yapılır.

Çerezlere izin verilmese dahi uygulamanın tüm işlevleri eksiksiz çalışır.

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

GitHub Pages HTML'e 10 dakikalık önbellek verir; **Cloudflare ise `.js` ve `.css`
dosyalarını kenarda 4 saat tutar** (`max-age=14400`). Bu, bir deploy'dan sonra yeni
JS ile eski CSS'in aynı anda servis edilmesine ve arayüzün bozulmasına yol açabilir.

Bunu önlemek için CSS bağlantıları içerik özetiyle damgalanır:
`css/styles.css?v=<hash>`. Damgayı `tools/build_reference.py` hesaplar ve hem üretilen
sayfalara hem elle yazılan üç sayfaya (`index.html`, `gizlilik.html`, `privacy.html`)
yazar. CSS değişince damga değişir, adres yeni bir önbellek anahtarı olur ve eski
sürüm servis edilemez.

**CSS'i elle düzenledikten sonra `python3 tools/build_reference.py` çalıştırmak
gerekir**, aksi hâlde damga eskide kalır.

JS modülleri birbirini damgasız `import` ettiği için aynı koruma onlarda yoktur;
JS'te kırıcı bir değişiklik yapılırsa Cloudflare önbelleğini temizlemek gerekebilir.

## EDI Referansı

`edi/` altındaki referans bölümü, `tools/build_reference.py` tarafından üretilir.
Elle düzenlenmez — kaynaklar şunlardır:

- `locales/*.json` — segment, eleman ve kod açıklamaları (uygulamayla ortak sözlük)
- `tools/content.py` — elle yazılmış segment açıklamaları, örnekler ve rehber yazıları
- `tools/blog.py` — blog yazıları

Üretilen bölümler: segment ve mesaj tipi sayfaları, rehberler, blog (`edi/blog/`) ve
**Ne Nedir?** arama sayfası (`edi/ara.html`, `edi/en/search.html`). Arama, üretilen
`edi/search-index.json` dosyasını istemci tarafında filtreler (`js/refSearch.js`);
bir mesaj tipi aratıldığında içindeki segmentleri de listeler.

Yeniden üretmek için:

```bash
python3 tools/build_reference.py
```

Komut `edi/` klasörünü silip yeniden kurar; ayrıca `sitemap.xml`, `robots.txt` ve
`js/referenceIndex.js` dosyalarını üretir. Sonuncusu, uygulamanın hangi segmentler
için referans bağlantısı gösterebileceğini bildirir — sayfası olmayan bir segmentte
bağlantı hiç çıkmaz, böylece 404 oluşmaz. Üretilen sayfalar repoya commit edilir; GitHub Pages'te
derleme adımı olmadığı için hazır HTML gerekir.

Çeviri dosyalarına yeni bir segment ya da kod eklendiğinde komutu tekrar çalıştırmak
yeterlidir; sayfalar kendiliğinden oluşur.

## Dönüşüm (EDI ↔ JSON ↔ XML)

Toolbar'daki **Dönüştür** menüsü dört yönü de sunar: EDI→JSON, JSON→EDI,
EDI→XML, XML→EDI (kaynak JSON ya da XML iken ikisi arasında da geçilebilir).
Sonuç **yeni bir sekmede** açılır; düzenlenebilir, geri çevrilebilir ve
kaydedilebilir — sekme altyapısının tamamı olduğu gibi kullanılır.

Dört yön tek bir kanonik modelden geçer, okuyucular ve yazıcılar bağımsızdır:

```
.edi  ─┐                                   ┌─  .edi
.json ─┼─ EdiModel { syntax, segments } ─┼─  .json
.xml  ─┘                                   └─  .xml
```

### Şema

`segments[].elements` **`string[][]`**'dir: dış dizi veri elemanları (etiket
hariç), iç dizi bileşenler. Basit eleman tek elemanlı dizidir. Nesne/anahtar
tabanlı bir şema `NAD+BY+871::9++ACME` içindeki `::` ve `++` boşluklarını
koruyamazdı; konumsal dizi korur.

`syntax` bloğu ayraçları, kaçış karakterini, satır sonu biçimini ve BOM'u taşır —
şemanın kayıpsız olmasının nedeni budur. XML sürümü JSON'un birebir aynasıdır
(`<segment tag="…"><element><component>…`), böylece tek ayrıştırma yolu yeter.

**Açıklamalı mod** (`Açıklamaları ekle`) segmentlere `description`, elemanlara
`info` ekler. Bunlar uygulamanın kendi sözlüğünden gelir — arayüzde ne yazıyorsa
dosyada da o yazar — ve şemanın **üst kümesidir**: okuyucu yok sayar, dolayısıyla
açıklamalı çıktı da geri dönüştürülebilir. Şema anahtarları hiçbir zaman
çevrilmez; yalnızca `description`/`info` değerleri yerelleşir, böylece bir dilde
üretilen dosya başka bir dilde açılabilir.

### Kayıpsızlık

Her dönüşümden sonra sonuç geri çevrilip EDI bayt biçiminde kaynakla
karşılaştırılır. Sekme banner'ında **Round-trip doğrulandı** / **Round-trip
farklı** rozeti çıkar; ikinci durumda ayrıca bir uyarı diyaloğu gösterilir.
Sessiz veri kaybı olmaz.

Bilinen tek normalleştirme: release karakterinin özel olmayan bir karakterden
önce kullanılması (`?X`) — bu geçersiz EDI'dir, standarda göre `X` olarak
çözülür ve `?` geri yazılmaz. Doğrulayıcı bu farkı yakalar.

`js/ediSyntax.js`, `js/parser.js`'teki `EDIParser`'dan **ayrıdır ve onun yerini
almaz**. EDIParser akıllı açıklama, detay paneli ve PDF/CSV üreticileri için
tasarlandı: satırları trim'ler, satır sonlarını siler, ayraçları sabit varsayar
ve release karakterini bilmez. Bunlar o kullanım için zararsız, ama round-trip
için değil. İki tarayıcının yan yana durması bilinçlidir — alternatifi
EDIParser'ı değiştirip ona bağlı bütün üreticileri regresyon riskine atmaktı.

### Sınama

Derleme adımı olmadığı için test koşucusu da yok; kayıpsızlık sınaması
tarayıcıda çalışır:

```
http://localhost:5599/?selftest=1
```

Gömülü örnekleri (X12, UNA + CRLF, kaçış karakterleri, özel ayraçlar, tek satır,
boş elemanlar) her iki hedefe ve her iki modda çevirip baytı baytına eşitlik
arar; sonucu diyalog ve `console.table` ile bildirir.

Dil dosyalarının anahtar paritesi ayrı bir komutla denetlenir:

```bash
python3 tools/check_locales.py
```

`js/i18n.js` İngilizceye fallback yaptığı için eksik bir anahtar hata vermez,
sessizce İngilizce metin sızdırır — bu komut onu yakalar.

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

Dönüştürülmüş sekmelerde vurgulama belgenin diline göre değişir (JSON ve XML için
ayrı kurallar). PDF/Excel dışa aktarma, segment detay paneli ve mesaj tipi tespiti
yalnızca EDI belgelerinde etkindir — belgenin dili `language` alanında tutulur.

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
| `tr/en/de/fr/es/it/zh-Hans.json` | `locales/*.json` | Swift'teki anahtarlar birebir + web'e özel anahtarlar (örnek dosya, sürükle-bırak ipucu, gizlilik/çerez bağlantıları, dönüşüm modülü) — 7 dilde 984 anahtar, `tools/check_locales.py` ile denetlenir |
| — | `js/sampleData.js` | Açılışta yüklenen gömülü örnek EDIFACT dosyası |
| — | `js/ediSyntax.js` | Kayıpsız EDI sözdizimi katmanı: UNA, X12 ISA konumsal ayraçları, release karakteri, satır sonu ve BOM korunumu |
| — | `js/convert.js` | Kanonik model, JSON ve XML okuyucu/yazıcıları, biçim algılama, round-trip doğrulaması, `?selftest=1` sınaması |
| — | `js/convertPanel.js` | Dönüştür menüsü, seçenekler ve dönüşümün yürütülmesi |
| — | `js/consent.js` | Consent Mode v2 varsayılanları; GA ve AdSense yükleyicileri |
| — | `js/referenceIndex.js` | Üretilmiştir: referans sayfası olan segment kodları |
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
