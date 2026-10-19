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

## §3 Creator Hub och publicering

1. **Slå på Studio Access to API Services** (2026-10-19). Playtesten visar
   `DataStore state is NoAccess`: utan den sparas ingenting, ProfileStore kör
   en mock och varje spelare börjar om. I Studio: **File → Experience
   Settings → Security → Enable Studio Access to API Services**, sedan
   **Save**. Det är det enda som hindrar att save och load kan provas.
