// Örnek dosya seçim ekranı.
//
// Mevcut `showDialog` dikey bir buton yığınıdır; 15 seçenek oraya sığmaz.
// Bu yüzden aynı `.backdrop` katmanını (arka plan, animasyon, Escape ile
// kapanma) paylaşan ama gövdesi ızgara olan ayrı bir bileşen kullanılır.
//
// Liste standarda göre iki gruba ayrılır ve her kart, o mesaj tipiyle
// uygulamanın NE YAPABİLDİĞİNİ rozetlerle gösterir — kullanıcı neden
// ORDERS'ta PDF'in açık, 850'de kapalı olduğunu böylece görür.
import { L } from './i18n.js';
import { SAMPLE_CATALOG, DEFAULT_SAMPLE_TYPE } from './sampleData.js';

const LAST_TYPE_KEY = 'lastSampleType';

const esc = (s) =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/** Standart kodu -> grup başlığı. Marka adları olduğu için çevrilmez. */
const GROUP_LABEL = { EDIFACT: 'UN/EDIFACT', X12: 'ANSI ASC X12' };

/** Son seçilen tip; hiç seçim yapılmamışsa varsayılan. */
export function lastSampleType() {
  try {
    const stored = localStorage.getItem(LAST_TYPE_KEY);
    if (stored && SAMPLE_CATALOG.some((s) => s.type === stored)) return stored;
  } catch {
    // Depolama kapalıysa varsayılana düşmek yeterli
  }
  return DEFAULT_SAMPLE_TYPE;
}

export function rememberSampleType(type) {
  try {
    localStorage.setItem(LAST_TYPE_KEY, type);
  } catch {
    // Seçim yalnızca oturum boyunca yaşar; sorun değil
  }
}

/**
 * Seçim ekranını çizer.
 * @param {HTMLElement} body  kartların yerleştirileceği konteyner
 * @param {string} selected   şu an seçili tip (işaretlenir)
 */
export function renderSamplePicker(body, selected) {
  const groups = ['EDIFACT', 'X12'];

  body.innerHTML = groups
    .map((standard) => {
      const items = SAMPLE_CATALOG.filter((s) => s.standard === standard);
      if (!items.length) return '';

      const cards = items
        .map((s) => {
          const badges = [];
          if (s.pdf) badges.push('<span class="sample-badge pdf">PDF</span>');
          if (s.excel) badges.push('<span class="sample-badge xls">Excel</span>');
          if (!s.pdf && !s.excel) {
            badges.push(`<span class="sample-badge view">${esc(L('sample_badge_view'))}</span>`);
          }

          return `
            <button class="sample-card${s.type === selected ? ' active' : ''}"
                    data-sample-type="${esc(s.type)}">
              <span class="sample-code">${esc(s.type)}</span>
              <span class="sample-name">${esc(L(`type_${s.type}`))}</span>
              <span class="sample-badges">${badges.join('')}</span>
            </button>`;
        })
        .join('');

      return `
        <div class="sample-group">
          <div class="sample-group-title">${esc(GROUP_LABEL[standard])}</div>
          <div class="sample-grid">${cards}</div>
        </div>`;
    })
    .join('');
}
