--!strict
--[[
	The long game's panel (GDD §6.4, §6.5, his rulings 2026-10-20): **your
	hotels** (the chain: the one played, Travel to another, Open the next and
	what each earns while not played), **Rebirth** (5★ on every hotel, what
	it takes and gives) and the **Moon Tree** (each node's level, effect and
	price in shards). Drawn from the `chain` and `progression` state
	sections; the server checks every purchase and travel again.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Format = require(ReplicatedStorage.Shared.Format)
local MoonTree = require(ReplicatedStorage.Shared.MoonTree)
local Net = require(ReplicatedStorage.Shared.Net)
local State = require(script.Parent.State)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)

local ProgressionPanel = {}

local window: Frame
local body: Frame

local function clear()
	for _, c in body:GetChildren() do
		if not c:IsA("UIListLayout") then
			c:Destroy()
		end
	end
end

local function line(text: string, ok: boolean, order: number)
	local l = Ui.label(
		body,
		`Req_{order}`,
		(if ok then "✔ " else "• ") .. text,
		UDim2.new(1, 0, 0, 24),
		18,
		if ok then Ui.Colour.Good else Ui.Colour.Text
	)
	l.LayoutOrder = order
end

local function stars(r: number?): string
	return if r then `{math.floor(r * 10 + 0.5) / 10}★` else "—"
end

local function drawChain(order: number): number
	local c = State.data.chain
	if not c then
		return order
	end
	local title =
		Ui.label(body, "ChainTitle", "Your hotels", UDim2.new(1, 0, 0, 30), 24, Ui.Colour.Gold)
	title.LayoutOrder = order
	for _, h in c.hotels do
		order += 1
		local row = Ui.frame(body, `Hotel_{h.id}`, UDim2.new(1, 0, 0, 52))
		row.BackgroundTransparency = 1
		row.LayoutOrder = order
		local text = if h.here
			then `{h.name}  ·  {stars(h.rating)}  ·  you are here`
			elseif h.opened then `{h.name}  ·  {stars(h.rating)}  ·  earning {Format.cash(
				h.perMinute or 0
			)}/min`
			else `{h.name}  ·  not opened`
		local l = Ui.label(
			row,
			"Name",
			text,
			UDim2.new(1, -190, 1, 0),
			18,
			if h.here then Ui.Colour.Good else Ui.Colour.Text
		)
		l.TextXAlignment = Enum.TextXAlignment.Left
		local label, colour, active
		if h.here then
			label, colour, active = "Playing", Ui.Colour.Ink, false
		elseif h.opened then
			label, colour, active = "Travel", Ui.Colour.Teal, true
		elseif h.canOpen then
			label, colour, active = `Open {Format.cash(h.cost or 0)}`, Ui.Colour.Pumpkin, true
		else
			label, colour, active = "Open the one before", Ui.Colour.Ink, false
		end
		local b = Ui.button(row, "Go", label, UDim2.fromOffset(180, 46), function()
			if active then
				Net.send("Travel", h.id)
			end
		end, colour)
		b.Position = UDim2.new(1, -180, 0, 3)
	end
	order += 1
	local note = Ui.label(
		body,
		"ChainNote",
		`The hotels you are not playing earn {math.floor(c.share * 100 + 0.5)} % of what they earn while you play them, staffed by their own residents.`,
		UDim2.new(1, 0, 0, 40),
		15,
		Ui.Colour.Muted
	)
	note.LayoutOrder = order
	return order + 1
end

local function draw()
	clear()
	local p = State.data.progression
	if not p then
		return
	end
	local head = Ui.label(
		body,
		"Head",
		`{Format.number(p.shards)} Moon Shards  ·  rebirths: {p.rebirths}  ·  Prestige Stars: {p.prestige}`,
		UDim2.new(1, 0, 0, 28),
		20,
		Ui.Colour.Moon
	)
	head.LayoutOrder = 1
	local order = drawChain(2)
	local r = p.req
	local title =
		Ui.label(body, "RebirthTitle", "Rebirth", UDim2.new(1, 0, 0, 30), 24, Ui.Colour.Gold)
	title.LayoutOrder = order
	for _, h in r.ratings do
		order += 1
		line(`{h.name} at {r.need}★ (now {stars(h.rating)})`, h.ok, order)
	end
	order += 1
	local gain = if r.floor
		then `Gives the right to buy floor {r.floorCap}`
		elseif r.prestige then "Gives a Prestige Star (+income)"
		else ""
	local keeps = Ui.label(
		body,
		"Keeps",
		"Keeps residents, the Monster Book, cosmetics, Moon Shards, the Moon Tree and friendship. Resets cash and every hotel: you start again at Haunted Manor. "
			.. gain,
		UDim2.new(1, 0, 0, 44),
		15,
		Ui.Colour.Muted
	)
	keeps.LayoutOrder = order
	order += 1
	local move = Ui.button(
		body,
		"Move",
		if r.ready
			then `Rebirth now: +{r.shards} Moon Shards`
			else `Not yet (would give {r.shards} shards)`,
		UDim2.new(1, 0, 0, 48),
		function()
			if r.ready then
				Net.send("Rebirth")
			end
		end,
		if r.ready then Ui.Colour.Pumpkin else Ui.Colour.Ink
	)
	move.LayoutOrder = order
	order += 1
	local treeTitle = Ui.label(
		body,
		"TreeTitle",
		"Moon Tree: permanent, kept on every rebirth",
		UDim2.new(1, 0, 0, 30),
		22,
		Ui.Colour.Gold
	)
	treeTitle.LayoutOrder = order
	order += 1
	local grid = Ui.frame(body, "Tree", UDim2.new(1, 0, 0, 200))
	grid.BackgroundTransparency = 1
	grid.LayoutOrder = order
	local layout = Instance.new("UIGridLayout")
	layout.CellSize = UDim2.new(0.33, -6, 0, 92)
	layout.CellPadding = UDim2.fromOffset(6, 6)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = grid
	for i, n in p.nodes do
		local def = MoonTree.ById[n.id]
		if def then
			local text = `{def.name}  {n.level}/{def.levels}\n{def.text}\n`
				.. (if n.cost then `🌙 {n.cost}` else "Full")
			local b = Ui.button(grid, n.id, text, UDim2.new(), function()
				Net.send("MoonTree", n.id)
			end, if n.cost and p.shards >= n.cost then Ui.Colour.Teal else Ui.Colour.PanelLight)
			b.LayoutOrder = i
			b.TextSize = 15
		end
	end
end

function ProgressionPanel.Init()
	local gui = Ui.screen("Panels", 6)
	window, body = Ui.window(
		gui,
		"ProgressionPanel",
		"Hotels, Rebirth & Moon Tree",
		UDim2.fromScale(0.6, 0.78),
		nil,
		true
	)
	Ui.list(body, Enum.FillDirection.Vertical, 6)
end

function ProgressionPanel.Start()
	Hud.button("ProgressionButton", "🌙 Moon", "Right", function()
		window.Visible = not window.Visible
		if window.Visible then
			draw()
		end
	end, 1)
	-- The chain's Travel (§6.4): the same panel, opened at its hotels.
	Hud.button("TravelButton", "🧳 Travel", "Right", function()
		window.Visible = not window.Visible
		if window.Visible then
			draw()
		end
	end, 2)
	State.changed:Connect(function()
		if window.Visible then
			draw()
		end
	end)
end

return ProgressionPanel
