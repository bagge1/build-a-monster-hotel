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
	-- Pass and product icons: the images Roblox made of ui/pass and ui/product
	-- when each was created in Creator Hub (2026-10-20); Store.luau names them.
	Pass_AutoCollectTill = "rbxassetid://137527705254534",
	Pass_NightManager = "rbxassetid://94076929740994",
	Pass_ResidentWingPlus = "rbxassetid://128320289487849",
	Pass_ExtraFloor = "rbxassetid://73851985276898",
	Pass_VipLobby = "rbxassetid://77851868856398",
	Product_StarterPack = "rbxassetid://93218272874994",
	Product_CallTheBus = "rbxassetid://89213177717307",
	Product_2xCash15m = "rbxassetid://108212009503000",
	Product_2xCash1h = "rbxassetid://78466280891832",
	Product_2xFriendship = "rbxassetid://92610015369003",
	Product_CashSmall = "rbxassetid://127253134563872",
	Product_CashMedium = "rbxassetid://93077811004758",
	Product_CashLarge = "rbxassetid://90656238311183",
	Product_AdCash2x15 = "rbxassetid://77985380174613",
	Product_Gift_AutoCollectTill = "rbxassetid://73971807703317",
	Product_Gift_NightManager = "rbxassetid://111824126868039",
	Product_Gift_ResidentWingPlus = "rbxassetid://110635326853317",
	Product_Gift_ExtraFloor = "rbxassetid://77760336089405",
	Product_Gift_VipLobby = "rbxassetid://108427241218399",
} :: { [string]: string }
