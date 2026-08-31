// Dönüşüm motoru — EDI <-> JSON <-> XML.
//
// Dört yönün tamamı (EDI->JSON, JSON->EDI, EDI->XML, XML->EDI) tek bir kanonik
// modelden geçer; okuyucular ve yazıcılar birbirinden bağımsızdır:
//
//   .edi  ─┐                                    ┌─  .edi
//   .json ─┼─ EdiModel { syntax, segments } ─┼─  .json
//   .xml  ─┘                                    └─  .xml
//
// Model js/ediSyntax.js'te tanımlıdır ve ayraç/kaçış/satır sonu bilgisini de
// taşır; şemanın kayıpsız olmasının nedeni budur.
import { loc, L } from './i18n.js';
import { EDIParser } from './parser.js';
import { analyzeElement } from './segmentDetail.js';
import { parseEDI, serializeEDI, looksLikeEDI } from './ediSyntax.js';

export const SCHEMA_JSON = 'ediviewer-edi-json';
export const SCHEMA_XML = 'ediviewer-edi-xml';
export const SCHEMA_VERSION = 1;

/** Dönüşüm hatası — `key` doğrudan bir i18n anahtarıdır. */
export class ConvertError extends Error {
  constructor(key, detail) {
    super(key);
    this.name = 'ConvertError';
    this.key = key;
    this.detail = detail ?? '';
  }
}

// Satır sonları şemada simgesel tutulur: XML öznitelik değerlerinde gerçek
// satır sonu normalize edilir, bu da round-trip'i sessizce bozardı.
const LB_NAME = { '\r\n': 'CRLF', '\n': 'LF', '\r': 'CR', '': 'NONE' };
const LB_VALUE = { CRLF: '\r\n', LF: '\n', CR: '\r', NONE: '' };

// =========================================================================
// MARK: - BİÇİM ALGILAMA
// =========================================================================

/**
 * İçeriğe (ve varsa dosya adına) bakarak biçimi belirler.
 * @returns {'edi'|'json'|'xml'}
 */
export function detectFormat(text, fileName) {
  const head = String(text ?? '').replace(/^﻿/, '').trimStart();
  if (head.startsWith('{')) return 'json';
  if (head.startsWith('<')) return 'xml';
  if (looksLikeEDI(head)) return 'edi';
  return languageOfName(fileName);
}

/** Dosya adının uzantısından belge dili. */
export function languageOfName(fileName) {
  const name = String(fileName ?? '').toLowerCase();
  if (name.endsWith('.json')) return 'json';
  if (name.endsWith('.xml')) return 'xml';
  return 'edi';
}

/** İçerik bizim dönüşüm şemamıza mı ait? (aç-ve-dönüştür teklifi için) */
export function isConversionDocument(text) {
  const head = String(text ?? '').replace(/^﻿/, '').trimStart();
  if (head.startsWith('{')) return head.includes(SCHEMA_JSON);
  if (head.startsWith('<')) return head.includes(SCHEMA_XML);
  return false;
}

// =========================================================================
// MARK: - GENEL API
// =========================================================================

export const ConvertManager = {
  /**
   * @param {string} text kaynak içerik
   * @param {{from:string, to:string, annotated?:boolean, pretty?:boolean}} opts
   * @returns {{text:string, roundTrip:{ok:boolean, reason?:string}}}
   */
  convert(text, { from, to, annotated = false, pretty = true }) {
    if (String(text ?? '').trim() === '') throw new ConvertError('conv_err_empty');

    const model = toModel(text, from);
    if (!model.segments.length) throw new ConvertError('conv_err_not_edi');

    const output = fromModel(model, to, { annotated, pretty });
    return { text: output, roundTrip: verify(text, output, model, from, to) };
  },

  toModel,
  fromModel,
};

/**
 * Dönüşümün kayıpsızlığını ölçer.
 *
 * Karşılaştırma her zaman EDI bayt biçimi üzerinden yapılır; çünkü asıl soru
 * "veri ve sözdizimi korundu mu" sorusudur. JSON/XML kaynaklarında ham metin
 * karşılaştırması yanıltıcı olurdu (girinti, anahtar sırası, açıklama alanları
 * kaynakta farklı olabilir).
 */
function verify(sourceText, outputText, model, from, to) {
  try {
    // 1. Kaynak EDI ise: ayrıştırma baytı baytına geri gelebiliyor mu?
    if (from === 'edi' && serializeEDI(model) !== sourceText) {
      return { ok: false, reason: 'parse' };
    }
    // 2. Çıktı tekrar modele çevrilince aynı EDI'yi mi veriyor?
    if (serializeEDI(toModel(outputText, to)) !== serializeEDI(model)) {
      return { ok: false, reason: 'back' };
    }
    return { ok: true };
  } catch (e) {
    return { ok: false, reason: e instanceof ConvertError ? e.key : 'error' };
  }
}

function toModel(text, format) {
  if (format === 'json') return jsonToModel(text);
  if (format === 'xml') return xmlToModel(text);
  return parseEDI(text);
}

function fromModel(model, format, opts) {
  if (format === 'json') return modelToJSON(model, opts);
  if (format === 'xml') return modelToXML(model, opts);
  return serializeEDI(model);
}

// =========================================================================
// MARK: - SÖZDİZİMİ BLOĞU (şema <-> model)
// =========================================================================

function syntaxToPlain(sx) {
  return {
    component: sx.component,
    element: sx.element,
    decimal: sx.decimal,
    release: sx.release ?? '',
    repetition: sx.repetition ?? '',
    terminator: sx.terminator,
    una: !!sx.unaPresent,
    unaLineBreak: !!sx.unaLineBreak,
    lineBreak: LB_NAME[sx.lineBreak] ?? nearestLineBreakName(sx.lineBreak),
    leadingLineBreak: !!sx.leadingLineBreak,
    trailingLineBreak: !!sx.trailingLineBreak,
    bom: !!sx.bom,
  };
}

function nearestLineBreakName(lb) {
  const s = String(lb ?? '');
  if (s.includes('\r\n')) return 'CRLF';
  if (s.includes('\n')) return 'LF';
  if (s.includes('\r')) return 'CR';
  return 'NONE';
}

function syntaxFromPlain(raw, standard) {
  const s = raw || {};
  const isX12 = standard === 'X12';
  return {
    component: pick(s.component, isX12 ? '>' : ':'),
    element: pick(s.element, isX12 ? '*' : '+'),
    decimal: pick(s.decimal, '.'),
    release: s.release ? String(s.release)[0] : null,
    repetition: s.repetition ? String(s.repetition)[0] : null,
    terminator: pick(s.terminator, isX12 ? '~' : "'"),
    unaPresent: bool(s.una),
    unaLineBreak: bool(s.unaLineBreak),
    lineBreak: LB_VALUE[String(s.lineBreak ?? 'LF').toUpperCase()] ?? '\n',
    leadingLineBreak: bool(s.leadingLineBreak),
    trailingLineBreak: s.trailingLineBreak === undefined ? true : bool(s.trailingLineBreak),
    bom: bool(s.bom),
  };
}

const pick = (value, fallback) =>
  value === undefined || value === null || value === '' ? fallback : String(value)[0];

const bool = (value) => value === true || value === 'true' || value === '1';

// =========================================================================
// MARK: - ANNOTASYON (açıklamalı mod)
// =========================================================================

/**
 * Segment ve eleman açıklamalarını üretir.
 *
 * Açıklamalar mevcut sözlükten gelir: segment metni EDIParser'ın akıllı
 * açıklamasından, eleman etiketleri segmentDetail'in analyzeElement motorundan.
 * Yeni bir çeviri katmanı YOKTUR — arayüzde ne görünüyorsa dosyada da o yazar.
 *
 * Bu alanlar şemanın üst kümesidir: okuyucu onları yok sayar, dolayısıyla
 * açıklamalı çıktı da geri dönüştürülebilir kalır.
 */
function buildAnnotations(model) {
  const ediText = serializeEDI(model);
  const parsed = EDIParser.parse(ediText);
  // Kaçışlanmış terminatör içeren dosyalarda EDIParser farklı sayıda segment
  // görebilir; hizalanmıyorsa segment açıklamalarını hiç üretme.
  const aligned = parsed.length === model.segments.length;
  const currency = findCurrency(model);

  return {
    messageType: EDIParser.detectMessageType(ediText),
    language: loc.currentLanguageCode,
    describe: (index) => (aligned ? parsed[index].smartDescription : ''),
    info: (seg) => {
      const rows = [];
      (seg.elements || []).forEach((el, idx) => {
        // analyzeElement ':' ile ayrılmış ham eleman bekler (sözleşmesi budur)
        const d = analyzeElement(seg.tag, el.join(':'), idx + 1, currency);
        if (d.label) rows.push({ index: idx + 1, label: d.label, value: d.value });
      });
      return rows;
    },
  };
}

/** CUX segmentinden para birimi (annotation'da PRI değerlerini süslemek için) */
function findCurrency(model) {
  const cux = (model.segments || []).find((s) => s.tag === 'CUX');
  if (!cux) return '';
  const first = cux.elements?.[0];
  return Array.isArray(first) && first.length > 1 ? first[1] : '';
}

// =========================================================================
// MARK: - JSON
// =========================================================================

export function modelToJSON(model, { annotated = false, pretty = true } = {}) {
  const ann = annotated ? buildAnnotations(model) : null;

  const payload = {
    format: SCHEMA_JSON,
    version: SCHEMA_VERSION,
    standard: model.standard,
    syntax: syntaxToPlain(model.syntax),
  };
  if (model.unterminated) payload.unterminated = true;
  if (ann) {
    payload.messageType = ann.messageType;
    payload.language = ann.language;
  }

  payload.segments = model.segments.map((seg, index) => {
    const out = { tag: seg.tag };
    if (ann) {
      const d = ann.describe(index);
      if (d) out.description = d;
    }
    out.elements = seg.elements;
    if (ann) {
      const rows = ann.info(seg);
      if (rows.length) out.info = rows;
    }
    return out;
  });

  return stringifyPayload(payload, pretty);
}

/**
 * Girintili JSON — ancak bileşen dizileri tek satırda kalır.
 *
 * Düz `JSON.stringify(x, null, 2)` her bileşeni ayrı satıra açar ve 40
 * segmentlik bir dosya 800 satıra çıkar. Dizileri önce yer tutucuya çevirip
 * sonra geri yazarak `["UNOC","3"]` biçimini koruyoruz.
 */
function stringifyPayload(payload, pretty) {
  if (!pretty) return JSON.stringify(payload);

  const inline = [];
  const json = JSON.stringify(
    payload,
    (key, value) => {
      if (Array.isArray(value) && value.every((v) => typeof v === 'string')) {
        inline.push(JSON.stringify(value));
        return `\u0001INLINE${inline.length - 1}\u0001`;
      }
      return value;
    },
    2
  );

  // JSON.stringify kontrol karakterlerini \u0001 olarak kaçışlar
  return json.replace(/"\\u0001INLINE(\d+)\\u0001"/g, (_m, i) => inline[Number(i)]);
}

export function jsonToModel(text) {
  let data;
  try {
    data = JSON.parse(text);
  } catch (e) {
    throw new ConvertError('conv_err_invalid_json', e.message);
  }
  if (!data || typeof data !== 'object' || !Array.isArray(data.segments)) {
    throw new ConvertError('conv_err_schema');
  }

  const standard = data.standard === 'X12' ? 'X12' : 'EDIFACT';
  return {
    standard,
    unterminated: bool(data.unterminated),
    syntax: syntaxFromPlain(data.syntax, standard),
    segments: data.segments.map(normalizeSegment),
  };
}

/** Elle düzenlenmiş dosyalara toleranslı: string eleman tek bileşene sarılır. */
function normalizeSegment(seg) {
  if (!seg || typeof seg !== 'object') throw new ConvertError('conv_err_schema');
  const elements = Array.isArray(seg.elements) ? seg.elements : [];
  return {
    tag: String(seg.tag ?? ''),
    elements: elements.map((el) =>
      Array.isArray(el) ? el.map((c) => String(c ?? '')) : [String(el ?? '')]
    ),
  };
}

// =========================================================================
// MARK: - XML
// =========================================================================

export function modelToXML(model, { annotated = false, pretty = true } = {}) {
  const ann = annotated ? buildAnnotations(model) : null;
  const nl = pretty ? '\n' : '';
  const pad = (n) => (pretty ? '  '.repeat(n) : '');
  const sx = syntaxToPlain(model.syntax);

  const out = [`<?xml version="1.0" encoding="UTF-8"?>${nl}`];

  const rootAttrs = [
    `format="${SCHEMA_XML}"`,
    `version="${SCHEMA_VERSION}"`,
    `standard="${xa(model.standard)}"`,
  ];
  if (model.unterminated) rootAttrs.push('unterminated="true"');
  if (ann) {
    rootAttrs.push(`messageType="${xa(ann.messageType)}"`);
    rootAttrs.push(`language="${xa(ann.language)}"`);
  }
  out.push(`<edi ${rootAttrs.join(' ')}>${nl}`);

  const syntaxAttrs = Object.entries(sx).map(([k, v]) => `${k}="${xa(v)}"`);
  out.push(`${pad(1)}<syntax ${syntaxAttrs.join(' ')}/>${nl}`);
  out.push(`${pad(1)}<segments>${nl}`);

  model.segments.forEach((seg, index) => {
    const desc = ann ? ann.describe(index) : '';
    out.push(`${pad(2)}<segment tag="${xa(seg.tag)}"${desc ? ` desc="${xa(desc)}"` : ''}>${nl}`);

    for (const el of seg.elements || []) {
      const comps = (el.length ? el : [''])
        // Bileşen etiketinin içinde ASLA girinti/satır sonu olmamalı:
        // textContent birebir okunuyor, boşluk eklersek veriye karışır.
        .map((c) => `<component>${xt(c)}</component>`)
        .join('');
      out.push(`${pad(3)}<element>${comps}</element>${nl}`);
    }

    if (ann) {
      for (const row of ann.info(seg)) {
        out.push(
          `${pad(3)}<info index="${row.index}" label="${xa(row.label)}" value="${xa(row.value)}"/>${nl}`
        );
      }
    }
    out.push(`${pad(2)}</segment>${nl}`);
  });

  out.push(`${pad(1)}</segments>${nl}`);
  out.push('</edi>');
  if (pretty) out.push('\n');
  return out.join('');
}

export function xmlToModel(text) {
  const doc = new DOMParser().parseFromString(String(text ?? ''), 'application/xml');
  if (doc.getElementsByTagName('parsererror').length) {
    throw new ConvertError('conv_err_invalid_xml');
  }

  const root = doc.documentElement;
  if (!root || root.nodeName !== 'edi') throw new ConvertError('conv_err_schema');

  const standard = root.getAttribute('standard') === 'X12' ? 'X12' : 'EDIFACT';

  const syntaxEl = root.getElementsByTagName('syntax')[0];
  const rawSyntax = {};
  if (syntaxEl) {
    for (const attr of Array.from(syntaxEl.attributes)) rawSyntax[attr.name] = attr.value;
  }

  const segmentEls = Array.from(root.getElementsByTagName('segment'));
  if (!segmentEls.length) throw new ConvertError('conv_err_schema');

  const segments = segmentEls.map((segEl) => ({
    tag: segEl.getAttribute('tag') ?? '',
    elements: Array.from(segEl.getElementsByTagName('element')).map((elEl) => {
      const comps = Array.from(elEl.getElementsByTagName('component'));
      return comps.length ? comps.map((c) => c.textContent ?? '') : [''];
    }),
  }));

  return {
    standard,
    unterminated: bool(root.getAttribute('unterminated')),
    syntax: syntaxFromPlain(rawSyntax, standard),
    segments,
  };
}

/** XML metin düğümü kaçışı */
function xt(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/** XML öznitelik kaçışı */
function xa(value) {
  return xt(value).replace(/"/g, '&quot;');
}

// =========================================================================
// MARK: - KENDİ KENDİNİ SINAMA (?selftest=1)
// =========================================================================

/** ISA sabit genişliklidir; 106 karakteri elle kurmak gerekiyor. */
function buildISA() {
  const pad = (s, n) => String(s).padEnd(n, ' ').slice(0, n);
  return [
    'ISA', '00', pad('', 10), '00', pad('', 10), 'ZZ', pad('SENDERID', 15),
    'ZZ', pad('RECEIVERID', 15), '260117', '1030', 'U', '00401', '000000905',
    '0', 'P', '>',
  ].join('*') + '~';
}

/** Sözdiziminin zorlandığı vakalar — asıl regresyon riski burada. */
const FIXTURES = {
  'X12 004010':
    buildISA() + '\nGS*PO*S*R*20260117*1030*1*X*004010~\nST*850*0001~\n' +
    'BEG*00*SA*PO-42**20260117~\nSE*3*0001~\nGE*1*1~\nIEA*1*000000905~\n',
  'UNA + CRLF':
    "UNA:+.? '\r\nUNB+UNOC:3+A:14+B:14+260117:1030+R1'\r\nUNH+1+ORDERS:D:96A:UN'\r\n" +
    "UNT+2+1'\r\nUNZ+1+R1'\r\n",
  'kaçış karakteri':
    "UNB+UNOC:3+A:14+B:14+260117:1030+R1'\nFTX+AAI+++ACME?+SONS ?: 50?? indirim'\nUNZ+1+R1'\n",
  'özel ayraçlar':
    'UNA|^.! ~UNB^UNOC|3^A|14^B|14^260117|1030^R1~FTX^AAI^^^A!^B~UNZ^1^R1~',
  'tek satır':
    "UNB+UNOC:3+A:14+B:14+260117:1030+R1'UNH+1+ORDERS:D:96A:UN'UNT+2+1'UNZ+1+R1'",
  'boş elemanlar':
    "UNB+UNOC:3+A:14+B:14+260117:1030+R1'\nNAD+BY+8798765432109::9++MEGA RETAIL AS+++++TR'\nUNZ+1+R1'\n",
};

/**
 * Gömülü örnekleri dört yönün tamamından geçirip baytı baytına eşitlik arar.
 * Derleme adımı olmadığı için test koşucusu yerine tarayıcıda çalışır:
 * adres çubuğuna ?selftest=1 eklemek yeterlidir.
 */
export function runSelfTest(extraSamples = {}) {
  const samples = { ...FIXTURES, ...extraSamples };
  const results = [];
  for (const [name, source] of Object.entries(samples)) {
    for (const target of ['json', 'xml']) {
      for (const annotated of [false, true]) {
        const row = {
          name: `${name} -> ${target}${annotated ? ' (açıklamalı)' : ''}`,
          ok: false,
          note: '',
        };
        try {
          const forward = ConvertManager.convert(source, { from: 'edi', to: target, annotated });
          const back = ConvertManager.convert(forward.text, { from: target, to: 'edi' });
          row.ok = forward.roundTrip.ok && back.text === source;
          if (!row.ok) row.note = forward.roundTrip.reason ?? 'bayt farkı';
        } catch (e) {
          row.note = e.key ? L(e.key) : String(e.message);
        }
        results.push(row);
      }
    }
  }
  return results;
}
