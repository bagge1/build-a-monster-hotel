# Nattbrief — 2026-10-26

Augusts val i förberedelsesessionen 2026-10-26 (02:54–), alla i GDD §18
2026-10-26:

- Expeditions efter rekommendationen.
- Ja till WAITING §2.48 (fem buggar) och §2.41 (rumstyper), och till många
  fler rumstyper där gästerna gör saker.
- **Natten får merga** till main när en gren är grön.
- Bara 90 %-regeln för veckokvoten.
- Han startar **Server and Clients** innan han lägger sig.

Han vill att natten arbetar ungefär **tio timmar i sträck utan att få slut
på saker att göra**, och att buggtestningen är **extensiv och rigorös**.
Hans ord: "Jag hittade allvarliga buggar 1 min efter jag playtestade i
fredags."

Läget vid start: weekly 0 %, 5-timmars 0 % (reset 06:50). Main är ren och
pushad. Spelet är inte publicerat.

Inte valt, och därför inte byggt: Co-managers (§2.5) och Winter crossover
(§2.8). Emotes och gruppbelöningen har inget förslag än och blir bara utkast.

## Hur buggar jagas i natt (gäller varje steg)

Fredagens buggar hittade han på en minut genom att bygga fritt med musen.
Kvällens tester gick genom remoter och dev-kommandon och såg dem inte, och
den exakta vägen i hans rapport hittades aldrig. Därför gäller i natt:

1. **Spela som han.** Ny `Test_`-profil, riktig mus och riktiga tangenter
   (`user_mouse_input`, `user_keyboard_input`), Studio framme. Dev-kommandon
   bara för att ställa upp ett läge, aldrig för det som provas.
2. **Angrip varje system enligt en lista** som skrivs i loggen innan
   rundan: verktygen i fel ordning, dubbelklick, avbrott mitt i en dragning,
   riva, flytta och sälja medan gäster bor där, kanter och hörn, våningar,
   trappor, fönster på en telefon, att lämna och komma tillbaka mitt i, att
   resa, återfödas och köpa i fel läge.
3. **En vakt på servern under alla playtests** (en Script i den körande
   servern, inte i `src/`). Den prövar spelets regler var 0,5 s och loggar
   varje brott med tid:
   - en gäst i ett rum som inte är färdigt,
   - NaN, oändligt eller negativt i pengar och poäng,
   - en resident på två ställen,
   - trasiga nycklar i profilen,
   - instanser som växer utan att något byggs (läckor),
   - varje fel eller varning i konsolen från spelets egen kod.
4. **Nya ögon på koden:** bakgrundsagenter, en per system (bygg och rum,
   gäster och buss, residents och personal, ekonomi och kedja,
   VIP/fynd/showcase, gränssnitt och inmatning). De har bara läsrätt, får
   ingen gissning med sig och har som uppdrag att hitta fel. Varje fynd
   **återskapas i Studio** innan det räknas. Läs usage före varje agent.
5. **Varje bugg hanteras likadant:** återskapad, en spec som faller,
   rättningen, sedd i spelet, alla specs och `stylua src/ && selene src/`
   igen. Den hamnar i loggens buggtabell: vad, hur den hittades, commit.

## Arbetet, i ordning

1. **Launch run del 1, två spelare** (`TESTRUN.md` "Launch run" del 1;
   skill `playtest` "Two players"). Han har startat Server and Clients.
   Kör det först, medan fönstren lever. Aldrig `start_stop_play` medan det
   körs, varje "leave"-halva sist. Stäng sedan Server- och klientfönstren via
   deras processer och behåll redigeringsfönstret. Dog sessionen innan:
   logga det och gå vidare.
2. **Buggjakt, runda 1** (minst 3 timmar). Börja med att **återskapa
   fredagens rapport som spelare**: en gäst som bor i ett rum som inte är
   inneslutet. Bygg, riv och dra väggar med musen medan gäster är bokade,
   tills vägen hittas eller varje väg är prövad och loggad. Därefter listan
   per system, vakten och agenterna ovan. Rättningar går till main.
3. **WAITING §2.48, de fem rättningarna** (GDD §18), på main med specs.
4. **Expeditions** (GDD A.11.2, §18) på grenen `claude/expeditions` i en
   egen worktree:
   - Kör först `tools/balance_model.py` med lön 0,75 och logga siffrorna.
     Slår resorna ändå Wing är det ett fynd för WAITING; värdet ändras inte.
   - `Shared/Expeditions` (ren, med spec), fältet `expedition` i profilen och
     på `ResidentRecord`, `ResidentService` (bortrest som Hunter Camp),
     Perks, rebirth kallar hem gruppen, Travel ändrar inget.
   - Brädans panel med Best for this trip, Collect-popupen och en timer på
     Residents-knappen (UI.md först).
   - `ExpeditionBoard`: först i `MODELS.md`, sedan som blockout i Luau.
     Notisen köas via `NotifyService`; texten är hans.
   - Merga när grinden nedan är grön.
5. **Rumstyper där gästerna gör saker** (GDD §18 2026-10-26). Det här är
   nattens största arbete:
   1. **Designen först**, som nattutkast i GDD **A.13**:
      - **Typerna.** Hans lista är bio, livemusik (bar, restaurang,
        dansgolv), äta, dricka, biljard, pool inomhus och utomhus, gym och
        spa. Lägg gärna till fler; den är inte skriven i sten.
      - **Per typ:** nyckelmöbler, övriga möbler, taggar, vilka arter som
        vill ha den och storlek.
      - **Vad som delas:** dekor och vissa möbler mellan typerna, så att
        rum som liknar varandra kan inredas lika.
      - **Gästerna besöker och använder rummen**, synligt. Det är kärnan i
        hans önskan.
      - **Utomhuspoolen**, och var den står (tomten eller förgården).
      - §2.41:s rekommendationer.
      - Alla siffror PLACEHOLDER. Varje val han inte gjort skrivs med en
        rekommendation och samlas i en ny punkt i WAITING §2.
   2. **Koden** på grenen `claude/room-types` i en egen worktree:
      - `Pieces`-rader och regler med spec.
      - Gästernas besök med vägar och `Use`-punkter.
      - Varje ny möbel i `MODELS.md` först, sedan som blockout i Luau med
        kontraktets attachments, enligt CLAUDE.md.
      - Spelad i Studio. Merga när grinden är grön.
   3. **Modellerna i Blender** (skill `modelling`), en typ i taget:
      - Grå silhuetter bredvid en person, sedan byggskript, validering,
        Workbench-bilder och en blind granskning.
      - Hans utseende samlas för morgonen i WAITING §1.
      - Ingenting läggs för import innan han sagt ja.
      - Blender bara på below-normal med `-t 4`, och ingen EEVEE eller
        Cycles medan Studio kör.
6. **Utkast till ikon och thumbnails tagna i spelet** (`screen_capture`,
   Studio framme). Bygg på anteckningarna på `claude/store-art-87789a`
   (merga den inte). Gör tre av varje, låt dem granskas blint och lägg dem i
   `archive/screens/store-art-2026-10-26/`. Uppdatera WAITING §4.6.
7. **Buggjakt, runda 2**, över main med allt mergat: samma metod, med
   tyngd på det nya och hur det spelar ihop med det gamla.

**När listan är slut** går natten vidare tills usage-grinden stoppar den,
med mer av samma slag:

- fler rumstypers modeller,
- buggjakt per system,
- specs för regler som saknar en,
- varje panel på telefon och surfplatta,
- konsolen på varje plats.

Utkast (bara i GDD och WAITING, ingen kod): emotes och gruppbelöningen.

## Grinden för merge till main (hans lov, GDD §18 2026-10-26)

- Grenen är uppdaterad mot main.
- Alla specs passerar under Lune, och `data` i Studio.
- `stylua src/ && selene src/` är rena.
- Det nya är **spelat i Studio med riktig inmatning**.
- `git merge --no-ff`, och efter merge en kort buggjakt över main med
  vakten på, med ren konsol. Först därefter pushas den.
- Hittas ett fel efter en merge som inte går att rätta direkt: `git revert`
  av mergen, logga varför.
- `default.project.json` ändras inte i natt, eftersom en ändring kräver att
  han startar om Rojo.

## Regler

- **Usage** (`get_usage`) läses före varje steg och varje agent, och var 20:e
  minut i ett långt steg. På 5-timmarsfönstret: från 85 % startas inget
  nytt; vid 90 % committa och sov till reset. Weekly 90 %: skriv
  morgonavsnittet och stoppa. Sätt en watchdog-cron direkt, varje timme.
- **Commit och push:** commit per steg, bara egna filer, efter sökväg.
  Pusha main och grenarna.
- **Aldrig:** Publish, den publicerade databasen eller `rojo serve`.
  Playtests bara mot Studios DataStore, med `Test_`-profiler och
  `ServerStorage.StudioProfile` satt.
- **Studio:**
  - Ta låset `.locks/studio` först.
  - Main-utcheckningen (som Rojo serverar) står på main. Byt den till en gren
    bara för att spela den, och byt tillbaka före varje sömn.
  - Studio får ligga framme medan han sover. Tar någon tillbaka fokus sitter
    han vid datorn: arbeta utan fokus från det ögonblicket.
  - Ett playtest per steg.
- **Värden och utseenden:** inga värden ändras och inga utseenden bestäms;
  de går till WAITING med ett förslag. Fel i layout och struktur rättas.
- **Inga frågor och inga knappar.** Varje tur slutar med `ScheduleWakeup`.
- **Loggen** skrivs på svenska i `archive/NATTLOGG-2026-10-26.md`, med tiden
  från `date` och en buggtabell.
- **På morgonen:**
  - Loggens sista avsnitt: buggarna, vad som mergats, vad som väntar på
    honom (efter WAITING §).
  - Uppdatera memory `phase-status`, WAITING och LAUNCH-tabellen.
