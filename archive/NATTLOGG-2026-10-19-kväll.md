# Nattlogg — 2026-10-19, kväll

## Sammanfattning (uppdateras varje varv)

- **Klart:** staff ihopslagen i main och provkörd (`9ff2588`).
- **Provat:** staff-specen 7/7; Room Service och Housekeeping går till rummet
  och tillbaka med "✓"; omplacering mitt i ärendet; två på en gång. Rebirth
  med panelens knapp; Frostfangs rum i en tomt; alla paneler på telefon
  (två rättade: Residents-raden och Ping-menyn). Byggt ur GDD:n: CI-lint
  (§13.1), VIP Lobbys gyllene namnskylt (§10.2), Bellhop kortar
  incheckningen (§4.6).
- **Pågår:** väntar på street och free-building (arbetar fortfarande).
- **Väntar på August:** WAITING §2.22 (VIP-märkets utseende), §2.23
  (Bellhops tal för incheckningen).

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
- **19:58** Staffs TESTRUN i playtest: Room Service går post → hall → dörr
  (vänd mot dörren, knackar) → post på klienten; "✓ Room Service" stiger vid
  dörren. Housekeeping städar två rum i tur och ordning med "✓". Gästen
  checkar ut medan residenten går → vänder ("Back"), inget "✓". Omplacerad
  till Front Desk mitt i ärendet → står vid nya posten direkt. Två Room
  Service (Slot 1, 2) tar rum 1 och 3 samtidigt; Mummyn (effektivitet 0,6)
  klar efter ~20 s = 12 ÷ 0,6. Ingen `[residents] tick failed`. Våning 3
  provas när free-building är inne; två spelare är Augusts. Commit `9ff2588`.
- **20:00** Street och free-building arbetar fortfarande. Beslut: a (ny
  spelare), d (mätning) och f (prestanda) görs efter sammanslagningarna,
  eftersom free-building skriver om byggandet och street lägger till skog och
  bussar; till dess b och c.
- **20:03** b: rebirth med panelens knapp (testprofil `Test_Eve1019a`; 4★
  räknat av spelet, men med indata satta av ett hjälpskript i Studio: 27
  sviter satta till nivå 3 och 30 femstjärniga recensioner, plus fem
  residenter i tjänst och fyra riktiga incheckningar): Moon-knappen, sedan **Move now: +24 Moon
  Shards** → Frostfang Lodge, 24 shards, 1 flytt, $100, inga rum, alla 6
  residenter kvar. Frostfangs rum i tomten: `fill IglooRoom` 43 rum på 3
  våningar, 812 meshdelar alla från Frostfangs kit, inga tomma; Snowball
  Sprite och Ice Imp gick in i Igloo-rum på våning 2 och 3. Vägen till
  våning 3 tog ungefär 70 s (till mätningen i d). Testprofilen avstängd igen.
- **20:07** c: telefonen (iPhone 14 liggande, 749×388), alla nio paneler
  öppnade en i taget. Sju ryms. Residents: rollknapparna Security och Holiday
  gick utanför panelens högerkant (x 692–910 av 34–714). Ping-menyn: sex rader
  (316 px) gick under skärmens nederkant. Rättat i `CollectionPanels` (de åtta
  knapparna delar radens bredd, texten krymper till högst 14 och bryts aldrig
  mitt i ord) och `Pings` (två kolumner på kort skärm, nederkant 280 av 388).
  Sett i spelet efter synk, skärmdump `archive/screens/2026-10-19_phone_residents.jpg`.
  Byggläget lämnas till efter free-building. Obs: klick via instance-sökväg i
  telefonemuleringen träffade två knappar på en gång (vänster och höger
  kolumn); MCP:ns fel, inte spelets. Obs 2: staff-testet 19:55 körde på
  Augusts egen profil (testprofilen var av): en Mummy (resident 2) lades
  till där och står på Room Service. Resten av kvällen kör på testprofiler.
- **20:10** g: en bakgrundsagent gick igenom GDD:n. Åtta luckor; de som
  krockar med street eller free-building väntar (tutorialens Commons på
  första bussen §11, Service/Cleanliness av personaltäckning §5.3, pingen
  som nämner rummet §7, gamepad/Input Action System §11). Hunter Camps
  mini-uppdrag (§8.1) är inte beskrivet: hans.
- **20:11** CI-lint (§13.1): `.github/workflows/lint.yml` (StyLua 2.5.2 och
  Selene 0.31.0 som i rokit.toml). Pushad `f7609e9`; körningen stod i kö,
  resultatet kollas nästa varv.
- **20:13** VIP Lobby (§10.2): gyllene namnskylt "VIP  <namn>" över huvudet
  och spelarens `VIP`-attribut, i takt med passet var 2 s (`SocialService`).
  Provat (testprofil `Test_Vip1019`): ingen skylt utan passet, skylt inom
  2 s med `pass VIPLobby`, tillbaka 3,6 s efter respawn, Roblox eget namn
  dolt, inga fel. BillboardGui syns inte i skärmdumpar, så utseendet är inte
  sett: WAITING §2.22.
- **20:14** CI-lint föll på Selene: Selene avslutar med kod 1 även på
  varningar, och main har varningen `BusRenderer` skuggar `bus`. Street-grenen
  tar bort den (selene 0 varningar där), så CI blir grön när street är inne.
  Inte rättad på main för att inte krocka med street.
- **20:16** g: Bellhop kortar incheckningen (§4.6 "check-in time"):
  `Staff.deskDelay` delar Front Desks väntan med 1 + 0,25 × bästa Bellhops
  effektivitet; talet PLACEHOLDER i GDD A.5 och WAITING §2.23. Ny regel i
  staff-specen (en Bellhop gör aldrig incheckningen långsammare): **8/8** i
  Studio. Uppmätt (testprofil `Test_Bell1019`, Skeleton på Front Desk): utan
  Bellhop 6,4 och 6,3 s från kön till incheckad; med Mummyn som Bellhop
  6,2 / 5,1 / 4,8 / 5,2 / 6,2 / 5,7 s (snitt 5,5; väntat 4,8 + upp till 1 s
  för sekundtakten; de långsamma stod bakom andra gäster i kön).
