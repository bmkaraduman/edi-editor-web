# idea.gift – text-mining tabanlı hediye arama motoru

Canlı alan adı: **idea.gift** (kod adı GiftFinder).

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

## Hızlı başlangıç

```bash
cd giftfinder
./setup.sh                      # bağımlılıklar + seed katalog + model eğitimi
uvicorn app.main:app --reload   # http://127.0.0.1:8000
python3 -m pytest tests         # 11 test
```

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
                       sözlükten facet'e çevrilir
app/ml/labeling.py     yeni feed ürünlerini etiketler: sınıflandırıcı ∪ sözlük
app/sources/           Amazon PA-API 5 (SigV4 imzalı), Awin ürün feed'i, genel
                       CSV / Google Shopping feed (Trendyol, Hepsiburada, bol.com…)
scripts/ingest.py      yapılandırılmış kaynaklardan çek -> etiketle -> kataloğa ekle
app/main.py            FastAPI: /api/search, /api/options, /go/{id} (affiliate yönlendirme)
web/                   5 dilli vitrin (body.html + style.css + ui.js); provider_api.js sunucu,
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

## Gerçek ürünleri bağlama

1. `.env.example` → `.env`; affiliate kimliklerini doldur. Kimlik yoksa link
   düz mağaza linki olarak çalışır (site bozulmaz, sadece komisyon izlenmez).
2. Kaynaklar:
   * **Amazon**: `AMAZON_ACCESS_KEY`, `AMAZON_SECRET_KEY`, `AMAZON_TAG_<CC>` (PA-API için
     her pazarda onaylı Associates hesabı gerekir).
   * **Awin**: Create-a-Feed'den "manual download URL" → ülke başına tek birleşik feed için
     `AWIN_FEED_ALL_DE` (satırlar feed'deki merchant_id sütunuyla mağazalara ayrılır) ya da
     mağaza başına `AWIN_FEED_<merchant_id>` (ör. `AWIN_FEED_otto`).
   * **CSV / Google Shopping feed**: `feeds/<CC>/<merchant_id>.csv` (ör.
     `feeds/TR/trendyol.csv`, `feeds/NL/bol.csv`). Sütun adları gevşek eşlenir
     (title/name/ürün adı, description/açıklama, price/fiyat, link, image).
3. `python3 scripts/ingest.py TR DE` → ürünler çekilir, text-mining modeliyle
   etiketlenir, kataloğa eklenir. Sunucuyu yeniden başlat.
4. Daha iyi model için: ingest edilen ürünlerden bazılarını elle düzeltip
   `"source": "manual"` yap, `python3 -m app.ml.train` ile yeniden eğit.

Seed ürünler mağazanın gerçek arama sayfasına (affiliate parametresiyle) yönlendirir;
böylece feed bağlanmadan da tıklamalar para kazandırır.

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
