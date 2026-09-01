// js/sampleData.js içindeki örnek dosyaları denetler:
//
//   · sayaç segmenti (EDIFACT UNT / X12 SE) doğru mu
//   · X12'de ISA tam 106 karakter mi (ayraçlar konumdan okunuyor)
//   · mesaj tipi doğru tespit ediliyor mu
//   · PDF/Excel izinleri ve üretici yönlendirmesi doğru mu
//     (bir tip adının başka bir örneğin serbest metninde geçmesi bunu bozar)
//   · katalogdaki pdf/excel bayrakları gerçek mantıkla ayrışmış mı
//   · üreticiler örnekten gerçekten veri çıkarıyor mu
//   · örnekler dönüşüm modülünde kayıpsız round-trip yapıyor mu
//
// Kullanım:  node tools/check_samples.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const store = {};
globalThis.localStorage = { getItem: (k) => store[k] ?? null, setItem: (k, v) => { store[k] = v; } };
globalThis.fetch = async (url) => {
  const p = `${ROOT}/${String(url)}`;
  if (!fs.existsSync(p)) return { ok: false, statusText: 'missing' };
  return { ok: true, json: async () => JSON.parse(fs.readFileSync(p, 'utf8')) };
};

const { loc } = await import(`${ROOT}/js/i18n.js`);
await loc.loadTranslations();

const { SAMPLE_CATALOG } = await import(`${ROOT}/js/sampleData.js`);
const { EDIParser } = await import(`${ROOT}/js/parser.js`);
const { PDFExportManager } = await import(`${ROOT}/js/pdfExport.js`);
const { CSVExportManager } = await import(`${ROOT}/js/csvExport.js`);
const { roundTripEDI } = await import(`${ROOT}/js/ediSyntax.js`);

// --- app.js:getExportPermissions birebir kopyası (tek doğruluk kaynağı orası) ---
function exportPermissions(content) {
  if (content.includes('SLSRPT')) return { pdf: true, excel: true };
  if (content.includes('PRICAT')) return { pdf: false, excel: true };
  const pdfGroup = ['ORDERS', 'ORDRSP', 'ORDCHG', 'DESADV', 'RECADV', 'IFTMIN', 'INVOIC', 'REMADV', 'DELJIT'];
  for (const t of pdfGroup) if (content.includes(t)) return { pdf: true, excel: false };
  return { pdf: false, excel: false };
}

// --- pdfExport.js router sırası ---
const PDF_ROUTER = ['ORDCHG', 'ORDRSP', 'ORDERS', 'DESADV', 'RECADV', 'IFTMIN', 'INVOIC', 'REMADV', 'DELJIT', 'SLSRPT'];
function pdfRoutesTo(content) {
  for (const t of PDF_ROUTER) if (content.includes(t)) return t;
  return 'GENERIC';
}
function csvRoutesTo(content) {
  if (content.includes('SLSRPT')) return 'SLSRPT';
  if (content.includes('PRICAT')) return 'PRICAT';
  return 'GENERIC';
}

// Her tipin PDF/CSV çıktısında GÖRÜNMESİ gereken, veriden türeyen dizgeler
const EXPECT = {
  ORDERS: ['PO-2026-0042', 'DARK CHOCOLATE BAR 100G', 'HAZELNUT SPREAD 400G', '1296.00', 'VOLUME DISCOUNT'],
  ORDRSP: ['ORS-2026-0042', 'DARK CHOCOLATE BAR 100G', 'ONLY 100 UNITS AVAILABLE FROM STOCK'],
  ORDCHG: ['PO-2026-0042', 'DARK CHOCOLATE BAR 100G'],
  DESADV: ['DN-2026-0088', 'DARK CHOCOLATE BAR 100G', '340123456789012345'],
  RECADV: ['RA-2026-0091', 'DARK CHOCOLATE BAR 100G', '96'],
  INVOIC: ['FT-2026-777', 'DARK CHOCOLATE BAR 100G', '1473.60', 'NL91ABNA0417164300', 'PO-2026-0042'],
  REMADV: ['RM-2026-0031', 'FT-2026-777', '1460.00', '13.60'],
  SLSRPT: ['SR-2026-01', 'DARK CHOCOLATE BAR 100G', '372'],
  DELJIT: ['DJ-2026-0007', 'DARK CHOCOLATE BAR 100G', 'CALL-2026-0451', 'PALLETISED'],
  IFTMIN: ['TR-2026-0015', 'ROTTERDAM', 'GEBZE'],
  PRICAT: [],
};
const CSV_EXPECT = {
  SLSRPT: ['5410013101234', 'DARK CHOCOLATE BAR 100G', '372', '926.28'],
  PRICAT: ['5410013101234', 'DARK CHOCOLATE BAR 100G', '1.85', '2.10', '2.49', 'NL', '24'],
};

let failures = 0;
const fail = (type, msg) => { failures++; console.log(`  ✗ ${type}: ${msg}`); };

console.log('tip       UNT  tespit                                    PDF/XLS  yonlendirme  round-trip');
console.log('─'.repeat(100));

for (const { type, standard, content, pdf, excel } of SAMPLE_CATALOG) {
  const segments = EDIParser.parse(content);
  const tags = segments.map((s) => s.tag);
  const isX12 = standard === 'X12';

  // --- 1. sayac segmenti: EDIFACT'te UNH..UNT, X12'de ST..SE (ikisi dahil) ---
  const openTag = isX12 ? 'ST' : 'UNH';
  const closeTag = isX12 ? 'SE' : 'UNT';
  const iOpen = tags.indexOf(openTag);
  const iClose = tags.indexOf(closeTag);
  const expectedUNT = iClose - iOpen + 1;
  const declaredUNT = parseInt(segments[iClose].elements[1], 10);
  const untOK = expectedUNT === declaredUNT;

  // --- 1b. X12'de ISA tam 106 karakter olmali (ayraclar konumdan okunuyor) ---
  let isaOK = true;
  if (isX12) {
    const isaLine = content.split('\n')[0];
    isaOK = isaLine.length === 106;
    if (!isaOK) fail(type, `ISA ${isaLine.length} karakter, 106 olmali`);
  }

  // --- 2. mesaj tipi tespiti ---
  const detected = EDIParser.detectMessageType(content);
  const detectOK = detected === loc.localize(`type_${type}`);

  // --- 3. izinler ve yonlendirme ---
  const perms = exportPermissions(content);
  const pdfTarget = pdfRoutesTo(content);
  const csvTarget = csvRoutesTo(content);
  const routeOK = perms.pdf ? pdfTarget === type : true;

  // --- 4. round-trip ---
  const rt = roundTripEDI(content);

  console.log(
    `${type.padEnd(9)} ${untOK && isaOK ? ' ok' : `!${declaredUNT}≠${expectedUNT}`.padEnd(3)}  ` +
    `${(detectOK ? detected : `YANLIS: ${detected}`).padEnd(41)} ` +
    `${(perms.pdf ? 'PDF' : '---')}/${(perms.excel ? 'XLS' : '---')}  ` +
    `${(perms.pdf ? pdfTarget : csvTarget).padEnd(12)} ${rt.ok ? 'ok' : 'FARKLI'}`
  );

  if (!untOK) fail(type, `${closeTag}+${declaredUNT} yazili, ${expectedUNT} olmali`);
  if (!detectOK) fail(type, `mesaj tipi yanlis tespit edildi: ${detected}`);
  if (!routeOK) fail(type, `PDF ureticisi ${pdfTarget}'e yonlendi, ${type} olmali`);
  if (!rt.ok) fail(type, `round-trip bozuk (diffAt=${rt.diffAt})`);

  // --- 4b. katalogdaki pdf/excel bayraklari gercek mantikla ayrismasin ---
  if (pdf !== perms.pdf) fail(type, `katalogda pdf:${pdf}, gercekte ${perms.pdf}`);
  if (excel !== perms.excel) fail(type, `katalogda excel:${excel}, gercekte ${perms.excel}`);

  // --- 5. ureticiler gercekten veri cikariyor mu ---
  if (perms.pdf) {
    const html = PDFExportManager.buildHTML(segments);
    for (const needle of EXPECT[type] ?? []) {
      if (!html.includes(needle)) fail(type, `PDF ciktisinda "${needle}" yok`);
    }
  }
  if (perms.excel) {
    const csv = CSVExportManager.generateCSV(segments);
    for (const needle of CSV_EXPECT[type] ?? []) {
      if (!csv.includes(needle)) fail(type, `CSV ciktisinda "${needle}" yok`);
    }
  }
}

console.log('─'.repeat(100));
console.log(failures ? `${failures} sorun bulundu` : `${SAMPLE_CATALOG.length} ornek: tum denetimler gecti`);
process.exit(failures ? 1 : 0);
