// Cloudflare Pages Function: GET /api/geo -> {"country": "DE"}, the visitor's country from
// Cloudflare's IP geolocation. The static site uses it to open the visitor's country.
export function onRequest({ request }) {
  const country = (request.cf && request.cf.country) || request.headers.get("cf-ipcountry") || "";
  return new Response(JSON.stringify({ country }), {
    headers: { "content-type": "application/json", "cache-control": "private, no-store" },
  });
}
