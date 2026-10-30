/* GiftFinder front-end: five languages, facet chips, budget, infinite "more". */
const I18N = {
  en: { hero: "Find a gift they will actually love", sub: "Pick who it is for and the occasion. Our text-mining engine reads thousands of product descriptions from local shops and ranks the best matches.", go: "Find gifts", ph: "e.g. my dad who loves fishing", budget: "Budget", reset: "Reset", results: "Suggestions", more: "Show more", view: "View on", empty: "No matches in this budget. Try widening it or removing a filter.", found: "{n} gift ideas", disclosure: "Links on this site are affiliate links: if you buy something we may earn a small commission at no extra cost to you. Prices and availability are those of the shop at the time of your visit." },
  de: { hero: "Finde ein Geschenk, das wirklich ankommt", sub: "Wähle, für wen es ist und zu welchem Anlass. Unsere Text-Mining-Engine liest Tausende Produktbeschreibungen deutscher Shops und sortiert die besten Treffer.", go: "Geschenke finden", ph: "z. B. mein Papa, der gern angelt", budget: "Budget", reset: "Zurücksetzen", results: "Vorschläge", more: "Mehr anzeigen", view: "Ansehen bei", empty: "Keine Treffer in diesem Budget. Erweitere es oder entferne einen Filter.", found: "{n} Geschenkideen", disclosure: "Links auf dieser Seite sind Affiliate-Links: Wenn du etwas kaufst, erhalten wir eine kleine Provision, ohne Mehrkosten für dich. Preise und Verfügbarkeit entsprechen dem Shop zum Zeitpunkt deines Besuchs." },
  tr: { hero: "Gerçekten sevecekleri hediyeyi bul", sub: "Kimin için olduğunu ve özel günü seç. Text-mining motorumuz Türkiye'deki mağazaların binlerce ürün açıklamasını okuyup en uygun hediyeleri sıralar.", go: "Hediye bul", ph: "örn. balık tutmayı seven babam", budget: "Bütçe", reset: "Sıfırla", results: "Öneriler", more: "Daha fazla göster", view: "Mağazada gör:", empty: "Bu bütçede sonuç yok. Bütçeyi genişlet veya bir filtreyi kaldır.", found: "{n} hediye fikri", disclosure: "Bu sitedeki bağlantılar affiliate (ortaklık) bağlantılarıdır: bir ürün satın alırsanız size ek maliyet olmadan küçük bir komisyon kazanabiliriz. Fiyat ve stok bilgisi ziyaret anındaki mağaza bilgisidir." },
  nl: { hero: "Vind een cadeau waar ze echt blij van worden", sub: "Kies voor wie het is en de gelegenheid. Onze text-mining engine leest duizenden productbeschrijvingen van Nederlandse winkels en zet de beste matches bovenaan.", go: "Cadeaus zoeken", ph: "bijv. mijn vader die graag vist", budget: "Budget", reset: "Wissen", results: "Suggesties", more: "Meer tonen", view: "Bekijk bij", empty: "Geen resultaten binnen dit budget. Verruim het of haal een filter weg.", found: "{n} cadeau-ideeën", disclosure: "Links op deze site zijn affiliate links: koop je iets, dan ontvangen wij mogelijk een kleine commissie zonder extra kosten voor jou. Prijzen en voorraad zijn die van de winkel op het moment van je bezoek." },
  fr: { hero: "Trouvez un cadeau qui fera vraiment plaisir", sub: "Choisissez pour qui et pour quelle occasion. Notre moteur de text mining lit des milliers de descriptions de produits de boutiques françaises et classe les meilleures idées.", go: "Trouver des cadeaux", ph: "ex. mon père qui adore la pêche", budget: "Budget", reset: "Réinitialiser", results: "Suggestions", more: "Voir plus", view: "Voir sur", empty: "Aucun résultat dans ce budget. Élargissez-le ou retirez un filtre.", found: "{n} idées cadeaux", disclosure: "Les liens de ce site sont des liens affiliés : si vous achetez, nous pouvons toucher une petite commission sans surcoût pour vous. Prix et disponibilité sont ceux de la boutique au moment de votre visite." },
};
const MULTI = { gender: false, age: false, occasion: false, personality: true };
const MAX_PERSONALITY = 3;

const state = { country: null, lang: "en", sel: { gender: null, age: [], occasion: [], personality: [] }, offset: 0, total: 0, q: "" };
let COUNTRIES = {};
const $ = (id) => document.getElementById(id);

function detectCountry() {
  const saved = localStorage.getItem("gf_country");
  if (saved && COUNTRIES[saved]) return saved;
  const nav = (navigator.language || "en").toLowerCase();
  if (nav.startsWith("de")) return "DE";
  if (nav.startsWith("tr")) return "TR";
  if (nav.startsWith("nl")) return "NL";
  if (nav.startsWith("fr")) return "FR";
  return "US";
}

function t(key, vars = {}) {
  let s = (I18N[state.lang] || I18N.en)[key] || I18N.en[key] || key;
  Object.entries(vars).forEach(([k, v]) => { s = s.replace(`{${k}}`, v); });
  return s;
}

function applyI18n() {
  document.documentElement.lang = state.lang;
  $("t-hero").textContent = t("hero"); $("t-sub").textContent = t("sub"); $("t-go").textContent = t("go");
  $("q").placeholder = t("ph"); $("t-budget").textContent = t("budget"); $("t-reset").textContent = t("reset");
  $("t-results").textContent = t("results"); $("more").textContent = t("more"); $("t-disclosure").textContent = t("disclosure");
  $("cur").textContent = COUNTRIES[state.country].currency;
}

function renderCountries() {
  const nav = $("countries"); nav.innerHTML = "";
  Object.entries(COUNTRIES).forEach(([cc, c]) => {
    const b = document.createElement("button");
    b.textContent = `${c.flag} ${c.name}`; b.className = cc === state.country ? "on" : "";
    b.onclick = () => setCountry(cc);
    nav.appendChild(b);
  });
}

async function setCountry(cc) {
  state.country = cc; state.lang = COUNTRIES[cc].lang; localStorage.setItem("gf_country", cc);
  renderCountries(); applyI18n();
  const opts = await (await fetch(`/api/options?lang=${state.lang}`)).json();
  renderFacets(opts);
  search(true);
}

function renderFacets(opts) {
  const root = $("facets"); root.innerHTML = "";
  Object.entries(opts.facets).forEach(([facet, labels]) => {
    const box = document.createElement("div"); box.className = "facet";
    const h = document.createElement("h3"); h.textContent = opts.titles[facet]; box.appendChild(h);
    const chips = document.createElement("div"); chips.className = "chips";
    labels.forEach((l) => {
      const c = document.createElement("button"); c.type = "button"; c.className = "chip"; c.dataset.facet = facet; c.dataset.id = l.id;
      c.textContent = l.label; c.onclick = () => toggle(facet, l.id);
      chips.appendChild(c);
    });
    box.appendChild(chips); root.appendChild(box);
  });
  syncChips();
}

function toggle(facet, id) {
  if (!MULTI[facet]) {
    if (facet === "gender") state.sel.gender = state.sel.gender === id ? null : id;
    else state.sel[facet] = state.sel[facet][0] === id ? [] : [id];
  } else {
    const arr = state.sel[facet];
    const i = arr.indexOf(id);
    if (i >= 0) arr.splice(i, 1); else if (arr.length < MAX_PERSONALITY) arr.push(id);
  }
  syncChips(); search(true);
}

function syncChips() {
  document.querySelectorAll(".chip").forEach((c) => {
    const f = c.dataset.facet, id = c.dataset.id;
    const on = f === "gender" ? state.sel.gender === id : state.sel[f].includes(id);
    c.classList.toggle("on", on);
  });
}

function params() {
  const p = new URLSearchParams({ country: state.country, q: state.q, limit: 24, offset: state.offset });
  if (state.sel.gender) p.set("gender", state.sel.gender);
  ["age", "occasion", "personality"].forEach((f) => state.sel[f].forEach((v) => p.append(f, v)));
  if ($("pmin").value) p.set("price_min", $("pmin").value);
  if ($("pmax").value) p.set("price_max", $("pmax").value);
  return p;
}

async function search(reset) {
  if (reset) { state.offset = 0; $("results").innerHTML = ""; }
  const data = await (await fetch(`/api/search?${params()}`)).json();
  state.total = data.total;
  if (data.results.length === 0 && state.offset === 0) {
    $("results").innerHTML = `<div class="empty">${t("empty")}</div>`;
  }
  data.results.forEach((r) => $("results").appendChild(card(r)));
  state.offset += data.results.length;
  $("count").textContent = t("found", { n: data.total });
  $("more").hidden = state.offset >= data.total;
  history.replaceState(null, "", `?${params()}`);
}

function card(r) {
  const el = document.createElement("article"); el.className = "card";
  const thumb = r.image ? `<img src="${r.image}" alt="" loading="lazy">` : r.emoji;
  el.innerHTML = `
    <div class="thumb">${thumb}</div>
    <div class="body">
      <h4>${esc(r.title)}</h4>
      <div class="desc">${esc(r.description)}</div>
      <div class="why">${r.why.map((w) => `<span>${esc(w)}</span>`).join("")}</div>
      <div class="foot"><span class="price">${esc(r.price_text)}</span><span class="merchant">${esc(r.merchant)}</span></div>
      <a class="buy" href="${r.link}" target="_blank" rel="nofollow sponsored noopener">${t("view")} ${esc(r.merchant)} →</a>
    </div>`;
  return el;
}

function esc(s) { return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

function restoreFromUrl() {
  const u = new URLSearchParams(location.search);
  if (u.get("country") && COUNTRIES[u.get("country")]) { localStorage.setItem("gf_country", u.get("country")); }
  state.q = u.get("q") || ""; $("q").value = state.q;
  state.sel.gender = u.get("gender") || null;
  ["age", "occasion", "personality"].forEach((f) => { state.sel[f] = u.getAll(f); });
  if (u.get("price_min")) $("pmin").value = u.get("price_min");
  if (u.get("price_max")) $("pmax").value = u.get("price_max");
}

async function init() {
  COUNTRIES = await (await fetch("/api/countries")).json();
  restoreFromUrl();
  await setCountry(detectCountry());
  $("form").onsubmit = (e) => { e.preventDefault(); state.q = $("q").value.trim(); search(true); };
  $("more").onclick = () => search(false);
  $("reset").onclick = () => { state.sel = { gender: null, age: [], occasion: [], personality: [] }; state.q = ""; $("q").value = ""; $("pmin").value = ""; $("pmax").value = ""; syncChips(); search(true); };
  ["pmin", "pmax"].forEach((id) => { $(id).onchange = () => search(true); });
  fetch("/api/stats").then((r) => r.json()).then((s) => {
    const m = s.model && s.model.holdout ? Object.entries(s.model.holdout).map(([k, v]) => `${k} F1 ${v.micro_f1}`).join(" · ") : "";
    $("stats").textContent = `${s.products} products · ${m}`;
  });
}
init();
