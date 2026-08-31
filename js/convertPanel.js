// Dönüşüm menüsü — toolbar açılır listesi ve dönüşümün yürütülmesi.
//
// Kendi modal bileşenini getirmez: mevcut .menu / .menu-popup / .menu-item
// yapısını kullanır, böylece dışarı tıklayınca kapanma ve tema uyumu bedavaya
// gelir. Sonuç yeni bir sekmede açılır; sekme, düzenleme ve kaydetme
// altyapısının tamamı DocumentManager'da zaten var.
import { L } from './i18n.js';
import { ConvertManager, ConvertError } from './convert.js';
import { stripExtension } from './documentManager.js';

/** Kaynak dile göre sunulacak hedefler. Dört yön de buradan çıkar. */
const TARGETS = {
  edi: ['json', 'xml'],
  json: ['edi', 'xml'],
  xml: ['edi', 'json'],
};

const LABEL_KEY = { edi: 'conv_to_edi', json: 'conv_to_json', xml: 'conv_to_xml' };

const OPTIONS_KEY = 'convertOptions';

/** Kullanıcı tercihleri — tema/dil gibi kalıcı tutulur. */
export const convertOptions = loadOptions();

function loadOptions() {
  const fallback = { annotated: false, pretty: true };
  try {
    const raw = localStorage.getItem(OPTIONS_KEY);
    if (!raw) return fallback;
    return { ...fallback, ...JSON.parse(raw) };
  } catch {
    return fallback;
  }
}

export function setConvertOption(name, value) {
  convertOptions[name] = value;
  try {
    localStorage.setItem(OPTIONS_KEY, JSON.stringify(convertOptions));
  } catch {
    // Depolama kapalıysa seçim yalnızca oturum boyunca yaşar; sorun değil.
  }
}

const esc = (s) =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/** Açılır listenin içeriği. Aktif belgenin diline göre hedefler değişir. */
export function convertMenuHTML(doc) {
  const language = doc && !doc.isStartPage ? doc.language || 'edi' : null;
  const targets = language ? TARGETS[language] || TARGETS.edi : [];

  const items = targets
    .map(
      (t) => `
        <button class="menu-item" data-convert-to="${t}">
          <span class="menu-check"></span>
          <span>${esc(L(LABEL_KEY[t]))}</span>
        </button>`
    )
    .join('');

  const body = items || `<div class="menu-empty">${esc(L('conv_hint_open'))}</div>`;

  const toggle = (name, labelKey) => `
    <button class="menu-item" data-convert-opt="${name}">
      <span class="menu-check">${convertOptions[name] ? '✓' : ''}</span>
      <span>${esc(L(labelKey))}</span>
    </button>`;

  return (
    `<div class="menu-header">${esc(L('conv_title'))}</div>` +
    body +
    '<div class="menu-sep"></div>' +
    `<div class="menu-header">${esc(L('conv_options'))}</div>` +
    toggle('annotated', 'conv_opt_annotated') +
    toggle('pretty', 'conv_opt_pretty')
  );
}

/**
 * Belgeyi hedef biçime çevirir.
 * @throws {ConvertError} arayüzün diyalogla göstereceği, çevrilebilir hata
 * @returns {{content:string, fileName:string, language:string, conversion:object}}
 */
export function convertDocument(doc, target) {
  const from = doc.language || 'edi';
  const { text, roundTrip } = ConvertManager.convert(doc.content, {
    from,
    to: target,
    annotated: convertOptions.annotated,
    pretty: convertOptions.pretty,
  });

  return {
    content: text,
    fileName: `${stripExtension(doc.fileName)}.${target}`,
    language: target,
    conversion: { ok: roundTrip.ok, reason: roundTrip.reason ?? '', from, to: target },
  };
}

/** ConvertError'ı showDialog seçeneklerine çevirir. */
export function conversionErrorDialog(error) {
  const key = error instanceof ConvertError ? error.key : null;
  return {
    icon: '⚠️',
    title: L('conv_err_title'),
    message: key ? L(key) : String(error?.message ?? ''),
  };
}
