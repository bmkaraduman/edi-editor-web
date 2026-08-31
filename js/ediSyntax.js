// EDI sözdizimi katmanı — kayıpsız okuma ve yazma.
//
// Bu dosya js/parser.js'teki EDIParser'dan AYRIDIR ve onun yerini almaz.
// EDIParser akıllı açıklama, detay paneli ve PDF/CSV üreticileri için tasarlandı:
// satırları trim'ler, tüm satır sonlarını siler, ayraçları +/:/' olarak sabit
// varsayar ve release (kaçış) karakterini bilmez. Bunlar o kullanım için
// zararsız; ama dönüşüm modülü EDI -> JSON/XML -> EDI çevriminde baytı baytına
// aynı sonucu üretmek zorunda olduğu için kendi tarayıcısını taşır.
//
// Burada tutulan şey "anlam" değil "sözdizimi"dir: ayraçlar, kaçışlar,
// satır sonları ve konumsal boşluklar. Anlamlandırma EDIParser'ın işi.

/** UN/EDIFACT servis karakterleri — UNA yoksa geçerli varsayılanlar. */
export const EDIFACT_DEFAULTS = {
  component: ':',
  element: '+',
  decimal: '.',
  release: '?',
  repetition: null,
  terminator: "'",
};

// ANSI X12'de ISA sabit genişliklidir: ayraçlar veriden değil KONUMDAN okunur.
// Segment 106 karakterdir (terminatör dahil).
const ISA_LENGTH = 106;
const ISA_ELEMENT_POS = 3;
const ISA_REPETITION_POS = 82; // ISA11 — 00403+ sürümünde tekrar ayracı
const ISA_VERSION_START = 84; // ISA12 (5 hane)
const ISA_VERSION_END = 89;
const ISA_COMPONENT_POS = 104; // ISA16
const ISA_TERMINATOR_POS = 105;

/** Tekrar ayracının anlamlı olduğu en düşük X12 sürümü. */
const X12_REPETITION_MIN_VERSION = '00403';

/**
 * İçeriğe bakarak ayraçları ve standardı belirler.
 * @param {string} body baştaki BOM ve boşluk ayıklanmış içerik
 */
export function detectSyntax(body) {
  // --- UN/EDIFACT: UNA servis dizgisi ---
  // UNA + bileşen + eleman + ondalık + release + tekrar/reserved + terminatör
  if (body.startsWith('UNA') && body.length >= 9) {
    const c = body.slice(3, 9);
    return {
      standard: 'EDIFACT',
      component: c[0],
      element: c[1],
      decimal: c[2],
      release: c[3] === ' ' ? null : c[3],
      // 5. konum sözdizimi 3'te "reserved" (boşluk), sözdizimi 4'te tekrar ayracı.
      // Boşluksa tekrar ayracı yok sayılır; bu her iki sürümde de doğru davranış.
      repetition: c[4] === ' ' ? null : c[4],
      terminator: c[5],
      unaPresent: true,
    };
  }

  // --- ANSI X12: ISA konumsal ---
  if (body.startsWith('ISA')) {
    const element = body[ISA_ELEMENT_POS] ?? '*';
    if (body.length >= ISA_LENGTH) {
      const version = body.slice(ISA_VERSION_START, ISA_VERSION_END);
      const rep = body[ISA_REPETITION_POS];
      return {
        standard: 'X12',
        component: body[ISA_COMPONENT_POS],
        element,
        decimal: '.',
        release: null, // X12'de kaçış karakteri yoktur
        repetition: version >= X12_REPETITION_MIN_VERSION && rep !== 'U' ? rep : null,
        terminator: body[ISA_TERMINATOR_POS],
        unaPresent: false,
      };
    }
    // Kırpılmış/bozuk ISA: yaygın varsayılanlara düş
    return {
      standard: 'X12',
      component: '>',
      element,
      decimal: '.',
      release: null,
      repetition: null,
      terminator: '~',
      unaPresent: false,
    };
  }

  return { standard: 'EDIFACT', ...EDIFACT_DEFAULTS, unaPresent: false };
}

/**
 * EDI metnini kanonik modele çevirir.
 *
 * Model:
 *   { standard, syntax, segments: [{ tag, elements: string[][] }], unterminated }
 *
 * `elements` dış dizi = veri elemanları (etiket hariç), iç dizi = bileşenler.
 * Basit eleman tek elemanlı dizidir. Boş bileşenler ("") konumsal olarak
 * korunur — `NAD+BY+871::9++ACME` içindeki `::` ve `++` böyle yaşar.
 */
export function parseEDI(text) {
  let rest = String(text ?? '');

  const bom = rest.charCodeAt(0) === 0xfeff;
  if (bom) rest = rest.slice(1);

  const leading = /^\s*/.exec(rest)[0];
  const body = rest.slice(leading.length);

  const sx = detectSyntax(body);
  const { segments, gaps, unterminated } = scan(body, sx);

  // UNA'dan sonraki boşluk ayrı tutulur: UNA'yı hemen UNB izleyen dosyalar da
  // her segmenti ayrı satıra yazan dosyalar da vardır.
  const unaGap = sx.unaPresent ? gaps.shift() ?? '' : '';

  const inner = gaps.slice(0, Math.max(0, gaps.length - 1));
  const last = gaps.length ? gaps[gaps.length - 1] : '';
  let lineBreak = inner.find((g) => g !== '') ?? '';
  if (lineBreak === '') lineBreak = last;

  return {
    standard: sx.standard,
    unterminated,
    syntax: {
      component: sx.component,
      element: sx.element,
      decimal: sx.decimal,
      release: sx.release,
      repetition: sx.repetition,
      terminator: sx.terminator,
      unaPresent: sx.unaPresent,
      unaLineBreak: unaGap !== '',
      lineBreak,
      leadingLineBreak: leading !== '' && leading === lineBreak,
      trailingLineBreak: last !== '',
      bom,
    },
    segments,
  };
}

/** Kanonik modeli EDI metnine geri yazar. */
export function serializeEDI(model) {
  const sx = { ...EDIFACT_DEFAULTS, ...(model.syntax || {}) };
  const lb = sx.lineBreak || '';

  // Kaçışlanması gereken karakterler. X12'de release yoktur -> küme kullanılmaz.
  const specials = new Set([sx.component, sx.element, sx.terminator]);
  if (sx.release) specials.add(sx.release);
  if (sx.repetition) specials.add(sx.repetition);

  const enc = (value) => {
    const s = String(value ?? '');
    if (!sx.release) return s;
    let out = '';
    for (const ch of s) {
      if (specials.has(ch)) out += sx.release;
      out += ch;
    }
    return out;
  };

  const parts = [];
  if (sx.bom) parts.push('﻿');
  if (sx.leadingLineBreak) parts.push(lb);

  if (sx.unaPresent) {
    parts.push(
      'UNA' + sx.component + sx.element + sx.decimal +
      (sx.release ?? ' ') + (sx.repetition ?? ' ') + sx.terminator
    );
    if (sx.unaLineBreak) parts.push(lb);
  }

  const segments = model.segments || [];
  segments.forEach((seg, index) => {
    const isLast = index === segments.length - 1;

    const fields = [enc(seg.tag)];
    for (const el of seg.elements || []) {
      const comps = Array.isArray(el) ? el : [el];
      fields.push((comps.length ? comps : ['']).map(enc).join(sx.component));
    }
    parts.push(fields.join(sx.element));

    // Sonlandırılmamış son segment (dosya terminatörsüz bitmişse) aynen korunur
    if (isLast && model.unterminated) return;

    parts.push(sx.terminator);
    if (!isLast || sx.trailingLineBreak) parts.push(lb);
  });

  return parts.join('');
}

/**
 * EDI -> model -> EDI çevriminin kayıpsız olup olmadığını ölçer.
 * @returns {{ok: boolean, model: object, result: string, diffAt: number}}
 */
export function roundTripEDI(text) {
  const source = String(text ?? '');
  const model = parseEDI(source);
  const result = serializeEDI(model);
  return { ok: result === source, model, result, diffAt: firstDifference(source, result) };
}

/** İki metnin ilk ayrıştığı konum; aynılarsa -1. */
export function firstDifference(a, b) {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) if (a[i] !== b[i]) return i;
  return a.length === b.length ? -1 : n;
}

/** Bu içerik EDI'ye benziyor mu? (EDIParser.isProbablyEDI'nin sözdizimsel eşi) */
export function looksLikeEDI(text) {
  const t = String(text ?? '').trim();
  return t.startsWith('UNA') || t.startsWith('UNB') || t.startsWith('ISA') ||
    t.includes('UNH+') || t.includes('ST*');
}

// =========================================================================
// MARK: - TARAYICI
// =========================================================================

function scan(body, sx) {
  const segments = [];
  const gaps = [];
  let i = sx.unaPresent ? 9 : 0;

  /** Terminatörden sonraki boşluğu (satır sonu/girinti) yutar ve kaydeder. */
  const takeGap = () => {
    const m = /^\s*/.exec(body.slice(i))[0];
    gaps.push(m);
    i += m.length;
  };

  if (sx.unaPresent) takeGap();

  let elements = [];
  let comps = [];
  let buf = '';
  let open = false;

  // X12'de ISA16'nın DEĞERİ bileşen ayracının kendisidir. O segmentte bileşene
  // bölmek ISA16'yı iki boş parçaya ayırırdı; ISA'da zaten composite yoktur.
  let splitComponents = true;

  while (i < body.length) {
    const ch = body[i];

    // Release karakteri kendinden sonrakini veri yapar (?+ -> +, ?? -> ?)
    if (sx.release && ch === sx.release && i + 1 < body.length) {
      buf += body[i + 1];
      i += 2;
      open = true;
      continue;
    }

    if (splitComponents && ch === sx.component) {
      comps.push(buf);
      buf = '';
      i++;
      open = true;
      continue;
    }

    if (ch === sx.element) {
      comps.push(buf);
      elements.push(comps);
      comps = [];
      buf = '';
      i++;
      open = true;
      if (elements.length === 1 && sx.standard === 'X12' && elements[0][0] === 'ISA') {
        splitComponents = false;
      }
      continue;
    }

    if (ch === sx.terminator) {
      comps.push(buf);
      elements.push(comps);
      segments.push(toSegment(elements));
      elements = [];
      comps = [];
      buf = '';
      open = false;
      splitComponents = true;
      i++;
      takeGap();
      continue;
    }

    buf += ch;
    i++;
    open = true;
  }

  // Terminatörsüz kalan artık: veriyi atmak yerine sakla, yazarken de
  // terminatör ekleme -> dosya yine baytı baytına geri gelir.
  if (open) {
    comps.push(buf);
    elements.push(comps);
    segments.push(toSegment(elements));
  }

  return { segments, gaps, unterminated: open };
}

function toSegment(elements) {
  const first = elements[0] || [''];
  return { tag: first[0] ?? '', elements: elements.slice(1) };
}
