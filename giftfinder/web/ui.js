/* GiftFinder UI: the search bar of comboboxes is the search engine. Expects a provider on window.GF:
   GF.countries() -> {CC:{name,lang,currency,flag}}
   GF.options(lang) -> {facets:{facet:[{id,label}]}, titles:{facet:text}}
   GF.search(params) -> {total, results:[...]}  params: country, gender, age[], occasion[], personality[], price_min, price_max, sort, limit, offset
   GF.stats() -> {products, model}   GF.demo -> bool */
const I18N = {
  en: { hero: "What are you looking for a gift for?", sub: "Choose who it is for, the occasion and their personality. The text-mining engine reads product descriptions from local shops and ranks what fits.", any: "Any", budget: "Budget", go: "Find gifts", sort: "Sort", relevance: "Best match", price_asc: "Price: low to high", price_desc: "Price: high to low", title: "Gift ideas", found: "{n} products", view: "View", empty: "Nothing matches this search. Try another budget or fewer criteria.", more: "Show more products", match: "{n}% match", pick: "Pick up to 3", over: "{a} and up", upto: "up to {b}", disclosure: "Links on this site are affiliate links: if you buy something we may earn a small commission at no extra cost to you. Prices and availability are those of the shop at the time of your visit.", demo: "<b>Demo catalog.</b> Example listings until the shop feeds are connected; links open the shop's search page for the product." },
  de: { hero: "Für wen suchst du ein Geschenk?", sub: "Wähle, für wen es ist, den Anlass und die Persönlichkeit. Die Text-Mining-Engine liest Produktbeschreibungen deutscher Shops und sortiert, was passt.", any: "Egal", budget: "Budget", go: "Geschenke finden", sort: "Sortieren", relevance: "Beste Treffer", price_asc: "Preis: aufsteigend", price_desc: "Preis: absteigend", title: "Geschenkideen", found: "{n} Produkte", view: "Ansehen", empty: "Nichts passt zu dieser Suche. Probiere ein anderes Budget oder weniger Kriterien.", more: "Mehr Produkte anzeigen", match: "{n}% passend", pick: "Bis zu 3 wählen", over: "ab {a}", upto: "bis {b}", disclosure: "Links auf dieser Seite sind Affiliate-Links: Wenn du etwas kaufst, erhalten wir eine kleine Provision ohne Mehrkosten für dich. Preise und Verfügbarkeit entsprechen dem Shop zum Zeitpunkt deines Besuchs.", demo: "<b>Demo-Katalog.</b> Beispiel-Listings, bis die Shop-Feeds angebunden sind; Links öffnen die Suchseite des Shops." },
  tr: { hero: "Kime hediye arıyorsun?", sub: "Kimin için olduğunu, özel günü ve karakterini seç. Text-mining motoru Türkiye'deki mağazaların ürün açıklamalarını okuyup uygun olanları sıralar.", any: "Fark etmez", budget: "Bütçe", go: "Hediye bul", sort: "Sırala", relevance: "En uygun", price_asc: "Fiyat: artan", price_desc: "Fiyat: azalan", title: "Hediye önerileri", found: "{n} ürün", view: "İncele", empty: "Bu aramaya uyan ürün yok. Başka bir bütçe dene veya kriter azalt.", more: "Daha fazla ürün göster", match: "%{n} uyum", pick: "En fazla 3 seç", over: "{a} ve üzeri", upto: "{b}'ye kadar", disclosure: "Bu sitedeki bağlantılar affiliate (ortaklık) bağlantılarıdır: bir ürün satın alırsanız size ek maliyet olmadan küçük bir komisyon kazanabiliriz. Fiyat ve stok bilgisi ziyaret anındaki mağaza bilgisidir.", demo: "<b>Demo katalog.</b> Mağaza feed'leri bağlanana kadar örnek ürünler gösterilir; bağlantılar mağazanın ürün arama sayfasını açar." },
  nl: { hero: "Voor wie zoek je een cadeau?", sub: "Kies voor wie het is, de gelegenheid en de persoonlijkheid. De text-mining engine leest productbeschrijvingen van Nederlandse winkels en zet wat past bovenaan.", any: "Maakt niet uit", budget: "Budget", go: "Cadeaus zoeken", sort: "Sorteren", relevance: "Beste match", price_asc: "Prijs: laag naar hoog", price_desc: "Prijs: hoog naar laag", title: "Cadeau-ideeën", found: "{n} producten", view: "Bekijk", empty: "Niets past bij deze zoekopdracht. Probeer een ander budget of minder criteria.", more: "Meer producten tonen", match: "{n}% match", pick: "Kies er maximaal 3", over: "{a} en meer", upto: "tot {b}", disclosure: "Links op deze site zijn affiliate links: koop je iets, dan ontvangen wij mogelijk een kleine commissie zonder extra kosten voor jou. Prijzen en voorraad zijn die van de winkel op het moment van je bezoek.", demo: "<b>Demo-catalogus.</b> Voorbeeldproducten totdat de winkelfeeds zijn gekoppeld; links openen de zoekpagina van de winkel." },
  fr: { hero: "Pour qui cherchez-vous un cadeau ?", sub: "Choisissez pour qui, l'occasion et la personnalité. Le moteur de text mining lit les descriptions de produits de boutiques françaises et classe ce qui convient.", any: "Peu importe", budget: "Budget", go: "Trouver des cadeaux", sort: "Trier", relevance: "Pertinence", price_asc: "Prix croissant", price_desc: "Prix décroissant", title: "Idées cadeaux", found: "{n} produits", view: "Voir", empty: "Rien ne correspond à cette recherche. Essayez un autre budget ou moins de critères.", more: "Voir plus de produits", match: "{n} % compatible", pick: "Choisissez-en 3 maximum", over: "{a} et plus", upto: "jusqu'à {b}", disclosure: "Les liens de ce site sont des liens affiliés : si vous achetez, nous pouvons toucher une petite commission sans surcoût pour vous. Prix et disponibilité sont ceux de la boutique au moment de votre visite.", demo: "<b>Catalogue de démonstration.</b> Fiches exemples en attendant les flux des boutiques ; les liens ouvrent la page de recherche de la boutique." },
};
const BUDGETS = { USD: [25, 50, 100, 200], EUR: [25, 50, 100, 200], TRY: [500, 1000, 2500, 5000] };
const EXAMPLES = [
  { gender: "female", occasion: "mothers_day", personality: ["wellness"] },
  { gender: "male", occasion: "fathers_day", personality: ["outdoor", "foodie"] },
  { age: "teen", occasion: "birthday", personality: ["gamer"] },
  { occasion: "new_baby" },
  { age: "senior", occasion: "retirement", personality: ["gardener"] },
  { occasion: "valentines", personality: ["homebody"] },
];
const PAGE = 36;
const state = { country: null, lang: "en", sel: { gender: "", age: "", occasion: "", personality: [], budget: "" }, sort: "relevance", offset: 0, total: 0, labels: {}, titles: {}, searched: false };
let COUNTRIES = {};
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function t(k, vars = {}) { let s = (I18N[state.lang] || I18N.en)[k] || I18N.en[k] || k; Object.entries(vars).forEach(([a, b]) => { s = s.replace(`{${a}}`, b); }); return s; }
function money(n) { const c = COUNTRIES[state.country]; if (c.currency === "TRY") return `${n.toLocaleString("tr-TR")} ₺`; if (c.currency === "EUR") return `${n} €`; return `$${n}`; }
function budgetRanges() { const b = BUDGETS[COUNTRIES[state.country].currency]; const r = [{ id: `0-${b[0]}`, label: t("upto", { b: money(b[0]) }) }]; for (let i = 0; i < b.length - 1; i++) r.push({ id: `${b[i]}-${b[i + 1]}`, label: `${money(b[i])} – ${money(b[i + 1])}` }); r.push({ id: `${b[b.length - 1]}-`, label: t("over", { a: money(b[b.length - 1]) }) }); return r; }

function fillSelect(id, options, value) { const s = $(id); s.innerHTML = ""; const any = document.createElement("option"); any.value = ""; any.textContent = t("any"); s.appendChild(any); options.forEach((o) => { const el = document.createElement("option"); el.value = o.id; el.textContent = o.label; s.appendChild(el); }); s.value = value || ""; s.parentElement.classList.toggle("set", !!s.value); }
function applyI18n(opts) {
  document.documentElement.lang = state.lang;
  $("t-hero").textContent = t("hero"); $("t-sub").textContent = t("sub"); $("go").textContent = t("go"); $("t-sort").textContent = t("sort"); $("more").textContent = t("more");
  $("t-disclosure").textContent = t("disclosure"); $("demo").innerHTML = t("demo"); $("demo").hidden = !GF.demo;
  ["gender", "age", "occasion", "personality"].forEach((f) => { $("l-" + f).textContent = opts.titles[f]; }); $("l-budget").textContent = t("budget");
  fillSelect("f-gender", opts.facets.gender.filter((o) => o.id !== "unisex"), state.sel.gender);
  fillSelect("f-age", opts.facets.age, state.sel.age);
  fillSelect("f-occasion", opts.facets.occasion, state.sel.occasion);
  fillSelect("f-budget", budgetRanges(), state.sel.budget);
  const menu = $("f-personality-menu"); menu.innerHTML = `<div class="hint">${t("pick")}</div>`;
  opts.facets.personality.forEach((o) => { const l = document.createElement("label"); l.innerHTML = `<input type="checkbox" value="${o.id}"> ${esc(o.label)}`; const cb = l.firstChild; cb.checked = state.sel.personality.includes(o.id); cb.onchange = () => { if (cb.checked) { if (state.sel.personality.length >= 3) { cb.checked = false; return; } state.sel.personality.push(o.id); } else state.sel.personality = state.sel.personality.filter((x) => x !== o.id); syncPersonality(); }; menu.appendChild(l); });
  syncPersonality();
  const sel = $("sort"); sel.innerHTML = ""; ["relevance", "price_asc", "price_desc"].forEach((k) => { const o = document.createElement("option"); o.value = k; o.textContent = t(k); sel.appendChild(o); }); sel.value = state.sort;
  const ex = $("examples"); ex.innerHTML = ""; EXAMPLES.forEach((e) => { const b = document.createElement("button"); b.type = "button"; b.textContent = [e.gender, e.age, e.occasion, ...(e.personality || [])].filter(Boolean).map((l) => state.labels[l]).join(" · "); b.onclick = () => { state.sel = { gender: e.gender || "", age: e.age || "", occasion: e.occasion || "", personality: [...(e.personality || [])], budget: "" }; applyI18n(opts); search(true); }; ex.appendChild(b); });
}
function syncPersonality() { const b = $("f-personality-btn"); const names = state.sel.personality.map((l) => state.labels[l] || l); b.textContent = names.length ? names.join(", ") : t("any"); b.parentElement.classList.toggle("set", names.length > 0); }
function renderCountries() { const nav = $("countries"); nav.innerHTML = ""; Object.entries(COUNTRIES).forEach(([cc, c]) => { const b = document.createElement("button"); b.type = "button"; b.textContent = `${c.flag} ${c.name}`; b.className = cc === state.country ? "on" : ""; b.onclick = () => setCountry(cc); nav.appendChild(b); }); }
async function setCountry(cc) {
  state.country = cc; state.lang = COUNTRIES[cc].lang; state.sel.budget = ""; try { localStorage.setItem("gf_country", cc); } catch (e) {}
  renderCountries();
  const opts = await GF.options(state.lang); state.labels = {}; Object.values(opts.facets).flat().forEach((l) => { state.labels[l.id] = l.label; }); state.titles = opts.titles; state.opts = opts;
  applyI18n(opts);
  if (state.searched) search(true);
}
function readBar() { state.sel.gender = $("f-gender").value; state.sel.age = $("f-age").value; state.sel.occasion = $("f-occasion").value; state.sel.budget = $("f-budget").value; ["f-gender", "f-age", "f-occasion", "f-budget"].forEach((id) => $(id).parentElement.classList.toggle("set", !!$(id).value)); }
function params() {
  const p = { country: state.country, sort: state.sort, limit: PAGE, offset: state.offset, age: state.sel.age ? [state.sel.age] : [], occasion: state.sel.occasion ? [state.sel.occasion] : [], personality: state.sel.personality };
  if (state.sel.gender) p.gender = state.sel.gender;
  if (state.sel.budget) { const [a, b] = state.sel.budget.split("-"); if (a) p.price_min = parseFloat(a); if (b) p.price_max = parseFloat(b); }
  return p;
}
async function search(reset) {
  state.searched = true; document.body.classList.add("results-mode"); $("results-wrap").hidden = false;
  if (reset) { state.offset = 0; $("results").innerHTML = ""; }
  const data = await GF.search(params());
  state.total = data.total;
  if (!data.results.length && state.offset === 0) $("results").innerHTML = `<div class="empty">${t("empty")}</div>`;
  data.results.forEach((r) => $("results").appendChild(card(r)));
  state.offset += data.results.length;
  const names = [state.sel.gender, state.sel.age, state.sel.occasion, ...state.sel.personality].filter(Boolean).map((l) => state.labels[l] || l);
  $("title").textContent = names.length ? `${t("title")} · ${names.join(" · ")}` : t("title");
  $("count").textContent = t("found", { n: data.total });
  $("more").hidden = state.offset >= data.total;
  if (reset) $("results-wrap").scrollIntoView({ behavior: "smooth", block: "start" });
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
  $("bar").onsubmit = (e) => { e.preventDefault(); readBar(); closeMenu(); search(true); };
  ["f-gender", "f-age", "f-occasion", "f-budget"].forEach((id) => { $(id).onchange = () => { readBar(); if (state.searched) search(true); }; });
  $("f-personality-menu").addEventListener("change", () => { if (state.searched) search(true); });
  const btn = $("f-personality-btn"), menu = $("f-personality-menu");
  const closeMenu = () => { menu.hidden = true; btn.setAttribute("aria-expanded", "false"); };
  btn.onclick = (e) => { e.stopPropagation(); menu.hidden = !menu.hidden; btn.setAttribute("aria-expanded", String(!menu.hidden)); };
  menu.onclick = (e) => e.stopPropagation();
  document.addEventListener("click", closeMenu); document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeMenu(); });
  $("more").onclick = () => search(false);
  $("sort").onchange = (e) => { state.sort = e.target.value; search(true); };
  $("home").onclick = (e) => { e.preventDefault(); state.searched = false; document.body.classList.remove("results-mode"); $("results-wrap").hidden = true; window.scrollTo({ top: 0 }); };
  await setCountry(detect());
  GF.stats().then((s) => { const h = s.model && s.model.holdout ? Object.entries(s.model.holdout).map(([k, v]) => `${k} F1 ${v.micro_f1}`).join(" · ") : ""; $("stats").textContent = `${s.products} products · text-mining model: ${h}`; });
}
init();
