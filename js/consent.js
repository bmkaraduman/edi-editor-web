// Rıza yönetimi — Google Consent Mode v2.
//
// Kendi çerez bandımız YOKTUR. AEA / Birleşik Krallık / İsviçre kullanıcılarına
// rıza ekranını Google'ın sertifikalı CMP'si (AdSense → Gizlilik ve mesajlaşma)
// gösterir. Buradaki görev, CMP karar verene kadar varsayılanı "reddedildi"
// tutmak; yani ölçüm ve reklam scriptleri yüklense bile çerez yazmazlar.
//
// Bu bölgelerin dışında (ör. Türkiye) varsayılan davranış korunur, aksi hâlde
// CMP hiç gösterilmediği için hiçbir veri toplanamazdı.

const GA_ID = 'G-3C1DF6XY4D';
const ADSENSE_CLIENT = 'ca-pub-7507702503844486';

/** AEA (AB 27 + İzlanda, Lihtenştayn, Norveç) + Birleşik Krallık + İsviçre */
const CONSENT_REQUIRED_REGIONS = [
  'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
  'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
  'SI', 'ES', 'SE', 'IS', 'LI', 'NO', 'GB', 'CH',
];

/**
 * Consent Mode varsayılanlarını tanımlar.
 * gtag.js'ten ÖNCE çalışmak zorundadır; sonrası geç kalmış sayılır.
 */
function setConsentDefaults() {
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };

  window.gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    // CMP'nin kararını bildirmesi için kısa bir pencere bırak
    wait_for_update: 500,
    region: CONSENT_REQUIRED_REGIONS,
  });

  // Rıza yokken reklam tıklama kimliklerini de kısıtla
  window.gtag('set', 'ads_data_redaction', true);
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

/** Gizlilik politikasının dile göre adresi (TR ayrı sayfa, diğerleri İngilizce) */
export function privacyURL() {
  return (localStorage.getItem('selectedLanguageCode') || 'en') === 'tr'
    ? 'gizlilik.html'
    : 'privacy.html';
}

/**
 * Google'ın CMP'si sayfada mı? Yalnızca rıza istenen bölgelerde yüklenir,
 * bu yüzden "Çerez Ayarları" düğmesi de yalnızca o zaman gösterilmelidir.
 */
export function consentUIAvailable() {
  return typeof window.googlefc?.showRevocationMessage === 'function';
}

/** Rıza ekranını yeniden açar (yalnızca CMP yüklüyse anlamlıdır). */
export function reopenConsent() {
  if (!consentUIAvailable()) return false;
  window.googlefc.showRevocationMessage();
  return true;
}

/**
 * Uygulama açılışında, mümkün olan en erken anda çağrılır.
 *
 * @param {{ads?: boolean}} opts
 *   ads=false → yalnızca ölçüm yüklenir, reklam yüklenmez.
 *   Editör sayfası bunu kullanır: gövdesi `overflow: hidden` ve `100vh`
 *   olduğu için Auto Ads'in yerleştirebileceği bir belge akışı yoktur;
 *   sabit yerleşimli araç arayüzüne reklam sokmak düzeni bozar.
 */
export function initConsent({ ads = true } = {}) {
  setConsentDefaults();
  loadGoogleAnalytics();
  if (ads) loadAdSense();
}
