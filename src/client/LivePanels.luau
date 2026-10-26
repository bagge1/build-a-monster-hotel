--!strict
--[[
	The live game's panels (GDD §8.2, §9, §10): the **Store** (passes and
	products with their Robux prices, the rewarded ad, active boosts) and
	**Daily** (the Featured Monster, three requests with claim and reroll, the
	login calendar, codes). Every button sends an intent the server rechecks;
	Roblox's own purchase prompt does the buying.

	A pass row has a **Gift** button (§10.1 point 4): it opens a row of the
	other players on the street, and picking one sends the intent; the server
	checks it and prompts the gift product.

	Also the notification opt-in (§9 "Return prompts"): offered once, after the
	first move-in, never at join.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local State = require(script.Parent.State)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)
local UiImages = require(script.Parent.UiImages)

local LivePanels = {}

local me = Players.LocalPlayer
local storeWindow: Frame
local storeBody: Frame
local dailyWindow: Frame
local dailyBody: Frame
local giftFor: string? = nil -- the pass key whose recipient is being picked
local codeRow: Frame

-- Leaves the kept list (`Ui.keptScroll`) and the code row standing: a redraw empties those itself.
local function clear(f: Instance)
	for _, c in f:GetChildren() do
		if not c:IsA("UIListLayout") and not c:IsA("ScrollingFrame") and c ~= codeRow then
			c:Destroy()
		end
	end
end

local function drawStore()
	clear(storeBody)
	local s = State.data.store
	if not s then
		return
	end
	local boosts = {}
	for name, left in s.boosts or {} do
		table.insert(
			boosts,
			`{if name == "Cash2x" then "2x Cash" else "2x Friendship"} {Format.duration(left)}`
		)
	end
	local head = Ui.label(
		storeBody,
		"Head",
		if #boosts > 0
			then "Active: " .. table.concat(boosts, "  ·  ")
			else "Convenience, capacity, cosmetics. Never winning.",
		UDim2.new(1, 0, 0, 24),
		16,
		Ui.Colour.Muted
	)
	head.LayoutOrder = 0
	local ad = Ui.button(
		storeBody,
		"Ad",
		"▶ Watch an ad: 2x Cash for 15 minutes (free)",
		UDim2.new(1, 0, 0, 44),
		function()
			Net.send("Ad")
		end,
		Ui.Colour.Teal
	)
	ad.LayoutOrder = 1
	local picking = 0
	if giftFor then
		local others = {}
		for _, p in Players:GetPlayers() do
			if p ~= me then
				table.insert(others, p)
			end
		end
		picking = 52
		local row = Ui.frame(storeBody, "GiftPicker", UDim2.new(1, 0, 0, 46), nil, Ui.Colour.Ink)
		row.LayoutOrder = 2
		Ui.corner(row, 10)
		Ui.list(row, Enum.FillDirection.Horizontal, 6)
		Ui.padding(row, 4)
		local passName = giftFor
		for _, e in s.entries do
			if e.key == giftFor then
				passName = e.name
			end
		end
		local pickHead = Ui.label(
			row,
			"Head",
			if #others > 0 then `Gift {passName} to:` else "Nobody else is on your street yet.",
			UDim2.fromOffset(if #others > 0 then 220 else 380, 38),
			15,
			Ui.Colour.Gold
		)
		pickHead.LayoutOrder = 0
		for i, p in others do
			local pick = Ui.button(
				row,
				`To_{p.UserId}`,
				p.DisplayName,
				UDim2.fromOffset(140, 38),
				function()
					local pass = giftFor
					giftFor = nil
					if pass then
						Net.send("Gift", pass, p.UserId)
					end
					drawStore()
				end,
				Ui.Colour.Teal
			)
			pick.LayoutOrder = i
		end
		local cancel = Ui.button(row, "Cancel", "Cancel", UDim2.fromOffset(90, 38), function()
			giftFor = nil
			drawStore()
		end, Ui.Colour.Panel)
		cancel.LayoutOrder = 100
	end
	local list = Ui.keptScroll(storeBody, "List", UDim2.new(1, 0, 1, -84 - picking))
	list.LayoutOrder = 3
	Ui.list(list, Enum.FillDirection.Vertical, 6)
	for i, e in s.entries do
		if e.key ~= "AdCash2x15" then
			local row = Ui.frame(list, e.key, UDim2.new(1, -10, 0, 58), nil, Ui.Colour.PanelLight)
			row.LayoutOrder = i
			Ui.corner(row, 10)
			local extra = if s.cash[e.key] then ` (now {s.cash[e.key]})` else ""
			-- Its icon (ui/pass, ui/product) cropped round as Roblox shows a pass; text-only without one.
			local icon = e.image and UiImages[e.image]
			local inset = 0
			if icon then
				inset = 54
				local img = Instance.new("ImageLabel")
				img.Name = "Icon"
				img.BackgroundTransparency = 1
				img.Image = icon
				img.Size = UDim2.fromOffset(50, 50)
				img.Position = UDim2.fromOffset(4, 4)
				img.Parent = row
				Ui.corner(img, 25)
			end
			local name = Ui.label(
				row,
				"Name",
				`{e.name}{if e.kind == "Pass" then "  ·  pass" else ""}`,
				UDim2.new(1, -150 - inset, 0, 24),
				18,
				Ui.Colour.Gold
			)
			name.Position = UDim2.fromOffset(10 + inset, 4)
			local text = Ui.label(
				row,
				"Text",
				e.text .. extra,
				UDim2.new(1, -150 - inset, 0, 26),
				14,
				Ui.Colour.Muted
			)
			text.Position = UDim2.fromOffset(10 + inset, 28)
			local label = if e.owned then "Owned" elseif not e.onSale then "Soon" else `R$ {e.price}`
			local b = Ui.button(
				row,
				"Buy",
				label,
				UDim2.fromOffset(120, 44),
				function()
					if not e.owned then
						Net.send("Buy", e.key)
					end
				end,
				if e.owned
					then Ui.Colour.Ink
					elseif e.onSale then Ui.Colour.Good
					else Ui.Colour.Panel
			)
			b.Position = UDim2.new(1, -128, 0, 7)
			if e.giftable then
				name.Size = UDim2.new(1, -250 - inset, 0, 24)
				text.Size = UDim2.new(1, -250 - inset, 0, 26)
				local g = Ui.button(row, "Gift", "🎁 Gift", UDim2.fromOffset(92, 44), function()
					giftFor = e.key
					drawStore()
				end, if e.giftOnSale then Ui.Colour.Pumpkin else Ui.Colour.Panel)
				g.Position = UDim2.new(1, -228, 0, 7)
			end
		end
	end
end

local function drawDaily()
	clear(dailyBody)
	local d = State.data.daily
	if not d then
		return
	end
	local featured = Ui.label(
		dailyBody,
		"Featured",
		`Featured monster today: {d.featured} (double friendship!)`,
		UDim2.new(1, 0, 0, 26),
		20,
		Ui.Colour.Pumpkin
	)
	featured.LayoutOrder = 0
	for i, r in d.list do
		local row =
			Ui.frame(dailyBody, `Req_{i}`, UDim2.new(1, 0, 0, 50), nil, Ui.Colour.PanelLight)
		row.LayoutOrder = i
		Ui.corner(row, 10)
		local t = Ui.label(
			row,
			"Text",
			`{r.text}   {r.have}/{r.target}`,
			UDim2.new(1, -250, 1, 0),
			17,
			if r.claimed then Ui.Colour.Muted else Ui.Colour.Text
		)
		t.Position = UDim2.fromOffset(10, 0)
		local done = r.have >= r.target
		local claim = Ui.button(
			row,
			"Claim",
			if r.claimed then "Done ✔" elseif done then "Claim" else "…",
			UDim2.fromOffset(110, 42),
			function()
				Net.send("Daily", "Claim", r.index)
			end,
			if done and not r.claimed then Ui.Colour.Good else Ui.Colour.Panel
		)
		claim.Position = UDim2.new(1, -236, 0, 4)
		local reroll = Ui.button(
			row,
			"Reroll",
			`Reroll ({d.rerolls})`,
			UDim2.fromOffset(116, 42),
			function()
				Net.send("Daily", "Reroll", r.index)
			end,
			Ui.Colour.Panel
		)
		reroll.Position = UDim2.new(1, -122, 0, 4)
		reroll.Visible = not r.claimed and d.rerolls > 0
	end
	local login = Ui.button(
		dailyBody,
		"Login",
		if d.loginClaimed
			then `Login calendar: day {d.loginDay}/7 claimed today`
			else `Claim login day {d.nextLoginDay}/7`,
		UDim2.new(1, 0, 0, 46),
		function()
			Net.send("Daily", "Login", 0)
		end,
		if d.loginClaimed then Ui.Colour.Ink else Ui.Colour.Pumpkin
	)
	login.LayoutOrder = 10
end

--[[ The code row, built once and left standing by every redraw (2026-10-26: rebuilt on each
	state send, it lost what was being typed and its focus, and the next keys went to the game,
	B opening build mode). ]]
local function buildCodes()
	codeRow = Ui.frame(dailyBody, "Codes", UDim2.new(1, 0, 0, 46))
	codeRow.BackgroundTransparency = 1
	codeRow.LayoutOrder = 11
	local box = Instance.new("TextBox")
	box.Name = "CodeBox"
	box.Size = UDim2.new(1, -130, 1, 0)
	box.BackgroundColor3 = Ui.Colour.Ink
	box.TextColor3 = Ui.Colour.Text
	box.PlaceholderText = "Enter a code"
	box.Font = Ui.Font
	box.TextSize = 18
	box.Text = ""
	box.ClearTextOnFocus = false
	box.Parent = codeRow
	Ui.corner(box, 10)
	local redeem = Ui.button(codeRow, "Redeem", "Redeem", UDim2.fromOffset(120, 46), function()
		if box.Text ~= "" then
			Net.send("Code", string.sub(box.Text, 1, 32))
			box.Text = ""
		end
	end, Ui.Colour.Teal)
	redeem.Position = UDim2.new(1, -120, 0, 0)
end

local function offerNotifications()
	-- §9: opt-in, used sparingly; asked after something the player cares about.
	task.delay(4, function()
		pcall(function()
			local service = game:GetService("ExperienceNotificationService") :: any
			if service:CanPromptOptInAsync() then
				service:PromptOptIn()
			end
		end)
	end)
end

function LivePanels.Init()
	local gui = Ui.screen("Panels", 6)
	storeWindow, storeBody = Ui.window(gui, "StorePanel", "Store", UDim2.fromScale(0.6, 0.78))
	Ui.list(storeBody, Enum.FillDirection.Vertical, 6)
	dailyWindow, dailyBody =
		Ui.window(gui, "DailyPanel", "Daily", UDim2.fromScale(0.6, 0.7), nil, true)
	Ui.list(dailyBody, Enum.FillDirection.Vertical, 6)
	buildCodes()
	-- The recipient being picked is forgotten with the Store (2026-10-26: it came back on reopening).
	storeWindow:GetPropertyChangedSignal("Visible"):Connect(function()
		if not storeWindow.Visible then
			giftFor = nil
		end
	end)
end

function LivePanels.Start()
	Hud.button("StoreButton", "🛍 Store", "Right", function()
		storeWindow.Visible = not storeWindow.Visible
		dailyWindow.Visible = false
		if storeWindow.Visible then
			drawStore()
		end
	end, 2)
	Hud.button("DailyButton", "📅 Daily", "Right", function()
		dailyWindow.Visible = not dailyWindow.Visible
		storeWindow.Visible = false
		if dailyWindow.Visible then
			drawDaily()
		end
	end, 3)
	local function playersChanged()
		if storeWindow.Visible and giftFor then
			drawStore()
		end
	end
	Players.PlayerAdded:Connect(playersChanged)
	Players.PlayerRemoving:Connect(function()
		task.defer(playersChanged)
	end)
	State.changed:Connect(function()
		if storeWindow.Visible then
			drawStore()
		end
		if dailyWindow.Visible then
			drawDaily()
		end
	end)
	local offered = false
	Net.listen("Moment", function(kind: string)
		if kind == "MoveIn" and not offered then
			offered = true
			offerNotifications()
		end
	end)
	local _ = me
end

return LivePanels
