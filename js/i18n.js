// LocalizationManager.swift -> web karşılığı
// JSON tabanlı çeviri, İngilizce fallback ile (ADIM 1/2/3 mantığı korundu).

export const Language = {
  tr: { code: 'tr', name: 'Türkçe' },
  en: { code: 'en', name: 'English' },
  de: { code: 'de', name: 'Deutsch' },
  fr: { code: 'fr', name: 'Français' },
  es: { code: 'es', name: 'Español' },
  it: { code: 'it', name: 'Italiano' },
  zhHans: { code: 'zh-Hans', name: '简体中文' },
};

export const allLanguages = Object.values(Language);

const STORAGE_KEY = 'selectedLanguageCode';

class LocalizationManager extends EventTarget {
  constructor() {
    super();
    this.translations = {};
    this._fallback = null;
    this.currentLanguageCode = localStorage.getItem(STORAGE_KEY) || 'en';
  }

  get currentLanguage() {
    return allLanguages.find((l) => l.code === this.currentLanguageCode) || Language.tr;
  }

  async setLanguage(code) {
    this.currentLanguageCode = code;
    localStorage.setItem(STORAGE_KEY, code);
    await this.loadTranslations();
  }

  async loadTranslations() {
    // ADIM 1: Varsayılan dili (İngilizce) yükle -> fallback mekanizması
    if (!this._fallback) {
      this._fallback = await this._fetchDict('en');
    }
    let temp = { ...this._fallback };

    // ADIM 2: Seçili dil İngilizce değilse üzerine yaz (merge)
    if (this.currentLanguageCode !== 'en') {
      const dict = await this._fetchDict(this.currentLanguageCode);
      if (dict) temp = { ...temp, ...dict };
    }

    // ADIM 3: UI güncellemesi
    this.translations = temp;
    this.dispatchEvent(new Event('change'));
  }

  async _fetchDict(code) {
    try {
      const res = await fetch(`locales/${code}.json`);
      if (!res.ok) throw new Error(res.statusText);
      return await res.json();
    } catch (e) {
      console.warn(`Dil dosyası okunamadı: ${code}.json`, e);
      return null;
    }
  }

  localize(key) {
    return this.translations[key] ?? key;
  }
}

export const loc = new LocalizationManager();

/** "key".localized karşılığı */
export function L(key) {
  return loc.localize(key);
}

/** String(format:) karşılığı — %@ ve %d yer tutucularını sırayla doldurur. */
export function Lf(key, ...args) {
  const format = loc.localize(key);
  let i = 0;
  return format.replace(/%(@|d|s|(\d+)\$@)/g, (m, _t, pos) => {
    if (pos) return args[parseInt(pos, 10) - 1] ?? '';
    return args[i++] ?? '';
  });
}
