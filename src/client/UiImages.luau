--!strict
--[[
	Every uploaded image id, and nowhere else (UI.md, "Images"). Drawn by
	`tools/draw_ui.py` into `ui/` (see `ui/README.md`), uploaded by Claude
	through the Studio MCP on 2026-10-19. An empty id means "not uploaded",
	and whatever reads it must still work (it falls back to the button's text).

	The HUD icons and the panel slices are white on transparent with the glow
	in alpha: colour them with `ImageColor3`, no upload needed.
]]

return {
	Icon_Build = "rbxassetid://126391139360408",
	Icon_Rating = "rbxassetid://104472748316559",
	Icon_Residents = "rbxassetid://101781906656805",
	Icon_Book = "rbxassetid://94603129614582",
	Icon_Moon = "rbxassetid://93009981453391",
	Icon_Store = "rbxassetid://106168697668255",
	Icon_Daily = "rbxassetid://117618941065922",
	Icon_Bus = "rbxassetid://114506860049623",
	Icon_Pitch = "rbxassetid://107489349349870",
	Icon_Boo = "rbxassetid://85947915176102",
	Icon_Cash = "rbxassetid://130700380638041",
	Icon_Till = "rbxassetid://107870778712239",
	PanelFill = "rbxassetid://139329611460977",
	PanelFrame = "rbxassetid://70385359653016",
	Gloom = "rbxassetid://121928999888188",
} :: { [string]: string }
