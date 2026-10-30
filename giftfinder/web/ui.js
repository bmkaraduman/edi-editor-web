/* GiftFinder storefront UI. Expects a provider on window.GF:
   GF.countries() -> {CC:{name,lang,currency,flag}}
   GF.options(lang) -> {facets:{facet:[{id,label}]}, titles:{facet:text}}
   GF.search(params) -> {total, results:[...]}   params: country, gender, age[], occasion[], personality[], price_min, price_max, sort, limit, offset
   GF.stats() -> {products, model}  GF.demo -> bool */
const I18N = {
  en: { filters: "Filters", rail: "Find the right gift", budget: "Budget", sort: "Sort", relevance: "Best match", price_asc: "Price: low to high", price_desc: "Price: high to low", reset: "Clear all filters", title: "Gift ideas", for: "for", found: "{n} products", view: "View", empty: "Nothing matches this budget. Widen it or remove a filter.", more: "Show more products", match: "{n}% match", disclosure: "Links on this site are affiliate links: if you buy something we may earn a small commission at no extra cost to you. Prices and availability are those of the shop at the time of your visit.", demo: "<b>Demo catalog.</b> Example listings until the shop feeds are connected; links open the shop's search page for the product.", upto: "up to" },
  de: { filters: "Filter", rail: "Das passende Geschenk finden", budget: "Budget", sort: "Sortieren", relevance: "Beste Treffer", price_asc: "Preis: aufsteigend", price_desc: "Preis: absteigend", reset: "Alle Filter löschen", title: "Geschenkideen", for: "für", found: "{n} Produkte", view: "Ansehen", empty: "Nichts passt zu diesem Budget. Erweitere es oder entferne einen Filter.", more: "Mehr Produkte anzeigen", match: "{n}% passend", disclosure: "Links auf dieser Seite sind Affiliate-Links: Wenn du etwas kaufst, erhalten wir eine kleine Provision ohne Mehrkosten für dich. Preise und Verfügbarkeit entsprechen dem Shop zum Zeitpunkt deines Besuchs.", demo: "<b>Demo-Katalog.</b> Beispiel-Listings, bis die Shop-Feeds angebunden sind; Links öffnen die Suchseite des Shops.", upto: "bis" },
  tr: { filters: "Filtreler", rail: "Doğru hediyeyi bul", budget: "Bütçe", sort: "Sırala", relevance: "En uygun", price_asc: "Fiyat: artan", price_desc: "Fiyat: azalan", reset: "Filtreleri temizle", title: "Hediye önerileri", for: "için", found: "{n} ürün", view: "İncele", empty: "Bu bütçede ürün yok. Bütçeyi genişlet veya bir filtreyi kaldır.", more: "Daha fazla ürün göster", match: "%{n} uyum", disclosure: "Bu sitedeki bağlantılar affiliate (ortaklık) bağlantılarıdır: bir ürün satın alırsanız size ek maliyet olmadan küçük bir komisyon kazanabiliriz. Fiyat ve stok bilgisi ziyaret anındaki mağaza bilgisidir.", demo: "<b>Demo katalog.</b> Mağaza feed'leri bağlanana kadar örnek ürünler gösterilir; bağlantılar mağazanın ürün arama sayfasını açar.", upto: "en fazla" },
  nl: { filters: "Filters", rail: "Vind het juiste cadeau", budget: "Budget", sort: "Sorteren", relevance: "Beste match", price_asc: "Prijs: laag naar hoog", price_desc: "Prijs: hoog naar laag", reset: "Alle filters wissen", title: "Cadeau-ideeën", for: "voor", found: "{n} producten", view: "Bekijk", empty: "Niets past binnen dit budget. Verruim het of haal een filter weg.", more: "Meer producten tonen", match: "{n}% match", disclosure: "Links op deze site zijn affiliate links: koop je iets, dan ontvangen wij mogelijk een kleine commissie zonder extra kosten voor jou. Prijzen en voorraad zijn die van de winkel op het moment van je bezoek.", demo: "<b>Demo-catalogus.</b> Voorbeeldproducten totdat de winkelfeeds zijn gekoppeld; links openen de zoekpagina van de winkel.", upto: "tot" },
  fr: { filters: "Filtres", rail: "Trouver le bon cadeau", budget: "Budget", sort: "Trier", relevance: "Pertinence", price_asc: "Prix croissant", price_desc: "Prix décroissant", reset: "Effacer les filtres", title: "Idées cadeaux", for: "pour", found: "{n} produits", view: "Voir", empty: "Rien ne correspond à ce budget. Élargissez-le ou retirez un filtre.", more: "Voir plus de produits", match: "{n} % compatible", disclosure: "Les liens de ce site sont des liens affiliés : si vous achetez, nous pouvons toucher une petite commission sans surcoût pour vous. Prix et disponibilité sont ceux de la boutique au moment de votre visite.", demo: "<b>Catalogue de démonstration.</b> Fiches exemples en attendant les flux des boutiques ; les liens ouvrent la page de recherche de la boutique.", upto: "jusqu'à" },
};
const QUICK = { USD: [25, 50, 100, 200], EUR: [25, 50, 100, 200], TRY: [500, 1000, 2500, 5000] };
const MULTI = { gender: false, age: false, occasion: false, personality: true };
const PAGE = 36;
const state = { country: null, lang: "en", sel: { gender: null, age: [], occasion: [], personality: [] }, sort: "relevance", offset: 0, total: 0, labels: {} };
let COUNTRIES = {};
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function t(k, vars = {}) { let s = (I18N[state.lang] || I18N.en)[k] || I18N.en[k] || k; Object.entries(vars).forEach(([a, b]) => { s = s.replace(`{${a}}`, b); }); return s; }
function fmtMoney(n) { const c = COUNTRIES[state.country]; if (c.currency === "TRY") return `${n.toLocaleString("tr-TR")} ₺`; if (c.currency === "EUR") return `${n} €`; return `$${n}`; }

function applyI18n() {
  document.documentElement.lang = state.lang;
  ["filters", "rail", "budget", "sort", "reset", "more"].forEach((k) => { $(k === "reset" || k === "more" ? k : "t-" + k).textContent = t(k); });
  $("t-disclosure").textContent = t("disclosure"); $("cur").textContent = COUNTRIES[state.country].currency;
  $("demo").innerHTML = t("demo"); $("demo").hidden = !GF.demo;
  const sel = $("sort"); sel.innerHTML = ""; ["relevance", "price_asc", "price_desc"].forEach((k) => { const o = document.createElement("option"); o.value = k; o.textContent = t(k); sel.appendChild(o); }); sel.value = state.sort;
  const q = $("quick"); q.innerHTML = ""; QUICK[COUNTRIES[state.country].currency].forEach((v) => { const b = document.createElement("button"); b.type = "button"; b.textContent = `${t("upto")} ${fmtMoney(v)}`; b.dataset.v = v; b.onclick = () => { $("pmin").value = ""; $("pmax").value = $("pmax").value == v ? "" : v; syncQuick(); search(true); }; q.appendChild(b); }); syncQuick();
}
function syncQuick() { document.querySelectorAll("#quick button").forEach((b) => b.classList.toggle("on", $("pmax").value == b.dataset.v && !$("pmin").value)); }
function renderCountries() { const nav = $("countries"); nav.innerHTML = ""; Object.entries(COUNTRIES).forEach(([cc, c]) => { const b = document.createElement("button"); b.type = "button"; b.textContent = `${c.flag} ${c.name}`; b.className = cc === state.country ? "on" : ""; b.onclick = () => setCountry(cc); nav.appendChild(b); }); }
async function setCountry(cc) {
  state.country = cc; state.lang = COUNTRIES[cc].lang; try { localStorage.setItem("gf_country", cc); } catch (e) {}
  renderCountries(); applyI18n();
  const opts = await GF.options(state.lang); state.labels = {}; Object.values(opts.facets).flat().forEach((l) => { state.labels[l.id] = l.label; });
  renderFacets(opts); search(true);
}
function renderFacets(opts) {
  const root = $("facets"); root.innerHTML = "";
  Object.entries(opts.facets).forEach(([facet, labels]) => {
    const box = document.createElement("div"); box.className = "group"; box.style.marginBottom = "18px";
    const h = document.createElement("h3"); h.innerHTML = `<span>${esc(opts.titles[facet])}</span>` + (MULTI[facet] ? `<small>max 3</small>` : ""); box.appendChild(h);
    const chips = document.createElement("div"); chips.className = "chips";
    labels.forEach((l) => { const c = document.createElement("button"); c.type = "button"; c.className = "chip"; c.dataset.facet = facet; c.dataset.id = l.id; c.textContent = l.label; c.onclick = () => toggle(facet, l.id); chips.appendChild(c); });
    box.appendChild(chips); root.appendChild(box);
  });
  syncChips();
}
function toggle(facet, id) {
  if (facet === "gender") state.sel.gender = state.sel.gender === id ? null : id;
  else if (!MULTI[facet]) state.sel[facet] = state.sel[facet][0] === id ? [] : [id];
  else { const a = state.sel[facet]; const i = a.indexOf(id); if (i >= 0) a.splice(i, 1); else if (a.length < 3) a.push(id); }
  syncChips(); search(true);
}
function syncChips() { document.querySelectorAll(".chip").forEach((c) => { const f = c.dataset.facet, id = c.dataset.id; c.classList.toggle("on", f === "gender" ? state.sel.gender === id : state.sel[f].includes(id)); }); renderActive(); }
function selectedLabels() { return [...(state.sel.gender ? [["gender", state.sel.gender]] : []), ...["age", "occasion", "personality"].flatMap((f) => state.sel[f].map((v) => [f, v]))]; }
function renderActive() {
  const a = $("active"); a.innerHTML = "";
  selectedLabels().forEach(([f, v]) => { const b = document.createElement("button"); b.type = "button"; b.textContent = `${state.labels[v] || v} ✕`; b.onclick = () => toggle(f, v); a.appendChild(b); });
  const names = selectedLabels().map(([, v]) => state.labels[v] || v);
  $("title").textContent = names.length ? `${t("title")} · ${names.join(" · ")}` : t("title");
}
function params() {
  const p = { country: state.country, sort: state.sort, limit: PAGE, offset: state.offset, age: state.sel.age, occasion: state.sel.occasion, personality: state.sel.personality };
  if (state.sel.gender) p.gender = state.sel.gender;
  if ($("pmin").value) p.price_min = parseFloat($("pmin").value);
  if ($("pmax").value) p.price_max = parseFloat($("pmax").value);
  return p;
}
async function search(reset) {
  if (reset) { state.offset = 0; $("results").innerHTML = ""; }
  const data = await GF.search(params());
  state.total = data.total;
  if (!data.results.length && state.offset === 0) $("results").innerHTML = `<div class="empty">${t("empty")}</div>`;
  data.results.forEach((r) => $("results").appendChild(card(r)));
  state.offset += data.results.length;
  $("count").textContent = t("found", { n: data.total });
  $("more").hidden = state.offset >= data.total;
}
function card(r) {
  const el = document.createElement("article"); el.className = "card";
  const thumb = r.image ? `<img src="${esc(r.image)}" alt="" loading="lazy">` : `<span aria-hidden="true">${r.emoji}</span>`;
  const match = r.match != null ? `<span class="badge match">${t("match", { n: r.match })}</span>` : "";
  el.innerHTML = `<div class="thumb">${thumb}<span class="badge shop">${esc(r.merchant)}</span>${match}</div>
    <div class="body"><h4>${esc(r.title)}</h4><div class="desc">${esc(r.description)}</div>
    <div class="why">${r.why.map((w) => `<span>${esc(w)}</span>`).join("")}</div>
    <div class="foot"><span class="price">${esc(r.price_text)}</span><a class="buy" href="${esc(r.link)}" target="_blank" rel="nofollow sponsored noopener">${t("view")} →</a></div></div>`;
  return el;
}
function detect() { try { const s = localStorage.getItem("gf_country"); if (s && COUNTRIES[s]) return s; } catch (e) {} const n = (navigator.language || "en").toLowerCase(); return n.startsWith("de") ? "DE" : n.startsWith("tr") ? "TR" : n.startsWith("nl") ? "NL" : n.startsWith("fr") ? "FR" : "US"; }
async function init() {
  COUNTRIES = await GF.countries();
  $("more").onclick = () => search(false);
  $("sort").onchange = (e) => { state.sort = e.target.value; search(true); };
  $("reset").onclick = () => { state.sel = { gender: null, age: [], occasion: [], personality: [] }; $("pmin").value = ""; $("pmax").value = ""; syncQuick(); syncChips(); search(true); };
  ["pmin", "pmax"].forEach((id) => { $(id).onchange = () => { syncQuick(); search(true); }; });
  $("filters-toggle").onclick = () => { $("rail").hidden = !$("rail").hidden; };
  if (window.matchMedia("(max-width: 860px)").matches) $("rail").hidden = true;
  await setCountry(detect());
  GF.stats().then((s) => { const h = s.model && s.model.holdout ? Object.entries(s.model.holdout).map(([k, v]) => `${k} F1 ${v.micro_f1}`).join(" · ") : ""; $("stats").textContent = `${s.products} products · text-mining model: ${h}`; });
}
init();
