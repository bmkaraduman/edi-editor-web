# -*- coding: utf-8 -*-
"""Blog yazıları.

Rehberlerden (content.GUIDES) farkı: rehberler bir konuyu baştan sona öğretir,
blog yazıları tek bir pratik soruyu kısa yoldan cevaplar. Jeneratör ikisini de
aynı şablonla üretir.
"""

BLOG_UI = {
    'tr': {
        'title': 'ediviewer Blog',
        'tagline': 'EDI dosyalarıyla çalışanlar için kısa, pratik yazılar.',
        'all_posts': 'Tüm yazılar',
        'back': 'Blog',
        'read_more': 'Devamını oku',
        'related_ref': 'İlgili referans',
    },
    'en': {
        'title': 'ediviewer Blog',
        'tagline': 'Short, practical posts for people who work with EDI files.',
        'all_posts': 'All posts',
        'back': 'Blog',
        'read_more': 'Read more',
        'related_ref': 'Related reference',
    },
}

POSTS = [
    # ---------------------------------------------------------------- 1
    {
        'slug': 'edi-nedir-neden-kullaniliyor',
        'slug_en': 'what-is-edi-why-still-used',
        'date': '2026-08-26',
        'refs': ['UNB', 'UNH'],
        'tr': {
            'title': 'EDI nedir ve API çağında neden hâlâ kullanılıyor?',
            'summary': 'REST API varken 40 yıllık bir format neden ayakta? Cevap teknolojide '
                       'değil, ticari ilişkide.',
            'body': """
EDI, iki şirketin ticari belgeleri insan eli değmeden değiş tokuş etmesidir.
Sipariş, irsaliye, fatura; hepsi standart bir yapıda, doğrudan sistemden sisteme.

## "JSON dursun, bu ne?"

EDI'yi ilk gören her yazılımcı aynı soruyu sorar: bugün REST API yazmak
varken neden 1980'lerden kalma bir metin formatı kullanılıyor?

Cevap teknik değil. Bir perakendeci binlerce tedarikçiyle çalışır. Her biriyle
ayrı API konuşmak yerine tek bir standart dayatır: "bize EDIFACT ORDERS
gönderin". Standart, taraflardan birinin diğerine uyum sağlama maliyetini
sıfırlar.

Üstelik bu standart onlarca yıldır aynı. 2005'te yazılmış bir entegrasyon bugün
hâlâ çalışıyor. API dünyasında bu cümle nadiren kurulur.

## Kim kullanıyor?

- **Perakende zincirleri** — sipariş ve fatura akışının neredeyse tamamı
- **Otomotiv** — üretim hattı beslemesi, JIT çağrıları
- **Lojistik** — sevkiyat talimatları ve durum bildirimleri
- **Sağlık ve kamu** — özellikle Avrupa'da

Türkiye'de de büyük zincir marketlerin tedarikçilerinden EDI beklemesi
yaygınlaşıyor.

## Peki gerçekten eski mi?

Format eski, mantık değil. EDI'nin çözdüğü problem — iki bağımsız sistemin
ortak bir sözlükle anlaşması — bugün de aynı. Modern alternatifler (API'ler,
Peppol gibi ağlar) aynı problemi farklı sözdizimiyle çözüyor.

Pratikte ikisi bir arada yaşıyor: pek çok firma iç sistemlerinde JSON kullanıp
dış dünyaya EDIFACT çeviriyor.

## Nereden başlamalı

Karşınıza bir EDI dosyası geldiyse önce **okuyabilmek** gerekir. Dosyayı
açıp segmentlerin ne anlama geldiğini görmek, entegrasyona girişmeden önceki
doğal ilk adımdır.
""",
        },
        'en': {
            'title': 'What is EDI, and why is it still used in the API era?',
            'summary': 'Why does a 40-year-old format survive alongside REST APIs? The answer '
                       'is commercial, not technical.',
            'body': """
EDI is how two companies exchange trade documents without human hands touching
them. Orders, despatch notes, invoices — all in a standard structure, straight
from one system to another.

## "Why not JSON?"

Every developer meeting EDI asks the same thing: with REST APIs available, why
use a text format from the 1980s?

The answer is not technical. A retailer works with thousands of suppliers.
Rather than negotiating a separate API with each one, it imposes a single
standard: "send us an EDIFACT ORDERS". The standard removes the cost of one
party adapting to the other.

And that standard has barely changed in decades. An integration written in 2005
still runs today. That sentence is rarely spoken in the API world.

## Who uses it?

- **Retail chains** — nearly all order and invoice flow
- **Automotive** — production line supply, just-in-time calls
- **Logistics** — transport instructions and status reports
- **Healthcare and public sector** — especially in Europe

## Is it really outdated?

The syntax is old; the logic is not. The problem EDI solves — two independent
systems agreeing on a shared vocabulary — has not changed. Modern alternatives
such as APIs and networks like Peppol solve the same problem with different
syntax.

In practice both coexist: many companies use JSON internally and translate to
EDIFACT at the boundary.

## Where to start

If an EDI file has landed on your desk, the first thing you need is to be able
to **read** it. Opening the file and seeing what the segments mean is the
natural first step, long before integration work begins.
""",
        },
    },
    # ---------------------------------------------------------------- 2
    {
        'slug': 'edifact-surumleri-d96a',
        'slug_en': 'edifact-versions-d96a',
        'date': '2026-08-26',
        'refs': ['UNH'],
        'tr': {
            'title': 'D.96A ne demek? EDIFACT sürümlerini anlamak',
            'summary': 'UNH satırındaki "D:96A:UN" ifadesinin her parçası ne anlatır ve '
                       'sürüm farkı neden önemlidir.',
            'body': """
Her EDIFACT mesajı hangi kural setine göre yazıldığını UNH segmentinde bildirir:

```
UNH+ME000001+ORDERS:D:96A:UN:EAN008'
```

Bu satırdaki her parça bir şey söyler.

## Parçalar

| Parça | Anlamı |
|---|---|
| `ORDERS` | Mesaj tipi |
| `D` | Dizin tipi — "Draft", yayımlanmış standart dizin |
| `96A` | Sürüm: 1996 yılının A yayımı |
| `UN` | Sorumlu kuruluş: Birleşmiş Milletler |
| `EAN008` | İlişkili kullanım kılavuzu (varsa) |

Yani `D.96A`, 1996'nın ilk yarısında yayımlanmış standart dizin demektir.

## Neden hâlâ 1996?

Yeni sürümler var — D.01B, D.07A, D.16A. Ama perakende sektörü büyük ölçüde
D.96A üzerinde kalmış durumda. Sebep basit: çalışan bir entegrasyonu
güncellemenin maliyeti, yeni sürümün getirdiği faydadan yüksek.

Sürümler arası fark çoğunlukla yeni segment ve kod eklemeleridir; temel yapı
(UNB, UNH, BGM, NAD, LIN) sürümler boyunca aynı kalmıştır.

## Beşinci parça: kullanım kılavuzu

`EAN008` gibi bir değer, standardın kendisini değil, bir sektör kılavuzunu
işaret eder. EANCOM, GS1'in perakende için hazırladığı EDIFACT alt kümesidir ve
pratikte Avrupa perakendesinde standardın kendisinden daha belirleyicidir.

Bu alan, ortağınızın şartnamesinde hangi kılavuza uyduğunuzu gösterir.

## Ne zaman sorun çıkar

Sürüm uyuşmazlığı sessiz bir hata kaynağıdır. Ortağınız D.01B beklerken D.96A
gönderirseniz mesaj çoğu zaman yine de işlenir — ta ki yalnızca yeni sürümde
bulunan bir segment kullanana kadar.

Bu yüzden şartnamedeki sürüm bilgisi, göz gezdirilecek değil, birebir
uyulacak bir alandır.
""",
        },
        'en': {
            'title': 'What does D.96A mean? Understanding EDIFACT versions',
            'summary': 'Every part of "D:96A:UN" in the UNH line, and why the version matters.',
            'body': """
Every EDIFACT message declares which rule set it follows, in the UNH segment:

```
UNH+ME000001+ORDERS:D:96A:UN:EAN008'
```

Each part of that line says something.

## The parts

| Part | Meaning |
|---|---|
| `ORDERS` | Message type |
| `D` | Directory type — the published standard directory |
| `96A` | Version: the A release of 1996 |
| `UN` | Controlling agency: the United Nations |
| `EAN008` | Associated usage guideline, where one applies |

So `D.96A` means the standard directory published in the first half of 1996.

## Why still 1996?

Newer versions exist — D.01B, D.07A, D.16A. Yet retail has largely stayed on
D.96A. The reason is simple: upgrading a working integration costs more than the
newer version is worth.

Differences between versions are mostly added segments and codes; the core
structure (UNB, UNH, BGM, NAD, LIN) has stayed the same throughout.

## The fifth part: the usage guideline

A value such as `EAN008` points not at the standard itself but at an industry
guideline. EANCOM is GS1's EDIFACT subset for retail, and in European retail it
is in practice more decisive than the standard it derives from.

This field records which guideline you are following, as set out in your
partner's specification.

## When it bites

A version mismatch is a quiet source of failure. Send D.96A where your partner
expects D.01B and the message will usually still process — right up until you
use a segment that exists only in the newer version.

That makes the version in the specification a field to match exactly, not one to
skim past.
""",
        },
    },
    # ---------------------------------------------------------------- 3
    {
        'slug': 'una-segmenti-ozel-ayiricilar',
        'slug_en': 'una-segment-custom-delimiters',
        'date': '2026-08-26',
        'refs': ['UNB'],
        'tr': {
            'title': 'UNA segmenti: ayırıcılar her zaman aynı değildir',
            'summary': 'Dosya UNA ile başlıyorsa varsayılan ayırıcıları unutun — hangi '
                       'karakterin ne olduğu orada yazar.',
            'body': """
EDIFACT ayrıştırıcı yazanların ilk varsayımı şudur: segment sonu `'`, eleman
ayracı `+`, alt eleman ayracı `:`. Çoğu dosyada doğrudur — ama garanti değildir.

## UNA ne yapar?

Bir dosya `UNA` ile başlıyorsa, o satır ayırıcıların ne olduğunu **tanımlar**:

```
UNA:+.? '
```

Altı karakterin her biri bir görevi belirler:

| Sıra | Karakter | Görev |
|---|---|---|
| 1 | `:` | Alt eleman ayracı |
| 2 | `+` | Eleman ayracı |
| 3 | `.` | Ondalık işareti |
| 4 | `?` | Kaçış (release) karakteri |
| 5 | (boşluk) | Ayrılmış, kullanılmıyor |
| 6 | `'` | Segment sonu |

Yukarıdaki örnek varsayılan değerleri tekrar ettiği için görsel olarak bir şey
değiştirmez. Ama şöyle bir UNA da geçerlidir:

```
UNA|*.? ~
```

Burada eleman ayracı `*`, segment sonu `~` olur. Varsayılanlara göre yazılmış
bir ayrıştırıcı bu dosyayı tek bir dev segment olarak okur.

## Ondalık işareti

Üçüncü karakter sık atlanır. Bazı ülkelerde ondalık ayracı virgüldür:

```
UNA:+,? '
```

Bu dosyada `PRI+AAA:1,85'` satırındaki değer bir buçuk değil, bir nokta
seksen beştir. Virgülü binlik ayracı sanıp `185` okumak, faturayı yüz kat
şişirir.

## Pratikte ne yapmalı

- Dosya `UNA` ile başlıyorsa ayırıcıları **oradan okuyun**, varsaymayın
- `UNA` yoksa varsayılanlar geçerlidir
- `UNA` satırı hiçbir zaman segment sonu karakteriyle bitmez; sabit altı
  karakter uzunluğundadır

Karşınıza gelen dosyada ilk üç harf `UNA` ise, ayrıştırma mantığınızı
çalıştırmadan önce bakılacak yer orasıdır.
""",
        },
        'en': {
            'title': 'The UNA segment: delimiters are not always the same',
            'summary': 'If a file opens with UNA, forget the defaults — that line says which '
                       'character does what.',
            'body': """
The first assumption every EDIFACT parser makes is that the segment terminator
is `'`, the element separator `+` and the component separator `:`. True for most
files — but not guaranteed.

## What UNA does

If a file opens with `UNA`, that line **defines** the delimiters:

```
UNA:+.? '
```

Each of the six characters sets one role:

| Position | Character | Role |
|---|---|---|
| 1 | `:` | Component separator |
| 2 | `+` | Element separator |
| 3 | `.` | Decimal mark |
| 4 | `?` | Release (escape) character |
| 5 | (space) | Reserved, unused |
| 6 | `'` | Segment terminator |

The example above restates the defaults, so it changes nothing visually. But
this is equally valid:

```
UNA|*.? ~
```

Here the element separator is `*` and the terminator `~`. A parser written to
the defaults reads that file as one enormous segment.

## The decimal mark

The third character is often overlooked. In some countries the decimal
separator is a comma:

```
UNA:+,? '
```

In that file, the value in `PRI+AAA:1,85'` is one point eight five, not one and
a half. Mistaking the comma for a thousands separator and reading `185` inflates
the invoice a hundredfold.

## What to do in practice

- If the file starts with `UNA`, **read** the delimiters from it; do not assume
- With no `UNA`, the defaults apply
- The `UNA` line never ends with a segment terminator; it is exactly six
  characters long

When the first three letters of a file are `UNA`, that is where to look before
your parsing logic runs at all.
""",
        },
    },
    # ---------------------------------------------------------------- 4
    {
        'slug': 'dtm-tarih-nitelikcileri',
        'slug_en': 'dtm-date-qualifiers',
        'date': '2026-08-26',
        'refs': ['DTM'],
        'tr': {
            'title': 'DTM: hangi tarih hangisi?',
            'summary': 'Bir mesajda beş farklı DTM olabilir. Hangisinin teslim, hangisinin '
                       'belge tarihi olduğunu nitelikçi söyler.',
            'body': """
Bir EDI mesajında tek bir "tarih" yoktur. Sipariş tarihi, istenen teslim
tarihi, fiili teslim tarihi, vade tarihi — hepsi ayrı DTM segmentleriyle
taşınır ve hepsi aynı görünür.

Ayıran şey ilk elemandaki **nitelikçidir**.

## En sık kullanılan nitelikçiler

| Kod | Anlamı |
|---|---|
| `137` | Belge / mesaj tarihi |
| `2` | İstenen teslim tarihi |
| `35` | Fiili teslim tarihi |
| `11` | Sevk tarihi |
| `13` | Vade (ödeme) tarihi |
| `132` | Tahmini varış |
| `356` | Dönem başlangıcı |
| `357` | Dönem bitişi |

`DTM+137:20260117:102'` belge tarihidir; `DTM+2:20260125:102'` ise teslim
tarihi. İkisini ayırmadan okuyan bir entegrasyon, siparişi yanlış güne planlar.

## Üçüncü parça: format

Değerin nasıl okunacağını üçüncü eleman söyler:

| Kod | Format | Örnek |
|---|---|---|
| `102` | YYYYMMDD | `20260117` |
| `203` | YYYYMMDDHHMM | `202601171030` |
| `718` | Tarih aralığı (iki tarih bitişik) | `2026010120260630` |
| `610` | YYYYMM (ay) | `202601` |
| `616` | YYYYWW (hafta) | `202603` |

Format kodunu okumadan değeri ayrıştırmak yaygın bir hatadır. `202601171030`
değerini `102` sanıp ilk sekiz haneyi almak size doğru günü verir ama saati
sessizce düşürür.

## Hafta formatı

`616` özellikle otomotivde görülür: teslimat haftası bildirilir, günü değil.
`202603` değeri 2026'nın üçüncü haftası demektir. Bunu tarih sanıp
ayrıştırmaya çalışmak anlamsız sonuç verir.

## Pratik kontrol

Bir dosyada beklediğiniz tarihi bulamıyorsanız, mesajdaki tüm DTM
satırlarını yan yana koyup nitelikçilerine bakın. Aradığınız tarih genellikle
oradadır, sadece farklı bir kodla.
""",
        },
        'en': {
            'title': 'DTM: which date is which?',
            'summary': 'A message can hold five different DTMs. The qualifier says which one '
                       'is delivery and which is the document date.',
            'body': """
There is no single "date" in an EDI message. Order date, requested delivery
date, actual delivery date, payment due date — each travels in its own DTM
segment, and they all look alike.

What separates them is the **qualifier** in the first element.

## The qualifiers you meet most

| Code | Meaning |
|---|---|
| `137` | Document / message date |
| `2` | Requested delivery date |
| `35` | Actual delivery date |
| `11` | Despatch date |
| `13` | Payment due date |
| `132` | Estimated arrival |
| `356` | Period start |
| `357` | Period end |

`DTM+137:20260117:102'` is the document date; `DTM+2:20260125:102'` is the
delivery date. An integration that reads them interchangeably schedules the
order on the wrong day.

## The third part: the format

The third element says how to read the value:

| Code | Format | Example |
|---|---|---|
| `102` | YYYYMMDD | `20260117` |
| `203` | YYYYMMDDHHMM | `202601171030` |
| `718` | A date range (two dates joined) | `2026010120260630` |
| `610` | YYYYMM (month) | `202601` |
| `616` | YYYYWW (week) | `202603` |

Parsing the value without reading the format code is a common mistake. Treating
`202601171030` as `102` and taking the first eight digits gives you the right
day while silently dropping the time.

## The week format

`616` turns up especially in automotive: the delivery week is stated, not the
day. `202603` means week three of 2026. Trying to parse that as a date produces
nonsense.

## A practical check

If you cannot find the date you expect in a file, line up every DTM in the
message and read their qualifiers. The date is usually there — under a different
code.
""",
        },
    },
    # ---------------------------------------------------------------- 5
    {
        'slug': 'qty-miktar-olcu-birimleri',
        'slug_en': 'qty-units-of-measure',
        'date': '2026-08-26',
        'refs': ['QTY', 'PRI'],
        'tr': {
            'title': 'Miktar ve birim: QTY segmentinde ne yazar?',
            'summary': 'Sipariş edilen mi, sevk edilen mi, teslim alınan mı? Ve PCE ile KGM '
                       'karışırsa ne olur.',
            'body': """
`QTY+21:480:PCE'` satırı üç şey söyler: hangi miktar, ne kadar, hangi birimde.
Üçünü de doğru okumak gerekir.

## Hangi miktar?

İlk eleman nitelikçidir ve miktarın anlamını belirler:

| Kod | Anlamı |
|---|---|
| `21` | Sipariş edilen miktar |
| `12` | Sevk edilen miktar |
| `194` | Teslim alınan miktar |
| `192` | Ücretsiz miktar |
| `152` | Satılan miktar (satış raporu) |
| `59` | Paket içi adet |

Aynı satırda birden fazla QTY bulunabilir. Mal kabul mesajında (RECADV) bu
zaten kuraldır: `12` sevk edileni, `194` teslim alınanı verir; ikisinin farkı
eksik teslimattır.

## Hangi birim?

Üçüncü eleman ölçü birimidir:

| Kod | Birim |
|---|---|
| `PCE` | Adet |
| `KGM` | Kilogram |
| `LTR` | Litre |
| `MTR` | Metre |
| `CT` | Karton / koli |
| `PF` | Palet |

Birim atlanırsa çoğu sistem adet varsayar. Kilogramla satılan bir ürün için bu
varsayım, siparişi bin kat yanlış hesaplatabilir.

## Fiyatla ilişkisi

Burada gözden kaçan bir nokta var: `PRI` segmenti **birim fiyattır** ve hangi
birim başına olduğunu söylemez. Yani `QTY`'deki birimle `PRI`'deki fiyatın aynı
temele oturduğu varsayılır.

Miktar kilogram, fiyat adet başınaysa hesap tutmaz. Bu tür uyuşmazlıklar
faturada ortaya çıkar ve genellikle geç fark edilir.

## Kontrol alışkanlığı

Bir satırın toplamı beklediğinizden farklıysa üç şeye bakın: nitelikçi doğru
mu, birim yazılmış mı, fiyat aynı birim üzerinden mi. Üçü tutuyorsa hata
başka yerdedir.
""",
        },
        'en': {
            'title': 'Quantity and unit: what a QTY segment says',
            'summary': 'Ordered, despatched or received? And what happens when PCE and KGM get '
                       'mixed up.',
            'body': """
The line `QTY+21:480:PCE'` says three things: which quantity, how much, and in
what unit. All three need reading correctly.

## Which quantity?

The first element is the qualifier and sets the meaning:

| Code | Meaning |
|---|---|
| `21` | Ordered quantity |
| `12` | Despatched quantity |
| `194` | Received quantity |
| `192` | Free-of-charge quantity |
| `152` | Quantity sold (sales report) |
| `59` | Number of units in a pack |

A line may carry several QTY segments. In a receiving advice (RECADV) that is
the rule rather than the exception: `12` gives what was despatched, `194` what
arrived, and the difference is the shortfall.

## Which unit?

The third element is the unit of measure:

| Code | Unit |
|---|---|
| `PCE` | Pieces |
| `KGM` | Kilograms |
| `LTR` | Litres |
| `MTR` | Metres |
| `CT` | Carton |
| `PF` | Pallet |

If the unit is omitted, most systems assume pieces. For a product sold by
weight, that assumption can be wrong by a factor of a thousand.

## Its relationship with price

An easily missed point: the `PRI` segment is a **unit price** and does not say
which unit it is per. The quantity's unit and the price's basis are assumed to
match.

If the quantity is in kilograms while the price is per piece, the arithmetic
fails. Mismatches like this surface on the invoice, usually late.

## A habit worth having

When a line total differs from what you expect, check three things: is the
qualifier right, is the unit stated, and is the price on the same basis. If all
three hold, the error is elsewhere.
""",
        },
    },
    # ---------------------------------------------------------------- 6
    {
        'slug': 'invoic-neden-reddedilir',
        'slug_en': 'why-invoices-get-rejected',
        'date': '2026-08-26',
        'refs': ['INVOIC', 'MOA', 'TAX'],
        'tr': {
            'title': 'Faturam neden reddedildi? INVOIC kontrol listesi',
            'summary': 'EDI faturaları çoğunlukla içerik yüzünden değil, eşleştirme ve toplam '
                       'hataları yüzünden geri döner.',
            'body': """
EDI faturası reddedildiğinde ilk düşünülen tutarın yanlış olduğudur. Pratikte
sebep genellikle daha sıradan bir şeydir.

## 1. Sipariş referansı eksik

Alıcı sistem faturayı siparişle eşleştiremezse elle işleme düşürür ya da
reddeder. Bağ şu satırla kurulur:

```
RFF+ON:PO-2026-0042'
```

Bu satır yoksa fatura "sahipsizdir". EDI faturalarında en sık görülen ret
sebebi budur.

## 2. Toplamlar tutmuyor

Özet bölümünde birden fazla MOA bulunur ve her biri farklı bir toplamdır:

| Kod | Anlamı |
|---|---|
| `79` | Mal toplamı (satırların toplamı) |
| `124` | Vergi tutarı |
| `77` | Genel toplam |
| `9` | Ödenecek tutar |

Alıcı sistem `79 + 124 = 77` eşitliğini kontrol eder. Yuvarlama farkı bile
reddedilmeye yeter. Satır tutarlarını kuruş bazında toplayıp özetle
karşılaştırmak, göndermeden önce yapılacak en ucuz kontroldür.

## 3. Vergi oranı belirtilmemiş

`TAX` segmenti yoksa ya da oran boşsa, alıcı KDV'yi kendisi hesaplayamaz ve
faturayı işleyemez:

```
TAX+7+VAT+++:::20'
```

## 4. Miktar sipariştekiyle uyuşmuyor

Fatura, teslim edilenden fazlasını içeriyorsa üçlü eşleştirme başarısız olur.
Kısmi teslimatta fatura da kısmi olmalıdır.

## 5. GLN yanlış

Fatura adresi (`NAD+IV`) ile sipariş adresi farklıysa ve bu ortakla mutabık
değilse, mesaj daha içeriğe bakılmadan reddedilir.

## 6. Para birimi yok

`CUX` segmenti yoksa tutarların hangi para biriminde olduğu belirsizdir. Bazı
sistemler varsayar, bazıları reddeder — ikisi de istenmez.

## Göndermeden önce

Faturayı bir görüntüleyicide açıp şu beş satırın varlığını doğrulamak,
ret döngüsünün büyük kısmını önler: `RFF+ON`, `CUX`, `TAX`, `MOA+79`,
`MOA+77`.
""",
        },
        'en': {
            'title': 'Why was my invoice rejected? An INVOIC checklist',
            'summary': 'EDI invoices usually come back for matching and totalling errors, not '
                       'for their content.',
            'body': """
When an EDI invoice is rejected, the first assumption is that an amount is
wrong. In practice the cause is usually more mundane.

## 1. The order reference is missing

If the buyer's system cannot match the invoice to an order, it drops to manual
handling or is rejected outright. The link is made by this line:

```
RFF+ON:PO-2026-0042'
```

Without it the invoice is orphaned. This is the single most common rejection
reason.

## 2. The totals do not add up

The summary section holds several MOA segments, each a different total:

| Code | Meaning |
|---|---|
| `79` | Goods total (sum of the lines) |
| `124` | Tax amount |
| `77` | Grand total |
| `9` | Amount payable |

The buyer's system checks that `79 + 124 = 77`. Even a rounding difference is
enough to fail. Summing the line amounts to the cent and comparing them against
the summary is the cheapest check you can run before sending.

## 3. No tax rate

With no `TAX` segment, or an empty rate, the buyer cannot compute VAT and cannot
process the invoice:

```
TAX+7+VAT+++:::20'
```

## 4. Quantities do not match the order

If the invoice bills more than was delivered, the three-way match fails. A
partial delivery must produce a partial invoice.

## 5. The wrong GLN

If the invoicee (`NAD+IV`) differs from the one agreed with the partner, the
message is rejected before its content is even read.

## 6. No currency

Without a `CUX` segment the currency of the amounts is undefined. Some systems
assume, others reject — neither is what you want.

## Before you send

Opening the invoice in a viewer and confirming five lines exist heads off most
of the rejection loop: `RFF+ON`, `CUX`, `TAX`, `MOA+79` and `MOA+77`.
""",
        },
    },
    # ---------------------------------------------------------------- 7
    {
        'slug': 'edi-dosyasini-excele-aktarmak',
        'slug_en': 'edi-to-excel',
        'date': '2026-08-26',
        'refs': ['LIN', 'QTY'],
        'tr': {
            'title': 'EDI dosyasını Excel\'e aktarmak',
            'summary': 'Segment yapısını satır-sütun düzenine çevirirken nelere dikkat etmeli.',
            'body': """
EDI dosyasını Excel'de görmek isteyen çoğu kişi aslında tek bir şeyi ister:
kalemleri bir tabloda yan yana görmek. Ama EDI tablo değil, iç içe geçmiş bir
ağaçtır; düzleştirmek bilinçli bir karar gerektirir.

## Sorun: hiyerarşi düzleşmiyor

Bir siparişte yapı şöyledir:

```
Mesaj
 ├── Başlık (BGM, DTM, NAD)
 └── Kalemler
      ├── LIN  → IMD, QTY, PRI, MOA
      └── LIN  → IMD, QTY, PRI, MOA
```

Excel'de bir satır bir kalem olmalıdır. Yani `LIN` satır açar, sonrasında gelen
`IMD`, `QTY`, `PRI` o satırın sütunlarını doldurur — ta ki bir sonraki `LIN`
gelene kadar.

Bu mantığı kurmadan dosyayı satır satır Excel'e dökerseniz, her segment ayrı bir
satır olur ve tablo işe yaramaz.

## Hangi sütunlar?

Bir sipariş için pratikte yeterli olan set:

| Sütun | Kaynak |
|---|---|
| Ürün kodu | `LIN` eleman 3 |
| Açıklama | `IMD` eleman 3, son parça |
| Miktar | `QTY` nitelikçi `21` |
| Birim | `QTY` üçüncü parça |
| Birim fiyat | `PRI` nitelikçi `AAA` |
| Satır tutarı | `MOA` nitelikçi `203` |

Başlık bilgileri (sipariş no, tarih, tedarikçi) tabloya değil, üst kısma ya da
ayrı bir sayfaya yazılır.

## Türkçe karakter tuzağı

CSV dosyasını Excel doğrudan açtığında Türkçe karakterler bozulabilir. Sebep,
Excel'in dosyayı UTF-8 sanmamasıdır. Çözüm, dosyanın başına BOM (byte order
mark) koymaktır — ediviewer'ın Excel çıktısı bunu zaten ekler.

## Ayraç seçimi

Türkçe Windows kurulumlarında Excel varsayılan olarak **noktalı virgül** bekler.
Virgülle ayrılmış bir dosya tek sütunda açılır. Bu yüzden CSV çıktılarında
`;` kullanmak Türkiye'de daha güvenlidir.

## Hızlı yol

Dosyayı ediviewer'da açıp **Excel'e Aktar** demek, yukarıdaki eşlemeyi hazır
yapar: kalemler satır satır, doğru sütunlarda, BOM ve noktalı virgülle.
""",
        },
        'en': {
            'title': 'Exporting an EDI file to Excel',
            'summary': 'What to watch for when flattening a segment structure into rows and '
                       'columns.',
            'body': """
Most people who want to see an EDI file in Excel want one thing: the line items
side by side in a table. But EDI is not a table — it is a nested tree, and
flattening it takes a deliberate decision.

## The problem: hierarchy does not flatten itself

An order is structured like this:

```
Message
 ├── Header (BGM, DTM, NAD)
 └── Line items
      ├── LIN  → IMD, QTY, PRI, MOA
      └── LIN  → IMD, QTY, PRI, MOA
```

In Excel one row should be one line item. So `LIN` opens a row, and the `IMD`,
`QTY` and `PRI` that follow fill that row's columns — until the next `LIN`
appears.

Dump the file into Excel line by line without that logic and every segment
becomes its own row, leaving a table nobody can use.

## Which columns?

The set that proves sufficient in practice for an order:

| Column | Source |
|---|---|
| Product code | `LIN` element 3 |
| Description | `IMD` element 3, last component |
| Quantity | `QTY` qualifier `21` |
| Unit | `QTY` third component |
| Unit price | `PRI` qualifier `AAA` |
| Line amount | `MOA` qualifier `203` |

Header information — order number, date, supplier — belongs above the table or
on a separate sheet, not in the rows.

## The encoding trap

Opening a CSV directly in Excel can corrupt accented characters, because Excel
does not assume UTF-8. The fix is a BOM (byte order mark) at the start of the
file; ediviewer's Excel export writes one already.

## Choosing a separator

Excel on many European locales expects a **semicolon**. A comma-separated file
opens in a single column there. Using `;` is the safer default outside the US.

## The quick route

Opening the file in ediviewer and choosing **Export to Excel** applies the
mapping above for you: line items as rows, in the right columns, with the BOM
and semicolons already handled.
""",
        },
    },
    # ---------------------------------------------------------------- 8
    {
        'slug': 'kucuk-isletme-edi-maliyeti',
        'slug_en': 'edi-cost-small-business',
        'date': '2026-08-26',
        'refs': [],
        'tr': {
            'title': 'Küçük bir işletme EDI\'ye ne kadar harcamalı?',
            'summary': 'Ayda 20 sipariş alan bir firmanın tam otomasyona ihtiyacı var mı? '
                       'Genellikle yok.',
            'body': """
Büyük bir müşteri "EDI ile çalışıyoruz" dediğinde küçük firmaların ilk refleksi
pahalı bir entegrasyon paketi aramaktır. Çoğu zaman bu erken bir karardır.

## Önce hacme bakın

Belirleyici soru şu: ayda kaç belge alıp göndereceksiniz?

| Hacim | Makul yaklaşım |
|---|---|
| Ayda 50'den az | Dosyayı görüntüleyip elle işleyin |
| Ayda 50-500 | Yarı otomatik: dosyadan tabloya, tablodan sisteme |
| Ayda 500+ | Tam entegrasyon yatırımı mantıklı |

Ayda 20 sipariş alan bir tedarikçi için tam otomasyon, kurulum ve bakım
maliyetiyle birlikte yıllarca kendini amorti etmez.

## Maliyet kalemleri

Bir EDI kurulumunda para üç yere gider:

- **Aktarım** — VAN kullanıyorsanız işlem başına ücret; SFTP/AS2'de sabit
  altyapı maliyeti
- **Yazılım** — çevirici (translator) lisansı ya da SaaS aboneliği
- **Kurulum ve bakım** — asıl gizli maliyet burada; ortak sürüm değiştirdiğinde
  ya da yeni alan eklediğinde tekrar iş çıkar

Üçüncüsü genellikle hafife alınır. Entegrasyon bir kez kurulup unutulan bir şey
değildir.

## Kademeli ilerlemek

Pratik bir yol şudur:

1. **Okuyun** — gelen dosyayı açıp anlayın, elle işleyin
2. **Dışa aktarın** — kalemleri tabloya dökün, kendi sisteminize toplu girin
3. **Otomatikleştirin** — hacim gerektirdiğinde entegrasyona geçin

İlk iki adım ücretsiz araçlarla yapılabilir ve pek çok firma yıllarca bu
seviyede kalır. Müşteriniz dosyayı nasıl işlediğinizle değil, doğru yanıt
verip vermediğinizle ilgilenir.

## Ne zaman otomasyona geçmeli

İşaret basittir: elle işleme süresi, hata maliyeti ya da gecikme müşteri
şikâyetine dönüşmeye başladığında. O noktaya kadar harcanmayan para,
işletmede kalır.
""",
        },
        'en': {
            'title': 'How much should a small business spend on EDI?',
            'summary': 'Does a company receiving 20 orders a month need full automation? '
                       'Usually not.',
            'body': """
When a large customer says "we work over EDI", a small supplier's first instinct
is to shop for an expensive integration package. That is usually a premature
decision.

## Start with volume

The question that decides it: how many documents will you send and receive per
month?

| Volume | A sensible approach |
|---|---|
| Under 50 a month | View the file and process it by hand |
| 50-500 a month | Semi-automatic: file to spreadsheet, spreadsheet to system |
| 500+ a month | Full integration starts to pay for itself |

For a supplier receiving twenty orders a month, full automation will not repay
its setup and maintenance cost for years.

## Where the money goes

An EDI setup spends in three places:

- **Transport** — per-transaction fees with a VAN; fixed infrastructure cost
  with SFTP or AS2
- **Software** — a translator licence or a SaaS subscription
- **Setup and maintenance** — the hidden one; every time the partner changes
  version or adds a field, there is work to do

The third is routinely underestimated. An integration is not something you build
once and forget.

## Moving in stages

A practical path:

1. **Read** — open the incoming file, understand it, process it by hand
2. **Export** — pull the line items into a spreadsheet and load them in bulk
3. **Automate** — move to integration when volume demands it

The first two steps can be done with free tools, and plenty of companies stay at
that level for years. Your customer cares whether you respond correctly, not how
you processed the file.

## When to automate

The signal is simple: when the time spent handling files by hand, the cost of
mistakes, or the delays start turning into customer complaints. Until then, the
money you do not spend stays in the business.
""",
        },
    },
    # ---------------------------------------------------------------- 9
    {
        'slug': 'edi-ve-e-fatura-farki',
        'slug_en': 'edi-vs-e-invoicing',
        'date': '2026-08-26',
        'refs': ['INVOIC'],
        'tr': {
            'title': 'EDI ile e-fatura aynı şey mi?',
            'summary': 'İkisi de elektronik fatura taşır ama amaçları, muhatapları ve zorunluluk '
                       'durumları farklıdır.',
            'body': """
Türkiye'de "elektronik fatura" denince akla e-Fatura ve e-Arşiv gelir. EDI de
fatura taşır. Aynı şey değildirler ve birbirinin yerine geçmezler.

## Muhatap kim?

Temel fark burada:

- **e-Fatura**, devlete karşı yükümlülüktür. Gelir İdaresi'nin belirlediği
  formatta (UBL-TR), onun altyapısı üzerinden gönderilir. Amaç vergi denetimidir.
- **EDI**, ticari ortağınıza karşı bir anlaşmadır. Formatı ve içeriği taraflar
  belirler. Amaç iş süreçlerini otomatikleştirmektir.

Biri yasal, diğeri ticari bir gerekliliktir.

## Kapsam farkı

e-Fatura yalnızca faturayı kapsar. EDI ise sipariş, sipariş yanıtı, sevk
ihbarı, mal kabul ve ödeme bildirimini de taşır. Fatura, EDI'nin ilgilendiği
zincirin yalnızca bir halkasıdır.

Bu yüzden EDI kullanan bir firma e-Fatura yükümlülüğünden kurtulmaz; ikisini
birlikte yürütür.

## Format farkı

| | e-Fatura | EDI (EDIFACT) |
|---|---|---|
| Format | UBL-TR (XML) | EDIFACT (metin) |
| Belirleyen | Gelir İdaresi | Ticaret ortakları |
| Zorunluluk | Yasal eşik üstü firmalar | Ortağın talebi |
| Kapsam | Yalnızca fatura | Tüm ticari zincir |

## Pratikte nasıl yürür?

Yaygın kurgu şudur: sipariş ve sevkiyat EDI ile akar, fatura hem EDI ile
ticari ortağa hem UBL-TR ile devlete gider. Aynı ticari olayın iki farklı
muhataba, iki farklı formatta bildirilmesi söz konusudur.

Bu ikilik gereksiz görünse de mantığı vardır: ortağınızın istediği alanlarla
devletin istediği alanlar örtüşmez.

## Karıştırılmaması gereken nokta

EDI faturası gönderdiğiniz için e-Fatura kesmediyseniz, vergi açısından fatura
kesilmemiş sayılır. Tersi de geçerlidir: e-Fatura kestiğiniz hâlde ortağınıza
EDI INVOIC göndermediyseniz, onun sistemi ödemeyi tetiklemez.
""",
        },
        'en': {
            'title': 'Is EDI the same as e-invoicing?',
            'summary': 'Both carry electronic invoices, but they differ in purpose, audience '
                       'and whether they are compulsory.',
            'body': """
Government e-invoicing schemes and EDI both move invoices electronically. They
are not the same thing, and one does not replace the other.

## Who is the counterparty?

That is the core difference:

- **E-invoicing** is an obligation towards the state. It uses a format the tax
  authority defines, sent over its infrastructure. The purpose is tax oversight.
- **EDI** is an agreement with your trading partner. The parties decide the
  format and content. The purpose is automating business processes.

One is a legal requirement, the other a commercial one.

## Different scope

E-invoicing covers the invoice alone. EDI also carries the order, the order
response, the despatch advice, the receiving advice and the remittance advice.
The invoice is one link in the chain EDI concerns itself with.

A company using EDI is therefore not exempt from e-invoicing; it runs both.

## Different formats

| | E-invoicing | EDI (EDIFACT) |
|---|---|---|
| Format | XML (UBL or similar) | EDIFACT (text) |
| Defined by | The tax authority | Trading partners |
| Compulsory | Above a legal threshold | When a partner requires it |
| Scope | The invoice only | The whole trade chain |

## How it works in practice

The common arrangement: orders and shipments flow over EDI, while the invoice
goes both to the trading partner as EDI and to the state in the mandated XML.
The same commercial event is reported to two audiences in two formats.

The duplication looks wasteful but has a logic to it: the fields your partner
needs and the fields the tax authority needs do not overlap.

## The point not to confuse

Sending an EDI invoice does not discharge a legal e-invoicing obligation. And
the reverse holds too: filing the legal e-invoice without sending your partner
an EDI INVOIC leaves their system with nothing to trigger payment.
""",
        },
    },
    # ---------------------------------------------------------------- 10
    {
        'slug': 'contrl-mesaji-teyit',
        'slug_en': 'contrl-acknowledgement',
        'date': '2026-08-26',
        'refs': ['UCI', 'UCM', 'UCS', 'UCD'],
        'tr': {
            'title': 'CONTRL: gönderdiğim dosya ulaştı mı?',
            'summary': 'EDI\'de "okundu bilgisi" CONTRL mesajıdır. Gelmiyorsa ya da hata '
                       'içeriyorsa ne anlama gelir.',
            'body': """
Bir EDI dosyası gönderdiniz. Ulaştı mı? İşlendi mi? Bunu söyleyen ayrı bir
mesaj vardır: **CONTRL**.

## Ne işe yarar?

CONTRL, içerikle ilgilenmez. "Siparişini kabul ettim" demez; "dosyanı aldım ve
sözdizimi geçerli" der. Yani teknik bir teyittir, ticari değil.

İki farklı şey karıştırılmamalıdır:

- **CONTRL** — dosya ulaştı, sözdizimi doğru
- **ORDRSP** — siparişi kabul ediyorum / etmiyorum

CONTRL almanız siparişinizin kabul edildiği anlamına gelmez.

## Yapısı

CONTRL mesajı, hata varsa nerede olduğunu gösterir:

| Segment | Görevi |
|---|---|
| `UCI` | Zarf düzeyinde durum |
| `UCM` | Mesaj düzeyinde durum |
| `UCS` | Hatalı segmentin sırası |
| `UCD` | Hatanın nedeni ve hangi eleman |

Durum kodları kısadır: `7` kabul, `4` reddedildi, `8` hata var ama işlendi.

```
UCI+REF00042+8712345678901:14+8798765432109:14+7'
```

Sondaki `7`, zarfın sorunsuz kabul edildiğini söyler.

## Hata geldiğinde

Reddedilme durumunda `UCS` size satır numarasını verir, `UCD` ise nedeni:

```
UCS+12'
UCD+13+QTY+2'
```

Bu, 12. segmentteki `QTY`'nin 2. veri elemanında hata olduğunu söyler. Elinizdeki
dosyayı açıp 12. segmente bakmak, sorunu doğrudan gösterir.

## Hiç CONTRL gelmiyorsa

Bu genellikle içerik hatası değil, **aktarım** sorunudur:

- Dosya karşı tarafa hiç ulaşmamıştır (SFTP dizini, AS2 sertifikası)
- Ortağınız CONTRL göndermiyordur — her ortak göndermez, şartnamede yazar
- Dosya ulaşmış ama işlenmeden kuyrukta beklemektedir

Sırasıyla bakılacak yer budur: önce aktarım kanalı, sonra şartname.

## Pratik öneri

CONTRL mesajlarını saklayın. Bir fatura "gelmedi" tartışmasında, tarihli bir
kabul teyidi en hızlı çözen belgedir.
""",
        },
        'en': {
            'title': 'CONTRL: did my file arrive?',
            'summary': 'The EDI equivalent of a read receipt is the CONTRL message. What it '
                       'means when none arrives, or when it carries errors.',
            'body': """
You sent an EDI file. Did it arrive? Was it processed? A separate message
answers that: **CONTRL**.

## What it does

CONTRL takes no interest in content. It does not say "I accept your order"; it
says "I received your file and the syntax is valid". It is a technical
acknowledgement, not a commercial one.

Two things not to confuse:

- **CONTRL** — the file arrived and parses
- **ORDRSP** — I do or do not accept the order

Receiving a CONTRL does not mean your order was accepted.

## Its structure

A CONTRL message points at where an error sits, if there is one:

| Segment | Role |
|---|---|
| `UCI` | Status at interchange level |
| `UCM` | Status at message level |
| `UCS` | Position of the offending segment |
| `UCD` | The reason and which element |

The status codes are terse: `7` accepted, `4` rejected, `8` processed with
errors.

```
UCI+REF00042+8712345678901:14+8798765432109:14+7'
```

The trailing `7` says the interchange was accepted cleanly.

## When an error comes back

On a rejection, `UCS` gives you the segment position and `UCD` the reason:

```
UCS+12'
UCD+13+QTY+2'
```

That says there is an error in the second data element of the `QTY` at segment
12. Opening your file and going to segment 12 shows the problem directly.

## When no CONTRL arrives at all

This is usually a **transport** problem rather than a content one:

- The file never reached the other side (SFTP directory, AS2 certificate)
- Your partner does not send CONTRL — not all do; the specification says so
- The file arrived but is sitting in a queue unprocessed

That is the order to check: the transport channel first, then the specification.

## A practical habit

Keep your CONTRL messages. In an argument about an invoice that "never
arrived", a timestamped acknowledgement is the fastest way to settle it.
""",
        },
    },
]
