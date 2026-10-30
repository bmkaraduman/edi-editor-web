/* Static provider: ranks in the browser from precomputed facet scores (DATA injected by scripts/export_static.py). */
(function () {
  const W = { gender: 0.9, age: 0.6, occasion: 0.8, personality: 1.0 };
  const norm = (s) => (s || "").replace(/ı/g, "i").replace(/İ/g, "i").replace(/ß/g, "ss").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();
  let index = null;
  function buildIndex(cc) {
    const docs = DATA.items.filter((it) => it.c === cc);
    const df = new Map(); const tfs = docs.map((it) => { const m = new Map(); it.n.split(" ").forEach((t) => t.length > 1 && m.set(t, (m.get(t) || 0) + 1)); m.forEach((_, t) => df.set(t, (df.get(t) || 0) + 1)); return m; });
    const N = docs.length; const idf = (t) => Math.log((N + 1) / ((df.get(t) || 0) + 1)) + 1;
    const vecs = tfs.map((m) => { const v = new Map(); let n = 0; m.forEach((c, t) => { const w = (1 + Math.log(c)) * idf(t); v.set(t, w); n += w * w; }); n = Math.sqrt(n) || 1; v.forEach((w, t) => v.set(t, w / n)); return v; });
    index = { cc, docs, vecs, idf };
  }
  function queryVec(text) { const m = new Map(); norm(text).split(" ").forEach((t) => t.length > 1 && m.set(t, (m.get(t) || 0) + 1)); const v = new Map(); let n = 0; m.forEach((c, t) => { const w = (1 + Math.log(c)) * index.idf(t); v.set(t, w); n += w * w; }); n = Math.sqrt(n) || 1; v.forEach((w, t) => v.set(t, w / n)); return v; }
  const cos = (a, b) => { let s = 0; a.forEach((w, t) => { const x = b.get(t); if (x) s += w * x; }); return s; };
  function expand(labels, lang) { const out = []; labels.forEach((l) => { const by = DATA.lexicon[l] || {}; out.push(...(by[lang] || []).slice(0, 6)); if (lang !== "en") out.push(...(by.en || []).slice(0, 6)); }); return out.join(" "); }

  function rank(p) {
    if (!index || index.cc !== p.country) buildIndex(p.country);
    const lang = DATA.countries[p.country].lang;
    const chosen = [...(p.gender && p.gender !== "unisex" ? [p.gender] : []), ...p.age, ...p.occasion, ...p.personality];
    const qv = chosen.length ? queryVec(expand(chosen, lang)) : null;
    const facets = [["age", p.age], ["occasion", p.occasion], ["personality", p.personality]];
    const out = [];
    index.docs.forEach((it, i) => {
      if (p.price_min != null && it.p < p.price_min) return; if (p.price_max != null && it.p > p.price_max) return;
      const g = (l) => it.s[l] || 0; let s = 0; const why = []; const parts = [];
      if (qv) s += cos(qv, index.vecs[i]);
      if (p.gender === "female" || p.gender === "male") { const o = p.gender === "female" ? "male" : "female"; const v = Math.max(g(p.gender), 0.7 * g("unisex")); s += W.gender * (v - 0.8 * g(o)); parts.push(v); if (g(p.gender) >= 0.5) why.push(p.gender); }
      facets.forEach(([f, ls]) => { if (!ls.length) return; let best = 0; ls.forEach((l) => { best = Math.max(best, g(l)); if (g(l) >= 0.5) why.push(l); }); s += W[f] * best; parts.push(best); });
      if (!chosen.length) s = ((i * 2654435761) % 1000) / 1000;
      const match = parts.length ? Math.round(100 * parts.reduce((a, b) => a + b, 0) / parts.length) : null;
      out.push({ it, s, why: [...new Set(why)].slice(0, 4), match });
    });
    if (p.sort === "price_asc") out.sort((a, b) => a.it.p - b.it.p || b.s - a.s);
    else if (p.sort === "price_desc") out.sort((a, b) => b.it.p - a.it.p || b.s - a.s);
    else out.sort((a, b) => b.s - a.s);
    const seen = {}; return out.filter((r) => { seen[r.it.cid] = (seen[r.it.cid] || 0) + 1; return seen[r.it.cid] <= 3; });
  }
  const lab = (l, lang) => (DATA.labels[l] || {})[lang] || l;
  window.GF = {
    demo: true,
    countries: async () => DATA.countries,
    options: async (lang) => ({ facets: Object.fromEntries(Object.entries(DATA.facets).map(([f, ls]) => [f, ls.map((l) => ({ id: l, label: lab(l, lang) }))])), titles: Object.fromEntries(Object.entries(DATA.titles).map(([f, v]) => [f, v[lang]])) }),
    stats: async () => ({ products: DATA.items.length, model: DATA.report }),
    search: async (p) => {
      const lang = DATA.countries[p.country].lang; const all = rank(p);
      return { total: all.length, results: all.slice(p.offset, p.offset + p.limit).map((r) => ({ id: r.it.id, title: r.it.t, description: r.it.d, price: r.it.p, price_text: r.it.pt, merchant: r.it.m, emoji: r.it.e, image: "", why: r.why.map((w) => lab(w, lang)), match: r.match, link: r.it.u })) };
    },
  };
})();
