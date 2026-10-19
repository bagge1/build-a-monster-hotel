# Nattlogg — 2026-10-19, kväll

## Sammanfattning (uppdateras varje varv)

- **Klart:** staff ihopslagen i main (fast-forward).
- **Provat:** staff-specen 7/7 i Studio; Room Service-ärendet på servern
  (ut, vid dörren, klart efter 12 s, tillbaka).
- **Pågår:** staffs TESTRUN-punkter i playtest.
- **Väntar på August:** —

Obevakad session (`/loop`, självstyrd) medan August är borta (från ca 20:00 i
2–3 timmar). Hans brief (andra versionen, 19:5x, ersätter den första):

1. **Slå ihop sessionernas grenar** i main, en i taget, i ordningen staff,
   street, free-building: granska diffen, stylua, selene, rojo build, specs,
   kontrollera synken i Studio, kör grenens TESTRUN-punkter i en playtest,
   rätta det som är fel, committa och pusha.
2. **Annars första sak som inte är gjord:**
   a. Spela som en ny spelare från början och rätta det som går sönder.
   b. De öppna TESTRUN-punkterna (piece-menyn med klick, rebirth med
      panelens knapp, Frostfangs rum i en tomt, gåva mellan två spelare).
   c. Telefonen: alla paneler i mobilemulering.
   d. Mät vistelser och inkomst med `tools/balance_model.py`; inga värden
      ändras, fynd till WAITING §2.
   e. Blind granskning av nya modeller och hotellet i spelet.
   f. Prestanda: delar och ljus per tomt och gata mot mobilbudgeten.
   g. Det som är bestämt i GDD:n men inte byggt (själv eller ny session).
   h. Saknas ett tal: utkast märkt PLACEHOLDER i GDD Appendix A, bygg,
      frågan i WAITING §2.
   Börja om från a när listan är slut.

## Regler för kvällen

- Kvoten före varje steg: veckan ≥ 90 % → avsluta. 5-timmarsfönstret ≥ 90 % →
  gör klart steget, committa, sov tills det nollställs, fortsätt sedan.
- Svara på sessionernas frågor med det val som går att ångra; skriv antagandet
  här. Hans val (utseende, värden, ny design) → WAITING §2.
- Ändras `default.project.json`: WAITING §0 (rojo serve startas om), ingen
  playtest på gammal synk. Modeller att importera: staga, WAITING §0.
- Aldrig ett värde han satt. Aldrig rojo serve. Inga tunga renderingar.
- Får starta nya sessioner (egna worktrees) för det som redan är bestämt i
  GDD:n men inte byggt, och slå ihop dem på samma sätt.
- När bara det som kräver August återstår: sammanfattningen färdig, peka på
  WAITING, committa, sov en timme i taget.

## Logg

- **19:51** Start. Kvot: 5 timmar 18 %, veckan 22 %. Läget: staff klar
  (3 commits, ingen körning), street och free-building arbetar fortfarande
  (ocommittat i sina worktrees). main ren på `d412374`.
- **19:52** staff granskad (ResidentService-ärendena, Staff.luau, GDD §4.6 och
  A.5 PLACEHOLDER, WAITING 2.17) och fast-forwardad i main (`8ce00bb`).
  stylua ren, selene 0 fel (1 varning som redan fanns på main:
  `BusRenderer` skuggar `bus`), rojo build OK. `default.project.json`
  oförändrad.
- **19:55** Synken i Studio: alla 66 skript lika många byte som på disk.
  Playtest: staff-specen **7 godkända, 0 fel**. Room Service på servern:
  request → Out 1,0 s → Work 2,1 s → Done 13,3 s → tillbaka 14,3 s.
