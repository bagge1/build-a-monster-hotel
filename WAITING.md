# Väntar på August

Allt som väntar på dig, på ett ställe. Det du har svarat på stryks
(`~~punkten~~`) med var svaret hamnade. Spelets egna engelska namn behålls.

Håll listan kort: bara det du kan titta på eller bestämma den här veckan.
Designfrågor som inte brådskar står i `docs/GDD.md` (§17) tills de gör det.

## §0 I Studio: import och Connect

<!-- En import: vilken mapp i blender/_import/ du väljer i dialogen.
Connect: knappen under fliken Plugins i Studio. -->

1. ~~**Starta om `rojo serve`** och tryck **Connect**~~ (gjort 2026-10-19:
   de nya mappningarna för `assets/Monsters`, `assets/HotelKit/HauntedManor`
   och `assets/HotelKit/FrostfangLodge` är igång; noterat i
   `archive/NATTLOGG-2026-10-19.md`).
2. ~~**Importera allt, 69 modeller i en import**~~ (gjort 2026-10-19:
   alla 69 inställda, kontrollerade och sparade i `assets/Monsters/`,
   `assets/HotelKit/HauntedManor/` och `assets/HotelKit/FrostfangLodge/`).
3. **Starta om `rojo serve` en gång till** (2026-10-19) och tryck **Connect**
   under fliken **Plugins** i Studio. Mapparna `assets/Monsters` och
   `assets/HotelKit/...` fanns inte när Rojo startade i morse, och Rojo läser
   bara in sådana mappar när det startar (`DEVNOTES.md`). Tills dess syns inga
   av de nya modellerna i spelet. Samma omstart tar också med den nya mappen
   `assets/Cosmetics` (för kosmetikans modeller senare). Säg till när det är gjort; modellerna i
   Workspace ligger kvar tills Claude har sett att de kommit fram.

## §1 Att titta på eller spela

<!-- Det bara en människa kan bedöma: hur det känns, hur det ser ut.
Med Claudes skärmdump där det finns en. -->

1. **Spela första kvarten** (2026-10-19). Tryck **Play** i Studio: Gloom leder
   dig genom bygga, checka in, kassan, bussen, en Slime som flyttar in, Coffin
   Suite och städning. Allt du ser är grå blockout-utkast (inga modeller än);
   utseendet är ditt att döma. Säg i vanliga ord vad som känns fel.
2. **Utseendet på gränssnittet** (2026-10-19): lila paneler, orange/turkos
   knappar, typsnittet Fredoka One, Gloom-bubblan högst upp i mitten. Nattens
   utkast; inget är bestämt.
3. **Store med presentknappar** (2026-10-19): bilden
   `archive/screens/2026-10-19_store_gifts.jpg`. En **🎁 Gift**-knapp på varje
   pass, raden för att välja mottagare överst. Nattutkast; utseendet är ditt.

4. **Kosmetika för hotellet** (2026-10-19, nattutkast): bilden
   `blender/cosmetics/hotel/review/front.png` (fler i samma mapp). Pumpkin
   sign, Icicle sign, Lantern sign, två familjevapen (Haunted Manor och
   Frostfang) och Bat bunting och Fairy lights över entrén, på båda hotellens
   skyltar och valv. Inget är importerat än; utseendet är ditt.

5. **Boo! på avstånd** (2026-10-19): servern godtar Boo! på 35 studs, men
   Claude kan inte se om knappen syns på skärmen så långt bort. När du spelar
   en Hunter Night: syns Boo! och fungerar den på ungefär 35 studs?

## §2 Beslut

<!-- En fråga i taget, med alternativen och Claudes rekommendation. -->

1. **Nattens utkast i GDD Appendix A** (2026-10-19). Allt som GDD:n inte
   bestämde valde natten som ett utkast så att spelet kunde byggas: priser på
   rum utöver Standard Room, decor och amenities, satisfaction-formeln,
   rating-formeln, hur walk-ins kommer, Frostfang Lodges arter och rum, Moon
   Tree-noderna, Hunter Night-detaljerna. Varje tal är märkt `PLACEHOLDER` i
   `src/shared/Constants.luau`. **Rekommendation:** spela först, läs sedan A.2
   (priser) och A.3 (satisfaction): det är de som styr hur det känns. Inget är
   ditt beslut förrän du sagt det.

2. **Frostfang Lodges startpengar** (2026-10-19). Efter en rebirth har man
   GDD:ns $100 (§6.3), men Frostfangs billigaste rum (Igloo Room) är nattens
   platshållare $1 000, och Frostfangs walk-ins kräver det rummet. Man kommer
   inte fast: residents tjänar ihop det (en Vampire Count på ungefär en minut).
   **Alternativ:** (a) behåll; (b) startpengar ×20 per location ($2 000 i
   Frostfang); (c) billigare Igloo Room. **Rekommendation:** (b), så att andra
   rundan börjar lika snabbt som den första.
3. **Gratis Coffin Suite i tutorialen** (2026-10-19). §11 vill att en Vampire
   Count kommer efter 10–15 minuter, men Coffin Suite kostar $40 000
   (platshållare) och kräver 3.5★. Natten lät Gloom låsa upp den och ge den
   första gratis (Appendix A.7). **Alternativ:** (a) gratis som nu; (b) ett
   tutorialpris; (c) ingen Vampire i tutorialen, bara målkortet.
   **Rekommendation:** (a), det är "moment of joy" som §11 bygger på.
4. **Gloom** (GDD §17 fråga 6): namnet och utseendet. Han är just nu en
   fladdermus-emoji i en pratbubbla.
5. **Co-managers** (GDD §7: en vän med byggrätt som får 10 % av inkomsten hen
   skapar) är inte byggt. Det behöver ett beslut om vad en co-manager får göra
   (bygga? sälja? flytta?) och om det ska kräva vänskap på Roblox.
   **Rekommendation:** bygga och placera, aldrig sälja; bara Roblox-vänner.

6. **Presentversioner av passen** (GDD §10.1 punkt 4) är **byggda som
   rekommendationen** (2026-10-19, GDD Appendix A.9): en knapp **🎁 Gift** på
   varje pass i Store, man väljer en spelare på samma gata, och presenten
   sparas hos mottagaren som om passet var köpt (den kommer fram även om hen
   har gått). Priset är passets eget (platshållare). **Att bestämma:** är det
   rätt, eller ska man kunna ge till vänner som inte är på servern?
   Produkterna behövs i Creator Hub (§3.2).

7. **Ekonomins takt** (2026-10-19, `archive/BALANCE-2026-10-19.md`, modellen
   `tools/balance_model.py`). Inga värden är ändrade; det här är mätningar mot
   §6.3. Med tutorialen går rebirth att göra efter 1:02 (målet 60–90 min).
   Utan tutorialen tar det ungefär **4 timmar**, och flaskhalsen är Vampire
   Count som resident: 10 glada vistelser (§4.2) med Vampires bara på :00/:30-
   bussarna. Andra fynd: ratingen når 5★ på 20–45 minuter (recensionerna blir
   nästan alltid 5★, och Fun/Style fylls billigt), inkomsten slutar växa efter
   30–45 minuter (walk-ins högst var 8:e sekund, tre våningar fulla), och köp
   kostar oftast långt under 2–5 minuters inkomst (§6.2). Rapporten ger ett par
   alternativ per fynd; **valet är ditt**. **Rekommendation:** läs fynd 2 och 3
   först (Vampire-flaskhalsen och ratingen), de styr mest.
   Natten rättade två saker som var buggar mot designen, inte värden: bara
   tutorialens Slime behöver 1 friendship (Vampire Count räknades också), och
   tutorialens Vampire kommer nu tre bussar efter målkortet (§11), inte direkt.

8. **Winter-eventet** (GDD §8.2 "Frostfang crossover", byggt som nattutkast
   2026-10-19, Appendix A.10): Winter har en egen valuta, **Snowflakes** ❄,
   som tjänas som Candy, och en Winter shop (Snowman decor 30, Icicle sign
   60, Fairy lights 90). **Att bestämma:** räcker det som crossover, eller ska
   Frostfang-gäster också åka med Night Bus till Haunted Manor under Winter?
   Då behöver de ett rum där (t.ex. vilket rum som helst av rätt storlek).
   **Rekommendation:** ja, ett Frostfang-monster per buss ibland, i ett
   Standard Room; det är det som gör det till en crossover.

9. **Skyltens eget vapen när man bär en skylt-kosmetika** (2026-10-19). Varje
   hotells skylt har redan ett gavelvapen ovanför tavlan (månen, snöflingan).
   Familjevapnen (kosmetika) står framför det och döljer mitten av det.
   **Alternativ:** (a) behåll båda; (b) dölj skyltens eget vapen medan en
   skylt-kosmetika bärs; (c) dölj det bara för familjevapnen.
   **Rekommendation:** (c): ramarna (pumpa, istappar, lyktor) passar ihop med
   gaveln, vapnen gör det inte.

## §3 Creator Hub och publicering

1. ~~**Slå på Studio Access to API Services**~~ (gjort 2026-10-19: på i
   Experience Settings; save och load provas nu, resultatet i
   `archive/NATTLOGG-2026-10-19.md` och memory `phase-status`).
2. **Skapa passen och produkterna i Creator Hub** (2026-10-19). GDD §10.2:s
   fem pass (Auto-Collect Till 149, Night Manager 249, Resident Wing+ 249,
   Extra Floor 299, VIP Lobby 399) och nio produkter (Starter Pack 99, Call the
   Bus 39, 2x Cash 49 och 149, 2x Friendship 79, Cash Pouch/Sack/Vault 49/149/449,
   och en gratis "2x Cash (ad)" som rewarded ad-belöning), plus fyra
   facade packs som pass (Gothic 99, Neon 149, Candy 199, Pirate 249: GDD:ns
   spann 99–249, priserna är platshållare att bestämma) och nio
   presentprodukter, en per pass ("Gift: Auto-Collect Till" osv., samma pris
   som passet, §2.6). Ge Claude id:na så
   skrivs de in i `src/shared/Store.luau`; tills dess står de som "Soon".
   Ikoner till dem ritas i natt (`ui/`). Slå också på **Managed Pricing** (§10.1).
3. **Notifikationer** (GDD §9): spelet ber om opt-in efter första move-in, men
   att *skicka* dem kräver Open Cloud utifrån. Säg till när det är dags.
4. **Översättning** (GDD §9: engelska, spanska, portugisiska, japanska): slå på
   **Automatic translation** för experiencen i Creator Hub (Localization).
   Spelets texter är engelska och kan översättas automatiskt.
5. **Grupp-belöningen** (GDD §9: gratis decor och +5 % cash för den som går med
   i gruppen): vilken grupp? Säg dess id så byggs belöningen.

