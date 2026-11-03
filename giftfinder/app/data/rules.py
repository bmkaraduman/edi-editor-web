"""Hand-written labelling rules: shop categories, keywords and product names -> facets.

Affiliate feeds carry no gift facets, but they do carry categories ("Wine, Spirits
& Tobacco > Wine", "Kinder > Kinderstrumpfhosen", "Men's Watches"), product types
and keywords. Those fields are far more reliable than a description that happens
to mention "schwarzer Tee" in a perfume's scent notes, so the rules below run on
the *strong* text only (title + category path + product type + keywords + brand)
and take precedence over the lexicon and the classifier.

Every rule has
  patterns  normalised phrases (see app/ml/preprocess.normalize). A trailing "*"
            matches a token prefix, which is how German compounds are caught
            ("herren*" -> Herrensocken, Herrenuhr, Herrenduft).
  labels    facet -> labels to assign
  gift      giftability prior in 0..1. 1 = classic present, 0.05 = office supply
            or spare part that should only appear when someone searches for it.
            The ranker multiplies by it and hides anything below GIFT_FLOOR
            from pure filter searches.

Add a rule when a merchant's category keeps producing odd results; the ids show up
in the product's "rules" field and on the detail page, so mistakes are traceable.
"""
from ..ml.preprocess import normalize

GIFT_FLOOR = 0.15


def R(rid, patterns, gift=0.8, **labels):
    return {"id": rid, "patterns": [normalize(p.rstrip("*")) + ("*" if p.endswith("*") else "") for p in patterns],
            "labels": {k: v for k, v in labels.items()}, "gift": gift}


RULES = [
    # ------------------------------------------------------------- who it is for
    R("for_him", ["herren*", "manner*", "männer*", "fur ihn", "for him", "men's", "mens", "men", "homme*", "heren*", "erkek*", "boyfriend", "husband", "ehemann", "vatertag*", "father's day"],
      gender=["male"]),
    R("for_her", ["damen*", "frauen*", "fur sie", "for her", "women's", "womens", "women", "ladies", "femme*", "dames*", "kadin*", "girlfriend", "wife", "ehefrau", "muttertag*", "mother's day"],
      gender=["female"]),
    R("kids", ["kinder*", "kids", "kid", "child*", "enfant*", "cocuk*", "jungen", "madchen", "boys", "girls", "spielzeug*", "toys", "toy"],
      age=["child"], gift=0.9),
    R("baby", ["baby*", "babies", "neugeboren*", "newborn", "bebe*", "bebek*", "sauglinge", "kleinkind*", "toddler"],
      age=["baby"], occasion=["new_baby"], gift=0.9),
    R("teen", ["teen*", "jugend*", "youth", "ado", "genc*"], age=["teen"]),
    R("senior", ["senior*", "rentner*", "ruhestand", "retirement", "grosseltern", "oma", "opa", "grandma", "grandpa", "grandparent*"],
      age=["senior"], occasion=["retirement"]),

    # ------------------------------------------------------------- food & drink
    R("wine", ["wein", "weine", "rotwein*", "weisswein*", "rosewein*", "wine", "wines", "vino", "sekt", "champagner", "champagne", "prosecco", "cava", "spirituosen", "spirits", "whisky", "whiskey", "gin", "rum", "likor*", "liqueur", "cognac", "vodka", "wodka", "sarap*", "wijn", "vin", "vins"],
      personality=["foodie"], age=["adult", "senior"], occasion=["christmas", "anniversary", "thank_you", "housewarming"], gift=1.0),
    R("gourmet", ["feinkost", "delikatess*", "gourmet", "olivenol", "olive oil", "schokolade", "chocolate", "pralinen", "gewurz*", "spices", "spice", "sauce", "hot sauce", "chili", "honig", "honey", "kase", "cheese", "grill*", "bbq", "barbecue", "kochen", "cooking", "kuchen*", "kitchen", "backen", "baking"],
      personality=["foodie"], gift=0.9),
    R("coffee_tea", ["kaffee*", "coffee", "espresso", "barista", "tee", "tea", "teekanne", "teapot", "matcha", "cay", "koffie", "thee", "cafe"],
      personality=["coffee_tea", "homebody"], gift=0.9),

    # ------------------------------------------------------------- beauty & wellness
    R("perfume", ["parfum*", "parfüm*", "perfume*", "fragrance*", "duft*", "eau de parfum", "eau de toilette", "decant*", "abfullung*", "cologne"],
      personality=["fashion", "wellness"], occasion=["birthday", "valentines", "christmas", "anniversary"], gift=1.0),
    R("skincare", ["pflege*", "skincare", "hautpflege", "kosmetik*", "cosmetic*", "beauty", "make-up", "makeup", "lippenstift", "lipstick", "nagel*", "nail", "bodylotion", "body lotion", "creme", "cream", "serum", "maske"],
      personality=["wellness", "fashion"], gift=0.85),
    R("spa", ["spa", "wellness", "massage*", "sauna", "aromatherap*", "duftkerze*", "scented candle*", "candle*", "kerze*", "badezusatz", "bath bomb*", "badebombe*", "yoga", "meditation*", "entspannung*", "relax*"],
      personality=["wellness", "homebody"], occasion=["get_well", "mothers_day"], gift=0.9),
    R("health_device", ["blutzucker*", "blood glucose", "blutdruck*", "blood pressure", "thermometer", "medizin*", "medical", "pflaster", "bandage*", "zahnbleaching", "teeth whitening", "zahnpflege", "oral health", "vitamin*", "nahrungserganzung*", "supplement*"],
      personality=["wellness"], occasion=["get_well"], gift=0.3),

    # ------------------------------------------------------------- fashion & accessories
    R("jewellery", ["schmuck*", "jewel*", "halskette*", "necklace*", "armband*", "bracelet*", "ohrring*", "earring*", "ring", "ringe", "anhanger", "pendant*", "sterling silber", "sterling silver", "gold", "takı", "sieraden", "bijou*"],
      personality=["fashion"], occasion=["birthday", "valentines", "anniversary", "christmas", "mothers_day"], gift=1.0),
    R("watch", ["uhr", "uhren", "armbanduhr*", "watch", "watches", "chronograph*", "saat", "horloge*", "montre*"],
      personality=["fashion"], occasion=["birthday", "graduation", "anniversary", "christmas"], gift=1.0),
    R("smartwatch", ["smartwatch*", "smart watch*", "fitness tracker*", "fitnesstracker*", "scanwatch*", "apple watch*", "garmin*"],
      personality=["tech", "fitness"], occasion=["birthday", "christmas"], gift=0.95),
    R("cufflinks", ["manschettenknopf*", "manschettenknöpfe", "cufflink*", "krawatte*", "tie", "fliege", "bow tie*", "kol dugme*"],
      gender=["male"], personality=["fashion"], occasion=["wedding", "graduation", "fathers_day", "anniversary"], gift=0.95),
    R("socks", ["socken*", "strumpf*", "strumpfe", "strumpfhose*", "tights", "stockings", "socks", "sock", "halterlos*", "kniestrumpf*", "corap*", "sokken", "chaussettes"],
      personality=["fashion", "homebody"], occasion=["christmas", "birthday"], gift=0.7),
    R("apparel", ["bekleidung", "kleidung", "clothes", "clothing", "apparel", "t-shirt*", "tshirt*", "shirt*", "hoodie*", "pullover*", "sweater*", "jacke*", "jacket*", "mutze*", "beanie*", "cap", "schal", "scarf", "handschuhe", "gloves", "kleid", "dress"],
      personality=["fashion"], gift=0.7),
    R("bags", ["tasche*", "bag", "bags", "rucksack*", "backpack*", "geldborse*", "portemonnaie*", "wallet*", "brieftasche*", "gurtel", "belt", "sonnenbrille*", "sunglasses"],
      personality=["fashion", "traveler"], gift=0.85),
    R("personalised", ["personalisiert*", "personalised", "personalized", "custom", "gravur*", "engraved", "graviert*", "foto projektion*", "photo projection*", "mit namen", "with name", "namens*"],
      occasion=["birthday", "anniversary", "valentines", "christmas", "mothers_day", "fathers_day"], gift=1.0),

    # ------------------------------------------------------------- hobbies
    R("fishing", ["angel*", "angeln", "fishing", "fish", "karpfen*", "carp", "koder", "lure*", "rute*", "rod", "rods", "rolle", "reel", "tackle", "haken", "hooks", "balik*", "vissen", "peche"],
      personality=["outdoor"], gender=["male"], occasion=["fathers_day", "birthday"], gift=0.8),
    R("fishing_parts", ["haken", "hooks", "hook", "vorfach*", "leader*", "montage*", "rig", "rigs", "wirbel", "swivel*", "blei", "sinker*", "schnur", "line", "braid*", "geflochten*", "knicklicht*", "pose", "posen", "float", "floats", "futter", "boilie*", "pellet*", "feeder"],
      personality=["outdoor"], gift=0.3),
    R("outdoor", ["outdoor*", "camping*", "wandern*", "hiking", "trekking*", "zelt", "tent", "jagd*", "hunting", "wildkamera*", "trail camera*", "fernglas*", "binocular*", "taschenlampe*", "flashlight*", "stirnlampe*", "headlamp*", "survival*", "multitool*", "multi-tool*", "garten*", "garden*"],
      personality=["outdoor"], gift=0.85),
    R("garden", ["garten*", "garden*", "gardening", "pflanze*", "plant", "plants", "blumentopf*", "planter*", "samen", "seeds", "bonsai", "gewachshaus*", "greenhouse*", "giesskanne*", "watering can*", "bahce*", "tuin*", "jardin*"],
      personality=["gardener", "outdoor"], occasion=["housewarming", "retirement"], gift=0.85),
    R("sports", ["sport*", "fitness*", "training*", "gym", "yoga*", "laufen", "running", "fahrrad*", "bike", "bicycle", "cycling", "radsport*", "fussball*", "football", "soccer", "tennis", "golf", "schwimm*", "swim*", "ski*", "hantel*", "dumbbell*", "massagepistole*", "massage gun*"],
      personality=["fitness", "outdoor"], gift=0.85),
    R("model_kit", ["modellbau*", "model kit*", "bausatz*", "revell", "tamiya", "plastikmodell*", "scale model*", "1:72", "1:35", "1:24", "1:48", "rc modell*", "rc car*", "rc-", "ferngesteuert*", "remote control*", "lego", "klemmbaustein*", "puzzle*", "brettspiel*", "board game*"],
      personality=["maker", "gamer"], age=["teen", "adult"], occasion=["birthday", "christmas"], gift=0.9),
    R("model_supplies", ["modellbauzubehor", "modellbaufarbe*", "polystyrol*", "styrene", "airbrush*", "klebstoff*", "glue", "farben & werkzeuge", "paints & tools", "pinsel", "brushes", "decal*", "ersatzteil*", "spare part*", "zubehor"],
      personality=["maker"], gift=0.3),
    R("crafts", ["basteln", "bastel*", "crafts", "craft", "handarbeit*", "handmade", "handgemacht", "diy", "nahen", "sewing", "stricken", "knitting", "wolle", "yarn", "malen", "painting", "zeichnen", "drawing", "kunst", "art", "artist*", "kreativ*", "creative"],
      personality=["artist", "maker"], gift=0.85),
    R("books", ["buch", "bucher", "book", "books", "roman", "novel", "e-book*", "ebook*", "horbuch*", "audiobook*", "lesen", "reading", "kitap*", "boek*", "livre*", "notizbuch*", "notebook", "journal", "tagebuch*", "diary"],
      personality=["bookworm"], gift=0.85),
    R("music", ["musik*", "music", "kopfhorer*", "headphone*", "earbuds", "lautsprecher*", "speaker*", "vinyl", "schallplatte*", "record player*", "plattenspieler*", "gitarre*", "guitar*", "piano*", "klavier*", "ukulele*", "muzik*", "muziek*", "musique*"],
      personality=["music", "tech"], gift=0.9),
    R("gaming", ["gaming*", "gamer*", "videospiel*", "video game*", "konsole*", "console*", "playstation*", "xbox*", "nintendo*", "switch spiel*", "controller", "headset", "maus", "mouse", "tastatur", "keyboard", "oyun*", "spel", "jeu*"],
      personality=["gamer", "tech"], age=["teen", "young_adult"], gift=0.9),
    R("tech_gadget", ["gadget*", "smartphone*", "handy*", "tablet*", "smart home*", "smart-home*", "kamera*", "camera*", "drohne*", "drone*", "powerbank*", "power bank*", "ladegerat*", "charger*", "bluetooth*", "projektor*", "projector*", "e-reader*", "kindle*", "roboter*", "robot*", "3d-drucker*", "3d printer*"],
      personality=["tech"], gift=0.85),
    R("pets", ["hund*", "dog", "dogs", "katze*", "cat", "cats", "haustier*", "pet", "pets", "hundehalsband*", "leine", "leash", "kratzbaum*", "aquarium*", "vogel*", "bird*", "futter", "kopek*", "kedi*", "hond*", "chien*"],
      personality=["pet_lover"], gift=0.85),
    R("travel", ["reise*", "travel*", "koffer*", "suitcase*", "luggage*", "trolley*", "reisetasche*", "weekender*", "passport*", "reisepass*", "weltkarte*", "world map*", "scratch map*", "rubbel*", "seyahat*", "reizen*", "voyage*"],
      personality=["traveler"], gift=0.9),
    R("home_decor", ["deko*", "decor*", "wohnaccessoire*", "home accessories", "vase*", "bilderrahmen*", "picture frame*", "poster*", "wandbild*", "wall art*", "kissen*", "cushion*", "pillow*", "decke", "blanket*", "heizdecke*", "lampe*", "lamp", "leuchte*", "ambiente*"],
      personality=["homebody"], occasion=["housewarming", "christmas"], gift=0.85),
    R("home_kitchen", ["home & garden", "haus & garten", "haushalt*", "household", "bathroom accessor*", "badezimmer*", "seifenspender*", "soap dispenser*", "kuche", "tableware", "geschirr*", "glaser", "glasses", "tasse*", "mug", "mugs", "flasche*", "bottle*", "karaffe*", "decanter*"],
      personality=["homebody", "foodie"], occasion=["housewarming"], gift=0.7),
    R("furniture", ["mobel", "möbel", "furniture", "tisch", "tische", "table", "stuhl*", "chair*", "sofa*", "couch*", "regal*", "shelf", "shelves", "schrank*", "cabinet*", "bett*", "bed", "nachttisch*", "nightstand*", "sideboard*", "kommode*"],
      personality=["homebody"], occasion=["housewarming"], gift=0.3),
    R("lighting_parts", ["led streifen*", "led strip*", "led controller*", "dmx*", "netzteil*", "power supply*", "trafo*", "transformer*", "dimmer*", "relais*", "relay*", "repeater*", "zigbee*", "leuchtmittel*", "light bulb*", "led modul*", "led profil*"],
      personality=["tech", "maker"], gift=0.1),

    # ------------------------------------------------------------- not a present
    R("office", ["office supplies", "buro*", "büro*", "burobedarf*", "schreibwaren*", "stationery", "ordner", "folder*", "toner*", "druckerpatrone*", "ink cartridge*", "kopierpapier*", "copy paper*", "etiketten", "labels", "haftnotiz*", "sticky note*", "whiteboard*", "weisswandtafel*", "flipchart*", "aktenvernichter*", "shredder*", "locher", "hefter", "stapler*", "restposten*", "clearance", "postausgangsbuch*", "formular*"],
      gift=0.05),
    R("network", ["netzwerk*", "network*", "patchkabel*", "patch cable*", "ethernet*", "lan-kabel*", "cat5*", "cat6*", "cat7*", "cat8*", "switch", "router*", "adapter*", "konverter*", "converter*", "kabel", "cable", "cables", "usb-c*", "hdmi*", "steckdose*", "stecker*", "plug", "rj45*", "glasfaser*", "fiber*", "server*", "rack*", "patchpanel*"],
      personality=["tech"], gift=0.05),
    R("machinery", ["motor*", "kleinmotor*", "engine*", "ersatzmotor*", "sprüher*", "spruher*", "sprayer*", "pumpe*", "pump", "maschine*", "machine*", "werkzeug*", "power tool*", "bohrmaschine*", "drill*", "sage", "saw", "industrie*", "industrial*"],
      personality=["maker", "gardener"], gift=0.2),
    R("writing_set", ["schreibgerate-set*", "schreibset*", "pen set*", "fuller*", "fountain pen*", "kugelschreiber*", "ballpoint*", "parker", "lamy", "montblanc", "cross pen*", "füllhalter*"],
      personality=["bookworm", "artist"], occasion=["graduation", "retirement", "thank_you"], gift=0.9),
]

# Umbrella category names that would trigger the wrong hobby rule ("Home & Garden" is not
# gardening, it is where soap dispensers live). Removed from the text before matching.
NEUTRAL = [normalize(x) for x in ("home & garden", "haus & garten", "home and garden", "home, garden", "garden & outdoor")]

_INDEX = [(r, [(p[:-1], True) if p.endswith("*") else (p, False) for p in r["patterns"]]) for r in RULES]


def match_rules(strong_text):
    """Return (labels, rule ids, gift) for the normalised strong text of a product.

    gift is the minimum of the matched rules' priors, so one "office" hit outweighs a
    hobby hit (an "Angler-Kalender" sold under Büro is still office stock) -- unless a
    rule with a prior >= 0.9 matched (a Parker pen set sold under office supplies is
    still a present), in which case that strong rule wins."""
    for phrase in NEUTRAL:
        strong_text = strong_text.replace(phrase, "home")
    padded = f" {strong_text} "
    toks = strong_text.split()
    labels, hit, gift = {}, [], None
    for rule, pats in _INDEX:
        ok = False
        for pat, prefix in pats:
            if prefix:
                if pat and any(t.startswith(pat) for t in toks):
                    ok = True
                    break
            elif f" {pat} " in padded:
                ok = True
                break
        if not ok:
            continue
        hit.append(rule["id"])
        if rule["gift"] >= 0.9 or (gift is not None and gift >= 0.9):
            gift = max(gift or 0.0, rule["gift"])
        else:
            gift = rule["gift"] if gift is None else min(gift, rule["gift"])
        for facet, ls in rule["labels"].items():
            for l in ls:
                if l not in labels.setdefault(facet, []):
                    labels[facet].append(l)
    return labels, hit, (0.5 if gift is None else gift)
