"""Labelled gift concepts in five languages.

This is the hand-labelled core of the training set. Each concept carries the
facet labels and a (title, description) pair per language. The seed builder
turns every concept into several merchant listings per country and augments
the text so the classifier sees varied phrasing.
"""

CONCEPTS = []


def c(cid, gender, age, occasion, personality, price, emoji, en, de, tr, nl, fr):
    CONCEPTS.append({
        "id": cid, "gender": gender, "age": age, "occasion": occasion,
        "personality": personality, "price_usd": price, "emoji": emoji,
        "text": {"en": en, "de": de, "tr": tr, "nl": nl, "fr": fr},
    })


# ---------------------------------------------------------------- tech / gamer
c("wireless_earbuds", "unisex", ["teen", "young_adult", "adult"], ["birthday", "christmas", "graduation"], ["tech", "music", "fitness"], (40, 180), "🎧",
  ("Wireless Noise-Cancelling Earbuds", "Bluetooth 5.3 earbuds with active noise cancelling, 30-hour battery and a wireless charging case. Great for commuting, workouts and calls."),
  ("Kabellose In-Ear-Kopfhörer mit Noise Cancelling", "Bluetooth-5.3-Ohrhörer mit aktiver Geräuschunterdrückung, 30 Stunden Akkulaufzeit und kabellosem Ladecase. Ideal für Pendeln, Sport und Telefonate."),
  ("Kablosuz Gürültü Önleyici Kulaklık", "Aktif gürültü engelleme, 30 saat pil ömrü ve kablosuz şarj kutusu olan Bluetooth 5.3 kulak içi kulaklık. Yolculuk, spor ve görüşmeler için ideal."),
  ("Draadloze oordopjes met noise cancelling", "Bluetooth 5.3 oordopjes met actieve ruisonderdrukking, 30 uur batterij en een draadloze oplaadcase. Fijn voor woon-werkverkeer, sporten en bellen."),
  ("Écouteurs sans fil à réduction de bruit", "Écouteurs Bluetooth 5.3 avec réduction de bruit active, 30 heures d'autonomie et boîtier de charge sans fil. Parfaits pour les trajets, le sport et les appels."))

c("smart_speaker", "unisex", ["young_adult", "adult", "senior"], ["christmas", "housewarming", "birthday"], ["tech", "music", "homebody"], (35, 120), "🔊",
  ("Smart Speaker with Voice Assistant", "Compact smart speaker with rich sound, voice control for music, timers and smart home devices. A practical gadget for any room."),
  ("Smarter Lautsprecher mit Sprachassistent", "Kompakter Smart Speaker mit sattem Klang, Sprachsteuerung für Musik, Timer und Smart-Home-Geräte. Praktisches Gadget für jeden Raum."),
  ("Sesli Asistanlı Akıllı Hoparlör", "Zengin ses, müzik ve akıllı ev cihazları için sesli kontrol sunan kompakt akıllı hoparlör. Her oda için pratik bir teknolojik hediye."),
  ("Slimme speaker met spraakassistent", "Compacte smart speaker met vol geluid, spraakbediening voor muziek, timers en slimme apparaten. Een handige gadget voor elke kamer."),
  ("Enceinte connectée avec assistant vocal", "Enceinte intelligente compacte au son riche, commande vocale pour la musique, les minuteurs et la maison connectée. Un gadget pratique pour toutes les pièces."))

c("power_bank", "unisex", ["teen", "young_adult", "adult"], ["birthday", "christmas", "graduation"], ["tech", "traveler"], (20, 60), "🔋",
  ("20000mAh Fast-Charging Power Bank", "Slim portable charger with USB-C power delivery that fills a phone three times. A must-have for travel and long days out."),
  ("20000mAh Powerbank mit Schnellladung", "Schlankes mobiles Ladegerät mit USB-C Power Delivery, lädt ein Smartphone dreimal voll. Unverzichtbar für Reisen und lange Tage unterwegs."),
  ("20000mAh Hızlı Şarj Powerbank", "Telefonu üç kez dolduran USB-C hızlı şarj destekli ince taşınabilir şarj cihazı. Seyahat ve uzun günler için vazgeçilmez."),
  ("20000mAh powerbank met snelladen", "Slanke powerbank met USB-C Power Delivery die een telefoon drie keer oplaadt. Onmisbaar op reis en tijdens lange dagen."),
  ("Batterie externe 20000mAh à charge rapide", "Chargeur portable fin avec USB-C Power Delivery, recharge un téléphone trois fois. Indispensable en voyage et pour les longues journées."))

c("mechanical_keyboard", "unisex", ["teen", "young_adult", "adult"], ["birthday", "christmas"], ["gamer", "tech"], (60, 150), "⌨️",
  ("RGB Mechanical Gaming Keyboard", "Compact 75% mechanical keyboard with hot-swappable switches, per-key RGB lighting and a braided cable. Built for gamers and typists."),
  ("Mechanische RGB-Gaming-Tastatur", "Kompakte 75%-Mechanik-Tastatur mit austauschbaren Switches, RGB-Beleuchtung pro Taste und Textilkabel. Für Gamer und Vielschreiber."),
  ("RGB Mekanik Oyuncu Klavyesi", "Değiştirilebilir switch, tuş başına RGB aydınlatma ve örgü kablolu kompakt %75 mekanik klavye. Oyuncular ve çok yazanlar için."),
  ("Mechanisch RGB gaming toetsenbord", "Compact 75% mechanisch toetsenbord met verwisselbare switches, RGB-verlichting per toets en gevlochten kabel. Gemaakt voor gamers."),
  ("Clavier mécanique gaming RGB", "Clavier mécanique compact 75% avec switches interchangeables, rétroéclairage RGB par touche et câble tressé. Conçu pour les gamers."))

c("gaming_headset", "unisex", ["teen", "young_adult"], ["birthday", "christmas"], ["gamer", "tech"], (40, 130), "🎮",
  ("Wireless Gaming Headset", "Low-latency wireless headset with 7.1 surround sound and a detachable noise-cancelling microphone. Compatible with PC, PlayStation and Nintendo Switch."),
  ("Kabelloses Gaming-Headset", "Latenzarmes Wireless-Headset mit 7.1-Surround-Sound und abnehmbarem Mikrofon. Kompatibel mit PC, PlayStation und Nintendo Switch."),
  ("Kablosuz Oyuncu Kulaklığı", "7.1 surround ses ve çıkarılabilir gürültü önleyici mikrofonlu düşük gecikmeli kablosuz kulaklık. PC, PlayStation ve Nintendo Switch ile uyumlu."),
  ("Draadloze gaming headset", "Draadloze headset met lage latentie, 7.1 surround sound en afneembare microfoon. Werkt met pc, PlayStation en Nintendo Switch."),
  ("Casque gaming sans fil", "Casque sans fil à faible latence avec son surround 7.1 et micro antibruit détachable. Compatible PC, PlayStation et Nintendo Switch."))

c("retro_console", "unisex", ["child", "teen", "young_adult", "adult"], ["birthday", "christmas", "fathers_day"], ["gamer", "tech"], (30, 90), "🕹️",
  ("Retro Handheld Game Console", "Pocket-sized retro console preloaded with hundreds of classic arcade and 8-bit games. Nostalgic fun for gamers of every age."),
  ("Retro-Handheld-Spielkonsole", "Taschenkonsole mit Hunderten klassischer Arcade- und 8-Bit-Spiele vorinstalliert. Nostalgischer Spielspaß für Gamer jeden Alters."),
  ("Retro El Oyun Konsolu", "Yüzlerce klasik arcade ve 8-bit oyun yüklü cep boyutunda retro konsol. Her yaştan oyuncu için nostaljik eğlence."),
  ("Retro handheld spelcomputer", "Zakformaat retro console met honderden klassieke arcade- en 8-bit games. Nostalgisch plezier voor gamers van elke leeftijd."),
  ("Console de jeu rétro portable", "Console rétro de poche avec des centaines de jeux d'arcade et 8 bits préinstallés. Plaisir nostalgique pour les joueurs de tout âge."))

c("smartwatch_fitness", "unisex", ["young_adult", "adult", "senior"], ["birthday", "christmas", "fathers_day", "mothers_day"], ["fitness", "tech"], (40, 250), "⌚",
  ("Fitness Smartwatch with Heart Rate & GPS", "Tracks steps, sleep, heart rate and 100+ sport modes with built-in GPS. Water resistant, 10-day battery, works with iPhone and Android."),
  ("Fitness-Smartwatch mit Pulsmesser & GPS", "Erfasst Schritte, Schlaf, Herzfrequenz und über 100 Sportmodi mit integriertem GPS. Wasserdicht, 10 Tage Akku, für iPhone und Android."),
  ("Nabız ve GPS'li Fitness Akıllı Saat", "Adım, uyku, nabız ve 100'den fazla spor modunu dahili GPS ile takip eder. Suya dayanıklı, 10 gün pil, iPhone ve Android uyumlu."),
  ("Fitness smartwatch met hartslag en GPS", "Meet stappen, slaap, hartslag en 100+ sportmodi met ingebouwde GPS. Waterdicht, 10 dagen batterij, werkt met iPhone en Android."),
  ("Montre connectée fitness avec cardio et GPS", "Suit les pas, le sommeil, la fréquence cardiaque et plus de 100 sports avec GPS intégré. Étanche, 10 jours d'autonomie, compatible iPhone et Android."))

c("instant_camera", "unisex", ["teen", "young_adult"], ["birthday", "christmas", "graduation", "wedding"], ["artist", "traveler", "tech"], (70, 130), "📸",
  ("Instant Camera with Film Pack", "Point-and-shoot instant camera that prints credit-card-sized photos on the spot. Includes a 20-sheet film pack and a carry strap."),
  ("Sofortbildkamera mit Filmpaket", "Sofortbildkamera, die Fotos im Scheckkartenformat direkt ausdruckt. Inklusive 20er-Filmpaket und Tragegurt."),
  ("Şipşak Fotoğraf Makinesi ve Film Paketi", "Kredi kartı boyutunda fotoğrafları anında basan şipşak kamera. 20 yapraklık film paketi ve askı dahildir."),
  ("Instax camera met filmpakket", "Instantcamera die foto's op creditcardformaat direct afdrukt. Inclusief 20 vellen film en een draagriem."),
  ("Appareil photo instantané avec pack de films", "Appareil instantané qui imprime des photos format carte de crédit sur-le-champ. Livré avec 20 films et une dragonne."))

c("ereader", "unisex", ["young_adult", "adult", "senior"], ["birthday", "christmas", "retirement", "mothers_day"], ["bookworm", "tech", "traveler"], (90, 200), "📖",
  ("6-inch E-Reader with Warm Light", "Glare-free e-ink reader with adjustable warm light, waterproof body and weeks of battery life. Holds thousands of books."),
  ("6-Zoll-eBook-Reader mit warmem Licht", "Blendfreier E-Ink-Reader mit einstellbarem warmem Licht, wasserdichtem Gehäuse und wochenlanger Akkulaufzeit. Platz für Tausende Bücher."),
  ("6 inç Sıcak Işıklı E-Kitap Okuyucu", "Ayarlanabilir sıcak ışık, suya dayanıklı gövde ve haftalarca pil ömrüne sahip yansımasız e-mürekkep okuyucu. Binlerce kitap sığar."),
  ("6-inch e-reader met warm licht", "Reflectievrije e-ink reader met instelbaar warm licht, waterdichte behuizing en wekenlange batterij. Ruimte voor duizenden boeken."),
  ("Liseuse 6 pouces avec lumière chaude", "Liseuse e-ink sans reflets, lumière chaude réglable, boîtier étanche et des semaines d'autonomie. Contient des milliers de livres."))

c("digital_frame", "unisex", ["adult", "senior"], ["mothers_day", "fathers_day", "christmas", "retirement", "anniversary"], ["homebody", "tech"], (60, 180), "🖼️",
  ("Wi-Fi Digital Photo Frame", "10-inch HD frame that family can send photos to from their phones anywhere in the world. Perfect for grandparents who love seeing the kids."),
  ("WLAN-Digitaler Bilderrahmen", "10-Zoll-HD-Rahmen, an den die Familie von überall Fotos vom Handy schicken kann. Perfekt für Oma und Opa, die die Enkel sehen möchten."),
  ("Wi-Fi Dijital Fotoğraf Çerçevesi", "Ailenin dünyanın her yerinden telefondan fotoğraf gönderebildiği 10 inç HD çerçeve. Torunlarını görmeyi seven büyükanne ve büyükbabalar için ideal."),
  ("Digitale fotolijst met wifi", "10-inch HD-lijst waar familie vanaf hun telefoon foto's naartoe stuurt, waar ook ter wereld. Perfect voor opa en oma."),
  ("Cadre photo numérique Wi-Fi", "Cadre HD 10 pouces sur lequel la famille envoie des photos depuis son téléphone, où qu'elle soit. Idéal pour les grands-parents."))

# ---------------------------------------------------------------- food / drink
c("gourmet_chocolate_box", "unisex", ["young_adult", "adult", "senior"], ["valentines", "mothers_day", "thank_you", "christmas", "birthday"], ["foodie"], (20, 60), "🍫",
  ("Artisan Chocolate Truffle Gift Box", "Assortment of 24 handmade truffles with dark, milk and salted caramel flavours in an elegant gift box with ribbon."),
  ("Handgemachte Pralinen in Geschenkbox", "24 handgemachte Trüffel mit Zartbitter-, Vollmilch- und Salzkaramell-Füllung in einer eleganten Geschenkbox mit Schleife."),
  ("El Yapımı Çikolata Trüf Hediye Kutusu", "Bitter, sütlü ve tuzlu karamel aromalı 24 el yapımı trüf, kurdeleli şık hediye kutusunda."),
  ("Ambachtelijke chocoladetruffels in cadeaudoos", "24 handgemaakte truffels met pure, melk- en gezouten karamelsmaak in een elegante geschenkdoos met lint."),
  ("Coffret de truffes au chocolat artisanales", "Assortiment de 24 truffes faites main aux saveurs noir, lait et caramel salé dans un élégant coffret cadeau avec ruban."))

c("hot_sauce_set", "male", ["young_adult", "adult"], ["fathers_day", "birthday", "christmas"], ["foodie"], (18, 45), "🌶️",
  ("Hot Sauce Tasting Set", "Six small-batch hot sauces from mild to extreme heat, with tasting notes. A fiery gift for the spice lover who puts chilli on everything."),
  ("Hot-Sauce-Probierset", "Sechs Chilisaucen aus kleinen Chargen von mild bis extrem scharf, mit Verkostungsnotizen. Ein feuriges Geschenk für Schärfe-Fans."),
  ("Acı Sos Tadım Seti", "Hafiften aşırı acıya altı özel üretim acı sos ve tadım notları. Her şeye biber koyan acı severlere ateşli bir hediye."),
  ("Hete saus proefset", "Zes ambachtelijke hete sauzen van mild tot extreem heet, met proefnotities. Een pittig cadeau voor de liefhebber van scherp eten."),
  ("Coffret dégustation de sauces piquantes", "Six sauces piquantes artisanales, du doux à l'extrême, avec notes de dégustation. Un cadeau brûlant pour l'amateur de piment."))

c("cheese_board", "unisex", ["adult", "senior"], ["housewarming", "wedding", "anniversary", "christmas"], ["foodie", "homebody"], (30, 90), "🧀",
  ("Bamboo Cheese Board with Knife Set", "Large bamboo serving board with a hidden drawer holding four stainless cheese knives. Elegant for entertaining and dinner parties."),
  ("Bambus-Käsebrett mit Messerset", "Großes Bambus-Servierbrett mit versteckter Schublade und vier Edelstahl-Käsemessern. Elegant für Gäste und Dinnerpartys."),
  ("Bambu Peynir Tahtası ve Bıçak Seti", "Dört paslanmaz peynir bıçağının gizli çekmecede saklandığı büyük bambu servis tahtası. Misafir ağırlamak için şık bir seçim."),
  ("Bamboe kaasplank met messenset", "Grote bamboe serveerplank met verborgen lade en vier roestvrijstalen kaasmessen. Stijlvol voor borrels en etentjes."),
  ("Plateau à fromage en bambou avec couteaux", "Grand plateau de service en bambou avec tiroir caché contenant quatre couteaux à fromage en inox. Élégant pour recevoir."))

c("bbq_tool_set", "male", ["adult", "senior"], ["fathers_day", "birthday", "retirement", "housewarming"], ["foodie", "outdoor"], (30, 80), "🍖",
  ("Stainless Steel BBQ Grill Tool Set", "20-piece grilling kit with tongs, spatula, skewers and thermometer in an aluminium case. For the dad who rules the barbecue."),
  ("Edelstahl-Grillbesteck-Set", "20-teiliges Grillset mit Zange, Wender, Spießen und Thermometer im Alukoffer. Für den Papa, der am Grill das Sagen hat."),
  ("Paslanmaz Çelik Mangal Seti", "Maşa, spatula, şiş ve termometre içeren 20 parça mangal seti, alüminyum çantada. Mangalın başındaki babalar için."),
  ("RVS barbecue gereedschapsset", "20-delige bbq-set met tang, spatel, spiesen en thermometer in een aluminium koffer. Voor de papa die de barbecue regeert."),
  ("Set d'ustensiles de barbecue en inox", "Kit de 20 pièces avec pince, spatule, brochettes et thermomètre dans une mallette en aluminium. Pour le papa roi du barbecue."))

c("pasta_making_kit", "unisex", ["young_adult", "adult"], ["housewarming", "wedding", "birthday"], ["foodie", "maker"], (35, 80), "🍝",
  ("Fresh Pasta Making Kit", "Everything to make pasta from scratch: a stainless pasta roller, drying rack, ravioli stamp and recipe booklet. A fun kitchen project for couples."),
  ("Pasta-Set zum Selbermachen", "Alles für frische Pasta: Edelstahl-Nudelmaschine, Trockenständer, Ravioli-Ausstecher und Rezeptheft. Ein schönes Küchenprojekt für Paare."),
  ("Taze Makarna Yapım Seti", "Sıfırdan makarna için her şey: paslanmaz makarna makinesi, kurutma askısı, ravioli kalıbı ve tarif kitapçığı. Çiftler için keyifli bir mutfak projesi."),
  ("Verse pasta maakset", "Alles om zelf pasta te maken: een rvs pastamachine, droogrek, raviolistempel en receptenboekje. Een leuk keukenproject voor stellen."),
  ("Kit pour pâtes fraîches maison", "Tout pour faire ses pâtes : machine à pâtes en inox, séchoir, moule à raviolis et livret de recettes. Un projet cuisine amusant pour les couples."))

c("whisky_glass_set", "male", ["adult", "senior"], ["fathers_day", "retirement", "birthday", "christmas"], ["foodie", "homebody"], (25, 70), "🥃",
  ("Whisky Glasses with Chilling Stones", "Two crystal tumblers, eight granite whisky stones and tongs in a wooden gift box. For the man who enjoys a dram without ice."),
  ("Whiskygläser mit Kühlsteinen", "Zwei Kristallgläser, acht Granit-Whiskysteine und Zange in einer Holz-Geschenkbox. Für den Mann, der seinen Whisky ohne Eis genießt."),
  ("Soğutma Taşlı Viski Bardağı Seti", "Ahşap hediye kutusunda iki kristal bardak, sekiz granit viski taşı ve maşa. Viskisini buzsuz seven erkekler için."),
  ("Whiskyglazen met koelstenen", "Twee kristallen glazen, acht granieten whiskystenen en een tang in een houten geschenkdoos. Voor de man die zijn whisky zonder ijs drinkt."),
  ("Verres à whisky avec pierres à whisky", "Deux verres en cristal, huit pierres en granit et une pince dans un coffret en bois. Pour l'homme qui savoure son whisky sans glace."))

c("wine_aerator_set", "unisex", ["adult", "senior"], ["housewarming", "anniversary", "thank_you", "christmas"], ["foodie"], (20, 55), "🍷",
  ("Wine Aerator and Opener Gift Set", "Electric corkscrew, aerating pourer, vacuum stopper and foil cutter in a sleek box. Elevates every bottle for the wine enthusiast."),
  ("Wein-Dekanter- und Öffner-Geschenkset", "Elektrischer Korkenzieher, Belüftungsausgießer, Vakuumstopfen und Folienschneider in edler Box. Für Weinliebhaber."),
  ("Şarap Havalandırıcı ve Açacak Hediye Seti", "Şık kutuda elektrikli tirbuşon, havalandırmalı servis ucu, vakum tıpa ve folyo kesici. Şarap tutkunları için."),
  ("Wijnbeluchter en opener cadeauset", "Elektrische kurkentrekker, beluchtende schenktuit, vacuümstop en foliesnijder in een strakke doos. Voor de wijnliefhebber."),
  ("Coffret aérateur et tire-bouchon", "Tire-bouchon électrique, bec aérateur, bouchon sous vide et coupe-capsule dans un coffret élégant. Pour l'amateur de vin."))

c("turkish_delight_box", "unisex", ["adult", "senior"], ["thank_you", "christmas", "get_well", "mothers_day"], ["foodie"], (15, 40), "🍬",
  ("Pistachio Turkish Delight Gift Box", "Traditional lokum with roasted pistachio and rose, dusted with coconut, in a decorative tin. A sweet thank-you gift."),
  ("Türkischer Honig mit Pistazien in Geschenkdose", "Traditionelles Lokum mit gerösteten Pistazien und Rose, mit Kokos bestäubt, in dekorativer Dose. Ein süßes Dankeschön."),
  ("Fıstıklı Lokum Hediye Kutusu", "Kavrulmuş fıstıklı ve güllü geleneksel lokum, hindistan cevizi kaplı, dekoratif teneke kutuda. Tatlı bir teşekkür hediyesi."),
  ("Turks fruit met pistache in cadeaublik", "Traditionele lokum met geroosterde pistache en roos, bestoven met kokos, in een decoratief blik. Een zoet bedankje."),
  ("Coffret de loukoums à la pistache", "Loukoum traditionnel à la pistache grillée et à la rose, saupoudré de noix de coco, dans une boîte décorative. Un doux merci."))

# ---------------------------------------------------------------- coffee / tea
c("pour_over_set", "unisex", ["young_adult", "adult"], ["birthday", "housewarming", "christmas"], ["coffee_tea", "foodie"], (25, 70), "☕",
  ("Pour-Over Coffee Maker Set", "Glass carafe with a stainless steel filter, gooseneck kettle and a bag of specialty beans. For the home barista who takes brewing seriously."),
  ("Pour-Over-Kaffeebereiter-Set", "Glaskaraffe mit Edelstahlfilter, Schwanenhalskessel und einer Packung Spezialitätenkaffee. Für Heim-Baristas mit Anspruch."),
  ("Pour-Over Kahve Demleme Seti", "Paslanmaz filtreli cam sürahi, ince ağızlı kettle ve bir paket nitelikli kahve çekirdeği. Demlemeyi ciddiye alan ev baristaları için."),
  ("Pour-over koffieset", "Glazen karaf met rvs filter, zwanenhalsketel en een zak specialty koffiebonen. Voor de thuisbarista die zetten serieus neemt."),
  ("Set de café filtre pour-over", "Carafe en verre avec filtre inox, bouilloire col de cygne et un sachet de café de spécialité. Pour le barista maison exigeant."))

c("turkish_coffee_set", "unisex", ["adult", "senior"], ["housewarming", "wedding", "mothers_day", "thank_you"], ["coffee_tea", "homebody"], (20, 60), "☕",
  ("Copper Turkish Coffee Set", "Hand-hammered copper cezve with two porcelain cups and saucers and a box of finely ground Turkish coffee. A traditional treat for hosts."),
  ("Türkisches Kaffeeset aus Kupfer", "Handgehämmerte Kupfer-Cezve mit zwei Porzellantassen samt Untertassen und einer Packung fein gemahlenem türkischem Kaffee."),
  ("Bakır Türk Kahvesi Seti", "El dövmesi bakır cezve, iki porselen fincan ve tabağı ile bir kutu ince öğütülmüş Türk kahvesi. Misafirperver evler için geleneksel bir hediye."),
  ("Koperen Turkse koffieset", "Handgehamerde koperen cezve met twee porseleinen kopjes en schotels en een doos fijngemalen Turkse koffie. Een traditioneel cadeau."),
  ("Service à café turc en cuivre", "Cezve en cuivre martelé main, deux tasses en porcelaine avec soucoupes et une boîte de café turc finement moulu. Un cadeau traditionnel."))

c("tea_sampler", "female", ["young_adult", "adult", "senior"], ["mothers_day", "get_well", "thank_you", "birthday"], ["coffee_tea", "wellness"], (15, 40), "🍵",
  ("Loose Leaf Tea Sampler with Infuser", "Twelve organic loose leaf teas from chamomile to jasmine green, with a glass infuser mug. A calming gift for tea lovers."),
  ("Lose-Tee-Probierset mit Teesieb", "Zwölf Bio-Tees von Kamille bis Jasmin-Grüntee, mit Glasbecher und Sieb. Ein beruhigendes Geschenk für Teeliebhaber."),
  ("Demlikli Dökme Çay Tadım Seti", "Papatyadan yaseminli yeşil çaya on iki organik dökme çay ve cam süzgeçli kupa. Çay severlere sakinleştirici bir hediye."),
  ("Losse thee proefset met theezeef", "Twaalf biologische losse theeën van kamille tot jasmijngroen, met een glazen mok met zeef. Een rustgevend cadeau voor theeliefhebbers."),
  ("Coffret de thés en vrac avec infuseur", "Douze thés bio en vrac, de la camomille au thé vert au jasmin, avec un mug infuseur en verre. Un cadeau apaisant pour les amateurs de thé."))

c("milk_frother", "unisex", ["young_adult", "adult"], ["christmas", "birthday", "housewarming"], ["coffee_tea", "tech"], (25, 70), "🥛",
  ("Electric Milk Frother", "Makes hot or cold foam for lattes, cappuccinos and matcha in under two minutes. Quiet, dishwasher-safe and coffee-shop quality at home."),
  ("Elektrischer Milchaufschäumer", "Bereitet heißen oder kalten Schaum für Latte, Cappuccino und Matcha in unter zwei Minuten. Leise, spülmaschinenfest, Café-Qualität zu Hause."),
  ("Elektrikli Süt Köpürtücü", "Latte, cappuccino ve matcha için iki dakikada sıcak veya soğuk köpük. Sessiz, bulaşık makinesinde yıkanabilir, evde kafe kalitesi."),
  ("Elektrische melkopschuimer", "Maakt in minder dan twee minuten warm of koud schuim voor latte, cappuccino en matcha. Stil en vaatwasserbestendig."),
  ("Mousseur à lait électrique", "Mousse chaude ou froide pour latte, cappuccino et matcha en moins de deux minutes. Silencieux, lavable au lave-vaisselle, qualité café à la maison."))

c("personalised_mug", "unisex", ["child", "teen", "young_adult", "adult", "senior"], ["birthday", "thank_you", "christmas", "fathers_day", "mothers_day"], ["coffee_tea", "homebody"], (10, 25), "🍵",
  ("Personalised Name Mug", "Ceramic 11oz mug printed with any name or short message, dishwasher and microwave safe. A small gift that gets used every morning."),
  ("Tasse mit Namen personalisiert", "Keramiktasse 330 ml mit Wunschnamen oder kurzer Botschaft, spülmaschinen- und mikrowellenfest. Ein kleines Geschenk für jeden Morgen."),
  ("İsme Özel Kupa", "İstediğiniz isim veya kısa mesaj baskılı 330 ml seramik kupa, bulaşık makinesi ve mikrodalga uyumlu. Her sabah kullanılacak küçük bir hediye."),
  ("Gepersonaliseerde mok met naam", "Keramische mok van 330 ml bedrukt met een naam of korte boodschap, vaatwasser- en magnetronbestendig. Een klein cadeau voor elke ochtend."),
  ("Mug personnalisé avec prénom", "Mug en céramique 330 ml imprimé avec un prénom ou un court message, compatible lave-vaisselle et micro-ondes. Un petit cadeau utilisé chaque matin."))

# ---------------------------------------------------------------- outdoor / fitness
c("hiking_backpack", "unisex", ["teen", "young_adult", "adult"], ["birthday", "christmas", "graduation"], ["outdoor", "traveler"], (50, 150), "🎒",
  ("30L Lightweight Hiking Backpack", "Water-resistant daypack with ventilated back panel, hydration sleeve and rain cover. Built for day hikes, trails and weekend trips."),
  ("30L Leichter Wanderrucksack", "Wasserabweisender Tagesrucksack mit belüftetem Rücken, Trinkblasenfach und Regenhülle. Für Tageswanderungen und Wochenendtrips."),
  ("30L Hafif Trekking Sırt Çantası", "Havalandırmalı sırt, su haznesi bölmesi ve yağmurluğu olan suya dayanıklı günlük çanta. Günübirlik doğa yürüyüşleri ve hafta sonu kampları için."),
  ("30L lichtgewicht wandelrugzak", "Waterafstotende dagrugzak met geventileerde rug, hoes voor drinkzak en regenhoes. Voor dagwandelingen en weekendtrips."),
  ("Sac à dos de randonnée 30L léger", "Sac de randonnée déperlant avec dos ventilé, poche d'hydratation et housse de pluie. Pour les randos à la journée et les week-ends."))

c("camping_lantern", "male", ["teen", "young_adult", "adult"], ["fathers_day", "birthday", "christmas"], ["outdoor", "tech"], (20, 50), "🏕️",
  ("Rechargeable LED Camping Lantern", "Collapsible lantern with 360° light, three brightness modes and a built-in power bank. Essential for camping, fishing and power cuts."),
  ("Wiederaufladbare LED-Campinglaterne", "Faltbare Laterne mit 360°-Licht, drei Helligkeitsstufen und integrierter Powerbank. Unverzichtbar beim Camping, Angeln und Stromausfall."),
  ("Şarjlı LED Kamp Feneri", "360° aydınlatma, üç parlaklık modu ve dahili powerbank ile katlanabilir fener. Kamp, balık ve elektrik kesintileri için şart."),
  ("Oplaadbare LED kampeerlantaarn", "Opvouwbare lantaarn met 360° licht, drie standen en ingebouwde powerbank. Onmisbaar bij kamperen, vissen en stroomuitval."),
  ("Lanterne de camping LED rechargeable", "Lanterne pliable à éclairage 360°, trois modes de luminosité et batterie externe intégrée. Indispensable en camping et pêche."))

c("yoga_mat_set", "female", ["teen", "young_adult", "adult"], ["birthday", "mothers_day", "christmas"], ["fitness", "wellness"], (25, 80), "🧘",
  ("Eco Yoga Mat with Strap and Blocks", "Non-slip cork and natural rubber mat, two foam blocks and a carrying strap. Supports yoga, pilates and stretching at home or in class."),
  ("Öko-Yogamatte mit Gurt und Blöcken", "Rutschfeste Matte aus Kork und Naturkautschuk, zwei Schaumblöcke und Tragegurt. Für Yoga, Pilates und Dehnen zu Hause oder im Kurs."),
  ("Askılı ve Bloklu Ekolojik Yoga Matı", "Kaymaz mantar ve doğal kauçuk mat, iki köpük blok ve taşıma askısı. Evde veya derste yoga, pilates ve esneme için."),
  ("Eco yogamat met riem en blokken", "Antislip mat van kurk en natuurrubber, twee schuimblokken en een draagriem. Voor yoga, pilates en stretchen thuis of in de les."),
  ("Tapis de yoga écologique avec sangle et briques", "Tapis antidérapant en liège et caoutchouc naturel, deux briques en mousse et une sangle. Pour le yoga, le pilates et les étirements."))

c("running_belt_bundle", "unisex", ["young_adult", "adult"], ["birthday", "christmas"], ["fitness", "outdoor"], (15, 40), "🏃",
  ("Runner's Essentials Kit", "Reflective running belt, LED armband, anti-blister socks and a handheld water bottle. A practical bundle for anyone training for a race."),
  ("Läufer-Starterset", "Reflektierender Laufgürtel, LED-Armband, Anti-Blasen-Socken und Handtrinkflasche. Praktisches Set für alle, die für einen Lauf trainieren."),
  ("Koşucu Temel Seti", "Reflektörlü koşu kemeri, LED kol bandı, nasır önleyici çorap ve el tipi matara. Yarışa hazırlanan herkes için pratik bir paket."),
  ("Hardloper essentials kit", "Reflecterende hardloopriem, LED-armband, anti-blaarsokken en een handbidon. Een praktisch pakket voor wie traint voor een loop."),
  ("Kit essentiel du coureur", "Ceinture de running réfléchissante, brassard LED, chaussettes anti-ampoules et gourde à main. Un ensemble pratique pour préparer une course."))

c("massage_gun", "male", ["young_adult", "adult"], ["fathers_day", "birthday", "christmas", "get_well"], ["fitness", "wellness", "tech"], (50, 150), "💆",
  ("Deep Tissue Massage Gun", "Quiet percussion massager with six heads and five speeds to ease sore muscles after the gym. Comes in a carry case with USB-C charging."),
  ("Massagepistole für tiefes Gewebe", "Leise Massagepistole mit sechs Aufsätzen und fünf Stufen gegen Muskelkater nach dem Training. Mit Koffer und USB-C-Ladung."),
  ("Derin Doku Masaj Tabancası", "Spor sonrası kas ağrılarını hafifleten altı başlıklı, beş hızlı sessiz masaj tabancası. Taşıma çantası ve USB-C şarj ile."),
  ("Massage gun voor diepe spieren", "Stil percussie-massageapparaat met zes opzetstukken en vijf standen tegen spierpijn na de sportschool. Met koffer en USB-C."),
  ("Pistolet de massage musculaire", "Masseur à percussion silencieux, six têtes et cinq vitesses pour soulager les muscles après la salle. Livré en mallette avec charge USB-C."))

c("insulated_bottle", "unisex", ["child", "teen", "young_adult", "adult"], ["birthday", "christmas", "graduation"], ["fitness", "outdoor", "traveler"], (20, 45), "🧴",
  ("Insulated Stainless Steel Water Bottle 1L", "Keeps drinks cold 24 hours or hot 12 hours, leak-proof lid and powder-coated finish. Engrave a name for a personal touch."),
  ("Isolierte Edelstahl-Trinkflasche 1L", "Hält Getränke 24 Stunden kalt oder 12 Stunden heiß, auslaufsicherer Deckel, pulverbeschichtet. Mit Namensgravur noch persönlicher."),
  ("1L Çelik Termos Matara", "İçecekleri 24 saat soğuk, 12 saat sıcak tutar, sızdırmaz kapak ve toz boya kaplama. İsim kazıtarak kişiselleştirin."),
  ("Geïsoleerde rvs drinkfles 1L", "Houdt dranken 24 uur koud of 12 uur warm, lekvrije dop en poedercoating. Laat een naam graveren voor een persoonlijk tintje."),
  ("Gourde isotherme en inox 1L", "Garde les boissons froides 24 h ou chaudes 12 h, bouchon anti-fuite et finition poudrée. Faites graver un prénom."))

c("fishing_kit", "male", ["child", "teen", "adult", "senior"], ["fathers_day", "birthday", "retirement"], ["outdoor"], (30, 90), "🎣",
  ("Telescopic Fishing Rod and Reel Combo", "Portable carbon-fibre rod, spinning reel, lures and tackle box in one bag. Ready for lakes, rivers and holiday fishing trips."),
  ("Teleskop-Angelrute mit Rolle im Set", "Tragbare Carbonrute, Spinnrolle, Köder und Angelbox in einer Tasche. Bereit für See, Fluss und Angelurlaub."),
  ("Teleskopik Olta ve Makara Seti", "Tek çantada taşınabilir karbon kamış, spin makara, yemler ve malzeme kutusu. Göl, nehir ve tatilde balık avı için hazır."),
  ("Telescopische hengel met molen set", "Draagbare carbon hengel, werpmolen, kunstaas en tacklebox in één tas. Klaar voor meren, rivieren en visvakanties."),
  ("Canne à pêche télescopique avec moulinet", "Canne en carbone portable, moulinet, leurres et boîte à pêche dans un sac. Prête pour les lacs, rivières et vacances."))

# ---------------------------------------------------------------- books / art / music
c("book_subscription", "unisex", ["young_adult", "adult", "senior"], ["birthday", "christmas", "retirement", "mothers_day"], ["bookworm"], (20, 60), "📚",
  ("Mystery Book Subscription Box", "A hand-picked new novel each month wrapped with a bookmark, tea and a literary treat. Choose fiction, thriller or romance for the reader."),
  ("Überraschungs-Buchbox im Abo", "Jeden Monat ein handverlesener neuer Roman, verpackt mit Lesezeichen, Tee und einer kleinen Leckerei. Belletristik, Thriller oder Romantik wählbar."),
  ("Sürpriz Kitap Abonelik Kutusu", "Her ay özenle seçilmiş yeni bir roman, kitap ayracı, çay ve küçük bir ikramla paketlenmiş. Kurgu, polisiye veya romantik seçeneği."),
  ("Verrassende boekenbox abonnement", "Elke maand een zorgvuldig gekozen nieuwe roman met boekenlegger, thee en iets lekkers. Kies fictie, thriller of romantiek."),
  ("Box littéraire surprise par abonnement", "Chaque mois un nouveau roman sélectionné, emballé avec un marque-page, du thé et une douceur. Au choix fiction, thriller ou romance."))

c("book_light_set", "unisex", ["child", "teen", "young_adult", "adult", "senior"], ["birthday", "christmas", "get_well"], ["bookworm", "homebody"], (12, 35), "🔖",
  ("Reading Light and Leather Bookmark Set", "Rechargeable clip-on reading lamp with warm light plus a personalised leather bookmark. For late-night reading in bed."),
  ("Leselampe und Leder-Lesezeichen-Set", "Wiederaufladbare Klemm-Leselampe mit warmem Licht und personalisiertem Leder-Lesezeichen. Für das Lesen spät im Bett."),
  ("Okuma Lambası ve Deri Kitap Ayracı Seti", "Sıcak ışıklı şarjlı kıskaçlı okuma lambası ve kişiye özel deri kitap ayracı. Gece yatakta kitap okuyanlar için."),
  ("Leeslampje en leren boekenlegger set", "Oplaadbaar klem-leeslampje met warm licht plus een gepersonaliseerde leren boekenlegger. Voor lezen in bed."),
  ("Liseuse et marque-page en cuir", "Lampe de lecture à pince rechargeable à lumière chaude et marque-page en cuir personnalisé. Pour lire tard au lit."))

c("watercolor_set", "unisex", ["child", "teen", "young_adult", "adult"], ["birthday", "christmas"], ["artist"], (20, 60), "🎨",
  ("Professional Watercolour Paint Set", "48 vibrant watercolour pans, brushes, a water brush and a cotton paper pad in a metal tin. For beginners and practising artists alike."),
  ("Professionelles Aquarellfarben-Set", "48 leuchtende Aquarellnäpfchen, Pinsel, Wassertankpinsel und Baumwollpapierblock in Metallbox. Für Anfänger und geübte Künstler."),
  ("Profesyonel Suluboya Seti", "Metal kutuda 48 canlı suluboya tableti, fırçalar, su hazneli fırça ve pamuklu kağıt blok. Başlayanlar ve sanatçılar için."),
  ("Professionele aquarelverfset", "48 levendige aquarelnapjes, penselen, waterbrush en een katoenpapierblok in een metalen doos. Voor beginners en ervaren kunstenaars."),
  ("Set de peinture aquarelle professionnel", "48 godets aquarelle vifs, pinceaux, pinceau à réservoir et bloc de papier coton dans une boîte métal. Pour débutants et artistes."))

c("sketching_kit", "unisex", ["teen", "young_adult"], ["birthday", "graduation", "christmas"], ["artist"], (15, 45), "✏️",
  ("Drawing and Sketching Pencil Kit", "33-piece set with graphite and charcoal pencils, blending stumps, erasers and a hardback sketchbook. Ideal for art students."),
  ("Zeichen- und Skizzier-Set", "33-teiliges Set mit Graphit- und Kohlestiften, Estompen, Radierern und Skizzenbuch mit festem Einband. Ideal für Kunststudenten."),
  ("Çizim ve Eskiz Kalem Seti", "Grafit ve kömür kalemler, karıştırma çubukları, silgiler ve sert kapaklı eskiz defteri içeren 33 parça set. Sanat öğrencileri için ideal."),
  ("Teken- en schetspotloden set", "33-delige set met grafiet- en houtskoolpotloden, doezelaars, gummen en een schetsboek met harde kaft. Ideaal voor kunststudenten."),
  ("Kit de crayons de dessin et croquis", "Set de 33 pièces avec crayons graphite et fusain, estompes, gommes et carnet de croquis rigide. Idéal pour les étudiants en art."))

c("vinyl_turntable", "unisex", ["young_adult", "adult", "senior"], ["birthday", "christmas", "retirement", "anniversary"], ["music", "homebody"], (80, 250), "🎵",
  ("Bluetooth Vinyl Turntable with Speakers", "Belt-drive record player with built-in stereo speakers and Bluetooth streaming. Brings the warm sound of vinyl to any living room."),
  ("Bluetooth-Plattenspieler mit Lautsprechern", "Riemengetriebener Plattenspieler mit integrierten Stereolautsprechern und Bluetooth. Bringt den warmen Vinyl-Klang ins Wohnzimmer."),
  ("Hoparlörlü Bluetooth Pikap", "Dahili stereo hoparlör ve Bluetooth akışlı kayışlı pikap. Plak sıcaklığını her oturma odasına taşır."),
  ("Bluetooth platenspeler met speakers", "Platenspeler met riemaandrijving, ingebouwde stereospeakers en Bluetooth. Brengt het warme vinylgeluid naar elke woonkamer."),
  ("Platine vinyle Bluetooth avec enceintes", "Platine à entraînement par courroie avec haut-parleurs stéréo intégrés et Bluetooth. Le son chaleureux du vinyle dans le salon."))

c("ukulele_starter", "unisex", ["child", "teen", "young_adult"], ["birthday", "christmas"], ["music"], (35, 80), "🎸",
  ("Ukulele Starter Kit", "Mahogany concert ukulele with gig bag, tuner, strap and online lessons. A fun first instrument for beginners of all ages."),
  ("Ukulele-Starterset", "Konzert-Ukulele aus Mahagoni mit Tasche, Stimmgerät, Gurt und Online-Kurs. Ein fröhliches erstes Instrument für Anfänger jeden Alters."),
  ("Ukulele Başlangıç Seti", "Çanta, akort aleti, askı ve online derslerle maun konser ukulele. Her yaştan yeni başlayanlar için eğlenceli ilk enstrüman."),
  ("Ukelele startersset", "Mahonie concert-ukelele met hoes, stemapparaat, band en online lessen. Een leuk eerste instrument voor beginners van elke leeftijd."),
  ("Kit ukulélé débutant", "Ukulélé concert en acajou avec housse, accordeur, sangle et cours en ligne. Un premier instrument ludique pour tous les âges."))

c("concert_poster_map", "unisex", ["young_adult", "adult"], ["birthday", "housewarming", "anniversary"], ["music", "artist"], (20, 60), "🎼",
  ("Custom Song Lyrics Wall Art Print", "A framed print of the lyrics to their favourite song, with the names and date of your choice. A meaningful piece for music lovers."),
  ("Personalisiertes Songtext-Wandbild", "Gerahmter Druck mit dem Text ihres Lieblingsliedes, mit Namen und Datum nach Wahl. Ein bedeutungsvolles Stück für Musikfans."),
  ("Kişiye Özel Şarkı Sözü Duvar Tablosu", "En sevdiği şarkının sözleriyle, istediğiniz isim ve tarihle çerçeveli baskı. Müzik severlere anlamlı bir parça."),
  ("Gepersonaliseerde songtekst wanddecoratie", "Ingelijste print van de tekst van hun favoriete nummer, met namen en datum naar keuze. Een betekenisvol stuk voor muziekliefhebbers."),
  ("Affiche personnalisée paroles de chanson", "Impression encadrée des paroles de leur chanson préférée, avec les prénoms et la date de votre choix. Un cadeau plein de sens pour les mélomanes."))

# ---------------------------------------------------------------- travel
c("scratch_world_map", "unisex", ["young_adult", "adult"], ["birthday", "housewarming", "graduation", "retirement"], ["traveler", "homebody"], (15, 40), "🗺️",
  ("Scratch-Off World Map Poster", "Large gold-foil world map that reveals colourful countries as you scratch off the places you've visited. Comes with a scratch tool and flag stickers."),
  ("Rubbel-Weltkarte Poster", "Große Weltkarte mit Goldfolie, die beim Freirubbeln besuchter Länder bunte Farben zeigt. Mit Rubbelwerkzeug und Flaggenstickern."),
  ("Kazınabilir Dünya Haritası Poster", "Gezilen ülkeleri kazıdıkça renkli ülkeler ortaya çıkan büyük altın folyolu dünya haritası. Kazıma aleti ve bayrak çıkartmaları dahil."),
  ("Kras wereldkaart poster", "Grote wereldkaart met goudfolie die kleurrijke landen onthult als je bezochte plekken wegkrast. Met kraspen en vlagstickers."),
  ("Carte du monde à gratter", "Grande carte du monde dorée qui dévoile des pays colorés au fur et à mesure des voyages grattés. Livrée avec outil à gratter et stickers drapeaux."))

c("travel_organizer_set", "female", ["young_adult", "adult"], ["birthday", "graduation", "christmas"], ["traveler", "fashion"], (20, 50), "🧳",
  ("Packing Cubes and Passport Holder Set", "Six compression packing cubes plus an RFID-blocking leather passport wallet. Keeps a suitcase tidy and documents safe on every trip."),
  ("Packwürfel und Reisepasshülle Set", "Sechs Kompressions-Packwürfel plus RFID-sichere Reisepasshülle aus Leder. Hält den Koffer ordentlich und Dokumente sicher auf jeder Reise."),
  ("Bavul Düzenleyici ve Pasaport Kılıfı Seti", "Altı sıkıştırmalı bavul düzenleyici ve RFID korumalı deri pasaport cüzdanı. Her seyahatte valizi düzenli, belgeleri güvende tutar."),
  ("Packing cubes en paspoorthoes set", "Zes compressie packing cubes plus een RFID-blokkerende leren paspoorthouder. Houdt de koffer netjes en documenten veilig."),
  ("Set de cubes de rangement et porte-passeport", "Six cubes de compression et un porte-passeport en cuir anti-RFID. Une valise ordonnée et des papiers en sécurité à chaque voyage."))

c("travel_pillow_kit", "unisex", ["young_adult", "adult", "senior"], ["birthday", "retirement", "christmas"], ["traveler", "homebody"], (15, 40), "✈️",
  ("Memory Foam Travel Pillow Set", "Ergonomic neck pillow with sleep mask, earplugs and a compact carry bag. Makes long flights and train journeys far more comfortable."),
  ("Memory-Foam-Reisekissen-Set", "Ergonomisches Nackenkissen mit Schlafmaske, Ohrstöpseln und kompakter Tasche. Macht lange Flüge und Zugfahrten deutlich bequemer."),
  ("Visko Seyahat Yastığı Seti", "Uyku maskesi, kulak tıkacı ve kompakt taşıma çantalı ergonomik boyun yastığı. Uzun uçuş ve tren yolculuklarını çok daha rahat kılar."),
  ("Traagschuim reiskussen set", "Ergonomisch nekkussen met slaapmasker, oordopjes en compacte draagtas. Maakt lange vluchten en treinreizen veel comfortabeler."),
  ("Coussin de voyage à mémoire de forme", "Oreiller cervical ergonomique avec masque de nuit, bouchons d'oreilles et pochette compacte. Pour des vols et trajets en train plus confortables."))

# ---------------------------------------------------------------- home / cozy / wellness
c("weighted_blanket", "unisex", ["young_adult", "adult", "senior"], ["christmas", "get_well", "birthday"], ["homebody", "wellness"], (40, 120), "🛋️",
  ("Weighted Blanket 7kg", "Soft weighted blanket with glass beads that eases stress and improves sleep. Comes with a removable minky cover for winter nights."),
  ("Gewichtsdecke 7kg", "Weiche Gewichtsdecke mit Glasperlen, die Stress lindert und den Schlaf verbessert. Mit abnehmbarem Kuschelbezug für Winternächte."),
  ("7 kg Ağırlıklı Battaniye", "Stresi azaltan ve uykuyu iyileştiren cam boncuklu yumuşak ağırlıklı battaniye. Kış geceleri için çıkarılabilir peluş kılıfla."),
  ("Verzwaringsdeken 7 kg", "Zachte verzwaringsdeken met glasparels die stress vermindert en de slaap verbetert. Met afneembare fleece hoes voor winteravonden."),
  ("Couverture lestée 7 kg", "Couverture lestée douce à billes de verre qui apaise le stress et améliore le sommeil. Housse minky amovible pour les nuits d'hiver."))

c("scented_candle_set", "female", ["young_adult", "adult", "senior"], ["housewarming", "mothers_day", "thank_you", "christmas", "birthday"], ["homebody", "wellness"], (15, 45), "🕯️",
  ("Soy Scented Candle Gift Set", "Three hand-poured soy candles in lavender, vanilla and cedarwood with 40-hour burn time each. Boxed and ready to gift."),
  ("Duftkerzen-Geschenkset aus Sojawachs", "Drei handgegossene Sojakerzen in Lavendel, Vanille und Zedernholz mit je 40 Stunden Brenndauer. Verpackt und bereit zum Verschenken."),
  ("Soya Mumu Kokulu Mum Hediye Seti", "Lavanta, vanilya ve sedir kokulu, her biri 40 saat yanan üç el dökümü soya mumu. Hediye kutusunda."),
  ("Geurkaarsen cadeauset van sojawas", "Drie handgegoten sojakaarsen in lavendel, vanille en cederhout met elk 40 branduren. Verpakt en klaar om te geven."),
  ("Coffret de bougies parfumées au soja", "Trois bougies de soja coulées main, lavande, vanille et cèdre, 40 heures de combustion chacune. Prêtes à offrir."))

c("spa_gift_basket", "female", ["young_adult", "adult", "senior"], ["mothers_day", "birthday", "get_well", "thank_you", "valentines"], ["wellness"], (25, 70), "🛁",
  ("Luxury Spa Gift Basket", "Bath bombs, body butter, a sheet mask, bath salts and a plush robe in a woven basket. A full self-care evening at home for her."),
  ("Luxus-Wellness-Geschenkkorb", "Badebomben, Körperbutter, Tuchmaske, Badesalz und ein flauschiger Bademantel im Korb. Ein ganzer Selfcare-Abend zu Hause für sie."),
  ("Lüks Spa Hediye Sepeti", "Banyo bombası, vücut yağı, kağıt maske, banyo tuzu ve peluş bornoz hasır sepette. Ona evde tam bir kişisel bakım akşamı."),
  ("Luxe spa cadeaumand", "Bruisballen, bodybutter, sheet mask, badzout en een zachte badjas in een gevlochten mand. Een complete verwenavond thuis voor haar."),
  ("Panier cadeau spa de luxe", "Bombes de bain, beurre corporel, masque en tissu, sels de bain et peignoir moelleux dans un panier tressé. Une soirée bien-être pour elle."))

c("essential_oil_diffuser", "unisex", ["young_adult", "adult", "senior"], ["housewarming", "mothers_day", "christmas", "get_well"], ["wellness", "homebody"], (20, 60), "🌿",
  ("Aromatherapy Diffuser with Essential Oils", "Ultrasonic wood-grain diffuser with colour-changing light and six pure essential oils. Creates a calm, spa-like atmosphere at home."),
  ("Aroma-Diffuser mit ätherischen Ölen", "Ultraschall-Diffuser in Holzoptik mit Farbwechsellicht und sechs reinen ätherischen Ölen. Schafft eine ruhige Spa-Atmosphäre zu Hause."),
  ("Uçucu Yağlı Aromaterapi Difüzörü", "Renk değiştiren ışıklı ahşap görünümlü ultrasonik difüzör ve altı saf uçucu yağ. Evde sakin bir spa atmosferi yaratır."),
  ("Aromadiffuser met etherische oliën", "Ultrasone diffuser in houtlook met kleurwisselend licht en zes pure etherische oliën. Zorgt thuis voor een rustige spa-sfeer."),
  ("Diffuseur d'aromathérapie avec huiles essentielles", "Diffuseur à ultrasons effet bois avec lumière changeante et six huiles essentielles pures. Une ambiance spa apaisante à la maison."))

c("sunrise_alarm", "unisex", ["teen", "young_adult", "adult"], ["christmas", "birthday", "graduation"], ["wellness", "tech"], (30, 80), "🌅",
  ("Sunrise Alarm Clock with Nature Sounds", "Wake-up light that brightens gradually like dawn, with sunset mode, FM radio and gentle nature sounds. Helps heavy sleepers wake naturally."),
  ("Lichtwecker mit Naturgeräuschen", "Wake-up-Light, das wie die Morgendämmerung langsam heller wird, mit Sonnenuntergangsmodus, FM-Radio und sanften Naturklängen."),
  ("Doğa Sesli Gün Doğumu Çalar Saat", "Şafak gibi yavaşça aydınlanan uyandırma ışığı, gün batımı modu, FM radyo ve yumuşak doğa sesleri. Ağır uyuyanlara doğal uyanış."),
  ("Wake-up light met natuurgeluiden", "Wekker die geleidelijk oplicht zoals de zonsopgang, met zonsondergangstand, FM-radio en zachte natuurgeluiden. Voor diepe slapers."),
  ("Réveil simulateur d'aube avec sons de la nature", "Lampe de réveil qui s'éclaire progressivement comme l'aube, mode coucher de soleil, radio FM et sons de nature. Un réveil en douceur."))

c("cozy_slippers_robe", "female", ["adult", "senior"], ["christmas", "mothers_day", "get_well", "birthday"], ["homebody"], (25, 70), "🧦",
  ("Fleece Robe and Memory Foam Slippers", "Ultra-soft plush bathrobe with matching non-slip slippers. The ultimate cosy set for lazy Sunday mornings and chilly evenings."),
  ("Fleece-Bademantel mit Memory-Foam-Hausschuhen", "Ultraweicher Plüsch-Bademantel mit passenden rutschfesten Hausschuhen. Das gemütlichste Set für faule Sonntage und kühle Abende."),
  ("Polar Sabahlık ve Visko Terlik Seti", "Ultra yumuşak peluş sabahlık ve uyumlu kaymaz terlik. Tembel pazar sabahları ve serin akşamlar için en rahat set."),
  ("Fleece badjas en traagschuim pantoffels", "Ultrazachte pluche badjas met bijpassende antislip pantoffels. De gezelligste set voor luie zondagen en koude avonden."),
  ("Peignoir polaire et chaussons à mémoire de forme", "Peignoir en peluche ultra-doux avec chaussons antidérapants assortis. L'ensemble cocooning idéal pour les dimanches paresseux."))

c("puzzle_1000", "unisex", ["child", "teen", "adult", "senior"], ["christmas", "birthday", "get_well", "retirement"], ["homebody", "artist"], (12, 30), "🧩",
  ("1000-Piece Jigsaw Puzzle", "Beautifully illustrated 1000-piece puzzle on thick recycled board with a poster guide. A relaxing weekend project for the whole family."),
  ("1000-Teile-Puzzle", "Wunderschön illustriertes 1000-Teile-Puzzle auf dicker Recyclingpappe mit Posteranleitung. Ein entspanntes Wochenendprojekt für die ganze Familie."),
  ("1000 Parçalı Yapboz", "Poster rehberli, kalın geri dönüştürülmüş kartonda güzel resimli 1000 parçalı puzzle. Tüm aile için rahatlatıcı bir hafta sonu etkinliği."),
  ("Puzzel van 1000 stukjes", "Prachtig geïllustreerde puzzel van 1000 stukjes op dik gerecycled karton met poster. Een ontspannend weekendproject voor het hele gezin."),
  ("Puzzle 1000 pièces", "Puzzle de 1000 pièces magnifiquement illustré sur carton recyclé épais avec poster. Un projet relaxant pour toute la famille."))

c("board_game_family", "unisex", ["child", "teen", "young_adult", "adult"], ["christmas", "birthday", "housewarming"], ["homebody", "gamer"], (25, 60), "🎲",
  ("Strategy Board Game for Families", "Award-winning tile-laying board game for 2-5 players, ages 8 and up. Easy to learn in ten minutes, endlessly replayable on game nights."),
  ("Strategie-Brettspiel für die Familie", "Preisgekröntes Legespiel für 2-5 Spieler ab 8 Jahren. In zehn Minuten gelernt, an Spieleabenden immer wieder neu."),
  ("Aile için Strateji Kutu Oyunu", "2-5 oyuncu, 8 yaş ve üzeri için ödüllü karo yerleştirme oyunu. On dakikada öğrenilir, oyun gecelerinde hiç sıkmaz."),
  ("Strategisch bordspel voor het gezin", "Bekroond legspel voor 2-5 spelers vanaf 8 jaar. In tien minuten te leren, eindeloos leuk op spelletjesavonden."),
  ("Jeu de société stratégique familial", "Jeu de pose de tuiles primé pour 2 à 5 joueurs, dès 8 ans. Appris en dix minutes, rejouable à l'infini en soirée jeux."))

# ---------------------------------------------------------------- fashion / jewellery
c("initial_necklace", "female", ["teen", "young_adult", "adult"], ["birthday", "valentines", "anniversary", "mothers_day", "graduation"], ["fashion"], (20, 90), "💎",
  ("Personalised Initial Necklace in Gold", "Dainty 18k gold-plated necklace with a hand-stamped initial pendant. Arrives in a velvet jewellery box, perfect for layering."),
  ("Personalisierte Initialen-Halskette vergoldet", "Zarte 18k vergoldete Kette mit handgestempeltem Buchstabenanhänger. Kommt in Samt-Schmuckbox, perfekt zum Kombinieren."),
  ("Kişiye Özel Altın Kaplama Harf Kolye", "El baskılı harf uçlu zarif 18 ayar altın kaplama kolye. Kadife takı kutusunda gelir, katmanlı kullanıma uygun."),
  ("Gepersonaliseerde initiaal ketting goudkleurig", "Fijne 18k verguld kettinkje met handgestempelde initiaalhanger. Geleverd in een fluwelen sieradendoosje."),
  ("Collier initiale personnalisé plaqué or", "Collier délicat plaqué or 18 carats avec pendentif initiale gravé à la main. Livré dans un écrin en velours."))

c("leather_wallet_engraved", "male", ["young_adult", "adult", "senior"], ["fathers_day", "birthday", "anniversary", "graduation", "christmas"], ["fashion"], (25, 80), "👛",
  ("Engraved Leather Bifold Wallet", "Full-grain leather wallet with RFID protection, engraved with his initials or a short message. Ages beautifully with daily use."),
  ("Graviertes Leder-Portemonnaie", "Geldbörse aus Vollnarbenleder mit RFID-Schutz, graviert mit Initialen oder kurzer Botschaft. Wird mit jedem Tag schöner."),
  ("İsim Kazınmış Deri Cüzdan", "RFID korumalı, baş harfleri veya kısa bir mesaj kazınabilen tam tane deri cüzdan. Her gün kullandıkça güzelleşir."),
  ("Gegraveerde leren portemonnee", "Portemonnee van volnerfleer met RFID-bescherming, gegraveerd met zijn initialen of korte boodschap. Wordt mooier met de tijd."),
  ("Portefeuille en cuir gravé", "Portefeuille en cuir pleine fleur avec protection RFID, gravé de ses initiales ou d'un court message. Se patine avec le temps."))

c("silk_scarf", "female", ["adult", "senior"], ["mothers_day", "birthday", "christmas", "thank_you"], ["fashion"], (25, 90), "🧣",
  ("Pure Silk Scarf with Floral Print", "Lightweight 100% mulberry silk square scarf in a hand-drawn floral design. Wear it on the neck, hair or handbag for an elegant touch."),
  ("Reiner Seidenschal mit Blumenmuster", "Leichtes Tuch aus 100% Maulbeerseide mit handgezeichnetem Blumendesign. Am Hals, im Haar oder an der Tasche ein eleganter Akzent."),
  ("Çiçek Desenli Saf İpek Eşarp", "El çizimi çiçek desenli, hafif %100 dut ipeği kare eşarp. Boyunda, saçta veya çantada şık bir dokunuş."),
  ("Zijden sjaal met bloemenprint", "Lichte vierkante sjaal van 100% moerbeizijde met handgetekend bloemdessin. Om de nek, in het haar of aan de tas."),
  ("Foulard en soie à imprimé floral", "Carré léger en 100% soie de mûrier au motif floral dessiné main. Au cou, dans les cheveux ou sur le sac pour une touche élégante."))

c("minimalist_watch", "male", ["young_adult", "adult"], ["graduation", "birthday", "anniversary", "christmas"], ["fashion"], (60, 200), "⌚",
  ("Minimalist Leather Strap Watch", "Slim 40mm case with a clean dial, Japanese quartz movement and a genuine leather strap. Understated style for work and weekends."),
  ("Minimalistische Uhr mit Lederarmband", "Schlankes 40-mm-Gehäuse mit klarem Zifferblatt, japanischem Quarzwerk und echtem Lederband. Dezenter Stil für Büro und Wochenende."),
  ("Minimalist Deri Kordonlu Saat", "Sade kadranlı 40 mm ince kasa, Japon quartz mekanizma ve hakiki deri kordon. İş ve hafta sonu için zarif bir stil."),
  ("Minimalistisch horloge met leren band", "Slanke 40 mm kast met strakke wijzerplaat, Japans quartz uurwerk en echt leren band. Ingetogen stijl voor werk en weekend."),
  ("Montre minimaliste bracelet cuir", "Boîtier fin de 40 mm au cadran épuré, mouvement quartz japonais et bracelet en cuir véritable. Un style sobre pour le travail et le week-end."))

c("cashmere_beanie_gloves", "unisex", ["teen", "young_adult", "adult"], ["christmas", "birthday", "valentines"], ["fashion", "outdoor"], (30, 80), "🧤",
  ("Cashmere Beanie and Touchscreen Gloves", "Soft cashmere-blend hat with matching gloves that work on phone screens. A warm, stylish winter set for him or her."),
  ("Kaschmir-Mütze und Touchscreen-Handschuhe", "Weiche Mütze aus Kaschmirmischung mit passenden Handschuhen für Smartphone-Displays. Warmes, stilvolles Winterset für sie und ihn."),
  ("Kaşmir Bere ve Dokunmatik Eldiven", "Telefon ekranında çalışan uyumlu eldivenlerle yumuşak kaşmir karışımlı bere. Ona ve ona sıcak, şık bir kış seti."),
  ("Kasjmier muts en touchscreen handschoenen", "Zachte muts van kasjmiermix met bijpassende handschoenen die werken op telefoonschermen. Een warme, stijlvolle winterset."),
  ("Bonnet en cachemire et gants tactiles", "Bonnet doux en mélange cachemire avec gants assortis compatibles écran tactile. Un ensemble d'hiver chaud et élégant."))

# ---------------------------------------------------------------- garden / pets
c("herb_garden_kit", "unisex", ["young_adult", "adult", "senior"], ["housewarming", "mothers_day", "birthday", "retirement"], ["gardener", "foodie"], (20, 50), "🌱",
  ("Indoor Herb Garden Starter Kit", "Grow basil, mint, parsley and thyme on the kitchen windowsill with organic seeds, soil discs and bamboo pots. Fresh herbs all year."),
  ("Kräutergarten-Starterset für drinnen", "Basilikum, Minze, Petersilie und Thymian auf der Fensterbank ziehen, mit Bio-Samen, Erdtabs und Bambustöpfen. Frische Kräuter das ganze Jahr."),
  ("İç Mekan Baharat Bahçesi Seti", "Organik tohumlar, toprak tabletleri ve bambu saksılarla mutfak penceresinde fesleğen, nane, maydanoz ve kekik yetiştirin."),
  ("Kruidentuin startpakket voor binnen", "Kweek basilicum, munt, peterselie en tijm op de vensterbank met biologische zaden, aardetabletten en bamboe potjes."),
  ("Kit de jardin d'herbes aromatiques d'intérieur", "Faites pousser basilic, menthe, persil et thym sur le rebord de la fenêtre avec graines bio, pastilles de terre et pots en bambou."))

c("garden_tool_set", "female", ["adult", "senior"], ["mothers_day", "retirement", "birthday", "housewarming"], ["gardener", "outdoor"], (25, 70), "🌷",
  ("Garden Tool Set with Tote Bag", "Stainless trowel, fork, pruner and gloves in a floral canvas tote with pockets. For the gardener who loves tending the flower beds."),
  ("Gartenwerkzeug-Set mit Tragetasche", "Edelstahl-Schaufel, Grabegabel, Gartenschere und Handschuhe in geblümter Canvas-Tasche. Für die Gärtnerin mit Liebe zum Beet."),
  ("Çantalı Bahçe Aletleri Seti", "Çiçekli kanvas çantada paslanmaz mala, çatal, budama makası ve eldiven. Çiçek tarhlarıyla ilgilenmeyi seven bahçıvanlar için."),
  ("Tuingereedschapsset met draagtas", "RVS schepje, vork, snoeischaar en handschoenen in een gebloemde canvas tas met vakken. Voor de tuinier die graag in de border werkt."),
  ("Set d'outils de jardin avec sac", "Transplantoir, griffe, sécateur en inox et gants dans un sac en toile fleurie. Pour la jardinière qui soigne ses massifs."))

c("bonsai_kit", "unisex", ["young_adult", "adult", "senior"], ["birthday", "retirement", "housewarming", "christmas"], ["gardener", "wellness"], (20, 45), "🌳",
  ("Grow Your Own Bonsai Kit", "Four species of bonsai seeds, biodegradable pots, soil and a detailed guide. A patient, mindful hobby that lasts for years."),
  ("Bonsai-Anzuchtset", "Samen von vier Bonsai-Arten, biologisch abbaubare Töpfe, Erde und ausführliche Anleitung. Ein geduldiges, achtsames Hobby für Jahre."),
  ("Kendi Bonsainizi Yetiştirin Seti", "Dört bonsai türü tohumu, çözünür saksılar, toprak ve ayrıntılı rehber. Yıllarca süren sabırlı ve huzurlu bir hobi."),
  ("Kweek je eigen bonsai set", "Zaden van vier bonsaisoorten, biologisch afbreekbare potjes, aarde en een uitgebreide gids. Een geduldige, mindful hobby."),
  ("Kit de culture de bonsaï", "Graines de quatre espèces de bonsaï, pots biodégradables, terreau et guide détaillé. Un passe-temps patient et apaisant."))

c("dog_gift_box", "unisex", ["young_adult", "adult", "senior"], ["christmas", "birthday", "thank_you"], ["pet_lover"], (20, 50), "🐶",
  ("Dog Lover Gift Box", "Durable rope toy, natural treats, a bandana and a personalised dog tag. For the owner whose dog is part of the family."),
  ("Geschenkbox für Hundefreunde", "Robustes Seilspielzeug, natürliche Leckerlis, Halstuch und personalisierte Hundemarke. Für Besitzer, deren Hund zur Familie gehört."),
  ("Köpek Sever Hediye Kutusu", "Dayanıklı ip oyuncak, doğal ödül, bandana ve kişiye özel köpek künyesi. Köpeği aileden sayan sahipler için."),
  ("Hondenliefhebber cadeaubox", "Stevig touwspeeltje, natuurlijke snacks, een bandana en een gepersonaliseerd hondenpenning. Voor baasjes bij wie de hond familie is."),
  ("Box cadeau pour amoureux des chiens", "Jouet en corde résistant, friandises naturelles, bandana et médaille personnalisée. Pour le maître dont le chien fait partie de la famille."))

c("cat_tree_toy", "unisex", ["young_adult", "adult", "senior"], ["christmas", "birthday", "housewarming"], ["pet_lover", "homebody"], (25, 80), "🐱",
  ("Cat Window Perch and Toy Bundle", "Suction-mounted window hammock with a feather wand, catnip mice and a tunnel. Hours of fun for the cat and the cat lover."),
  ("Katzen-Fensterliege mit Spielzeug-Set", "Saugnapf-Fensterhängematte mit Federangel, Katzenminze-Mäusen und Tunnel. Stundenlanger Spaß für Katze und Katzenfreund."),
  ("Kedi Pencere Yatağı ve Oyuncak Seti", "Vantuzlu pencere hamağı, tüylü oyuncak çubuk, kedi nanesi fareler ve tünel. Kedi ve kedi severi için saatlerce eğlence."),
  ("Kattenhangmat voor het raam met speelgoed", "Raamhangmat met zuignappen, verenhengel, kattenkruidmuisjes en een tunnel. Urenlang plezier voor kat en kattenliefhebber."),
  ("Hamac de fenêtre pour chat et jouets", "Hamac à ventouses pour fenêtre avec plumeau, souris à l'herbe à chat et tunnel. Des heures de plaisir pour le chat et son maître."))

c("pet_portrait", "unisex", ["young_adult", "adult", "senior"], ["birthday", "christmas", "valentines", "thank_you"], ["pet_lover", "artist"], (30, 90), "🖼️",
  ("Custom Pet Portrait from Photo", "An artist turns a photo of their dog or cat into a framed renaissance-style portrait. A funny, heartfelt gift for proud pet parents."),
  ("Haustier-Porträt nach Foto", "Ein Künstler verwandelt ein Foto von Hund oder Katze in ein gerahmtes Porträt im Renaissance-Stil. Witzig und herzlich für stolze Tiereltern."),
  ("Fotoğraftan Özel Evcil Hayvan Portresi", "Bir sanatçı köpek veya kedisinin fotoğrafını çerçeveli rönesans tarzı portreye dönüştürür. Gururlu hayvan ebeveynlerine eğlenceli bir hediye."),
  ("Huisdierportret op basis van foto", "Een kunstenaar maakt van een foto van hun hond of kat een ingelijst portret in renaissancestijl. Grappig en hartverwarmend."),
  ("Portrait d'animal personnalisé d'après photo", "Un artiste transforme la photo de leur chien ou chat en portrait encadré style Renaissance. Drôle et touchant pour les parents d'animaux."))

# ---------------------------------------------------------------- maker / DIY
c("multitool", "male", ["young_adult", "adult", "senior"], ["fathers_day", "birthday", "christmas", "retirement"], ["maker", "outdoor"], (30, 120), "🔧",
  ("18-in-1 Stainless Multi-Tool", "Pliers, knife, screwdrivers, saw and bottle opener folded into one pocket tool with a leather sheath. For the handyman and the camper."),
  ("18-in-1 Edelstahl-Multitool", "Zange, Messer, Schraubendreher, Säge und Flaschenöffner in einem Taschenwerkzeug mit Lederetui. Für Heimwerker und Camper."),
  ("18'i 1 Arada Çelik Çok Amaçlı Alet", "Pense, bıçak, tornavida, testere ve şişe açacağı deri kılıflı tek cep aletinde. Tamirci ruhlular ve kampçılar için."),
  ("18-in-1 rvs multitool", "Tang, mes, schroevendraaiers, zaag en flesopener in één zakgereedschap met leren hoes. Voor de klusser en de kampeerder."),
  ("Outil multifonction 18 en 1 en inox", "Pince, couteau, tournevis, scie et décapsuleur réunis dans un outil de poche avec étui en cuir. Pour le bricoleur et le campeur."))

c("3d_puzzle_model", "unisex", ["teen", "young_adult", "adult"], ["birthday", "christmas"], ["maker", "homebody"], (25, 60), "🏗️",
  ("Wooden Mechanical 3D Puzzle Model", "Build a working marble run or clock from 300 laser-cut wooden pieces, no glue needed. A satisfying hands-on project for tinkerers."),
  ("Mechanisches 3D-Holzpuzzle", "Aus 300 lasergeschnittenen Holzteilen eine funktionierende Kugelbahn oder Uhr bauen, ganz ohne Kleber. Ein befriedigendes Projekt für Tüftler."),
  ("Ahşap Mekanik 3D Puzzle Modeli", "300 lazer kesim ahşap parçadan yapıştırıcısız çalışan bir bilye yolu veya saat yapın. Meraklı eller için tatmin edici bir proje."),
  ("Houten mechanische 3D-puzzel", "Bouw een werkende knikkerbaan of klok uit 300 lasergesneden houten onderdelen, zonder lijm. Een bevredigend project voor knutselaars."),
  ("Puzzle 3D mécanique en bois", "Construisez un circuit à billes ou une horloge fonctionnelle à partir de 300 pièces en bois découpées au laser, sans colle. Pour les bricoleurs."))

c("electronics_kit", "unisex", ["child", "teen"], ["birthday", "christmas"], ["maker", "tech"], (25, 70), "🔌",
  ("Electronics Discovery Kit for Kids", "Snap-together circuit kit with 100 projects, from alarms to FM radios. Teaches children 8+ how electricity works through play."),
  ("Elektronik-Experimentierkasten für Kinder", "Steckbarer Schaltkreis-Baukasten mit 100 Projekten von Alarmanlagen bis FM-Radio. Zeigt Kindern ab 8 spielerisch, wie Strom funktioniert."),
  ("Çocuklar için Elektronik Keşif Seti", "Alarmdan FM radyoya 100 proje içeren geçmeli devre seti. 8 yaş ve üzeri çocuklara elektriği oyunla öğretir."),
  ("Elektronica ontdekset voor kinderen", "Klik-circuitset met 100 projecten, van alarmen tot FM-radio's. Leert kinderen vanaf 8 jaar spelenderwijs hoe elektriciteit werkt."),
  ("Kit découverte électronique pour enfants", "Kit de circuits à clipser avec 100 projets, de l'alarme à la radio FM. Apprend aux enfants dès 8 ans comment fonctionne l'électricité."))

c("candle_making_kit", "female", ["teen", "young_adult", "adult"], ["birthday", "christmas", "mothers_day"], ["maker", "homebody", "artist"], (25, 55), "🕯️",
  ("DIY Candle Making Kit", "Soy wax, wicks, fragrance oils, dried flowers and tins to pour eight scented candles at home. A creative evening project with friends."),
  ("DIY-Kerzengießset", "Sojawachs, Dochte, Duftöle, Trockenblumen und Dosen für acht selbst gegossene Duftkerzen. Ein kreativer Abend mit Freundinnen."),
  ("Kendin Yap Mum Yapım Seti", "Evde sekiz kokulu mum dökmek için soya mumu, fitiller, koku yağları, kuru çiçekler ve kutular. Arkadaşlarla yaratıcı bir akşam."),
  ("DIY kaarsen maken set", "Sojawas, lonten, geurolie, droogbloemen en blikjes om thuis acht geurkaarsen te gieten. Een creatief avondje met vriendinnen."),
  ("Kit de fabrication de bougies", "Cire de soja, mèches, huiles parfumées, fleurs séchées et boîtes pour couler huit bougies parfumées. Une soirée créative entre amies."))

# ---------------------------------------------------------------- baby / kids
c("baby_memory_book", "unisex", ["baby"], ["new_baby"], ["homebody", "artist"], (15, 40), "👶",
  ("Baby's First Year Memory Book", "Linen-bound keepsake journal to record milestones, photos and handprints from birth to first birthday. A thoughtful gift for new parents."),
  ("Babys erstes Jahr Erinnerungsbuch", "Leinengebundenes Erinnerungsalbum für Meilensteine, Fotos und Handabdrücke von der Geburt bis zum ersten Geburtstag. Für frischgebackene Eltern."),
  ("Bebeğin İlk Yılı Anı Defteri", "Doğumdan ilk doğum gününe kilometre taşları, fotoğraflar ve el izleri için keten ciltli anı defteri. Yeni anne babalara düşünceli bir hediye."),
  ("Baby's eerste jaar herinneringsboek", "Linnen gebonden dagboek voor mijlpalen, foto's en handafdrukken van geboorte tot eerste verjaardag. Een attent kraamcadeau."),
  ("Album souvenir de la première année de bébé", "Journal relié en lin pour consigner les étapes, photos et empreintes de la naissance au premier anniversaire. Pour les jeunes parents."))

c("baby_gift_basket", "unisex", ["baby"], ["new_baby"], ["homebody"], (30, 80), "🍼",
  ("Newborn Gift Basket", "Organic cotton onesies, a muslin swaddle, a plush rabbit and a wooden rattle in a keepsake basket. Everything a baby shower gift should be."),
  ("Geschenkkorb zur Geburt", "Bio-Baumwoll-Bodys, Musselin-Pucktuch, Plüschhase und Holzrassel im Erinnerungskorb. Alles, was ein Geschenk zur Geburt braucht."),
  ("Yenidoğan Hediye Sepeti", "Organik pamuk zıbınlar, müslin kundak, peluş tavşan ve ahşap çıngırak hatıra sepetinde. Bir baby shower hediyesinde olması gereken her şey."),
  ("Kraamcadeau mand", "Rompertjes van biologisch katoen, een hydrofiele doek, een pluche konijn en een houten rammelaar in een bewaarmand. Het perfecte kraamcadeau."),
  ("Panier cadeau de naissance", "Bodies en coton bio, lange en mousseline, lapin en peluche et hochet en bois dans un panier souvenir. Le cadeau de naissance idéal."))

c("wooden_toy_train", "unisex", ["baby", "child"], ["birthday", "christmas", "new_baby"], ["maker", "homebody"], (20, 60), "🚂",
  ("Wooden Train Set with Tracks", "50-piece beech wood railway with bridges, trains and trees, compatible with major brands. Safe, durable play for toddlers from 2 years."),
  ("Holzeisenbahn-Set mit Schienen", "50-teilige Buchenholz-Eisenbahn mit Brücken, Zügen und Bäumen, kompatibel mit großen Marken. Sicheres, robustes Spiel ab 2 Jahren."),
  ("Raylı Ahşap Tren Seti", "Köprü, tren ve ağaçlı 50 parça kayın ahşap demiryolu, büyük markalarla uyumlu. 2 yaş ve üzeri için güvenli ve dayanıklı oyun."),
  ("Houten treinset met rails", "50-delige beukenhouten spoorbaan met bruggen, treinen en bomen, past op grote merken. Veilig en stevig speelgoed vanaf 2 jaar."),
  ("Circuit de train en bois", "Chemin de fer en hêtre de 50 pièces avec ponts, trains et arbres, compatible avec les grandes marques. Jeu sûr et solide dès 2 ans."))

c("kids_science_kit", "unisex", ["child"], ["birthday", "christmas"], ["maker", "tech"], (20, 50), "🔬",
  ("Kids Science Experiment Kit", "50 safe experiments with crystals, volcanoes and slime, plus goggles and a lab notebook. Hands-on STEM fun for curious kids aged 6-12."),
  ("Experimentierkasten für Kinder", "50 sichere Experimente mit Kristallen, Vulkanen und Schleim, plus Schutzbrille und Laborheft. MINT-Spaß für neugierige Kinder von 6-12."),
  ("Çocuk Bilim Deney Seti", "Kristal, yanardağ ve slime ile 50 güvenli deney, gözlük ve laboratuvar defteri dahil. 6-12 yaş meraklı çocuklara uygulamalı STEM eğlencesi."),
  ("Wetenschap experimenteerset voor kinderen", "50 veilige experimenten met kristallen, vulkanen en slijm, plus bril en labnotitieboek. STEM-plezier voor nieuwsgierige kinderen van 6-12."),
  ("Kit d'expériences scientifiques pour enfants", "50 expériences sûres avec cristaux, volcans et slime, lunettes et carnet de labo inclus. Du STEM ludique pour les curieux de 6 à 12 ans."))

c("plush_nightlight", "unisex", ["baby", "child"], ["birthday", "christmas", "new_baby", "get_well"], ["homebody"], (15, 40), "🧸",
  ("Plush Star Projector Night Light", "Cuddly turtle that projects stars onto the ceiling in soothing colours with a 45-minute auto-off. Helps little ones fall asleep without fear of the dark."),
  ("Plüsch-Sternenhimmel-Nachtlicht", "Kuschelige Schildkröte, die Sterne in sanften Farben an die Decke projiziert, mit 45-Minuten-Abschaltung. Hilft Kleinen beim Einschlafen."),
  ("Peluş Yıldız Projektör Gece Lambası", "Tavana yumuşak renklerde yıldızlar yansıtan, 45 dakikada kapanan sevimli kaplumbağa. Küçüklerin karanlık korkusu olmadan uyumasına yardım eder."),
  ("Pluche sterrenprojector nachtlampje", "Knuffelschildpad die sterren in rustgevende kleuren op het plafond projecteert, met automatische uitschakeling na 45 minuten."),
  ("Veilleuse peluche projecteur d'étoiles", "Tortue câline qui projette des étoiles au plafond en couleurs apaisantes, arrêt automatique après 45 minutes. Pour s'endormir sans peur du noir."))

c("kids_art_easel", "unisex", ["child"], ["birthday", "christmas"], ["artist"], (40, 90), "🖍️",
  ("Double-Sided Kids Art Easel", "Height-adjustable wooden easel with chalkboard, whiteboard, paper roll and paint cups. Keeps young artists busy for hours."),
  ("Doppelseitige Kinder-Staffelei", "Höhenverstellbare Holzstaffelei mit Kreidetafel, Whiteboard, Papierrolle und Farbbechern. Beschäftigt kleine Künstler stundenlang."),
  ("Çift Taraflı Çocuk Resim Şövalesi", "Kara tahta, beyaz tahta, kağıt rulosu ve boya kaplarıyla yükseklik ayarlı ahşap şövale. Küçük sanatçıları saatlerce meşgul eder."),
  ("Dubbelzijdige kinderschildersezel", "In hoogte verstelbare houten ezel met krijtbord, whiteboard, papierrol en verfbakjes. Houdt jonge kunstenaars urenlang bezig."),
  ("Chevalet double face pour enfants", "Chevalet en bois réglable en hauteur avec tableau noir, tableau blanc, rouleau de papier et pots de peinture. Pour occuper les petits artistes."))

c("teen_led_strip", "unisex", ["teen"], ["birthday", "christmas"], ["tech", "gamer", "music"], (15, 40), "💡",
  ("Smart LED Strip Lights 10m", "App-controlled RGB light strip that syncs to music, with 16 million colours and voice control. Transforms a teenager's bedroom or gaming setup."),
  ("Smarter LED-Streifen 10m", "App-gesteuerter RGB-Lichtstreifen, der sich mit Musik synchronisiert, 16 Millionen Farben und Sprachsteuerung. Verwandelt das Jugendzimmer oder Gaming-Setup."),
  ("10m Akıllı LED Şerit", "Müzikle senkronize olan, 16 milyon renkli ve sesli kontrollü uygulama kontrollü RGB şerit. Genç odasını veya oyun kurulumunu dönüştürür."),
  ("Slimme LED-strip 10 m", "App-gestuurde RGB-lichtstrip die meebeweegt op muziek, met 16 miljoen kleuren en spraakbediening. Maakt van een tienerkamer een gaming setup."),
  ("Ruban LED connecté 10 m", "Ruban RGB piloté par appli, synchronisé avec la musique, 16 millions de couleurs et commande vocale. Transforme la chambre d'un ado ou un setup gaming."))

c("student_desk_set", "unisex", ["teen", "young_adult"], ["graduation", "birthday"], ["tech", "bookworm"], (25, 70), "🎓",
  ("Graduation Desk Organiser with Lamp", "Bamboo desk organiser, LED lamp with wireless phone charging and a leather notebook. Sets up a student for university life."),
  ("Schreibtisch-Set mit Lampe zum Abschluss", "Bambus-Organizer, LED-Lampe mit kabellosem Handy-Laden und Ledernotizbuch. Die perfekte Ausstattung für den Studienstart."),
  ("Lambalı Mezuniyet Masa Düzenleyici Seti", "Bambu masa düzenleyici, kablosuz telefon şarjlı LED lamba ve deri defter. Üniversite hayatına başlayan öğrenciye tam donanım."),
  ("Bureau organizer met lamp voor afstuderen", "Bamboe bureau-organizer, LED-lamp met draadloos opladen en een leren notitieboek. Klaar voor het studentenleven."),
  ("Set de bureau avec lampe pour diplômé", "Organiseur de bureau en bambou, lampe LED avec chargeur sans fil et carnet en cuir. Pour bien démarrer la vie étudiante."))

# ---------------------------------------------------------------- couples / wedding
c("couples_photo_album", "unisex", ["young_adult", "adult"], ["anniversary", "valentines", "wedding"], ["homebody", "artist"], (20, 60), "💑",
  ("Personalised Couple's Photo Album", "Linen photo album embossed with your names and date, 60 pages for the story of your relationship. A romantic anniversary gift."),
  ("Personalisiertes Fotoalbum für Paare", "Leinen-Fotoalbum mit geprägten Namen und Datum, 60 Seiten für die Geschichte eurer Beziehung. Ein romantisches Jahrestagsgeschenk."),
  ("Kişiye Özel Çift Fotoğraf Albümü", "İsimleriniz ve tarih kabartmalı keten fotoğraf albümü, ilişkinizin hikayesi için 60 sayfa. Romantik bir yıldönümü hediyesi."),
  ("Gepersonaliseerd fotoalbum voor stellen", "Linnen fotoalbum met jullie namen en datum, 60 pagina's voor het verhaal van jullie relatie. Een romantisch jubileumcadeau."),
  ("Album photo personnalisé pour couple", "Album en lin embossé de vos prénoms et de la date, 60 pages pour l'histoire de votre couple. Un cadeau d'anniversaire romantique."))

c("star_map_print", "unisex", ["young_adult", "adult"], ["anniversary", "valentines", "wedding", "new_baby"], ["artist", "homebody"], (20, 70), "✨",
  ("Custom Star Map Print", "The night sky exactly as it looked on your special date and place, printed on museum-quality paper. Framed option available."),
  ("Personalisierte Sternenkarte", "Der Nachthimmel genau so, wie er an eurem besonderen Datum und Ort aussah, gedruckt auf Museumspapier. Auch gerahmt erhältlich."),
  ("Kişiye Özel Yıldız Haritası", "Özel tarihiniz ve yerinizdeki gece gökyüzü, müze kalitesinde kağıda basılmış. Çerçeveli seçenek mevcut."),
  ("Gepersonaliseerde sterrenkaart", "De sterrenhemel precies zoals die eruitzag op jullie bijzondere datum en plaats, gedrukt op museumkwaliteit papier. Ook ingelijst."),
  ("Carte du ciel personnalisée", "Le ciel étoilé tel qu'il était à votre date et lieu spéciaux, imprimé sur papier qualité musée. Option encadrée."))

c("wedding_cutting_board", "unisex", ["young_adult", "adult"], ["wedding", "anniversary", "housewarming"], ["foodie", "homebody"], (25, 70), "💍",
  ("Engraved Walnut Cutting Board for Couples", "Solid walnut board engraved with the couple's surname and wedding date. A keepsake for the newlyweds' kitchen."),
  ("Graviertes Walnuss-Schneidebrett für Paare", "Massives Walnussbrett mit Gravur von Familienname und Hochzeitsdatum. Ein Erinnerungsstück für die Küche des Brautpaars."),
  ("Çiftlere Özel Kazınmış Ceviz Kesme Tahtası", "Çiftin soyadı ve düğün tarihi kazınmış masif ceviz tahta. Yeni evlilerin mutfağı için bir hatıra."),
  ("Gegraveerde walnoten snijplank voor stellen", "Massief walnoten plank gegraveerd met achternaam en trouwdatum. Een aandenken voor de keuken van het bruidspaar."),
  ("Planche à découper en noyer gravée pour couple", "Planche en noyer massif gravée du nom de famille et de la date du mariage. Un souvenir pour la cuisine des jeunes mariés."))

c("date_night_box", "unisex", ["young_adult", "adult"], ["valentines", "anniversary", "wedding"], ["homebody", "foodie"], (25, 60), "❤️",
  ("Date Night Idea Box for Couples", "52 scratch-off date ideas, from cooking challenges to stargazing, with a couple's journal. Keeps the romance alive all year."),
  ("Date-Night-Box für Paare", "52 Rubbelkarten mit Date-Ideen, von Kochduellen bis Sternegucken, plus Paar-Tagebuch. Hält die Romantik das ganze Jahr lebendig."),
  ("Çiftler için Randevu Gecesi Kutusu", "Yemek yarışmasından yıldız izlemeye 52 kazı-kazan randevu fikri ve çift günlüğü. Romantizmi yıl boyu canlı tutar."),
  ("Date night box voor stellen", "52 kraskaarten met date-ideeën, van kookuitdagingen tot sterren kijken, plus een koppeldagboek. Houdt de romantiek het hele jaar levend."),
  ("Box de soirées en amoureux", "52 idées de rendez-vous à gratter, du défi cuisine à l'observation des étoiles, avec un journal de couple. La romance toute l'année."))

c("flower_bouquet", "female", ["young_adult", "adult", "senior"], ["valentines", "mothers_day", "birthday", "anniversary", "get_well", "thank_you"], ["homebody", "gardener"], (25, 80), "💐",
  ("Fresh Rose and Lily Bouquet Delivery", "Hand-tied bouquet of red roses and white lilies delivered to the door with a personal card. The classic romantic gesture."),
  ("Rosen- und Lilienstrauß mit Lieferung", "Handgebundener Strauß aus roten Rosen und weißen Lilien, mit persönlicher Karte an die Haustür geliefert. Die klassische romantische Geste."),
  ("Taze Gül ve Zambak Buketi Teslimatı", "Kapıya teslim, kişisel kartlı el yapımı kırmızı gül ve beyaz zambak buketi. Klasik romantik jest."),
  ("Vers boeket rozen en lelies bezorgd", "Handgebonden boeket rode rozen en witte lelies aan huis bezorgd met een persoonlijk kaartje. Het klassieke romantische gebaar."),
  ("Bouquet de roses et lys livré", "Bouquet de roses rouges et lys blancs lié à la main, livré à domicile avec une carte personnelle. Le geste romantique par excellence."))

# ---------------------------------------------------------------- seniors / retirement
c("retirement_watch_box", "male", ["senior"], ["retirement"], ["fashion", "homebody"], (40, 120), "🎁",
  ("Engraved Retirement Watch Box", "Wooden watch display case engraved with a retirement message, holding six timepieces. A dignified gift for a long career."),
  ("Gravierte Uhrenbox zum Ruhestand", "Hölzerne Uhrenbox mit eingravierter Ruhestandsbotschaft für sechs Uhren. Ein würdiges Geschenk für ein langes Berufsleben."),
  ("Kazınmış Emeklilik Saat Kutusu", "Emeklilik mesajı kazınmış, altı saat alan ahşap saat kutusu. Uzun bir kariyere yakışır bir hediye."),
  ("Gegraveerde horlogebox voor pensioen", "Houten horlogekist gegraveerd met een pensioenboodschap, plaats voor zes horloges. Een waardig cadeau voor een lange carrière."),
  ("Coffret à montres gravé pour la retraite", "Écrin en bois gravé d'un message de départ en retraite, pour six montres. Un cadeau digne d'une longue carrière."))

c("birdfeeder_camera", "unisex", ["adult", "senior"], ["retirement", "birthday", "christmas", "fathers_day"], ["gardener", "outdoor", "tech"], (60, 180), "🐦",
  ("Smart Bird Feeder with Camera", "Solar-powered feeder with an HD camera that identifies visiting birds and sends clips to a phone. Brings nature to the garden and the sofa."),
  ("Smartes Vogelhaus mit Kamera", "Solarbetriebenes Futterhaus mit HD-Kamera, das Vögel erkennt und Clips aufs Handy schickt. Bringt die Natur in den Garten und aufs Sofa."),
  ("Kameralı Akıllı Kuş Yemliği", "Gelen kuşları tanıyıp telefona video gönderen HD kameralı güneş enerjili yemlik. Doğayı bahçeye ve koltuğa getirir."),
  ("Slimme vogelvoeder met camera", "Voederhuisje op zonne-energie met HD-camera die vogels herkent en clips naar de telefoon stuurt. Natuur in de tuin en op de bank."),
  ("Mangeoire connectée avec caméra", "Mangeoire solaire avec caméra HD qui identifie les oiseaux et envoie des vidéos sur le téléphone. La nature au jardin et dans le canapé."))

c("large_print_puzzle_book", "unisex", ["senior"], ["get_well", "birthday", "christmas", "retirement"], ["bookworm", "homebody"], (10, 25), "📰",
  ("Large Print Crossword and Sudoku Collection", "Three spiral-bound books of large-print crosswords, sudoku and word searches with a soft-grip pen. Keeps the mind sharp and entertained."),
  ("Großdruck-Rätselbuch-Sammlung", "Drei Spiralbücher mit Kreuzworträtseln, Sudoku und Wortsuche in Großdruck, plus Stift mit Softgriff. Hält den Geist fit und unterhalten."),
  ("Büyük Puntolu Bulmaca Kitabı Seti", "Büyük puntolu çapraz bulmaca, sudoku ve kelime avı içeren üç spiralli kitap ve yumuşak tutuşlu kalem. Zihni canlı ve eğlenceli tutar."),
  ("Grootletter puzzelboeken set", "Drie spiraalgebonden boeken met kruiswoordpuzzels, sudoku en woordzoekers in grote letters, met een pen. Houdt de geest scherp."),
  ("Collection de mots croisés et sudoku en gros caractères", "Trois cahiers à spirale de mots croisés, sudoku et mots mêlés en gros caractères avec un stylo ergonomique. Garde l'esprit vif."))

c("heated_blanket", "unisex", ["adult", "senior"], ["christmas", "get_well", "mothers_day", "birthday"], ["homebody", "wellness"], (35, 90), "🔥",
  ("Electric Heated Throw Blanket", "Soft fleece throw with six heat settings, auto shut-off and a machine-washable design. Comfort for cold evenings and aching joints."),
  ("Elektrische Heizdecke", "Weiche Fleece-Decke mit sechs Wärmestufen, automatischer Abschaltung und maschinenwaschbar. Wohltuend an kalten Abenden und bei Gelenkschmerzen."),
  ("Elektrikli Isıtmalı Battaniye", "Altı ısı ayarı, otomatik kapanma ve makinede yıkanabilir yumuşak polar battaniye. Soğuk akşamlar ve ağrıyan eklemler için konfor."),
  ("Elektrische warmtedeken", "Zachte fleece deken met zes warmtestanden, automatische uitschakeling en wasbaar in de machine. Comfort op koude avonden."),
  ("Plaid chauffant électrique", "Plaid polaire doux avec six niveaux de chaleur, arrêt automatique et lavable en machine. Du réconfort pour les soirées froides."))

# ---------------------------------------------------------------- experiences / misc
c("cooking_class_voucher", "unisex", ["young_adult", "adult"], ["birthday", "anniversary", "christmas", "thank_you"], ["foodie", "maker"], (50, 150), "👨‍🍳",
  ("Cooking Class Gift Voucher", "A hands-on cooking workshop with a professional chef, from sushi to Italian pasta, redeemable in major cities. An experience gift that creates memories."),
  ("Kochkurs-Gutschein", "Praktischer Kochworkshop mit Profikoch, von Sushi bis Pasta, einlösbar in vielen Städten. Ein Erlebnisgeschenk, das Erinnerungen schafft."),
  ("Yemek Kursu Hediye Çeki", "Suşiden İtalyan makarnasına profesyonel şefle uygulamalı yemek atölyesi, büyük şehirlerde geçerli. Anı biriktiren bir deneyim hediyesi."),
  ("Kookworkshop cadeaubon", "Een praktische kookworkshop met een professionele chef, van sushi tot Italiaanse pasta, inwisselbaar in grote steden. Een belevenis als cadeau."),
  ("Bon cadeau cours de cuisine", "Atelier de cuisine avec un chef professionnel, des sushis aux pâtes italiennes, valable dans les grandes villes. Une expérience à offrir."))

c("gift_card_generic", "unisex", ["teen", "young_adult", "adult", "senior"], ["birthday", "christmas", "graduation", "thank_you"], ["fashion", "tech"], (25, 100), "💳",
  ("Digital Gift Card", "An instant e-gift card in any amount, delivered by email with a personal message. The safe choice when you do not know what they want."),
  ("Digitaler Geschenkgutschein", "Sofort per E-Mail gelieferter Gutschein in beliebigem Betrag mit persönlicher Nachricht. Die sichere Wahl, wenn man den Wunsch nicht kennt."),
  ("Dijital Hediye Kartı", "E-posta ile anında gönderilen, istediğiniz tutarda ve kişisel mesajlı hediye kartı. Ne istediğini bilmediğinizde güvenli seçim."),
  ("Digitale cadeaukaart", "Direct per e-mail bezorgde cadeaubon in elk bedrag met persoonlijke boodschap. De veilige keuze als je niet weet wat ze willen."),
  ("Carte cadeau numérique", "Carte cadeau électronique du montant de votre choix, envoyée par e-mail avec un message personnel. Le choix sûr quand on hésite."))

c("lego_architecture", "unisex", ["teen", "young_adult", "adult"], ["birthday", "christmas", "fathers_day"], ["maker", "traveler", "homebody"], (40, 150), "🧱",
  ("Architecture Building Brick Set", "Detailed 1500-piece brick model of a world-famous skyline for display. A relaxing build for adults who never outgrew construction toys."),
  ("Architektur-Klemmbaustein-Set", "Detailliertes 1500-teiliges Modell einer weltberühmten Skyline zum Ausstellen. Entspanntes Bauen für Erwachsene, die Bausteine nie aufgegeben haben."),
  ("Mimari Yapı Taşı Seti", "Sergilemek için dünyaca ünlü bir siluetin 1500 parçalık ayrıntılı modeli. Yapı oyuncaklarını asla bırakmayan yetişkinler için rahatlatıcı bir inşa."),
  ("Architectuur bouwstenen set", "Gedetailleerd model van 1500 steentjes van een wereldberoemde skyline om neer te zetten. Ontspannend bouwen voor volwassenen."),
  ("Set de briques architecture", "Modèle détaillé de 1500 briques d'une skyline mondialement connue à exposer. Une construction relaxante pour les adultes restés enfants."))

c("photo_calendar", "unisex", ["adult", "senior"], ["christmas", "mothers_day", "fathers_day", "anniversary"], ["homebody", "artist"], (12, 35), "📅",
  ("Personalised Photo Wall Calendar", "A 12-month wall calendar printed with your own family photos and marked birthdays. A gift grandparents look at every single day."),
  ("Personalisierter Foto-Wandkalender", "12-Monats-Wandkalender mit eigenen Familienfotos und markierten Geburtstagen. Ein Geschenk, das Oma und Opa jeden Tag ansehen."),
  ("Kişiye Özel Fotoğraflı Duvar Takvimi", "Kendi aile fotoğraflarınız ve işaretli doğum günleriyle 12 aylık duvar takvimi. Büyükanne ve büyükbabanın her gün baktığı bir hediye."),
  ("Gepersonaliseerde fotokalender", "12-maanden wandkalender met je eigen familiefoto's en gemarkeerde verjaardagen. Een cadeau waar opa en oma elke dag naar kijken."),
  ("Calendrier mural photo personnalisé", "Calendrier mural 12 mois imprimé avec vos photos de famille et les anniversaires marqués. Un cadeau que les grands-parents regardent chaque jour."))

c("teacher_gift_set", "female", ["adult"], ["thank_you"], ["bookworm", "coffee_tea"], (15, 40), "🍎",
  ("Thank You Teacher Gift Set", "A tote bag, insulated tumbler, notebook and pen printed with a thank-you message for the best teacher. Perfect for end of school year."),
  ("Dankeschön-Set für Lehrerinnen", "Stofftasche, Thermobecher, Notizbuch und Stift mit Dankesbotschaft für die beste Lehrerin. Ideal zum Schuljahresende."),
  ("Öğretmene Teşekkür Hediye Seti", "En iyi öğretmene teşekkür mesajlı bez çanta, termos bardak, defter ve kalem. Dönem sonu için ideal."),
  ("Bedankt juf cadeauset", "Een tas, isolerende drinkbeker, notitieboek en pen bedrukt met een bedankje voor de beste juf. Perfect voor het einde van het schooljaar."),
  ("Coffret cadeau merci maîtresse", "Tote bag, gobelet isotherme, carnet et stylo imprimés d'un message de remerciement pour la meilleure maîtresse. Pour la fin d'année scolaire."))

c("get_well_care_package", "unisex", ["young_adult", "adult", "senior"], ["get_well"], ["wellness", "homebody"], (25, 60), "🩹",
  ("Get Well Soon Care Package", "Herbal tea, honey, fuzzy socks, a soothing balm, a puzzle book and a handwritten card. Comfort for a friend recovering at home or in hospital."),
  ("Gute-Besserung-Paket", "Kräutertee, Honig, kuschelige Socken, Balsam, Rätselheft und handgeschriebene Karte. Trost für Freunde, die zu Hause oder im Krankenhaus genesen."),
  ("Geçmiş Olsun Bakım Paketi", "Bitki çayı, bal, yumuşak çorap, rahatlatıcı balsam, bulmaca kitabı ve el yazısı kart. Evde veya hastanede iyileşen bir dosta moral."),
  ("Beterschap verwenpakket", "Kruidenthee, honing, warme sokken, een verzachtende balsem, een puzzelboek en een handgeschreven kaart. Troost voor een herstellende vriend."),
  ("Colis de réconfort bon rétablissement", "Tisane, miel, chaussettes douillettes, baume apaisant, livre de jeux et carte manuscrite. Du réconfort pour un ami en convalescence."))

c("doormat_personalised", "unisex", ["young_adult", "adult"], ["housewarming", "wedding"], ["homebody"], (20, 45), "🚪",
  ("Personalised Coir Doormat", "Natural coir doormat printed with the family name or a welcome message of your choice. The first thing guests see at a new home."),
  ("Personalisierte Kokos-Fußmatte", "Fußmatte aus Naturkokos mit Familiennamen oder Willkommensspruch nach Wahl. Das Erste, was Gäste im neuen Zuhause sehen."),
  ("Kişiye Özel Koko Paspas", "Aile adı veya istediğiniz karşılama mesajı baskılı doğal koko paspas. Yeni evde misafirlerin gördüğü ilk şey."),
  ("Gepersonaliseerde kokos deurmat", "Natuurlijke kokosmat bedrukt met de familienaam of een welkomstboodschap naar keuze. Het eerste wat gasten zien bij het nieuwe huis."),
  ("Paillasson en coco personnalisé", "Paillasson en fibre de coco imprimé du nom de famille ou d'un message de bienvenue. La première chose que voient les invités."))

c("smart_plant_pot", "unisex", ["young_adult", "adult"], ["housewarming", "birthday", "christmas"], ["gardener", "tech", "homebody"], (30, 80), "🪴",
  ("Self-Watering Smart Planter", "Ceramic planter with a water reservoir and app alerts for light and moisture. Keeps houseplants alive for people who forget to water."),
  ("Selbstbewässernder Smart-Blumentopf", "Keramiktopf mit Wasserreservoir und App-Hinweisen zu Licht und Feuchtigkeit. Hält Zimmerpflanzen am Leben, auch wenn man das Gießen vergisst."),
  ("Kendi Kendini Sulayan Akıllı Saksı", "Su hazneli ve ışık ile nem için uygulama uyarılı seramik saksı. Sulamayı unutanlar için ev bitkilerini hayatta tutar."),
  ("Zelfwaterende slimme bloempot", "Keramische pot met waterreservoir en app-meldingen voor licht en vocht. Houdt kamerplanten in leven voor wie water geven vergeet."),
  ("Pot de fleurs connecté à réserve d'eau", "Pot en céramique avec réservoir et alertes sur l'application pour la lumière et l'humidité. Pour ceux qui oublient d'arroser."))
