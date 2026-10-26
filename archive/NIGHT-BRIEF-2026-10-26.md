# Nattbrief — 2026-10-26

Augusts val i förberedelsesessionen 2026-10-26 (02:54–): **A, sedan B**;
Expeditions efter rekommendationen (GDD §18 2026-10-26); **bara 90 %-regeln**
för veckokvoten; han startar **Server and Clients** innan han lägger sig.
Läget vid start: weekly 0 %, 5-timmars 0 % (reset 06:50), main ren och
pushad, spelet inte publicerat, funktionsfrysning på main (`LAUNCH.md`).

## A. Lanseringen, på main (bara rättningar, specs, tester, dokument)

1. **Launch run del 1, två spelare** (`TESTRUN.md` "Launch run" del 1; skill
   `playtest` "Two players"). Han har startat Server and Clients. Kör det
   först, medan fönstren lever. Aldrig `start_stop_play` medan det körs,
   aldrig en spelande spelares profil från en annan datamodell, varje
   "leave"-halva sist. Stäng sedan Server- och klientfönstren via deras
   processer och behåll redigeringsfönstret. Dog sessionen innan du hann
   dit: logga det och gå vidare med en spelare.
   Klart = varje punkt i del 1 körd `[x]` eller märkt `[?]`/`[A]` med varför.
2. **Det som krävde riktig inmatning** (datorn var upptagen förra gången):
   byggläget och PieceMenu på iPhone 14 och iPad 10 i simulatorn med riktiga
   tryck; väggspöket (`showRun`) med riktig mus; sedan TESTRUN:s öppna
   `[ ]`/`[?]` som en person kan köra.
3. **Buggjakt genom att spela:** en ny spelare (ny `Test_`-profil) genom
   alla tre platserna; Travel och Rebirth med panelernas knappar; långa
   körningar med konsolen bevakad; ett fullt hotell. Varje fel rättas med en
   spec där regeln går att uttrycka, och ses igen i spelet.
4. **Utkast till ikon och thumbnails tagna i spelet** (Studio framme,
   `screen_capture`). Bygg på anteckningarna på grenen `claude/store-art-87789a`
   ("how to do better") men merga den inte. Gör tre av varje, granska dem
   blint (skill `blind-review`) och lägg dem i
   `archive/screens/store-art-2026-10-26/`. Uppdatera WAITING §4.6 så att han
   väljer på morgonen. Utseendet är hans.

## B. Efter lanseringen: Expeditions, på en egen gren som inte mergas

5. **Modellen först** (A.11.7): kör `tools/balance_model.py` med lön 0,75
   enligt staying's rules och offline-taket. Logga siffrorna. Om resorna
   ändå slår Wing är det ett fynd för WAITING; värdet ändras inte.
6. **Bygg A.11.2** på grenen `claude/expeditions` i en **egen worktree**, så
   att main-utcheckningen (som Rojo serverar) står kvar på main:
   - `Shared/Expeditions` (ren, med spec), fältet `expedition` i profilen och
     på `ResidentRecord`, `ResidentService` (bortrest som Hunter Camp),
     Perks, rebirth kallar hem gruppen, Travel ändrar inget.
   - Brädans panel med Best for this trip, Collect-popupen och en timer på
     Residents-knappen (UI.md först).
   - `ExpeditionBoard`: först i `MODELS.md` (`Prompt`-attachment), sedan som
     blockout i Luau enligt CLAUDE.md. Själva modellen och dess utseende går
     till WAITING.
   - Notisen köas via `NotifyService`. Texten är hans (WAITING §2.38).
   - Alla siffror PLACEHOLDER i `Constants`, utom hans beslut i GDD §18.
   - Ingen ändring i `default.project.json`, eftersom den kräver att han
     startar om Rojo.
7. **Spela Expeditions i Studio:** när A är committat och pushat, byt
   main-utcheckningen till grenen, spela med en `Test_`-profil (en kort och
   en lång resa, rebirth och Travel mitt i en resa, offline-taket), och byt
   sedan tillbaka till main. Lämna aldrig utcheckningen på grenen över en
   sömn eller till morgonen. Grenen pushas, mergas aldrig.

## När listan är slut

Natten slutar bara vid usage-grinden. Gör mer av samma slag, i den här
ordningen:

- buggjakt genom att spela,
- specs för regler som saknar en,
- varje panel på telefon och surfplatta,
- konsolen på varje plats,
- serverns kostnad med ett fullt hotell.

Därefter, på egna grenar som inte mergas: efter-lanserings-arbete vars
design redan är beslutad. Design som inte är beslutad skrivs som utkast i GDD
Appendix A och WAITING, och byggs inte.

## Regler

- Usage före varje steg (`get_usage`). Från 85 % på 5-timmarsfönstret
  startas inget nytt; vid 90 %: commit, sedan sov till reset. Vid weekly
  90 %: skriv morgonavsnittet och stoppa. Watchdog-cron varje timme.
- Commit per steg, bara egna filer och efter sökväg. Pusha main och grenen.
  **Aldrig merge, aldrig Publish, aldrig den publicerade databasen**: bara
  Studios, med `Test_`-profiler och `ServerStorage.StudioProfile` satt.
  Aldrig `rojo serve`.
- Studio-låset `.locks/studio`. Studio får ligga framme medan han sover.
  Tar någon tillbaka fokus sitter han vid datorn: från det ögonblicket
  arbetar du utan fokus. Ett playtest per steg.
- Blender bara på below-normal med `-t 4`, och inga tunga renderingar medan
  Studio kör.
- Inga värden ändras och inga utseenden bestäms (de går till WAITING med
  ett förslag). Fel i layout och struktur rättas.
- Inga frågor och inga knappar. Varje tur slutar med `ScheduleWakeup`.
- Loggen skrivs på svenska i `archive/NATTLOGG-2026-10-26.md`, med tiden
  tagen från `date`.
- Morgonen: loggens sista avsnitt, memory `phase-status`, WAITING, LAUNCH-
  tabellen.
