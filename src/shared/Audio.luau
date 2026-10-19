--!strict
--[[
	Every sound id in the game, in one place (GDD §12 "Audio": playful
	harpsichord, a "ding" on cash, a fanfare for rare check-ins).

	LOOKED UP, NEVER RECALLED (DEVNOTES.md, "Audio"): each id was found in the
	Creator Store through the Studio MCP on 2026-10-19 and checked to load in
	a playtest (`IsLoaded`, `TimeLength` in the comment). The music and the
	fanfare are APM Music's licensed library tracks; the short effects are
	free uploads. Every pick is a night draft for August's ear (WAITING.md §1).
]]

local Audio = {}

Audio.Music = "rbxassetid://9042223208" -- APM "Chaconne pour les Ombres", harpsichord and strings, 61.5 s loop
Audio.Cash = "rbxassetid://5995351511" -- "coin ding (uncopyrighted)", self-made by its uploader, 0.6 s
Audio.Fanfare = "rbxassetid://1844584698" -- APM "Winner", 4.6 s: rare check-ins and move-ins
Audio.BusHorn = "rbxassetid://125488657993933" -- a bus horn, 1.8 s
Audio.Bell = "rbxassetid://115073483242365" -- a bell, 2.5 s: the front desk

return Audio
