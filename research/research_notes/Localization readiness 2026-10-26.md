# Localization readiness (2026-10-26, a read-only code survey)

The GDD names English, Spanish, Portuguese and Japanese (line 543) and puts
localization in M6 Polish. Nothing in `src/` uses `LocalizationService`,
`Translator` or `AutoLocalize` yet; every string is English, inline.

## Counts (from greps)

- Client: ~230 text setters in 20 files, ~660 distinct capitalised literals,
  182 string interpolations (BuildController alone: 74 setters).
- Server: 75 `Net.fire` Toast/Announce/Refused sites in 16 services (33+
  interpolated), plus ~92 refusal reasons returned by validators and sent as
  they are (e.g. `BuildService.luau:146`).
- Gloom: an English step table in `TutorialController.luau`, gamepad variants
  in `pad =` fields.
- Names in shared tables: 27 species, ~218 pieces, 16 cosmetics, 8 events.

## Why Roblox's auto-translate alone is not enough

1. Runtime-built text never matches a captured entry: `LivePanels.luau:228`
   (`{r.text} {r.have}/{r.target}`), `:263` (login calendar),
   `BusService.luau:376` (`The {sp.name} chose {owner.DisplayName}'s hotel!`,
   English word order and possessive), `BuildService.luau:494`
   (`refunded ${back}`), `BookService.luau:136`, `Format.duration` ("3h 05m").
2. Server text arrives finished over remotes (`Hud.luau:409-421`).
3. World text built on the server (signs in `HotelKit.luau:416-443`,
   `PlotService.luau:520/549`, `HotelService.luau:686-689`, leaderboards,
   `StreetService.luau:166` "BUS"): auto-capture there must be checked in Studio.
4. Text that cannot grow: 7 TextScaled and 9 AutomaticSize against ~230
   setters; HUD buttons 110×44 at 18 (`Hud.luau:225`), "Move" 110×46, "None"
   90×46, "Cancel" 90×38, window titles a fixed 40 px, fixed 50 px daily rows.
   Spanish and Portuguese run ~30 % longer.

## Fonts

Everything is `Enum.Font.FredokaOne` (`Ui.luau:38` and 11 server copies). It
covers Spanish and Portuguese accents (á é í ó ú ñ ã õ ç ¿ ¡). It has no
Japanese: Roblox's fallback would draw it in another face, and the fallback is
not certain (⟳ drew a blank, `BuildController.luau:2556`). Japanese must be seen
in Studio before it is promised.

## Recommended approach

A small shared `Text.t(key, args)` module: an English table of named format
strings (`Bus.Chose = "The {species} chose {owner}'s hotel!"`); the client
formats through `Translator:FormatByKey` (one translator per player) with the
English table as fallback; the server sends key and args instead of text
(`Net.fire(p, "Toast", "Bus.Chose", {species=..., owner=...}, "Rare")`),
refusal reasons become keys; a `tools/` script exports the table as the CSV the
cloud localization table imports; labels showing player names and numbers get
`AutoLocalize = false`; the fixed buttons and rows get AutomaticSize or a
`UITextSizeConstraint`, once in `Ui.luau` where possible.

Cost: ~20 client files, 16 server services, `Net`, `Format`, `Ui`, the shared
name tables, the new module and the export tool: ~1,000 call sites, a
multi-session job, best done before more UI is written or as one M6 pass. Specs
asserting English text keep passing with a key-based English fallback.

## August's decisions

WAITING §2.70.
