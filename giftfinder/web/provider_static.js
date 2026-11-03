/* Static provider: ranks in the browser from data.json (built by scripts/export_static.py).
   Same house rules as the server: pictures verified at build time, one listing per product /
   family / near-duplicate cluster, giftability floor and damping, a per-shop cap per block. */
(function () {
  const W = { gender: 0.9, age: 0.6, occasion: 0.8, personality: 1.0 };
  const GIFT_FLOOR = 0.15, HOME_FLOOR = 0.5, MERCHANT_CAP = 4, BLOCK = 12;
  const norm = (s) => (s || "").replace(/ı/g, "i").replace(/İ/g, "i").replace(/ß/g, "ss").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();
  const NEAR_STEM = 0.5, NEAR_DESC = 0.9;
  let DATA = null, index = null;
  /* variant stem: title cut at the first separator, size/colour/volume tokens removed (mirrors app/ml/search.py) */
  const VARIANT_TOKEN = /^(\d+([.,]\d+)?(ml|cl|l|g|kg|mm|cm|m|w|v|a|er|x|st|stk|pcs|pack|paar|pair)?|x?s|m|l|xl|xxl|xxxl|\d+-\d+|\d+\/\d+|gr(o|ö)(ss|ß)e|size|farbe|colou?r|black|white|schwarz|weiss|blau|blue|rot|red|grau|grey|gray|beige|braun|brown|grun|green|gelb|yellow|rosa|pink|navy|marine|oliv|olive|silber|silver|gold)$/;
  const stemTokens = (t) => norm(t.split(/\s+[–|\-\/]\s+|\s*\|\s*|,\s+/)[0]).split(" ").filter((x) => x && !VARIANT_TOKEN.test(x));
  const trigrams = (s) => { const g = new Set(); const p = ` ${s} `; for (let i = 0; i < p.length - 2; i++) g.add(p.slice(i, i + 3)); return g; };
  const setCos = (a, b) => { let n = 0; a.forEach((x) => { if (b.has(x)) n++; }); return n / Math.sqrt(a.size * b.size || 1); };
  function prepare(it) {
    const toks = stemTokens(it.t);
    it.k = it.cid ? ["concept:" + it.cid] : [`${it.mid}:${toks.slice(0, 3).join(" ")}`, `fam:${it.mid}:${toks.slice(0, 2).join(" ")}`];
    if (it.i) it.k.push("img:" + it.i);
    it.tg = trigrams(toks.join(" ")); it.dw = new Set(norm(it.d).split(" ").filter((x) => x.length > 2));
    it.n = [norm(it.t), norm(it.t), norm((it.kw || []).join(" ")), norm(it.d), norm(it.b || ""), norm(it.cat || ""), norm(it.pt2 || "")].join(" ");
  }
  const ready = fetch("/data.json").then((r) => r.json()).then((d) => { DATA = d; d.items.forEach(prepare); return d; });
  const nearDuplicate = (it, shown) => shown.some((o) => setCos(it.tg, o.tg) >= NEAR_STEM || setCos(it.dw, o.dw) >= NEAR_DESC);
  /* tokens plus a 5-letter prefix per long token, so "weihnachten" meets "Weihnachts-Flaschentüte" and "geschenk" meets "Geschenkset" */
  const toks = (text) => { const out = []; text.split(" ").forEach((t) => { if (t.length > 1) { out.push(t); if (t.length > 5) out.push(t.slice(0, 5) + "~"); } }); return out; };
  function buildIndex(cc) {
    const docs = DATA.items.filter((it) => it.c === cc);
    const df = new Map(); const tfs = docs.map((it) => { const m = new Map(); toks(it.n).forEach((t) => m.set(t, (m.get(t) || 0) + 1)); m.forEach((_, t) => df.set(t, (df.get(t) || 0) + 1)); return m; });
    const N = docs.length; const idf = (t) => Math.log((N + 1) / ((df.get(t) || 0) + 1)) + 1;
    const vecs = tfs.map((m) => { const v = new Map(); let n = 0; m.forEach((c, t) => { const w = (1 + Math.log(c)) * idf(t); v.set(t, w); n += w * w; }); n = Math.sqrt(n) || 1; v.forEach((w, t) => v.set(t, w / n)); return v; });
    index = { cc, docs, vecs, idf };
  }
  function queryVec(text) { const m = new Map(); toks(norm(text)).forEach((t) => m.set(t, (m.get(t) || 0) + 1)); const v = new Map(); let n = 0; m.forEach((c, t) => { const w = (1 + Math.log(c)) * index.idf(t); v.set(t, w); n += w * w; }); n = Math.sqrt(n) || 1; v.forEach((w, t) => v.set(t, w / n)); return v; }
  const cos = (a, b) => { let s = 0; a.forEach((w, t) => { const x = b.get(t); if (x) s += w * x; }); return s; };
  function expand(labels, lang) { const out = []; labels.forEach((l) => { const by = DATA.lexicon[l] || {}; out.push(...(by[lang] || []).slice(0, 6)); if (lang !== "en") out.push(...(by.en || []).slice(0, 6)); }); return out.join(" "); }
  const keysOf = (it) => it.k;
  /* one listing per product / family / near-duplicate (checked against what the page shows, for the
     first `need` picks), plus at most MERCHANT_CAP per shop per block (surplus moves down) */
  function pick(rows, exclude = [], need = 60, cap = MERCHANT_CAP) {
    const seen = new Set(exclude); const out = [], deferred = []; const per = {}, shown = {};
    rows.forEach((r) => {
      const ks = keysOf(r.it); if (ks.some((k) => seen.has(k))) return;
      if (out.length < need && nearDuplicate(r.it, shown[r.it.mid] || [])) return;
      ks.forEach((k) => seen.add(k));
      const key = r.it.mid + ":" + Math.floor(out.length / BLOCK);
      if ((per[key] || 0) >= cap) { deferred.push(r); return; }
      per[key] = (per[key] || 0) + 1; out.push(r); (shown[r.it.mid] = shown[r.it.mid] || []).push(r.it);
    });
    return out.concat(deferred);
  }
  function rank(p) {
    if (!index || index.cc !== p.country) buildIndex(p.country);
    const lang = DATA.countries[p.country].lang;
    const chosen = [...(p.gender && p.gender !== "unisex" ? [p.gender] : []), ...p.age, ...p.occasion, ...p.personality];
    const typed = norm(p.q || "");
    const qv = chosen.length || typed ? queryVec(`${typed} ${typed} ${chosen.length ? expand(chosen, lang) : ""}`) : null;
    const facets = [["age", p.age], ["occasion", p.occasion], ["personality", p.personality]];
    const out = [];
    index.docs.forEach((it, i) => {
      if (p.price_min != null && it.p < p.price_min) return; if (p.price_max != null && it.p > p.price_max) return;
      if (!typed && it.g < GIFT_FLOOR) return;
      const g = (l) => it.s[l] || 0; let s = 0; const why = []; const parts = [];
      if (qv) s += cos(qv, index.vecs[i]) * (typed ? 2 : 1);
      if (p.gender === "female" || p.gender === "male") { const o = p.gender === "female" ? "male" : "female"; const v = Math.max(g(p.gender), 0.7 * g("unisex")); s += W.gender * (v - 0.8 * g(o)); parts.push(v); if (g(p.gender) >= 0.5) why.push(p.gender); }
      facets.forEach(([f, ls]) => { if (!ls.length) return; let best = 0; ls.forEach((l) => { best = Math.max(best, g(l)); if (g(l) >= 0.5) why.push(l); }); s += W[f] * best; parts.push(best); });
      if (!chosen.length && !typed) s = (((i + 1) * 2654435761) % 1000) / 1000 * (it.g >= HOME_FLOOR ? it.g : 0); else s *= 0.3 + 0.7 * it.g;
      const match = parts.length ? Math.round(100 * parts.reduce((a, b) => a + b, 0) / parts.length) : null;
      out.push({ it, s, why: [...new Set(why)].slice(0, 4), match });
    });
    if (p.sort === "price_asc") out.sort((a, b) => a.it.p - b.it.p || b.s - a.s);
    else if (p.sort === "price_desc") out.sort((a, b) => b.it.p - a.it.p || b.s - a.s);
    else out.sort((a, b) => b.s - a.s);
    return pick(out, [], (p.offset || 0) + (p.limit || 36) + BLOCK);
  }
  const lab = (l, lang) => (DATA.labels[l] || {})[lang] || l;
  const render = (it, lang, why = [], match = null) => ({ id: it.id, title: it.t, description: it.d, price: it.p, price_text: it.pt, rrp_text: it.rt || null, merchant: it.m, brand: it.b || "", emoji: it.e, image: it.i || "", gallery: it.i ? 1 + (it.imgs || []).length : 0, why: why.map((w) => lab(w, lang)), match, link: it.u, detail: `/p/${it.id}` });
  window.GF = {
    countries: async () => (await ready).countries,
    options: async (lang) => { await ready; return { facets: Object.fromEntries(Object.entries(DATA.facets).map(([f, ls]) => [f, ls.map((l) => ({ id: l, label: lab(l, lang) }))])), titles: Object.fromEntries(Object.entries(DATA.titles).map(([f, v]) => [f, v[lang]])) }; },
    stats: async () => { await ready; return { products: DATA.items.length, model: DATA.report }; },
    search: async (p) => {
      await ready; const lang = DATA.countries[p.country].lang; const all = rank(p);
      return { total: all.length, demo: !DATA.real.includes(p.country), results: all.slice(p.offset, p.offset + p.limit).map((r) => render(r.it, lang, r.why, r.match)) };
    },
    upcoming: async (cc) => {
      await ready; const u = DATA.upcoming[cc]; if (!u) return null; const lang = DATA.countries[cc].lang;
      const all = rank({ country: cc, age: [], occasion: [u.occasion], personality: [], sort: "relevance" });
      return Object.assign({}, u, { total: all.length, results: all.slice(0, 8).map((r) => render(r.it, lang, r.why, r.match)) });
    },
    product: async (id) => {
      await ready; const it = DATA.items.find((x) => x.id === id); if (!it) return null;
      const lang = DATA.countries[it.c].lang; const d = render(it, lang);
      Object.assign(d, { country: it.c, lang, images: it.i ? [it.i, ...(it.imgs || [])] : [], category: it.cat || "", product_type: "", keywords: it.kw || [], details: it.det || {}, rules: it.r || [], source: it.src || "feed",
        labels: Object.fromEntries(Object.entries(it.lab || {}).filter(([f, ls]) => ls.length && !(f === "gender" && ls[0] === "unisex")).map(([f, ls]) => [f, ls.map((l) => ({ id: l, label: lab(l, lang) }))])) });
      if (!index || index.cc !== it.c) buildIndex(it.c);
      const qv = queryVec([it.t, (it.kw || []).join(" "), it.cat || ""].join(" "));
      const rows = index.docs.map((x, i) => ({ it: x, s: cos(qv, index.vecs[i]) * (0.3 + 0.7 * x.g) })).filter((r) => r.it.id !== it.id).sort((a, b) => b.s - a.s);
      d.similar = pick(rows, keysOf(it), 8 + BLOCK, Infinity).filter((r) => !nearDuplicate(r.it, [it])).slice(0, 8).map((r) => render(r.it, lang));
      return d;
    },
  };
})();
