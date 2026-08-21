// CSVExportManager.swift -> web karşılığı
import { L } from './i18n.js';
import { get, swiftSplit } from './parser.js';

export const CSVExportManager = {
  // Ana Yönlendirme Fonksiyonu
  generateCSV(segments) {
    const fullContent = segments.map((s) => s.rawLine).join('\n');

    if (fullContent.includes('SLSRPT')) return generateSlsrptCSV(segments);
    if (fullContent.includes('PRICAT')) return generatePricatCSV(segments);
    return generateGenericCSV(segments);
  },
};

// =========================================================================
// MARK: - 1. SLSRPT (SATIŞ RAPORU) MOTORU 📉
// =========================================================================
function generateSlsrptCSV(segments) {
  const headers = [
    L('csv_row'), L('csv_ean'), L('csv_prod_desc'),
    L('csv_sold_qty'), L('csv_unit'), L('csv_unit_price'), L('csv_revenue'),
  ];

  let csv = headers.join(';') + '\n';

  let currentCode = '', currentDesc = '', soldQty = '0', unit = '', price = '0.00', revenue = '0.00';
  let lineCount = 0;

  for (const seg of segments) {
    if (seg.tag === 'LIN') {
      if (currentCode !== '') {
        lineCount += 1;
        csv += `${lineCount};${currentCode};${currentDesc};${soldQty};${unit};${price};${revenue}\n`;
      }
      currentCode = swiftSplit(getElement(seg, 3), ':')[0] ?? '';
      currentDesc = ''; soldQty = '0'; unit = ''; price = '0.00'; revenue = '0.00';
    }

    if (currentCode !== '') {
      if (seg.tag === 'IMD') {
        const p = swiftSplit(getElement(seg, 3), ':');
        currentDesc = clean(p.length ? p[p.length - 1] : '');
      }
      if (seg.tag === 'QTY') {
        const parts = swiftSplit(getElement(seg, 1), ':');
        if (parts[0] === '152' && parts.length >= 2) {
          soldQty = parts[1];
          unit = parts.length > 2 ? parts[2] : '';
        }
      }
      if (seg.tag === 'MOA') {
        const parts = swiftSplit(getElement(seg, 1), ':');
        if (parts[0] === '203' && parts.length >= 2) revenue = parts[1];
      }
      if (seg.tag === 'PRI') {
        const parts = swiftSplit(getElement(seg, 1), ':');
        if (parts.length >= 2) price = parts[1];
      }
    }
  }

  if (currentCode !== '') {
    lineCount += 1;
    csv += `${lineCount};${currentCode};${currentDesc};${soldQty};${unit};${price};${revenue}\n`;
  }

  return csv;
}

// =========================================================================
// MARK: - 2. PRICAT (FİYAT KATALOĞU) MOTORU 🏷️
// =========================================================================
function generatePricatCSV(segments) {
  const headers = [
    L('csv_row'), L('csv_gtin'), L('csv_prod_desc'), L('csv_origin'),
    L('csv_net_price'), L('csv_gross_price'), L('csv_retail_price'), L('csv_pack_qty'),
  ];

  let csv = headers.join(';') + '\n';

  let currentCode = '', currentDesc = '', origin = '', netPrice = '', grossPrice = '', retailPrice = '', packQty = '';
  let lineCount = 0;

  for (const seg of segments) {
    if (seg.tag === 'LIN') {
      if (currentCode !== '') {
        lineCount += 1;
        csv += `${lineCount};${currentCode};${currentDesc};${origin};${netPrice};${grossPrice};${retailPrice};${packQty}\n`;
      }
      currentCode = swiftSplit(getElement(seg, 3), ':')[0] ?? '';
      currentDesc = ''; origin = ''; netPrice = ''; grossPrice = ''; retailPrice = ''; packQty = '';
    }

    if (currentCode !== '') {
      if (seg.tag === 'IMD') {
        const p = swiftSplit(getElement(seg, 3), ':');
        currentDesc = clean(p.length ? p[p.length - 1] : '');
      }
      if (seg.tag === 'ALI') origin = getElement(seg, 1);
      if (seg.tag === 'PAC') packQty = getElement(seg, 1);
      if (seg.tag === 'PRI') {
        const parts = swiftSplit(getElement(seg, 1), ':');
        if (parts.length >= 2) {
          const type = parts[0];
          const val = parts[1];
          if (type === 'AAA') netPrice = val;
          else if (type === 'AAB') grossPrice = val;
          else if (type === 'AAE') retailPrice = val;
        }
      }
    }
  }

  if (currentCode !== '') {
    lineCount += 1;
    csv += `${lineCount};${currentCode};${currentDesc};${origin};${netPrice};${grossPrice};${retailPrice};${packQty}\n`;
  }

  return csv;
}

// =========================================================================
// MARK: - 3. GENERIC (STANDART) MOTOR 📝
// =========================================================================
function generateGenericCSV(segments) {
  const headers = [
    L('csv_row'), L('csv_segment'), L('csv_code'), L('csv_desc'),
    L('csv_val1'), L('csv_val2'), L('csv_val3'), L('csv_raw'),
  ];

  let csv = headers.join(';') + '\n';

  segments.forEach((seg, index) => {
    const tag = clean(seg.tag);
    const rawLine = clean(seg.rawLine);

    // Segment Açıklaması (JSON sözlüğünden)
    const key = `seg_${seg.tag}`;
    const localizedDesc = L(key);
    const description = localizedDesc !== key ? clean(localizedDesc) : '-';

    const val1 = seg.elements.length > 1 ? clean(seg.elements[1]) : '';
    const val2 = seg.elements.length > 2 ? clean(seg.elements[2]) : '';
    const val3 = seg.elements.length > 3 ? clean(seg.elements[3]) : '';

    csv += `${index + 1};${tag};${val1};${description};${val1};${val2};${val3};${rawLine}\n`;
  });

  return csv;
}

// =========================================================================
// MARK: - YARDIMCI METODLAR
// =========================================================================
function clean(text) {
  return String(text).replace(/;/g, ',').replace(/\n/g, ' ');
}

function getElement(seg, index) {
  return get(seg.elements, index);
}

/** CSVDocument.fileWrapper karşılığı: UTF-8 BOM + içerik */
export function csvBlob(text) {
  return new Blob(['﻿' + text], { type: 'text/csv;charset=utf-8' });
}
