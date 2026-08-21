# -*- coding: utf-8 -*-
"""Referans bölümünün elle yazılmış içeriği.

Çeviri dosyalarındaki (locales/*.json) segment ve kod açıklamaları veriyi sağlar;
buradaki metinler ise o veriyi bağlama oturtan açıklamalar, örnekler ve rehber
yazılarıdır. Jeneratör (build_reference.py) ikisini birleştirir.
"""

# =========================================================================
# ARAYÜZ METİNLERİ
# =========================================================================

UI = {
    'tr': {
        'lang_name': 'Türkçe',
        'other_lang': 'English',
        'hub_title': 'EDI Referansı',
        'hub_tagline': 'EDIFACT segmentleri, mesaj tipleri ve kod listeleri için '
                       'Türkçe başvuru kaynağı.',
        'segments': 'Segmentler',
        'messages': 'Mesaj Tipleri',
        'guides': 'Rehberler',
        'segment_of': 'segmenti',
        'elements': 'Veri Elemanları',
        'codes': 'Kod Listesi',
        'example': 'Örnek',
        'position': 'Sıra',
        'description': 'Açıklama',
        'code': 'Kod',
        'meaning': 'Anlamı',
        'back_to_ref': 'EDI Referansı',
        'open_in_app': 'Bu örneği editörde aç',
        'all_segments': 'Tüm segmentler',
        'all_messages': 'Tüm mesaj tipleri',
        'no_elements': 'Bu segment için eleman açıklaması tanımlı değil.',
        'related': 'İlgili',
        'app_cta_title': 'EDI dosyanızı tarayıcıda açın',
        'app_cta_text': 'ediviewer, EDIFACT ve X12 dosyalarını okunabilir hâle getirir; '
                        'PDF ve Excel\'e aktarır. Dosyalarınız cihazınızdan çıkmaz.',
        'app_cta_btn': 'Uygulamayı aç',
        'toc': 'İçindekiler',
        'typical_flow': 'Tipik Segment Akışı',
        'who_sends': 'Kim gönderir',
        'used_for': 'Ne için kullanılır',
    },
    'en': {
        'lang_name': 'English',
        'other_lang': 'Türkçe',
        'hub_title': 'EDI Reference',
        'hub_tagline': 'A reference for EDIFACT segments, message types and code lists.',
        'segments': 'Segments',
        'messages': 'Message Types',
        'guides': 'Guides',
        'segment_of': 'segment',
        'elements': 'Data Elements',
        'codes': 'Code List',
        'example': 'Example',
        'position': 'Pos.',
        'description': 'Description',
        'code': 'Code',
        'meaning': 'Meaning',
        'back_to_ref': 'EDI Reference',
        'open_in_app': 'Open this example in the editor',
        'all_segments': 'All segments',
        'all_messages': 'All message types',
        'no_elements': 'No element descriptions are defined for this segment.',
        'related': 'Related',
        'app_cta_title': 'Open your EDI file in the browser',
        'app_cta_text': 'ediviewer makes EDIFACT and X12 files readable and exports them '
                        'to PDF and Excel. Your files never leave your device.',
        'app_cta_btn': 'Open the app',
        'toc': 'Contents',
        'typical_flow': 'Typical Segment Flow',
        'who_sends': 'Who sends it',
        'used_for': 'What it is used for',
    },
}

# =========================================================================
# SEGMENT AÇIKLAMALARI VE ÖRNEKLERİ
# =========================================================================
# purpose: segmentin ne işe yaradığı (1-3 cümle)
# example: gerçekçi bir EDIFACT satırı
# note:    dikkat edilmesi gereken pratik ayrıntı (opsiyonel)

SEGMENTS = {
    'UNB': {
        'example': "UNB+UNOC:3+8712345678901:14+8798765432109:14+260117:1030+REF00042'",
        'tr': {
            'purpose': 'Zarf başlığı. Bir EDI aktarımının en dış katmanıdır; gönderen ve '
                       'alıcıyı, kullanılan karakter setini, aktarım tarihini ve zarfa '
                       'verilen takip numarasını taşır. Her dosyada tam olarak bir tane bulunur.',
            'note': 'Karakter seti (UNOC gibi) yanlış seçilirse Türkçe karakterler karşı '
                    'tarafta bozuk görünür. UNOC Latin-1, UNOA ise yalnızca büyük harf ve '
                    'rakam kabul eder.',
        },
        'en': {
            'purpose': 'Interchange header. The outermost layer of an EDI transmission: it '
                       'carries the sender and receiver, the character set in use, the '
                       'transmission timestamp and the interchange control reference. Exactly '
                       'one appears per file.',
            'note': 'Choosing the wrong character set (such as UNOA instead of UNOC) is a '
                    'common cause of mangled accented characters, since UNOA permits only '
                    'uppercase letters and digits.',
        },
    },
    'UNH': {
        'example': "UNH+ME000001+ORDERS:D:96A:UN:EAN008'",
        'tr': {
            'purpose': 'Mesaj başlığı. Zarfın içindeki her bir mesajı başlatır ve o mesajın '
                       'hangi tipte olduğunu (ORDERS, INVOIC vb.), hangi sürüm ve alt sürümü '
                       'kullandığını bildirir.',
            'note': 'Bir zarf birden fazla mesaj taşıyabilir; her biri kendi UNH ile başlar '
                    've UNT ile biter.',
        },
        'en': {
            'purpose': 'Message header. Opens each message inside the interchange and declares '
                       'its type (ORDERS, INVOIC and so on) along with the version and release '
                       'it conforms to.',
            'note': 'One interchange may carry several messages; each opens with UNH and '
                    'closes with UNT.',
        },
    },
    'BGM': {
        'example': "BGM+220+PO-2026-0042+9'",
        'tr': {
            'purpose': 'Belgenin kimliğini verir: belge türü (sipariş, fatura, irsaliye...), '
                       'belge numarası ve mesajın amacı (orijinal, iptal, değişiklik).',
            'note': 'Üçüncü eleman kritiktir: 9 "orijinal", 1 "iptal", 4 "değişiklik" '
                    'demektir. Yanlış değer, karşı tarafta yinelenen sipariş oluşturabilir.',
        },
        'en': {
            'purpose': 'Identifies the document itself: its type (order, invoice, despatch '
                       'advice...), its number, and the purpose of the message (original, '
                       'cancellation, change).',
            'note': 'The third element matters: 9 means original, 1 cancellation, 4 change. '
                    'A wrong value here can create duplicate orders downstream.',
        },
    },
    'DTM': {
        'example': "DTM+137:20260117:102'",
        'tr': {
            'purpose': 'Tarih, saat veya süre taşır. Hangi tarihten bahsedildiğini ilk '
                       'elemandaki nitelikçi belirler: 137 belge tarihi, 2 teslim tarihi, '
                       '35 fiili teslim tarihi gibi.',
            'note': 'Üçüncü eleman format kodudur. 102 = YYYYMMDD, 203 = YYYYMMDDHHMM, '
                    '718 = tarih aralığı. Formatı okumadan tarihi ayrıştırmak hataya açıktır.',
        },
        'en': {
            'purpose': 'Carries a date, time or period. The qualifier in the first element '
                       'says which date is meant: 137 document date, 2 delivery date, '
                       '35 actual delivery date, and so on.',
            'note': 'The third element is the format code: 102 = YYYYMMDD, 203 = '
                    'YYYYMMDDHHMM, 718 = a date range. Parsing the value without reading the '
                    'format is a frequent source of bugs.',
        },
    },
    'NAD': {
        'example': "NAD+SU+8712345678901::9++ACME FOODS BV+Havenweg 5+ROTTERDAM+3011AA+NL'",
        'tr': {
            'purpose': 'Bir tarafı ve adresini tanımlar. İlk eleman tarafın rolünü söyler: '
                       'SU tedarikçi, BY alıcı, DP teslimat adresi, IV fatura adresi.',
            'note': 'Pratikte taraf çoğunlukla GLN numarasıyla tanınır ve isim/adres alanları '
                    'boş bırakılır. GLN eşleşmesi yapılamıyorsa mesaj genellikle reddedilir.',
        },
        'en': {
            'purpose': 'Identifies a party and its address. The first element gives the role: '
                       'SU supplier, BY buyer, DP delivery party, IV invoicee.',
            'note': 'In practice the party is usually recognised by its GLN and the name and '
                    'address fields are left empty. If the GLN cannot be matched, the message '
                    'is normally rejected.',
        },
    },
    'LIN': {
        'example': "LIN+1++5410013101234:EN'",
        'tr': {
            'purpose': 'Bir satır kalemini başlatır. Satır numarasını ve ürünün kimliğini '
                       '(çoğunlukla EAN/GTIN barkodu) taşır. Kendisinden sonra gelen IMD, '
                       'QTY, PRI, MOA segmentleri bu satıra aittir.',
            'note': 'EN nitelikçisi barkodun EAN/GTIN olduğunu belirtir. Satır kalemi, bir '
                    'sonraki LIN gelene kadar devam eder.',
        },
        'en': {
            'purpose': 'Opens a line item, carrying the line number and the product identifier '
                       '(usually an EAN/GTIN barcode). The IMD, QTY, PRI and MOA segments that '
                       'follow belong to this line.',
            'note': 'The EN qualifier marks the identifier as an EAN/GTIN. A line item '
                    'continues until the next LIN appears.',
        },
    },
    'QTY': {
        'example': "QTY+21:480:PCE'",
        'tr': {
            'purpose': 'Miktar bildirir. Hangi miktardan bahsedildiğini nitelikçi belirler: '
                       '21 sipariş miktarı, 12 sevk edilen, 194 teslim alınan, 152 satılan.',
            'note': 'Üçüncü eleman ölçü birimidir (PCE adet, KGM kilogram, LTR litre). '
                    'Birim yazılmazsa adet varsayılır, bu da yanlış anlaşılmaya açıktır.',
        },
        'en': {
            'purpose': 'States a quantity. The qualifier says which one: 21 ordered, '
                       '12 despatched, 194 received, 152 sold.',
            'note': 'The third element is the unit of measure (PCE pieces, KGM kilograms, '
                    'LTR litres). When omitted, pieces are assumed, which invites confusion.',
        },
    },
    'PRI': {
        'example': "PRI+AAA:1.85'",
        'tr': {
            'purpose': 'Birim fiyatı taşır. AAA net fiyat, AAB brüt fiyat, AAE tavsiye edilen '
                       'perakende satış fiyatıdır.',
            'note': 'PRI para birimini içermez; para birimi mesaj düzeyindeki CUX '
                    'segmentinden okunur. Bu ayrım sıkça gözden kaçar.',
        },
        'en': {
            'purpose': 'Carries a unit price. AAA is the net price, AAB the gross price and '
                       'AAE the recommended retail price.',
            'note': 'PRI does not carry a currency; the currency comes from the CUX segment at '
                    'message level. This split is easy to overlook.',
        },
    },
    'MOA': {
        'example': "MOA+203:888.00'",
        'tr': {
            'purpose': 'Parasal tutar bildirir. 203 satır tutarı, 79 mal toplamı, '
                       '124 vergi tutarı, 77 fatura genel toplamı anlamına gelir.',
            'note': 'Aynı mesajda birden fazla MOA bulunur ve her biri farklı bir toplamı '
                    'ifade eder; nitelikçiye bakmadan toplama yapmak yanlış sonuç verir.',
        },
        'en': {
            'purpose': 'States a monetary amount. 203 is the line amount, 79 the goods total, '
                       '124 the tax amount and 77 the invoice grand total.',
            'note': 'A message contains several MOA segments, each meaning a different total. '
                    'Summing them without checking the qualifier produces wrong figures.',
        },
    },
    'IMD': {
        'example': "IMD+F++:::BITTER CIKOLATA 100G'",
        'tr': {
            'purpose': 'Ürünün serbest metin açıklamasını taşır. Barkodun tanınmadığı '
                       'durumlarda ürünün ne olduğunu insan gözüyle anlamayı sağlar.',
            'note': 'Açıklama genellikle dört boş alt elemandan sonra gelir (:::) — bu '
                    'yüzden ayrıştırırken son parçayı almak gerekir.',
        },
        'en': {
            'purpose': 'Carries a free-text description of the item, letting a human tell what '
                       'the product is when the barcode is not recognised.',
            'note': 'The text usually sits after four empty sub-elements (:::), so a parser '
                    'has to take the last component.',
        },
    },
    'CUX': {
        'example': "CUX+2:EUR:9'",
        'tr': {
            'purpose': 'Mesajın para birimini belirler. Fiyat ve tutar taşıyan tüm '
                       'segmentler bu para biriminde yorumlanır.',
            'note': 'Mesajda CUX yoksa para birimi belirsizdir; taraflar arasındaki '
                    'anlaşmaya göre varsayılır. Bu, faturalarda ciddi hatalara yol açabilir.',
        },
        'en': {
            'purpose': 'Sets the currency for the message. Every segment carrying a price or '
                       'an amount is interpreted in this currency.',
            'note': 'Without a CUX the currency is implicit and has to be assumed from the '
                    'trading agreement — a genuine source of costly invoice errors.',
        },
    },
    'RFF': {
        'example': "RFF+ON:PO-2026-0042'",
        'tr': {
            'purpose': 'Başka bir belgeye referans verir. ON sipariş numarası, DQ irsaliye '
                       'numarası, IV fatura numarası, CT sözleşme numarasıdır.',
            'note': 'Faturanın hangi siparişe ait olduğu genellikle RFF+ON ile kurulur; '
                    'bu bağ olmadan otomatik eşleştirme yapılamaz.',
        },
        'en': {
            'purpose': 'References another document. ON is the order number, DQ the despatch '
                       'advice number, IV the invoice number and CT the contract number.',
            'note': 'The link between an invoice and its order is normally made with RFF+ON; '
                    'without it, automatic matching is impossible.',
        },
    },
    'FTX': {
        'example': "FTX+AAI+++TESLIMAT 08.00-16.00 SAATLERI ARASINDA YAPILACAKTIR'",
        'tr': {
            'purpose': 'Serbest metin notu taşır. Teslimat talimatı, ödeme koşulu ya da genel '
                       'bir açıklama olabilir.',
            'note': 'Serbest metin makine tarafından yorumlanmaz; kritik bilgiyi yalnızca FTX '
                    'içine koymak otomasyonu bozar. Metinde iki nokta üst üste kullanılacaksa '
                    'kaçış karakteri (?) gerekir.',
        },
        'en': {
            'purpose': 'Carries a free-text note: a delivery instruction, a payment condition '
                       'or a general remark.',
            'note': 'Free text is not machine-interpretable, so putting critical information '
                    'only in an FTX breaks automation. A colon inside the text must be escaped '
                    'with the release character (?).',
        },
    },
    'UNT': {
        'example': "UNT+35+ME000001'",
        'tr': {
            'purpose': 'Mesajı kapatır. İçerdiği segment sayısını (UNH ve UNT dahil) ve '
                       'UNH\'deki referans numarasını tekrarlar.',
            'note': 'Segment sayısı tutmuyorsa alıcı sistem mesajı genellikle reddeder; '
                    'bu, aktarımda eksilme olmadığını doğrulayan bir sağlama görevi görür.',
        },
        'en': {
            'purpose': 'Closes the message, repeating the number of segments it contains '
                       '(including UNH and UNT) and the reference number from UNH.',
            'note': 'If the segment count does not match, the receiving system usually rejects '
                    'the message; the count acts as a checksum against truncation.',
        },
    },
    'UNZ': {
        'example': "UNZ+1+REF00042'",
        'tr': {
            'purpose': 'Zarfı kapatır. İçerdiği mesaj sayısını ve UNB\'deki zarf referansını '
                       'tekrarlar.',
            'note': None,
        },
        'en': {
            'purpose': 'Closes the interchange, repeating the number of messages it contains '
                       'and the interchange reference from UNB.',
            'note': None,
        },
    },
    'TAX': {
        'example': "TAX+7+VAT+++:::20'",
        'tr': {
            'purpose': 'Vergi bilgisini taşır. Vergi tipini (KDV gibi) ve oranını bildirir.',
            'note': 'Oran genellikle son alt elemanda yer alır ve yüzde olarak yazılır; '
                    '20 değeri %20 demektir.',
        },
        'en': {
            'purpose': 'Carries tax information: the type of tax (such as VAT) and its rate.',
            'note': 'The rate normally sits in the last sub-element and is expressed as a '
                    'percentage, so 20 means 20%.',
        },
    },
    'ALC': {
        'example': "ALC+A++++DI::ADET ISKONTOSU'",
        'tr': {
            'purpose': 'İndirim veya ek masraf bildirir. A indirim (allowance), C masraf '
                       '(charge) anlamına gelir.',
            'note': 'ALC genellikle kendisinden sonra gelen PCD (yüzde) veya MOA (tutar) '
                    'segmentiyle birlikte okunur; tek başına tutar taşımaz.',
        },
        'en': {
            'purpose': 'Declares an allowance or a charge. A means allowance (discount), '
                       'C means charge.',
            'note': 'ALC is normally read together with the PCD (percentage) or MOA (amount) '
                    'segment that follows; on its own it carries no value.',
        },
    },
    'PAC': {
        'example': "PAC+40+:52+CT'",
        'tr': {
            'purpose': 'Paketleme bilgisini taşır: kaç koli, hangi ambalaj tipinde.',
            'note': 'Sevk irsaliyelerinde (DESADV) palet ve koli hiyerarşisi PAC, CPS ve GIN '
                    'segmentlerinin birlikte kullanılmasıyla kurulur.',
        },
        'en': {
            'purpose': 'Carries packaging information: how many packages, and of what type.',
            'note': 'In despatch advices (DESADV) the pallet and carton hierarchy is built '
                    'from PAC, CPS and GIN used together.',
        },
    },
    'GIN': {
        'example': "GIN+BJ+340123456789012345'",
        'tr': {
            'purpose': 'Kimlik numarası taşır. BJ nitelikçisi SSCC (palet/koli seri numarası) '
                       'anlamına gelir.',
            'note': 'SSCC, depo girişinde paletin fiziksel olarak taranan barkoduyla '
                    'eşleşmelidir; eşleşmezse mal kabul otomasyonu durur.',
        },
        'en': {
            'purpose': 'Carries an identity number. The BJ qualifier denotes an SSCC, the '
                       'serial shipping container code of a pallet or carton.',
            'note': 'The SSCC must match the barcode physically scanned at goods-in; if it '
                    'does not, receiving automation stops.',
        },
    },
    'LOC': {
        'example': "LOC+9+GEBZE MERKEZ DEPO'",
        'tr': {
            'purpose': 'Bir yer bildirir. 9 yükleme yeri, 11 boşaltma yeri, 7 teslim yeri '
                       'anlamına gelir.',
            'note': None,
        },
        'en': {
            'purpose': 'States a place. 9 is the place of loading, 11 the place of discharge '
                       'and 7 the place of delivery.',
            'note': None,
        },
    },
    'TDT': {
        'example': "TDT+20++30++ACME LOJISTIK'",
        'tr': {
            'purpose': 'Taşıma detaylarını taşır: taşıma aşaması, taşıma modu (karayolu, '
                       'denizyolu) ve taşıyıcı firma.',
            'note': None,
        },
        'en': {
            'purpose': 'Carries transport details: the stage of carriage, the mode of '
                       'transport (road, sea) and the carrier.',
            'note': None,
        },
    },
    'CNT': {
        'example': "CNT+2:2'",
        'tr': {
            'purpose': 'Kontrol toplamı. Mesajdaki satır sayısı veya toplam miktar gibi bir '
                       'değeri doğrulama amacıyla tekrarlar.',
            'note': None,
        },
        'en': {
            'purpose': 'A control total. Repeats a value such as the number of line items or '
                       'the total quantity so the receiver can verify it.',
            'note': None,
        },
    },
    'UNS': {
        'example': "UNS+S'",
        'tr': {
            'purpose': 'Bölüm ayracı. Mesajın detay bölümünün bittiğini ve özet bölümünün '
                       'başladığını bildirir.',
            'note': 'S değeri "summary" (özet) demektir. Bu segmentten sonra gelen MOA '
                    'segmentleri satır değil, mesaj toplamlarıdır.',
        },
        'en': {
            'purpose': 'Section separator. Marks the end of the detail section and the start '
                       'of the summary section.',
            'note': 'The value S stands for summary. MOA segments after this point are '
                    'message-level totals, not line amounts.',
        },
    },
}

# =========================================================================
# MESAJ TİPİ AÇIKLAMALARI
# =========================================================================

MESSAGES = {
    'ORDERS': {
        'flow': ['UNB', 'UNH', 'BGM', 'DTM', 'NAD', 'CUX', 'LIN', 'IMD', 'QTY', 'PRI', 'UNS', 'MOA', 'UNT', 'UNZ'],
        'tr': {
            'sender': 'Alıcı (satın alan taraf) tedarikçiye gönderir.',
            'used_for': 'Mal veya hizmet sipariş etmek için kullanılan temel EDI mesajıdır. '
                        'Hangi ürünün, ne miktarda, hangi fiyata ve ne zaman teslim edilmek '
                        'üzere istendiğini bildirir.',
            'body': 'ORDERS, EDI zincirinin başlangıç noktasıdır. Gönderildikten sonra '
                    'tedarikçi genellikle ORDRSP ile yanıt verir, malı gönderirken DESADV, '
                    'faturayı keserken INVOIC üretir. Bu dört mesaj birbirine BGM belge '
                    'numarası ve RFF referansları üzerinden bağlanır.\n\n'
                    'Sipariş değiştirilecekse yeni bir ORDERS değil, ORDCHG gönderilir; '
                    'iptal için ise BGM\'in üçüncü elemanına 1 yazılır. Bu ayrımı atlamak, '
                    'karşı tarafta yinelenen sipariş oluşmasının en yaygın sebebidir.',
        },
        'en': {
            'sender': 'Sent by the buyer to the supplier.',
            'used_for': 'The core EDI message for ordering goods or services. It states which '
                        'product is wanted, in what quantity, at what price and for delivery '
                        'when.',
            'body': 'ORDERS is the starting point of the EDI chain. Once sent, the supplier '
                    'usually replies with an ORDRSP, produces a DESADV when despatching the '
                    'goods and an INVOIC when billing. These four messages are tied together '
                    'by the BGM document number and RFF references.\n\n'
                    'To change an order you send an ORDCHG rather than a second ORDERS; to '
                    'cancel one you set the third element of BGM to 1. Missing this '
                    'distinction is the most common cause of duplicated orders.',
        },
    },
    'ORDRSP': {
        'flow': ['UNB', 'UNH', 'BGM', 'DTM', 'RFF', 'NAD', 'LIN', 'QTY', 'PRI', 'UNT', 'UNZ'],
        'tr': {
            'sender': 'Tedarikçi, aldığı siparişe yanıt olarak gönderir.',
            'used_for': 'Siparişin kabul edildiğini, kısmen kabul edildiğini veya '
                        'reddedildiğini bildirir. Satır bazında farklı yanıt verilebilir.',
            'body': 'ORDRSP\'nin değeri satır bazında yanıt verebilmesindedir: LIN '
                    'segmentindeki aksiyon kodu 5 kabul, 7 red, 3 değişiklik önerisi anlamına '
                    'gelir. Böylece tedarikçi "üç kalemi gönderebilirim, dördüncü stokta yok" '
                    'diyebilir.\n\n'
                    'Reddedilen veya değiştirilen satırlarda gerekçe genellikle FTX ile '
                    'iletilir. Alıcı sistem bu yanıtı otomatik işleyip siparişi günceller.',
        },
        'en': {
            'sender': 'Sent by the supplier in response to an order.',
            'used_for': 'Confirms that an order is accepted, partially accepted or rejected. '
                        'The response can differ line by line.',
            'body': 'The value of ORDRSP lies in its per-line answers: the action code on the '
                    'LIN segment is 5 for accepted, 7 for rejected and 3 for a proposed '
                    'change. A supplier can therefore say "I can ship three items, the fourth '
                    'is out of stock".\n\n'
                    'Reasons for a rejection or a change are normally carried in an FTX. The '
                    'buyer\'s system processes the response automatically and updates the order.',
        },
    },
    'INVOIC': {
        'flow': ['UNB', 'UNH', 'BGM', 'DTM', 'RFF', 'NAD', 'CUX', 'LIN', 'QTY', 'PRI', 'MOA', 'TAX', 'UNS', 'MOA', 'UNT', 'UNZ'],
        'tr': {
            'sender': 'Tedarikçi (satıcı) alıcıya gönderir.',
            'used_for': 'Ticari faturanın elektronik karşılığıdır. Satır kalemlerini, '
                        'vergileri ve ödenecek toplam tutarı taşır.',
            'body': 'INVOIC, EDI mesajları arasında en çok doğrulama gerektirenidir çünkü '
                    'muhasebe kaydına dönüşür. Alıcı sistem genellikle üçlü eşleştirme yapar: '
                    'sipariş (ORDERS), mal kabul (RECADV) ve fatura tutarları birbirini '
                    'tutmalıdır.\n\n'
                    'Toplamlar özet bölümünde MOA ile verilir: 79 mal toplamı, 124 vergi, '
                    '77 genel toplam, 9 ödenecek tutar. Bu nitelikçileri karıştırmak, '
                    'faturanın reddedilmesinin en yaygın teknik sebebidir. Banka bilgisi '
                    'gerekiyorsa FII segmentiyle taşınır.',
        },
        'en': {
            'sender': 'Sent by the supplier to the buyer.',
            'used_for': 'The electronic equivalent of a commercial invoice, carrying line '
                        'items, taxes and the total amount payable.',
            'body': 'INVOIC demands the most validation of any EDI message because it becomes '
                    'an accounting entry. The receiving system normally performs a three-way '
                    'match: the order (ORDERS), the goods receipt (RECADV) and the invoice '
                    'must agree.\n\n'
                    'Totals appear in the summary section as MOA values: 79 goods total, '
                    '124 tax, 77 grand total, 9 amount payable. Confusing these qualifiers is '
                    'the most common technical reason for an invoice being rejected. Bank '
                    'details, when required, travel in the FII segment.',
        },
    },
    'DESADV': {
        'flow': ['UNB', 'UNH', 'BGM', 'DTM', 'RFF', 'NAD', 'CPS', 'PAC', 'GIN', 'LIN', 'QTY', 'UNT', 'UNZ'],
        'tr': {
            'sender': 'Tedarikçi, malı sevk ederken gönderir.',
            'used_for': 'Sevk ihbarı / irsaliye. Malın yola çıktığını, hangi paletlerde '
                        'hangi ürünlerin bulunduğunu önceden bildirir.',
            'body': 'DESADV\'nin asıl gücü paketleme hiyerarşisini taşımasıdır: CPS '
                    'segmentleri palet-koli ilişkisini kurar, GIN segmentleri her paletin '
                    'SSCC barkodunu verir.\n\n'
                    'Depo, mal gelmeden önce bu bilgiyi aldığı için giriş işlemini '
                    'hazırlayabilir; palet barkodu okutulduğunda içindekiler zaten bilinir. '
                    'Bu, mal kabul süresini dramatik biçimde kısaltır ve RECADV ile '
                    'karşılaştırma yapılmasını sağlar.',
        },
        'en': {
            'sender': 'Sent by the supplier when the goods are despatched.',
            'used_for': 'The despatch advice. It announces in advance that goods are on their '
                        'way and which products sit on which pallets.',
            'body': 'The real strength of DESADV is that it carries the packing hierarchy: CPS '
                    'segments establish the pallet-to-carton relationship and GIN segments '
                    'give each pallet its SSCC barcode.\n\n'
                    'Because the warehouse receives this before the goods arrive, it can '
                    'prepare the receipt; when the pallet barcode is scanned its contents are '
                    'already known. This shortens goods-in dramatically and makes comparison '
                    'against the RECADV possible.',
        },
    },
    'RECADV': {
        'flow': ['UNB', 'UNH', 'BGM', 'DTM', 'RFF', 'NAD', 'LIN', 'QTY', 'UNT', 'UNZ'],
        'tr': {
            'sender': 'Alıcı, malı teslim aldıktan sonra gönderir.',
            'used_for': 'Mal kabul bildirimi. Fiilen ne kadar mal teslim alındığını, sevk '
                        'edilenle karşılaştırmalı olarak bildirir.',
            'body': 'RECADV\'de aynı satır için iki QTY bulunur: 12 sevk edilen, 194 teslim '
                    'alınan miktar. Aradaki fark eksik, fazla veya hasarlı teslimatı ortaya '
                    'çıkarır.\n\n'
                    'Bu mesaj olmadan fatura itirazları elle yürütülür; RECADV ile fark '
                    'otomatik tespit edilir ve gerekirse fatura kesilmeden önce düzeltilir.',
        },
        'en': {
            'sender': 'Sent by the buyer after the goods have been received.',
            'used_for': 'The receiving advice. It reports how much was actually received, set '
                        'against what was despatched.',
            'body': 'A RECADV carries two QTY values for the same line: 12 for the quantity '
                    'despatched and 194 for the quantity received. The difference exposes '
                    'short, over or damaged deliveries.\n\n'
                    'Without this message, invoice disputes are handled by hand; with it, the '
                    'discrepancy is detected automatically and can be corrected before the '
                    'invoice is even issued.',
        },
    },
    'SLSRPT': {
        'flow': ['UNB', 'UNH', 'BGM', 'DTM', 'NAD', 'CUX', 'LIN', 'QTY', 'MOA', 'UNT', 'UNZ'],
        'tr': {
            'sender': 'Perakendeci tedarikçiye gönderir.',
            'used_for': 'Satış raporu. Belirli bir dönemde hangi üründen ne kadar satıldığını '
                        'bildirir.',
            'body': 'SLSRPT, sipariş zincirinin dışında kalan ama tedarik planlaması için '
                    'kritik bir mesajdır. Tedarikçi, mağaza rafında ne olup bittiğini görerek '
                    'üretim ve sevkiyatını buna göre ayarlar.\n\n'
                    'Dönem başlangıcı ve bitişi DTM 356 ve 357 ile verilir. Satılan miktar '
                    'QTY 152 nitelikçisiyle taşınır; ciro ise MOA 203 ile.',
        },
        'en': {
            'sender': 'Sent by the retailer to the supplier.',
            'used_for': 'A sales report stating how much of each product was sold in a given '
                        'period.',
            'body': 'SLSRPT sits outside the ordering chain but is critical to supply '
                    'planning: it lets the supplier see what is happening on the shelf and '
                    'adjust production and shipping accordingly.\n\n'
                    'The period start and end are given by DTM 356 and 357. The quantity sold '
                    'travels with the QTY 152 qualifier and the revenue with MOA 203.',
        },
    },
    'PRICAT': {
        'flow': ['UNB', 'UNH', 'BGM', 'DTM', 'NAD', 'CUX', 'LIN', 'IMD', 'PRI', 'PAC', 'UNT', 'UNZ'],
        'tr': {
            'sender': 'Tedarikçi alıcıya gönderir.',
            'used_for': 'Fiyat kataloğu. Ürün listesini, fiyatları ve ambalaj bilgilerini '
                        'toplu olarak iletir.',
            'body': 'PRICAT genellikle sipariş öncesi ana veri alışverişi için kullanılır. '
                    'Alıcı, tedarikçinin ürün ve fiyat listesini kendi sistemine aktarır; '
                    'böylece siparişlerde doğru barkod ve fiyat kullanılır.\n\n'
                    'Bir satırda birden fazla PRI bulunabilir: AAA net, AAB brüt, AAE tavsiye '
                    'edilen perakende fiyatı. Menşe ülke ALI, ambalaj miktarı PAC ile verilir.',
        },
        'en': {
            'sender': 'Sent by the supplier to the buyer.',
            'used_for': 'A price catalogue conveying the product list, prices and packaging '
                        'details in bulk.',
            'body': 'PRICAT is normally used for master-data exchange ahead of ordering. The '
                    'buyer loads the supplier\'s product and price list into its own system so '
                    'that orders carry the correct barcode and price.\n\n'
                    'A line may carry several PRI segments: AAA net, AAB gross and AAE '
                    'recommended retail price. Country of origin comes from ALI and the pack '
                    'quantity from PAC.',
        },
    },
}

# =========================================================================
# REHBER YAZILARI
# =========================================================================

GUIDES = [
    {
        'slug': 'edifact-nedir',
        'slug_en': 'what-is-edifact',
        'tr': {
            'title': 'EDIFACT nedir? Yapısı ve okunuşu',
            'summary': 'EDIFACT dosyalarının katman katman yapısı, ayırıcı karakterler ve '
                       'bir satırın nasıl okunacağı.',
            'body': """
EDIFACT (Electronic Data Interchange For Administration, Commerce and Transport),
Birleşmiş Milletler tarafından geliştirilmiş uluslararası bir elektronik veri
değişim standardıdır. Avrupa'da perakende, lojistik ve otomotiv sektörlerinde
fiilî standarttır; Kuzey Amerika'da ise büyük ölçüde ANSI ASC X12 kullanılır.

## Neden böyle görünüyor?

Bir EDIFACT dosyası ilk bakışta okunaksızdır:

```
UNB+UNOC:3+8712345678901:14+8798765432109:14+260117:1030+REF00042'
```

Bu tasarım tercihi bilinçlidir. Standart, 1980'lerde hat kapasitesinin pahalı
olduğu bir dönemde tasarlandı; her karakter maliyetliydi. XML ya da JSON gibi
etiket tekrar eden formatlar yerine, anlamın **konumdan** çıkarıldığı sıkı bir
yapı seçildi.

## Üç katman

Bir EDIFACT dosyası iç içe üç katmandan oluşur:

- **Zarf (interchange)** — `UNB` ile açılır, `UNZ` ile kapanır. Gönderen ve
  alıcıyı taşır. Bir dosyada tek zarf bulunur.
- **Mesaj (message)** — `UNH` ile açılır, `UNT` ile kapanır. Bir zarf birden
  fazla mesaj taşıyabilir; her mesaj bir belgedir (bir sipariş, bir fatura).
- **Segment** — her satır bir segmenttir. `NAD` adres, `QTY` miktar, `MOA` tutar.

## Ayırıcı karakterler

Dört karakter yapıyı kurar:

| Karakter | Görevi |
|---|---|
| `'` | Segment sonu |
| `+` | Eleman ayracı |
| `:` | Alt eleman ayracı |
| `?` | Kaçış (release) karakteri |

Bir metnin içinde bu karakterlerden biri geçecekse önüne `?` konur. Örneğin
`ACME?+ORTAKLARI` metni, `+` karakterini ayraç değil harf olarak okutur. Bu
kaçış kuralını atlamak, ayrıştırıcıların en sık takıldığı yerdir.

Ayırıcılar varsayılan değildir, değiştirilebilir: dosya `UNA` segmentiyle
başlıyorsa ayırıcılar oradan okunur.

## Bir satırı okumak

```
NAD+SU+8712345678901::9++ACME FOODS BV+Havenweg 5+ROTTERDAM+3011AA+NL'
```

Elemanlara ayıralım:

- `NAD` — segment kodu: taraf ve adres
- `SU` — rol: tedarikçi (supplier)
- `8712345678901::9` — firma kimliği; `9` GS1 standardını gösterir
- (boş) — kullanılmayan eleman
- `ACME FOODS BV` — firma ünvanı
- `Havenweg 5` — sokak
- `ROTTERDAM` — şehir
- `3011AA` — posta kodu
- `NL` — ülke

Dikkat edin: boş elemanlar **atlanmaz**, `++` şeklinde yerinde durur. Çünkü
anlam konumdan gelir; bir eleman düşerse sonraki her şey kayar.

## Nereden devam etmeli

Segment segment ilerlemek için segment referansına, belirli bir belge tipini
anlamak için mesaj tipleri bölümüne bakabilirsiniz.
""",
        },
        'en': {
            'title': 'What is EDIFACT? Structure and how to read it',
            'summary': 'The layered structure of EDIFACT files, the delimiter characters and '
                       'how to read a single line.',
            'body': """
EDIFACT (Electronic Data Interchange For Administration, Commerce and Transport)
is an international standard for electronic data interchange developed by the
United Nations. It is the de facto standard in European retail, logistics and
automotive; North America largely uses ANSI ASC X12 instead.

## Why does it look like that?

An EDIFACT file is unreadable at first glance:

```
UNB+UNOC:3+8712345678901:14+8798765432109:14+260117:1030+REF00042'
```

This is a deliberate design choice. The standard was created in the 1980s when
line capacity was expensive and every character cost money. Rather than a format
that repeats tags, like XML or JSON, it uses a tight structure where meaning is
derived from **position**.

## Three layers

An EDIFACT file consists of three nested layers:

- **Interchange** — opens with `UNB`, closes with `UNZ`. Carries the sender and
  receiver. There is one per file.
- **Message** — opens with `UNH`, closes with `UNT`. One interchange may hold
  several messages; each message is one document (an order, an invoice).
- **Segment** — every line is a segment. `NAD` for an address, `QTY` for a
  quantity, `MOA` for an amount.

## Delimiter characters

Four characters carry the structure:

| Character | Role |
|---|---|
| `'` | Segment terminator |
| `+` | Element separator |
| `:` | Component separator |
| `?` | Release (escape) character |

If one of these characters appears inside a value, it is preceded by `?`. For
example `ACME?+PARTNERS` reads the `+` as a letter rather than a separator.
Ignoring this escape rule is where parsers most often break.

The delimiters are not fixed: if the file opens with a `UNA` segment, they are
read from there.

## Reading a line

```
NAD+SU+8712345678901::9++ACME FOODS BV+Havenweg 5+ROTTERDAM+3011AA+NL'
```

Split into elements:

- `NAD` — segment code: party and address
- `SU` — role: supplier
- `8712345678901::9` — party identifier; `9` indicates the GS1 standard
- (empty) — unused element
- `ACME FOODS BV` — company name
- `Havenweg 5` — street
- `ROTTERDAM` — city
- `3011AA` — postcode
- `NL` — country

Note that empty elements are **not** omitted; they stay in place as `++`.
Meaning comes from position, so dropping one shifts everything after it.

## Where to go next

Work through the segment reference to go segment by segment, or the message
types section to understand a particular kind of document.
""",
        },
    },
    {
        'slug': 'edifact-x12-farki',
        'slug_en': 'edifact-vs-x12',
        'tr': {
            'title': 'EDIFACT ve ANSI X12 arasındaki farklar',
            'summary': 'İki büyük EDI standardının ayırıcıları, segment isimleri ve '
                       'kullanım bölgeleri nasıl ayrışır.',
            'body': """
Dünyada iki büyük EDI standardı kullanılır: Avrupa merkezli **UN/EDIFACT** ve
Kuzey Amerika merkezli **ANSI ASC X12**. Aynı işi yaparlar ama sözdizimleri ve
isimlendirmeleri farklıdır.

## Ayırıcı karakterler

| | EDIFACT | X12 |
|---|---|---|
| Segment sonu | `'` | `~` |
| Eleman ayracı | `+` | `*` |
| Alt eleman ayracı | `:` | `>` |

Bir dosyanın hangi standarda ait olduğunu anlamanın en hızlı yolu ilk satıra
bakmaktır: `UNB` ile başlıyorsa EDIFACT, `ISA` ile başlıyorsa X12'dir.

## Segment ve belge isimleri

EDIFACT belge tiplerini okunabilir adlarla anar (`ORDERS`, `INVOIC`, `DESADV`);
X12 ise sayısal işlem kümesi numaraları kullanır.

| Belge | EDIFACT | X12 |
|---|---|---|
| Satın alma siparişi | ORDERS | 850 |
| Sipariş yanıtı | ORDRSP | 855 |
| Sipariş değişikliği | ORDCHG | 860 |
| Sevk ihbarı | DESADV | 856 |
| Fatura | INVOIC | 810 |
| Stok raporu | INVRPT | 846 |
| Ödeme bildirimi | REMADV | 820 |

Segment isimleri de ayrışır: EDIFACT'te adres `NAD`, X12'de `N1`; miktar
EDIFACT'te `QTY`, X12'de genellikle satır segmentinin (`PO1`, `IT1`) içindedir.

## Yapısal fark

X12, zarfı üç katmanda kurar: `ISA` (interchange), `GS` (functional group) ve
`ST` (transaction set). EDIFACT'te fonksiyonel grup katmanı (`UNG`) isteğe
bağlıdır ve pratikte çoğu zaman kullanılmaz.

## Hangisiyle çalışacaksınız?

Bu genellikle sizin değil, ticaret ortağınızın kararıdır. Avrupalı bir zincir
mağazayla çalışıyorsanız EDIFACT, Amerikalı bir perakendeciyle çalışıyorsanız
X12 beklemelisiniz. Her iki formatı da aynı araçla açıp okuyabilmek, iki
tarafla birden çalışan firmalar için pratik bir gerekliliktir.
""",
        },
        'en': {
            'title': 'EDIFACT versus ANSI X12',
            'summary': 'How the two major EDI standards differ in delimiters, segment names '
                       'and regional use.',
            'body': """
Two major EDI standards are in use worldwide: the European **UN/EDIFACT** and the
North American **ANSI ASC X12**. They do the same job with different syntax and
naming.

## Delimiter characters

| | EDIFACT | X12 |
|---|---|---|
| Segment terminator | `'` | `~` |
| Element separator | `+` | `*` |
| Component separator | `:` | `>` |

The quickest way to tell which standard a file follows is to look at the first
line: `UNB` means EDIFACT, `ISA` means X12.

## Segment and document names

EDIFACT names document types in readable form (`ORDERS`, `INVOIC`, `DESADV`);
X12 uses numeric transaction set codes.

| Document | EDIFACT | X12 |
|---|---|---|
| Purchase order | ORDERS | 850 |
| Order response | ORDRSP | 855 |
| Order change | ORDCHG | 860 |
| Despatch advice | DESADV | 856 |
| Invoice | INVOIC | 810 |
| Inventory report | INVRPT | 846 |
| Remittance advice | REMADV | 820 |

Segment names diverge too: an address is `NAD` in EDIFACT and `N1` in X12;
quantity is `QTY` in EDIFACT but usually sits inside the line segment (`PO1`,
`IT1`) in X12.

## Structural difference

X12 builds its envelope in three layers: `ISA` (interchange), `GS` (functional
group) and `ST` (transaction set). In EDIFACT the functional group layer (`UNG`)
is optional and in practice rarely used.

## Which one will you work with?

That is usually your trading partner's decision rather than yours. Working with a
European chain means EDIFACT; working with an American retailer means X12. Being
able to open and read both formats in one tool is a practical necessity for
companies that trade with both.
""",
        },
    },
    {
        'slug': 'edi-dosyasi-sorun-giderme',
        'slug_en': 'edi-troubleshooting',
        'tr': {
            'title': 'EDI dosyalarında sık yapılan hatalar',
            'summary': 'Reddedilen mesajların arkasındaki en yaygın teknik sebepler ve '
                       'nasıl fark edilecekleri.',
            'body': """
Bir EDI mesajı reddedildiğinde sebep genellikle iş mantığında değil,
sözdiziminde ya da nitelikçi seçiminde olur. Aşağıdakiler pratikte en sık
karşılaşılanlar.

## 1. Kaçış karakteri unutulur

Serbest metin alanlarında (`FTX`, `IMD`) geçen `+`, `:`, `'` karakterleri
ayraç sanılır ve satır ortadan bölünür. Doğrusu, bu karakterlerin önüne `?`
koymaktır.

```
FTX+AAI+++TESLIMAT 08?:00 SONRASI      ← doğru
FTX+AAI+++TESLIMAT 08:00 SONRASI       ← satırı bozar
```

## 2. Boş elemanlar atlanır

EDIFACT'te anlam konumdan gelir. Kullanılmayan bir eleman silinemez, yerinde
boş bırakılır:

```
NAD+SU+8712345678901::9++ACME FOODS BV    ← doğru (çift + boş elemanı korur)
NAD+SU+8712345678901::9+ACME FOODS BV     ← firma adı yanlış elemana düşer
```

## 3. UNT segment sayısı tutmaz

`UNT`, mesajdaki segment sayısını taşır ve bu sayıya `UNH` ile `UNT` de
dahildir. Elle satır eklenip sayı güncellenmezse alıcı sistem mesajı sağlama
hatası olarak reddeder.

## 4. Yanlış tarih formatı kodu

`DTM` segmentinin üçüncü elemanı formatı söyler. `102` ile `203` karıştırılırsa
saat bilgisi tarihin parçası sanılır:

```
DTM+137:20260117:102'      ← 17.01.2026
DTM+137:202601171030:203'  ← 17.01.2026 10:30
```

## 5. Para birimi eksikliği

`PRI` ve `MOA` para birimi taşımaz; birim mesaj düzeyindeki `CUX`'tan gelir.
`CUX` yoksa tutarlar belirsizdir ve karşı taraf kendi varsayılanını uygular —
faturalarda bu, gerçek maliyeti olan bir hatadır.

## 6. MOA nitelikçileri karıştırılır

Özet bölümünde birden fazla `MOA` bulunur ve her biri farklı bir toplamdır:
`79` mal toplamı, `124` vergi, `77` genel toplam, `9` ödenecek tutar.
Nitelikçiye bakmadan ilk `MOA`'yı toplam sanmak yaygın bir hatadır.

## 7. Karakter seti uyuşmazlığı

`UNB`'deki `UNOA`, yalnızca büyük harf ve rakam kabul eder. Türkçe karakter
içeren bir metni `UNOA` ile göndermek karşı tarafta bozulmaya yol açar; Latin-1
için `UNOC` kullanılmalıdır.

## Nasıl kontrol edilir

Dosyayı ediviewer'da açtığınızda segment etiketleri renklendirilir ve seçtiğiniz
satırın her elemanı adlandırılmış olarak listelenir. Bir elemanın beklediğiniz
etiketin karşısında durmaması, çoğu zaman yukarıdaki hatalardan birine işaret
eder.
""",
        },
        'en': {
            'title': 'Common mistakes in EDI files',
            'summary': 'The most frequent technical reasons behind rejected messages, and how '
                       'to spot them.',
            'body': """
When an EDI message is rejected, the cause usually lies in syntax or qualifier
choice rather than business logic. These are the ones seen most often in
practice.

## 1. The release character is forgotten

A `+`, `:` or `'` appearing inside a free-text field (`FTX`, `IMD`) is taken for
a separator and splits the line. The fix is to precede such characters with `?`.

```
FTX+AAI+++DELIVERY AFTER 08?:00      ← correct
FTX+AAI+++DELIVERY AFTER 08:00       ← breaks the line
```

## 2. Empty elements are dropped

In EDIFACT, meaning comes from position. An unused element cannot be removed; it
is left empty in place:

```
NAD+SU+8712345678901::9++ACME FOODS BV    ← correct (the double + preserves it)
NAD+SU+8712345678901::9+ACME FOODS BV     ← the name lands in the wrong element
```

## 3. The UNT segment count does not match

`UNT` carries the number of segments in the message, including `UNH` and `UNT`
themselves. Adding a line by hand without updating the count makes the receiving
system reject the message as a checksum failure.

## 4. Wrong date format code

The third element of `DTM` states the format. Confusing `102` with `203` makes
the time part read as if it belonged to the date:

```
DTM+137:20260117:102'      ← 17 Jan 2026
DTM+137:202601171030:203'  ← 17 Jan 2026 10:30
```

## 5. Missing currency

`PRI` and `MOA` carry no currency; it comes from the `CUX` segment at message
level. Without a `CUX` the amounts are ambiguous and the receiver applies its own
default — on invoices, a mistake with a real cost.

## 6. MOA qualifiers get mixed up

The summary section holds several `MOA` segments, each a different total: `79`
goods total, `124` tax, `77` grand total, `9` amount payable. Treating the first
`MOA` as the total without reading the qualifier is a common error.

## 7. Character set mismatch

`UNOA` in the `UNB` accepts only uppercase letters and digits. Sending text with
accented characters as `UNOA` corrupts it at the other end; `UNOC` should be used
for Latin-1.

## How to check

Opening the file in ediviewer highlights the segment tags and lists every element
of the selected line with a name against it. An element sitting opposite a label
you did not expect usually points to one of the mistakes above.
""",
        },
    },
]
