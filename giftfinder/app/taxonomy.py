"""Facet taxonomy and multilingual lexicons.

Every product is described along four facets. The lexicons below serve three
purposes: (1) weak labelling of raw affiliate-feed items that come without
labels, (2) query expansion when the visitor only picks filters and types no
free text, and (3) the UI labels for each supported language.
"""

LANGS = ["en", "de", "tr", "nl", "fr"]

FACETS = {
    "gender": ["female", "male", "unisex"],
    "age": ["baby", "child", "teen", "young_adult", "adult", "senior"],
    "occasion": [
        "birthday", "anniversary", "valentines", "christmas", "mothers_day",
        "fathers_day", "wedding", "graduation", "new_baby", "housewarming",
        "retirement", "get_well", "thank_you",
    ],
    "personality": [
        "tech", "gamer", "foodie", "coffee_tea", "outdoor", "fitness",
        "bookworm", "artist", "music", "traveler", "homebody", "fashion",
        "gardener", "pet_lover", "wellness", "maker",
    ],
}

# Filter values that never go together. The search bar hides an option that clashes with
# what is already picked (a baby has no "Gamer" personality, "Her" has no Father's Day).
# Per age: the occasions and personalities that fit; ages not listed fit everything.
AGE_FITS = {
    "baby": {"occasion": ["birthday", "christmas", "new_baby"],
             "personality": ["bookworm", "music", "pet_lover"]},
    "child": {"occasion": ["birthday", "christmas", "get_well", "thank_you"],
              "personality": ["tech", "gamer", "outdoor", "fitness", "bookworm", "artist", "music", "pet_lover", "maker", "fashion", "gardener", "foodie"]},
    "teen": {"occasion": ["birthday", "christmas", "valentines", "graduation", "get_well", "thank_you"],
             "personality": ["tech", "gamer", "outdoor", "fitness", "bookworm", "artist", "music", "traveler", "pet_lover", "maker", "fashion", "foodie", "wellness"]},
    "young_adult": {"occasion": [o for o in FACETS["occasion"] if o != "retirement"]},
    "senior": {"occasion": [o for o in FACETS["occasion"] if o != "graduation"]},
}
GENDER_CLASHES = {"female": ["fathers_day"], "male": ["mothers_day"]}


def clashes():
    """Sorted [a, b] label pairs that cannot be picked together."""
    pairs = set()
    for age, fits in AGE_FITS.items():
        for facet, ok in fits.items():
            pairs |= {tuple(sorted((age, l))) for l in FACETS[facet] if l not in ok}
    for gender, bad in GENDER_CLASHES.items():
        pairs |= {tuple(sorted((gender, l))) for l in bad}
    return [list(p) for p in sorted(pairs)]


# Facets where exactly one label applies per product.
SINGLE_LABEL = {"gender"}

# label -> lang -> keywords used for weak labelling and query expansion.
LEXICON = {
    # ---- gender ----
    "female": {
        "en": ["for her", "women", "woman", "girlfriend", "wife", "mom", "mother", "sister", "daughter", "ladies"],
        "de": ["für sie", "damen", "frau", "frauen", "freundin", "ehefrau", "mama", "mutter", "schwester", "tochter"],
        "tr": ["kadın", "kadınlar", "sevgiliye", "eşe", "anne", "anneye", "kız kardeş", "kızı", "bayan", "ona kadın"],
        "nl": ["voor haar", "dames", "vrouw", "vrouwen", "vriendin", "echtgenote", "mama", "moeder", "zus", "dochter"],
        "fr": ["pour elle", "femme", "femmes", "copine", "épouse", "maman", "mère", "soeur", "fille", "madame"],
    },
    "male": {
        "en": ["for him", "men", "man", "boyfriend", "husband", "dad", "father", "brother", "son", "gentlemen"],
        "de": ["für ihn", "herren", "mann", "männer", "freund", "ehemann", "papa", "vater", "bruder", "sohn"],
        "tr": ["erkek", "erkekler", "sevgiliye erkek", "kocaya", "baba", "babaya", "erkek kardeş", "oğlu", "bay"],
        "nl": ["voor hem", "heren", "man", "mannen", "vriend", "echtgenoot", "papa", "vader", "broer", "zoon"],
        "fr": ["pour lui", "homme", "hommes", "copain", "mari", "papa", "père", "frère", "fils", "monsieur"],
    },
    "unisex": {
        "en": ["unisex", "for everyone", "for anyone", "for all"],
        "de": ["unisex", "für alle", "für jeden"],
        "tr": ["unisex", "herkese", "herkes için"],
        "nl": ["unisex", "voor iedereen"],
        "fr": ["unisexe", "pour tous", "pour tout le monde"],
    },
    # ---- age ----
    "baby": {
        "en": ["baby", "newborn", "infant", "toddler", "0-2"],
        "de": ["baby", "neugeborene", "säugling", "kleinkind"],
        "tr": ["bebek", "yenidoğan", "yeni doğan", "0-2 yaş"],
        "nl": ["baby", "pasgeboren", "peuter", "dreumes"],
        "fr": ["bébé", "nouveau-né", "nourrisson", "tout-petit"],
    },
    "child": {
        "en": ["kids", "children", "child", "boys", "girls", "ages 3", "ages 6", "ages 8"],
        "de": ["kinder", "kind", "jungen", "mädchen", "ab 3 jahren", "ab 6 jahren"],
        "tr": ["çocuk", "çocuklar", "erkek çocuk", "kız çocuk", "3 yaş", "6 yaş", "8 yaş"],
        "nl": ["kinderen", "kind", "jongens", "meisjes", "vanaf 3 jaar", "vanaf 6 jaar"],
        "fr": ["enfants", "enfant", "garçons", "filles", "dès 3 ans", "dès 6 ans"],
    },
    "teen": {
        "en": ["teen", "teenager", "teens", "13-17", "young people"],
        "de": ["teenager", "jugendliche", "teenie", "jugend"],
        "tr": ["genç", "gençler", "ergen", "lise"],
        "nl": ["tiener", "tieners", "jongeren", "puber"],
        "fr": ["ado", "adolescent", "adolescents", "jeunes"],
    },
    "young_adult": {
        "en": ["young adult", "student", "college", "twenties", "millennial", "gen z"],
        "de": ["junge erwachsene", "student", "studentin", "zwanziger", "uni"],
        "tr": ["genç yetişkin", "öğrenci", "üniversite", "yirmili"],
        "nl": ["jongvolwassene", "student", "studenten", "twintiger"],
        "fr": ["jeune adulte", "étudiant", "étudiante", "vingtaine"],
    },
    "adult": {
        "en": ["adult", "adults", "grown-up", "professional", "colleague", "coworker"],
        "de": ["erwachsene", "erwachsener", "kollege", "kollegin", "beruf"],
        "tr": ["yetişkin", "yetişkinler", "iş arkadaşı", "meslektaş"],
        "nl": ["volwassene", "volwassenen", "collega"],
        "fr": ["adulte", "adultes", "collègue", "professionnel"],
    },
    "senior": {
        "en": ["senior", "seniors", "grandma", "grandpa", "grandmother", "grandfather", "elderly", "retiree"],
        "de": ["senioren", "oma", "opa", "großmutter", "großvater", "rentner"],
        "tr": ["yaşlı", "büyükanne", "büyükbaba", "anneanne", "babaanne", "dede", "emekli"],
        "nl": ["senior", "oma", "opa", "grootmoeder", "grootvader", "ouderen"],
        "fr": ["senior", "seniors", "mamie", "papi", "grand-mère", "grand-père", "retraité"],
    },
    # ---- occasion ----
    "birthday": {
        "en": ["birthday", "bday", "turning 30", "turning 40", "turning 50"],
        "de": ["geburtstag", "geburtstagsgeschenk", "zum 30", "zum 40", "zum 50"],
        "tr": ["doğum günü", "doğumgünü", "yaş günü", "30 yaş", "40 yaş"],
        "nl": ["verjaardag", "verjaardagscadeau", "jarig", "30 jaar", "40 jaar"],
        "fr": ["anniversaire", "cadeau d'anniversaire", "30 ans", "40 ans", "50 ans"],
    },
    "anniversary": {
        "en": ["anniversary", "years together", "couple", "couples"],
        "de": ["jahrestag", "hochzeitstag", "paar", "pärchen"],
        "tr": ["yıldönümü", "yıl dönümü", "evlilik yıldönümü", "çift"],
        "nl": ["jubileum", "trouwdag", "huwelijksverjaardag", "koppel"],
        "fr": ["anniversaire de mariage", "anniversaire de couple", "couple", "noces"],
    },
    "valentines": {
        "en": ["valentine", "valentine's day", "romantic", "love", "sweetheart"],
        "de": ["valentinstag", "romantisch", "liebe", "liebling"],
        "tr": ["sevgililer günü", "romantik", "aşk", "sevgili", "14 şubat"],
        "nl": ["valentijn", "valentijnsdag", "romantisch", "liefde"],
        "fr": ["saint-valentin", "saint valentin", "romantique", "amour", "amoureux"],
    },
    "christmas": {
        "en": ["christmas", "xmas", "holiday", "stocking stuffer", "secret santa", "new year"],
        "de": ["weihnachten", "weihnachtsgeschenk", "nikolaus", "wichteln", "advent", "neujahr"],
        "tr": ["yılbaşı", "yeni yıl", "noel", "yılbaşı hediyesi"],
        "nl": ["kerst", "kerstmis", "kerstcadeau", "sinterklaas", "nieuwjaar"],
        "fr": ["noël", "cadeau de noël", "nouvel an", "fêtes de fin d'année"],
    },
    "mothers_day": {
        "en": ["mother's day", "mothers day", "mom", "mum"],
        "de": ["muttertag", "muttertagsgeschenk", "mama"],
        "tr": ["anneler günü", "anneye hediye", "anne"],
        "nl": ["moederdag", "moederdagcadeau", "mama"],
        "fr": ["fête des mères", "maman"],
    },
    "fathers_day": {
        "en": ["father's day", "fathers day", "dad"],
        "de": ["vatertag", "vatertagsgeschenk", "papa"],
        "tr": ["babalar günü", "babaya hediye", "baba"],
        "nl": ["vaderdag", "vaderdagcadeau", "papa"],
        "fr": ["fête des pères", "papa"],
    },
    "wedding": {
        "en": ["wedding", "bride", "groom", "newlyweds", "engagement", "bridal"],
        "de": ["hochzeit", "hochzeitsgeschenk", "braut", "bräutigam", "verlobung", "brautpaar"],
        "tr": ["düğün", "düğün hediyesi", "gelin", "damat", "nişan", "evlilik"],
        "nl": ["bruiloft", "huwelijk", "bruid", "bruidegom", "verloving", "trouwcadeau"],
        "fr": ["mariage", "cadeau de mariage", "mariée", "marié", "fiançailles", "jeunes mariés"],
    },
    "graduation": {
        "en": ["graduation", "graduate", "grad", "diploma", "class of"],
        "de": ["abschluss", "abitur", "absolvent", "bachelor", "master", "schulabschluss"],
        "tr": ["mezuniyet", "mezun", "diploma", "mezuniyet hediyesi"],
        "nl": ["afstuderen", "geslaagd", "diploma", "afgestudeerd"],
        "fr": ["diplôme", "remise des diplômes", "diplômé", "bac", "réussite"],
    },
    "new_baby": {
        "en": ["new baby", "baby shower", "newborn gift", "new parents", "expecting"],
        "de": ["geburt", "babyparty", "zur geburt", "frischgebackene eltern", "neugeborenes"],
        "tr": ["yeni bebek", "baby shower", "doğum hediyesi", "yeni anne", "hoşgeldin bebek"],
        "nl": ["kraamcadeau", "babyshower", "geboorte", "pasgeboren", "kersverse ouders"],
        "fr": ["naissance", "cadeau de naissance", "baby shower", "jeunes parents", "nouveau-né"],
    },
    "housewarming": {
        "en": ["housewarming", "new home", "new apartment", "moving in", "home decor"],
        "de": ["einzug", "einweihung", "neues zuhause", "wohnungseinweihung", "wohndeko"],
        "tr": ["yeni ev", "ev hediyesi", "taşınma", "ev dekorasyonu", "hoş geldin evine"],
        "nl": ["housewarming", "nieuwe woning", "nieuw huis", "verhuizing", "woondecoratie"],
        "fr": ["crémaillère", "pendaison de crémaillère", "nouvelle maison", "déco maison"],
    },
    "retirement": {
        "en": ["retirement", "retiring", "retiree", "farewell"],
        "de": ["ruhestand", "rente", "pensionierung", "abschied"],
        "tr": ["emeklilik", "emekli", "veda", "emeklilik hediyesi"],
        "nl": ["pensioen", "pensionering", "afscheid", "gepensioneerd"],
        "fr": ["retraite", "départ en retraite", "retraité", "pot de départ"],
    },
    "get_well": {
        "en": ["get well", "get well soon", "recovery", "feel better", "comfort"],
        "de": ["gute besserung", "genesung", "aufmunterung", "trost"],
        "tr": ["geçmiş olsun", "iyileşme", "moral", "hasta ziyareti"],
        "nl": ["beterschap", "herstel", "opkikker", "troost"],
        "fr": ["bon rétablissement", "prompt rétablissement", "guérison", "réconfort"],
    },
    "thank_you": {
        "en": ["thank you", "thanks", "appreciation", "gratitude", "teacher gift", "host gift"],
        "de": ["dankeschön", "danke", "anerkennung", "lehrergeschenk", "gastgeschenk"],
        "tr": ["teşekkür", "teşekkür hediyesi", "öğretmene hediye", "minnet"],
        "nl": ["bedankt", "bedankje", "dank je", "waardering", "juf cadeau"],
        "fr": ["merci", "remerciement", "gratitude", "cadeau maîtresse"],
    },
    # ---- personality ----
    "tech": {
        "en": ["tech", "gadget", "smart", "wireless", "bluetooth", "usb", "charger", "electronic", "geek"],
        "de": ["technik", "gadget", "smart", "kabellos", "bluetooth", "usb", "ladegerät", "elektronik", "nerd"],
        "tr": ["teknoloji", "gadget", "akıllı", "kablosuz", "bluetooth", "usb", "şarj", "elektronik", "teknolojik"],
        "nl": ["tech", "gadget", "slim", "draadloos", "bluetooth", "usb", "oplader", "elektronica"],
        "fr": ["tech", "gadget", "connecté", "sans fil", "bluetooth", "usb", "chargeur", "électronique", "geek"],
    },
    "gamer": {
        "en": ["gamer", "gaming", "video game", "console", "playstation", "xbox", "nintendo", "pc gaming", "controller"],
        "de": ["gamer", "gaming", "videospiel", "konsole", "playstation", "xbox", "nintendo", "zocker", "controller"],
        "tr": ["oyuncu", "gamer", "oyun", "video oyunu", "konsol", "playstation", "xbox", "nintendo", "gaming"],
        "nl": ["gamer", "gaming", "videogame", "console", "playstation", "xbox", "nintendo", "controller"],
        "fr": ["gamer", "gaming", "jeu vidéo", "console", "playstation", "xbox", "nintendo", "manette", "joueur"],
    },
    "foodie": {
        "en": ["foodie", "gourmet", "cooking", "chef", "kitchen", "recipe", "snack", "chocolate", "cheese", "wine", "bbq", "grill"],
        "de": ["feinschmecker", "gourmet", "kochen", "koch", "küche", "rezept", "schokolade", "käse", "wein", "grill"],
        "tr": ["gurme", "yemek", "mutfak", "aşçı", "tarif", "çikolata", "peynir", "şarap", "mangal", "lezzet"],
        "nl": ["foodie", "gourmet", "koken", "kok", "keuken", "recept", "chocolade", "kaas", "wijn", "bbq"],
        "fr": ["gourmet", "gourmand", "cuisine", "chef", "recette", "chocolat", "fromage", "vin", "barbecue", "épicurien"],
    },
    "coffee_tea": {
        "en": ["coffee", "espresso", "barista", "tea", "matcha", "mug", "french press", "pour over", "latte"],
        "de": ["kaffee", "espresso", "barista", "tee", "matcha", "tasse", "becher", "kaffeeliebhaber"],
        "tr": ["kahve", "espresso", "barista", "çay", "matcha", "kupa", "türk kahvesi", "fincan", "kahve sever"],
        "nl": ["koffie", "espresso", "barista", "thee", "matcha", "mok", "koffieliefhebber"],
        "fr": ["café", "expresso", "barista", "thé", "matcha", "mug", "tasse", "amateur de café"],
    },
    "outdoor": {
        "en": ["outdoor", "hiking", "camping", "adventure", "trail", "nature", "backpack", "tent", "fishing"],
        "de": ["outdoor", "wandern", "camping", "abenteuer", "natur", "rucksack", "zelt", "angeln"],
        "tr": ["outdoor", "doğa", "kamp", "macera", "yürüyüş", "trekking", "sırt çantası", "çadır", "balık"],
        "nl": ["outdoor", "wandelen", "kamperen", "avontuur", "natuur", "rugzak", "tent", "vissen"],
        "fr": ["plein air", "randonnée", "camping", "aventure", "nature", "sac à dos", "tente", "pêche"],
    },
    "fitness": {
        "en": ["fitness", "gym", "workout", "running", "yoga", "cycling", "sport", "athlete", "training"],
        "de": ["fitness", "gym", "workout", "laufen", "yoga", "radfahren", "sport", "sportler", "training"],
        "tr": ["fitness", "spor", "antrenman", "koşu", "yoga", "bisiklet", "sporcu", "egzersiz"],
        "nl": ["fitness", "sportschool", "workout", "hardlopen", "yoga", "fietsen", "sport", "training"],
        "fr": ["fitness", "salle de sport", "entraînement", "course", "yoga", "vélo", "sport", "sportif"],
    },
    "bookworm": {
        "en": ["book", "books", "reader", "reading", "novel", "bookworm", "library", "bookmark", "kindle", "literature"],
        "de": ["buch", "bücher", "leser", "lesen", "roman", "leseratte", "bibliothek", "lesezeichen", "literatur"],
        "tr": ["kitap", "kitaplar", "okur", "okuma", "roman", "kitap kurdu", "kütüphane", "kitap ayracı", "edebiyat"],
        "nl": ["boek", "boeken", "lezer", "lezen", "roman", "boekenwurm", "bibliotheek", "boekenlegger"],
        "fr": ["livre", "livres", "lecteur", "lecture", "roman", "rat de bibliothèque", "marque-page", "littérature"],
    },
    "artist": {
        "en": ["art", "artist", "painting", "drawing", "sketch", "watercolor", "creative", "craft", "calligraphy"],
        "de": ["kunst", "künstler", "malen", "zeichnen", "skizze", "aquarell", "kreativ", "basteln", "kalligraphie"],
        "tr": ["sanat", "sanatçı", "resim", "çizim", "eskiz", "suluboya", "yaratıcı", "el işi", "kaligrafi"],
        "nl": ["kunst", "kunstenaar", "schilderen", "tekenen", "schets", "aquarel", "creatief", "knutselen"],
        "fr": ["art", "artiste", "peinture", "dessin", "croquis", "aquarelle", "créatif", "loisirs créatifs"],
    },
    "music": {
        "en": ["music", "vinyl", "record", "headphones", "speaker", "guitar", "piano", "concert", "musician", "playlist"],
        "de": ["musik", "vinyl", "schallplatte", "kopfhörer", "lautsprecher", "gitarre", "klavier", "konzert", "musiker"],
        "tr": ["müzik", "plak", "pikap", "kulaklık", "hoparlör", "gitar", "piyano", "konser", "müzisyen"],
        "nl": ["muziek", "vinyl", "plaat", "koptelefoon", "speaker", "gitaar", "piano", "concert", "muzikant"],
        "fr": ["musique", "vinyle", "disque", "casque", "enceinte", "guitare", "piano", "concert", "musicien"],
    },
    "traveler": {
        "en": ["travel", "traveler", "trip", "luggage", "passport", "suitcase", "wanderlust", "world map", "vacation"],
        "de": ["reise", "reisen", "reisender", "gepäck", "reisepass", "koffer", "fernweh", "weltkarte", "urlaub"],
        "tr": ["seyahat", "gezgin", "gezi", "valiz", "pasaport", "bavul", "dünya haritası", "tatil", "yolculuk"],
        "nl": ["reizen", "reiziger", "reis", "bagage", "paspoort", "koffer", "wereldkaart", "vakantie"],
        "fr": ["voyage", "voyageur", "bagage", "passeport", "valise", "carte du monde", "vacances", "globe-trotter"],
    },
    "homebody": {
        "en": ["cozy", "home", "blanket", "candle", "pajamas", "slippers", "relax", "comfort", "hygge", "lounge"],
        "de": ["gemütlich", "zuhause", "decke", "kerze", "pyjama", "hausschuhe", "entspannen", "kuschelig"],
        "tr": ["rahat", "ev", "battaniye", "mum", "pijama", "terlik", "dinlenme", "konfor", "sıcak", "keyif"],
        "nl": ["gezellig", "thuis", "deken", "kaars", "pyjama", "pantoffels", "ontspannen", "knus"],
        "fr": ["cocooning", "maison", "plaid", "bougie", "pyjama", "chaussons", "détente", "confort", "douillet"],
    },
    "fashion": {
        "en": ["fashion", "style", "jewelry", "necklace", "bracelet", "watch", "scarf", "handbag", "wallet", "elegant"],
        "de": ["mode", "stil", "schmuck", "halskette", "armband", "uhr", "schal", "handtasche", "geldbörse", "elegant"],
        "tr": ["moda", "stil", "takı", "kolye", "bileklik", "saat", "atkı", "çanta", "cüzdan", "şık"],
        "nl": ["mode", "stijl", "sieraden", "ketting", "armband", "horloge", "sjaal", "handtas", "portemonnee", "elegant"],
        "fr": ["mode", "style", "bijoux", "collier", "bracelet", "montre", "écharpe", "sac à main", "portefeuille", "élégant"],
    },
    "gardener": {
        "en": ["garden", "gardening", "plant", "plants", "seeds", "flower", "herb", "succulent", "planter", "balcony"],
        "de": ["garten", "gärtnern", "pflanze", "pflanzen", "samen", "blume", "kräuter", "sukkulente", "blumentopf", "balkon"],
        "tr": ["bahçe", "bahçecilik", "bitki", "bitkiler", "tohum", "çiçek", "saksı", "sukulent", "balkon"],
        "nl": ["tuin", "tuinieren", "plant", "planten", "zaden", "bloem", "kruiden", "vetplant", "bloempot", "balkon"],
        "fr": ["jardin", "jardinage", "plante", "plantes", "graines", "fleur", "herbes", "succulente", "pot", "balcon"],
    },
    "pet_lover": {
        "en": ["dog", "cat", "pet", "puppy", "kitten", "pet owner", "paw", "dog lover", "cat lover"],
        "de": ["hund", "katze", "haustier", "welpe", "kätzchen", "pfote", "hundebesitzer", "katzenliebhaber"],
        "tr": ["köpek", "kedi", "evcil hayvan", "yavru köpek", "yavru kedi", "pati", "kedi sever", "köpek sever"],
        "nl": ["hond", "kat", "huisdier", "puppy", "kitten", "poot", "hondenliefhebber", "kattenliefhebber"],
        "fr": ["chien", "chat", "animal de compagnie", "chiot", "chaton", "patte", "maître de chien", "amoureux des chats"],
    },
    "wellness": {
        "en": ["wellness", "spa", "self-care", "skincare", "massage", "aromatherapy", "bath", "meditation", "relaxation", "essential oil"],
        "de": ["wellness", "spa", "selbstfürsorge", "hautpflege", "massage", "aromatherapie", "bad", "meditation", "entspannung"],
        "tr": ["wellness", "spa", "kişisel bakım", "cilt bakımı", "masaj", "aromaterapi", "banyo", "meditasyon", "rahatlama"],
        "nl": ["wellness", "spa", "zelfzorg", "huidverzorging", "massage", "aromatherapie", "bad", "meditatie", "ontspanning"],
        "fr": ["bien-être", "spa", "soin de soi", "soin de la peau", "massage", "aromathérapie", "bain", "méditation", "relaxation"],
    },
    "maker": {
        "en": ["diy", "maker", "tool", "tools", "woodworking", "kit", "build", "3d print", "soldering", "workshop"],
        "de": ["diy", "heimwerker", "werkzeug", "werkzeuge", "holzarbeiten", "bausatz", "bauen", "3d-druck", "löten", "werkstatt"],
        "tr": ["kendin yap", "diy", "alet", "aletler", "ahşap işçiliği", "kit", "yapım", "3d yazıcı", "lehim", "atölye"],
        "nl": ["doe-het-zelf", "klussen", "gereedschap", "houtbewerking", "bouwpakket", "bouwen", "3d-printen", "solderen"],
        "fr": ["bricolage", "diy", "outil", "outils", "menuiserie", "kit", "construire", "impression 3d", "soudure", "atelier"],
    },
}

# Human readable UI labels per language.
UI_LABELS = {
    "female": {"en": "Her", "de": "Sie", "tr": "Kadın", "nl": "Haar", "fr": "Elle"},
    "male": {"en": "Him", "de": "Ihn", "tr": "Erkek", "nl": "Hem", "fr": "Lui"},
    "unisex": {"en": "Anyone", "de": "Egal", "tr": "Fark etmez", "nl": "Iedereen", "fr": "Peu importe"},
    "baby": {"en": "Baby (0-2)", "de": "Baby (0-2)", "tr": "Bebek (0-2)", "nl": "Baby (0-2)", "fr": "Bébé (0-2)"},
    "child": {"en": "Child (3-12)", "de": "Kind (3-12)", "tr": "Çocuk (3-12)", "nl": "Kind (3-12)", "fr": "Enfant (3-12)"},
    "teen": {"en": "Teen (13-17)", "de": "Teenager (13-17)", "tr": "Genç (13-17)", "nl": "Tiener (13-17)", "fr": "Ado (13-17)"},
    "young_adult": {"en": "Young adult (18-30)", "de": "Junger Erwachsener (18-30)", "tr": "Genç yetişkin (18-30)", "nl": "Jongvolwassene (18-30)", "fr": "Jeune adulte (18-30)"},
    "adult": {"en": "Adult (31-60)", "de": "Erwachsener (31-60)", "tr": "Yetişkin (31-60)", "nl": "Volwassene (31-60)", "fr": "Adulte (31-60)"},
    "senior": {"en": "Senior (60+)", "de": "Senior (60+)", "tr": "60 yaş üstü", "nl": "Senior (60+)", "fr": "Senior (60+)"},
    "birthday": {"en": "Birthday", "de": "Geburtstag", "tr": "Doğum günü", "nl": "Verjaardag", "fr": "Anniversaire"},
    "anniversary": {"en": "Anniversary", "de": "Jahrestag", "tr": "Yıldönümü", "nl": "Jubileum", "fr": "Anniversaire de couple"},
    "valentines": {"en": "Valentine's Day", "de": "Valentinstag", "tr": "Sevgililer Günü", "nl": "Valentijnsdag", "fr": "Saint-Valentin"},
    "christmas": {"en": "Christmas / New Year", "de": "Weihnachten", "tr": "Yılbaşı", "nl": "Kerst / Sinterklaas", "fr": "Noël"},
    "mothers_day": {"en": "Mother's Day", "de": "Muttertag", "tr": "Anneler Günü", "nl": "Moederdag", "fr": "Fête des mères"},
    "fathers_day": {"en": "Father's Day", "de": "Vatertag", "tr": "Babalar Günü", "nl": "Vaderdag", "fr": "Fête des pères"},
    "wedding": {"en": "Wedding", "de": "Hochzeit", "tr": "Düğün", "nl": "Bruiloft", "fr": "Mariage"},
    "graduation": {"en": "Graduation", "de": "Abschluss", "tr": "Mezuniyet", "nl": "Afstuderen", "fr": "Diplôme"},
    "new_baby": {"en": "New baby", "de": "Geburt", "tr": "Yeni bebek", "nl": "Kraamcadeau", "fr": "Naissance"},
    "housewarming": {"en": "Housewarming", "de": "Einzug", "tr": "Yeni ev", "nl": "Housewarming", "fr": "Crémaillère"},
    "retirement": {"en": "Retirement", "de": "Ruhestand", "tr": "Emeklilik", "nl": "Pensioen", "fr": "Retraite"},
    "get_well": {"en": "Get well", "de": "Gute Besserung", "tr": "Geçmiş olsun", "nl": "Beterschap", "fr": "Rétablissement"},
    "thank_you": {"en": "Thank you", "de": "Dankeschön", "tr": "Teşekkür", "nl": "Bedankje", "fr": "Merci"},
    "tech": {"en": "Tech lover", "de": "Technikfan", "tr": "Teknoloji meraklısı", "nl": "Techliefhebber", "fr": "Geek"},
    "gamer": {"en": "Gamer", "de": "Gamer", "tr": "Oyuncu", "nl": "Gamer", "fr": "Gamer"},
    "foodie": {"en": "Foodie", "de": "Feinschmecker", "tr": "Gurme", "nl": "Foodie", "fr": "Gourmet"},
    "coffee_tea": {"en": "Coffee & tea", "de": "Kaffee & Tee", "tr": "Kahve & çay", "nl": "Koffie & thee", "fr": "Café & thé"},
    "outdoor": {"en": "Outdoor", "de": "Outdoor", "tr": "Doğa / kamp", "nl": "Outdoor", "fr": "Plein air"},
    "fitness": {"en": "Fitness", "de": "Fitness", "tr": "Spor", "nl": "Fitness", "fr": "Sport"},
    "bookworm": {"en": "Bookworm", "de": "Leseratte", "tr": "Kitap kurdu", "nl": "Boekenwurm", "fr": "Lecteur"},
    "artist": {"en": "Artist", "de": "Künstler", "tr": "Sanatçı", "nl": "Creatieveling", "fr": "Artiste"},
    "music": {"en": "Music", "de": "Musik", "tr": "Müzik", "nl": "Muziek", "fr": "Musique"},
    "traveler": {"en": "Traveler", "de": "Reisender", "tr": "Gezgin", "nl": "Reiziger", "fr": "Voyageur"},
    "homebody": {"en": "Homebody", "de": "Gemütlich", "tr": "Ev insanı", "nl": "Huismus", "fr": "Cocooning"},
    "fashion": {"en": "Fashion", "de": "Mode", "tr": "Moda", "nl": "Mode", "fr": "Mode"},
    "gardener": {"en": "Gardener", "de": "Gärtner", "tr": "Bahçe", "nl": "Tuinier", "fr": "Jardinier"},
    "pet_lover": {"en": "Pet lover", "de": "Tierfreund", "tr": "Hayvansever", "nl": "Dierenvriend", "fr": "Ami des animaux"},
    "wellness": {"en": "Wellness", "de": "Wellness", "tr": "Wellness", "nl": "Wellness", "fr": "Bien-être"},
    "maker": {"en": "Maker / DIY", "de": "Heimwerker", "tr": "Kendin yap", "nl": "Klusser", "fr": "Bricoleur"},
}

FACET_TITLES = {
    "gender": {"en": "Who is it for?", "de": "Für wen?", "tr": "Kimin için?", "nl": "Voor wie?", "fr": "Pour qui ?"},
    "age": {"en": "Age", "de": "Alter", "tr": "Yaş", "nl": "Leeftijd", "fr": "Âge"},
    "occasion": {"en": "Occasion", "de": "Anlass", "tr": "Özel gün", "nl": "Gelegenheid", "fr": "Occasion"},
    "personality": {"en": "Personality", "de": "Persönlichkeit", "tr": "Karakter", "nl": "Persoonlijkheid", "fr": "Personnalité"},
}


# Languages added from app/i18n/<lang>.json (pl, it, es, sv, fi, pt, da, ro ...).
from .i18n import LANGS as _ADDED  # noqa: E402

for _lang, _d in _ADDED.items():
    if _lang not in LANGS:
        LANGS.append(_lang)
    for _l, _ws in _d.get("lexicon", {}).items():
        if _l in LEXICON:
            LEXICON[_l][_lang] = [w.strip("*").strip().lower() for w in _ws if w.strip("*").strip()]
    for _l, _t in _d.get("ui_labels", {}).items():
        if _l in UI_LABELS:
            UI_LABELS[_l][_lang] = _t
    for _f, _t in _d.get("facet_titles", {}).items():
        if _f in FACET_TITLES:
            FACET_TITLES[_f][_lang] = _t

def all_labels():
    return [label for labels in FACETS.values() for label in labels]


def facet_of(label):
    for facet, labels in FACETS.items():
        if label in labels:
            return facet
    raise KeyError(label)
