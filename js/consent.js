// Çerez onayı.
// Google Analytics ve AdSense YALNIZCA kullanıcı kabul ettikten sonra yüklenir;
// reddedilirse hiçbir harici istek yapılmaz.
import { loc, L } from './i18n.js';

const KEY = 'cookieConsent'; // 'granted' | 'denied' | (yok)
const GA_ID = 'G-3C1DF6XY4D';
const ADSENSE_CLIENT = 'ca-pub-7507702503844486';

let injected = false;
let bannerEl = null;
let hideTimer = null;

// =========================================================================
// MARK: - DURUM
// =========================================================================

export function getConsent() {
  const v = localStorage.getItem(KEY);
  return v === 'granted' || v === 'denied' ? v : null;
}

function setConsent(value) {
  localStorage.setItem(KEY, value);
}

// =========================================================================
// MARK: - ÜÇÜNCÜ TARAF SCRIPTLERİ
// =========================================================================

function loadGoogleAnalytics() {
  const s = document.createElement('script');
  s.async = true;
  s.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  document.head.appendChild(s);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
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

/** Yalnızca onay verildiğinde ve bir kez çağrılır. */
function injectTrackers() {
  if (injected) return;
  injected = true;
  loadGoogleAnalytics();
  loadAdSense();
}

// =========================================================================
// MARK: - BANDROL
// =========================================================================

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function renderBanner() {
  if (!bannerEl) return;
  bannerEl.innerHTML = `
    <div class="consent-text">
      <div class="consent-title">${esc(L('consent_title'))}</div>
      <div class="consent-msg">${esc(L('consent_msg'))}</div>
    </div>
    <div class="consent-actions">
      <button class="consent-btn" data-consent="denied">${esc(L('consent_reject'))}</button>
      <button class="consent-btn primary" data-consent="granted">${esc(L('consent_accept'))}</button>
    </div>`;
}

export function showBanner() {
  if (!bannerEl) {
    bannerEl = document.createElement('div');
    bannerEl.className = 'consent-banner';
    bannerEl.setAttribute('role', 'dialog');
    bannerEl.setAttribute('aria-live', 'polite');

    bannerEl.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-consent]');
      if (!btn) return;
      const choice = btn.dataset.consent;
      setConsent(choice);
      hideBanner();
      if (choice === 'granted') injectTrackers();
    });

    document.body.appendChild(bannerEl);

    // Dil değişince bandroldeki metinler de güncellensin
    loc.addEventListener('change', renderBanner);
  }

  // Gizleme zamanlayıcısı beklemedeyse iptal et; yoksa yeni açılan
  // bandrolü hemen tekrar gizler.
  if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }

  renderBanner();
  bannerEl.hidden = false;

  // Girişte aşağıdan yukarı kaysın.
  // requestAnimationFrame arka plandaki sekmelerde tetiklenmediği için
  // geçişi zorlanmış bir reflow ile başlatıyoruz.
  void bannerEl.offsetWidth;
  bannerEl.classList.add('visible');
}

function hideBanner() {
  if (!bannerEl) return;
  bannerEl.classList.remove('visible');
  hideTimer = setTimeout(() => {
    if (bannerEl) bannerEl.hidden = true;
    hideTimer = null;
  }, 200);
}

// =========================================================================
// MARK: - GİRİŞ NOKTASI
// =========================================================================

/** Uygulama açılışında çağrılır. */
export function initConsent() {
  const choice = getConsent();
  if (choice === 'granted') {
    injectTrackers();
  } else if (choice === null) {
    showBanner();
  }
  // 'denied' -> hiçbir şey yüklenmez
}

/**
 * Kullanıcının kararını geri alması için (GDPR: onayı geri çekmek,
 * vermek kadar kolay olmalıdır). "Hakkında" penceresinden çağrılır.
 */
export function reopenConsent() {
  localStorage.removeItem(KEY);
  showBanner();
}
