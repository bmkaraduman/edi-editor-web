# giftdetect.com landing pages

Texts of the country home pages (`/de/`) and the gift lists (`/de/geschenke/fuer-papa/`),
one file per language: `content/lists/<lang>.json`. `scripts/list_pages.py` holds the lists
themselves (which search each one runs) and builds the pages; a list is written for a
country only when enough products fit it well.

* `root`: the URL segment for "gifts" (`geschenke`, `cadeaux`).
* `under_slug`, `under_h1`, `under_description`: the "under a price" pages
  (`/de/geschenke/zu-weihnachten/unter-50/`, "Weihnachtsgeschenke unter 50 €").
* `home`: title, description, heading and subline of a country's home page; `{country}` is
  the country's name.
* `ui`: the fixed words of the pages. `stats` is the line of numbers under the intro
  (`{n}` products, `{shops}`, `{country}`, `{min}`, `{max}`, `{median}`).
* `lists.<id>`: `slug` (lowercase ASCII, hyphens, unique), `h1` (the search phrase),
  `title` (at most 60 characters), `description` (120 to 160 characters), `intro` (two or
  three sentences). The ids are those of `LISTS` in `scripts/list_pages.py`; a new list needs
  an entry there and texts in every language (`tests/test_lists.py` checks it).

English is one file for five countries; for the United Kingdom, Ireland and Australia "mom"
becomes "mum" in the texts and the slugs (`/gb/gifts/for-mum/`).
