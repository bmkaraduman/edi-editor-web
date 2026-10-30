/* Server-backed provider: talks to the FastAPI endpoints. */
window.GF = {
  demo: true,
  countries: async () => (await fetch("/api/countries")).json(),
  options: async (lang) => (await fetch(`/api/options?lang=${lang}`)).json(),
  stats: async () => (await fetch("/api/stats")).json(),
  search: async (p) => {
    const u = new URLSearchParams({ country: p.country, sort: p.sort, limit: p.limit, offset: p.offset });
    if (p.gender) u.set("gender", p.gender);
    ["age", "occasion", "personality"].forEach((f) => (p[f] || []).forEach((v) => u.append(f, v)));
    if (p.price_min != null) u.set("price_min", p.price_min);
    if (p.price_max != null) u.set("price_max", p.price_max);
    return (await fetch(`/api/search?${u}`)).json();
  },
};
