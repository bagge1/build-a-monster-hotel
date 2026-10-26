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

8. ~~**Starta om `rojo serve` och tryck Connect**~~ (gjort 2026-10-19 kväll: `Scenery` synkad, de fem träden i spelet, `TESTRUN.md` fas 12) (träden är
   ~~importerade~~ 2026-10-19 22:34, sparade i `assets/Scenery/`, men syns i
   spelet först efter omstarten). Ursprungligen: **Importera fem träd** (2026-10-19, skogen runt gatan; grenen är
   **ihopslagen i main 2026-10-19 20:27**, så det kan göras nu): först **starta
   om `rojo serve`** och tryck **Connect** (fliken **Plugins** i Studio):
   grenen lägger till mappen `assets/Scenery`, som Rojo bara ser efter en
   omstart. Sedan importerar du de fem `Tree_*.fbx` i `blender/_import/`
   (`Tree_Crooked`, `Tree_Bare`, `Tree_Hollow`, `Tree_Fir`,
   `Tree_SnowFir`) till **Workspace** och skriver *importerat*. Ligger det
   filer där från en annan session vars import också står här, ta allt i en
   dialog. Tills träden är importerade ritar spelet enkla klossträd på samma
   platser. Bilden: `blender/street/trees/review/sheet.png`.

9. ~~**Importera 52 modeller: att bygga fritt**~~ (gjort 2026-10-19 22:34:
   alla 52 inställda, sparade och synkade; lobbyskalet och `FrontDesk` sedda
   i en playtest, `TESTRUN.md` fas 13) (2026-10-19, grenen
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

10. ~~**Importera 15 modeller: den nya dekoren**~~ (gjort 2026-10-20: alla 15 inställda, sparade och synkade; de tio placerade och sedda i ett speltest, `TESTRUN.md`) (2026-10-20, ditt ja till
   bilderna): de tio nya dekorbitarna för Haunted Manor (Grandfather Clock,
   Wall Clock, Black Roses, Carnivorous Plant, Ghost Fern, Armchair, Velvet
   Sofa, Bookshelf, Side Table, Grand Piano) och fem som redan finns i spelet
   men flimrade på några ställen (Sand Tray, Cauldron, Moon Window,
   Chandelier och Frostfangs Cocoa Mug; samma utseende). Importera **alla
   filer i `blender/_import/`** till **Workspace** i en dialog och skriv
   *importerat*. Bilderna: `blender/hotel/haunted_manor/review/decor/`.

11. ~~**Importera 49 modeller: fasaderna**~~ (importerat av dig 2026-10-20 kväll; fix-up, kollision och `.rbxm` klara samma kväll; natten 2026-10-21: alla 256 delar jämförda mot importen och lika, Workspace-kopiorna och `blender/_import/` borttagna, `blender/facade/README.md`. Klart.) (2026-10-20). Väggarna runt det du
   äger, i sju stilar: hotellkitens egna (Haunted Manor, Frostfang Lodge) och
   de fem fasadpaketen (Gothic, Neon, Candy, Pirate, Slime). Varje stil har
   sju bitar: en slät vägg, fyra väggar med fönster (Twin sash, Arched,
   Round, Wide), entrén och hörnstolpen. Importera **alla filer i
   `blender/_import/`** till **Workspace** i en dialog och skriv *importerat*
   (inte mitt i en playtest). Filerna heter `<Stil>_Facade_...`; Claude döper
   om dem. Titta gärna först på bilderna i §1 punkt 12: säger du nej till en
   stil behöver den inte importeras än.

13. ~~**Starta om `rojo serve` och tryck Connect, före importen i punkt 12**~~ (gjort av dig 2026-10-21 eftermiddag)
   (2026-10-21 förmiddag): projektfilen har fått mappen för Bayou Spas kit
   (`assets/HotelKit/BayouSpa`), som Rojo bara ser efter en omstart. Sedan
   **Connect** (fliken **Plugins** i Studio). Utan det sparas inte Bayou Spas
   väggar, möbler och sällsynta set.

12. ~~**Importera 136 modeller: väggarna, dörren, möblerna, de sällsynta seten,
   souveniren och tre nya möbler**~~ (gjort 2026-10-23: alla 136 inställda
   (Box överallt, `LOD_Proxy` dold), kontrollerade och sparade. Haunted Manor
   51 och "The Count's Study" 5 i `assets/HotelKit/HauntedManor/`, Frostfang
   Lodge 34 och "Aurora Lodge" 5 i `assets/HotelKit/FrostfangLodge/`, Bayou
   Spa 35 och "Lantern Grove" 5 i `assets/HotelKit/BayouSpa/`,
   `Souvenir_Base` i `assets/Cosmetics/`; de prefixade (`FrostfangLodge_*`,
   `BayouSpa_*`) sparade utan prefix i sitt kits mapp. `blender/_import/` är
   tom.)

14. ~~**Importera en (1) modell: Skeleton med skelett, provet för riktiga
   animationer**~~ (gjort 2026-10-23 02:52: inställd, sparad i
   `assets/Monsters/Skeleton.rbxm` på grenen `claude/monster-animations-6c1d3c`,
   provad i Studio: varje färgdel bär sin skinning, Tiny och Giant skalar
   skelettet, de sex rörelserna vrider benen som de ska, och kostnaden är liten;
   se `blender/monsters/rig_proto/README.md`. Kvar: att se det med egna ögon,
   §1.13.) (2026-10-23, LAUNCH.md #6). Skeleton byggd igen med ett
   skelett (benen `Hips`, `Spine`, `Head`, armar, lår och smalben) som alla
   färgdelar följer; i Blender syns det rätt i en provpose. Nu ska det visas i
   Studio att varje färgdel böjer sig med benen, att Tiny och Giant skalar
   skelettet, och vad det kostar. Gör det **efter** importen i punkt 12, inte
   under den: importera den enda filen i `blender/_import_rig/` till
   **Workspace**, och i importfönstret, under **Rig General**, välj **Rig
   Type: Custom**. Skriv *importerat*; resten är vårt.

15. ~~**Importera 27 modeller: Bayou Spas kit, fasad och VIP-loungen**~~
   (gjort 2026-10-23: alla 27 inställda (Box överallt, `LOD_Proxy` dold,
   `import_fixup.luau` för varje set), kontrollerade och sparade. Bayou Spas
   kit 15 och fasad 7 utan prefix i `assets/HotelKit/BayouSpa/`, VIP-loungens
   5 `Decor_Vip*` i `assets/HotelKit/HauntedManor/`; de synkade kopiorna
   stämmer del för del. `blender/_import/` är tom. Setens `README.md`.)
   (2026-10-23, ditt ja samma dag). Alla filer i `blender/_import/` till
   **Workspace** i en dialog, med vanliga inställningar (inte Custom rig),
   och skriv *importerat*. Gärna en import i taget: först punkt 14 eller
   den här, sedan den andra.

16. ~~**Importera 27 monster med skelett: alla som finns**~~ (gjort 2026-10-24
   natt: alla 27 inställda, kontrollerade och sparade riggade i
   `assets/Monsters/`; de synkade kopiorna stämmer del för del;
   `blender/_import/` är tom; setens `README.md`, `archive/NATTLOGG-2026-10-24.md`)
   (2026-10-23, LAUNCH.md #6). Haunted Manors 10, Frostfangs 7 och Bayou Spas 10, byggda igen med
   skelett (samma utseende som de du har sagt ja till; nu böjer de sig).
   Skeleton-provet i punkt 14 höll, så nu alla. Alla filer i
   `blender/_import/` (orkestreraren lägger dem där) till **Workspace** i en
   dialog, och under **Rig General** välj **Rig Type: Custom**. Skriv
   *importerat*; resten är vårt. Inte mitt i en annan import.

- **Nästa import (natten 2026-10-26):** Haunted Manors `Furniture_PoolTable`,
  `Furniture_PingPongTable` och `Furniture_ArcadeCabinet` har fått platser för
  besökare (formerna oförändrade). Claude stagar dem i `blender/_import/` när du
  vill importera; tills dess tar varje bit en besökare.

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

11. **Spela med en handkontroll** (2026-10-19 kväll, GDD §11 "Gamepad
   navigation for everything"). Byggt och ihopslaget: Y tar markeringen till
   menyknapparna, A trycker, B stänger fönstret överst (och backar ur
   byggläget), i byggläget flyttar vänster spak biten, RB vrider, D-pad byter
   våning och vrider vyn. Studio kan inte trycka på en handkontroll, så det
   är ditt att känna på (`TESTRUN.md`, "Gamepad navigation"). Tangentbordet
   och musen fungerar som förut (provat).

12. ~~**Fasaderna: titta och säg ja eller vad som ska ändras**~~ (ditt ja 2026-10-23 till alla sju stilar; GDD §18) (2026-10-20,
   utkast från dina ja till en rad per stil; granskade blint i tre rundor).
   Alla sju från gatan: `blender/facade/review/overview.png` (överst Haunted
   Manor, Frostfang, Gothic, Neon; nederst Candy, Pirate, Slime). Varje stil
   närmare: `blender/facade/<stil>/review/sheet.png` (hela hotellet, entrén med
   en person, ett yttre och ett inre hörn, och de fem väggbitarna utifrån och
   inifrån). En rad per bit, i varje stil:
   - **`Facade_Wall`**: slät vägg, 12 studs, stilens band (sockel, lister).
   - **`Facade_Window_TwinSash`**: två höga smala rutor, 3,2 × 9 (Gothic: två
     spetsbågar; Pirate: två ventiler).
   - **`Facade_Window_Arched`**: ett högt bågfönster under listen vid 12
     (Frostfang, Candy och Pirate: rundbågat; Gothic: spetsbåge till 13).
   - **`Facade_Window_Round`**: ett runt fönster, 6,8 över (Gothic: en ros;
     Pirate: en stor ventil med mässingsring och rep).
   - **`Facade_Window_Wide`**: tre rutor över en blomlåda på konsoler (Gothic:
     tre spetsbågar; Pirate: en låda med örter; Neon: lysande blommor).
   - **`Facade_Entrance`**: valvet, 9 × 9 fritt, och lyktan som hänger i det
     (kitens valv är lobbyns godkända, flyttade ut framför väggen).
   - **`Facade_Corner`**: stolpen i varje hörn med en list längs ytterkanten
     (Candy: en rund polkagris; Pirate: ett rep och en lykta; Gothic: en
     gargoyle).
   Stilarna: Haunted Manor och Frostfang som lobbyns framvägg; Gothic mörk
   skiffer, spetsiga fönster, röd blyinfattning, gargoyler; Neon mörka paneler
   med cyan och magenta rör runt fönstren (de lyser i spelet, inte i bilden);
   Candy rosa rån i lager med grädde emellan (inget rutnät, `taste.md`),
   glasyr som droppar, polkagrishörn, ett körsbär på valvet; Pirate smala
   väderbitna plankor med förskjutna skarvar, mässingsventiler, rep runt
   fönstren, lyktor på hörnen; Slime gröna väggar, slem som samlas på
   fönsterbrädorna och droppar.

13. **Se monstren röra sig** (2026-10-23, LAUNCH.md #6). Allt som går att
   mäta utan att titta är provat (§0.14), men ingen har sett ett monster böja
   sig. Det kan bara ses med Studio framme. När alla 27 är importerade med
   skelett: spela och titta på gästerna. Hur ska det kännas:
   - **Walk**: ett studsigt leksakssteg (Biped), ett mjukt hopp (Blob), en
     framåtlutad glidning med släpande svans (Float), en S-slingring (Serpent).
   - **Idle**: andas, ser sig långsamt omkring.
   - **Happy**: små hopp med armarna upp i ett V; går glad ut efter en bra
     vistelse.
   - **Sad**: hänger med huvudet, sjunkna axlar; när en önskan väntar.
   - **CheckIn**: en gång vid disken: armen svepande ut och en bugning (Blob
     och Float snurrar).
   - **Staff**: höger hand i arbete (knackar, torkar) vid dörren.
   Säg vad som känns fel med dina ord ("för hoppigt", "armarna för höga").
   (Natten 2026-10-24: alla 27 är importerade och sparade; i ett playtest rör
   alla fem kroppsformer benen, Tiny och Giant också. Bild:
   `archive/screens/2026-10-24_rigged_residents.jpg`. Nu kan du titta.)

14. ~~**Byggläget på en telefon täcker sig självt**~~ (rättat 2026-10-24 på
   morgonen, ditt "hur kan du ställa en så dum fråga i en nattloop": ett
   överlapp är ett fel, inte ett val). På korta skärmar slutar
   verktygsraderna 8 px ovanför remsan och rullar, och högermenyn göms medan
   du bygger, som vänstermenyn redan gjorde; på en dator är allt som förut.
   Sett i Studios telefonsimulator samma kväll: verktygen slutar vid y 152,
   remsan börjar vid 190, två hela rader syns och resten rullas fram med ett
   finger (Done nås). Före: `archive/screens/2026-10-24_phone_build_overlap.jpg`,
   efter: `archive/screens/2026-10-24_phone_build_fixed.jpg`. Hur det ser ut
   är ditt att säga.

15. **Titta på gränssnittet på telefonen** (kvällssprinten 2026-10-24/25).
   Åtta fel i layouten rättades (mätta och sedda i Studios simulator på
   iPhone 14 och iPad 10), och tre av dem syns: **HUD:ens vänsterkolumn är
   två knappar bred på en telefon** (som högerkolumnen; förut gick VIP under
   skärmkanten), **Ping-menyn öppnas vänster om högerkolumnen** (förut låg
   den över själva Ping-knappen), och **rumsvyn är inte nedskalad på en
   telefon** (knapparna 44 px, mitten rullar). Bilder:
   `archive/screens/2026-10-24_phone_hud_before.jpg`,
   `2026-10-24_phone_ping_fixed.jpg`, `2026-10-24_phone_roomview_fixed.jpg`,
   `2026-10-24_ipad_roomview_fixed.jpg`. På din telefon: säg om något känns
   trångt eller fel. Och bildtiden med ett fullt hotell gick inte att mäta i
   natt (datorn användes); den riktiga siffran är din telefons (§4).
   **Telefonen spelar nu alltid liggande** (båda hållen): spelet tillät
   stående (Roblox standard), och stående klipptes toppraden i båda
   kanterna och kolumnerna täckte mitten
   (`archive/screens/2026-10-25_phone_portrait_before.jpg`). Satt på
   klienten (`LandscapeSensor`), lätt att ändra om du vill ha stående;
   då behöver gränssnittet en egen stående layout. **Glooms pratbubbla
   står nu längs nederkanten på en telefon** (överst täckte den fem
   menyknappar på en iPhone 7): `archive/screens/2026-10-25_iphone7_gloom_fixed.jpg`.

16. **Barens disk och lilla scen** (natten 2026-10-26, GDD A.13; byggda och
   validerade i Blender, tre blinda granskningar triagerade i
   `blender/rooms/haunted_manor_bar/README.md`; **inte importerade, inget
   lagt i `_import/`**). Bilder (Workbench, glöden syns olyst):
   `archive/screens/2026-10-26_bar/bar_game_camera.jpg`, `bar_front.jpg`,
   `bar_counter_close.jpg`, `bar_stage_close.jpg`, silhuetterna
   `bar_silhouettes.jpg` (tre per bit; valda: disken med bakhylla, scenen med
   välvd fond). Dina val:
   - Diskens storlek: **3×1** (tre gästplatser framför, förslag) eller 3×2
     med en gång bakom.
   - Baksidorna är släta på båda (att göra dem färdiga kostar ~300 trianglar
     som disken inte har). Förslag: behåll, de står mot väggen.
   - Spegeln läses som ett fönster (förslag: mörkare blå), skivan är mörk
     (förslag: ljusare trä), diskens höjd 3,7 (förslag: behåll), scenens
     bredd.
   - Gäster 3 studs isär vid disken når varandras armar (kontraktets en plats
     per ruta); dansaren står 2,15 bakom mikrofonen.
   Säg ja eller vad som ska ändras; först efter ditt ja läggs de för import.

17. **Biografens duk och stolsrad** (natten 2026-10-26, GDD A.13; byggda och
   validerade i Blender, fem blinda granskningar triagerade i
   `blender/rooms/haunted_manor_cinema/README.md`; **inte importerade**).
   Bilder: `archive/screens/2026-10-26_cinema/cinema_game_camera.jpg`,
   `cinema_in_use.jpg` (gäster i raden), `cinema_silhouettes.jpg` (valda:
   duken i en spetsbågig scenram med ridåer, raden med tre stolar under var
   sin båge). Dina val:
   - Duken läses som en **dockteater** (tre granskare): behåll, eller byt till
     en enkel duk i ram på väggen (alternativ B). Förslag: behåll, med en ljus
     `Screen`-yta som spelet kan tända.
   - Stolarna står 2,75 isär och armstöden överlappar: behåll 3×1, eller 4×1
     med luft. Förslag: behåll.
   - Andra raden ser inte över den första under 7-studs-taket: en upphöjd
     rad (en "riser"-bit) eller högre tak (~9). Förslag: en riser-bit senare.
   - Radens rygg: crimson paneler (byggt) eller trä (förslag: trä); stolens
     höjd 1,7, lampornas storlek, tornspetsarna.

18. **Inomhuspoolen och solstolen** (natten 2026-10-26, GDD A.13; byggda och
   validerade i Blender, tre blinda granskningar i
   `blender/rooms/haunted_manor_pool/README.md`; **inte importerade**).
   Bilder: `archive/screens/2026-10-26_pool/pool_game_camera.jpg`,
   `pool_poolside.jpg`, `pool_silhouettes.jpg`. Dina val:
   - **Storleken:** byggd **4×2** (tre simmare) i stället för A.13:s 3×2 (två
     simmare); spelets rad står kvar på 3×2 tills du valt. Förslag: 4×2.
   - **Djupet** (det största): golvet går inte att gräva, så vattnet är 0,72
     djupt, och kontraktets simmare (mitten 1,5 under ytan) sticker benen
     genom golvet. Förslag: koden döljer simmarens ben, eller ett eget
     simklipp med benen uppdragna.
   - Gargoylens stråle läses som en stång (alla tre rundorna): förslag att
     koden gör `Jet_1` till genomskinligt fallande vatten. Gargoylens storlek.
   - Utseenden: rombbandet (lästes som ett kasino), hörnspirorna (en
     fontän), solstolens nackstöd.

19. **Gymmets bänk, löpband och boxsäck** (natten 2026-10-26, GDD A.13;
   validerade i Blender, tre blinda granskningar i
   `blender/rooms/haunted_manor_gym/README.md`; **inte importerade**). Bilder:
   `archive/screens/2026-10-26_gym/gym_game_camera.jpg`, `gym_silhouettes.jpg`
   (valda: bänk med lågt ställ, löpband med räcken och konsol, boxsäck i en
   järngalge). Dina val:
   - Stången får vara 2,2 bred (kontraktets inset) men händerna hänger vid
     ±1,46. Förslag: ett undantag så att stången når ±1,45.
   - Att ligga på bänken läses som en säng eller kista. Förslag: en
     `Lift`-placering med fötterna på golvet (en rad i MODELS.md).
   - Bänkens höjd i spelets rad går från 2,5 till 4,5 (ställningen står över
     den liggande); rättas när modellerna importeras.
   - Utseenden: galgen, klockkonsolen, det mörka järnet, ränder på bandet.

20. **Spaets badtunna och massagebänk** (natten 2026-10-26, GDD A.13;
   validerade i Blender, tre blinda granskningar i
   `blender/rooms/haunted_manor_spa/README.md`; **inte importerade**). Bilder:
   `archive/screens/2026-10-26_spa/spa_game_camera.jpg`, `spa_silhouettes.jpg`.
   Dina val:
   - **Tunnan 3×3 med fyra gäster** (i stället för radens 2×2, som bara rymmer
     en) eller 3×2 med tre. Förslag: 3×3.
   - Kanten 2,45 hög med två trappsteg i hörnen som väg in (ingen granskare
     såg en väg in); föremålen på de bakre stegen; ånga behöver ett namn i
     MODELS.md (t.ex. `Steam_1`).
   - Bänkens hästskoformade ansiktsstöd, höjden 2,35, ett klipp för att ligga
     på magen.

21. **Dansgolvet, högtalaren och discokulan** (natten 2026-10-26, GDD A.13;
   validerade i Blender, tre blinda granskningar i
   `blender/rooms/haunted_manor_dance/README.md`; **inte importerade**; spelets
   rader stämmer redan). Bilder: `archive/screens/2026-10-26_dance/`
   (`dance_game_camera.jpg`, `dance_four_floors.jpg`: fyra golv i rad,
   `dance_silhouettes.jpg`). Dina val:
   - Plattornas färger: magenta och månblått (mot Manors egna nycklar).
   - Kulan kan inte hänga över golvet (en 1×1-bit håller sin kula i sin ruta
     och under 7): ett taklager i MODELS.md först. Stativet läses som en
     gongong eller galge, och kulan sitter i huvudhöjd.
   - Dansare 3 isär når varandras armar (en plats per ruta, som vid disken).
   - Utseenden: högtalaren bakifrån (en garderob), de halva guldprickarna vid
     ett ensamt golvs kant, det tunna mörka järnet.

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
   - ~~**De nya dekorbitarna för Haunted Manor**~~ (dina val 2026-10-20: golvuret
     A, flygeln A, Armchair kvar på 1 × 1, taggar och priser som GDD A.2
     föreslog; ditt ja till bilderna samma dag, båda i GDD §18). **Modellerade**
     (`blender/hotel/haunted_manor/README.md`, "2026-10-20"), granskade blint i
     fyra rundor, importerade och sedda placerade i spelet (`TESTRUN.md`,
     `archive/screens/2026-10-20_decor_ingame_*.jpg`).
     Små saker som är dina:
     - **Sittplatserna** är 2 studs breda per person (avatarens kropp); med armarna
       är avataren 4, så armarna går genom armstöden och två på soffan överlappar
       med armarna. **Alternativet:** 4 per person (soffan rymmer då en, Armchair
       vore 2 × 1). **Rekommendation:** behåll 2: ingen kod sätter någon i dem än.
     - **Flygeln** har en riktig flygels mått mot den stående personen (tangenterna
       vid 2,48, halva hans längd); en sittande avatar får inte plats med låren
       under klaviaturen. **Alternativet:** höj den ungefär 1 stud (den ser då stor
       ut bredvid en stående). **Rekommendation:** behåll.
     - **Väggklockan** är ungefär 4 studs hög, större än en riktig (silhuettens
       storlek). **Rekommendation:** behåll: urtavlan syns på en telefon.
     - **Armchair** är 5 studs hög som silhuetten (lika hög som en stående
       person); en sittande syns inte bakom öronlappen. **Rekommendation:** behåll.
     - **Black Roses** har röda hjärtan i svarta kronblad; en granskare såg dem som
       röda rosor, en annan som en mörk fläck. **Rekommendation:** behåll.
     - **Carnivorous Plant**: två granskare tyckte att en köttätande växt med öppna
       käftar påminner om Marios Piranha Plant, även efter att färgerna ändrats
       (mörkgröna käftar, vinröd insida, halmgula tänder, stenkruka).
       **Rekommendation:** behåll: formen är en flugfälla.
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

27. ~~**Tempot efter bussarna: rebirth tar 3,5–5,4 timmar**~~ (besvarat 2026-10-20: "fix 2 and 3", rekommendationen byggd: bussen 3–8 per spelare, vistelserna dubblade, Legendarys vänskap 5; GDD §4.2, §4.3, §18. Mätt efteråt: rebirth 1:50 med tutorial och 2:41 utan, fortfarande över 60–90 min, och Vampire Count som resident är det som väntas på; `archive/BALANCE-2026-10-20.md`. Inga fler värden ändrade.) (2026-10-19 kväll,
   mätt med en uppdaterad kopia av `tools/balance_model.py`, median av 8
   körningar; rapporten `archive/BALANCE-2026-10-19-evening.md`). Utan
   walk-ins kommer högst 4 gäster var 3:e minut för en ensam spelare (80 i
   timmen; förut upp till 450). Rummen står tomma 84–90 % av tiden. Med
   tutorial / utan: $1M efter 2:33 / 4:25 h (förut 1:02 / 1:19), rebirth
   efter 3:33 / 5:24 h. GDD:ns mål är 60–90 minuter. Dina beslut rörs inte
   (bussens intervall, 40 %, BasePay). **Att bestämma:** vad som ska ge
   efter. Förslag med uppmätt effekt:
   - bussens gränser 2–4 → 3–8 per spelare (platshållare): $1M 2:12 / 2:58 h;
   - vistelserna dubblade (Common 180 s … Legendary 600 s; startvärden i
     §4.2): $1M 1:39 / 2:41 h;
   - båda: $1M 1:20 / 1:54 h, rebirth 3:08 / 4:30 h (väntar på Vampire
     Count som resident);
   - båda och Legendarys vänskap 10 → 5: rebirth **1:40 / 2:41 h**.
   **Rekommendation:** båda och vänskapen 5, sedan spela och känna efter.
   (Mätt före tutorialens Commons, som bara rör de första två bussarna.)

28. ~~**Tutorialens gratis Coffin Suite får inte plats**~~ (besvarat 2026-10-20: (a) byggt, goal-kortet ger också ett gratis främre område bredvid startområdet, och Gloom säger det; GDD §11, A.7. I modellen står sviten klar 4:00 och Vampire Count checkar in 11:19. Inte spelat i Studio än.) (2026-10-19 kväll,
   samma mätning). Goal-kortet ger en gratis Coffin Suite (3×3), men
   startområdet (4×5 celler) rymmer den inte bredvid tutorialens två
   Standard Rooms med gång till dörrarna, och en våning för $500 har en ny
   spelare först efter ungefär 14 minuter. Då kommer Vampire Count inte
   heller. **Att bestämma:** hur det ska gå ihop. **Förslag:** (a) Goal-kortet
   ger också nästa område eller våning gratis; (b) startområdet blir 5×6;
   (c) tutorialen bygger bara ett Standard Room före sviten.
   **Rekommendation:** (a), ett gratis område bredvid startområdet, eftersom
   det också lär ut att köpa områden.

29. **Långa vägar uppåt i ett stort hotell** (2026-10-19 kväll, provat i
   Studio). I ett fullt hotell (`fill`, 49 bitar på 3 våningar) där
   trapporna står långt från disken går en gäst **1 300–1 450 studs** till
   ett rum på våning 3, alltså 130–145 s i 10 studs/s, och Room Service hinner
   aldrig fram innan requestens 30 s går ut (residenten vände efter 24 s).
   Spelet tillåter en trappa i lobbyraden så länge den inte stänger någon
   dörr, och då måste alla gå runt hela våningen. Mätningen i §2.27 räknade
   med 70 s till våning 3. **Att bestämma:** (a) personal på ärende går
   fortare (t.ex. 20 studs/s; talet är en platshållare i A.5), (b)
   requestens tid växer med avståndet till rummet, (c) trappor får inte stå
   i lobbyraden, (d) låt det vara: en dålig planlösning straffar sig själv.
   **Rekommendation:** (a) och (c): personalen ska synas arbeta, inte gå
   förgäves, och lobbyraden ska vara gästernas väg in.

30. **Rutor i stället för områden** (dina beslut 2026-10-20, GDD §5.4 och
   A.1). **Byggt och spelat i Studio 2026-10-20** (`TESTRUN.md`, "Tiles,
   desks and the facade"): startkvadraten 4 × 4, disken mitt emot valvet,
   rutor köpta en i taget, väggar bara runt det du äger på varje våning, flera
   diskar. Det som är Claudes läsning eller platshållare, att säga till om:
   - ~~En köpt ruta gäller alla våningar~~ (ditt svar 2026-10-20: rutor köps
     per våning, dyrare högre upp; en ny våning har inga väggar förrän du köper
     rutor). Platshållare: en ruta på våning f kostar 2^(f−1) gånger.
   - Priset: ruta nummer n kostar **$50 × 1,03^n** (hela tomten ungefär som
     de sex områdena, ~$72 000). Ett skrivbord till kostar **$500**.
   - ~~Ovanför våning 1 står gatsidan öppen~~ (ditt svar 2026-10-20: väggar
     mot gatan på alla våningar; GDD A.1).
   - Bakdörren till Resident Wing försvinner (ingen går igenom den).
   - Tutorialens gratis område för Coffin Suite blir gratis rutor (en 3 × 4
     bit bredvid startkvadraten: till höger om sviten får plats där, annars
     till vänster).
   - **Bara ett Standard Room får plats i startkvadraten** bredvid disken (ditt
     "ett rum till höger om den"). Tutorialens steg "bygg ett andra rum" kräver
     därför att spelaren först köper fyra rutor (ungefär $210) och sedan rummet
     ($57); Gloom säger nu det ("tap the gold tiles beside your hotel"). Spelat:
     det går med de pengar en ny spelare har efter första gästen plus lite
     till. **Säg till** om startkvadraten ska rymma två rum (till exempel 4 × 5)
     eller om de första rutorna ska vara billigare.
   - **Diskarna** ligger under fliken "Stairs, desks" i Build. Gästerna ställer
     sig vid disken med kortast kö; du checkar in vid den disk du står vid,
     Front Desk-personalen vid alla.
   - Utan lobbymodell **startar du på gångens fot** framför valvet (forecourtens
     `PathFoot`), och golvvalet "Lobby" finns inte längre (bara korridoren och
     rummen). Entertainment-personalen står precis innanför valvet.
   - Köpbara rutor visas i Build som **guldplattor med pris**; ett tryck köper.
     Hur de ser ut är ditt.
   - Ett fönster kostar **$100** (platshållare), och att sälja det ger allt tillbaka.

31. **Att vrida kameran i Build** (din rapport 2026-10-20: "you cant rotate
   the camera in build mode"). Provat utan att ta fokus från dig: tangenterna
   **,** och **.** vrider kameran, liksom knappen **↻ View** (och styrkorsets
   vänster/höger); Roblox egen kamera är avstängd i Build och tar inte
   musen. Höger musknapp med drag är gjort oberoende av allt annat som kan
   "ta" musrörelsen, men det kan bara provas med riktig mus. **Säg** hur du
   försökte vrida (höger musknapp och dra, styrplatta, några tangenter?), och
   om **Q / E** eller en text i Build om hur man vrider vore bättre. Provas med
   riktig mus i en nattkörning eller när du säger till (`TESTRUN.md`, "Build
   camera turn"). *Natten 2026-10-21:* höger musknapp och dra på tomten
   vrider kameran (400 pixlar ≈ ett halvt varv), ett drag som börjar på en
   knapp gör det inte, och ett högerklick utan drag slutar placera. Kvar för
   dig: om det känns rätt, och svaret på frågan ovan.
32. **Flip och fönster** (dina beslut 2026-10-20, GDD A.1): byggda och provade
   via spelets egna anrop (`TESTRUN.md`, "Flip", "Windows"). **F** gör ingenting
   för de importerade rummen än: Roblox kan inte spegla en mesh, så varje rum
   behöver sin `_Mirror` från kitets skript (MODELS.md); tills dess säger Build
   "Can't be flipped yet". Fönstren är grå blockformer tills kitets fönster
   finns. Att välja kort, trycka F och trycka på en vägg med riktig mus provas
   i en nattkörning.

33. **Mer dekor och fler sätt att inreda** (din fråga 2026-10-20): en lista i
   `docs/DECOR_IDEAS.md`: nya dekorbitar per önskemål, för Frostfang och för
   de kommande platserna, och nya sätt att inreda (tapeter, mattor, ett
   taklager för ljuskronor och lampor, ljusets färg, dörr- och sängstilar,
   dekor som rör sig, set, förgården, porträtt av residenter). **Två fynd:**
   de sällsynta gästernas önskemål har bara en sak var (Mumien, Häxan,
   Varulven, Vampyren, Banshee), och i Frostfang finns ingen dekor och
   ingen bekvämlighet alls för Yetins *quiet* och Aurora Spirits *silence*.
   **Välj** vad som ska byggas. **Rekommendation:** först två eller tre saker
   per tunt önskemål (Frostfangs *quiet* och *silence* först), sedan
   tapeter, sedan taklagret.

34. **Fasaderna: det granskarna såg som är ditt** (2026-10-20, tre blinda
   rundor; resten är rättat, `blender/facade/README.md`, "Blind reviews"):
   - **Frostfangs gavel** syns som ett tunt streck uppifrån, och **Haunted
     Manors spetsgavel** som en tråd: det är lobbyns godkända valv. *Ändra
     inget* eller *ge gaveln tak och tjocklek*. **Rekommendation:** ge
     Frostfangs gavel ett snötäckt tak som syns uppifrån; behåll Haunted
     Manors.
   - **Fönstrens storlek**: rutorna är 9 studs höga på en våning på 17, och
     Round och Wide sitter högre (botten vid 4 och 3,5) än Twin sash och
     Arched (3). Granskarna läste dem som kyrka eller kontor, inte mysigt.
     **Rekommendation:** behåll; de passar våningens höjd.
   - **Glaset är mörkt**, utifrån och inifrån (`Glass` är en egen del).
     *Mörkt*, *genomskinligt* (koden gör det; man ser då rummets egen vägg
     bakom) eller *upplyst på natten*. **Rekommendation:** mörkt nu, upplyst
     varmt på natten senare.
   - **Neons entré** läses som en lastport: en kvadratisk öppning med rör.
     **Rekommendation:** behåll som utkast; ett tak över dörren kan komma
     sedan.
   - **Väggarnas insidor** är släta färgband, som lobbyns framvägg var.
     **Rekommendation:** behåll; rummen har egna väggar.
   - **Ovanför fönstren** är 5–6 studs slät vägg upp till taklisten, och
     Haunted Manor, Gothic och Neon är lika mörka lådor uppifrån.
     **Rekommendation:** behåll tills du sett dem i spelet; en list eller ett
     mönster högt upp kan läggas till per stil.
   - **Pirates hörnlyktor** sitter högt (13–16 studs). Lägre går, men då
     måste hörnets regel om att hålla sig undan fönstren ändras.
     **Rekommendation:** behåll.
   - **Neons vinkel** över dörren svävar fritt. *Behåll*, *ta bort* eller
     *gör den till en skylt med ram*. **Rekommendation:** ta bort den.
   - **I spelet, natten 2026-10-21** (två blinda granskare på bilder från en
     playtest, `blender/facade/README.md`, "In the game"; bilderna i
     `archive/screens/2026-10-21_facade_*.jpg`):
     - **Bandet mellan våningarna** har platsens färg (lila i Haunted Manor)
       vad du än bär för fasad: det är golvplattans kant i glipan på 1 stud
       ovanför varje vägg. På Pirate och Slime läses det som ett lila streck
       som inte hör dit (`2026-10-21_facade_pirate_band.jpg`). *Behåll*,
       *ge kanten fasadens färg* (koden, liten ändring) eller *gör
       väggbitarna 18 höga så att de täcker kanten* (modellerna).
       **Rekommendation:** ge kanten fasadens färg när en fasad bärs.
     - **Neon försvinner på natten**: väggen är nästan svart mot himlen, bara
       rören syns (`2026-10-21_facade_neon_night.jpg`). **Rekommendation:**
       en ljusare mörkblå vägg, eller rör längs varje våningskant.
     - **Pirate läses som stockstuga**, **Slime som ett grönmålat hus**:
       temat bärs av detaljer som är för små på gatans avstånd.
       **Rekommendation:** titta på dem i spelet först; större drypp och
       ett räcke eller en kölbåge är nästa steg om du håller med.
     - **Hörnstolparna** läses som målade ränder (Haunted Manor, Frostfang),
       **lyktan** hänger mitt i valvet (foten 7,5 över tröskeln, kolliderar
       inte), och **pumpan** på Haunted Manors valv är för liten för att
       läsas. **Rekommendation:** behåll alla tre tills du sett dem.

35. **Kedjans öppna värden** (dina beslut 2026-10-20, nu i GDD §3, §6.4,
   §6.6, §8.3 och §18). Nattens bygge använder PLACEHOLDER tills du bestämmer:
   - **Bakgrundsandelen**: hur mycket ett hotell du inte spelar tjänar, som
     andel av vad det tjänar när du spelar det. **Rekommendation:** 25 %
     (lockar att resa tillbaka, men de gamla hotellen är aldrig döda).
   - **Plots per server**: 8, 10 eller 12. **Rekommendation:** 10: fler än
     så och tre gator med varsitt hotell per spelare blir många delar på en
     telefon (natten mäter det i steg 7).
   - **Våningstaket**: *6 genom rebirth, 7 med passet*, eller *5 och 6*.
     **Rekommendation:** 6 och 7: rebirth 9 blir den sista som ger en
     våning, och Prestige Stars tar över därefter.
   - **Prestige Stars effekt**: förslaget är + inkomst och lite ovanligare
     gäster. **Rekommendation:** +5 % inkomst per stjärna och +2 % chans
     till en högre sällsynthet per stjärna, båda med tak vid 10 stjärnor.
   - ~~**Platsernas pris**~~ (besvarat 2026-10-23 med balanskörningen:
     $400 000 och $1 000 000, betalning ×5 per plats; GDD §18,
     `archive/BALANCE-2026-10-23.md`): vad Frostfang Lodge och Bayou Spa kostar att
     öppna. **Rekommendation:** Frostfang $250 000, Bayou Spa $10M, och
     att varje plats tjänar ×20 den förra (som Frostfangs rum redan gör);
     `tools/balance_model.py` prövar dem mot dina tider (steg 6).
   - **Mätt natten 2026-10-21** (`archive/BALANCE-2026-10-21.md`, 4 frön, med
     tutorial): 5★ på Haunted Manor 31:35 (mål 30–60), Frostfang 49 min efter
     (mål 60–90), Bayou Spa 75 min efter (mål 90–120), rebirth-redo 2:44
     (mål 3–4,5 h). Det som gör de senare för snabba: **plattor och våningar
     kostar lika mycket på varje plats** medan rummen kostar ×20; med dem
     också ×20 blev det 62 och 94 min och rebirth 3:12, inom alla mål.
     **Rekommendation:** plattor och våningar ×20 per plats (som rummen).
     Inget värde är ändrat. (Felet att ett nytt hotell ärvde det gamlas
     betygsunderlag är rättat samma natt: varje hotell har sitt eget.)
   - **Mätt igen med byggda rum** (2026-10-21 morgon,
     `archive/BALANCE-2026-10-21b.md`): med tutorial 5★ Haunted Manor 27 min
     (3 under), Frostfang +67, Bayou +95, rebirth 3:15: inom målen utom det
     första. Utan tutorial: 5★ 57 min, Frostfang +130 (40 över), rebirth 4:36
     (6 över). Orsak: 5★ kommer med ett litet hotell (staplarna ger upp till
     +30 i nöjdhet), så sparandet till öppningspriset tar längst tid. Inget
     värde ändrat.
36. **Bayou Spa: arterna och rummen** (ditt beslut 2026-10-20: plats 3 vid
   lansering, familjen är din att välja). Ett utkast att stryka i, alla
   namn egna; sällsyntheten följer Haunted Manors (3 vanliga, 2 ovanliga,
   2 sällsynta, 1 episk, 1 legendarisk, 1 mytisk):

   | Art | Sällsynthet | Rum | Gillar | Personal | Egenhet |
   |---|---|---|---|---|---|
   | Bog Frog | Common | Lily Pad Room | steam, jazz | Entertainment | Kväker ett ackord vid incheckningen |
   | Mossling | Common | Lily Pad Room | moss, quiet | Housekeeping | Små skott växer där den sitter |
   | Firefly Sprite | Common | Willow Nook | fireflies, herbs | Room Service | Lyser upp korridoren där den går |
   | Mud Puppy | Uncommon | Mud Bath | mud, steam | Bellhop | Skakar lera på dörrvakten |
   | Gator Ghoul | Uncommon | Mud Bath | mud, jazz | Security | Ler med alldeles för många tänder |
   | Will-o'-Wisp | Rare | Willow Nook | fireflies, quiet | Front Desk | Slocknar när den blir blyg |
   | Swamp Hag | Rare | Herb Loft | herbs, steam | Entertainment | Brygger en dimma som luktar mynta |
   | Bayou Hydra | Epic | Steam Grotto | steam, jazz | Room Service | Varje huvud beställer något eget |
   | Cypress King | Legendary | Cypress Suite | moss, fireflies | Front Desk | Bär en krona av eldflugor |
   | Moon Heron | Mythic | Moonlit Lagoon | quiet, fireflies | Entertainment | Dess rop lugnar hela gatan |

   Rummen: Lily Pad Room 2×2, Willow Nook 2×2, Mud Bath 2×3, Herb Loft
   2×3, Steam Grotto 3×3, Cypress Suite 3×3, Moonlit Lagoon 3×3 (priserna
   ×20 Frostfangs, PLACEHOLDER). Ny dekor för de nya smakerna: Moss Mound,
   Firefly Jar, Steam Vent, Herb Rack, Mud Pot (jazz har redan Record
   Player). **Stryk, byt namn eller välj** arterna; natten bygger dem som
   klossmodeller med PLACEHOLDER-värden (steg 6) så att platsen går att
   spela, och de byts när du valt.

37. ~~**Bygg rummen själv, rumsvyn och en fri kamera i Build**~~ (besvarat
   samma natt: du väljer rumstypen, med en tooltip om monstren och
   nyckelmöblerna; varje stapel sin egen bonus, med min fördelning; inget
   rum drar ner stjärnorna; väggar på rutkanter, halva rutor med en knapp;
   inga färdiga rum; bekvämligheterna likadant; före världen och endless
   content. Allt i GDD §5.4 och §18.) (dina idéer 2026-10-21 natt, i
   chatten). Claudes förslag var:
   - **Rum av väggar:** du drar väggar längs rutornas kanter och sätter en
     dörr i en vägg; ett inneslutet område med en dörr är ett rum. Du
     möblerar det: en säng eller dubbelsäng, nattduksbord, sedan dekor.
     **Rummets typ** avgörs av dess nyckelmöbel (en säng: Standard Room, en
     kista: Coffin Suite, en sarkofag: Sarcophagus Suite …), med en minsta
     storlek per typ. *Avgörs av nyckelmöbeln* eller *du väljer typen när
     du trycker på rummet*. **Rekommendation:** nyckelmöbeln, som i Two
     Point Hospital: det man ser är det rummet är.
   - **Färdiga rum som snabbval:** dagens rum blir ritningar som lägger
     väggar och möbler i ett tryck, så en ny spelare (och en telefon) slipper
     dra varje vägg. **Rekommendation:** behåll dem så.
   - **Tre staplar i rummet:** storlek, möbler och dekor, och tillsammans
     ger de rummets nivå (i dag T1–T3 av dekorpoängen). *Tre staplar som
     tillsammans ger nivån* eller *varje stapel ger sin egen bonus*.
     **Rekommendation:** tillsammans, så att det finns ett mål.
   - **Rumsvyn:** tryck på ett rum så zoomar kameran in på det, väggen mot
     kameran blir genomskinlig, och staplarna visas. **Rekommendation:** ja.
   - **Kameran:** en fri kamera inom hotellets område: W/S framåt och bakåt,
     A/D åt sidan, hjulet zoomar, höger musknapp och dra vrider (åt sidan)
     och lutar (uppifrån till nästan vågrätt), en knapp för rakt uppifrån.
     På telefonen: ett finger flyttar, två fingrar zoomar och vrider.
     **Rekommendation:** bygg den först, den står på egen hand.
   - **Vad det kostar:** rummen byggs om från grunden (bygglogiken,
     rutnätet, gästernas vägar, modellerna: väggar, dörrar och möbler i
     stället för hela rum). De 21 spegelrummen från natten behövs inte när
     rummen byggs av väggar (Flip försvinner). **Fråga:** ska detta före
     resten av nattens lista (världen, endless content)?

38. **Endless content: dina beslut** (GDD A.11, nattutkast 2026-10-21,
   granskat av en blind granskare samma dag; varje fynd står bredvid sitt
   förslag i A.11 som "Scrutiny 2026-10-21"). Alla siffror är PLACEHOLDER.
   Per del: det som är ditt, valen och rekommendationen efter granskningen.
   - **VIP contracts:** *hur VIP:n kommer* (bussen bokad till hotellet /
     en vanlig gäst / en inspektion), *vad kontraktet kräver* (rumstyp och
     staplar / typ och art / ett mål för hela hotellet), *tidsgränsen*
     (45 min spel / 24 h / UTC-dagen), *belöningen* (pengar / pengar och
     artens Souvenir / Moon Shards), *hur många samtidigt* (1 / 1, 2 från
     4★ / 3). **Rekommendation:** bussen, rumstyp och staplar, 45 min spel
     som bara räknas när det hotellet spelas, pengar och Souvenir, 1 och 2
     från 4★. Nytt efter granskningen: **högst 3 avklarade per dag**, ett
     missat kontrakt försvinner, kravet ligger alltid över ditt bästa rum,
     och **VIP:n är en extra plats på bussen** (räknas inte i 40 %, rummet
     hålls) — en rad om det i §4.3 väntar på ditt ja.
   - **Expeditions:** *vem som får gå* (Wing-boende / även personal / en
     egen plats), *klockan* (realtid / speltid), *belöningen* (fast / fast
     och en chans på ett fynd / du väljer), *vad som gör en resa bättre*
     (antal och sällsynthet / gillar platsen / nivå), *Robux-skip* (nej /
     ja), *notis* "Your residents are back" (nej / ja). **Rekommendation:**
     Wing-boende, realtid, fast och ett fynd, gillar och nivå, inget skip,
     notisen. Nytt: resan betalar **1,5 × vad de hade tjänat på att stanna,
     med offline-taket** (annars var 8 h-resan vid varje utloggning alltid
     bäst), fyndchans per resa bland ännu inte funna bitar, en knapp **Best
     for this trip**; rebirth kallar hem gruppen. Notisen är en tredje text
     som du gör i Creator Hub (Engagement → Notifications).
     *Byggs natten 2026-10-26 enligt rekommendationerna (PLACEHOLDER), på en
     egen gren som inte mergas före lanseringen; lönen besvarad, se nedan.
     Kvar som ditt: punkterna ovan och notisens text.*
   - **Rare decor sets och Souvenirs:** *hur fynd görs* (slump / milstolpar /
     Souvenirs av milstolpe, set-bitar av slump med garanti), *vad ett set
     gör* (bara utseende / Decor-stapeln i ett rum / hela hotellet),
     *kopior* (en / en per fynd / hittad en gång, sedan köpt), *genom
     rebirth* (behålls / förloras). **Rekommendation:** milstolpe och
     slump med garanti, Decor-stapeln (+0,25) **i ett rum per set och
     hotell**, kopior till butikens pris per poäng, behålls. Nytt: **ett
     set per plats vid lansering** (15 bitar i stället för 30), slumpen
     drar bara ofunna bitar. **Ditt utseende:** *varje Souvenir egen
     modell* eller *en gemensam form (en liten monter) i artens färger med
     dess märke*. **Rekommendation:** den gemensamma formen, så att 27
     Souvenirs inte blir 27 modeller.
   - **The showcase:** *räckvidd* (gatan / gatan och en global veckotopp /
     även en visningstomt för andras sparade hotell), *vad som gillas*
     (spelaren / varje hotell / varje rum), *vilken siffra* (livstid /
     livstid på skylten och en veckosiffra / sedan rebirth), *belöning*
     (ingen / pengar per gilla / kosmetika vid milstolpar).
     **Rekommendation:** **bara gatan vid lansering** (Visit når inte ett
     hotell på en annan server), spelaren, livstid och vecka, kosmetika.
     Nytt: dagens uppdrag blir **"Visit 3 hotels"** i stället för "Like 3
     hotels"; den globala topplistan efter lansering, där varje gillare
     räknas en gång i veckan per spelare.
   - **Deeper mutations:** *vad som staplas* (en storlek och ett utseende /
     två vilka som helst / inget), *betalningen* (multiplicerad ×10 /
     adderad ×6 / den största +1), *rotationen* (månad / vecka / per
     familj), *Monster Book* (en stapel fyller båda och ger en titel / varje
     kombination en sida). **Rekommendation:** storlek och utseende,
     adderad, månad, båda fylls. Nytt: månadens mutation är en rad bland
     utseendena (så Golden finns varje månad) och en egen Seasons-rad i
     boken. **Ditt:** *får en missad månads mutation komma tillbaka utanför
     säsong som ett VIP contract*, eller *bara nästa år*.
     **Rekommendation:** bara nästa år, eftersom Seasons-raden inte längre
     hindrar någon titel.
   - **Residents level up:** *vad en nivå ger* (Wing och personal / även
     perk / bara Wing), *taket* (10 för alla / efter sällsynthet / höjs av
     rebirth), *hur nivån tas* (automatiskt / för pengar), *dubbletter
     som XP* (nej / ja). **Rekommendation:** Wing och personal, 10 för alla,
     för pengar, nej. Nytt: priset räknas i **den boendes egen Wing-takt**
     (betalar tillbaka på 2–27 h), XP **1 per minut i arbete** i Wing och
     som personal lika (cirka 15 h spel till taket).
   - **Vad rebirth behåller** (§6.4): i dag Residents, Monster Book,
     kosmetika, Moon Shards, Moon Tree, vänskap. Ska **nivåerna** och
     **fynden** (decor-set, Souvenirs) också behållas? Granskaren menar att
     rebirth då bara tar väggarna. **Rekommendation:** behåll båda: rebirth
     tar fortfarande pengarna, alla hotell och platserna, nivån har ett tak
     och set-bonusen gäller ett rum per set och hotell. Ett beslut, skrivet i
     §6.4.
   - **Byggordningen** (A.11.7): decor-modellerna börjar direkt vid sidan
     av; sedan The showcase, Residents level up, Deeper mutations, Rare
     decor sets, VIP contracts och sist Expeditions, när
     `tools/balance_model.py` har prövat dem mot offline-taket.
   - *Byggt 2026-10-21 morgon enligt rekommendationerna (PLACEHOLDER, går att
     ändra):* Showcase (bara gatan, "Visit 3 hotels", livstidsräkning på
     skylten, veckans favorit per gata, fyra skyltmärken vid 10/50/200/1000
     likes), residents levlar (tak 10, behålls genom rebirth), staplade
     mutationer (storlek + utseende, månadens mutation mars Mossy, maj
     Rainbow, juli Sunburnt, september Moonlit, titeln "Stacked Host").
     Dina beslut kvar: skyltmärkenas utseende, om nivåerna ska följa med
     genom rebirth, om en missad månads mutation får komma tillbaka, och
     månadsmutationernas namn.
   - *VIP contracts byggt 2026-10-21 morgon (PLACEHOLDER alla siffror i
     `Constants.Contracts`):* VIP:n åker som en extra plats på bussen (raden
     om det i GDD §4.3 är din), tre kontrakt per dag, 45 min, belöningen 15
     minuters inkomst × 1–6 efter sällsynthet. Dina frågor: belöningen på ett
     nytt hotell blir stor ($9K–18K, inkomsten räknas minst $10/s): rätt? En
     VIP som inte blir nöjd ger ingen belöning: rätt? **Rekommendation:**
     räkna inkomsten utan golv, och ge halva belöningen för en olycklig VIP.
   - ~~*Expeditions är inte byggda:* modellen visar att resorna fortfarande
     slår Wing (1,25–1,5 × med Pay 1,5; `archive/BALANCE-2026-10-21c.md`),
     och A.11 säger att de byggs först när det är ett riktigt val. Ditt
     beslut: Pay under 1 (0,75 eller 0,5), XP bara för speltid, och
     matchningsbonusen på fyndchansen. **Rekommendation:** Pay 0,75, XP som
     i Wing, bonusen på fyndchansen; och att en resa som kommer hem före
     inloggning inte också fyller offline-kassan.~~ (besvarat 2026-10-26:
     "Ja, rekommendationen"; GDD §18.)
   - *Sällsynt dekor och souvenirer byggt 2026-10-21 morgon (PLACEHOLDER i
     `Constants.Finds`):* fynd vid nöjda vistelser av Rare+ (2 %) och Hunter
     Night (25 % per spelare på gatan), pity efter 40 missar, setbonus +0,25
     på Decor-baren i det äldsta rummet med hela setet, souvenir vid artens
     tredje inflyttning eller första VIP-kontrakt; fynden behålls genom
     rebirth. Dina frågor: siffrorna; om fynden behålls; ett souvenirmärke för
     alla arter (färgat per art) ok; riktiga emblembilder (i dag en skiva med
     initialen); "äldsta rummet" som rätt tolkning.
   - *Expeditions byggt 2026-10-26 på grenen `claude/expeditions` (inte mergat, inte kört i Studio; PLACEHOLDER i `Constants.Expeditions` utom Pay 0,75):* antaget: platserna Haunted Woods / Frostfang Pass / Bayou Backwaters och vad var och en "gillar" (taggar ur arternas preferenser); gruppen är hemma i Wing när tiden är slut, lönen och fyndet väntar på Collect (tavlan i Wing-trädgårdens främre hörn på skyltens sida, eller pop-upen var som helst); en resa kan inte avbrytas; en rebirth betalar det räknade hittills (pengarna går sedan med rebirthen) och en resa som redan är hemma hämtas med sitt fynd; gruppens egna perks räknas inte i lönen; resornas fynd räknas inte mot vistelsernas pity (40), bara mot resornas egen (10 långa); notisen för resor på 2 h och mer har en PLACEHOLDER-text, "[PLACEHOLDER] Your residents are back from their expedition!", din att skriva i Creator Hub.

39. **Väggarna, dörren och möblerna: det granskaren såg som är ditt**
   (natten 2026-10-21; modellerna i `blender/rooms/<hotell>/`, bilderna i
   `review/`; felen rättas i byggskriptet samma natt, se dess README):
   - **Frostfangs väggar** läses som ett trästaket eller en bastu, inte en
     islodge, och dörren har Haunted Manors spetsbåge. **Rekommendation:**
     ljusare timmer med snö på överkanten och en rund eller rak dörr.
   - **Frostfangs möbler:** Ice Bed läses som en solstol, Ice Slab som en
     stengrav, Snow Nest och Glacier Coil som två likadana badkar.
     **Rekommendation:** gör om dem efter din bild när du har sett dem.
   - **De randiga diskarna** (Breakfast Buffet, Cocoa Bar) läses som
     tivolistånd, **garderoben** har ett starkt guldtak, **orgelns** pipor syns
     som prickar uppifrån, **Den Nest** läses som en hundkorg.
     **Rekommendation:** titta på dem i spelet först.
   - **Kistan och sarkofagen är stängda** och gästen ligger på locket.
     *Stängda* eller *öppna så att gästen ligger i*. **Rekommendation:** öppna.
     *Natten:* kistan är nu öppen och bredare (gästen ligger i den, en
     andra granskning visade att den låg på locket); sarkofagen är stängd.
     Säg till om kistan ska vara stängd igen.
   - **Badkaret** (2×1 rutor) rymmer en gäst halvliggande, inte rak.
     *Behåll 2×1* eller *gör det 3×2*. **Rekommendation:** 3×2.
   - **Orgeln** har en pall men gästen står vid den. *Stå* eller *sitta*.
     **Rekommendation:** sitta.
   - **Dörröppningen är 4 studs bred** (kontraktet, som rummens dörrar var):
     en bred gäst och en spelare får inte plats bredvid varandra.
     *Behåll 4* eller *5 studs* (väggbiten är 6). **Rekommendation:** 5.

40. **De byggda rummen i spelet: det som är ditt** (natten 2026-10-21, byggt
   och spelat i Studio, `TESTRUN.md` "Built rooms"):
   - **Startrummet** är ett L på fyra rutor till höger om disken sett från
     gatan: en 2×2 får inte plats, eftersom väggar inte får röra disken eller
     entrén. *Duger formen och sidan*, eller *flytta disken så att en 2×2
     får plats*. **Rekommendation:** flytta disken ett steg in.
   - **En ruta köpt bredvid ett rum får väggar av sig själv, gratis**, och
     **att välja rumstyp kostar inget**. **Rekommendation:** behåll båda.
   - **Tutorialens andra rum** kostar ungefär $180 (två rutor, väggar, dörr,
     Bed). **Rekommendation:** behåll; det är tidigt och billigt.
   - **Rumsvyn på mobilen:** panelens text är liten och HUD:ens högerkolumn
     skymmer rummet. **Rekommendation:** dölj högerkolumnen i rumsvyn och
     gör panelen bredare; säg till om du vill något annat när du sett den.

41. ~~**Nya rumstyper av de nya möblerna?**~~ (ditt ja 2026-10-26 till rekommendationerna, och mycket fler rumstyper: GDD §18 och A.13, byggs natten 2026-10-26) (natten 2026-10-21; 21 nya bitar
   för matsal, spel, lounge, badrum, trädgård och lobby, `Pieces.luau`,
   PLACEHOLDER). Frågor som är dina, var och en *ja* eller *nej*:
   - Ett **Game Room** (nyckel: Pool Table, Ping-Pong Table eller Arcade
     Cabinet, taggen fun) — och vilken art ska vilja ha fun? Ingen vill det i
     dag, så spelbitarna fyller bara Furniture-baren. **Rekommendation:** ja,
     och ge fun till Pumpkin Head och Ice Imp.
   - Ett **Dining Room** (nyckel: Breakfast Buffet eller Salad Bar), eller
     räcker Snack Bar? **Rekommendation:** räcker; låt Salad Bar och Dessert
     Trolley också vara nyckel för Snack Bar.
   - Ska ett rum med **Washstand och Toilet** räknas som en-suite och ge en
     bonus? **Rekommendation:** ja, en liten bonus på nöjdheten.
   - Ska **Fountain och Garden Bench** vara nyckel för Graveyard Garden?
     **Rekommendation:** ja.
   - Ska den nya **dekoren** finnas på alla platser (en modell per hotell)?
     **Rekommendation:** ja, när Frostfangs och Bayou Spas modeller görs.
   - **Utseenden granskaren tog upp** (felen rättas samma natt): Hall Stand
     läses som ett golvur, Crystal Ball Table som en tunna (duken utan veck),
     Fountains strålar som blå stavar (en vatteneffekt i koden kan ersätta
     dem), Arcade Cabinets myntlucka som ett ansikte. **Rekommendation:**
     titta på dem i spelet först.

42. **Världen: det som är ditt** (2026-10-21 morgon; tre gator i en värld,
   byggt och spelat i Studio utan bilder, `TESTRUN.md` "The world"):
   - **Avståndet mellan gatorna** (`World.StreetSpacing` 1400, PLACEHOLDER):
     nästa gatas hotell syns från gatans sista tomter men inte från de
     mittersta (dimman). *Behåll* eller *korta*. **Rekommendation:** korta
     till 1100, så syns de från fler tomter.
   - **Frostfangs och Bayou Spas mark- och lyktfärger, och ängen** längs
     vägen mellan gatorna: utkast. **Rekommendation:** titta när bilderna
     finns.
   - **Bayou Spas träd:** en cypress som klossmodell i dag, plus Bare och
     Crooked. *Modellera en cypress* eller *andra träd*. **Rekommendation:**
     en cypress med mossa.
   - **Två spelare på två gator samtidigt** är inte provat (bara du kan
     starta **Server and Clients**).

43. **Bayou Spas väggar och möbler: det som är ditt** (2026-10-21 morgon;
   `blender/rooms/bayou_spa/`, bilderna i `review/`; felen rättas i skriptet):
   - **Väggarna** läses som grön salongspanel snarare än träsk (inga plankor,
     ingen mossa eller väder). **Rekommendation:** grövre plank och mossa.
   - **Lily Basin och Steam Pool** är lika uppifrån (runda, turkosa, med
     näckrosblad), och Lily Basin är ankelhög. **Rekommendation:** gör
     Lily Basin högre som ett fat på fot.
   - **Pilträden** på Willow Hammock läses som svampar. **Rekommendation:**
     hängande grenar i stället för kupoler.
   - **Poserna** (modellerarens val): man ligger i Mud Tub och Steam Pool och
     sitter på Lagoon Perch. Ok?
   - **Frostfangs egna möbler har snö** på några (garderob, hylla, arkad,
     lampa) men inte andra, och de snötäckta blir vita block uppifrån.
     *Ingen snö inomhus* eller *snö på alla*. **Rekommendation:** ingen snö
     inomhus, frost i stället.
   - **Badkaren** (alla tre hotellen) är för korta för en gäst som ligger
     rak: samma fråga som i §2.39 (2×1 eller 3×2).

44. **De sällsynta seten: utseenden som är dina** (2026-10-21 förmiddag;
   `blender/decor/<set>/review/`; felen rättas i skriptet):
   - **Aurora Lodge** (Frostfang) läses mer som jul än islodge: den röda
     slädan med guldmedar är tomtens. *Behåll* eller *en släde i ljust trä och
     is*. **Rekommendation:** ljust trä och is.
   - **Lantern Grove** (Bayou Spa): lampan och grammofonen ser ut som vanliga
     möbler; kanoten och fönstret bär sällsyntheten. **Rekommendation:**
     titta på dem i spelet först.
   - **Namnen** på seten (The Count's Study, Aurora Lodge, Lantern Grove) är
     arbetsnamn.

45. **Glas och barpallar** (2026-10-21 eftermiddag):
   - **Glaset:** ingen kod gjorde delarna som heter `Glass` (fönsterrutorna i
     fasaderna, salladsbarens skydd, souvenirens glaskupa) genomskinliga, så
     de var ogenomskinliga i spelet. Nu gör koden dem till glas, ljust
     blåvitt och 55 % genomskinligt (min början). *Behåll*, *klarare* eller
     *mer frostat*. **Rekommendation:** titta i spelet först.
   - **Barpallen vid disken** (Frostfang): den sittandes knän slutar 0,55
     framför diskens kant, så gästen sitter en bit ut från disken. Modellerna
     kan inte rätta det (pallens `Use`-punkt och avstånden är kontraktets).
     **Rekommendation:** koden flyttar en barpall 0,7 mot en disk den står
     vänd mot.
   - **Sitthöjden** (alla tre hotellen): stolar, toalett och bänk har sitsen
     1,72–1,82 över golvet, så en sittande persons fötter hänger 0,6–0,7
     ovanför golvet (granskningen såg det på alla sitsar). Jag mäter först en
     riktig avatar på en stol i Studio. **Rekommendation:** blir fallet från
     sits till fot ~1,1, sänk sitsarna till ~1,1–1,2 och matbord och kortbord
     till ~2,0; barpallar och diskar som de är (fötterna på ringen).
   - **Cocoa Lounge-disken** (Frostfang) har röd-vita ränder ("candy-cane
     counter") som en granskare läste som cirkustält. *Behåll* eller *björk
     med ett rött band*. **Rekommendation:** behåll.
   - **Bayous mossgirlanger** längs disk- och bordskanter lästes som mögel.
     **Rekommendation:** behåll mossan men som en kort ljusgrön tofs per bit,
     inte mörka bågar längs hela kanter.
   - **Frostfangs snöflingor:** tre stora snidade flingor på salladsbarens
     luckor mot en sköld på buffén. **Rekommendation:** behåll (snidade
     flingor är lodgens panel, skölden buffens eget märke).
   - **Salladsbarens glasskydd:** granskarna drar åt två håll (för lågt att nå
     under, sedan för högt för att skydda något). Nu 1,6 över maten.
     **Rekommendation:** sänk underkanten till 1,1 över maten: mellan ansikte
     och mat, och gästen når ändå under.
   - **Spelhyllans höjd** (en granskare: för låg, en annan: för hög). Nu
     undersidan 2,26, toppen 5,06. **Rekommendation:** behåll och bedöm den i
     Studio bredvid en avatar.
   - **Frostfangs matstol:** ryggen når en sittandes tinningar och läses som
     en tron. **Rekommendation:** sänk toppen till ~3,6 (axelhöjd) med runda
     toppen och snöflingan kvar.
   - **Det granskarna drog åt båda håll** (sex rundor; sjätte rundan i
     `blender/rooms/<hotell>/README.md`): toaletten (vinglas eller
     blomkruka), Bayous värmelampor över maten (döljer maten uppifrån),
     Frostfangs buffé (läses som en byrå), Bayous golvlampa (fågelbur).
     **Rekommendation:** bedöm dem i spelet efter importen.

46. **Världen sedd i spelet: det granskaren såg som är ditt** (2026-10-22
   kväll; de första bilderna av de tre gatorna, blind granskning, `TESTRUN.md`
   "The world"). Bilderna ligger i `archive/screens/2026-10-22_world_*.jpg`.
   Det som är kodfel tar nästa session (se nedan). Det här är utseende:
   - **Hotellen har inget tak** sett från spelets höjda kamera; man ser ner
     i en öppen låda (som i §2.13). **Rekommendation:** ett platt tak med
     list över varje köpt ruta på översta våningen, i fasadens stil.
   - **Tomtens oköpta rutor är en svart platta** som i snön läses som asfalt
     (som i §2.24). **Rekommendation:** samma mark som platsens värld, med
     en svag kant, i stället för svart.
   - **Bayou Spa läses inte som träsk:** limegrön mark, samma kala träd som
     Creepy Lane, inget vatten, vass eller dimma; hotellet, kanterna och
     marken har samma gröna. Kantstenen lyser limegrönt längs hela gatan.
     **Rekommendation:** mörkare, gråare grön mark, vass och ett par
     vattenpölar mellan träden, kantstenen inte lysande. (Cypressen, §0,
     ersätter klossträden.)
   - **Frostfangs hotell läses som ett kontor:** platt blå låda med vita
     band. **Rekommendation:** vänta på taket; timmer och snö på listen sedan.
   - **Gatlyktorna:** 13–14 per sida, tätt, "en landningsbana".
     **Rekommendation:** hälften så många, varannan borttagen.
   - **Tre beläggningar på tio studs** framför entrén (rosa tegel, orange
     kullersten, mörkt grus) och två olika kantstenar. **Rekommendation:**
     forecourtens gång i trottoarens tegel.
   - **Gatorna är skarpa rektanglar** med skogen i en rak linje och tomma
     tomter ("en parkeringsplats"). **Rekommendation:** låt skogskanten gå
     ojämnt in mot tomternas baksida.
   - **Vägen mellan gatorna** går genom mörker utan lyktor eller kant och
     svänger i rät vinkel vid gatans ände. **Rekommendation:** några lyktor
     längs den och en rundad sväng.

47. **Bayou Spas cypress: kronan** (2026-10-22 kväll; `blender/street/trees/`,
   bilderna i `review/blind/`, silhuetterna i `review/silhouettes_cypress.png`).
   Byggd och validerad: en räfflad stam som vidgar sig till en hög fot, fyra
   knän, mossa i långa trasiga draperier och en krona av breda klumpar. Tre
   blinda granskningar i rad läser kronan som "en akacia eller paraplytall
   på en pinne", inte en cypress, hur tät den än görs. Stammen, foten och
   mossan är rättade. **Alternativ:** (a) behåll klumparna, det är leksaksstilen;
   (b) en kon av hängande, fransiga våningar som granarnas men platta och
   olivgröna, med mossan draperad över grenarna (en sumpcypress är ett
   barrträd med smal topp); (c) silhuett B, lutande med ett paraply.
   **Rekommendation:** (b): det läses som cypress på avstånd och kostar inte
   fler trianglar. Den är inte lagd för import förrän du valt.

48. ~~**Buggar där rättningen är ett beslut**~~ (ditt ja 2026-10-26 till alla fem rekommendationerna, GDD §18; rättas natten 2026-10-26) (2026-10-22 kväll, tre
   kodgranskningar; det som var rena fel är rättat, se nedan). Fyra frågor:
   - *Byggt på grenen `claude/fixes-2-48`, inte kört i Studio (2026-10-26).*
   - **Ett accepterat VIP-kontrakt efter en rebirth** stannar kvar för ett
     hotell som kedjan inte längre har; dess klocka går aldrig, så det tar en
     plats i ledgern (och en av dagens tre) tills hotellet öppnas igen, kanske
     i timmar. Gamla erbjudanden från ett högre betyg finns också kvar (en
     Mythic vid 2★). **Rekommendation:** en rebirth avslutar kontrakten och
     erbjudandena för hotell som kedjan inte har kvar, utan straff.
   - **Personal räknas två gånger:** flyttar man en resident från ett hotell
     man lämnat till det man spelar, fortsätter det lämnade hotellet tjäna som
     om det hade personalen kvar (dess takt fryses när man åker). **Rekommendation:**
     en resident som är personal på ett annat hotell kan inte flyttas förrän
     man är där, eller så räknas det lämnade hotellets takt om när den flyttas.
   - **Offline-inkomsten** får vänbonusen (+10 %) om en vän råkar vara online
     när man kommer tillbaka, för hela tiden man var borta. **Rekommendation:**
     ingen vänbonus på offline-inkomst.
   - **Personal på ett hotell man inte spelar** får ingen XP, residenter i
     Wing får (A.11.6 säger "i samma takt i Wing och vid en personalpost ...
     medan spelaren spelar"). **Rekommendation:** samma XP för personal på
     kedjans andra hotell, som för Wing.
   - **Eventdekor** (sålda en gång) kan ställas ut i hur många kopior som
     helst gratis, och varje kopia ger full Decor. **Rekommendation:** en
     kopia per köp, som de andra.

49. ~~**Bayou Spas kit och fasad: det som är ditt**~~ (ditt ja 2026-10-23 till alla modeller, med rekommendationerna nedan; GDD §18) (2026-10-23, LAUNCH.md
   arbete 5; `blender/hotel/bayou_spa/`, `blender/facade/bayou_spa/`, bilderna
   i deras `review/`; tre blinda rundor, resten är rättat, se README:erna).
   Byggt: disken, trappan (två), skylten, dörrskylten, de fem Bayou-dekorerna
   och de fem alla kit har, och fasadens sju delar. **Ditt ja eller nej per
   modell** i godkännanderundan. Det granskarna såg som är ditt:
   - **Fasaden läses som "en grön lada"** på avstånd: salviagrön panel,
     gröna fönsterluckor, ett cypressvalv med lotus, mossa och en
     eldflugelykta. *Behåll* eller *mer träsk på väggarna*.
     **Rekommendation:** se den i spelet först (Workbenchs platta ljus gör
     salvian mörk); är den fortfarande en lada, mossa längs taklisten och en
     fris av näckrosblad på listen vid 12.
   - **Steam Vent** läses som en snögubbe av vita bollar: ånga som inte kan
     vara genomskinlig blir alltid bollar. *Behåll* eller *ta bort ångan*
     (en het pöl med galler). **Rekommendation:** behåll.
   - **Mud Pot** läses som en gryta. **Rekommendation:** behåll (en kruka
     med lera är vad namnet säger).
   - **Fasadens fönsterluckor** är 1–1,5 studs breda (mer får inte plats
     bredvid ett 8 studs brett fönster på en 12-studsdel) och gröna mot
     salvian; granskarna läste dem som stuprör. *Behåll*, *en annan färg*
     (lotusrosa eller mörk cypress) eller *inga luckor*. **Rekommendation:**
     behåll och se dem i spelet.
   - **Tredje rundan** (bara utseenden kvar): Moss Mound läses som en slime
     (de rosa svamparna som en tunga), Firefly Jar som en lykta (glaset är en
     bur av ribbor eftersom inget kan vara genomskinligt; den glödande kärnan
     syns mellan dem), Herb Rack som en stege med pärlband. **Rekommendation:**
     se dem i spelet med glöden tänd först; svamparna kan bli bruna.
   - Inte ändrat, gemensamt för alla kit: diskens layout (nyckelskåpet vid
     bakkanten), trappans boxar, mattans hörnbit, bänken, blomlådan.

50. ~~**VIP-loungesetet**~~ (ditt ja 2026-10-23 till bitarna, priserna som PLACEHOLDER, pengar och rekommendationerna nedan; GDD §18) (2026-10-23; GDD A.2, §10.2; `blender/decor/vip_lounge/`,
   `review/pieces_sheet.png`): fem dekorbitar för alla platser, en modell för
   alla tre hotellen (svart lack, guld, röd sammet): **Velvet Rope** (3×1,
   quiet, $300), **VIP Sofa** (2×1, två sittplatser, quiet, $600), **Cupcake
   Tower** (1×1, snacks, $400), **Red Carpet** (4×2 matta, $200), **VIP Sign**
   (2×1 på väggen, "VIP" i glödlampor, $500). Allt PLACEHOLDER. Frågor:
   - **Bitarna, taggarna och priserna.** *Stryk, byt eller sätt priser*.
   - **Köps för pengar** som annan dekor (passet låser upp dem); eventdekor är
     gratis att ställa ut, men en VIP-bit gratis vore Decor-poäng för Robux.
     *Pengar* eller *gratis*. **Rekommendation:** pengar (byggt så).
   - **Cupcake Tower** står på golvet till 3,9 studs; granskarna läste den
     som en julgran. *Behåll* eller *mindre, på ett bord*.
     **Rekommendation:** behåll till du sett den i spelet.
   - **Mattan** är kitens gemensamma löpare i rött och guld; granskarna
     ville ha mer mönster. **Rekommendation:** behåll, så att den passar ihop
     med de andra löparna.

51. **De riggade monstren i spelet: en blind granskares intryck** (natten
   2026-10-24; tre nattbilder från trädgården bakom Bayou-hotellet, i
   scratchpad, en av dem i `archive/screens/2026-10-24_rigged_residents.jpg`).
   Allt nedan är utseenden du redan sagt ja till; inget är ändrat. Det
   granskaren såg, med Claudes förslag:
   - **Ögonen bländar** (Slime, Mud Puppy): de lysande ögonen läses som
     lampor, "en vit prick" på en telefon. Förslag: titta i spelet först
     (§1.13); dämpas de, är det en ändring i `Glow_Eyes` för alla.
   - **Frost Troll läses som en marshmallow bakifrån**, Werewolf som en björn
     bakifrån, Mud Puppys röda tofs som en mössa. Förslag: behåll (bara
     ryggar syntes; ditt ja gällde framsidan).
   - **Ghost sitter på gräset** i stället för att sväva: uppmätt 0,34 studs
     luft under. Förslag: behåll till du sett den röra sig (§1.13).
   - **Slime och Mud Puppy syns dåligt** på håll i spelets kamera (små, mörk
     brun mot mörkgrönt). Förslag: behåll; storlekarna är dina (`Species.luau`, dina ja).
   - Falskt eller utrett: Skeleton "lutad 45°" (stilla: höfterna 0°, ryggen
     högst 2° på 6 s; en gångbild inte mätt, så lita på dina ögon i §1.13);
     Hydran "saknas" (den stod 89 studs bort, utanför bild); trädgårdens svarta
     bakkant är hotellets mark i natten.

52. **Det första intrycket: gatan, entrén och lobbyn, enligt en blind
   granskare** (natten 2026-10-24; bilder `archive/screens/2026-10-24_along_street.jpg`
   och `2026-10-24_lobby_desk.jpg`, ett nytt hotell på Creepy Lane). Inget är
   ändrat: allt nedan är utseenden eller placeringar du redan sagt ja till.
   Det granskaren tog upp, med Claudes förslag:
   - **Hotellet läses som en container**: platt tak utan list eller takfot,
     sidoväggen helt slät, ingen skylt på själva huset. Förslag: titta efter
     lanseringen (fasaderna är godkända; en takfot vore en ny bit i alla sju
     stilar).
   - **Lobbyn är en stor tom låda**: kala väggar, nästan svart golv, disken
     liten mitt i, inget som visar var gästerna köar. Förslag: en kömarkering
     framför disken (en matta finns redan som dekor) efter lanseringen.
   - **Insidan av framväggen är rosa** mot de lila innerväggarna, och
     taket syns svart över väggarna från den höjda kameran. Förslag: titta i
     spelet; fasadens insida har fasadens färg.
   - **Rumsdörren öppnar mot svart** (rummet är mörkt inifrån lobbyn), och
     skylten ovanför är för liten för att läsas. Dörren är 4 × 7,2 som
     kontraktet säger.
   - **En svävande orange kula över valvet**: entréns lykta, utan synlig
     fästare. Förslag: titta på den; en konsol vore en ändring i fasaderna.
   - **Den orange trottoarkanten** är det skarpaste i varje bild, och **de
     tomma tomterna syns inte** (inget visar att marken bredvid går att äga).
     Förslag: behåll till efter lanseringen.
   - **Skylten står på trottoaren långt från dörren** och läses som en
     busshållplats. Förslag: behåll (den flyttades dit ur entrén 2026-10-19).
   - Falskt: gången "en person bred" (6 studs, ditt värde); gästen "inne i
     spelarens fötter" (Claude ställde spelaren på köplatsen, och gäster
     kolliderar inte).

53. **Kosmetikan i spelet, enligt en blind granskare** (kvällen 2026-10-24;
   skyltarna Pumpkin, Icicle och Lantern, entréns Bat Bunting och Fairy
   Lights; bilder `archive/screens/2026-10-24_cosmetic_pumpkin_sign.jpg` och
   `2026-10-24_cosmetic_bat_bunting.jpg`). Inget ändrat; allt är utseende.
   - **Bat Bunting syns knappt**: mörka fladdermöss mot den mörka valvväggen,
     och de läses som vimplar. Förslag: ljusare färg eller en kant, efter
     lanseringen; den säljs inte för Robux förrän du sett den.
   - **Pumpan läses inte som en pumpa** (toppen bakom skyltens lila huvud,
     bara orange sidor och en sågtandad kant syns), och skylten får en
     neonkant bara med pumpan. **Snön på Icicle** läses som rör, mest på
     högra sidan.
   - **Lyktorna och ljusslingan lyser inte upp något** synligt: varje
     kosmetika har sitt ljus enligt kontraktet (ett per set), men svagt.
   - **Entrédekorationerna sitter inne i valvet** bakom lyktan, inte på
     valvets framsida, och syns inte från sidan.
   Claudes förslag: titta på dem i spelet (Store → kosmetika) och säg vilka
   som ska göras om efter lanseringen.

54. **Tutorialens andra rum bakom hotellet** (kvällssprinten 2026-10-24,
   tutorialen spelad som ny spelare med riktig mus, `Test_Launch1024g`).
   Startrummet täcker hela bakre raden av startkvadraten, så fyra plattor
   köpta rakt bakom hotellet (det naturliga stället) blir en ficka utan
   väg till hallen: köpet sätter väggar mot startrummet av sig självt, och
   enda dörren som går är **genom startrummet**. Spelet godtar det (rummet
   blir färdigt och gästerna går genom startrummet till det), så ingen
   fastnar, men Gloom säger "draw Walls round them, put in a Door" och
   väggarna finns redan. Frågan är din: får ett rum nås bara genom ett
   annat rum? Förslag: **ja, behåll** för lanseringen (inget fastnar);
   efteråt kan guldplattorna i SecondRoom visa bara de som gränsar till
   hallen, eller Gloom säga "beside the hallway".

55. **Ett rum som öppnas mot en avstängd korridor** (natten 2026-10-26,
   kodgranskning; **troligen din fredagsbugg**, "en gäst i ett rum som inte
   är inneslutet"). Enligt A.12 är en yta *hall* bara om den har entréns
   mynning, en trappa eller en disk. Bygger man en korridor och stänger den
   mot lobbyn med en dörr, är korridoren ingen hall, och tar man sedan bort
   en vägg mellan ett rum och korridoren blir rummet **hela ytan**: väggen
   är borta, rummet växer (storleksstapeln stiger) och är fortfarande
   "färdigt", så bussen bokar gäster dit. Ett tredje rum vars enda dörr går
   till korridoren nås då bara genom det rummet (jfr 54). Koden gör som A.12
   säger, så det är ditt val:
   - **A (förslag):** en yta räknas som hall också när den har **två eller
     fler dörrar** (en korridor), så att ett rum aldrig kan öppnas mot den
     (`RoomTaken`, som mot lobbyn). Enkelt att förstå: ett rum har en dörr.
   - B: behåll, ett rum kan vara vilken sluten yta som helst med en dörr.
   - C: en vägg mellan ett rum och en yta utan rum får inte tas bort
     (rummet ändrar aldrig form utan Walls → Make room).
   Natten återskapar det i Studio och ändrar inget.

56. **Decor-flikens ordning** (natten 2026-10-26, spelat med mus som ny
   spelare): fliken börjar med **13 låsta "?"-kort** (sällsynta fynd och
   souvenirer) och butiken kommer först efter dem; på skärmen syns bara
   låsta kort, och man måste scrolla för att hitta något att köpa. Ordningen
   står i UI.md (Found, sedan ej funna, sedan butiken). Förslag: **Found,
   butiken, ej funna sist**.

57. **Rum där gästerna gör saker: dina val** (natten 2026-10-26, utkastet är
   GDD A.13; alla siffror PLACEHOLDER). Natten bygger reglerna, raderna och
   blockouter för fyra typer (Game Room, Bar, Indoor Pool, Cinema) och väntar
   med det som står nedan.
   - **Besök:** en gäst går ibland från sitt rum till ett aktivitetsrum som
     möter en av dess preferenser, gör saken 20–40 s och går tillbaka. Ett
     besök räknas som preferensen mött och ger +5 nöjdhet. Våningsregeln i
     dag (en amenity på samma våning räcker, osedd) försvinner. **Förslag:
     ja.**
   - **Typerna** (A.13.2): Game Room, Billiard Hall, Cinema, Bar,
     Restaurant, Dance Floor, Indoor Pool, Outdoor Pool, Gym, Spa, Karaoke
     Lounge, Sauna (Frostfang), och de amenities som finns blir besöksrum.
     Stryk eller lägg till fritt. **Förslag:** alla; Billiard Hall kan slås
     ihop med Game Room om du vill ha färre.
   - **Nya preferenser** (*film, drinks, dining, dance, swim, fitness,
     pampering, singing, billiards*): i dag har varje art två. **Förslag:**
     en tredje preferens per art enligt kolumnen "Wanted by" i A.13.2, så att
     varje typ har minst två arter som vill dit.
   - **Utomhuspoolen** (A.13.4): A en gård bakom hotellet (nya
     "yard"-plattor utan tak, staket, grind), B förgården bredvid gången, C
     taket. **Förslag: A.**
   - **Delade möbelset** (A.13.3: Lounge, Dining, Stage, Poolside, Games,
     Fitness): en möbel räknas i varje typ dess set tjänar. **Förslag: ja.**
   - Utseendet på varje modell är ditt (§1), och ingen läggs för import
     innan du sagt ja.

58. **Ett hotell du lämnat tjänar på sin senaste takt, med boost och VIP**
   (natten 2026-10-26, kodgranskning). Bakgrundsinkomsten (25 % av takten
   när du spelade det, §6.4) räknar in en 2x-boost, VIP:ns ×2 och
   vänbonusen som gällde då. Spelar du ett hotell under en 15-minutersboost
   och reser, tjänar det på dubbel takt så länge du är borta. Det tjänar
   också om du sålt allt i det innan du åkte. **Förslag:** takten räknas
   utan boost, VIP och vänbonus (bara gästernas grundlön och personalen).

59. **Trappan säger inte varför den inte går** (natten 2026-10-26, spelat med
   mus på en ny våning 2). Efter att plattor köpts ovanför nekades trappan i
   alla fyra vridningar med "The door would open into a wall", fast det som
   saknades var en ruta att kliva av på (trappans fot eller topp utanför det
   ägda, eller mot disken). **Förslag:** spöket visar trappans fot och topp
   som två markerade rutor (grön/röd), och texten säger vilken som är
   blockerad ("The top lands outside your floor 2" / "The foot is against the
   desk"). Det är text och visning, så det väntar på ditt ja.

60. **Rum där gästerna gör saker: två följder av besöken** (natten 2026-10-26,
   runda 2). (a) Bussens bonus för amenities räknar nu **hela hotellets** rum
   som går att besöka (förut bara våningens), med samma vikt, så den kan bli
   större. Förslag: behåll, och väg om den när du balanserar A.13. (b) Ett
   populärt aktivitetsrum har nästan alltid en besökare och är då "busy": det
   går inte att riva, byta typ eller ändra storlek på det. Förslag: en knapp i
   rumsvyn "Close for guests" som slutar ta emot nya besök tills rummet är
   tomt.

## §3 Creator Hub och publicering

1. ~~**Slå på Studio Access to API Services**~~ (gjort 2026-10-19: på i
   Experience Settings; save och load provas nu, resultatet i
   `archive/NATTLOGG-2026-10-19.md` och memory `phase-status`).
2. ~~**Skapa passen och produkterna i Creator Hub**~~ (gjort 2026-10-20 av
   Claude i din Creator Hub, på ditt ord: de fem passen, de åtta produkterna,
   ad-belöningen och fem presentprodukter, med GDD §10.2:s priser och
   ikonerna från `ui/`; id:na står i `src/shared/Store.luau`). Kvar:
   - **Ad-belöningen "2x Cash (ad)" kostar 1 Robux**: Roblox tillåter inte en
     gratis produkt. Ingen betalar den (annonsen ger den, och Store visar den
     inte), men priset syns i Creator Hub.
   - **Facade packs** (fyra pass och deras presenter) skapas när fasaderna är
     modellerade och har bilder; tills dess står de som "Soon". Fasaderna och
     ikonerna finns nu (grenen `claude/store-art-87789a`: pass- och
     presentikoner i `ui/`, `Store.luau` med id 0). Kvar: passen och
     presenterna skapas i Creator Hub (orkestreraren i webbläsaren, LAUNCH #9)
     och id:na skrivs in; grenen mergas inte förrän dess (natten 2026-10-24).
   - **Managed Pricing** (§10.1) är inte påslaget: Creator Hub →
     experiencen → **Monetization** → **Passes**, knappen **Get started**
     under "Earn more with Managed Pricing". Ditt val; Claude kan göra det
     om du säger till.
3. **Notifikationer** (GDD §9, A.9; dina val 2026-10-20: "till is full" och
   "Full Moon tonight"). **Byggt** (`src/server/NotifyService.luau`): spelets
   egna servrar skickar via Open Cloud, ingen server utanför behövs. Provat i
   Studio 2026-10-20: kön, att en server tar en notis åt gången, lördagens
   utskick och att den som redan spelar hoppas över; själva sändningen bara
   loggad ("would send"), eftersom nyckeln saknas. Kvar, i ordning:
   1. **API-nyckeln (din; Claude får inte hantera nycklar):** Creator Hub →
      **Open Cloud** → **API Keys** → **Create API Key**. Lägg till API-systemet
      för **user notifications** med skrivrätt, begränsat till den här
      experiencen. Kopiera nyckeln.
   2. **Hemligheten (din):** Creator Hub → experiencen → **Secrets** → skapa
      en som heter exakt `OpenCloudKey`, klistra in nyckeln, domän
      `apis.roblox.com`.
   3. ~~**HTTP:** Studio → File → **Experience Settings** → **Security** →
      **Allow HTTP Requests** på.~~ (gjort av dig 2026-10-23; når den
      publicerade servern med nästa Publish, LAUNCH #11.)
   4. **De två texterna** skapas i Creator Hub (experiencen → **Engagement** →
      **Notifications**): "Your residents' till is full" och "Full Moon
      tonight". Claude kan göra det om du säger till; deras id skrivs sedan in
      i `NotifyService.Messages`.
   Claude kollar de exakta menynamnen i Robloxs dokumentation när du är där.
4. ~~**Översättning**~~ (påslagen av dig; Claude lade till koreanska,
   indonesiska och turkiska 2026-10-23: 14 språk, alla med Strings & Products
   och Information på; Audience → Localization → Languages).
5. **Grupp-belöningen** (GDD §9: gratis decor och +5 % cash för den som går med
   i gruppen): vilken grupp? Säg dess id så byggs belöningen.

## §4 Före release

**Lanseringen (dina beslut 2026-10-23, planen i `LAUNCH.md`):** soft launch så
fort allt är klart, målet den här helgen. Inget testet med vänner: du och
Claude testar. Det som är ditt, i ordning:

1. ~~**Importen av de 136 filerna**~~ (§0.12): gjord och sparad
   2026-10-23.
2. ~~**Din manuella reset** av veckokvoten när Claude skickar en notis.~~
   (bortfallen: ingen manuell reset, ditt besked 2026-10-23, `LAUNCH.md`.)
3. **Notifikationernas nyckel och hemlighet** (§3.3 steg 1–2), 5 minuter.
4. ~~**Bayou, VIP-loungen och de fyra facade-paketen**~~: ja till allt
   2026-10-23.
5. ~~**Balanskörningens sammanfattning:** ditt ja innan värdena gäller.~~
   (besvarat 2026-10-23: "ja till balanskörningen"; de sju värdena är dina
   beslut, GDD §18, PLACEHOLDER struket på dem; sammanfattningen i
   `archive/BALANCE-2026-10-23.md`.)
6. **Ikon och thumbnails:** välj av tre.
   *Natten 2026-10-26:* tre thumbnails och tre ikoner tagna **i spelet**
   (`archive/screens/store-art-2026-10-26/`: byggläget över ett fullt hotell,
   gatan med skylten, rumsvyn med ett Skeleton och en Zombie; ikonerna
   beskurna ur dem), blint granskade. Granskarens dom: **ingen är klar för
   butiken**: gränssnittet tar en tredjedel (1, 3), monstren är prickar,
   rummen mörka och tomma, fasaden en slät vägg utan fönster (2), skylten
   klipps i ikon 1. Bäst: thumbnail 1 (visar idén) och ikon 2 (en figur).
   Två fel den såg är rättade samma natt (⟳ som inte ritades, en klippt
   Place-knapp). **Förslag:** behåll Blender-bilderna (punkten ovan) som
   huvudbilder; ta om rumsvyn i spelet utan HUD, med tända rum och en
   möblerad svit, som en extra "så här ser det ut"-bild om du vill ha en.
7. ~~**Frågeformuläret** (Maturity & Compliance)~~: redan ifyllt (ditt
   besked 2026-10-23).
8. **Titel och beskrivning:** titeln "Build A Monster Hotel!" (din,
   2026-10-23); Claudes nya beskrivning (989 tecken, med en Halloween-rad som
   ska bort efter 3 november) står i `docs/STORE_PAGE.md`. Du klistrar in
   den, eller säger till så lägger Claude in den i Creator Hub.
9. **Publish**, en kvart på **din egen telefon**, och att göra spelet publikt.
   Före Publish (natten 2026-10-24): Studios öppna kopia säger fortfarande
   **60** spelare per server (`Players.MaxPlayers`), fast Creator Hub säger
   10, och spelet varnar om det vid varje Play. Claudes råd: stäng platsen och
   öppna den igen från Roblox (**File → Open from Roblox**) innan du trycker
   Publish, så att Studio läser 10 och inte skriver tillbaka 60. Claude
   kontrollerar serverstorleken i Creator Hub efter Publish.

<!-- Checklistan till en release. Först ett test med vänner (privat), sedan
den publika. Claude bockar av sitt; det som är ditt står med menyn. -->

**Testet med vänner (privat):**

1. **Låst till Studio:** fusk-kommandona (`DevCommand`) och testprofilen
   (`StudioProfile`) fungerar bara i Studio; på en publicerad server finns
   inga kommandon alls (2026-10-20). Claudes; inte provat på en riktig
   server än.
2. ~~**Serverstorlek 10**~~ (ditt ja 2026-10-23; satt av Claude samma dag:
   Places → startplatsen → Access → Maximum Visitor Count, var 6). Private
   servers på för 100 Robux i månaden (Audience → Advanced settings); **priset
   kan bara ändras var 60:e dag.**
3. ~~**Tempot och tutorialens svit**~~ (§2.27, §2.28): byggt och spelat i
   Studio 2026-10-20 (`TESTRUN.md`, "Pacing and the tutorial's free area").
4. **Spela på en riktig telefon** (§1.9) och **spela första kvarten** (§1.1).
5. **Publicera** (File → Publish to Roblox), så kommer ändringarna och
   den borttagna `SpawnLocation` (§2.13) med.
6. **Vem som får spela:** i Creator Hub ersätter publiken **Playtest** de
   gamla Private och Limited; där bjuder du in testarna. Claude kollar de
   exakta stegen i Roblox dokumentation när du är där.

**Den publika releasen, därtill:**

7. ~~**Passen och produkterna**~~ (§3.2, skapade 2026-10-20); kvar där:
   facade packs och Managed Pricing.
8. **Frågeformuläret om innehåll** (Creator Hub, experiencens
   **Maturity & Compliance**). Claudes genomgång av koden (2026-10-20), att
   svara ärligt efter:
   - Våld: inget. Hunter Night skrämmer bort jägare med Boo! och fällor;
     ingen skada, ingen död (`HunterService`).
   - Rädsla: tecknat läskigt, "cozy creepy". Inget blod, ingen alkohol,
     inget grovt, ingen romantik.
   - Slump: mutationer slumpas gratis i spelet; inget betalt slumpköp (§10.1).
   - Spelarnas eget: man ställer ut färdiga bitar på ett rutnät; ingen fri
     text, ingen ritning. Pings är färdiga fraser; den enda textrutan är
     koder, och den syns bara för en själv.
   - Chatten är Robloxs egen.
   Det bör ge **Minimal** eller **Mild**, vilket Kids/Select kräver (§14.3).
9. **Koderna** `WELCOME` ($500) och `SPOOKY` (3 Moon Shards) är
   platshållare: vilka ska finnas (§9)?
10. **Ikon och miniatyrbilder:** Claude ritar utkast när du vill;
    utseendet är ditt.
11. Rewarded ads, översättning, notifikationer och gruppen: §3.3–3.5 och
    ad-produkten i §3.2.
12. **Hur många delar en full server bär** (kvällssprinten 2026-10-25, mätt
    i Studio). Ett fullt hotell (3 våningar, 43 rum) är 3 751 delar, och
    kedjans hotell som inte spelas ritas lika fullt på sina gator (också
    3 751). Tio spelare med tre fulla hotell var blir ~112 000 delar på
    servern; klienterna klarar sig (strömning är på, en telefon i
    simulatorn höll 16,7 ms i median). Servern är inte mätt med tio
    spelare. **Förslag:** mät på en riktig server efter Publish (del 3). Om
    minnet blir för högt ritar Claude kedjans icke spelade hotell som bara
    fasad och skylt (de syns bara på avstånd från en annan gata), efter
    lanseringen.
