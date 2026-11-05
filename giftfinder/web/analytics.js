/* Google Analytics 4 with consent (DSGVO): nothing is loaded until the visitor accepts.
   The choice is kept in localStorage ("gd_consent": granted | denied); the footer link reopens the banner.
   window.GA_ID is set by the page. window.track(name, params) is a no-op until gtag exists. */
(function () {
  const ID = window.GA_ID;
  const KEY = "gd_consent";
  const read = () => { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
  const write = (v) => { try { localStorage.setItem(KEY, v); } catch (e) {} };
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  let loaded = false;
  function load() {
    if (loaded || !ID) return;
    loaded = true;
    gtag("consent", "default", { analytics_storage: "granted", ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" });
    const s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID; document.head.appendChild(s);
    gtag("js", new Date());
    gtag("config", ID, { send_page_view: false, anonymize_ip: true });
    window.gtag = gtag;
    (window.__pending || []).forEach(([n, p]) => gtag("event", n, p));
    window.__pending = null;
  }
  window.track = (name, params) => {
    if (window.gtag) window.gtag("event", name, params || {});
    else if (read() === "granted") { (window.__pending = window.__pending || []).push([name, params || {}]); load(); }
  };
  const T = {
    de: ["Wir verwenden Google Analytics, um zu verstehen, welche Geschenkideen ankommen. Daten werden anonymisiert; Werbe-Cookies gibt es nicht.", "Erlauben", "Ablehnen", "Cookie-Einstellungen"],
    en: ["We use Google Analytics to learn which gift ideas work. Data is anonymised; there are no advertising cookies.", "Allow", "Decline", "Cookie settings"],
    tr: ["Hangi hediye fikirlerinin ilgi gördüğünü anlamak için Google Analytics kullanıyoruz. Veriler anonimdir; reklam çerezi yoktur.", "İzin ver", "Reddet", "Çerez ayarları"],
    nl: ["We gebruiken Google Analytics om te zien welke cadeau-ideeën aanslaan. Gegevens zijn geanonimiseerd; er zijn geen advertentiecookies.", "Toestaan", "Weigeren", "Cookie-instellingen"],
    fr: ["Nous utilisons Google Analytics pour savoir quelles idées cadeaux plaisent. Les données sont anonymisées ; aucun cookie publicitaire.", "Autoriser", "Refuser", "Paramètres des cookies"],
  };
  Object.assign(T, window.CONSENT_EXTRA || {});      // languages added from app/i18n/*.json
  const lang = () => (document.documentElement.lang || "de").slice(0, 2);
  function banner() {
    const t = T[lang()] || T.de;
    let el = document.getElementById("consent");
    if (!el) { el = document.createElement("div"); el.id = "consent"; el.className = "consent"; document.body.appendChild(el); }
    el.innerHTML = `<p>${t[0]}</p><div class="consent-actions"><button type="button" class="consent-no">${t[2]}</button><button type="button" class="consent-yes">${t[1]}</button></div>`;
    el.querySelector(".consent-yes").onclick = () => { write("granted"); el.remove(); load(); window.track("consent_granted"); window.track("page_view", { page_path: location.pathname, page_title: document.title, page_location: location.href }); };
    el.querySelector(".consent-no").onclick = () => { write("denied"); el.remove(); };
  }
  function footerLink() {
    const f = document.querySelector("footer");
    if (!f || document.getElementById("consent-link")) return;
    const a = document.createElement("a"); a.href = "#"; a.id = "consent-link"; a.textContent = (T[lang()] || T.de)[3];
    a.onclick = (e) => { e.preventDefault(); banner(); };
    const p = document.createElement("p"); p.appendChild(a); f.appendChild(p);
  }
  window.openConsent = banner;      // the settings menu reopens the banner too
  function init() {
    footerLink();
    const c = read();
    if (c === "granted") load();
    else if (c !== "denied") banner();
    /* the UI sets <html lang> once the country is known (or switched): relabel banner and link */
    new MutationObserver(() => {
      if (document.getElementById("consent")) banner();
      const a = document.getElementById("consent-link"); if (a) a.textContent = (T[lang()] || T.de)[3];
    }).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
