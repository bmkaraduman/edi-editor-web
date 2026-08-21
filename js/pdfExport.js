// PDFExportManager.swift -> web karşılığı
// WKWebView.createPDF yerine tarayıcının kendi yazdırma motoru (Save as PDF) kullanılır.
import { L } from './i18n.js';
import { get, swiftSplit } from './parser.js';

// =========================================================================
// MARK: - PDF MANAGER
// =========================================================================

export const PDFExportManager = {
  // --- ANA FONKSİYON (ROUTER) ---
  exportToPDF(segments) {
    const fullContent = segments.map((s) => s.rawLine).join('\n');
    let htmlContent;

    if (fullContent.includes('ORDCHG')) htmlContent = generateOrdchgHTML(segments);
    else if (fullContent.includes('ORDRSP')) htmlContent = generateOrdrspHTML(segments);
    else if (fullContent.includes('ORDERS')) htmlContent = generateOrdersHTML(segments);
    else if (fullContent.includes('DESADV')) htmlContent = generateDesadvHTML(segments);
    else if (fullContent.includes('RECADV')) htmlContent = generateRecadvHTML(segments);
    else if (fullContent.includes('IFTMIN')) htmlContent = generateIftminHTML(segments);
    else if (fullContent.includes('INVOIC')) htmlContent = generateInvoicHTML(segments);
    else if (fullContent.includes('REMADV')) htmlContent = generateRemadvHTML(segments);
    else if (fullContent.includes('DELJIT')) htmlContent = generateDeljitHTML(segments);
    else if (fullContent.includes('SLSRPT')) htmlContent = generateSlsrptHTML(segments);
    else htmlContent = generateGenericHTML(segments);

    savePDF(htmlContent);
  },

  /** Önizleme/geliştirme için ham HTML */
  buildHTML(segments) {
    const fullContent = segments.map((s) => s.rawLine).join('\n');
    if (fullContent.includes('ORDCHG')) return generateOrdchgHTML(segments);
    if (fullContent.includes('ORDRSP')) return generateOrdrspHTML(segments);
    if (fullContent.includes('ORDERS')) return generateOrdersHTML(segments);
    if (fullContent.includes('DESADV')) return generateDesadvHTML(segments);
    if (fullContent.includes('RECADV')) return generateRecadvHTML(segments);
    if (fullContent.includes('IFTMIN')) return generateIftminHTML(segments);
    if (fullContent.includes('INVOIC')) return generateInvoicHTML(segments);
    if (fullContent.includes('REMADV')) return generateRemadvHTML(segments);
    if (fullContent.includes('DELJIT')) return generateDeljitHTML(segments);
    if (fullContent.includes('SLSRPT')) return generateSlsrptHTML(segments);
    return generateGenericHTML(segments);
  },
};

// =========================================================================
// MARK: - YARDIMCI METODLAR
// =========================================================================

function getVal(segments, tag, idx) {
  const seg = segments.find((s) => s.tag === tag);
  return seg ? get(seg.elements, idx) : '';
}

/** DTM segmentinden qualifier'a göre ham tarihi çeker (137, 133, 64, 203, 356, 357...) */
function rawDTM(segments, qualifier) {
  const seg = segments.find((s) => s.tag === 'DTM' && get(s.elements, 1).startsWith(qualifier));
  if (!seg) return '';
  const parts = swiftSplit(get(seg.elements, 1), ':');
  return parts.length > 1 ? parts[1] : '';
}

function formatAddress(segments, role, title) {
  const seg = segments.find((s) => s.tag === 'NAD' && get(s.elements, 1) === role);
  if (!seg) return '';
  let name = get(seg.elements, 4);
  if (name === '') name = get(seg.elements, 3);
  const city = get(seg.elements, 6);
  const address = get(seg.elements, 5);
  const glnPart = swiftSplit(get(seg.elements, 2), ':')[0] ?? '';
  return `
    <div class="card">
        <h3>${title}</h3>
        <strong>${name}</strong><br>
        ${address === '' ? '' : `${address}<br>`}
        ${city}<br><small style="color:#666">ID: ${glnPart}</small>
    </div>
    `;
}

function formatDateTime(raw) {
  if (raw.length === 8) return `${raw.slice(6, 8)}.${raw.slice(4, 6)}.${raw.slice(0, 4)}`;
  return raw;
}

/** Ortak sayfa/yazdırma stili (A4) */
const PAGE_CSS = `
    @page { size: A4; margin: 0; }
    html, body { margin: 0; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
`;

// =========================================================================
// MARK: - 🔵 ORDERS (SİPARİŞ)
// =========================================================================
function generateOrdersHTML(segments) {
  const docNo = getVal(segments, 'BGM', 2);
  const docDate = formatDateTime(rawDTM(segments, '137'));

  const supplierHTML = formatAddress(segments, 'SU', L('pdf_header_supplier'));
  const buyerHTML = formatAddress(segments, 'BY', L('pdf_header_buyer'));
  const deliveryHTML = formatAddress(segments, 'DP', L('pdf_header_delivery'));

  const items = [];
  let currentItem = newOrderItem();
  let calculatedGrandTotal = 0.0;

  for (const seg of segments) {
    if (seg.tag === 'LIN') {
      if (currentItem.code !== '') items.push(currentItem);
      currentItem = newOrderItem();
      currentItem.code = swiftSplit(get(seg.elements, 3), ':')[0] ?? '';
    }
    if (currentItem.code !== '') {
      if (seg.tag === 'IMD') currentItem.desc = lastPart(get(seg.elements, 3));
      if (seg.tag === 'QTY') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts.length >= 2) {
          currentItem.quantity = parts[1];
          currentItem.unit = parts.length > 2 ? parts[2] : '';
        }
      }
      if (seg.tag === 'PRI') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts.length >= 2) currentItem.price = parts[1];
      }
      // İskonto vb.
      if (seg.tag === 'ALC') {
        const type = get(seg.elements, 1);
        const reason = get(seg.elements, 5);
        const sign = type === 'A' ? '-' : '+';
        const color = type === 'A' ? 'green' : 'red';
        currentItem.discounts += `<div style="color:${color}; font-size:11px;">${sign} ${reason}</div>`;
      }
    }
  }
  if (currentItem.code !== '') items.push(currentItem);

  for (const item of items) {
    const qty = parseFloat(item.quantity) || 0;
    const price = parseFloat(item.price) || 0;
    const lineTotal = qty * price;
    item.total = lineTotal.toFixed(2);
    calculatedGrandTotal += lineTotal;
  }
  const grandTotalStr = calculatedGrandTotal.toFixed(2);

  const rowsHTML = items.map((item) => `
            <tr>
                <td>${item.code}</td>
                <td><strong>${item.desc}</strong><br>${item.discounts}</td>
                <td style="text-align:right;">${item.quantity} ${item.unit}</td>
                <td style="text-align:right;">${item.price}</td>
                <td style="text-align:right;"><strong>${item.total}</strong></td>
            </tr>
            `).join('');

  return `
        <!DOCTYPE html><html><head><meta charset="utf-8"><style>${PAGE_CSS}
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; }
            .header { border-bottom: 4px solid #007AFF; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
            .title { font-size: 28px; font-weight: 900; color: #333; text-transform: uppercase; }
            .meta { text-align: right; line-height: 1.6; font-size: 14px; }
            .addresses { display: flex; gap: 20px; margin-bottom: 40px; }
            .card { flex: 1; background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
            .card h3 { font-size: 11px; color: #888; text-transform: uppercase; margin: 0 0 5px 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th { text-align: left; background: #007AFF; color: white; padding: 12px; font-size: 12px; text-transform: uppercase; }
            td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 14px; }
            .footer-wrapper { display: flex; justify-content: flex-end; margin-top: 30px; page-break-inside: avoid; }
            .total-box { width: 300px; background-color: #f1f3f5; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; }
            .total-row { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px; color: #555; }
            .grand-total { font-size: 22px; font-weight: 900; color: #007AFF; border-top: 2px solid #ccc; padding-top: 15px; margin-top: 10px; }
        </style></head><body>
            <div class="header">
                <div><div class="title">${L('pdf_title_orders')}</div><small>ORDERS / ${docDate}</small></div>
                <div class="meta"><div>Ref: <strong>${docNo}</strong></div></div>
            </div>
            <div class="addresses">${supplierHTML}${buyerHTML}${deliveryHTML}</div>
            <table><thead><tr>
                <th width="15%">${L('pdf_col_code')}</th>
                <th width="45%">${L('pdf_col_desc')}</th>
                <th width="10%" style="text-align:right;">${L('pdf_col_qty')}</th>
                <th width="15%" style="text-align:right;">${L('pdf_col_price')}</th>
                <th width="15%" style="text-align:right;">${L('pdf_col_total')}</th>
            </tr></thead><tbody>${rowsHTML}</tbody></table>
            <div class="footer-wrapper"><div class="total-box">
                <div class="total-row grand-total"><span>${L('pdf_label_grand_total')}:</span><span>€ ${grandTotalStr}</span></div>
            </div></div>
        </body></html>
        `;
}

function newOrderItem() {
  return { code: '', desc: '', quantity: '', unit: '', price: '', total: '', details: '', discounts: '' };
}

/** Swift: split(separator:":").last */
function lastPart(value) {
  const p = swiftSplit(value, ':');
  return p.length ? p[p.length - 1] : '';
}

// =========================================================================
// MARK: - 🟢 ORDRSP (SİPARİŞ YANITI)
// =========================================================================
function generateOrdrspHTML(segments) {
  const docNo = getVal(segments, 'BGM', 2);
  const docDate = formatDateTime(rawDTM(segments, '137'));

  const supplierHTML = formatAddress(segments, 'SU', L('pdf_header_sender'));
  const buyerHTML = formatAddress(segments, 'BY', L('pdf_header_buyer'));

  const items = [];
  let currentItem = newOrdrspItem();

  for (const seg of segments) {
    if (seg.tag === 'LIN') {
      if (currentItem.code !== '') items.push(currentItem);
      currentItem = newOrdrspItem();
      currentItem.actionCode = get(seg.elements, 2);
      currentItem.code = swiftSplit(get(seg.elements, 3), ':')[0] ?? '';
    }
    if (currentItem.code !== '') {
      if (seg.tag === 'IMD') currentItem.desc = lastPart(get(seg.elements, 3));
      if (seg.tag === 'QTY') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts.length >= 2) {
          const qual = parts[0];
          const val = parts[1];
          const unit = parts.length > 2 ? parts[2] : '';
          if (qual === '21') { currentItem.orderedQty = val; currentItem.unit = unit; }
          if (qual === '12') { currentItem.acceptedQty = val; currentItem.unit = unit; }
        }
      }
      if (seg.tag === 'PRI') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts.length >= 2) currentItem.price = parts[1];
      }
      if (seg.tag === 'FTX') currentItem.reason = get(seg.elements, 4);
    }
  }
  if (currentItem.code !== '') items.push(currentItem);

  const rowsHTML = items.map((item) => {
    let badge = '';
    let style = '';
    switch (item.actionCode) {
      case '5': badge = '✅'; break;
      case '7': badge = '❌'; style = 'background-color:#fff5f5;color:#999;'; break;
      case '3': badge = '⚠️'; style = 'background-color:#fff9db;'; break;
      default: badge = '';
    }
    return `
            <tr style="${style}">
                <td>${item.code}</td>
                <td><strong>${item.desc}</strong> ${badge}<br><small>${item.reason}</small></td>
                <td style="text-align:right;">${item.orderedQty}</td>
                <td style="text-align:right;">${item.acceptedQty}</td>
                <td style="text-align:right;">${item.price}</td>
            </tr>
            `;
  }).join('');

  return `
        <!DOCTYPE html><html><head><meta charset="utf-8"><style>${PAGE_CSS}
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; }
            .header { border-bottom: 4px solid #28a745; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
            .title { font-size: 26px; font-weight: 900; color: #28a745; text-transform: uppercase; }
            .meta { text-align: right; line-height: 1.6; font-size: 14px; }
            .addresses { display: flex; gap: 20px; margin-bottom: 30px; }
            .card { flex: 1; background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
            .card h3 { font-size: 11px; color: #888; text-transform: uppercase; margin: 0 0 5px 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th { text-align: left; background: #28a745; color: white; padding: 10px; font-size: 12px; text-transform: uppercase; }
            td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 13px; }
        </style></head><body>
            <div class="header">
                <div><div class="title">${L('pdf_title_ordrsp')}</div><small>ORDRSP / ${docDate}</small></div>
                <div class="meta"><div>Ref: <strong>${docNo}</strong></div></div>
            </div>
            <div class="addresses">${supplierHTML}${buyerHTML}</div>
            <table><thead><tr>
                <th>${L('pdf_col_code')}</th><th>${L('pdf_col_desc')}</th>
                <th style="text-align:right;">${L('pdf_col_ordered')}</th><th style="text-align:right;">${L('pdf_col_accepted')}</th><th style="text-align:right;">${L('pdf_col_price')}</th>
            </tr></thead><tbody>${rowsHTML}</tbody></table>
            <div style="margin-top:30px; font-size:12px; color:#666; text-align:center;">${L('pdf_note_ordrsp')}</div>
        </body></html>
        `;
}

function newOrdrspItem() {
  return { code: '', desc: '', actionCode: '', orderedQty: '-', acceptedQty: '-', unit: '', price: '', reason: '' };
}

// =========================================================================
// MARK: - 🟠 ORDCHG (SİPARİŞ DEĞİŞİKLİĞİ)
// =========================================================================
function generateOrdchgHTML(segments) {
  // ORDERS ile neredeyse aynıdır, sadece başlık ve renkler değişir.
  return generateOrdersHTML(segments)
    .split(L('pdf_title_orders')).join(L('pdf_title_ordchg'))
    .split('ORDERS /').join('ORDCHG /')
    .split('#007AFF').join('#fd7e14'); // Mavi -> Turuncu
}

// =========================================================================
// MARK: - 🟣 DESADV (İRSALİYE)
// =========================================================================
function generateDesadvHTML(segments) {
  const docNo = getVal(segments, 'BGM', 2);
  const docDate = formatDateTime(rawDTM(segments, '137'));

  const supplierHTML = formatAddress(segments, 'SU', L('pdf_header_sender'));
  const deliveryHTML = formatAddress(segments, 'DP', L('pdf_header_delivery'));

  const items = [];
  let currentItem = newDesadvItem();
  let currentSSCC = '';

  for (const seg of segments) {
    if (seg.tag === 'GIN' && get(seg.elements, 1) === 'BJ') currentSSCC = get(seg.elements, 2);
    if (seg.tag === 'LIN') {
      if (currentItem.code !== '') items.push(currentItem);
      currentItem = newDesadvItem();
      currentItem.code = swiftSplit(get(seg.elements, 3), ':')[0] ?? '';
      currentItem.sscc = currentSSCC;
    }
    if (currentItem.code !== '') {
      if (seg.tag === 'IMD') currentItem.desc = lastPart(get(seg.elements, 3));
      if (seg.tag === 'QTY') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts.length >= 2) {
          currentItem.qty = parts[1];
          currentItem.unit = parts.length > 2 ? parts[2] : '';
        }
      }
    }
  }
  if (currentItem.code !== '') items.push(currentItem);

  const rowsHTML = items.map((item) => {
    const ssccHtml = item.sscc === '' ? '' : `<br><small style="color:#6f42c1">📦 ${item.sscc}</small>`;
    return `
            <tr>
                <td>${item.code}</td>
                <td><strong>${item.desc}</strong>${ssccHtml}</td>
                <td style="text-align:right;">${item.qty} ${item.unit}</td>
            </tr>
            `;
  }).join('');

  return `
        <!DOCTYPE html><html><head><meta charset="utf-8"><style>${PAGE_CSS}
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; }
            .header { border-bottom: 4px solid #6f42c1; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
            .title { font-size: 26px; font-weight: 900; color: #6f42c1; text-transform: uppercase; }
            .meta { text-align: right; line-height: 1.6; font-size: 14px; }
            .addresses { display: flex; gap: 20px; margin-bottom: 30px; }
            .card { flex: 1; background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
            .card h3 { font-size: 11px; color: #888; text-transform: uppercase; margin: 0 0 5px 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th { text-align: left; background: #6f42c1; color: white; padding: 10px; font-size: 12px; text-transform: uppercase; }
            td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 13px; }
        </style></head><body>
            <div class="header">
                <div><div class="title">${L('pdf_title_desadv')}</div><small>DESADV / ${docDate}</small></div>
                <div class="meta"><div>Ref: <strong>${docNo}</strong></div></div>
            </div>
            <div class="addresses">${supplierHTML}${deliveryHTML}</div>
            <table><thead><tr>
                <th width="20%">${L('pdf_col_code')}</th>
                <th width="60%">${L('pdf_col_desc')}</th>
                <th width="20%" style="text-align:right;">${L('pdf_col_shipped')}</th>
            </tr></thead><tbody>${rowsHTML}</tbody></table>
        </body></html>
        `;
}

function newDesadvItem() {
  return { code: '', desc: '', qty: '', unit: '', sscc: '', batch: '', expiry: '' };
}

// =========================================================================
// MARK: - 🧪 RECADV (MAL KABUL)
// =========================================================================
function generateRecadvHTML(segments) {
  const docNo = getVal(segments, 'BGM', 2);
  const docDate = formatDateTime(rawDTM(segments, '137'));

  const supplierHTML = formatAddress(segments, 'SU', L('pdf_header_supplier'));
  const warehouseHTML = formatAddress(segments, 'DP', L('pdf_header_delivery'));

  const items = [];
  let currentItem = newRecadvItem();

  for (const seg of segments) {
    if (seg.tag === 'LIN') {
      if (currentItem.code !== '') items.push(currentItem);
      currentItem = newRecadvItem();
      currentItem.code = swiftSplit(get(seg.elements, 3), ':')[0] ?? '';
    }
    if (currentItem.code !== '') {
      if (seg.tag === 'IMD') currentItem.desc = lastPart(get(seg.elements, 3));
      if (seg.tag === 'QTY') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts.length >= 2) {
          const q = parts[0];
          const v = parts[1];
          const u = parts.length > 2 ? parts[2] : '';
          if (q === '12') { currentItem.despatchedQty = v; currentItem.unit = u; }
          if (q === '194') { currentItem.receivedQty = v; currentItem.unit = u; }
        }
      }
    }
  }
  if (currentItem.code !== '') items.push(currentItem);

  const rowsHTML = items.map((item) => {
    const s = parseFloat(item.despatchedQty) || 0;
    const r = parseFloat(item.receivedQty) || 0;
    const diff = r - s;
    let diffHtml;
    if (diff < 0) diffHtml = `<span style="color:red">${Math.trunc(diff)}</span>`;
    else if (diff > 0) diffHtml = `<span style="color:blue">+${Math.trunc(diff)}</span>`;
    else diffHtml = '<span style="color:green">OK</span>';

    return `
            <tr>
                <td>${item.code}</td><td><strong>${item.desc}</strong></td>
                <td style="text-align:right;">${item.despatchedQty}</td>
                <td style="text-align:right;">${item.receivedQty}</td>
                <td style="text-align:right;">${diffHtml}</td>
            </tr>
            `;
  }).join('');

  return `
        <!DOCTYPE html><html><head><meta charset="utf-8"><style>${PAGE_CSS}
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; }
            .header { border-bottom: 4px solid #20c997; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
            .title { font-size: 26px; font-weight: 900; color: #20c997; text-transform: uppercase; }
            .meta { text-align: right; line-height: 1.6; font-size: 14px; }
            .addresses { display: flex; gap: 20px; margin-bottom: 30px; }
            .card { flex: 1; background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
            .card h3 { font-size: 11px; color: #888; text-transform: uppercase; margin: 0 0 5px 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th { text-align: left; background: #20c997; color: white; padding: 10px; font-size: 12px; text-transform: uppercase; }
            td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 13px; }
        </style></head><body>
            <div class="header">
                <div><div class="title">${L('pdf_title_recadv')}</div><small>RECADV / ${docDate}</small></div>
                <div class="meta"><div>Ref: <strong>${docNo}</strong></div></div>
            </div>
            <div class="addresses">${supplierHTML}${warehouseHTML}</div>
            <table><thead><tr>
                <th>${L('pdf_col_code')}</th><th>${L('pdf_col_desc')}</th>
                <th style="text-align:right;">${L('pdf_col_shipped')}</th>
                <th style="text-align:right;">${L('pdf_col_received')}</th>
                <th style="text-align:right;">${L('pdf_col_diff')}</th>
            </tr></thead><tbody>${rowsHTML}</tbody></table>
            <div style="margin-top:30px; font-size:12px; color:#666; text-align:center;">${L('pdf_note_recadv')}</div>
        </body></html>
        `;
}

function newRecadvItem() {
  return { code: '', desc: '', unit: '', despatchedQty: '0', receivedQty: '0', varianceReason: '' };
}

// =========================================================================
// MARK: - 🚛 IFTMIN (NAKLİYE TALİMATI)
// =========================================================================
function generateIftminHTML(segments) {
  const docNo = getVal(segments, 'BGM', 2);
  const docDate = formatDateTime(rawDTM(segments, '137'));

  // Teslim Alma / Teslim Etme
  const raw1 = rawDTM(segments, '133');
  const raw2 = rawDTM(segments, '64');
  const pickupDate = raw1 !== '' ? formatDateTime(raw1) : '-';
  const deliveryDate = raw2 !== '' ? formatDateTime(raw2) : '-';

  // Lokasyonlar
  let loadingPlace = '';
  let dischargePlace = '';
  for (const seg of segments) {
    if (seg.tag === 'LOC') {
      if (get(seg.elements, 1) === '9') loadingPlace = get(seg.elements, 2);
      if (get(seg.elements, 1) === '11') dischargePlace = get(seg.elements, 2);
    }
  }

  const shipperHTML = formatAddress(segments, 'CZ', L('pdf_header_sender'));
  const consigneeHTML = formatAddress(segments, 'CN', L('pdf_header_delivery'));

  const items = [];
  let currentItem = newIftminItem();

  for (const seg of segments) {
    if (seg.tag === 'GID') {
      if (currentItem.id !== '') items.push(currentItem);
      currentItem = newIftminItem();
      currentItem.id = get(seg.elements, 1);
    }
    if (currentItem.id !== '') {
      if (seg.tag === 'PAC') {
        currentItem.packageQty = get(seg.elements, 1);
        currentItem.packageType = swiftSplit(get(seg.elements, 3), ':')[0] ?? 'PK';
      }
      if (seg.tag === 'MEA') {
        const parts = swiftSplit(get(seg.elements, 3), ':');
        if (parts.length >= 2) currentItem.weight = `${parts[1]} ${parts[0]}`;
      }
      if (seg.tag === 'HAN') currentItem.handling = get(seg.elements, 1);
    }
  }
  if (currentItem.id !== '') items.push(currentItem);

  let rowsHTML = '';
  let totalWeight = 0.0;
  for (const item of items) {
    const wStr = swiftSplit(item.weight, ' ')[0] ?? '0';
    totalWeight += parseFloat(wStr) || 0;
    rowsHTML += `<tr><td>${item.id}</td><td><strong>${item.packageQty}</strong> ${item.packageType}</td><td>${item.weight}</td><td>${item.handling}</td></tr>`;
  }

  return `
            <!DOCTYPE html><html><head><meta charset="utf-8"><style>${PAGE_CSS}
                body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; }
                .header { border-bottom: 4px solid #795548; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
                .title { font-size: 26px; font-weight: 900; color: #795548; text-transform: uppercase; }
                .meta { text-align: right; line-height: 1.6; font-size: 14px; }
                .route-box { background: #fdfbf7; border: 1px solid #d7ccc8; padding: 20px; margin-bottom: 30px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; }
                .route-point { flex: 1; }
                .route-arrow { flex: 0 0 50px; text-align: center; font-size: 24px; color: #795548; }
                .route-label { font-size: 11px; color: #8d6e63; text-transform: uppercase; font-weight: bold; }
                .route-val { font-size: 16px; font-weight: bold; color: #3e2723; margin-top: 5px; }
                .route-date { font-size: 12px; color: #555; margin-top: 2px; }
                .addresses { display: flex; gap: 20px; margin-bottom: 30px; }
                .card { flex: 1; background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
                .card h3 { font-size: 11px; color: #888; text-transform: uppercase; margin: 0 0 5px 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                th { text-align: left; background: #795548; color: white; padding: 10px; font-size: 12px; text-transform: uppercase; }
                td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 13px; }
                .total-weight-box { text-align: right; margin-top: 20px; font-size: 16px; font-weight: bold; color: #795548; }
            </style></head><body>
                <div class="header">
                    <div><div class="title">${L('pdf_title_iftmin')}</div><small>IFTMIN / ${docDate}</small></div>
                    <div class="meta"><div>Ref: <strong>${docNo}</strong></div></div>
                </div>
                <div class="route-box">
                    <div class="route-point"><div class="route-label">FROM</div><div class="route-val">📍 ${loadingPlace}</div><div class="route-date">📅 ${pickupDate}</div></div>
                    <div class="route-arrow">➝</div>
                    <div class="route-point" style="text-align:right;"><div class="route-label">TO</div><div class="route-val">🏁 ${dischargePlace}</div><div class="route-date">📅 ${deliveryDate}</div></div>
                </div>
                <div class="addresses">${shipperHTML}${consigneeHTML}</div>
                <table><thead><tr>
                    <th width="20%">${L('pdf_col_seq')}</th><th width="40%">${L('pdf_col_qty')}</th><th width="20%">${L('pdf_col_weight')}</th><th width="20%">Info</th>
                </tr></thead><tbody>${rowsHTML}</tbody></table>
                <div class="total-weight-box">TOTAL: ${Math.trunc(totalWeight)} KG</div>
            </body></html>
            `;
}

function newIftminItem() {
  return { id: '', packageType: '', packageQty: '', weight: '', handling: '' };
}

// =========================================================================
// MARK: - 🔵 INVOIC (FATURA)
// =========================================================================
function generateInvoicHTML(segments) {
  const docNo = getVal(segments, 'BGM', 2);
  const docDate = formatDateTime(rawDTM(segments, '137'));

  let orderRef = '-';
  let despatchRef = '-';
  for (const seg of segments.filter((s) => s.tag === 'RFF')) {
    const p = swiftSplit(get(seg.elements, 1), ':');
    const type = p.length ? p[0] : '';
    const val = p.length ? p[p.length - 1] : '-';
    if (type === 'ON') orderRef = val;
    if (type === 'DQ') despatchRef = val;
  }

  let bankName = '';
  let iban = '';
  let accountName = '';
  const fiiSeg = segments.find((s) => s.tag === 'FII' && get(s.elements, 1) === 'RB');
  if (fiiSeg) {
    accountName = get(fiiSeg.elements, 2);
    const rawIban = swiftSplit(get(fiiSeg.elements, 2), '+')[0] ?? '';
    iban = rawIban.includes(':') ? (swiftSplit(rawIban, ':')[0] ?? '') : rawIban;
    bankName = get(fiiSeg.elements, 4);
  }

  const sellerHTML = formatAddress(segments, 'SE', L('pdf_header_sender'));
  const buyerHTML = formatAddress(segments, 'BY', L('pdf_header_buyer'));

  const items = [];
  let currentItem = newInvoicItem();

  for (const seg of segments) {
    if (seg.tag === 'LIN') {
      if (currentItem.code !== '') items.push(currentItem);
      currentItem = newInvoicItem();
      currentItem.code = swiftSplit(get(seg.elements, 3), ':')[0] ?? '';
    }
    if (currentItem.code !== '') {
      if (seg.tag === 'IMD') currentItem.desc = lastPart(get(seg.elements, 3));
      if (seg.tag === 'QTY') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts.length >= 2) {
          currentItem.qty = parts[1];
          currentItem.unit = parts.length > 2 ? parts[2] : '';
        }
      }
      if (seg.tag === 'PRI') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts.length >= 2) currentItem.price = parts[1];
      }
      if (seg.tag === 'MOA') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if ((parts[0] ?? '') === '203' && parts.length >= 2) currentItem.total = parts[1];
      }
      if (seg.tag === 'TAX') {
        const parts = swiftSplit(get(seg.elements, 5), ':');
        if (parts.length) currentItem.vatRate = parts[parts.length - 1];
      }
    }
  }
  if (currentItem.code !== '') items.push(currentItem);

  let lineTotal = '0.00';
  let taxTotal = '0.00';
  let grandTotal = '0.00';
  let payableTotal = '0.00';
  for (const seg of segments) {
    if (seg.tag === 'MOA') {
      const parts = swiftSplit(get(seg.elements, 1), ':');
      if (parts.length >= 2) {
        const type = parts[0];
        const val = parts[1];
        if (type === '79') lineTotal = val;
        if (type === '124') taxTotal = val;
        if (type === '77') grandTotal = val;
        if (type === '9') payableTotal = val;
      }
    }
  }
  if (payableTotal === '0.00') payableTotal = grandTotal;

  const rowsHTML = items.map((item) => `
                <tr>
                    <td>${item.code}</td><td><strong>${item.desc}</strong></td>
                    <td style="text-align:right;">%${item.vatRate === '' ? '0' : item.vatRate}</td>
                    <td style="text-align:right;">${item.qty} ${item.unit}</td>
                    <td style="text-align:right;">${item.price}</td>
                    <td style="text-align:right;"><strong>${item.total}</strong></td>
                </tr>
                `).join('');

  return `
            <!DOCTYPE html><html><head><meta charset="utf-8"><style>${PAGE_CSS}
                body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; }
                .header { border-bottom: 4px solid #002366; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
                .title { font-size: 32px; font-weight: 900; color: #002366; text-transform: uppercase; letter-spacing: 1px; }
                .meta { text-align: right; line-height: 1.6; font-size: 14px; }
                .bank-box { background: #eef2f7; border: 1px solid #ced4da; padding: 15px; margin-bottom: 30px; border-radius: 4px; display: flex; align-items: center; gap: 20px; }
                .bank-icon { font-size: 24px; flex-shrink: 0; }
                .bank-info-group { min-width: 120px; }
                .bank-title { font-size: 10px; color: #666; text-transform: uppercase; font-weight:bold; margin-bottom: 2px; }
                .bank-val { font-size: 11px; font-weight: bold; color: #002366; font-family: monospace; word-break: break-all; }
                .addresses { display: flex; gap: 20px; margin-bottom: 30px; }
                .card { flex: 1; background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
                .card h3 { font-size: 11px; color: #888; text-transform: uppercase; margin: 0 0 5px 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                th { text-align: left; background: #002366; color: white; padding: 10px; font-size: 12px; text-transform: uppercase; }
                td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 13px; }
                .footer-wrapper { display: flex; justify-content: flex-end; margin-top: 30px; page-break-inside: avoid; }
                .total-box { width: 300px; }
                .total-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; color: #555; }
                .grand-total { font-size: 24px; font-weight: 900; color: #002366; border-top: 3px solid #002366; padding-top: 15px; margin-top: 10px; }
            </style></head><body>
                <div class="header">
                    <div><div class="title">${L('pdf_title_invoic')}</div><small>INVOIC / ${docDate}</small></div>
                    <div class="meta"><div>No: <strong>${docNo}</strong></div><div>Order: ${orderRef}</div></div>
                </div>
                <div class="addresses">${sellerHTML}${buyerHTML}</div>
                <div class="bank-box"><div class="bank-icon">🏦</div><div class="bank-info-group"><div class="bank-title">BANK</div><div style="font-weight:bold;">${bankName}</div></div><div class="bank-info-group" style="flex:2;"><div class="bank-title">IBAN</div><div class="bank-val">${iban}</div></div><div class="bank-info-group"><div class="bank-title">ACCOUNT</div><div class="bank-val">${accountName}</div></div></div>
                <table><thead><tr><th width="15%">${L('pdf_col_code')}</th><th width="40%">${L('pdf_col_desc')}</th><th width="10%">${L('pdf_col_vat')}</th><th width="10%">${L('pdf_col_qty')}</th><th width="10%">${L('pdf_col_price')}</th><th width="15%">${L('pdf_col_total')}</th></tr></thead><tbody>${rowsHTML}</tbody></table>
                <div class="footer-wrapper"><div class="total-box">
                    <div class="total-row"><span>${L('pdf_label_subtotal')}:</span><span>${lineTotal}</span></div>
                    <div class="total-row"><span>${L('pdf_label_taxes')}:</span><span>${taxTotal}</span></div>
                    <div class="total-row grand-total"><span>${L('pdf_label_payable')}:</span><span>€ ${payableTotal}</span></div>
                </div></div>
                <div style="margin-top:50px; font-size:10px; color:#999; text-align:center;">${L('pdf_note_invoic')}</div>
            </body></html>
            `;
}

function newInvoicItem() {
  return { code: '', desc: '', qty: '', unit: '', price: '', total: '', vatRate: '' };
}

// =========================================================================
// MARK: - 🟢 REMADV (ÖDEME DETAY)
// =========================================================================
function generateRemadvHTML(segments) {
  const docNo = getVal(segments, 'BGM', 2);
  const docDate = formatDateTime(rawDTM(segments, '137'));

  const rawValue = rawDTM(segments, '203');
  const valueDate = rawValue !== '' ? formatDateTime(rawValue) : '-';

  let totalPaid = '0.00';
  for (const seg of segments) {
    if (seg.tag === 'DOC') break;
    if (seg.tag === 'MOA') {
      const parts = swiftSplit(get(seg.elements, 1), ':');
      if (parts[0] === '12') totalPaid = parts.length ? parts[parts.length - 1] : '0.00';
    }
  }

  const payerHTML = formatAddress(segments, 'PR', L('pdf_header_payer'));
  const payeeHTML = formatAddress(segments, 'PE', L('pdf_header_payee'));

  const items = [];
  let currentItem = newRemadvItem();

  for (const seg of segments) {
    if (seg.tag === 'DOC') {
      if (currentItem.docNo !== '') items.push(currentItem);
      currentItem = newRemadvItem();
      const typeCode = get(seg.elements, 1);
      currentItem.docType = typeCode === '381' ? 'C.NOTE' : 'INVOICE';
      currentItem.docNo = get(seg.elements, 2);
    }
    if (currentItem.docNo !== '') {
      if (seg.tag === 'DTM') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts[0] === '137' && parts.length > 1) currentItem.date = formatDateTime(parts[1]);
      }
      if (seg.tag === 'MOA') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        const type = parts.length ? parts[0] : '';
        const val = parts.length ? parts[parts.length - 1] : '0';
        if (type === '12') currentItem.paidAmount = val;
        if (type === '19') currentItem.deduction = val;
      }
      if (seg.tag === 'AJT') currentItem.reason = `Code: ${get(seg.elements, 2)}`;
    }
  }
  if (currentItem.docNo !== '') items.push(currentItem);

  const rowsHTML = items.map((item) => {
    const typeBadge = item.docType === 'C.NOTE'
      ? `<span class="badge" style="background:#6c757d">${item.docType}</span>`
      : `<span class="badge" style="background:#007bff">${item.docType}</span>`;
    const deductionHTML = (item.deduction !== '' && item.deduction !== '0')
      ? `<div style="font-size:11px; color:#dc3545; margin-top:4px;">🔻 ${item.deduction} <br>(${item.reason})</div>`
      : '';
    return `<tr><td><strong>${item.docNo}</strong><br>${typeBadge}</td><td>${item.date}</td><td style="text-align:right;"><div style="font-weight:bold; font-size:15px;">${item.paidAmount}</div>${deductionHTML}</td></tr>`;
  }).join('');

  return `
            <!DOCTYPE html><html><head><meta charset="utf-8"><style>${PAGE_CSS}
                body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; }
                .header { border-bottom: 4px solid #28a745; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
                .title { font-size: 26px; font-weight: 900; color: #28a745; text-transform: uppercase; }
                .meta { text-align: right; line-height: 1.6; font-size: 14px; }
                .total-paid-box { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 20px; margin-bottom: 30px; border-radius: 8px; text-align:center; }
                .tp-label { font-size: 12px; text-transform: uppercase; font-weight:bold; }
                .tp-val { font-size: 32px; font-weight: 900; margin-top: 5px; }
                .addresses { display: flex; gap: 20px; margin-bottom: 30px; }
                .card { flex: 1; background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
                .card h3 { font-size: 11px; color: #888; text-transform: uppercase; margin: 0 0 5px 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                th { text-align: left; background: #28a745; color: white; padding: 10px; font-size: 12px; text-transform: uppercase; }
                td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 13px; }
                .badge { display: inline-block; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; color: white; margin-top: 4px; }
            </style></head><body>
                <div class="header">
                    <div><div class="title">${L('pdf_title_remadv')}</div><small>REMADV / ${docDate}</small></div>
                    <div class="meta"><div>Ref: <strong>${docNo}</strong></div><div>Date: ${valueDate}</div></div>
                </div>
                <div class="total-paid-box"><div class="tp-label">${L('pdf_label_total_paid')}</div><div class="tp-val">€ ${totalPaid}</div></div>
                <div class="addresses">${payerHTML}${payeeHTML}</div>
                <table><thead><tr><th width="40%">Ref</th><th width="30%">Date</th><th width="30%" style="text-align:right;">Paid</th></tr></thead><tbody>${rowsHTML}</tbody></table>
            </body></html>
            `;
}

function newRemadvItem() {
  return { docType: '', docNo: '', date: '', paidAmount: '', deduction: '', reason: '' };
}

// =========================================================================
// MARK: - 🔴 DELJIT (JIT ÇAĞRISI)
// =========================================================================
function generateDeljitHTML(segments) {
  const docNo = getVal(segments, 'BGM', 2);
  const docDate = formatDateTime(rawDTM(segments, '137'));

  const factoryHTML = formatAddress(segments, 'BY', L('pdf_header_factory'));
  const supplierHTML = formatAddress(segments, 'SE', L('pdf_header_supplier'));

  const items = [];
  let currentLinCode = '';
  let currentLinDesc = '';
  let currentLinLoc = '';
  let currentLinNote = '';
  let currentItem = newDeljitItem();

  for (const seg of segments) {
    if (seg.tag === 'LIN') {
      currentLinCode = swiftSplit(get(seg.elements, 3), ':')[0] ?? '';
      currentLinDesc = ''; currentLinLoc = ''; currentLinNote = '';
    }
    if (seg.tag === 'IMD') currentLinDesc = lastPart(get(seg.elements, 3));
    if (seg.tag === 'LOC') {
      const place = get(seg.elements, 2);
      if (place !== '') currentLinLoc += (currentLinLoc === '' ? '' : ' / ') + place;
    }
    if (seg.tag === 'FTX') currentLinNote = get(seg.elements, 4);

    if (seg.tag === 'SEQ') {
      if (currentItem.sequence !== '') items.push(currentItem);
      currentItem = newDeljitItem();
      currentItem.sequence = get(seg.elements, 2);
      currentItem.code = currentLinCode;
      currentItem.desc = currentLinDesc;
      currentItem.location = currentLinLoc;
      currentItem.note = currentLinNote;
    }
    if (currentItem.sequence !== '') {
      if (seg.tag === 'QTY') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts.length >= 2) currentItem.qty = `${parts[1]} ${parts.length > 2 ? parts[2] : ''}`;
      }
      if (seg.tag === 'DTM') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts[0] === '2' && parts.length > 1) {
          const val = parts[1];
          if (val.length >= 12) {
            currentItem.time = `${val.slice(8, 10)}:${val.slice(10, 12)}`;
          } else {
            currentItem.time = val;
          }
        }
      }
      if (seg.tag === 'GIR') currentItem.ref = swiftSplit(get(seg.elements, 2), ':')[0] ?? '';
    }
  }
  if (currentItem.sequence !== '') items.push(currentItem);

  const rowsHTML = items.map((item) => {
    const noteHTML = item.note === '' ? '' : `<div style="font-size:11px; background:#fff3cd; color:#856404; padding:2px 5px; border-radius:3px; margin-top:3px; display:inline-block;">⚠️ ${item.note}</div>`;
    return `
                <tr>
                    <td style="text-align:center; background:#fbeaea; font-weight:bold; color:#dc3545;">${item.time}</td>
                    <td style="text-align:center;">${item.sequence}</td>
                    <td><strong>${item.desc}</strong><br><small>Kod: ${item.code}</small><br>${noteHTML}</td>
                    <td><div class="loc-badge">📍 ${item.location}</div><div style="font-size:11px; color:#666; margin-top:2px;">Ref: ${item.ref}</div></td>
                    <td style="text-align:right; font-weight:bold; font-size:16px;">${item.qty}</td>
                </tr>
                `;
  }).join('');

  return `
            <!DOCTYPE html><html><head><meta charset="utf-8"><style>${PAGE_CSS}
                body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; }
                .header { border-bottom: 4px solid #dc3545; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
                .title { font-size: 26px; font-weight: 900; color: #dc3545; text-transform: uppercase; }
                .meta { text-align: right; line-height: 1.6; font-size: 14px; }
                .priority-box { background: #dc3545; color: white; padding: 15px; margin-bottom: 30px; border-radius: 4px; text-align:center; font-weight:bold; letter-spacing:1px;}
                .addresses { display: flex; gap: 20px; margin-bottom: 30px; }
                .card { flex: 1; background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
                .card h3 { font-size: 11px; color: #888; text-transform: uppercase; margin: 0 0 5px 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                th { text-align: left; background: #333; color: white; padding: 10px; font-size: 12px; text-transform: uppercase; }
                td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 13px; }
                .loc-badge { background: #e2e3e5; color: #383d41; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; display: inline-block; }
            </style></head><body>
                <div class="header">
                    <div><div class="title">${L('pdf_title_deljit')}</div><small>DELJIT / ${docDate}</small></div>
                    <div class="meta"><div>Ref: <strong>${docNo}</strong></div></div>
                </div>
                <div class="priority-box">⚠️ JIT / URGENT</div>
                <div class="addresses">${supplierHTML}${factoryHTML}</div>
                <table><thead><tr>
                    <th width="10%" style="text-align:center;">${L('pdf_col_time')}</th>
                    <th width="10%" style="text-align:center;">${L('pdf_col_seq')}</th>
                    <th width="35%">${L('pdf_col_part')}</th>
                    <th width="25%">${L('pdf_col_loc')}</th>
                    <th width="20%" style="text-align:right;">${L('pdf_col_qty')}</th>
                </tr></thead><tbody>${rowsHTML}</tbody></table>
                <div style="margin-top:30px; font-size:11px; color:#666; text-align:center;">${L('pdf_note_deljit')}</div>
            </body></html>
            `;
}

function newDeljitItem() {
  return { sequence: '', time: '', code: '', desc: '', qty: '', location: '', ref: '', note: '' };
}

// =========================================================================
// MARK: - 📉 SLSRPT (SATIŞ RAPORU)
// =========================================================================
function generateSlsrptHTML(segments) {
  const docNo = getVal(segments, 'BGM', 2);
  const docDate = formatDateTime(rawDTM(segments, '137'));

  const rawStart = rawDTM(segments, '356');
  const rawEnd = rawDTM(segments, '357');
  const periodStart = rawStart !== '' ? formatDateTime(rawStart) : '-';
  const periodEnd = rawEnd !== '' ? formatDateTime(rawEnd) : '-';

  const storeHTML = formatAddress(segments, 'SE', L('pdf_header_store'));
  const supplierHTML = formatAddress(segments, 'SU', L('pdf_header_supplier'));

  const items = [];
  let currentItem = newSlsrptItem();

  for (const seg of segments) {
    if (seg.tag === 'LIN') {
      if (currentItem.code !== '') items.push(currentItem);
      currentItem = newSlsrptItem();
      currentItem.code = swiftSplit(get(seg.elements, 3), ':')[0] ?? '';
    }
    if (currentItem.code !== '') {
      if (seg.tag === 'IMD') currentItem.desc = lastPart(get(seg.elements, 3));
      if (seg.tag === 'QTY') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts[0] === '152' && parts.length >= 2) {
          currentItem.soldQty = parts[1];
          currentItem.unit = parts.length > 2 ? parts[2] : '';
        }
      }
      if (seg.tag === 'MOA') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts[0] === '203' && parts.length >= 2) currentItem.revenue = parts[1];
      }
      if (seg.tag === 'PRI') {
        const parts = swiftSplit(get(seg.elements, 1), ':');
        if (parts.length >= 2) currentItem.unitPrice = parts[1];
      }
    }
  }
  if (currentItem.code !== '') items.push(currentItem);

  let totalRevenue = 0.0;
  let totalUnits = 0;
  let rowsHTML = '';

  for (const item of items) {
    totalRevenue += parseFloat(item.revenue) || 0.0;
    totalUnits += Math.trunc(parseFloat(item.soldQty) || 0);

    rowsHTML += `
                <tr>
                    <td>${item.code}</td>
                    <td><strong>${item.desc}</strong></td>
                    <td style="text-align:right;">${item.unitPrice}</td>
                    <td style="text-align:right; font-weight:bold;">${item.soldQty} ${item.unit}</td>
                    <td style="text-align:right; font-weight:bold; color:#2c3e50;">${item.revenue}</td>
                </tr>
                `;
  }
  const totalRevenueStr = totalRevenue.toFixed(2);

  return `
            <!DOCTYPE html><html><head><meta charset="utf-8"><style>${PAGE_CSS}
                body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; }
                .header { border-bottom: 4px solid #1a252f; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
                .title { font-size: 26px; font-weight: 900; color: #1a252f; text-transform: uppercase; letter-spacing:1px; }
                .meta { text-align: right; line-height: 1.6; font-size: 14px; }
                .kpi-container { display: flex; gap: 20px; margin-bottom: 30px; }
                .kpi-card { flex: 1; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; text-align: center; }
                .kpi-title { font-size: 11px; color: #7f8c8d; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; }
                .kpi-val { font-size: 28px; font-weight: 900; color: #2c3e50; margin-top: 10px; }
                .kpi-icon { font-size: 24px; margin-bottom: 5px; }
                .addresses { display: flex; gap: 20px; margin-bottom: 30px; }
                .card { flex: 1; background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
                .card h3 { font-size: 11px; color: #888; text-transform: uppercase; margin: 0 0 5px 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                th { text-align: left; background: #2c3e50; color: white; padding: 10px; font-size: 12px; text-transform: uppercase; }
                td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 13px; }
                .period-badge { background: #d6eaf8; color: #1a5276; padding: 5px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; display:inline-block; margin-top:5px; }
            </style></head><body>
                <div class="header">
                    <div>
                        <div class="title">${L('pdf_title_slsrpt')}</div>
                        <small>SLSRPT / ${docDate}</small>
                        <div class="period-badge">${L('pdf_label_period')}: ${periodStart} - ${periodEnd}</div>
                    </div>
                    <div class="meta"><div>Ref: <strong>${docNo}</strong></div><div>EUR</div></div>
                </div>
                <div class="kpi-container">
                    <div class="kpi-card"><div class="kpi-icon">💰</div><div class="kpi-title">${L('pdf_label_total_revenue')}</div><div class="kpi-val">€ ${totalRevenueStr}</div></div>
                    <div class="kpi-card"><div class="kpi-icon">📦</div><div class="kpi-title">${L('pdf_label_total_units')}</div><div class="kpi-val">${totalUnits}</div></div>
                    <div class="kpi-card"><div class="kpi-icon">📊</div><div class="kpi-title">${L('pdf_label_total_sku')}</div><div class="kpi-val">${items.length}</div></div>
                </div>
                <div class="addresses">${storeHTML}${supplierHTML}</div>
                <table>
                    <thead><tr>
                        <th width="15%">${L('pdf_col_code')}</th>
                        <th width="45%">${L('pdf_col_desc')}</th>
                        <th width="15%" style="text-align:right;">${L('pdf_col_price')}</th>
                        <th width="10%" style="text-align:right;">${L('pdf_col_qty')}</th>
                        <th width="15%" style="text-align:right;">${L('pdf_label_total_revenue')}</th>
                    </tr></thead>
                    <tbody>${rowsHTML}</tbody>
                </table>
                <div style="margin-top:30px; font-size:11px; color:#666; text-align:center;">${L('pdf_note_slsrpt')}</div>
            </body></html>
            `;
}

function newSlsrptItem() {
  return { code: '', desc: '', soldQty: '0', unit: '', revenue: '0.00', unitPrice: '' };
}

// =========================================================================
// MARK: - ⚪️ GENERIC MOTOR (DİĞERLERİ)
// =========================================================================
function generateGenericHTML(segments) {
  const rawContent = segments.map((s) => s.rawLine).join('<br>');
  return `<html><head><meta charset="utf-8"><style>${PAGE_CSS}</style></head><body style="font-family:monospace; padding:20px;"><h3>EDI Viewer</h3><div style="background:#f0f0f0; padding:10px;">${rawContent}</div></body></html>`;
}

// =========================================================================
// MARK: - PDF KAYDETME (savePanel + WKWebView.createPDF karşılığı)
// Tarayıcının yazdırma diyaloğu açılır; "Hedef: PDF olarak kaydet" seçilir.
// =========================================================================
function savePDF(htmlContent) {
  const old = document.getElementById('pdf-print-frame');
  if (old) old.remove();

  const iframe = document.createElement('iframe');
  iframe.id = 'pdf-print-frame';
  iframe.setAttribute('aria-hidden', 'true');
  iframe.style.cssText = 'position:fixed; right:0; bottom:0; width:0; height:0; border:0; visibility:hidden;';
  document.body.appendChild(iframe);

  iframe.srcdoc = htmlContent;
  iframe.onload = () => {
    // Yazı tiplerinin yerleşmesi için bir tık bekle
    setTimeout(() => {
      try {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
      } catch (e) {
        console.error('❌ PDF Oluşturma Hatası:', e);
      }
    }, 120);
  };
}
