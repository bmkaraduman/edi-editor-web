// Rıza yönetimi — Google Consent Mode v2 + yedek bant.
//
// Asıl plan: rıza ekranını AEA / Birleşik Krallık / İsviçre'de Google'ın
// sertifikalı CMP'si gösterir. Ancak CMP sayfaya hiç gelmezse (site henüz
// reklam yayınına açılmamışsa böyle olur) kimse izin veremez; izinler
// varsayılan "reddedildi"de kalır ve o bölgelerden ölçüm de toplanamaz.
//
// Bu yüzden bir yedek bant vardır: CMP birkaç saniye içinde yüklenmezse
// devreye girer ve YALNIZCA ölçüm (analytics) izni ister. Reklam izinleri
// bilerek dışarıda bırakılmıştır — Google, AEA'da reklam için sertifikalı
// bir CMP şartı koşar ve elle yazılmış bir bant bu şartı karşılamaz.

const GA_ID = 'G-3C1DF6XY4D';
const ADSENSE_CLIENT = 'ca-pub-7507702503844486';

/** AEA (AB 27 + İzlanda, Lihtenştayn, Norveç) + Birleşik Krallık + İsviçre */
const CONSENT_REQUIRED_REGIONS = [
  'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
  'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
  'SI', 'ES', 'SE', 'IS', 'LI', 'NO', 'GB', 'CH',
];

const STORE_KEY = 'analyticsConsent'; // 'granted' | 'denied'
const CMP_WAIT_MS = 4000;

// =========================================================================
// CONSENT MODE
// =========================================================================

function setConsentDefaults() {
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };

  window.gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    wait_for_update: 500,
    region: CONSENT_REQUIRED_REGIONS,
  });

  window.gtag('set', 'ads_data_redaction', true);

  // Daha önce ölçüme izin verilmişse geri yükle
  if (localStorage.getItem(STORE_KEY) === 'granted') {
    window.gtag('consent', 'update', { analytics_storage: 'granted' });
  }
}

function loadGoogleAnalytics() {
  const s = document.createElement('script');
  s.async = true;
  s.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  document.head.appendChild(s);

  window.gtag('js', new Date());
  window.gtag('config', GA_ID);
}

function loadAdSense() {
  const s = document.createElement('script');
  s.async = true;
  s.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_CLIENT}`;
  s.crossOrigin = 'anonymous';
  document.head.appendChild(s);
}

// =========================================================================
// YEDEK BANT
// =========================================================================

const TEXTS = {
  tr: { t: 'Ziyaretçi istatistikleri', m: 'Siteyi geliştirebilmek için anonim kullanım istatistikleri toplamak istiyoruz. Reddederseniz hiçbir ölçüm yapılmaz; uygulama aynı şekilde çalışır.', y: 'Kabul Et', n: 'Reddet', p: 'Gizlilik Politikası' },
  en: { t: 'Visitor statistics', m: 'We would like to collect anonymous usage statistics to improve the site. If you decline, no measurement takes place and the app works exactly the same.', y: 'Accept', n: 'Decline', p: 'Privacy Policy' },
  de: { t: 'Besucherstatistiken', m: 'Wir möchten anonyme Nutzungsstatistiken erheben, um die Website zu verbessern. Wenn Sie ablehnen, findet keine Messung statt.', y: 'Akzeptieren', n: 'Ablehnen', p: 'Datenschutz' },
  fr: { t: 'Statistiques de visite', m: "Nous souhaitons collecter des statistiques d'usage anonymes pour améliorer le site. Si vous refusez, aucune mesure n'est effectuée.", y: 'Accepter', n: 'Refuser', p: 'Confidentialité' },
  es: { t: 'Estadísticas de visitas', m: 'Nos gustaría recopilar estadísticas de uso anónimas para mejorar el sitio. Si lo rechazas, no se realiza ninguna medición.', y: 'Aceptar', n: 'Rechazar', p: 'Privacidad' },
  it: { t: 'Statistiche di visita', m: "Vorremmo raccogliere statistiche d'uso anonime per migliorare il sito. Se rifiuti, non viene effettuata alcuna misurazione.", y: 'Accetta', n: 'Rifiuta', p: 'Privacy' },
  'zh-Hans': { t: '访问统计', m: '我们希望收集匿名使用统计以改进网站。若您拒绝，将不会进行任何统计。', y: '接受', n: '拒绝', p: '隐私政策' },
};

function lang() {
  const stored = localStorage.getItem('selectedLanguageCode');
  if (stored && TEXTS[stored]) return stored;
  const doc = document.documentElement.lang;
  return TEXTS[doc] ? doc : 'en';
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/** Gizlilik politikasının bulunduğu sayfaya göre göreli adresi */
export function privacyURL() {
  const tr = lang() === 'tr';
  // edi/ altındaki sayfalar kökten bir ya da iki seviye aşağıdadır
  const depth = (location.pathname.match(/\/edi\//) ? location.pathname.split('/').length - 2 : 0);
  const up = '../'.repeat(Math.max(0, depth));
  return up + (tr ? 'gizlilik.html' : 'privacy.html');
}

let bannerEl = null;

function showFallbackBanner() {
  if (bannerEl) return;
  const t = TEXTS[lang()];

  bannerEl = document.createElement('div');
  bannerEl.className = 'consent-banner';
  bannerEl.setAttribute('role', 'dialog');
  bannerEl.innerHTML = `
    <div class="consent-text">
      <div class="consent-title">${esc(t.t)}</div>
      <div class="consent-msg">${esc(t.m)}
        <a class="consent-link" href="${privacyURL()}">${esc(t.p)}</a>
      </div>
    </div>
    <div class="consent-actions">
      <button class="consent-btn" data-consent="denied">${esc(t.n)}</button>
      <button class="consent-btn primary" data-consent="granted">${esc(t.y)}</button>
    </div>`;

  bannerEl.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-consent]');
    if (!btn) return;
    const choice = btn.dataset.consent;
    localStorage.setItem(STORE_KEY, choice);
    if (choice === 'granted') {
      window.gtag('consent', 'update', { analytics_storage: 'granted' });
    }
    hideFallbackBanner();
  });

  // Giriş animasyonu YALNIZCA çalışacağından emin olduğumuzda uygulanır.
  // Gizli/kısıtlanmış sekmede CSS geçişleri ilerlemez; başlangıç durumunu
  // uygulayıp geçişe güvenirsek bant ekran dışında, saydam hâlde takılı kalır.
  // Böyle bir durumda animasyonu tümüyle atlayıp bandı doğrudan yerine koyarız.
  const animate = !document.hidden
    && !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (animate) bannerEl.classList.add('entering');
  document.body.appendChild(bannerEl);
  if (animate) {
    void bannerEl.offsetWidth;
    bannerEl.classList.remove('entering');
  }
}

function hideFallbackBanner() {
  if (!bannerEl) return;
  const el = bannerEl;
  bannerEl = null;
  el.classList.add('leaving');
  setTimeout(() => el.remove(), 250);
}

/** Ziyaretçi rıza istenen bir bölgede mi? Cloudflare'in trace ucundan okunur. */
async function inConsentRegion() {
  // Yerel geliştirmede Cloudflare yok; boşuna istek atıp konsola 404 düşürme
  if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') return false;
  try {
    const txt = await (await fetch('/cdn-cgi/trace', { cache: 'no-store' })).text();
    const loc = txt.match(/^loc=(\w+)/m)?.[1];
    return CONSENT_REQUIRED_REGIONS.includes(loc);
  } catch {
    // Belirlenemiyorsa (yerel geliştirme) bant gösterilmez;
    // Consent Mode varsayılanları zaten depolamayı kısıtlıyor.
    return false;
  }
}

/**
 * Google'ın CMP'si gelmezse yedek bandı devreye alır.
 * CMP gelirse hiçbir şey yapılmaz — sertifikalı olan o.
 */
async function armFallback() {
  if (localStorage.getItem(STORE_KEY)) return;      // karar verilmiş
  if (!(await inConsentRegion())) return;           // rıza gerekmiyor

  await new Promise((r) => setTimeout(r, CMP_WAIT_MS));
  if (consentUIAvailable()) return;                 // CMP geldi, karışma
  if (localStorage.getItem(STORE_KEY)) return;

  showFallbackBanner();
}

// =========================================================================
// DIŞA AÇIK API
// =========================================================================

/** Google'ın CMP'si sayfada mı? */
export function consentUIAvailable() {
  return typeof window.googlefc?.showRevocationMessage === 'function';
}

/** Rıza ekranını yeniden açar: önce Google'ın CMP'si, yoksa yedek bant. */
export function reopenConsent() {
  if (consentUIAvailable()) {
    window.googlefc.showRevocationMessage();
    return true;
  }
  localStorage.removeItem(STORE_KEY);
  showFallbackBanner();
  return true;
}

/**
 * Açılışta, mümkün olan en erken anda çağrılır.
 * @param {{ads?: boolean}} opts ads=false → yalnızca ölçüm yüklenir.
 */
export function initConsent({ ads = true } = {}) {
  setConsentDefaults();
  loadGoogleAnalytics();
  if (ads) loadAdSense();
  armFallback();
}
