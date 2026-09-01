// Örnek EDI dosyaları — mesaj tipine göre.
//
// Gömülü tutulur; böylece sunucuya ek istek gitmez ve çevrimdışı da çalışır.
// (samples/ klasöründeki dosyalar uygulamadan yüklenmez; onlar elle
// sürükle-bırak denemeleri için durur.)
//
// TEK BİR SENARYO: bütün örnekler aynı iş akışını anlatır — ACME FOODS BV
// (tedarikçi, NL) ile MEGA RETAIL AS (alıcı, TR) arasındaki PO-2026-0042
// numaralı sipariş. Belgeler birbirine RFF referanslarıyla bağlıdır:
//
//   ORDERS ─► ORDRSP ─► ORDCHG ─► DESADV ─► RECADV ─► INVOIC ─► REMADV
//
// Zincir boyunca sayılar da tutarlıdır: 2. kalemden 120 adet istenir, ORDRSP
// 100 adet onaylar, DESADV 100 sevk eder, RECADV 96 kabul eder (4 adet hasarlı),
// INVOIC sevk edileni faturalar, REMADV hasarlı adedin bedelini düşer.
// Böylece örnek seti aynı zamanda EDI akışını anlatan bir örnek olur.

const SUPPLIER = 'NAD+SU+8712345678901::9++ACME FOODS BV+Havenweg 5+ROTTERDAM+3011AA+NL';
const BUYER = 'NAD+BY+8798765432109::9++MEGA RETAIL AS+Barbaros Bulvari 12+ISTANBUL+34353+TR';
const DELIVERY = 'NAD+DP+8798765432199::9++MEGA DEPO+Organize Sanayi 4+GEBZE+41400+TR';

/**
 * Desteklenen örnekler. Sıra, seçim ekranındaki sırayla aynıdır.
 * `standard` alanı listeyi UN/EDIFACT ve ANSI X12 gruplarına ayırır.
 */
export const SAMPLE_CATALOG = [
  // ---------------------------------------------------------------------
  // 1. ORDERS — siparişin kendisi. Zincirin başlangıcı.
  // ---------------------------------------------------------------------
  {
    type: 'ORDERS',
    pdf: true,
    excel: false,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8712345678901:14+8798765432109:14+260117:1030+REF00042'
UNH+ME000001+ORDERS:D:96A:UN:EAN008'
BGM+220+PO-2026-0042+9'
DTM+137:20260117:102'
DTM+2:20260125:102'
FTX+AAI+++DELIVERY BETWEEN 08.00 AND 16.00'
RFF+CT:CONTRACT-2025-88'
${BUYER}'
${SUPPLIER}'
${DELIVERY}'
CTA+PD+:PURCHASING DEPARTMENT'
COM+purchasing@megaretail.com:EM'
CUX+2:EUR:9'
LIN+1++5410013101234:EN'
IMD+F++:::DARK CHOCOLATE BAR 100G'
QTY+21:480:PCE'
PRI+AAA:1.85'
MOA+203:888.00'
LIN+2++5410013109999:EN'
IMD+F++:::HAZELNUT SPREAD 400G'
QTY+21:120:PCE'
PRI+AAA:3.40'
ALC+A++++DI::VOLUME DISCOUNT'
PCD+3:5'
MOA+203:408.00'
UNS+S'
MOA+79:1296.00'
MOA+124:259.20'
MOA+77:1555.20'
CNT+2:2'
UNT+30+ME000001'
UNZ+1+REF00042'
`,
  },

  // ---------------------------------------------------------------------
  // 2. ORDRSP — satır bazında yanıt: 1. kalem tam kabul (5),
  //    2. kalem değişiklik önerisi (3) — stokta 100 adet var.
  // ---------------------------------------------------------------------
  {
    type: 'ORDRSP',
    pdf: true,
    excel: false,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8712345678901:14+8798765432109:14+260117:1530+ORS042'
UNH+1+ORDRSP:D:96A:UN:EAN008'
BGM+231+ORS-2026-0042+9'
DTM+137:20260117:102'
RFF+ON:PO-2026-0042'
${SUPPLIER}'
${BUYER}'
CUX+2:EUR:9'
LIN+1+5+5410013101234:EN'
IMD+F++:::DARK CHOCOLATE BAR 100G'
QTY+21:480:PCE'
QTY+12:480:PCE'
PRI+AAA:1.85'
LIN+2+3+5410013109999:EN'
IMD+F++:::HAZELNUT SPREAD 400G'
QTY+21:120:PCE'
QTY+12:100:PCE'
PRI+AAA:3.40'
FTX+AAI+++ONLY 100 UNITS AVAILABLE FROM STOCK'
UNT+19+1'
UNZ+1+ORS042'
`,
  },

  // ---------------------------------------------------------------------
  // 3. ORDCHG — sipariş değişikliği. BGM'in 3. elemanı 4 = değişiklik.
  //    1. kalem 600'e çıkar (3), 2. kalem iptal (7).
  // ---------------------------------------------------------------------
  {
    type: 'ORDCHG',
    pdf: true,
    excel: false,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8798765432109:14+8712345678901:14+260118:0830+POC042'
UNH+1+ORDCHG:D:96A:UN:EAN008'
BGM+220+PO-2026-0042+4'
DTM+137:20260118:102'
DTM+2:20260127:102'
RFF+ON:PO-2026-0042'
${BUYER}'
${SUPPLIER}'
${DELIVERY}'
CUX+2:EUR:9'
LIN+1+3+5410013101234:EN'
IMD+F++:::DARK CHOCOLATE BAR 100G'
QTY+21:600:PCE'
PRI+AAA:1.85'
MOA+203:1110.00'
LIN+2+7+5410013109999:EN'
IMD+F++:::HAZELNUT SPREAD 400G'
QTY+21:0:PCE'
FTX+AAI+++LINE 2 CANCELLED, LINE 1 INCREASED TO 600'
UNS+S'
MOA+79:1110.00'
CNT+2:2'
UNT+22+1'
UNZ+1+POC042'
`,
  },

  // ---------------------------------------------------------------------
  // 4. DESADV — sevk ihbarı. GIN+BJ palet SSCC'sini taşır ve
  //    kendisinden SONRA gelen kalemlere uygulanır.
  // ---------------------------------------------------------------------
  {
    type: 'DESADV',
    pdf: true,
    excel: false,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8712345678901:14+8798765432109:14+260118:0915+DN0088'
UNH+1+DESADV:D:96A:UN:EAN005'
BGM+351+DN-2026-0088+9'
DTM+137:20260118:102'
DTM+11:20260118:102'
RFF+ON:PO-2026-0042'
${SUPPLIER}'
${DELIVERY}'
TDT+20++30++ACME LOGISTICS'
CPS+1'
PAC+2+:52+PAL'
PCI+33E'
GIN+BJ+340123456789012345'
LIN+1++5410013101234:EN'
IMD+F++:::DARK CHOCOLATE BAR 100G'
QTY+12:480:PCE'
LIN+2++5410013109999:EN'
IMD+F++:::HAZELNUT SPREAD 400G'
QTY+12:100:PCE'
CNT+2:2'
UNT+20+1'
UNZ+1+DN0088'
`,
  },

  // ---------------------------------------------------------------------
  // 5. RECADV — mal kabul. QTY 12 sevk edilen, QTY 194 kabul edilen:
  //    2. kalemde 4 adet fark var (hasar).
  // ---------------------------------------------------------------------
  {
    type: 'RECADV',
    pdf: true,
    excel: false,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8798765432109:14+8712345678901:14+260119:1420+RA0091'
UNH+1+RECADV:D:96A:UN:EAN007'
BGM+632+RA-2026-0091+9'
DTM+137:20260119:102'
RFF+DQ:DN-2026-0088'
${SUPPLIER}'
${DELIVERY}'
LIN+1++5410013101234:EN'
IMD+F++:::DARK CHOCOLATE BAR 100G'
QTY+12:480:PCE'
QTY+194:480:PCE'
LIN+2++5410013109999:EN'
IMD+F++:::HAZELNUT SPREAD 400G'
QTY+12:100:PCE'
QTY+194:96:PCE'
FTX+AAO+++4 UNITS DAMAGED ON ARRIVAL'
CNT+2:2'
UNT+17+1'
UNZ+1+RA0091'
`,
  },

  // ---------------------------------------------------------------------
  // 6. INVOIC — fatura. Sevk edilen miktar faturalanır (100, 120 değil).
  //    Özet MOA'ları: 79 mal, 124 vergi, 77 genel toplam, 9 ödenecek.
  // ---------------------------------------------------------------------
  {
    type: 'INVOIC',
    pdf: true,
    excel: false,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8712345678901:14+8798765432109:14+260120:1100+INV777'
UNH+1+INVOIC:D:96A:UN:EAN008'
BGM+380+FT-2026-777+9'
DTM+137:20260120:102'
DTM+35:20260118:102'
RFF+ON:PO-2026-0042'
RFF+DQ:DN-2026-0088'
NAD+SE+8712345678901::9++ACME FOODS BV+Havenweg 5+ROTTERDAM+3011AA+NL'
${BUYER}'
FII+RB+NL91ABNA0417164300:ACME FOODS BV:::ABN AMRO'
CUX+2:EUR:9'
PAT+1++5:3:D:30'
LIN+1++5410013101234:EN'
IMD+F++:::DARK CHOCOLATE BAR 100G'
QTY+47:480:PCE'
PRI+AAA:1.85'
MOA+203:888.00'
TAX+7+VAT+++:::20'
LIN+2++5410013109999:EN'
IMD+F++:::HAZELNUT SPREAD 400G'
QTY+47:100:PCE'
PRI+AAA:3.40'
MOA+203:340.00'
TAX+7+VAT+++:::20'
UNS+S'
MOA+79:1228.00'
MOA+124:245.60'
MOA+77:1473.60'
MOA+9:1473.60'
TAX+7+VAT+++:::20'
UNT+30+1'
UNZ+1+INV777'
`,
  },

  // ---------------------------------------------------------------------
  // 7. REMADV — ödeme bildirimi. Başlıktaki MOA+12 toplam ödemedir ve
  //    DOC'tan ÖNCE gelmek zorundadır. AJT+1+71 = hasar nedeniyle kesinti.
  // ---------------------------------------------------------------------
  {
    type: 'REMADV',
    pdf: true,
    excel: false,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8798765432109:14+8712345678901:14+260220:0900+RM0031'
UNH+1+REMADV:D:96A:UN:EAN010'
BGM+481+RM-2026-0031+9'
DTM+137:20260220:102'
DTM+203:20260222:102'
NAD+PR+8798765432109::9++MEGA RETAIL AS+Barbaros Bulvari 12+ISTANBUL+34353+TR'
NAD+PE+8712345678901::9++ACME FOODS BV+Havenweg 5+ROTTERDAM+3011AA+NL'
CUX+2:EUR:9'
MOA+12:1460.00'
FII+RB+NL91ABNA0417164300:ACME FOODS BV:::ABN AMRO'
DOC+380+FT-2026-777'
DTM+137:20260120:102'
MOA+12:1460.00'
MOA+19:13.60'
AJT+1+71'
UNT+15+1'
UNZ+1+RM0031'
`,
  },

  // ---------------------------------------------------------------------
  // 8. SLSRPT — satış raporu. Tek PDF + Excel üreten tip.
  //    QTY 152 satılan miktar, DTM 356/357 dönem başı ve sonu.
  // ---------------------------------------------------------------------
  {
    type: 'SLSRPT',
    pdf: true,
    excel: true,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8798765432109:14+8712345678901:14+260201:0800+SR001'
UNH+1+SLSRPT:D:96A:UN'
BGM+563+SR-2026-01+9'
DTM+137:20260201:102'
DTM+356:20260101:102'
DTM+357:20260131:102'
NAD+SE+8798765432109::9++MEGA RETAIL AS+Barbaros Bulvari 12+ISTANBUL+34353+TR'
${SUPPLIER}'
NAD+ST+8798765432199::9++MEGA STORE 42+Bagdat Caddesi 100+ISTANBUL+34728+TR'
CUX+2:EUR:9'
LIN+1++5410013101234:EN'
IMD+F++:::DARK CHOCOLATE BAR 100G'
QTY+152:372:PCE'
PRI+AAA:2.49'
MOA+203:926.28'
LIN+2++5410013109999:EN'
IMD+F++:::HAZELNUT SPREAD 400G'
QTY+152:88:PCE'
PRI+AAA:4.10'
MOA+203:360.80'
UNS+S'
MOA+79:1287.08'
CNT+2:2'
UNT+23+1'
UNZ+1+SR001'
`,
  },

  // ---------------------------------------------------------------------
  // 9. PRICAT — fiyat kataloğu. Yalnızca Excel üretir.
  //    PRI nitelikçileri: AAA net, AAB brüt, AAE tavsiye edilen perakende.
  // ---------------------------------------------------------------------
  {
    type: 'PRICAT',
    pdf: false,
    excel: true,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8712345678901:14+8798765432109:14+260105:0700+PC001'
UNH+1+PRICAT:D:96A:UN:EAN006'
BGM+9+PC-2026-01+9'
DTM+137:20260105:102'
DTM+194:20260201:102'
${SUPPLIER}'
${BUYER}'
CUX+2:EUR:9'
LIN+1++5410013101234:EN'
IMD+F++:::DARK CHOCOLATE BAR 100G'
ALI+NL'
PAC+24+:52+CT'
PRI+AAA:1.85'
PRI+AAB:2.10'
PRI+AAE:2.49'
LIN+2++5410013109999:EN'
IMD+F++:::HAZELNUT SPREAD 400G'
ALI+NL'
PAC+12+:52+CT'
PRI+AAA:3.40'
PRI+AAB:3.85'
PRI+AAE:4.10'
UNT+22+1'
UNZ+1+PC001'
`,
  },

  // ---------------------------------------------------------------------
  // 10. DELJIT — tam zamanında teslimat çağrısı. SEQ her çağrı penceresini,
  //     GIR çağrı numarasını, DTM+2 istenen teslim tarihini taşır.
  // ---------------------------------------------------------------------
  {
    type: 'DELJIT',
    pdf: true,
    excel: false,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8798765432109:14+8712345678901:14+260210:0600+DJ0007'
UNH+1+DELJIT:D:96A:UN:EAN008'
BGM+241+DJ-2026-0007+9'
DTM+137:20260210:102'
${BUYER}'
NAD+SE+8712345678901::9++ACME FOODS BV+Havenweg 5+ROTTERDAM+3011AA+NL'
LIN+1++5410013101234:EN'
IMD+F++:::DARK CHOCOLATE BAR 100G'
LOC+11+GEBZE DOCK 3'
FTX+AAI+++PALLETISED, DO NOT STACK'
SEQ++1'
QTY+1:240:PCE'
DTM+2:20260216:102'
GIR+1+CALL-2026-0451:AAN'
SEQ++2'
QTY+1:240:PCE'
DTM+2:20260223:102'
GIR+1+CALL-2026-0452:AAN'
UNT+18+1'
UNZ+1+DJ0007'
`,
  },

  // ---------------------------------------------------------------------
  // 11. IFTMIN — nakliye talimatı. LOC+9 yükleme, LOC+11 boşaltma yeri;
  //     NAD+CZ gönderen, NAD+CN alıcı; GID/PAC/MEA/HAN yük kalemleri.
  // ---------------------------------------------------------------------
  {
    type: 'IFTMIN',
    pdf: true,
    excel: false,
    standard: 'EDIFACT',
    content: `UNB+UNOC:3+8712345678901:14+9012345678903:14+260118:1000+TR0015'
UNH+1+IFTMIN:D:96A:UN'
BGM+610+TR-2026-0015+9'
DTM+137:20260118:102'
DTM+133:20260118:102'
DTM+64:20260119:102'
FTX+AAI+++KEEP BETWEEN 2 AND 8 DEGREES CELSIUS'
NAD+CZ+8712345678901::9++ACME FOODS BV+Havenweg 5+ROTTERDAM+3011AA+NL'
NAD+CN+8798765432199::9++MEGA DEPO+Organize Sanayi 4+GEBZE+41400+TR'
LOC+9+ROTTERDAM'
LOC+11+GEBZE'
TDT+20++30++ACME LOGISTICS'
EQD+CN+ACLU1234567+++2'
GID+1+24:CT'
HAN+CO'
PAC+24+:52+CT'
MEA+AAE++KGM:480'
GID+2+12:CT'
PAC+12+:52+CT'
MEA+AAE++KGM:180'
CNT+11:2'
UNT+21+1'
UNZ+1+TR0015'
`,
  },

  // =====================================================================
  // ANSI ASC X12 — Kuzey Amerika karşılıkları.
  //
  // Ayraçlar EDIFACT'teki gibi UNA'dan değil, ISA'nın KONUMUNDAN okunur:
  // ISA sabit 106 karakterdir, eleman ayracı 3. karakter, bileşen ayracı
  // 104., segment sonlandırıcı 105. karakterdir. Bu yüzden ISA satırındaki
  // boşluk dolgusu süs değildir — kısaltılırsa dosya ayrıştırılamaz.
  //
  // Bu tiplerin PDF/Excel üreticisi yoktur; yalnızca görüntülenir ve
  // JSON/XML'e çevrilebilirler.
  // =====================================================================

  // 12. 850 — EDIFACT ORDERS karşılığı
  {
    type: '850',
    pdf: false,
    excel: false,
    standard: 'X12',
    content: `ISA*00*          *00*          *ZZ*ACMEFOODS      *ZZ*MEGARETAIL     *260117*1030*U*00401*000000905*0*P*>~
GS*PO*ACMEFOODS*MEGARETAIL*20260117*1030*1*X*004010~
ST*850*0001~
BEG*00*SA*PO-2026-0042**20260117~
REF*CT*CONTRACT-2025-88~
DTM*002*20260125~
N1*BY*MEGA RETAIL INC*UL*0798765432109~
N3*100 Market Street~
N4*CHICAGO*IL*60601*US~
N1*SU*ACME FOODS LLC*UL*0712345678901~
N3*5 Harbor Road~
N4*NEWARK*NJ*07102*US~
PO1*1*480*EA*1.85**UP*840013101234~
PID*F****DARK CHOCOLATE BAR 100G~
PO1*2*120*EA*3.40**UP*840013109999~
PID*F****HAZELNUT SPREAD 400G~
CTT*2~
SE*16*0001~
GE*1*1~
IEA*1*000000905~
`,
  },

  // 13. 810 — EDIFACT INVOIC karşılığı. TDS tutarı kuruş cinsindendir
  //     (147360 = 1473.60), X12'de ondalık nokta yazılmaz.
  {
    type: '810',
    pdf: false,
    excel: false,
    standard: 'X12',
    content: `ISA*00*          *00*          *ZZ*ACMEFOODS      *ZZ*MEGARETAIL     *260120*1100*U*00401*000000912*0*P*>~
GS*IN*ACMEFOODS*MEGARETAIL*20260120*1100*2*X*004010~
ST*810*0002~
BIG*20260120*FT-2026-777*20260117*PO-2026-0042~
REF*DP*DN-2026-0088~
N1*SE*ACME FOODS LLC*UL*0712345678901~
N3*5 Harbor Road~
N4*NEWARK*NJ*07102*US~
N1*BY*MEGA RETAIL INC*UL*0798765432109~
N3*100 Market Street~
N4*CHICAGO*IL*60601*US~
ITD*01*3*2**10**30~
IT1*1*480*EA*1.85**UP*840013101234~
PID*F****DARK CHOCOLATE BAR 100G~
IT1*2*100*EA*3.40**UP*840013109999~
PID*F****HAZELNUT SPREAD 400G~
TXI*ST*245.60~
TDS*147360~
CTT*2~
SE*18*0002~
GE*1*2~
IEA*1*000000912~
`,
  },

  // 14. 856 — EDIFACT DESADV karşılığı. X12'de sevkiyat HL hiyerarşisiyle
  //     kurulur: S (sevkiyat) > O (sipariş) > I (kalem).
  {
    type: '856',
    pdf: false,
    excel: false,
    standard: 'X12',
    content: `ISA*00*          *00*          *ZZ*ACMEFOODS      *ZZ*MEGARETAIL     *260118*0915*U*00401*000000908*0*P*>~
GS*SH*ACMEFOODS*MEGARETAIL*20260118*0915*3*X*004010~
ST*856*0003~
BSN*00*DN-2026-0088*20260118*0915~
HL*1**S~
TD1*CTN25*2****G*660*LB~
TD5**2*ACMELOG*M~
REF*BM*BOL-2026-0088~
DTM*011*20260118~
N1*SF*ACME FOODS LLC*UL*0712345678901~
N1*ST*MEGA DC GEBZE*UL*0798765432199~
HL*2*1*O~
PRF*PO-2026-0042~
HL*3*2*I~
LIN**UP*840013101234~
SN1**480*EA~
PID*F****DARK CHOCOLATE BAR 100G~
HL*4*2*I~
LIN**UP*840013109999~
SN1**100*EA~
PID*F****HAZELNUT SPREAD 400G~
CTT*4~
SE*21*0003~
GE*1*3~
IEA*1*000000908~
`,
  },

  // 15. 997 — EDIFACT CONTRL karşılığı. Gelen 850'nin teknik onayı:
  //     AK5*A satır grubu kabul, AK9*A tüm grup kabul.
  {
    type: '997',
    pdf: false,
    excel: false,
    standard: 'X12',
    content: `ISA*00*          *00*          *ZZ*MEGARETAIL     *ZZ*ACMEFOODS      *260117*1045*U*00401*000000906*0*P*>~
GS*FA*MEGARETAIL*ACMEFOODS*20260117*1045*4*X*004010~
ST*997*0004~
AK1*PO*1~
AK2*850*0001~
AK5*A~
AK9*A*1*1*1~
SE*6*0004~
GE*1*4~
IEA*1*000000906~
`,
  },
];

/** Tip koduna göre erişim: SAMPLES.ORDERS gibi */
export const SAMPLES = Object.fromEntries(SAMPLE_CATALOG.map((s) => [s.type, s]));

/** Açılışta ve seçim yapılmamışken kullanılan tip */
export const DEFAULT_SAMPLE_TYPE = 'ORDERS';

/** Dosya adı dile bağımsızdır: ORDERS_sample.edi, 850_sample.edi ... */
export function sampleFileName(type) {
  return `${type}_sample.edi`;
}

/** Verilen tipin içeriği; tip bilinmiyorsa varsayılana düşer. */
export function sampleContent(type) {
  return (SAMPLES[type] ?? SAMPLES[DEFAULT_SAMPLE_TYPE]).content;
}

// Geriye dönük uyumluluk (js/app.js ve ?selftest=1 hâlâ bunları kullanıyor)
export const SAMPLE_FILE_NAME = sampleFileName(DEFAULT_SAMPLE_TYPE);
export const SAMPLE_EDI = sampleContent(DEFAULT_SAMPLE_TYPE);
