// EdiSegment.swift -> web karşılığı (EDIParser)
import { L } from './i18n.js';

/** Array.get(_:) güvenli erişim karşılığı */
export function get(arr, index) {
  if (index >= 0 && index < arr.length) return arr[index];
  return '';
}

/**
 * Swift'in `split(separator:)` davranışı: boş parçaları atar.
 * (JS'in String.split'i boşları korur, Swift'in components(separatedBy:) gibi.)
 */
export function swiftSplit(str, sep) {
  return String(str).split(sep).filter((p) => p.length > 0);
}

/**
 * Segment açıklamasını sözlükten çeker.
 *
 * Anahtarlar tarihsel olarak iki yazımla birikmiş: 116 `seg_` anahtarının 48'i
 * büyük (`seg_UNB`), 68'i küçük harfli (`seg_unz`) ve 30 segmentin ikisi birden
 * var. Tek yazımla arayan çağıranlar bu yüzden bazı segmentlerde ham anahtar
 * gösteriyordu — örneğin her EDIFACT dosyasının son satırındaki UNZ için
 * "seg_UNZ", her X12 dosyasının ilk satırındaki ISA için "seg_ISA".
 *
 * @returns {string} açıklama; sözlükte hiç karşılığı yoksa boş dizge
 */
export function segmentDescription(tag) {
  const upper = `seg_${String(tag).toUpperCase()}`;
  const fromUpper = L(upper);
  if (fromUpper !== upper) return fromUpper;

  const lower = `seg_${String(tag).toLowerCase()}`;
  const fromLower = L(lower);
  return fromLower !== lower ? fromLower : '';
}

export const EDIParser = {
  // --- 1. DOSYA TÜRÜNÜ ALGILA (Banner ve PDF Başlığı için) ---
  detectMessageType(content) {
    // EDIFACT Taraması (UNH)
    const unh = content.match(/UNH\+.*?\+([A-Z]+)/);
    if (unh) {
      const parts = unh[0].split('+').filter((p) => p.length > 0);
      const lastPart = parts[parts.length - 1];
      if (lastPart !== undefined) {
        const typeCode = lastPart.split(':')[0] ?? '';
        return L(`type_${typeCode}`);
      }
    }

    // ANSI X12 Taraması (ST)
    const st = content.match(/ST\*([0-9]+)/);
    if (st) {
      const parts = st[0].split('*').filter((p) => p.length > 0);
      const lastPart = parts[parts.length - 1];
      if (lastPart !== undefined) {
        return L(`type_${lastPart}`);
      }
    }

    return L('type_UNKNOWN');
  },

  // --- 2. PARSE İŞLEMİ (Satırlara Bölme) ---
  parse(content) {
    const isX12 = content.includes('ISA*') || content.includes('GS*');
    const terminator = isX12 ? '~' : "'";
    const elementSeparator = isX12 ? '*' : '+';
    const subElementSeparator = isX12 ? '>' : ':';

    const rawSegments = content
      .replace(/\n/g, '')
      .replace(/\r/g, '')
      .split(terminator);

    const result = [];
    for (const line of rawSegments) {
      const cleanLine = line.trim();
      if (cleanLine.length === 0) continue;

      const elements = cleanLine.split(elementSeparator);
      const tag = elements[0] ?? '???';
      const smartDescription = generateSmartDescription(tag, elements, isX12, subElementSeparator);

      result.push({ rawLine: cleanLine, tag, elements, smartDescription });
    }
    return result;
  },

  // --- 4. VALIDASYON ---
  isProbablyEDI(content) {
    const trimmed = content.trim();
    return (
      trimmed.startsWith('UNB') ||
      trimmed.startsWith('ISA') ||
      trimmed.startsWith('UNA') ||
      trimmed.includes('UNH+') ||
      trimmed.includes('ST*')
    );
  },
};

// --- 3. AKILLI AÇIKLAMA ÜRETİCİ ---
function generateSmartDescription(tag, elements, isX12, subSep) {
  const g = (i) => get(elements, i);
  const getSub = (i, subIndex) => {
    const parts = g(i).split(subSep);
    return subIndex < parts.length ? parts[subIndex] : '';
  };

  if (isX12) {
    // --- ANSI X12 (ABD) ---
    switch (tag) {
      case 'ISA': return `🇺🇸 ${L('seg_isa')}`;
      case 'ST': return `📄 ${L('seg_st')}: ${g(1)}`;
      case 'BIG': return `🔖 ${L('seg_big')}: ${g(2)}`;
      case 'BEG': return `🔖 ${L('seg_beg')}: ${g(3)}`;
      case 'N1': return `🏢 ${L('seg_n1')}: ${g(2)}`;
      case 'PO1': return `📦 ${L('seg_po1')}`;
      case 'IT1': return `📦 ${L('seg_it1')}`;
      case 'PID': return `📝 ${L('seg_pid')}: ${g(5)}`;
      case 'TDS': return `💰 ${L('seg_tds')}: ${g(1)}`;
      case 'CAD': return `🚚 ${L('seg_cad')}`;
      case 'ISS': return `📊 ${L('seg_iss')}`;
      case 'SLN': return `📎 ${L('seg_sln')}`;
      case 'SE': return `🔚 ${L('seg_se')}`;
      case 'IEA': return `🏁 ${L('seg_iea')}`;
      default: return tag;
    }
  }

  // --- EDIFACT (AVRUPA) ---
  switch (tag) {
    // 1. Başlık ve Referanslar
    case 'UNB': return `📁 ${L('seg_unb')}`;
    case 'UNH': return `📄 ${L('seg_unh')}: ${getSub(2, 0)}`;
    case 'BGM': return `🔖 ${L('seg_bgm')}: ${g(2)}`;
    case 'DTM': return `📅 ${L('seg_dtm')}: ${getSub(1, 1)}`;
    case 'RFF': return `📎 ${L('seg_rff')}: ${getSub(1, 1)}`;
    case 'FTX': return `📝 ${L('seg_ift')}: ${getSub(4, 0)}`;

    // 2. Taraflar ve İletişim
    case 'NAD': {
      const role = g(1);
      const name = g(4);
      if (role === 'SU') return `🏭 ${L('desc_supplier')}: ${name}`;
      if (role === 'BY') return `👤 ${L('desc_buyer')}: ${name}`;
      if (role === 'DP') return `📍 ${L('desc_delivery_party')}: ${name}`;
      if (role === 'IV') return `📨 ${L('seg_invoicee')}: ${name}`;
      return `🏢 ${L('seg_nad')} (${role}): ${name}`;
    }
    case 'CTA': return `📞 ${L('seg_cta')}: ${getSub(2, 1)}`;
    case 'COM': return `📧 ${L('seg_com')}: ${getSub(1, 0)}`;

    // 3. Ürün ve Fiyat
    case 'LIN': return `📦 ${L('seg_lin')}: ${getSub(3, 0)}`;
    case 'PIA': return `🏷️ ${L('seg_pia')}: ${getSub(2, 0)}`;
    case 'IMD': return `📝 ${L('seg_imd')}: ${getSub(3, 3) === '' ? g(3) : getSub(3, 3)}`;
    case 'QTY': return `🔢 ${L('seg_qty')}: ${getSub(1, 1)}`;
    case 'MOA': return `💰 ${L('seg_moa')}: ${getSub(1, 1)}`;
    case 'PRI': return `🏷️ ${L('seg_pri')}: ${getSub(1, 1)}`;
    case 'TAX': return `💸 ${L('seg_tax')}`;
    case 'ALC': return `📉 ${L('seg_alc')}`;
    case 'CUX': return `💱 ${L('seg_cud')}: ${getSub(1, 1)}`;
    case 'ALI': return `🌍 ${L('seg_ali')}`;

    // 4. Lojistik ve Paketleme
    case 'TDT': return `🚚 ${L('seg_tdt')}`;
    case 'CPS': return `🌲 ${L('seg_cps')}: Seviye ${g(1)}`;
    case 'PAC': return `📦 ${L('seg_pac')}: ${g(1)}`;
    case 'PCI': return `📋 ${L('seg_pci')}`;
    case 'GIN': return `🆔 ${L('seg_gin')}: ${getSub(2, 0)}`;
    case 'GIR': return `🔗 ${L('seg_gir')}`;
    case 'MEA': return `⚖️ ${L('seg_mea')}: ${getSub(3, 1)} ${getSub(3, 0)}`;
    case 'DIM': return `📏 ${L('seg_dim')}`;
    case 'LOC': return `📍 ${L('seg_loc')}: ${getSub(2, 0)}`;
    case 'HAN': return `⚠️ ${L('seg_han')}`;
    case 'TOD': return `🚢 ${L('seg_tod')}`;
    case 'EQD': return `🚛 ${L('seg_eqd')}`;
    case 'TSR': return `🛠️ ${L('seg_tsr')}`;
    case 'SEL': return `🔒 ${L('seg_sel')}: ${getSub(1, 0)}`;
    case 'SCC': return `📅 ${L('seg_scc')}`;

    // 5. Finans ve Gümrük
    case 'FII': return `🏦 ${L('seg_fii')}`;
    case 'PAI': return `💳 ${L('seg_pai')}`;
    case 'PAT': return `🗓️ ${L('seg_pat')}`;
    case 'CUS': return `🛃 ${L('seg_cus')}`;
    case 'DOC': return `📄 ${L('seg_doc')}`;

    // 6. Bitiş
    case 'UNZ': return `🏁 ${L('seg_unz')}`;
    case 'UNT': return `🔚 ${L('seg_unt')}`;

    default: return `Segment: ${tag}`;
  }
}
