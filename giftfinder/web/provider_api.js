/* Server-backed provider: talks to the FastAPI endpoints. */
window.GF = {
  countries: async () => (await fetch("/api/countries")).json(),
  options: async (lang) => (await fetch(`/api/options?lang=${lang}`)).json(),
  stats: async () => (await fetch("/api/stats")).json(),
  broken: async (id) => fetch(`/api/broken/${encodeURIComponent(id)}`, { method: "POST" }),
  upcoming: async (country) => (await fetch(`/api/upcoming?country=${country}&limit=16`)).json(),
  product: async (id) => { const r = await fetch(`/api/product/${encodeURIComponent(id)}`); return r.ok ? r.json() : null; },
  search: async (p) => {
    const u = new URLSearchParams({ country: p.country, sort: p.sort, limit: p.limit, offset: p.offset });
    if (p.q) u.set("q", p.q);
    if (p.gender) u.set("gender", p.gender);
    ["age", "occasion", "personality"].forEach((f) => (p[f] || []).forEach((v) => u.append(f, v)));
    if (p.price_min != null) u.set("price_min", p.price_min);
    if (p.price_max != null) u.set("price_max", p.price_max);
    return (await fetch(`/api/search?${u}`)).json();
  },
};
