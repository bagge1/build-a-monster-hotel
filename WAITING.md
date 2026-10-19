# Väntar på August

Allt som väntar på dig, på ett ställe. Det du har svarat på stryks
(`~~punkten~~`) med var svaret hamnade. Spelets egna engelska namn behålls.

Håll listan kort: bara det du kan titta på eller bestämma den här veckan.
Designfrågor som inte brådskar står i `docs/GDD.md` (§17) tills de gör det.

## §0 I Studio: import och Connect

<!-- En import: vilken mapp i blender/_import/ du väljer i dialogen.
Connect: knappen under fliken Plugins i Studio. -->

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

## §3 Creator Hub och publicering

1. **Slå på Studio Access to API Services** (2026-10-19). Playtesten visar
   `DataStore state is NoAccess`: utan den sparas ingenting, ProfileStore kör
   en mock och varje spelare börjar om. I Studio: **File → Experience
   Settings → Security → Enable Studio Access to API Services**, sedan
   **Save**. Det är det enda som hindrar att save och load kan provas.
