# giftdetect.com – text-mining tabanlı hediye arama motoru

Canlı alan adı: **giftdetect.com** (kod adı GiftFinder; eski ad idea.gift).

Cinsiyet, yaş, özel gün ve karakter seçimine (ya da serbest metne) göre hediye
öneren çok dilli bir site. Ürünler, her ülkenin **affiliate programı olan yerel
mağazalarından** gelir; arama motoru ürün **başlığı + açıklaması** üzerinde
text mining ile çalışır.

| Ülke | Dil | Para | Mağazalar (affiliate ağı) |
|------|-----|------|---------------------------|
| 🇺🇸 US | en | USD | Amazon (Associates), Etsy (Awin), Uncommon Goods / Target / Walmart (impact.com) |
| 🇩🇪 DE | de | EUR | Amazon.de (PartnerNet), OTTO, Etsy, Thalia, Douglas (Awin) |
| 🇹🇷 TR | tr | TRY | Trendyol (Ortaklık Programı), Hepsiburada / Çiçeksepeti / n11 (Gelirortakları), Amazon.com.tr |
| 🇳🇱 NL | nl | EUR | bol.com (Partnerprogramma), Amazon.nl, Coolblue / Etsy (Awin), Wehkamp (Daisycon) |
| 🇫🇷 FR | fr | EUR | Amazon.fr (Partenaires), Fnac, Cdiscount, Etsy, Nature & Découvertes (Awin) |

Sitede **DE, NL, FR, US** açık (`ACTIVE_COUNTRIES=DE,NL,FR,US`). Bu ülkelerin ürünleri
Awin feed'lerinden gelir (Ankashop yayıncı hesabı, tanıtım alanı giftdetect.com; DE 23,
NL 20, FR 12, US 43 programa katılındı). TR config'de durur: Awin'de Türkiye
reklamvereni yok, Trendyol/Gelirortakları feed'i gelince açılır.

## Hızlı başlangıç

```bash
cd giftfinder
python3 -m venv .venv && source .venv/bin/activate   # bağımlılıklar .venv'de; her yeni kabukta activate
./setup.sh                      # bağımlılıklar + seed katalog + model eğitimi
uvicorn app.main:app --reload   # http://127.0.0.1:8000
python3 -m pytest tests         # 22 test
```

`.venv` etkin değilse komutları `.venv/bin/python …` ile çalıştır.

Docker: `docker build -t giftfinder . && docker run -p 8000:8000 --env-file .env giftfinder`

## Nasıl çalışıyor

```
app/taxonomy.py        4 facet (gender / age / occasion / personality), 38 etiket,
                       her etiket için 5 dilde sözlük (lexicon)
app/data/concepts.py   88 elle etiketlenmiş hediye konsepti × 5 dil (eğitim verisi)
scripts/build_seed.py  konseptleri ülke başına 3 mağaza listesine çevirir, metni
                       sözlük cümleleriyle zenginleştirir -> app/data/catalog.json
app/ml/train.py        TF-IDF (kelime 1-2gram + karakter 3-5gram) + sözlük-isabet
                       kanalı -> facet başına one-vs-rest lojistik regresyon
app/ml/search.py       sıralama = metin benzerliği (kosinüs) + seçilen facet
                       olasılıkları; serbest metindeki ipuçları ("babam", "balık")
                       sözlükten facet'e çevrilir. Feed etiketlerine 0.75 güven
                       (elle etiketler 1.0); filtresiz ana sayfa karışımında
                       "hediye" demeyen feed satırları geri planda kalır
app/data/rules.py      kategori/keyword/ürün adı -> facet kural listesi (~45 kural, 5 dil)
                       + hediyelik puanı (şarap 1.0, ofis malzemesi 0.05)
app/ml/labeling.py     yeni feed ürünlerini etiketler: kurallar > güçlü alan sözlüğü
                       (başlık, kategori yolu, ürün tipi, keywords, marka) > açıklama
                       sözlüğü (≥2 isabet, kuralın karar vermediği facet'te) > sınıflandırıcı
app/sources/           Amazon PA-API 5 (SigV4 imzalı), Awin ürün feed'i, genel
                       CSV / Google Shopping feed (Trendyol, Hepsiburada, bol.com…)
scripts/ingest.py      yapılandırılmış kaynaklardan çek -> etiketle -> kataloğa ekle
app/occasions.py       ülkeye göre tarihli özel günler (Noel 24/25, Sevgililer, Anneler /
                       Babalar Günü; DE Vatertag = Christi Himmelfahrt) -> en yakın gün
app/main.py            FastAPI: /api/search, /api/product/{id}, /api/upcoming (ana sayfa
                       "yaklaşan gün" şeridi), /go/{id} (affiliate
                       yönlendirme), /p/{id} (ürün detay sayfası, SEO başlık/og:image ile)
web/                   5 dilli vitrin + ürün detay sayfası (galeri, etiketler, keywords,
                       detaylar, benzer ürünler); provider_api.js sunucu,
                       provider_static.js tarayıcı içi sıralama (statik demo)
```

### Eğitim sonuçları (konsept bazlı %20 hold-out, görülmemiş ürün tipleri)

| Facet | micro-F1 | macro-F1 |
|-------|---------:|---------:|
| gender | 0.85 | 0.38 |
| age | 0.77 | 0.63 |
| occasion | 0.73 | 0.66 |
| personality | 0.79 | 0.81 |

Bölme konsept bazında yapıldığı için test setindeki ürün tipleri eğitimde hiç
görülmemiştir; sayılar gerçek feed'lerdeki genellemeyi yansıtır. Eğitim sırasında
"ipucu tutarlı" gürültü eklenir: rastgele bir özel gün/karakter cümlesi
(ör. *"Idéal pour la fête des pères"*) ve etiketi metne eklenir, böylece model
açık ipuçlarını ürün tipi önyargısından üstün tutmayı öğrenir.

### Vitrin kuralları

* **Resmi olmayan ürün gösterilmez.** Ingest her görseli gerçekten indirir
  (`app/sources/images.py`, 32 paralel istek; `VERIFY_IMAGES=0` ile atlanır): 404 /
  görsel olmayan yanıt → ürün atılır, kırık galeri görselleri silinir. Tarayıcıda yine de
  yüklenemeyen bir kart kendini kaldırır ve `POST /api/broken/{id}` ile bildirir; ürün
  `app/data/hidden.jsonl`'a yazılıp bir daha gösterilmez. Seed (demo) ürünler yalnızca
  henüz gerçek ürünü olmayan ülkelerde görünür ve orada "Demo katalog" uyarısı çıkar.
* **Aynı ürün tekrar gösterilmez.** Üç anahtar birlikte çalışır
  (`app/ml/search.py: dedupe_keys`): varyant kökü (başlık ilk ayırıcıda kesilir,
  ölçü/renk sözcükleri atılır, ilk 3 sözcük + mağaza), görsel URL'si (varyantlar çoğu
  zaman aynı fotoğrafı paylaşır) ve ürün ailesi (mağaza + ilk 2 sözcük: "Chateau
  Purcari …", "Personalisierte Foto …"). Ayrıca bir mağaza her 12'lik sonuç bloğunda
  en fazla 4 kart alır; fazlası listenin sonuna kayar. Ana sayfadaki yaklaşan gün
  şeridi de aynı aramadan geçer.
* **Hediyelik puanı.** Kurallardan gelen 0-1 arası puan sıralamayı çarpar; 0.15 altı
  (ofis malzemesi, ağ kablosu) yalnızca serbest metin aramasında çıkar, filtresiz ana
  sayfa karışımına yalnızca 0.5 üstü girer. 0.9+ puanlı bir kural (kalem seti) ofis
  kuralını ezer.
* **Etiket güveni.** Elle etiket 1.0, kural etiketi 0.9, sözlük/sınıflandırıcı 0.75;
  "% passend" rozeti buna göre değişir.
* **Eğitim.** `app/ml/train.py` seed konseptlerin yanına en fazla 1500 kural-etiketli
  gerçek feed ürünü ekler (gerçek mağaza dili); ingest sonrası `python3 -m app.ml.train`.

## Gerçek ürünleri bağlama

1. `.env.example` → `.env`; affiliate kimliklerini doldur. `.env` uygulama ve
   script'ler tarafından otomatik okunur (gerçek ortam değişkenleri önceliklidir).
   Kimlik yoksa link düz mağaza linki olarak çalışır (site bozulmaz, sadece
   komisyon izlenmez).
2. Kaynaklar:
   * **Amazon**: `AMAZON_ACCESS_KEY`, `AMAZON_SECRET_KEY`, `AMAZON_TAG_<CC>` (PA-API için
     her pazarda onaylı Associates hesabı gerekir).
   * **Awin**: Create-a-Feed'de şu sütunları seç: product_name, description, aw_deep_link,
     aw_product_id, merchant_id/merchant_name, search_price, rrp_price, currency,
     merchant_image_url, large_image, alternate_image(_two/_three/_four),
     merchant_category, merchant_product_category_path, product_type, brand_name,
     keywords, colour, condition, product_model, dimensions, specifications,
     delivery_cost, promotional_text, product_short_description. "manual download URL" → ülke başına tek birleşik feed için
     `AWIN_FEED_ALL_DE` (boşlukla ayrılmış birden çok URL olabilir: bir Awin formatlı
     Create-a-Feed URL'si + yalnızca Google formatı sunan mağazaların feed URL'leri;
     Feed List: Toolbox → Create-a-Feed → "Feed List Download".
     Satırlar feed'deki merchant_id / advertiser_id sütunuyla mağazalara ayrılır;
     config'de olmayan reklamverenler `awin_<mid>` olarak, feed'deki adıyla gösterilir) ya da
     mağaza başına `AWIN_FEED_<merchant_id>` (ör. `AWIN_FEED_otto`). Feed akışla okunur
     (gzip desteklenir); yüz binlerce satırlık birleşik feed'lerde her reklamverenden en
     fazla `INGEST_LIMIT` (varsayılan 500) ürün rastgele örneklenir, metninde
     "Geschenk/gift/cadeau/hediye" geçenler önceliklidir. Böylece katalog tek bir
     ofis-malzemesi mağazasıyla dolmaz.
   * **CSV / Google Shopping feed**: `feeds/<CC>/<merchant_id>.csv` (ör.
     `feeds/TR/trendyol.csv`, `feeds/NL/bol.csv`). Sütun adları gevşek eşlenir
     (title/name/ürün adı, description/açıklama, price/fiyat, link, image).
3. `python3 scripts/ingest.py TR DE` → ürünler çekilir, text-mining modeliyle
   etiketlenir, kataloğa eklenir. Sunucuyu yeniden başlat. (Almanya feed'i: 170 bin
   satır, 22 reklamveren → ~50 saniyede ~6.300 ürün.)
4. Daha iyi model için: ingest edilen ürünlerden bazılarını elle düzeltip
   `"source": "manual"` yap, `python3 -m app.ml.train` ile yeniden eğit.

Seed ürünler mağazanın gerçek arama sayfasına (affiliate parametresiyle) yönlendirir;
böylece feed bağlanmadan da tıklamalar para kazandırır.

## Yayın (giftdetect.com, Cloudflare Pages)

Canlı site sunucusuz statik sürümdür: sıralama tarayıcıda yapılır, veri `data.json`
olarak gelir (6 bin ürün ≈ 7 MB, sıkıştırılmış ≈ 1 MB). Sunucu sürümüyle aynı kurallar
(resim doğrulama ingest'te, tekrar önleme ve yakın-kopya testi tarayıcıda, hediyelik
puanı, mağaza kotası, yaklaşan gün şeridi, `/p/{id}` ürün sayfaları `_redirects` ile).

```bash
python3 scripts/ingest.py DE && python3 -m app.ml.train   # yeni feed sonrası
python3 scripts/export_static.py dist                      # dist/: index.html, data.json, _redirects, sitemap.xml
npx wrangler@4 pages deploy dist --project-name giftdetect --branch main
```

İlk kurulum: `npx wrangler@4 login`, `npx wrangler@4 pages project create giftdetect
--production-branch main --force` (Pages projesi; `--force` yalnızca ilk kez), Pages
projesine özel alan adı (giftdetect.com, www) ve DNS'te `CNAME @ -> giftdetect.pages.dev`
(proxy açık). Önizleme adresi: https://giftdetect.pages.dev

## Analytics

Google Analytics 4 (`GA_MEASUREMENT_ID`, varsayılan G-XN9SC9S3K2; boş = kapalı). `web/analytics.js`
DSGVO için onay bandı gösterir ve gtag'i yalnızca "Erlauben" sonrasında yükler (reklam
çerezi yok, IP anonim); karar localStorage'da, altbilgideki "Cookie-Einstellungen" ile
değiştirilir. Olaylar: `page_view` (/, /search, /p/{id}), `search` (facet'ler + sonuç
sayısı), `view_item`, `shop_click` (affiliate tıklaması; kart ya da ürün sayfasından),
`upcoming_all`, `consent_granted`.

## API

```
GET /api/search?country=TR&gender=female&age=adult&occasion=mothers_day
               &personality=wellness&personality=coffee_tea&price_min=&price_max=
               &sort=relevance|price_asc|price_desc&limit=36&offset=0
GET /api/options?lang=tr      facet etiketleri
GET /api/countries            ülkeler ve mağazalar
GET /go/{id}                  affiliate yönlendirme (tıklama app/data/clicks.jsonl'a yazılır)
GET /api/stats                katalog boyutu + model raporu

Statik demo (sunucusuz, tarayıcı içi sıralama): `python3 scripts/export_static.py giftfinder-static.html`
```
