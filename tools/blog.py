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

EDI'yi ilk gören her yazılımcı aynı soruyu sorar: bugün REST API yazmak varken
neden 1980'lerden kalma bir metin formatı kullanılıyor?

Cevap teknik değil, ticari. Bir perakende zinciri binlerce tedarikçiyle çalışır.
Her biriyle ayrı bir API konuşmak yerine tek bir standart dayatır: "bize EDIFACT
ORDERS gönderin". Standart, uyum sağlama maliyetini zincirin kendisinden
tedarikçiye kaydırır — ve tedarikçi için de bu maliyet, her müşteriye ayrı
entegrasyon yazmaktan ucuzdur.

## Asıl mesele: N×M problemi

Diyelim 500 tedarikçi ve 20 zincir var. Herkes kendi API'siyle konuşsaydı
teorik olarak 10.000 ayrı entegrasyon gerekirdi. Ortak bir standart bunu
520 entegrasyona indirir: herkes yalnızca standardı bir kez öğrenir.

Bu, EDI'nin çözdüğü asıl problemdir ve teknolojiyle ilgisi yoktur. Format
değişse de problem aynı kalır; nitekim Peppol gibi modern ağlar da aynı mantıkla
çalışır, yalnızca sözdizimi farklıdır.

## Kim kullanıyor?

- **Perakende zincirleri** — sipariş ve fatura akışının neredeyse tamamı. Bir
  markete tedarikçi olmak istiyorsanız EDI genellikle sözleşme şartıdır.
- **Otomotiv** — üretim hattı beslemesi ve tam zamanında (JIT) teslimat
  çağrıları. Burada gecikme doğrudan bandın durması demektir.
- **Lojistik** — sevkiyat talimatları, taşıma durum bildirimleri, gümrük
  belgeleri.
- **Sağlık ve kamu** — özellikle Avrupa'da ihale ve fatura süreçleri.

Türkiye'de de büyük zincir marketlerin tedarikçilerinden EDI beklemesi
yaygınlaşıyor; çoğu zaman ilk karşılaşma da böyle oluyor: müşteriden gelen bir
şartname ve ekinde örnek bir dosya.

## Bir EDI mesajı neye benzer?

Aşağıdaki dört satır bir siparişin başlangıcıdır:

```
UNB+UNOC:3+8712345678901:14+8798765432109:14+260117:1030+REF00042'
UNH+ME000001+ORDERS:D:96A:UN:EAN008'
BGM+220+PO-2026-0042+9'
NAD+BY+8798765432109::9++MEGA RETAIL AS+Barbaros Bulvari 12+ISTANBUL+34353+TR'
```

Okunması zor görünse de mantığı basittir. Her satır bir **segment**, satır
başındaki üç harf ise o segmentin ne anlattığını söyler:

| Segment | Anlamı |
|---|---|
| `UNB` | Zarf başlığı: kimden kime, ne zaman |
| `UNH` | Mesaj başlığı: bu bir ORDERS, D.96A sürümü |
| `BGM` | Belge numarası: PO-2026-0042 |
| `NAD` | Taraf bilgisi: `BY` alıcı demek |

Segmentlerin içi `+` ile veri elemanlarına, elemanlar da gerektiğinde `:` ile
alt parçalara bölünür. Yapının tamamı budur; geri kalanı hangi kodun ne
anlama geldiğini bilmekten ibarettir.

## Peki gerçekten eski mi?

Format eski, mantık değil. EDI'nin çözdüğü problem — iki bağımsız sistemin
ortak bir sözlükle anlaşması — bugün de aynı.

Üstelik bu standart onlarca yıldır kararlı. 2005'te yazılmış bir entegrasyon
bugün hâlâ çalışıyor olabilir. API dünyasında bu cümle nadiren kurulur; sürüm
yükseltmeleri, kaldırılan uç noktalar ve değişen kimlik doğrulama şemaları
gündelik iştir. EDI'de "çalışıyorsa dokunma" gerçekten mümkündür.

Formatın maliyeti ise okunabilirlik. Sıkıştırılmış, insana göre tasarlanmamış
bir sözdizimi bu; hata ayıklarken doğru araca ihtiyaç duymanızın nedeni de bu.

## EDI ile API birlikte nasıl yaşıyor?

Pratikte ikisi bir arada bulunur. Yaygın kurulum şöyledir:

- İç sistemler kendi aralarında JSON konuşur
- Dış dünyaya açılan sınırda bir dönüştürücü katman durur
- Bu katman giden veriyi EDIFACT'e, gelen EDIFACT'i JSON'a çevirir

Yani EDI çoğu zaman uygulamanın içine değil, kenarına yerleşir. Bu ayrım
önemlidir: iş mantığınızı EDI segmentleri üzerine kurmak yerine, kendi veri
modelinizi koruyup sınırda çeviri yapmak uzun vadede daha az acı verir.

## Nereden başlamalı

Karşınıza bir EDI dosyası geldiyse sıra şudur:

1. **Dosyayı okuyabilir hale getirin.** Hangi mesaj tipi, hangi taraflar, hangi
   kalemler? Bu adım entegrasyona girişmeden önce yapılmalıdır.
2. **Ortağınızın şartnamesini isteyin.** EDIFACT geniştir; her ortak alt kümesini
   ve zorunlu alanlarını kendi belgesinde tanımlar. Standart tek başına yeterli
   değildir.
3. **Örnek dosyayla şartnameyi karşılaştırın.** Şartnamede zorunlu denen bir alan
   örnekte boşsa, bu genellikle sizin değil şartnamenin eskimiş olduğunun
   işaretidir; sormak zaman kazandırır.
4. **Sonra kod yazın.** Ayrıştırıcıyı kendiniz yazmadan önce, elinizdeki
   dosyanın gerçekten ne içerdiğini görmüş olun.

İlk adım için tarayıcıda çalışan bir görüntüleyici yeterlidir; dosyayı hiçbir
yere yüklemeden segmentlerin ne anlama geldiğini görebilirsiniz.
""",
        },
        'en': {
            'title': 'What is EDI, and why is it still used in the API era?',
            'summary': 'Why does a 40-year-old format survive alongside REST APIs? The answer '
                       'is commercial, not technical.',
            'body': """
EDI is the exchange of commercial documents between two companies without human
hands in the middle. Orders, despatch notes, invoices — all in a standard
structure, straight from one system to another.

## "We have JSON. What is this?"

Every developer who meets EDI for the first time asks the same question: why use
a text format from the 1980s when you could write a REST API today?

The answer is commercial, not technical. A retail chain works with thousands of
suppliers. Rather than negotiating a separate API with each one, it imposes a
single standard: "send us an EDIFACT ORDERS". The standard shifts the cost of
adapting from the chain to the supplier — and for the supplier it is still
cheaper than writing a bespoke integration per customer.

## The real issue: the N×M problem

Say there are 500 suppliers and 20 chains. If everyone spoke their own API, you
would in theory need 10,000 separate integrations. A shared standard reduces
that to 520: each party learns the standard once.

That is the problem EDI actually solves, and it has nothing to do with
technology. Change the format and the problem remains; modern networks such as
Peppol work on the same logic, only with a different syntax.

## Who uses it?

- **Retail chains** — almost the entire order and invoice flow. If you want to
  supply a supermarket, EDI is often a contractual requirement.
- **Automotive** — feeding the production line and just-in-time delivery calls.
  Here a delay means the line stops.
- **Logistics** — shipping instructions, transport status reports, customs
  documents.
- **Healthcare and the public sector** — particularly tendering and invoicing in
  Europe.

For most people the first encounter looks the same: a specification from a
customer with a sample file attached.

## What does an EDI message look like?

These four lines are the beginning of a purchase order:

```
UNB+UNOC:3+8712345678901:14+8798765432109:14+260117:1030+REF00042'
UNH+ME000001+ORDERS:D:96A:UN:EAN008'
BGM+220+PO-2026-0042+9'
NAD+BY+8798765432109::9++MEGA RETAIL AS+Barbaros Bulvari 12+ISTANBUL+34353+TR'
```

It looks impenetrable, but the logic is simple. Each line is a **segment**, and
the three letters at the start say what that segment is about:

| Segment | Meaning |
|---|---|
| `UNB` | Interchange header: from whom, to whom, when |
| `UNH` | Message header: this is an ORDERS, version D.96A |
| `BGM` | Document number: PO-2026-0042 |
| `NAD` | Party details: `BY` means buyer |

Inside a segment, `+` separates data elements, and `:` splits an element into
components where needed. That is the whole structure; the rest is knowing what
each code means.

## So is it really outdated?

The format is old; the logic is not. The problem EDI solves — two independent
systems agreeing on a shared vocabulary — is the same today.

The standard is also remarkably stable. An integration written in 2005 may still
run unchanged. That sentence is rarely spoken in the API world, where version
bumps, removed endpoints and changing authentication schemes are routine work.
In EDI, "if it works, leave it alone" is genuinely possible.

What the format costs you is readability. It is a compact syntax that was never
designed for humans, which is exactly why you need the right tool when
debugging.

## How do EDI and APIs coexist?

In practice they sit side by side. The common arrangement is:

- Internal systems speak JSON among themselves
- A translation layer sits at the boundary to the outside world
- That layer converts outgoing data to EDIFACT and incoming EDIFACT to JSON

EDI usually lives at the edge of the application rather than inside it. This
distinction matters: modelling your business logic on EDI segments hurts in the
long run. Keep your own data model and translate at the boundary.

## Where to start

If an EDI file has landed on your desk, the order of work is:

1. **Make the file readable.** Which message type, which parties, which line
   items? Do this before you touch any integration code.
2. **Ask your partner for their specification.** EDIFACT is broad; every partner
   defines its own subset and mandatory fields in a separate document. The
   standard alone is not enough.
3. **Compare the sample file against the specification.** If a field the spec
   calls mandatory is empty in the sample, that usually means the spec is out of
   date rather than that you are wrong. Asking saves time.
4. **Then write code.** Before writing a parser, make sure you have actually seen
   what the file contains.

A browser-based viewer is enough for the first step: you can see what the
segments mean without uploading the file anywhere.
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
Bir EDI şartnamesinde `ORDERS D.96A UN EAN008` gibi bir satır görürsünüz. Bu dört
parça, dosyanın hangi sözlüğe göre okunacağını söyler. Yanlış sürüm, "geçerli ama
anlaşılmayan" bir dosya demektir.

## Dört parça ne anlatır?

Bilgi `UNH` segmentinin ikinci veri elemanında durur:

```
UNH+ME000001+ORDERS:D:96A:UN:EAN008'
```

| Parça | Değer | Anlamı |
|---|---|---|
| Mesaj tipi | `ORDERS` | Bu bir sipariş |
| Sürüm | `D` | Taslak (draft) dizin ailesi |
| Yayın | `96A` | 1996 yılının A yayını |
| Kuruluş | `UN` | Birleşmiş Milletler (UN/CEFACT) |
| Atama kodu | `EAN008` | Sektör alt kümesi — burada GS1/EAN |

İlk üçü standardı, sonuncusu ise **kimin alt kümesini** kullandığınızı belirler.

## Neden hâlâ 1996?

D.96A, EDIFACT'in en yaygın kullanılan yayınıdır. Daha yeni yayınlar var —
D.01B, D.07A ve sonrası — ama perakende dünyası büyük ölçüde 96A'da kaldı.

Sebep atalet değil, ekonomi. Bir yayın yükseltmesi zincirin bütün tedarikçilerini
aynı anda etkiler. Kazanç sınırlıysa kimse binlerce iş ortağını yeni bir sürüme
taşımak istemez. Çalışan bir standardı değiştirmenin maliyeti, yeni alanların
faydasından büyüktür.

Bu yüzden "eski sürüm kullanıyoruz" cümlesi EDI'de bir kusur değil, çoğu zaman
bilinçli bir tercihtir.

## Asıl belirleyici: atama kodu

Şartnameyi okurken en çok gözden kaçan parça sonuncusudur. `EAN008`, `EAN009`,
`ETEB01` gibi kodlar, standardın hangi **sektörel alt kümesinin** geçerli
olduğunu söyler.

Alt küme şunları belirler:

- Hangi segmentlerin kullanıldığı — standarttaki her segment kullanılmaz
- Hangi alanların zorunlu olduğu
- Kod listelerinin hangi değerlerle sınırlandığı

Yani `ORDERS D.96A` iki farklı ortakta farklı görünebilir. Standart aynıdır, alt
küme farklıdır. Şartname olmadan yalnızca sürüme bakarak entegrasyon yazmak,
işin en sık tekrarlanan hatasıdır.

## Sürüm uyuşmazlığı nasıl fark edilir?

Genellikle dosya reddedilmez, **yanlış yorumlanır**. Belirtiler:

- Beklediğiniz bir alan boş geliyor — o alan sizin sürümünüzde başka bir konumda
- Bir kod listesi değeri tanınmıyor — yeni yayında eklenmiş bir kod
- Segment sırası şartnameyle uyuşmuyor — gruplama kuralları yayınlar arasında
  değişebilir

Gelen dosyanın `UNH` satırına bakmak bu soruların çoğunu bir bakışta cevaplar.

## Hangi sürümü kullanmalısınız?

Bu size ait bir karar değil. **Ticari ortağınız ne diyorsa o.** Sipariş
gönderen taraf sürümü belirler; siz uyarsınız.

İki ortak farklı sürüm istiyorsa iki ayrı eşleme (mapping) yazmanız gerekir. Bu
normaldir; EDI entegrasyonlarının çoğu ortak başına ayrı yapılandırma taşır.

## Pratikte ne yapmalı

1. Gelen dosyanın `UNH` satırındaki dört parçayı not edin
2. Şartnamedeki değerle karşılaştırın — özellikle atama kodunu
3. Uyuşmazlık varsa kod yazmadan önce ortağınıza sorun

Elinizdeki dosyanın hangi sürümü kullandığını görmek için dosyayı bir
görüntüleyicide açmak yeterli; `UNH` genellikle ikinci satırdır.
""",
        },
        'en': {
            'title': 'What does D.96A mean? Understanding EDIFACT versions',
            'summary': 'Every part of "D:96A:UN" in the UNH line, and why the version matters.',
            'body': """
An EDI specification will show you a line like `ORDERS D.96A UN EAN008`. Those
four parts say which dictionary the file should be read against. The wrong
version means a file that is valid but misunderstood.

## What do the four parts say?

The information sits in the second data element of the `UNH` segment:

```
UNH+ME000001+ORDERS:D:96A:UN:EAN008'
```

| Part | Value | Meaning |
|---|---|---|
| Message type | `ORDERS` | This is a purchase order |
| Version | `D` | The draft directory family |
| Release | `96A` | Release A of 1996 |
| Agency | `UN` | The United Nations (UN/CEFACT) |
| Association code | `EAN008` | An industry subset — here GS1/EAN |

The first three identify the standard; the last identifies **whose subset** you
are using.

## Why is it still 1996?

D.96A is the most widely used EDIFACT release. Newer ones exist — D.01B, D.07A
and later — but the retail world largely stayed on 96A.

The reason is economics, not inertia. Upgrading a release affects every supplier
of a chain at once. Where the gain is limited, nobody wants to move thousands of
trading partners to a new version. The cost of changing a working standard
outweighs the benefit of the new fields.

So "we are on an old release" is rarely a defect in EDI; more often it is a
deliberate choice.

## The part that really decides: the association code

The most commonly overlooked part of the line is the last one. Codes such as
`EAN008`, `EAN009` or `ETEB01` say which **industry subset** of the standard
applies.

The subset determines:

- Which segments are used — not every segment in the standard is
- Which fields are mandatory
- Which values the code lists are restricted to

So `ORDERS D.96A` can look different at two different partners. The standard is
the same; the subset is not. Writing an integration from the version alone,
without the specification, is the single most repeated mistake in this work.

## How does a version mismatch show up?

Usually the file is not rejected — it is **misread**. The symptoms:

- A field you expected arrives empty, because in your release it sits elsewhere
- A code list value is not recognised, because it was added in a later release
- Segment order does not match the specification, because grouping rules can
  change between releases

Looking at the `UNH` line of the incoming file answers most of these at a glance.

## Which version should you use?

That is not your decision. **Whatever your trading partner says.** The party
sending the order sets the version; you follow it.

If two partners want different versions, you need two mappings. This is normal;
most EDI integrations carry per-partner configuration.

## What to do in practice

1. Note the four parts on the `UNH` line of the incoming file
2. Compare them with the values in the specification, the association code above all
3. If they differ, ask your partner before writing any code

To see which version a file uses, opening it in a viewer is enough; `UNH` is
usually the second line.
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
EDIFACT dosyalarının çoğu `+` ile eleman, `:` ile alt eleman ve `'` ile satır
ayırır. Ama bu bir zorunluluk değil, yalnızca varsayılan. Dosyanın başındaki
`UNA` segmenti bu karakterleri değiştirebilir.

## UNA neye benzer?

Varsayılan hâli şudur:

```
UNA:+.? '
```

`UNA`'dan sonraki **altı karakter** sırasıyla şunları tanımlar:

| Konum | Varsayılan | Görevi |
|---|---|---|
| 1 | `:` | Alt eleman (bileşen) ayırıcı |
| 2 | `+` | Veri elemanı ayırıcı |
| 3 | `.` | Ondalık işareti |
| 4 | `?` | Kaçış (release) karakteri |
| 5 | boşluk | Ayrılmış / tekrar ayırıcı |
| 6 | `'` | Segment sonlandırıcı |

Altıncı karakterin boşluk olmadığına dikkat edin — `'` işaretidir ve hemen
ardından ilk gerçek segment gelir.

## Neden değiştirilir?

Çünkü veri içinde o karakter geçiyordur. Bir ürün açıklamasında `+` varsa,
ayırıcı olarak `+` kullanan bir dosyada bu karakter satırı yanlış yerden böler.
İki çözüm vardır: kaçış karakteri kullanmak ya da ayırıcıyı değiştirmek.

Farklı ayırıcılı bir dosya şuna benzer:

```
UNA|^.! ~UNB^UNOC|3^A|14^B|14^260117|1030^R1~
```

Burada `^` eleman, `|` alt eleman, `~` segment sonu. Gözle okunması alışılmadık
görünür ama yapı birebir aynıdır.

## Kaçış karakteri nasıl çalışır?

Ayırıcıyı değiştirmek yerine tek tek kaçırmak da mümkündür. Varsayılan kaçış
karakteri `?` şunu yapar: kendisinden sonraki karakteri **veri** hâline getirir.

```
FTX+AAI+++ACME?+SONS ?: 50?? indirim'
```

Bu satırın çözülmüş hâli şudur:

- `?+` → `+` (ayırıcı değil, veri)
- `?:` → `:` (ayırıcı değil, veri)
- `??` → `?` (kaçış karakterinin kendisi)

Yani metin aslında `ACME+SONS : 50? indirim` demektir. Kaçış karakterini
görmezden gelen bir ayrıştırıcı bu satırı yanlış böler ve genellikle hatayı çok
sonra, alan sayısı tutmadığında fark eder.

## UNA yoksa ne olur?

Varsayılanlar geçerlidir. `UNA` isteğe bağlıdır; dosya doğrudan `UNB` ile de
başlayabilir. Bu tamamen geçerli bir dosyadır.

Dolayısıyla bir ayrıştırıcının yapması gereken şudur: dosyanın başında `UNA`
varsa oradan oku, yoksa varsayılanları kullan.

## Sık yapılan hata

Ayırıcıları koda gömmek. `split('+')` yazan bir kod, `UNA` kullanan bir dosyada
sessizce yanlış sonuç üretir — çökmez, sadece yanlış okur. Bu tür hatalar
üretimde uzun süre fark edilmeden yaşayabilir.

Aynı şey ANSI X12 tarafında da geçerlidir, ama orada mekanizma farklıdır:
ayırıcılar `UNA` gibi bir segmentte değil, `ISA` satırının **sabit
konumlarında** durur. Eleman ayırıcı 4. karakter, alt eleman ayırıcı 105.,
segment sonlandırıcı 106. karakterdir. Bu yüzden `ISA` satırındaki boşluk
dolgusu süs değildir; kısaltılırsa dosya ayrıştırılamaz.

## Kontrol listesi

- Dosya `UNA` ile mi başlıyor? Öyleyse ayırıcıları oradan alın
- Ayrıştırıcınız kaçış karakterini tanıyor mu?
- X12 tarafında `ISA` satırı tam 106 karakter mi?

Bir dosyanın hangi ayırıcıları kullandığını anlamanın en hızlı yolu, ilk satıra
bakmaktır.
""",
        },
        'en': {
            'title': 'The UNA segment: delimiters are not always the same',
            'summary': 'If a file opens with UNA, forget the defaults — that line says which '
                       'character does what.',
            'body': """
Most EDIFACT files separate elements with `+`, components with `:` and segments
with `'`. But that is only the default, not a rule. The `UNA` segment at the
start of a file can change those characters.

## What does UNA look like?

In its default form:

```
UNA:+.? '
```

The **six characters** after `UNA` define, in order:

| Position | Default | Purpose |
|---|---|---|
| 1 | `:` | Component (sub-element) separator |
| 2 | `+` | Data element separator |
| 3 | `.` | Decimal mark |
| 4 | `?` | Release (escape) character |
| 5 | space | Reserved / repetition separator |
| 6 | `'` | Segment terminator |

Note that the sixth character is not a space — it is `'`, and the first real
segment follows immediately after it.

## Why would anyone change them?

Because the data contains that character. If a product description contains a
`+`, then in a file using `+` as a separator that character splits the line in
the wrong place. There are two ways out: escape it, or change the separator.

A file with different separators looks like this:

```
UNA|^.! ~UNB^UNOC|3^A|14^B|14^260117|1030^R1~
```

Here `^` separates elements, `|` components and `~` segments. It reads oddly, but
the structure is identical.

## How does the release character work?

Instead of changing the separator you can escape occurrences one by one. The
default release character `?` makes the character that follows it **data**.

```
FTX+AAI+++ACME?+SONS ?: 50?? discount'
```

Decoded, that line reads:

- `?+` → `+` (data, not a separator)
- `?:` → `:` (data, not a separator)
- `??` → `?` (the release character itself)

So the text is actually `ACME+SONS : 50? discount`. A parser that ignores the
release character splits this line incorrectly and usually notices only much
later, when the field count does not add up.

## What if there is no UNA?

The defaults apply. `UNA` is optional; a file may start directly with `UNB`, and
that is perfectly valid.

So a parser should do this: if the file starts with `UNA`, read the separators
from it; otherwise use the defaults.

## The common mistake

Hard-coding the separators. Code that calls `split('+')` will quietly produce
wrong results on a file that uses `UNA` — it does not crash, it just misreads.
Faults of this kind can live in production unnoticed for a long time.

The same concern applies to ANSI X12, but the mechanism differs: there the
separators are not in a segment like `UNA` but at **fixed positions** in the
`ISA` line. The element separator is character 4, the component separator 105 and
the segment terminator 106. This is why the space padding in an `ISA` line is not
decoration; shorten it and the file can no longer be parsed.

## Checklist

- Does the file start with `UNA`? If so, take the separators from it
- Does your parser understand the release character?
- On the X12 side, is the `ISA` line exactly 106 characters?

The quickest way to find out which separators a file uses is to look at its
first line.
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
Bir EDI dosyasında birden fazla `DTM` satırı görürsünüz ve hepsi tarih taşır.
Hangisinin belge tarihi, hangisinin teslim tarihi olduğunu söyleyen şey satırın
kendisi değil, içindeki **nitelikçi koddur**.

## Yapısı

```
DTM+137:20260117:102'
```

Üç parça vardır:

| Parça | Değer | Anlamı |
|---|---|---|
| Nitelikçi | `137` | Bu bir belge tarihi |
| Değer | `20260117` | 17 Ocak 2026 |
| Format | `102` | `YYYYMMDD` biçiminde |

Nitelikçiyi okumadan tarihi kullanmak, EDI'de en sık yapılan hatalardan biridir.

## Sık karşılaşılan nitelikçiler

| Kod | Anlamı |
|---|---|
| `137` | Belge / mesaj tarihi |
| `2` | İstenen teslim tarihi |
| `35` | Fiili teslim tarihi |
| `11` | Sevk (despatch) tarihi |
| `132` | Tahmini varış |
| `203` | Ödeme tarihi |
| `263` | Fatura dönemi |
| `356` | Dönem başlangıcı |
| `357` | Dönem bitişi |

`137` neredeyse her mesajda bulunur; diğerleri mesaj tipine göre değişir. Bir
siparişte `2` (istenen teslim), bir irsaliyede `11` (sevk), bir satış raporunda
`356`/`357` (dönem) görürsünüz.

## Format kodu neden önemli?

Üçüncü parça tarihin nasıl yazıldığını söyler. En yaygın ikisi:

| Kod | Biçim | Örnek |
|---|---|---|
| `102` | `YYYYMMDD` | `20260117` |
| `203` | `YYYYMMDDHHMM` | `202601171430` |

Daha eski dosyalarda `101` (`YYMMDD`) de görülür. İki haneli yıl, 2000 öncesi
kalıntısıdır ve yüzyılı tahmin etmeyi gerektirir — mümkünse kaçının.

Format kodunu yok sayıp uzunluğa göre tahmin yürüten kodlar bir süre çalışır,
sonra saat bilgisi taşıyan bir dosyada bozulur.

## UNB'deki tarih farklıdır

Zarf başlığındaki tarih bu kalıba uymaz:

```
UNB+UNOC:3+A:14+B:14+260117:1030+REF00042'
```

Buradaki `260117:1030`, `YYMMDD:HHMM` biçimindedir ve nitelikçisi yoktur — her
zaman aktarımın gönderilme zamanıdır. Yani `UNB` tarihini `DTM` mantığıyla
okumaya çalışmak sonuç vermez.

## Zaman dilimi meselesi

EDIFACT tarihleri varsayılan olarak zaman dilimi taşımaz. `202601171430` hangi
saat diliminde 14:30? Standart bunu söylemez; şartname söyler.

Pratikte iki yaklaşım vardır: ya her iki taraf yerel saati kullanır ve bunu
sözleşmede sabitler, ya da `DTM` yanında ayrı bir zaman dilimi göstergesi
taşınır. Uluslararası akışlarda bu ayrımı atlamak, teslim tarihlerinin bir gün
kaymasına yol açabilir.

## Aynı nitelikçi birden fazla geçerse

Bu geçerlidir ve anlamı konuma bağlıdır. Mesaj başlığında geçen bir `DTM`,
belgenin tamamı için geçerlidir; bir `LIN` (kalem) segmentinden sonra geçen aynı
kod yalnızca o kalem için geçerlidir.

```
DTM+2:20260125:102'      <- tum siparis icin istenen teslim
LIN+1++5410013101234:EN'
DTM+2:20260130:102'      <- yalnizca bu kalem icin
```

Kalem düzeyindeki tarih, başlıktakini o kalem için **ezer**. Bu kuralı atlayan
eşlemeler, kısmi teslimatlarda yanlış tarih üretir.

## Kontrol listesi

1. Nitelikçiyi okuyun, konumdan tahmin etmeyin
2. Format kodunu kullanın, uzunluğa bakarak tahmin etmeyin
3. `UNB` tarihini ayrı ele alın
4. Kalem düzeyindeki `DTM`'in başlıktakini ezdiğini unutmayın

Bir dosyadaki tarihlerin hangisinin ne olduğunu görmek için, satırı seçtiğinizde
nitelikçiyi çözen bir görüntüleyici en hızlı yoldur.
""",
        },
        'en': {
            'title': 'DTM: which date is which?',
            'summary': 'A message can hold five different DTMs. The qualifier says which one '
                       'is delivery and which is the document date.',
            'body': """
An EDI file contains several `DTM` lines and all of them carry dates. What tells
you which is the document date and which is the delivery date is not the line
itself but the **qualifier** inside it.

## The structure

```
DTM+137:20260117:102'
```

There are three parts:

| Part | Value | Meaning |
|---|---|---|
| Qualifier | `137` | This is a document date |
| Value | `20260117` | 17 January 2026 |
| Format | `102` | In `YYYYMMDD` form |

Using a date without reading its qualifier is one of the most common mistakes in
EDI.

## Qualifiers you will meet

| Code | Meaning |
|---|---|
| `137` | Document / message date |
| `2` | Requested delivery date |
| `35` | Actual delivery date |
| `11` | Despatch date |
| `132` | Estimated arrival |
| `203` | Payment date |
| `263` | Invoicing period |
| `356` | Period start |
| `357` | Period end |

`137` appears in almost every message; the others depend on the message type. An
order carries `2` (requested delivery), a despatch advice `11` (despatch), a
sales report `356`/`357` (the period).

## Why the format code matters

The third part says how the date is written. The two most common:

| Code | Format | Example |
|---|---|---|
| `102` | `YYYYMMDD` | `20260117` |
| `203` | `YYYYMMDDHHMM` | `202601171430` |

Older files may also use `101` (`YYMMDD`). The two-digit year is a pre-2000
leftover and forces you to guess the century — avoid it where you can.

Code that ignores the format and guesses from the length works for a while, then
breaks on the first file that carries a time.

## The date in UNB is different

The date in the interchange header does not follow this pattern:

```
UNB+UNOC:3+A:14+B:14+260117:1030+REF00042'
```

Here `260117:1030` is in `YYMMDD:HHMM` form and has no qualifier — it is always
the moment the interchange was sent. Trying to read the `UNB` date with `DTM`
logic will not work.

## The time zone question

EDIFACT dates carry no time zone by default. In which zone is `202601171430`
14:30? The standard does not say; the specification does.

In practice there are two approaches: either both sides use local time and fix
that in the agreement, or a separate time zone indicator travels alongside the
`DTM`. In cross-border flows, skipping this distinction can shift delivery dates
by a day.

## When the same qualifier appears twice

That is valid, and the meaning depends on position. A `DTM` in the message header
applies to the whole document; the same code after a `LIN` (line item) segment
applies only to that item.

```
DTM+2:20260125:102'      <- requested delivery for the whole order
LIN+1++5410013101234:EN'
DTM+2:20260130:102'      <- for this line item only
```

The line-level date **overrides** the header for that item. Mappings that skip
this rule produce wrong dates on partial deliveries.

## Checklist

1. Read the qualifier; do not infer meaning from position
2. Use the format code; do not guess from the length
3. Treat the `UNB` date separately
4. Remember that a line-level `DTM` overrides the header

To see which date is which in a file, the quickest route is a viewer that
decodes the qualifier when you select the line.
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
`QTY` segmenti bir miktar taşır. Ama "480" tek başına bir şey ifade etmez: 480
adet mi, 480 koli mi, 480 kilogram mı? Cevap segmentin diğer iki parçasındadır.

## Yapısı

```
QTY+21:480:PCE'
```

| Parça | Değer | Anlamı |
|---|---|---|
| Nitelikçi | `21` | Bu sipariş edilen miktardır |
| Değer | `480` | Miktarın kendisi |
| Birim | `PCE` | Adet (piece) |

Üçünü birlikte okumadan miktarı kullanmak, envanterde ciddi hatalara yol açar.

## Nitelikçi: hangi miktar?

Aynı dosyada birden fazla `QTY` bulunabilir ve her biri farklı bir soruyu
cevaplar:

| Kod | Anlamı |
|---|---|
| `21` | Sipariş edilen miktar |
| `12` | Sevk edilen miktar |
| `47` | Faturalanan miktar |
| `194` | Teslim alınan miktar |
| `152` | Satılan miktar (satış raporunda) |
| `59` | Ambalaj içindeki adet |

Bir sipariş zincirinde bu kodlar birbirini takip eder: `21` istenir, `12` sevk
edilir, `194` kabul edilir, `47` faturalanır. Aralarındaki fark, çoğu ticari
anlaşmazlığın başladığı yerdir.

Örneğin bir mal kabul mesajında iki satır yan yana durur:

```
QTY+12:100:PCE'
QTY+194:96:PCE'
```

Yüz adet sevk edilmiş, doksan altısı kabul edilmiş. Aradaki dört adetlik fark,
hasar veya eksik gönderim demektir ve genellikle bir `FTX` satırında açıklanır.

## Birim kodları

Birimler UN/ECE Recommendation 20 listesinden gelir. Sık kullanılanlar:

| Kod | Anlamı |
|---|---|
| `PCE` | Adet |
| `KGM` | Kilogram |
| `LTR` | Litre |
| `MTR` | Metre |
| `CT` | Karton / koli |
| `PA` | Paket |
| `CS` | Kasa |

Dikkat edilmesi gereken nokta: aynı ürün farklı satırlarda farklı birimle
görünebilir. Sipariş `CT` (koli) cinsinden verilip fatura `PCE` (adet) cinsinden
kesilebilir. Dönüşüm oranı ürün ana verisinde durur, EDI dosyasında değil.

## Ondalık ayırıcı tuzağı

Miktar ondalıklıysa hangi karakterin ondalık işareti olduğunu `UNA` segmenti
söyler. Varsayılan `.` işaretidir:

```
QTY+21:12.5:KGM'
```

Ama `UNA` üçüncü karakteri `,` yapmışsa dosyada `12,5` yazar. Ondalık işaretini
sabit varsayan kod, virgüllü bir dosyada ya çöker ya da sayıyı yanlış okur.

Ayrıca EDIFACT'te binlik ayırıcı **kullanılmaz**. `1.234` bin iki yüz otuz dört
değil, bir tam iki yüz otuz dört binde demektir.

## Eksi miktarlar

Bir miktar negatif olabilir; iade ve düzeltme belgelerinde bu normaldir:

```
QTY+21:-12:PCE'
```

Eksi işareti değerin başına gelir. Miktarı işaretsiz bir tam sayı olarak
saklayan sistemler burada sessizce yanlış kayıt üretir.

## Kontrol listesi

1. Nitelikçiyi okuyun — `21` ile `12` çok farklı şeylerdir
2. Birimi taşıyın; miktarı birimden ayırmayın
3. Ondalık işaretini `UNA`'dan alın
4. Negatif değerlere izin verin

Bir dosyadaki miktarların hangisinin ne olduğunu görmek için, nitelikçiyi ve
birim kodunu açık metne çeviren bir görüntüleyici en hızlı yoldur.
""",
        },
        'en': {
            'title': 'Quantity and unit: what a QTY segment says',
            'summary': 'Ordered, despatched or received? And what happens when PCE and KGM get '
                       'mixed up.',
            'body': """
The `QTY` segment carries a quantity. But "480" on its own means nothing: 480
pieces, 480 cartons, or 480 kilograms? The answer is in the segment's other two
parts.

## The structure

```
QTY+21:480:PCE'
```

| Part | Value | Meaning |
|---|---|---|
| Qualifier | `21` | This is the ordered quantity |
| Value | `480` | The quantity itself |
| Unit | `PCE` | Pieces |

Using the quantity without reading all three leads to real inventory errors.

## The qualifier: which quantity?

A file can contain several `QTY` segments, each answering a different question:

| Code | Meaning |
|---|---|
| `21` | Ordered quantity |
| `12` | Despatched quantity |
| `47` | Invoiced quantity |
| `194` | Received quantity |
| `152` | Quantity sold (in a sales report) |
| `59` | Number of units per pack |

Along an order chain these codes follow one another: `21` is ordered, `12` is
despatched, `194` is received, `47` is invoiced. The differences between them are
where most commercial disputes begin.

In a receiving advice, for instance, two lines sit side by side:

```
QTY+12:100:PCE'
QTY+194:96:PCE'
```

One hundred were despatched, ninety-six accepted. The gap of four means damage or
a short delivery, and is usually explained in an `FTX` line.

## Unit codes

Units come from UN/ECE Recommendation 20. The common ones:

| Code | Meaning |
|---|---|
| `PCE` | Piece |
| `KGM` | Kilogram |
| `LTR` | Litre |
| `MTR` | Metre |
| `CT` | Carton |
| `PA` | Pack |
| `CS` | Case |

One thing to watch: the same product can appear in different units on different
lines. An order may be placed in `CT` (cartons) and invoiced in `PCE` (pieces).
The conversion factor lives in your product master data, not in the EDI file.

## The decimal separator trap

If a quantity has decimals, the `UNA` segment says which character is the decimal
mark. The default is `.`:

```
QTY+21:12.5:KGM'
```

But if `UNA` set the third character to `,`, the file will contain `12,5`. Code
that assumes a fixed decimal mark will either crash or misread the number.

EDIFACT also uses **no thousands separator**. `1.234` is not one thousand two
hundred and thirty-four; it is one point two three four.

## Negative quantities

A quantity can be negative, which is normal on returns and correction documents:

```
QTY+21:-12:PCE'
```

The minus sign precedes the value. Systems that store quantities as unsigned
integers silently record the wrong figure here.

## Checklist

1. Read the qualifier — `21` and `12` are very different things
2. Carry the unit with the value; never separate them
3. Take the decimal mark from `UNA`
4. Allow negative values

To see what each quantity in a file means, the quickest route is a viewer that
translates the qualifier and unit code into plain text.
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
INVOIC, EDI mesajları arasında en çok reddedileni. Sebebi genellikle karmaşık
değil: birkaç alan yanlış, bir toplam tutmuyor ya da bir referans eksik. Aşağıda
en sık karşılaşılan nedenler sırayla.

## 1. Toplamlar tutmuyor

En yaygın neden bu. Özet bölümündeki `MOA` nitelikçileri karıştırılır:

| Kod | Anlamı |
|---|---|
| `79` | Mal toplamı (vergi hariç) |
| `124` | Vergi tutarı |
| `77` | Genel toplam (vergi dahil) |
| `9` | Ödenecek tutar |

Kural basittir: `79 + 124 = 77` olmalıdır. Alıcı sistem bunu aritmetik olarak
doğrular ve tutmuyorsa faturayı işleme almaz.

```
MOA+79:1228.00'
MOA+124:245.60'
MOA+77:1473.60'
```

Ayrıca kalem düzeyindeki `MOA+203` değerlerinin toplamı `79`'a eşit olmalıdır.
Yuvarlama farkları burada sorun çıkarır: her kalemi ayrı yuvarlayıp topladığınızda
tek seferde yuvarlamaktan farklı sonuç çıkabilir.

## 2. Sipariş referansı eksik veya yanlış

Alıcı sistem genellikle **üçlü eşleştirme** yapar: sipariş (ORDERS), mal kabul
(RECADV) ve fatura birbirini tutmalıdır. Bunu yapabilmesi için faturanın sipariş
numarasını taşıması gerekir:

```
RFF+ON:PO-2026-0042'
```

`ON` nitelikçisi "order number" demektir. Bu satır yoksa ya da numara alıcının
sistemindekiyle birebir aynı değilse eşleştirme başarısız olur. Baştaki sıfırlar
ve boşluklar önemlidir; `PO-42` ile `PO-0042` farklı numaralardır.

## 3. Miktar sevk edilenle uyuşmuyor

Fatura, **sevk edilen** miktarı faturalamalıdır, sipariş edileni değil. Kısmi
teslimat yapıldıysa fark buradan çıkar:

- Sipariş: 120 adet (`QTY+21`)
- Sevk edilen: 100 adet (`QTY+12`)
- Faturalanması gereken: 100 adet (`QTY+47`)

120 üzerinden kesilen bir fatura reddedilir. Bu, otomatik kontrollerin en
kolay yakaladığı hatadır.

## 4. Vergi bilgisi eksik

`TAX` segmenti oranı ve türü taşır:

```
TAX+7+VAT+++:::20'
```

Buradaki `7` "vergi" anlamına gelen nitelikçi, `VAT` vergi türü, sondaki `20`
ise yüzde oranıdır. Oran yazılmazsa ya da kalem düzeyindeki oranlarla özet
bölümündeki vergi tutarı çelişirse fatura geri döner.

Farklı vergi oranlı kalemler varsa her oran için ayrı vergi alt toplamı
gerekebilir; bu, şartnameye göre değişir.

## 5. GLN eşleşmiyor

Taraflar isimle değil, **GLN numarasıyla** tanınır:

```
NAD+SE+8712345678901::9++ACME FOODS BV+...'
```

Alıcının sisteminde kayıtlı olmayan bir GLN, faturanın hangi tedarikçiye ait
olduğunun anlaşılamaması demektir. Firma adının doğru yazılması bu durumu
kurtarmaz — eşleştirme numara üzerinden yapılır.

Sık karşılaşılan bir varyant: fatura kesen tüzel kişi (`SE`) ile malı gönderen
depo (`SU`) farklıdır ve şartname hangisinin nerede olacağını belirtir.

## 6. Para birimi belirtilmemiş

`CUX` segmenti yoksa alıcı sistem tutarları hangi para biriminde okuyacağını
bilemez:

```
CUX+2:EUR:9'
```

Tek para birimiyle çalışan ortaklarda bu bazen atlanır ve varsayılan kabul
edilir; ama şartname istiyorsa zorunludur.

## Reddedilince ne yapmalı

1. Varsa `CONTRL` mesajına bakın — sözdizimi hatasıysa satır numarasını verir
2. Sözdizimi geçerliyse hata iş kuralındadır: önce toplamları, sonra
   referansları kontrol edin
3. Faturayı ve ilgili siparişi yan yana açıp kalem kalem karşılaştırın

Bu karşılaştırmayı yapmanın en hızlı yolu, iki dosyayı da açıp `MOA`, `QTY` ve
`RFF` satırlarını okunur biçimde görmektir.
""",
        },
        'en': {
            'title': 'Why was my invoice rejected? An INVOIC checklist',
            'summary': 'EDI invoices usually come back for matching and totalling errors, not '
                       'for their content.',
            'body': """
INVOIC is the most frequently rejected EDI message. The reason is usually not
complicated: a few wrong fields, a total that does not add up, or a missing
reference. Here are the most common causes, in order.

## 1. The totals do not add up

This is the leading cause. The `MOA` qualifiers in the summary section get mixed
up:

| Code | Meaning |
|---|---|
| `79` | Goods total (excluding tax) |
| `124` | Tax amount |
| `77` | Grand total (including tax) |
| `9` | Amount payable |

The rule is simple: `79 + 124 = 77`. The receiving system checks this
arithmetically and will not process an invoice where it fails.

```
MOA+79:1228.00'
MOA+124:245.60'
MOA+77:1473.60'
```

The line-level `MOA+203` values must also sum to `79`. Rounding differences bite
here: rounding each line separately and then adding can give a different result
from rounding once.

## 2. Missing or wrong order reference

The receiving system usually performs a **three-way match**: the order (ORDERS),
the goods receipt (RECADV) and the invoice must agree. For that, the invoice has
to carry the order number:

```
RFF+ON:PO-2026-0042'
```

The `ON` qualifier means "order number". If that line is absent, or the number is
not character-for-character what the buyer has on file, the match fails. Leading
zeros and spaces matter; `PO-42` and `PO-0042` are different numbers.

## 3. Quantity does not match what was despatched

An invoice should bill the **despatched** quantity, not the ordered one. On a
partial delivery the difference shows up here:

- Ordered: 120 pieces (`QTY+21`)
- Despatched: 100 pieces (`QTY+12`)
- To be invoiced: 100 pieces (`QTY+47`)

An invoice raised for 120 will be rejected. This is the easiest error for
automated checks to catch.

## 4. Missing tax information

The `TAX` segment carries the rate and the type:

```
TAX+7+VAT+++:::20'
```

Here `7` is the qualifier meaning "tax", `VAT` is the tax type, and the trailing
`20` is the percentage. If the rate is absent, or the line-level rates contradict
the tax amount in the summary, the invoice comes back.

Where line items carry different rates, a separate tax subtotal per rate may be
required; this depends on the specification.

## 5. The GLN does not match

Parties are identified by **GLN number**, not by name:

```
NAD+SE+8712345678901::9++ACME FOODS BV+...'
```

A GLN that is not registered in the buyer's system means the invoice cannot be
attributed to a supplier. Spelling the company name correctly does not rescue
this — the match runs on the number.

A common variant: the legal entity raising the invoice (`SE`) differs from the
warehouse that shipped the goods (`SU`), and the specification says which belongs
where.

## 6. No currency stated

Without a `CUX` segment the receiving system does not know which currency the
amounts are in:

```
CUX+2:EUR:9'
```

Partners working in a single currency sometimes omit it and assume a default, but
where the specification requires it, it is mandatory.

## What to do after a rejection

1. Look for a `CONTRL` message — if it is a syntax error, it gives you the
   segment number
2. If the syntax is valid, the fault is in a business rule: check the totals
   first, then the references
3. Open the invoice and the related order side by side and compare line by line

The quickest way to make that comparison is to open both files and read the
`MOA`, `QTY` and `RFF` lines in plain language.
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
Elinizde bir EDI dosyası var ve içindeki kalemleri tabloya dökmek istiyorsunuz —
belki muhasebeye göndermek, belki fiyatları kontrol etmek için. EDI satır tabanlı
bir yapı; tabloya çevirmek göründüğünden biraz daha dikkat ister.

## Neden doğrudan açılmıyor?

Bir `.edi` dosyasını Excel'e sürüklerseniz her segment tek bir hücreye düşer.
Sebep, EDI'nin **hiyerarşik** olması: bir kalemin bilgisi tek satırda değil,
birbirini takip eden birkaç satırda durur.

```
LIN+1++5410013101234:EN'
IMD+F++:::BITTER CIKOLATA 100G'
QTY+21:480:PCE'
PRI+AAA:1.85'
MOA+203:888.00'
```

Bu beş satır **tek bir tablo satırıdır**: ürün kodu, açıklama, miktar, fiyat,
tutar. Tabloya çevirmek, `LIN` gördüğünde yeni satır açıp sonraki segmentleri o
satırın sütunlarına yazmak demektir.

## Hangi segment hangi sütun?

Tipik bir sipariş veya fatura için eşleme şudur:

| Segment | Sütun | Nereden |
|---|---|---|
| `LIN` | Ürün kodu (GTIN) | 3. elemanın ilk parçası |
| `IMD` | Ürün açıklaması | 3. elemanın son parçası |
| `QTY` | Miktar ve birim | Nitelikçiye göre `21`, `12` veya `47` |
| `PRI` | Birim fiyat | `AAA` net fiyat |
| `MOA` | Satır tutarı | `203` nitelikçisi |

Nitelikçileri atlamamak önemli: bir kalemde birden fazla `QTY` olabilir ve
hangisini istediğinize siz karar vermelisiniz.

## Dikkat edilecek noktalar

**Kalem sınırını doğru belirleyin.** Yeni bir `LIN` gelene kadar okunan her şey
mevcut kaleme aittir. Özet bölümü (`UNS`'den sonrası) kaleme ait değildir; oradaki
`MOA+79` satırını kalem tutarı sanmak sık yapılan bir hatadır.

**Başlık bilgisini ayrı tutun.** Sipariş numarası, tarih ve taraf bilgisi kalem
düzeyinde değil belge düzeyindedir. Bunları her satıra kopyalamak isterseniz
tabloyu düzleştirmiş olursunuz — bu genellikle istenen şeydir ama bilinçli bir
tercih olmalıdır.

**Ondalık işaretini koruyun.** Excel'in bölgesel ayarı virgül bekliyorsa,
noktayla yazılmış `1.85` metin olarak algılanabilir ve toplama işlemleri
çalışmaz. CSV oluştururken hedef sistemin ayarını düşünün.

**Baştaki sıfırları kaybetmeyin.** GTIN gibi kodlar sayı değil metindir.
`05410013101234` Excel'de sayıya dönüşürse baştaki sıfır silinir ve kod artık
eşleşmez. Sütunu metin olarak biçimlendirmek gerekir.

## Her dosya tabloya uygun mu?

Hayır. Kalem listesi taşıyan mesajlar (sipariş, fatura, satış raporu, fiyat
kataloğu) doğal olarak tabloya oturur. Ama bir `CONTRL` teyit mesajını ya da bir
nakliye talimatını tabloya çevirmek pek anlamlı olmaz; onların yapısı liste
değildir.

Satış raporu (SLSRPT) ve fiyat kataloğu (PRICAT) bu iş için en uygun ikisidir:
ikisi de doğrudan "ürün başına bir satır" mantığıyla çalışır.

## Pratik yol

Kendiniz ayrıştırıcı yazmadan önce, dosyayı bir görüntüleyicide açıp doğrudan
CSV'ye aktarmayı deneyin. Hangi sütunların çıktığını görmek, kendi eşlemenizi
yazarken neye ihtiyacınız olduğunu da netleştirir.

Dosyanızı hiçbir yere yüklemeden bunu yapabilirsiniz; dönüşüm tarayıcının içinde
çalışabilir ve ticari veriniz cihazınızdan çıkmaz.
""",
        },
        'en': {
            'title': 'Exporting an EDI file to Excel',
            'summary': 'What to watch for when flattening a segment structure into rows and '
                       'columns.',
            'body': """
You have an EDI file and you want its line items in a spreadsheet — perhaps to
send to accounting, perhaps to check prices. EDI is a line-based structure, and
turning it into a table takes a little more care than it appears.

## Why does it not just open?

Drag a `.edi` file into Excel and every segment lands in a single cell. The reason
is that EDI is **hierarchical**: the information about one item does not sit on
one line but across several consecutive ones.

```
LIN+1++5410013101234:EN'
IMD+F++:::DARK CHOCOLATE BAR 100G'
QTY+21:480:PCE'
PRI+AAA:1.85'
MOA+203:888.00'
```

Those five lines are **one row of a table**: product code, description, quantity,
price, amount. Converting to a table means starting a new row when you see `LIN`
and writing the following segments into that row's columns.

## Which segment becomes which column?

For a typical order or invoice the mapping is:

| Segment | Column | Taken from |
|---|---|---|
| `LIN` | Product code (GTIN) | First component of element 3 |
| `IMD` | Product description | Last component of element 3 |
| `QTY` | Quantity and unit | `21`, `12` or `47` by qualifier |
| `PRI` | Unit price | `AAA` net price |
| `MOA` | Line amount | Qualifier `203` |

Do not skip the qualifiers: an item can carry several `QTY` segments and you have
to decide which one you want.

## Things to watch

**Get the item boundary right.** Everything read until the next `LIN` belongs to
the current item. The summary section (after `UNS`) does not belong to any item;
mistaking its `MOA+79` line for a line amount is a common error.

**Keep header data separate.** The order number, date and party details sit at
document level, not item level. Copying them onto every row flattens the table —
usually what you want, but it should be a deliberate choice.

**Preserve the decimal mark.** If Excel's regional setting expects a comma, a
value written as `1.85` may be read as text and your sums will not work. Consider
the target system's settings when you build the CSV.

**Do not lose leading zeros.** Codes such as GTINs are text, not numbers. If
`05410013101234` is converted to a number in Excel, the leading zero disappears
and the code no longer matches. The column needs to be formatted as text.

## Is every file suited to a table?

No. Messages that carry a list of items — orders, invoices, sales reports, price
catalogues — map naturally onto rows. But turning a `CONTRL` acknowledgement or a
transport instruction into a table makes little sense; their structure is not a
list.

Sales reports (SLSRPT) and price catalogues (PRICAT) are the two best suited:
both work on a "one row per product" basis already.

## A practical route

Before writing your own parser, open the file in a viewer and try exporting it
straight to CSV. Seeing which columns come out also clarifies what you need when
you write your own mapping.

You can do this without uploading the file anywhere; the conversion can run
inside the browser, so your commercial data never leaves your device.
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
Bir zincir market "EDI ile çalışıyoruz" dedi ve şimdi ne kadar tutacağını
bilmiyorsunuz. Rakam vermek zor, ama maliyetin **nereden** çıktığını bilmek
teklifleri karşılaştırmayı kolaylaştırır.

## Maliyet nerede birikiyor?

Dört kalem var ve sıralamaları çoğu zaman şaşırtıcıdır:

| Kalem | Ağırlık |
|---|---|
| Yazılım / abonelik | Genellikle en küçük kalem |
| İlk kurulum ve eşleme | Tek seferlik, ama en büyük kalemlerden |
| Ortak başına ek entegrasyon | Yeni müşteri = yeni iş |
| Bakım ve destek | Sürekli, çoğu zaman hafife alınır |

Asıl para yazılımda değil, **eşlemede** (mapping) durur. Yani gelen EDI
alanlarının sizin sisteminizdeki alanlara nasıl karşılık geldiğini tanımlama
işinde. Bu iş her ortak için kısmen tekrarlanır çünkü her ortağın şartnamesi
farklıdır.

## Üç yaklaşım

**1. EDI servis sağlayıcısı (VAN veya bulut)**

Aylık abonelik ödersiniz, sağlayıcı dönüşümü ve iletimi üstlenir. Genellikle
aktarım hacmine veya ortak sayısına göre fiyatlanır.

- Artısı: hızlı başlarsınız, teknik yük sizde değil
- Eksisi: sürekli gider, hacim arttıkça artar; sağlayıcıya bağımlılık

**2. Kendi entegrasyonunuzu yazmak**

ERP'nize doğrudan bir EDI modülü eklersiniz veya kendiniz geliştirirsiniz.

- Artısı: aylık gider yok, tam kontrol
- Eksisi: geliştirme süresi, ve asıl önemlisi **bakım**. Ortak şartnamesini
  değiştirdiğinde güncellemesi gereken sizsiniz.

**3. Elle işlemek**

Dosyayı açıp bakmak, veriyi elle sisteme girmek. Kulağa ilkel gelir ama ayda
birkaç sipariş alan bir tedarikçi için gerçekten mantıklı olabilir.

- Artısı: sıfır kurulum maliyeti
- Eksisi: hacim arttığında hata oranı ve zaman maliyeti hızla büyür

## Hangi eşik nerede?

Kaba bir sağduyu ölçüsü:

- **Ayda 10'un altında belge** — elle işlemek çoğu zaman en ucuzu. Otomasyonun
  kurulum maliyetini çıkarmaz.
- **Ayda 10–100 arası** — yarı otomatik çözümler mantıklı: dosyayı okuyup
  tabloya çevirip sisteme aktarmak.
- **Ayda 100'ün üstü veya birden fazla ortak** — tam otomasyon kendini öder.

Bu eşikler sektöre göre kayar. Otomotivde tek bir gecikmiş teslimat bandı
durdurabileceği için hacim düşük olsa da otomasyon zorunlu olabilir.

## Sık yapılan hata: erken taahhüt

En pahalı senaryo, tek bir müşteri için pahalı bir altyapı kurup o müşteriyi
kaybetmektir. İlk EDI talebiniz geldiğinde şunu sorun: bu ortak hacminizin ne
kadarını oluşturuyor ve önümüzdeki bir yılda kaç ortak daha EDI isteyecek?

Cevap "bir ortak, düşük hacim" ise, önce elle veya yarı otomatik başlamak
savunulabilir bir karardır. Otomasyona geçiş kapısı açık kalır; tersi doğru
değildir.

## Görünmeyen maliyetler

Teklifleri karşılaştırırken sorulacak sorular:

- Yeni bir ticari ortak eklemek ne kadar? (Çoğu zaman ayrı ücretlendirilir)
- Şartname değişikliğinde eşleme güncellemesi dahil mi?
- Test ortamı var mı? Üretimde deneme yapmak istemezsiniz
- Aktarım kanalı (AS2, SFTP) ayrı mı ücretlendiriliyor?
- Sözleşme bitince eşlemeleriniz size ait mi?

Son madde özellikle önemli: bazı sağlayıcılarda yıllarca biriken eşleme
mantığı sağlayıcının mülkiyetinde kalır ve taşınması yeniden yazmak anlamına
gelir.

## Nereden başlamalı

Karar vermeden önce elinizdeki örnek dosyaya bakın. Kaç kalem var, hangi
segmentler kullanılıyor, şartname ne kadar karmaşık? Bu, alacağınız tekliflerin
gerçekçi olup olmadığını anlamanın en ucuz yoludur — ve bunun için henüz bir
şey satın almanız gerekmez.
""",
        },
        'en': {
            'title': 'How much should a small business spend on EDI?',
            'summary': 'Does a company receiving 20 orders a month need full automation? '
                       'Usually not.',
            'body': """
A retail chain has told you they "work with EDI", and you have no idea what it
will cost. Naming a figure is hard, but knowing **where** the cost comes from
makes quotes much easier to compare.

## Where does the money go?

There are four items, and their order often surprises people:

| Item | Weight |
|---|---|
| Software / subscription | Usually the smallest item |
| Initial setup and mapping | One-off, but among the largest |
| Extra integration per partner | A new customer means new work |
| Maintenance and support | Ongoing, and routinely underestimated |

The real money is not in the software but in the **mapping** — defining how
incoming EDI fields correspond to fields in your own system. That work partly
repeats for every partner, because every partner's specification differs.

## Three approaches

**1. An EDI service provider (VAN or cloud)**

You pay a monthly subscription and the provider handles translation and
transmission. Pricing is usually by volume or by number of partners.

- Upside: you start quickly and carry no technical load
- Downside: a permanent cost that grows with volume, plus dependence on the
  provider

**2. Building your own integration**

You add an EDI module to your ERP, or develop one yourself.

- Upside: no monthly fee, full control
- Downside: development time and, more importantly, **maintenance**. When a
  partner changes its specification, you are the one who updates it.

**3. Handling it manually**

Open the file, read it, key the data in. It sounds primitive, but for a supplier
receiving a few orders a month it can genuinely be the right answer.

- Upside: zero setup cost
- Downside: error rate and time cost grow quickly with volume

## Where are the thresholds?

As a rough rule of thumb:

- **Under 10 documents a month** — manual handling is usually cheapest. Automation
  will not earn back its setup cost.
- **Between 10 and 100** — semi-automatic approaches make sense: read the file,
  convert it to a table, import it.
- **Over 100, or several partners** — full automation pays for itself.

These thresholds shift by industry. In automotive, where one late delivery can
stop a production line, automation may be mandatory even at low volume.

## The common mistake: committing too early

The most expensive outcome is building costly infrastructure for a single
customer and then losing that customer. When your first EDI request arrives, ask:
what share of my volume is this partner, and how many more partners will ask for
EDI within a year?

If the answer is "one partner, low volume", starting manually or semi-manually is
a defensible decision. The door to automation stays open; the reverse is not
true.

## The costs you do not see

Questions worth asking when comparing quotes:

- What does adding a new trading partner cost? (It is often billed separately)
- Are mapping updates included when a specification changes?
- Is there a test environment? You do not want to experiment in production
- Is the transport channel (AS2, SFTP) charged separately?
- When the contract ends, do your mappings belong to you?

That last point matters more than it looks: with some providers, mapping logic
built up over years remains the provider's property, and moving means rewriting
it.

## Where to start

Before deciding anything, look at the sample file you were sent. How many line
items, which segments, how complex is the specification? That is the cheapest way
to judge whether the quotes you receive are realistic — and it does not require
buying anything yet.
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
İkisi de elektronik, ikisi de fatura taşıyor, ama aynı şey değiller. Türkiye'de
çalışan bir firma çoğu zaman **ikisini birden** kullanır ve karıştırmak
entegrasyon planını baştan yanlış kurmaya yol açar.

## Temel fark: kim için zorunlu?

**e-Fatura** yasal bir yükümlülüktür. Devletin belirlediği formatta (Türkiye'de
UBL-TR), devletin belirlediği kanaldan (GİB) geçer. Amacı vergi denetimidir.

**EDI** ticari bir anlaşmadır. Formatı ve kanalı taraflar belirler. Amacı
operasyonu otomatikleştirmektir.

| | e-Fatura | EDI |
|---|---|---|
| Zorunluluk | Yasal | Sözleşmeye bağlı |
| Format | UBL-TR (XML) | EDIFACT, X12 |
| Kanal | GİB üzerinden | Taraflar arası (AS2, SFTP, VAN) |
| Kapsam | Yalnızca fatura | Sipariş, irsaliye, fatura, ödeme… |
| Doğrulayan | Devlet | Ticari ortak |

## Asıl ayrım: kapsam

En önemli fark tabloda görünen son satır. e-Fatura yalnızca faturayı ilgilendirir.
EDI ise ticari sürecin tamamını taşır:

```
ORDERS  -> siparis
ORDRSP  -> siparis yaniti
DESADV  -> sevk ihbari
RECADV  -> mal kabul
INVOIC  -> fatura
REMADV  -> odeme bildirimi
```

Yani "EDI'ye geçtik" cümlesi genellikle "artık siparişleri de elektronik
alıyoruz" demektir; e-Fatura ise sürecin yalnızca son adımını kapsar.

## Neden ikisi birden gerekiyor?

Çünkü farklı taraflara hesap veriyorlar.

Bir zincir markete tedarikçiyseniz, market sizden EDIFACT INVOIC isteyebilir —
kendi sistemine otomatik girmesi için. Aynı faturayı ayrıca e-Fatura olarak GİB
üzerinden de kesmeniz gerekir, çünkü yasal geçerlilik oradan gelir.

Aynı ticari olay, iki farklı formatta, iki farklı yere gider. Bu tekrar tuhaf
görünür ama sistemlerin amaçları farklıdır.

## Pratik sonuçları

**Numaralar tutmalı.** EDI faturasındaki belge numarası ile e-Faturadaki numara
aynı olmalıdır. Aksi hâlde mutabakatta iki ayrı fatura görünür ve kimse hangisinin
gerçek olduğunu bilemez.

**Tutarlar tutmalı.** İki formata farklı yuvarlama uygulayan sistemler, kuruş
farkları üretir. Bu farklar denetimde soru işareti yaratır.

**Zamanlama önemlidir.** EDI faturası ortağınıza ulaşıp e-Fatura henüz
kesilmemişse, ortak ödeme yapamayabilir. Sıralamayı süreçte netleştirmek gerekir.

## Avrupa'daki durum

Avrupa'da benzer bir ayrım **Peppol** ile kurulmuştur. Peppol, e-Faturanın
sınır ötesi karşılığı gibi çalışır: standart bir ağ ve format (Peppol BIS,
yine UBL tabanlı). EDIFACT ise ticari akışta varlığını sürdürür.

Yani Avrupa'da da tablo benzerdir: yasal katman UBL tabanlı bir ağa, operasyonel
katman EDIFACT'e dayanır.

## Karıştırılmaması gereken nokta

"e-Fatura kesiyoruz, EDI'ye gerek yok" cümlesi yanlıştır. e-Fatura siparişinizi
almaz, sevkiyatınızı bildirmez, mal kabulünüzü kaydetmez. Ticari ortağınız EDI
istiyorsa, bunun sebebi faturayı almak değil, **süreci** otomatikleştirmektir.

Tersi de doğrudur: EDI kullanmak yasal yükümlülüğünüzü ortadan kaldırmaz.

## Nereden başlamalı

Elinizde her iki formattan örnek varsa, ikisini yan yana koyup aynı faturanın
nasıl göründüğünü karşılaştırmak öğretici olur. EDIFACT tarafındaki dosyayı
okunur hâle getirmek, hangi alanın hangi UBL alanına karşılık geldiğini
görmenin ilk adımıdır.
""",
        },
        'en': {
            'title': 'Is EDI the same as e-invoicing?',
            'summary': 'Both carry electronic invoices, but they differ in purpose, audience '
                       'and whether they are compulsory.',
            'body': """
Both are electronic and both carry invoices, but they are not the same thing. A
company often needs **both**, and confusing them leads to an integration plan
that is wrong from the start.

## The basic difference: mandatory for whom?

**E-invoicing** is a legal obligation. It uses a format the state defines (UBL in
most European schemes, UBL-TR in Türkiye) and a channel the state defines. Its
purpose is tax oversight.

**EDI** is a commercial agreement. The parties choose the format and the channel.
Its purpose is to automate operations.

| | E-invoicing | EDI |
|---|---|---|
| Obligation | Legal | Contractual |
| Format | UBL (XML) | EDIFACT, X12 |
| Channel | Via the tax authority or a certified network | Between the parties (AS2, SFTP, VAN) |
| Scope | Invoices only | Orders, despatch, invoices, payment… |
| Validated by | The state | Your trading partner |

## The real distinction: scope

The most important difference is the second-to-last row. E-invoicing concerns
only the invoice. EDI carries the whole commercial process:

```
ORDERS  -> purchase order
ORDRSP  -> order response
DESADV  -> despatch advice
RECADV  -> receiving advice
INVOIC  -> invoice
REMADV  -> remittance advice
```

So "we moved to EDI" usually means "we now receive orders electronically too",
whereas e-invoicing covers only the last step of the process.

## Why do you need both?

Because they answer to different parties.

If you supply a retail chain, the chain may require an EDIFACT INVOIC so that it
can post the invoice automatically. You will still have to issue the same invoice
through the legal e-invoicing channel, because that is where legal validity comes
from.

The same commercial event goes to two places in two formats. The duplication
looks odd, but the systems exist for different reasons.

## Practical consequences

**The numbers must agree.** The document number on the EDI invoice and on the
e-invoice must be identical. Otherwise reconciliation shows two invoices and
nobody knows which is real.

**The amounts must agree.** Systems that round differently in the two formats
produce penny differences, and those differences raise questions in an audit.

**Timing matters.** If the EDI invoice reaches your partner before the e-invoice
has been issued, they may be unable to pay. The order of the two steps needs to be
explicit in your process.

## The European picture

In Europe the same distinction is drawn through **Peppol**. Peppol works as the
cross-border counterpart of national e-invoicing: a standard network and format
(Peppol BIS, again UBL-based). EDIFACT continues to carry the commercial flow.

So the table looks similar there too: the legal layer rests on a UBL-based
network, the operational layer on EDIFACT.

## The point not to confuse

"We issue e-invoices, so we do not need EDI" is wrong. E-invoicing does not
receive your orders, announce your shipments or record your goods receipts. If
your trading partner asks for EDI, the reason is not to receive the invoice but
to automate the **process**.

The reverse holds as well: using EDI does not remove your legal obligation.

## Where to start

If you have samples of both formats, putting them side by side and comparing how
the same invoice looks is instructive. Making the EDIFACT file readable is the
first step towards seeing which field corresponds to which UBL element.
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
Bir EDI dosyası gönderdiniz. Ulaştı mı? İşlendi mi? Bunu ayrı bir mesaj cevaplar:
**CONTRL**. Okundu bilgisinin EDI karşılığıdır.

## Ne yapar, ne yapmaz

CONTRL içerikle ilgilenmez. "Siparişini kabul ettim" demez; "dosyanı aldım ve
sözdizimi geçerli" der. Yani teknik bir teyittir, ticari değil.

İki farklı şey karıştırılmamalıdır:

- **CONTRL** — dosya ulaştı, sözdizimi doğru
- **ORDRSP** — siparişi kabul ediyorum / etmiyorum

CONTRL almanız siparişinizin kabul edildiği anlamına gelmez. Sözdizimi kusursuz
ama ticari olarak reddedilecek bir sipariş de olumlu CONTRL alır.

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

Sondaki `7`, zarfın sorunsuz kabul edildiğini söyler. Bu satırdaki referans
numarası (`REF00042`) gönderdiğiniz dosyanın `UNB` satırındaki numarayla
eşleşir — hangi teyidin hangi dosyaya ait olduğunu böyle bulursunuz.

## Hata geldiğinde

Reddedilme durumunda `UCS` size segment sırasını verir, `UCD` ise nedeni:

```
UCS+12'
UCD+13+QTY+2'
```

Bu, 12. segmentteki `QTY`'nin 2. veri elemanında hata olduğunu söyler. Elinizdeki
dosyayı açıp 12. segmente bakmak sorunu doğrudan gösterir.

Sık görülen hata kodları:

| Kod | Anlamı |
|---|---|
| `12` | Geçersiz değer |
| `13` | Zorunlu alan eksik |
| `15` | Kod listesinde olmayan değer |
| `35` | Segment fazla tekrarlanmış |
| `36` | Segment eksik |

Bu kodlar sorunun **türünü** söyler, çözümünü değil. "Zorunlu alan eksik"
uyarısı aldığınızda hangi alanın zorunlu olduğunu şartnameniz söyler.

## Hiç CONTRL gelmiyorsa

Bu genellikle içerik hatası değil, **aktarım** sorunudur. Sırayla bakılacak
yerler:

1. **Dosya karşı tarafa ulaştı mı?** SFTP dizinini, AS2 sertifikasının süresini,
   bağlantı günlüklerini kontrol edin.
2. **Ortağınız CONTRL gönderiyor mu?** Her ortak göndermez. Bu şartnamede
   yazar; gönderilmiyorsa beklemek boşunadır.
3. **Dosya ulaşmış ama kuyrukta mı bekliyor?** Bazı sistemler toplu işler,
   teyit saatler sonra gelebilir.

Beklenen süre de şartnamede tanımlıdır; genellikle birkaç dakika ile birkaç saat
arasında değişir.

## Siz CONTRL göndermeli misiniz?

Gelen dosyaları işliyorsanız, ortağınız büyük ihtimalle sizden de teyit
bekleyecektir. Bu tek yönlü bir mekanizma değildir.

Kendi CONTRL'ünüzü üretirken en sık yapılan hata, her dosyaya koşulsuz `7`
(kabul) yollamaktır. Bu, sözdizimi hatalı bir dosyayı da "kabul edildi" diye
işaretler ve karşı taraf sorunu ancak fatura ödenmediğinde fark eder.

## Pratik öneri

CONTRL mesajlarını saklayın. Bir fatura "gelmedi" tartışmasında, tarihli bir
kabul teyidi meseleyi en hızlı çözen belgedir. Sözdizimi geçerliliğini
kanıtlamak, ticari anlaşmazlığı çözmez ama tartışmayı doğru yere taşır:
dosya ulaştıysa sorun aktarımda değil, iş kuralındadır.

Elinize bir CONTRL geçtiğinde, `UCS` ve `UCD` satırlarındaki numaraları
gönderdiğiniz dosyayla yan yana okumak en hızlı teşhis yoludur.
""",
        },
        'en': {
            'title': 'CONTRL: did my file arrive?',
            'summary': 'The EDI equivalent of a read receipt is the CONTRL message. What it '
                       'means when none arrives, or when it carries errors.',
            'body': """
You sent an EDI file. Did it arrive? Was it processed? A separate message answers
that: **CONTRL**. It is the EDI equivalent of a read receipt.

## What it does and does not do

CONTRL takes no interest in content. It does not say "I accept your order"; it
says "I received your file and the syntax is valid". It is a technical
acknowledgement, not a commercial one.

Two things not to confuse:

- **CONTRL** — the file arrived and parses
- **ORDRSP** — I do or do not accept the order

Receiving a CONTRL does not mean your order was accepted. An order with flawless
syntax that will be commercially rejected still gets a positive CONTRL.

## Its structure

A CONTRL message shows where the error is, if there is one:

| Segment | Purpose |
|---|---|
| `UCI` | Status at interchange level |
| `UCM` | Status at message level |
| `UCS` | Position of the segment in error |
| `UCD` | The reason and which element |

The status codes are short: `7` accepted, `4` rejected, `8` errors present but
processed.

```
UCI+REF00042+8712345678901:14+8798765432109:14+7'
```

The trailing `7` says the interchange was accepted without problems. The reference
on that line (`REF00042`) matches the number on the `UNB` line of the file you
sent — that is how you tell which acknowledgement belongs to which file.

## When errors come back

On a rejection, `UCS` gives you the segment position and `UCD` the reason:

```
UCS+12'
UCD+13+QTY+2'
```

That says there is an error in the second data element of the `QTY` at segment 12.
Opening your file and looking at segment 12 shows the problem directly.

Error codes you will see often:

| Code | Meaning |
|---|---|
| `12` | Invalid value |
| `13` | Mandatory field missing |
| `15` | Value not in the code list |
| `35` | Segment repeated too many times |
| `36` | Segment missing |

These codes tell you the **kind** of problem, not the fix. When you get "mandatory
field missing", your specification tells you which field is mandatory.

## If no CONTRL arrives at all

That is usually a **transport** problem rather than a content one. Places to look,
in order:

1. **Did the file reach the other side?** Check the SFTP directory, the expiry of
   the AS2 certificate, and the connection logs.
2. **Does your partner send CONTRL at all?** Not everyone does. The specification
   says so; if they do not, waiting is pointless.
3. **Did it arrive but sit in a queue?** Some systems process in batches and the
   acknowledgement can be hours behind.

The expected turnaround is also defined in the specification; it usually ranges
from a few minutes to a few hours.

## Should you send CONTRL yourself?

If you process incoming files, your partner will most likely expect an
acknowledgement from you too. This is not a one-way mechanism.

The most common mistake when generating your own CONTRL is returning an
unconditional `7` (accepted) for every file. That marks a syntactically broken
file as accepted, and the other side only discovers the problem when an invoice
goes unpaid.

## A practical suggestion

Keep your CONTRL messages. In an argument about an invoice that "never arrived", a
dated acknowledgement is the document that settles it fastest. Proving syntactic
validity does not resolve a commercial dispute, but it moves the discussion to the
right place: if the file arrived, the problem is not transport but a business
rule.

When a CONTRL lands on your desk, reading the numbers in its `UCS` and `UCD` lines
alongside the file you sent is the quickest route to a diagnosis.
""",
        },
    },
]
