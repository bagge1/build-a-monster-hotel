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
3. ~~**Starta om `rojo serve` en gång till**~~ (gjort 2026-10-19: alla 69
   modeller har kommit fram och stämmer del för del med importen; noterat i
   setens `README.md`).
4. ~~**Importera elva modeller**~~ (gjort 2026-10-19: alla elva inställda,
   sparade och synkade; lobbyn är strålad och gången, `TESTRUN.md` fas 10).
5. ~~**Importera 27 modeller i den dubbla skalan**~~ (gjort 2026-10-19:
   alla 27 inställda, sparade och synkade; hotellet gånget och strålat,
   `TESTRUN.md` fas 11.) Båda
   hotellens rum, bekvämligheter, `Lobby`, `StairCore` och `StairCoreTop`,
   ombyggda i den nya skalan (en cell 12 studs, en våning 18, väggarna upp
   till bjälklaget). Importera **alla filer i `blender/_import/`** till
   **Workspace** i en dialog och skriv *importerat*. Frostfangs tre som
   delar namn med Haunted Manors heter `FrostfangLodge_...` i mappen; Claude
   döper om dem. Skylten och dekoren är oförändrade och ingår inte. Bilden:
   `archive/screens/2026-10-19_doubled_scale.jpg` (övre raden Haunted Manor,
   nedre Frostfang: gatan, lobbyn mot disken, ett rum, trappan).

6. ~~**Importera 25 modeller igen**~~ (gjort 2026-10-19: alla 25 inställda,
   sparade och synkade, `TESTRUN.md` fas 11) (2026-10-19, granskningen i spelet):
   trappans ledstång stack upp genom våningen ovanför, och dörrkarmarna gick
   högre än bågen. Alla rum och bekvämligheter och båda hotellens
   `StairCore` och `StairCoreTop`. Importera **alla filer i
   `blender/_import/`** till **Workspace** i en dialog och skriv
   *importerat*. Gatlyktorna står nu parvis vid varje entré (koden, ingen
   import).

7. ~~**Importera fyra modeller**~~ (gjort 2026-10-19: alla fyra inställda, sparade och synkade; tavlorna sitter över dörrarna i spelet) (2026-10-19, dina rapporter från spelet): båda
   lobbyerna och den nya trätavlan över rumsdörrarna (`RoomPlaque`, en per
   hotell: mörkt trä med guldkant i Haunted Manor, timmer med vit kant i
   Frostfang; namnet och tier skrivs på den, tillståndet på en andra rad). I
   lobbyerna: mattans
   slut efter svängen mot disken var rött utan guldkant, och kassan var vänd
   mot gästerna och stod för nära klockan (nu 4,4 studs isär, tangenterna
   mot den som står bakom disken). Alla fyra ligger i `blender/_import/`. Importera **alla
   filerna** till **Workspace** i en dialog och skriv *importerat* (inte mitt
   i en playtest).

8. **Importera fem träd** (2026-10-19, skogen runt gatan; grenen är
   **ihopslagen i main 2026-10-19 20:27**, så det kan göras nu): först **starta
   om `rojo serve`** och tryck **Connect** (fliken **Plugins** i Studio):
   grenen lägger till mappen `assets/Scenery`, som Rojo bara ser efter en
   omstart. Sedan importerar du de fem `Tree_*.fbx` i `blender/_import/`
   (`Tree_Crooked`, `Tree_Bare`, `Tree_Hollow`, `Tree_Fir`,
   `Tree_SnowFir`) till **Workspace** och skriver *importerat*. Ligger det
   filer där från en annan session vars import också står här, ta allt i en
   dialog. Tills träden är importerade ritar spelet enkla klossträd på samma
   platser. Bilden: `blender/street/trees/review/sheet.png`.

9. **Importera 52 modeller: att bygga fritt** (2026-10-19, grenen
   `claude/free-building-4b66e3`; grenen är **ihopslagen i main 2026-10-19
   kväll**, så importera nu; tills dess står lobbyn utan disk i spelet; ta
   den i samma dialog som träden i punkt 8, alla 57 filer). Båda hotellens
   lobby blir ett skal (golv, framvägg, valv), disken med kassan och
   nyckeltavlan blir en egen bit (`FrontDesk`), bänkarna, krukorna och mattan
   blir dekor (`Decor_Bench`, `Decor_UrnPlanter`, `Decor_RugRunner`,
   `Decor_RugCorner`, `Decor_RugSquare`), all dekor passar rutnätet av 3 studs,
   och rummens golv är en enda del (mattan i rummet är skild från golvet, så
   att ett valt golv kan läggas på). Importera **alla filer i
   `blender/_import/`** till **Workspace** i en dialog och skriv
   *importerat*. Frostfangs som delar namn med Haunted Manors heter
   `FrostfangLodge_...` i mappen; Claude döper om dem. Bilden:
   `archive/screens/2026-10-19_lobby_shell_desk.jpg` (lobbyn uppifrån med
   disken, bänken, krukorna och mattorna).

## §1 Att titta på eller spela

<!-- Det bara en människa kan bedöma: hur det känns, hur det ser ut.
Med Claudes skärmdump där det finns en. -->

1. **Spela första kvarten** (2026-10-19). Tryck **Play** i Studio: Gloom leder
   dig genom bygga, checka in, kassan, bussen, en Slime som flyttar in, Coffin
   Suite och städning. Rummen, lobbyn, trapporna, monstren och bussen är nu
   de riktiga modellerna (se punkt 6); utseendet är ditt att döma. Säg i vanliga ord vad som känns fel.
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

6. **De riktiga modellerna i spelet** (2026-10-19): bilderna
   `archive/screens/2026-10-19_real_models_hotel.jpg` (hotellet med alla
   rum från kitet) och `archive/screens/2026-10-19_real_models_bus.jpg`
   (Night Bus med gäster). Allt är byggt av de importerade modellerna nu;
   strukturen är kontrollerad (trappor gångna, golv och dörrar med strålar).
   Hur det ser ut är ditt.

7. ~~**Den nya lobbyn**~~ (besvarat 2026-10-19: du godkände utseendet, layout A
   i båda hotellen och skylten i förgårdens hörn; noterat i setens `README.md`.
   Claude ser den i spelet efter importen, §0 punkt 4.)

8. **Gatan, när grenen är ihopslagen** (2026-10-19): förgården framför
   varje hotell (trottoaren, gräsytan, gången fram till valvet, skylten i
   hörnet, fällorna bredvid gången), Night Bus som kör ut ur skogen runt
   kröken i väster, stannar vid x = −90 och 90 och kör in i skogen igen i
   öster, gästerna som strövar på trottoarerna och stannar en stund vid
   varje entré, och skogen runt gatan. Claude spelar igenom det först
   (`TESTRUN.md` fas 12); utseendet och känslan är dina.

9. **Ett fullt hotell och skogen på en riktig telefon** (2026-10-19 kväll,
   efter importen i §0.8–0.9). Mätt i Studio: ett fullt hotell är 1 642
   delar (budgeten ~3 000) och 110 punktljus (51 rumslampor, 49 ljus i
   dekoren); skogen är 677 träd. Studio kan inte visa hur en telefon klarar
   det. Spela en stund på din telefon med ett fullt hotell och säg om det
   hackar; då mäter Claude vad som drar mest.

10. **Kassan och disken med E** (2026-10-19 kväll). Kassans prompt och
   diskens sitter 3 studs isär, båda på E, och bara en av dem visas åt
   gången. Claude kunde inte utlösa kassans prompt bredvid diskens
   (inkasseringen gick via HUD:ens Collect). Prova i spelet: står du vid
   disken, går det lätt att välja kassan? Säg till om det är krångligt.

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

10. ~~**Lobbyns disk står framför rumsdörrar**~~ (besvarat 2026-10-19: du
   sa att skylten står mitt framför entrén, att man inte kan stå vid disken
   och att lobbyn är en uteplats med en disk, inte en reception. Reglerna står
   i `.claude/skills/modelling/taste.md`. Lobbyn och skylten görs om; Claude
   visar grå silhuetter först. Ett nytt steg, skill `blind-review`, låter en
   annan modell utan sammanhang granska bilderna innan du ser dem.)

11. **Lobbyns utseende: det granskarna såg som är ditt** (2026-10-19,
   blind granskning i tre rundor, setens `README.md`). Fyra saker, med Claudes
   rekommendation:
   - "Lobbyn är en korridor och disken syns inte från dörren." Det följer av
     två rader och layout A. Claude lade en matta från dörren till disken.
     **Rekommendation:** behåll; prova i spelet. En tredje rad kan komma senare.
   - "Fasaden är en platt låda", för Frostfang "blå utanpå, timmer inuti".
     Framväggen kan inte ha relief utåt (inget får stå utanför tomten).
     **Rekommendation:** vänta till fasadbitarna (`Facade_Wall`) görs, så att
     front och sidor blir ett. För Frostfang kan framväggen få timmer utanpå
     redan nu om du vill.
   - "Skylten är en reklamtavla" (16 × 6 studs, Frostfangs gavel smalare än
     tavlan, istappar i huvudhöjd). Skylten är oförändrad, bara flyttad.
     **Rekommendation:** behåll storleken, den ska läsas på en telefon från
     gatan.
   - "Nyckeltavlan hänger för högt" (runda 3), medan runda 1 sa att
     receptionistens huvud skymde den. Nycklarna hänger nu 5–7,3 studs upp.
     **Rekommendation:** behåll; titta i spelet.

12. ~~**Skalan: "dubbla allt, ungefär"**~~ (besvarat 2026-10-19: hela
   rutnätet dubblas, en cell 12 studs, en våning 18 studs, väggarna upp till
   bjälklaget; möbler, dörrar och trappsteg behåller personens storlek. Står i
   `CLAUDE.md`, "The scale of a person", och GDD §3 och §18. Byggs i en egen
   session.)

13. **Den dubbla skalan: det granskarna såg som är ditt** (2026-10-19,
   fem blinda granskningar av renderingarna, setens `README.md`). Det som var
   fel är rättat (väggen över entrén, dörrkarmarna, mattorna, en list och en
   bröstpanel på rummens väggar mot lobbyn, trappans ledstång). Kvar är fyra
   saker som är utseende, med Claudes rekommendation:
   - "Lobbyn är en lång korridor och disken syns inte från dörren." Lobbyn är
     nu 144 × 24 studs, och disken står 60 studs från entrén (layout A, vid
     gaveln bort från trappan). **Rekommendation:** gå den i spelet först; blir
     den tom, möblera sträckan mellan entrén och disken (soffgrupper, mattor),
     hellre än att flytta disken.
   - "Rummen är tomma lådor." Ett 2×2-rum är 24 × 24 × 17 studs med samma säng
     och möbel som förut. **Rekommendation:** en möbelgrupp till i varje rum
     (en fåtölj med ett sidobord, en garderob) och större tavlor; spelarnas
     dekor fyller resten.
   - "Disken når hakan." Disken är 3,8 studs hög, 76 % av en 5-studs person
     (en riktig disk är ungefär 61 %, 3,1 studs). Du godkände disken i
     lobbyomgörningen. **Rekommendation:** sänk till 3,2 när du ser den i
     spelet, om den känns hög.
   - "Fasaden är platt och entrén syns inte" (i alla rundor). Entrébågen är
     dörrstor (9 × 9) i en 144 studs lång vägg, och inget får sticka ut
     utanför tomten. Claude har lagt till en list ovanför fönstren och en
     taklist. **Rekommendation:** som i punkt 11, vänta till fasadbitarna;
     vill du ha entrén mer synlig nu kan bågen bli större (dörrar ska vara
     minst 4 × 7, så bara utseendet bestämmer).
   - Granskningen i spelet: "översta våningen står öppen mot himlen" (inget
     tak) och "fönstren har inget glas". **Rekommendation:** taket med
     fasadbitarna; glas kan koden lägga i fönstren när du vill.
   - Den ljusa rutan mitt på gatan är platsens egen `SpawnLocation` (12 × 12
     studs, från Studios mall); spelet använder den inte, spelarna börjar vid
     lobbyns `Spawn`. **Rekommendation:** ta bort den. Claude kan ta bort den
     i Studio; den är borta för gott när du sparar och publicerar (File →
     Publish to Roblox). **Claude har tagit bort den i Studio (2026-10-19, du
   rapporterade den som en glitch); publicera (File → Publish to Roblox) så
   är den borta för gott.**

14. ~~**Night Bus: det som är öppet**~~ (besvarat 2026-10-19: 40 % av
   gatans lediga rum per buss, en buss var 3:e minut, gästerna strövar förbi
   entréerna i ungefär en minut, och tutorialens första gäst är den enda som
   dyker upp från ingenstans; GDD §4.3 och §18. Gränserna minst 2 och högst 4
   per spelare är Claudes platshållare tills du säger annat.)
15. ~~**"Keep the stairs clear" där det inte finns någon trappa**~~ och
   ~~**köpa tomter**~~ (besvarat 2026-10-19: tomten köps i områden, trappor
   köps och placeras, allt går att bygga om, även receptionen, och man kan
   byta golv och ställa ut mattor och dekor; GDD §5.4 och §18). Det som är
   öppet står i punkt 16.
16. ~~**Att bygga fritt: det som är öppet**~~ (besvarat 2026-10-19: ja till Claudes rekommendationer nedan, alla tal platshållare; GDD §5.4) (2026-10-19, GDD §5.4). Fem frågor,
   med Claudes rekommendation:
   - **Områdena:** 4 × 5 celler (48 × 60 studs) bakom lobbyn, tre i bredd och
     två på djupet, sex per våning. Två 2×2-rum på var sida om en korridor
     ryms i ett, alltså fyra Standard Rooms, som du ville att man börjar med
     (en reception och plats för 2–4 Standard Rooms). Man börjar med det
     mittersta främre. **Rekommendation:** ett
     köpt område gäller alla våningar; priserna är platshållare tills du
     sätter dem.
   - **Trapporna:** en trappa är 2×2 och går från sin våning till våningen
     ovanför, på samma celler. Varje våning måste nås av minst en trappa,
     och den sista trappan till en våning med rum kan inte tas bort.
     **Rekommendation:** när man köper en våning får man den första trappan
     till den gratis att placera.
   - **Receptionen:** disken med kassan och nyckeltavlan blir en bit som man
     flyttar. **Rekommendation:** var som helst på våning 1 där gästerna når
     den från entrén, och bara en. Lobbyn blir då ett skal (golv, framvägg,
     valv), och bänkar och krukor blir dekor.
   - **Dekor:** **Rekommendation:** placeras fritt på ett rutnät av 3 studs
     (en kvarts cell), vrids i 90°, i rum, lobby och korridorer. Ett rums
     önskemål (taggar) kommer från dekoren innanför dess väggar, i stället för
     de tre platserna per rum. Golv väljs per rum, per lobby och för
     korridorerna, från en uppsättning per hotell.
   - **Vilka dekorationer?** Du nämnde klockor, blommor, växter, möbler och
     ett piano. **Att bestämma:** listan för Haunted Manor och vad var och en
     ger (taggar, Style). Claude modellerar dem och visar grå silhuetter
     först.
   - **Tier genom inredning** (din idé, 2026-10-19): möbler, mattor och annan
     dekor i ett rum samlar poäng, och rummet når T2 och till sist T3, och
     varje tier höjer rummets värde (i dag köps T1–T5 för pengar, ×4 per
     tier). **Att bestämma:** poäng per sak och gränserna för T2 och T3.
     **Rekommendation:** varje dekor ger Style-poäng efter sitt pris; T2 vid
     100 och T3 vid 300 för ett 2×2-rum, mer för större rum; varje tier +50 %
     betalning som i dag.
17. ~~**Room Service syns inte**~~ (besvarat 2026-10-19: du vill se personalen
   arbeta, inte stå vid disken; GDD §5.4). Byggs i en egen session: Room
   Service går till rummet och tillbaka, Housekeeping till rummet som ska
   städas, och en "✓" vid dörren när det är klart.
   **Byggt, ihopslaget i main och provkört i Studio 2026-10-19 kväll** (Room Service och Housekeeping går till rummet och tillbaka, "✓" vid dörren; våning 3 provas när fri byggnad är inne):
   tiden är som förut, men aldrig kortare än att den hinner gå dit och stå
   2 s vid dörren, och en anställd tar ett jobb i taget (fler anställda tar
   fler rum samtidigt i stället för ett rum snabbare). Platshållare i GDD
   Appendix A.5; säg till om du vill ha det på något annat sätt.

18. **En skog runt gatan** (byggd 2026-10-19 på grenen
   `claude/street-bus-forest-253849`: importen i §0 punkt 8, frågorna om
   utseendet i punkt 20) (din idé, 2026-10-19: "så det inte ser ut som en
   stor gräsplätt"), och **Night Bus svänger in ur skogen** i stället för att
   dyka upp. Nya modeller (träd: kala, krokiga, några granar för Frostfang) som
   Claude modellerar och visar som grå silhuetter först, och en väg som går
   in i skogen i båda ändar. Görs i en egen session; utseendet är ditt.

19. ~~**En förgård framför hotellet**~~ (besvarat 2026-10-19: ja till rekommendationen, 24 studs; GDD §5.4) (din idé, 2026-10-19): en trottoar som
   gästerna går på, en gång fram till entrén, och fällorna placeras där (i
   dag sitter de på tre platser i lobbyn). **Att bestämma:** hur djup.
   **Rekommendation:** 24 studs (två celler) mellan trottoaren och fasaden,
   trottoaren 8 studs bred längs gatan, gången 6 studs bred fram till valvet;
   skylten står kvar i förgårdens hörn. Tomterna flyttas då 24 studs bort från
   gatan. Hör ihop med Night Bus (gästerna strövar på trottoaren) och skogen.

20. **Träden: det granskarna såg som är ditt** (2026-10-19, fyra blinda
   granskningar, `blender/street/trees/README.md`). Det mesta är rättat;
   kvar är utseendefrågor:
   - **Det ihåliga trädet** (ögonen i hålet): ett träd med ansikte, som det
     var tänkt, eller läser det som en figur med huva? **Rekommendation:**
     behåll ansiktet, det är "cozy creepy".
   - **Kvistarnas toppar:** en granskare ville ha trubbigare (de flimrar
     annars på en telefon), nästa tyckte att de trubbiga ser avsågade ut.
     **Rekommendation:** behåll dem trubbiga.
   - Grenarna är kantiga band utan förtjockning där de möter stammen (en
     förtjockning kostar ungefär 40 av ett träds 800 trianglar), och
     snölocken på granarna lämnar en grön kant under sig.
     **Rekommendation:** låt dem vara tills du sett dem i spelet.

21. **Gatan: Claudes tolkningar av dina beslut** (2026-10-19, GDD Appendix
   A.1 och A.3; allt går att ändra):
   - **Alla gäster åker buss därifrån också:** inte bara den som inget
     hotell tog, utan även den som checkat ut och den som tröttnade vid
     disken går till närmaste hållplats och väntar på nästa buss.
   - **Tutorialens Vampire Count kommer med bussen**, bokad till spelarens
     hotell (den strövar inte och kan inte tas av någon annan), i stället för
     att dyka upp. Bara Slimen i början går in från ingenstans.
   - **Hur gästerna strövar:** var fjärde gäst går samma väg (norra eller
     södra trottoaren, öster- eller västerut), så att bussens gäster
     tillsammans passerar alla sex hotellen; en minut räcker till två eller
     tre entréer var.
   - **Bussen kör på gatans norra halva**, dörren mot den norra trottoaren,
     så hållplatserna står mellan hotell 1 och 2 och mellan 2 och 3.
   **Rekommendation:** behåll alla fyra.

22. **VIP Lobbys märke och gyllene namnskylt** (GDD §10.2, byggt
   2026-10-19 kväll, provat i Studio med testprofil). I dag: med passet står
   ditt namn i guld över huvudet med "VIP" framför ("VIP  oden"), i stället
   för Roblox eget namn; märket är just det ordet "VIP" på skylten.
   **Att bestämma:** räcker det som märke, eller vill du ha en ikon (en krona,
   en stjärna) eller märket någon annanstans (spelarlistan)? **Rekommendation:**
   behåll ordet på skylten tills lounge-dekoren finns, och ta ikonen då
   tillsammans med den.

23. **Bellhop kortar incheckningen** (GDD §4.6:s tabell säger "Guest walking
   speed, check-in time"; bara gångfarten var byggd). Byggt 2026-10-19 kväll
   med ett platshållartal: bästa Bellhop delar Front Desks väntan med
   1 + 0,25 × dess effektivitet (6 s → 4,8 s med en Mummy), samma 25 % som
   gångfarten. Provat i Studio. **Att bestämma:** talet (GDD Appendix A.5,
   PLACEHOLDER). **Rekommendation:** behåll 25 %, samma som gångfarten.

24. **Att bygga fritt: det som är byggt och det som är ditt** (2026-10-19,
   GDD §5.4, A.1, A.2; grenen `claude/free-building-4b66e3`, inte spelad i
   Studio än, `TESTRUN.md` fas 12). Byggt enligt ditt ja: områden, trappor
   som bitar, en flyttbar disk, dekor på ett rutnät av 3 studs, golv per rum,
   lobby och korridor, och tier från inredning. Fem saker är dina:
   - **De nya dekorbitarna för Haunted Manor** (klockor, blommor, växter,
     möbler, piano): grå silhuetter bredvid en person,
     `archive/screens/2026-10-19_decor_silhouettes.jpg` (Grandfather Clock,
     Wall Clock, Black Roses, Carnivorous Plant, Ghost Fern, Armchair, Velvet
     Sofa, Bookshelf, Side Table, Grand Piano). **Välj:** Grandfather Clock A
     (golvur) eller B (kistformad), Grand Piano A (flygel) eller B (pianino;
     då passar den också mot en vägg). **Armchair** är för smal på en ruta
     (sitsen 1,44 bred, en person 2): **rekommendation** 2 × 1 rutor. Sätt
     taggar och priser: Claudes förslag står i GDD A.2 (till exempel Grand
     Piano: music, slow music, $2 500). Tills du valt visas de som enkla block
     i spelet.
   - **Den blinda granskningen av disken** (Haunted Manors README): kassan ser
     ut som en fågelholk från gästens sida, klockan är guld på guldskiva, och
     lobbygolvets schack är stort (6 studs rutor; ett golv du väljer ersätter
     det). **Rekommendation:** behåll alla tre tills du sett dem i spelet.
   - **Talen** (alla platshållare): områdena $1 000, $3 000, $8 000, $20 000,
     $50 000; en trappa $250 (den första till en ny våning gratis); golv
     gratis; försäljning ger halva priset tillbaka. **Ett fynd om tier:** med
     1 poäng per $ når en Coffin Suite ($40 000) T3 med $675 dekor, medan ett
     Standard Room ($50) behöver $300. **Rekommendation:** låt gränserna följa
     rummets pris (till exempel T2 vid 2 × rummets pris i dekor och T3 vid
     6 ×), så att dyra rum kräver dyrare inredning.
   - **Raderna ovanför lobbyn på våning 2 och uppåt** är i dag ett galleri:
     man går där, ställer dekor och trappor, men inga rum (områdena är 4 × 5
     bakom lobbyn, som du sa ja till). **Alternativet:** de främre områdena
     når ända fram till gatan ovanför våning 1 (4 × 7 där). **Rekommendation:**
     se galleriet i spelet först.
   - **Områden som inte är köpta** ligger kvar innanför fasaden med en mörk
     platta och en prislapp i byggläget. **Alternativet:** fasaden och
     bjälklagen följer bara de köpta områdena, så hotellet växer synligt.
     **Rekommendation:** spela med plattorna först; det andra är ett större
     bygge (fasaden är gatusessionens).
   - **Comfort i betyget** räknar nu rummens tier mot högsta tier (T3 av T3
     ger fullt, som T5 av T5 gjorde); förr gav T1 20 av 100, nu 33.

25. **Tutorialens Commons på första bussarna** (GDD §11 1:45 "The tutorial
   weights Commons toward your hotel", byggt 2026-10-19 på en egen gren, inte
   spelat i Studio, `TESTRUN.md` fasen "tutorial Commons and the named ping").
   När Slimen har sitt rum tar de **2** första bussarna under tutorialen med
   upp till **2** Commons var för den nya spelarens lediga rum (Slime,
   Skeleton eller Pumpkin Head, efter vilka rum som står lediga), i stället
   för andra dragna gäster, så bussen behåller sin storlek (dina 40 %). De
   strövar som alla gäster, så man kan Pitcha dem, och får **+10** i poäng
   mot den nya spelarens hotell. Med +10 slår ett nytt 1★-hotell ett 4★-hotell
   utan pitch, och står jämnt mot ett 5★-hotell som uppfyller båda
   önskemålen; en pitch avgör då. Alla tre talen är PLACEHOLDER (GDD
   Appendix A.7). **Alternativet:** boka dem direkt till hotellet (säkert,
   men då går de inte att pitcha, och §11 säger "Pitch one").
   **Rekommendation:** behåll 2 bussar, 2 per buss och +10: de nya rummen
   fylls nästan alltid, och pitchen lär ut att det lönar sig att springa ut
   till gästerna.

26. **Personal och städning i tid i betyget** (GDD §5.3 och Appendix A.4,
   byggt 2026-10-19 natt på en egen gren, inte spelat i Studio än,
   `TESTRUN.md` "Rating: staff coverage and cleaning on time"). §5.3 säger att
   Service kommer delvis från personalens täckning och Cleanliness från rum
   städade i tid och Housekeepings täckning; byggt var bara väntan vid disken,
   besvarade önskemål och andelen smutsiga rum. Nu, med platshållartal:
   **Service** + 10 vid full Front Desk-täckning och + 10 vid full Room
   Service-täckning; **Cleanliness** + 10 vid full Housekeeping-täckning och
   + 10 när alla av de senaste 20 städningarna skedde inom 40 s (ett rum som
   är smutsigt längre än så räknas som sent redan nu). Täckning: personalens
   summerade effektivitet mot behovet (en disk; ett Room Service- eller
   Housekeeping-djur per 4 rum). Poängen läggs ovanpå och kategorierna
   stannar inom 0–100, så ett hotell utan personal får samma betyg som förut
   och mer personal sänker aldrig något. **Att bestämma:** (A) behålla det
   så, tillägg ovanpå, eller (B) väga om kategorierna, till exempel
   Cleanliness = 60 % rena rum + 20 % i tid + 20 % täckning och Service på
   samma sätt, vilket sänker betyget för ett hotell utan personal (och kan
   skjuta upp 2★-rummen, §5.2). Talen (10, 10, 10, 10, 4 rum, 40 s) är dina
   i båda fallen. **Rekommendation:** (A) tills `tools/balance_model.py`
   räknar med personal: i (A) ger städning i tid inget när alla rum redan är
   rena, men ingenting du redan balanserat flyttas; (B) är tydligare men bör
   prövas i modellen först.

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

