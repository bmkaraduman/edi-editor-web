// "Ne Nedir?" arama modülü.
// Referans dizinini (search-index.json) çekip istemci tarafında filtreler.
// Dizin tools/build_reference.py tarafından üretilir.

const TYPE_ORDER = ['msg', 'seg', 'code'];

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/** Türkçe karakterleri de kapsayan sadeleştirme: "İMD" ~ "imd" */
function norm(s) {
  return String(s)
    .toLocaleLowerCase('tr')
    .replace(/ı/g, 'i').replace(/İ/g, 'i')
    .replace(/ş/g, 's').replace(/ğ/g, 'g')
    .replace(/ü/g, 'u').replace(/ö/g, 'o').replace(/ç/g, 'c')
    .trim();
}

/**
 * Puanlama: tam kod eşleşmesi en üstte, sonra kodun başlangıcı,
 * sonra açıklama içinde geçenler.
 */
function score(item, q) {
  const code = norm(item.c);
  const name = norm(item.n);
  if (code === q) return 0;
  if (code.startsWith(q)) return 1;
  if (code.includes(q)) return 2;
  if (name.startsWith(q)) return 3;
  if (name.includes(q)) return 4;
  return -1;
}

export function initSearch({ index, labels }) {
  const input = document.getElementById('q');
  const out = document.getElementById('results');
  const hint = document.getElementById('hint');

  let data = null;
  let pending = null;

  const load = fetch(index)
    .then((r) => r.json())
    .then((d) => { data = d; if (pending !== null) run(pending); })
    .catch(() => { out.innerHTML = '<p class="search-none">index unavailable</p>'; });

  function run(raw) {
    const q = norm(raw);
    if (!data) { pending = raw; return; }

    if (q.length < 1) {
      out.innerHTML = '';
      hint.hidden = false;
      return;
    }
    hint.hidden = true;

    const hits = [];
    for (const item of data) {
      const sc = score(item, q);
      if (sc >= 0) hits.push([sc, item]);
    }
    hits.sort((a, b) => a[0] - b[0] || a[1].c.localeCompare(b[1].c));

    if (!hits.length) {
      out.innerHTML = `<p class="search-none">${esc(labels.none)}</p>`;
      return;
    }

    // Bir mesaj tipi tam eşleştiyse içindeki segmentleri de göster
    const exactMsg = hits.find(([sc, it]) => sc === 0 && it.t === 'msg');
    const byType = { msg: [], seg: [], code: [] };
    for (const [, it] of hits.slice(0, 120)) byType[it.t]?.push(it);

    let html = '';
    for (const t of TYPE_ORDER) {
      const list = byType[t];
      if (!list.length) continue;
      html += `<h2>${esc(labels[t])}</h2><div class="search-list">`;
      for (const it of list) {
        html += `<a class="search-hit" href="${it.u}">
          <code>${esc(it.c)}</code><span>${esc(it.n)}</span></a>`;
      }
      html += '</div>';
    }

    if (exactMsg && exactMsg[1].f?.length) {
      const m = exactMsg[1];
      const segs = data.filter((x) => x.t === 'seg' && m.f.includes(x.c));
      html += `<h2>${esc(m.c)} ${esc(labels.inside)}</h2><div class="search-list">`;
      for (const s of m.f) {
        const found = segs.find((x) => x.c === s);
        html += `<a class="search-hit" href="${found ? found.u : '#'}">
          <code>${esc(s)}</code><span>${esc(found ? found.n : '')}</span></a>`;
      }
      html += '</div>';
    }

    out.innerHTML = html;
  }

  input.addEventListener('input', () => run(input.value));

  // Adres satırından gelen sorgu:  ara.html?q=NAD
  const fromURL = new URLSearchParams(location.search).get('q');
  if (fromURL) {
    input.value = fromURL;
    load.then(() => run(fromURL));
  }
}
