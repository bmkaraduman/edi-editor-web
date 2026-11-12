# giftdetect.com blog

One Markdown file per article and language: `content/blog/<lang>/<id>.md`. `id` is the
same in every language (it ties the translations together for hreflang); the URL uses the
language's own `slug`: `https://giftdetect.com/blog/<lang>/<slug>/`.
`scripts/export_static.py` turns them into static pages with the site's gift search bar on
top, and lists them in `sitemap-blog.xml`.

Languages: en, de, nl, fr, pl, it, es, sv, fi, da, pt (Brazil), ro — the languages of the
countries the site shows.

```markdown
---
id: christmas-gift-ideas
slug: weihnachtsgeschenke-ideen
title: Weihnachtsgeschenke 2026: 40 Ideen für die ganze Familie
description: Meta description, 140-160 characters, with the main search phrase.
date: 2026-11-12
search: occasion=christmas
---

Intro paragraph (the first paragraph is also the teaser on the blog index).

## A section heading

Text with **bold**, *italic* and [links](blog:gifts-for-dad).

- list item
- list item

1. numbered item

[[search occasion=christmas gender=female | Weihnachtsgeschenke für sie finden]]
```

* Front matter: `id`, `slug` (lowercase ASCII, hyphens), `title` (≤ 65 characters is ideal),
  `description` (140-160 characters), `date` (YYYY-MM-DD), `search` (the facets of the big
  search button under the article).
* Body: `##` / `###` headings, paragraphs, `-` and `1.` lists, `**bold**`, `*italic*`,
  `[text](url)` links. No HTML, no images.
* `[[search key=value ... | Button text]]` on a line of its own is a button that opens the
  gift search with those filters. Keys: `gender` (female, male), `age` (baby, child, teen,
  young_adult, adult, senior), `occasion`, `personality` (up to 3, comma-separated),
  `category` (comma-separated), `max` (price ceiling in the local currency). Values are the
  ids from `app/taxonomy.py`.
* Links to other articles: `[text](blog:<id>)`; the export turns them into the same
  language's URL, so a translation keeps its links without knowing the other slugs.
