/* giftdetect.com UI: the search bar of comboboxes is the search engine; /p/{id} is the product page. Expects a provider on window.GF:
   GF.countries() -> {CC:{name,lang,currency,flag}}
   GF.options(lang) -> {facets:{facet:[{id,label}]}, titles:{facet:text}}
   GF.search(params) -> {total, demo, results:[...]}  params: country, q, gender, age[], occasion[], personality[], price_min, price_max, sort, limit, offset
   GF.product(id) -> {...card fields, images[], brand, category, keywords[], details{}, labels{facet:[{id,label}]}, similar[]}
   GF.stats() -> {products, model} */
const I18N = {
  en: { hero: "What are you looking for a gift for?", sub: "Choose who it is for, the occasion and their personality. The text-mining engine reads product descriptions from local shops and ranks what fits.", any: "Any", budget: "Budget", go: "Find gifts", sort: "Sort", relevance: "Best match", price_asc: "Price: low to high", price_desc: "Price: high to low", title: "Gift ideas", found: "{n} products", view: "View", empty: "Nothing matches this search. Try another budget or fewer criteria.", more: "Show more products", match: "{n}% match", pick: "Pick up to 3", over: "{a} and up", upto: "up to {b}", disclosure: "Links on this site are affiliate links: if you buy something we may earn a small commission at no extra cost to you. Prices and availability are those of the shop at the time of your visit.", demo: "<b>Demo catalog.</b> Example listings until the shop feeds are connected; links open the shop's search page for the product.", back: "← Back to the gift search", shop: "Open at {shop} →", similar: "Similar gift ideas", fits: "A fit for", details: "Details", keywords: "Keywords", brand: "Brand", category: "Category", was: "was {p}", pictures: "{n} pictures", colour: "Colour", condition: "Condition", model: "Model", dimensions: "Dimensions", specifications: "Material / specs", delivery_cost: "Delivery", promotion: "Offer", notfound: "This product is no longer in the catalog.", gender: "For", age: "Age", occasion: "Occasion", personality: "Personality", loading: "Loading…", up_title: "Gifts for {occ}", up_days: "{occ} is in {n} days ({date})", up_today: "{occ} is today!", up_all: "All gifts for {occ} →", settings: "Settings", country: "Country", cookies: "Cookie settings" },
  de: { hero: "Für wen suchst du ein Geschenk?", sub: "Wähle, für wen es ist, den Anlass und die Persönlichkeit. Die Text-Mining-Engine liest Produktbeschreibungen deutscher Shops und sortiert, was passt.", any: "Egal", budget: "Budget", go: "Geschenke finden", sort: "Sortieren", relevance: "Beste Treffer", price_asc: "Preis: aufsteigend", price_desc: "Preis: absteigend", title: "Geschenkideen", found: "{n} Produkte", view: "Ansehen", empty: "Nichts passt zu dieser Suche. Probiere ein anderes Budget oder weniger Kriterien.", more: "Mehr Produkte anzeigen", match: "{n}% passend", pick: "Bis zu 3 wählen", over: "ab {a}", upto: "bis {b}", disclosure: "Links auf dieser Seite sind Affiliate-Links: Wenn du etwas kaufst, erhalten wir eine kleine Provision ohne Mehrkosten für dich. Preise und Verfügbarkeit entsprechen dem Shop zum Zeitpunkt deines Besuchs.", demo: "<b>Demo-Katalog.</b> Beispiel-Listings, bis die Shop-Feeds angebunden sind; Links öffnen die Suchseite des Shops.", back: "← Zurück zur Geschenksuche", shop: "Bei {shop} ansehen →", similar: "Ähnliche Geschenkideen", fits: "Passt für", details: "Details", keywords: "Stichwörter", brand: "Marke", category: "Kategorie", was: "statt {p}", pictures: "{n} Bilder", colour: "Farbe", condition: "Zustand", model: "Modell", dimensions: "Maße", specifications: "Material / Daten", delivery_cost: "Versand", promotion: "Aktion", notfound: "Dieses Produkt ist nicht mehr im Katalog.", gender: "Für", age: "Alter", occasion: "Anlass", personality: "Persönlichkeit", loading: "Lädt…", up_title: "Geschenke zu {occ}", up_days: "{occ} ist in {n} Tagen ({date})", up_today: "{occ} ist heute!", up_all: "Alle Geschenke zu {occ} →", settings: "Einstellungen", country: "Land", cookies: "Cookie-Einstellungen" },
  tr: { hero: "Kime hediye arıyorsun?", sub: "Kimin için olduğunu, özel günü ve karakterini seç. Text-mining motoru Türkiye'deki mağazaların ürün açıklamalarını okuyup uygun olanları sıralar.", any: "Fark etmez", budget: "Bütçe", go: "Hediye bul", sort: "Sırala", relevance: "En uygun", price_asc: "Fiyat: artan", price_desc: "Fiyat: azalan", title: "Hediye önerileri", found: "{n} ürün", view: "İncele", empty: "Bu aramaya uyan ürün yok. Başka bir bütçe dene veya kriter azalt.", more: "Daha fazla ürün göster", match: "%{n} uyum", pick: "En fazla 3 seç", over: "{a} ve üzeri", upto: "{b}'ye kadar", disclosure: "Bu sitedeki bağlantılar affiliate (ortaklık) bağlantılarıdır: bir ürün satın alırsanız size ek maliyet olmadan küçük bir komisyon kazanabiliriz. Fiyat ve stok bilgisi ziyaret anındaki mağaza bilgisidir.", demo: "<b>Demo katalog.</b> Mağaza feed'leri bağlanana kadar örnek ürünler gösterilir; bağlantılar mağazanın ürün arama sayfasını açar.", back: "← Hediye aramasına dön", shop: "{shop}'da gör →", similar: "Benzer hediye fikirleri", fits: "Kime uygun", details: "Detaylar", keywords: "Anahtar kelimeler", brand: "Marka", category: "Kategori", was: "eski fiyat {p}", pictures: "{n} görsel", colour: "Renk", condition: "Durum", model: "Model", dimensions: "Ölçüler", specifications: "Malzeme / özellikler", delivery_cost: "Kargo", promotion: "Kampanya", notfound: "Bu ürün artık katalogda değil.", gender: "Kime", age: "Yaş", occasion: "Özel gün", personality: "Karakter", loading: "Yükleniyor…", up_title: "{occ} hediyeleri", up_days: "{occ} {n} gün sonra ({date})", up_today: "{occ} bugün!", up_all: "Tüm {occ} hediyeleri →", settings: "Ayarlar", country: "Ülke", cookies: "Çerez ayarları" },
  nl: { hero: "Voor wie zoek je een cadeau?", sub: "Kies voor wie het is, de gelegenheid en de persoonlijkheid. De text-mining engine leest productbeschrijvingen van Nederlandse winkels en zet wat past bovenaan.", any: "Maakt niet uit", budget: "Budget", go: "Cadeaus zoeken", sort: "Sorteren", relevance: "Beste match", price_asc: "Prijs: laag naar hoog", price_desc: "Prijs: hoog naar laag", title: "Cadeau-ideeën", found: "{n} producten", view: "Bekijk", empty: "Niets past bij deze zoekopdracht. Probeer een ander budget of minder criteria.", more: "Meer producten tonen", match: "{n}% match", pick: "Kies er maximaal 3", over: "{a} en meer", upto: "tot {b}", disclosure: "Links op deze site zijn affiliate links: koop je iets, dan ontvangen wij mogelijk een kleine commissie zonder extra kosten voor jou. Prijzen en voorraad zijn die van de winkel op het moment van je bezoek.", demo: "<b>Demo-catalogus.</b> Voorbeeldproducten totdat de winkelfeeds zijn gekoppeld; links openen de zoekpagina van de winkel.", back: "← Terug naar de cadeauzoeker", shop: "Bekijk bij {shop} →", similar: "Vergelijkbare cadeau-ideeën", fits: "Past bij", details: "Details", keywords: "Trefwoorden", brand: "Merk", category: "Categorie", was: "was {p}", pictures: "{n} foto's", colour: "Kleur", condition: "Staat", model: "Model", dimensions: "Afmetingen", specifications: "Materiaal / specificaties", delivery_cost: "Verzending", promotion: "Actie", notfound: "Dit product staat niet meer in de catalogus.", gender: "Voor", age: "Leeftijd", occasion: "Gelegenheid", personality: "Persoonlijkheid", loading: "Laden…", up_title: "Cadeaus voor {occ}", up_days: "{occ} is over {n} dagen ({date})", up_today: "{occ} is vandaag!", up_all: "Alle cadeaus voor {occ} →", settings: "Instellingen", country: "Land", cookies: "Cookie-instellingen" },
  fr: { hero: "Pour qui cherchez-vous un cadeau ?", sub: "Choisissez pour qui, l'occasion et la personnalité. Le moteur de text mining lit les descriptions de produits de boutiques françaises et classe ce qui convient.", any: "Peu importe", budget: "Budget", go: "Trouver des cadeaux", sort: "Trier", relevance: "Pertinence", price_asc: "Prix croissant", price_desc: "Prix décroissant", title: "Idées cadeaux", found: "{n} produits", view: "Voir", empty: "Rien ne correspond à cette recherche. Essayez un autre budget ou moins de critères.", more: "Voir plus de produits", match: "{n} % compatible", pick: "Choisissez-en 3 maximum", over: "{a} et plus", upto: "jusqu'à {b}", disclosure: "Les liens de ce site sont des liens affiliés : si vous achetez, nous pouvons toucher une petite commission sans surcoût pour vous. Prix et disponibilité sont ceux de la boutique au moment de votre visite.", demo: "<b>Catalogue de démonstration.</b> Fiches exemples en attendant les flux des boutiques ; les liens ouvrent la page de recherche de la boutique.", back: "← Retour à la recherche de cadeaux", shop: "Voir chez {shop} →", similar: "Idées cadeaux similaires", fits: "Convient pour", details: "Détails", keywords: "Mots-clés", brand: "Marque", category: "Catégorie", was: "au lieu de {p}", pictures: "{n} photos", colour: "Couleur", condition: "État", model: "Modèle", dimensions: "Dimensions", specifications: "Matière / caractéristiques", delivery_cost: "Livraison", promotion: "Offre", notfound: "Ce produit n'est plus dans le catalogue.", gender: "Pour", age: "Âge", occasion: "Occasion", personality: "Personnalité", loading: "Chargement…", up_title: "Cadeaux pour {occ}", up_days: "{occ} : dans {n} jours ({date})", up_today: "{occ}, c'est aujourd'hui !", up_all: "Tous les cadeaux pour {occ} →", settings: "Paramètres", country: "Pays", cookies: "Paramètres des cookies" },
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
const DETAIL_KEYS = ["colour", "condition", "model", "dimensions", "specifications", "delivery_cost", "promotion"];
const track = (name, params) => { if (window.track) window.track(name, params || {}); };
const pageView = (path, title) => track("page_view", { page_path: path, page_title: title || document.title, page_location: location.origin + path, country: state.country });
const state = { country: null, lang: "en", sel: { gender: "", age: "", occasion: "", personality: [], budget: "" }, sort: "relevance", offset: 0, total: 0, labels: {}, titles: {}, searched: false, view: "home", product: null };
let COUNTRIES = {};
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function t(k, vars = {}) { let s = (I18N[state.lang] || I18N.en)[k] || I18N.en[k] || k; Object.entries(vars).forEach(([a, b]) => { s = s.replace(`{${a}}`, b); }); return s; }
function money(n) { const c = COUNTRIES[state.country]; if (c.currency === "TRY") return `${n.toLocaleString("tr-TR")} ₺`; if (c.currency === "EUR") return `${n} €`; return `$${n}`; }
function budgetRanges() { const b = BUDGETS[COUNTRIES[state.country].currency]; const r = [{ id: `0-${b[0]}`, label: t("upto", { b: money(b[0]) }) }]; for (let i = 0; i < b.length - 1; i++) r.push({ id: `${b[i]}-${b[i + 1]}`, label: `${money(b[i])} – ${money(b[i + 1])}` }); r.push({ id: `${b[b.length - 1]}-`, label: t("over", { a: money(b[b.length - 1]) }) }); return r; }

function fillSelect(id, options, value) { const s = $(id); s.innerHTML = ""; const any = document.createElement("option"); any.value = ""; any.textContent = t("any"); s.appendChild(any); options.forEach((o) => { const el = document.createElement("option"); el.value = o.id; el.textContent = o.label; s.appendChild(el); }); s.value = value || ""; s.parentElement.classList.toggle("set", !!s.value); }
function applyI18n(opts) {
  document.documentElement.lang = state.lang;
  $("t-hero").textContent = t("hero"); $("t-sub").textContent = t("sub"); $("go").textContent = t("go"); $("t-sort").textContent = t("sort"); $("more").textContent = t("more");
  $("t-disclosure").textContent = t("disclosure"); $("demo").innerHTML = t("demo"); $("back").textContent = t("back"); $("t-similar").textContent = t("similar");
  ["gender", "age", "occasion", "personality"].forEach((f) => { $("l-" + f).textContent = opts.titles[f]; }); $("l-budget").textContent = t("budget");
  fillSelect("f-gender", opts.facets.gender.filter((o) => o.id !== "unisex"), state.sel.gender);
  fillSelect("f-age", opts.facets.age, state.sel.age);
  fillSelect("f-occasion", opts.facets.occasion, state.sel.occasion);
  fillSelect("f-budget", budgetRanges(), state.sel.budget);
  const menu = $("f-personality-menu"); menu.innerHTML = `<div class="hint">${t("pick")}</div>`;
  opts.facets.personality.forEach((o) => { const l = document.createElement("label"); l.innerHTML = `<input type="checkbox" value="${o.id}"> ${esc(o.label)}`; const cb = l.firstChild; cb.checked = state.sel.personality.includes(o.id); cb.onchange = () => { if (cb.checked) { if (state.sel.personality.length >= 3) { cb.checked = false; return; } state.sel.personality.push(o.id); } else state.sel.personality = state.sel.personality.filter((x) => x !== o.id); syncPersonality(); }; menu.appendChild(l); });
  syncPersonality();
  const sel = $("sort"); sel.innerHTML = ""; ["relevance", "price_asc", "price_desc"].forEach((k) => { const o = document.createElement("option"); o.value = k; o.textContent = t(k); sel.appendChild(o); }); sel.value = state.sort;
  const ex = $("examples"); ex.innerHTML = ""; EXAMPLES.forEach((e) => { const b = document.createElement("button"); b.type = "button"; b.textContent = [e.gender, e.age, e.occasion, ...(e.personality || [])].filter(Boolean).map((l) => state.labels[l]).join(" · "); b.onclick = () => { state.sel = { gender: e.gender || "", age: e.age || "", occasion: e.occasion || "", personality: [...(e.personality || [])], budget: "" }; applyI18n(opts); showSearch(); search(true); }; ex.appendChild(b); });
}
function syncPersonality() { const b = $("f-personality-btn"); const names = state.sel.personality.map((l) => state.labels[l] || l); b.textContent = names.length ? names.join(", ") : t("any"); b.parentElement.classList.toggle("set", names.length > 0); }
/* Settings menu: the visitor's country is picked automatically (see detect); the menu lets them change it. */
const PICKED = "gd_country";          // set only when the visitor picks a country in the menu
function renderSettings() {
  const c = COUNTRIES[state.country];
  $("settings-flag").textContent = c.flag; $("settings-btn").title = `${t("settings")} · ${c.name}`; $("settings-btn").setAttribute("aria-label", t("settings"));
  $("settings-pop").innerHTML = `<div class="menu-header">${esc(t("country"))}</div>` +
    Object.entries(COUNTRIES).map(([cc, x]) => `<button type="button" class="menu-item" role="menuitemradio" aria-checked="${cc === state.country}" data-country="${cc}"><span class="menu-check">${cc === state.country ? "✓" : ""}</span><span>${x.flag} ${esc(x.name)}</span></button>`).join("") +
    (window.openConsent ? `<div class="menu-sep"></div><button type="button" class="menu-item" role="menuitem" data-cookies="1"><span class="menu-check"></span><span>${esc(t("cookies"))}</span></button>` : "");
}
function toggleSettings(open) { const pop = $("settings-pop"); open = open == null ? pop.hidden : open; pop.hidden = !open; $("settings").classList.toggle("open", open); $("settings-btn").setAttribute("aria-expanded", String(open)); }
async function setCountry(cc, opts = {}) {
  state.country = cc; state.lang = COUNTRIES[cc].lang; state.sel.budget = "";
  renderSettings();
  const o = await GF.options(state.lang); state.labels = {}; Object.values(o.facets).flat().forEach((l) => { state.labels[l.id] = l.label; }); state.titles = o.titles; state.opts = o;
  applyI18n(o);
  loadUpcoming();
  if (state.view === "product" && !opts.keepProduct) { showSearch(); }
  if (state.searched && state.view !== "product") search(true);
}
function readBar() { state.sel.gender = $("f-gender").value; state.sel.age = $("f-age").value; state.sel.occasion = $("f-occasion").value; state.sel.budget = $("f-budget").value; ["f-gender", "f-age", "f-occasion", "f-budget"].forEach((id) => $(id).parentElement.classList.toggle("set", !!$(id).value)); }
function params() {
  const p = { country: state.country, sort: state.sort, limit: PAGE, offset: state.offset, age: state.sel.age ? [state.sel.age] : [], occasion: state.sel.occasion ? [state.sel.occasion] : [], personality: state.sel.personality };
  if (state.sel.gender) p.gender = state.sel.gender;
  if (state.sel.budget) { const [a, b] = state.sel.budget.split("-"); if (a) p.price_min = parseFloat(a); if (b) p.price_max = parseFloat(b); }
  return p;
}
async function loadUpcoming() {
  if (!GF.upcoming) return;
  const cc = state.country; const wrap = $("upcoming-wrap"); wrap.hidden = true;
  let u; try { u = await GF.upcoming(cc); } catch (e) { return; }
  if (!u || cc !== state.country || !u.results.length) return;
  const date = new Date(u.date + "T12:00:00").toLocaleDateString(state.lang, { day: "numeric", month: "long" });
  $("up-title").textContent = `🎁 ${t("up_title", { occ: u.label })}`;
  $("up-sub").textContent = u.days === 0 ? t("up_today", { occ: u.label }) : t("up_days", { occ: u.label, n: u.days, date });
  $("up-all").textContent = t("up_all", { occ: u.label });
  $("up-all").onclick = () => { track("upcoming_all", { occasion: u.occasion }); state.sel = { gender: "", age: "", occasion: u.occasion, personality: [], budget: "" }; applyI18n(state.opts); search(true); };
  const grid = $("upcoming"); grid.innerHTML = ""; u.results.forEach((r) => grid.appendChild(card(r)));
  wrap.hidden = false;
}
/* ---------------------------------------------------------------- views */
function showSearch() {
  state.view = state.searched ? "results" : "home";
  $("product-wrap").hidden = true; $("results-wrap").hidden = !state.searched; $("bar-wrap").hidden = false; $("hero").hidden = false;
  document.body.classList.toggle("results-mode", state.searched); document.body.classList.remove("product-mode");
}
async function search(reset) {
  state.searched = true; showSearch();
  if (reset) { state.offset = 0; $("results").innerHTML = ""; }
  const data = await GF.search(params());
  state.total = data.total;
  if (reset) {
    const sel = state.sel;
    track("search", { search_term: [sel.gender, sel.age, sel.occasion, ...sel.personality, sel.budget].filter(Boolean).join(" "), gender: sel.gender || "any", age: sel.age || "any", occasion: sel.occasion || "any", personality: sel.personality.join(",") || "any", budget: sel.budget || "any", country: state.country, results: data.total });
    pageView("/search", t("title"));
  }
  $("demo").hidden = !data.demo;
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
  const pics = r.gallery > 1 ? `<span class="badge pics">📷 ${r.gallery}</span>` : "";
  const was = r.rrp_text ? `<s class="was">${esc(r.rrp_text)}</s>` : "";
  el.innerHTML = `<a class="thumb" href="${esc(r.detail)}" data-id="${esc(r.id)}">${thumb}<span class="badge shop">${esc(r.merchant)}</span>${match}${pics}</a>
    <div class="body"><h4><a href="${esc(r.detail)}" data-id="${esc(r.id)}">${esc(r.title)}</a></h4><div class="desc">${esc(r.description)}</div>
    <div class="why">${r.why.map((w) => `<span>${esc(w)}</span>`).join("")}</div>
    <div class="foot"><span class="price">${esc(r.price_text)} ${was}</span><a class="buy" href="${esc(r.link)}" target="_blank" rel="nofollow sponsored noopener">${t("view")} →</a></div></div>`;
  el.querySelectorAll("a[data-id]").forEach((a) => { a.onclick = (e) => { e.preventDefault(); openProduct(a.dataset.id, true); }; });
  el.querySelector(".buy").onclick = () => track("shop_click", { item_id: r.id, item_name: r.title, merchant: r.merchant, price: r.price, currency: r.currency, from: state.view });
  const img = el.querySelector(".thumb img");
  if (img) img.onerror = () => { el.remove(); reportBroken(r.id); };
  return el;
}
const reported = new Set();
function reportBroken(id) { if (reported.has(id) || !GF.broken) return; reported.add(id); GF.broken(id).catch(() => {}); }
async function openProduct(id, push) {
  if (push) history.pushState({ product: id }, "", `/p/${id}`);
  state.view = "product"; state.product = id;
  document.body.classList.add("product-mode"); document.body.classList.remove("results-mode");
  $("hero").hidden = true; $("bar-wrap").hidden = true; $("results-wrap").hidden = true; $("product-wrap").hidden = false;
  $("product").innerHTML = `<div class="loading">${t("loading")}</div>`; $("similar").innerHTML = ""; $("t-similar").hidden = true;
  window.scrollTo({ top: 0 });
  const d = await GF.product(id);
  if (!d) { $("product").innerHTML = `<div class="empty">${t("notfound")}</div>`; return; }
  renderProduct(d);
  track("view_item", { item_id: d.id, item_name: d.title, merchant: d.merchant, price: d.price, currency: d.currency, country: state.country });
  pageView(`/p/${id}`, d.title);
}
function renderProduct(d) {
  const imgs = d.images && d.images.length ? d.images : [];
  const gallery = imgs.length
    ? `<div class="gallery"><div class="main"><img id="g-main" src="${esc(imgs[0])}" alt="${esc(d.title)}"></div>${imgs.length > 1 ? `<div class="thumbs">${imgs.map((u, i) => `<button type="button" class="${i === 0 ? "on" : ""}" data-src="${esc(u)}"><img src="${esc(u)}" alt="" loading="lazy"></button>`).join("")}</div>` : ""}</div>`
    : `<div class="gallery"><div class="main emoji">${d.emoji || "🎁"}</div></div>`;
  const labels = Object.entries(d.labels || {}).filter(([, ls]) => ls.length).map(([facet, ls]) => `<div class="facet-row"><span class="facet-name">${esc(t(facet))}</span>${ls.map((l) => `<span class="chip ${facet}">${esc(l.label)}</span>`).join("")}</div>`).join("");
  const details = DETAIL_KEYS.filter((k) => d.details && d.details[k]).map((k) => `<div class="row"><dt>${esc(t(k))}</dt><dd>${esc(d.details[k])}</dd></div>`).join("");
  const meta = [d.brand ? `<div class="row"><dt>${esc(t("brand"))}</dt><dd>${esc(d.brand)}</dd></div>` : "", d.category ? `<div class="row"><dt>${esc(t("category"))}</dt><dd>${esc(d.category)}</dd></div>` : "", d.product_type && d.product_type !== d.category ? `<div class="row"><dt>${esc(t("category"))}</dt><dd>${esc(d.product_type)}</dd></div>` : ""].join("");
  const kws = (d.keywords || []).length ? `<div class="keywords"><span class="facet-name">${esc(t("keywords"))}</span>${d.keywords.map((k) => `<span class="chip kw">${esc(k)}</span>`).join("")}</div>` : "";
  const was = d.rrp_text ? `<s class="was">${esc(t("was", { p: d.rrp_text }))}</s>` : "";
  const longDesc = d.details && d.details.short_description && d.details.short_description !== d.description ? d.description : d.description;
  $("product").innerHTML = `${gallery}
    <div class="info">
      <div class="shopline"><span class="badge shop">${esc(d.merchant)}</span>${d.brand ? `<span class="brand">${esc(d.brand)}</span>` : ""}</div>
      <h1>${esc(d.title)}</h1>
      <div class="priceline"><span class="price">${esc(d.price_text)}</span>${was}</div>
      <a class="cta" href="${esc(d.link)}" target="_blank" rel="nofollow sponsored noopener">${esc(t("shop", { shop: d.merchant }))}</a>
      ${labels ? `<div class="fits"><h3>${esc(t("fits"))}</h3>${labels}</div>` : ""}
      <p class="longdesc">${esc(longDesc)}</p>
      ${kws}
      ${meta || details ? `<dl class="details"><h3>${esc(t("details"))}</h3>${meta}${details}</dl>` : ""}
    </div>`;
  $("product").querySelector(".cta").onclick = () => track("shop_click", { item_id: d.id, item_name: d.title, merchant: d.merchant, price: d.price, currency: d.currency, from: "product" });
  $("product").querySelectorAll(".thumbs button").forEach((b) => { b.onclick = () => { $("g-main").src = b.dataset.src; $("product").querySelectorAll(".thumbs button").forEach((x) => x.classList.toggle("on", x === b)); }; b.querySelector("img").onerror = () => b.remove(); });
  const main = $("g-main");
  if (main) main.onerror = () => { const left = imgs.filter((u) => u !== main.src && u !== main.getAttribute("src")); if (left.length) { imgs.splice(0, imgs.length, ...left); main.src = left[0]; } else { reportBroken(d.id); $("product").querySelector(".gallery").innerHTML = `<div class="main emoji">🎁</div>`; } };
  document.title = `${d.title} · giftdetect.com`;
  const sims = d.similar || []; $("t-similar").hidden = !sims.length; $("similar").innerHTML = ""; sims.forEach((r) => $("similar").appendChild(card(r)));
}
/* Which country to open: the one the visitor picked in the settings menu, else the country
   they are visiting from (Cloudflare IP geolocation via /api/geo; neighbours without their
   own catalog map to the closest one), else their browser language, else the first one. */
const NEAR = { AT: "DE", CH: "DE", LI: "DE", LU: "FR", MC: "FR" };
function fetchGeo() { return fetch("/api/geo", { cache: "no-store" }).then((r) => (r.ok ? r.json() : {})).then((j) => (j.country || "").toUpperCase()).catch(() => ""); }
async function detect(geoP) {
  try { const s = localStorage.getItem(PICKED); if (s && COUNTRIES[s]) return s; } catch (e) {}
  const lang = (navigator.language || "en").slice(0, 2).toLowerCase();
  let geo = await geoP;
  if (geo === "BE") geo = lang === "fr" ? "FR" : "NL";
  const byLang = { de: "DE", nl: "NL", fr: "FR", tr: "TR", en: "US" }[lang];
  return [geo, NEAR[geo], byLang, "US"].find((c) => c && COUNTRIES[c]) || Object.keys(COUNTRIES)[0];
}
function route() { const m = location.pathname.match(/^\/p\/([A-Za-z0-9_-]+)/); return m ? m[1] : null; }
async function init() {
  const geoP = fetchGeo();
  COUNTRIES = await GF.countries();
  $("settings-btn").onclick = (e) => { e.stopPropagation(); toggleSettings(); };
  $("settings-pop").onclick = (e) => {
    e.stopPropagation();
    const item = e.target.closest("[data-country]"), cookies = e.target.closest("[data-cookies]");
    toggleSettings(false);
    if (cookies && window.openConsent) window.openConsent();
    if (!item) return;
    const cc = item.dataset.country; try { localStorage.setItem(PICKED, cc); } catch (err) {}
    track("country_pick", { country: cc, from: state.country });
    if (cc !== state.country) setCountry(cc);
  };
  document.addEventListener("click", () => toggleSettings(false));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") toggleSettings(false); });
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
  const goHome = (e) => { e.preventDefault(); if (state.view === "product") history.pushState({}, "", "/"); state.searched = false; showSearch(); document.title = "giftdetect.com"; window.scrollTo({ top: 0 }); };
  $("home").onclick = goHome;
  $("back").onclick = (e) => { e.preventDefault(); if (state.view === "product") history.pushState({}, "", "/"); showSearch(); document.title = "giftdetect.com"; if (state.searched) $("results-wrap").scrollIntoView({ block: "start" }); };
  window.addEventListener("popstate", () => { const id = route(); if (id) openProduct(id, false); else { showSearch(); document.title = "giftdetect.com"; } });
  const pid = route();
  if (pid) {
    const p = await GF.product(pid);
    if (p) { await setCountry(COUNTRIES[p.country] ? p.country : await detect(geoP), { keepProduct: true }); state.view = "product"; state.product = pid; document.body.classList.add("product-mode"); $("hero").hidden = true; $("bar-wrap").hidden = true; $("product-wrap").hidden = false; renderProduct(p); }
    else await setCountry(await detect(geoP));
  } else { await setCountry(await detect(geoP)); pageView("/", "giftdetect.com"); }
  GF.stats().then((s) => { const h = s.model && s.model.holdout ? Object.entries(s.model.holdout).map(([k, v]) => `${k} F1 ${v.micro_f1}`).join(" · ") : ""; $("stats").textContent = `${s.products} products · text-mining model: ${h}`; });
}
init();
