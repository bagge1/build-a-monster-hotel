--!strict
--[[
	The long game's panel (GDD §6.4, §6.5): **Move** (rebirth: what it asks,
	what is met, the Moon Shards it would give, where it goes) and the **Moon
	Tree** (each node's level, effect and price in shards). Drawn from the
	`progression` state section; the server checks every purchase again.
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

local function draw()
	clear()
	local p = State.data.progression
	if not p then
		return
	end
	local head = Ui.label(
		body,
		"Head",
		`{p.locationName}  ·  {Format.number(p.shards)} Moon Shards  ·  moves so far: {p.rebirths}`,
		UDim2.new(1, 0, 0, 28),
		20,
		Ui.Colour.Moon
	)
	head.LayoutOrder = 1
	local r = p.req
	local title =
		Ui.label(body, "MoveTitle", `Move to {r.next}`, UDim2.new(1, 0, 0, 30), 24, Ui.Colour.Gold)
	title.LayoutOrder = 2
	line("Hotel rating 4★", r.rating, 3)
	line(r.cashText, r.cash, 4)
	line(`A {r.residentName} resident`, r.resident, 5)
	local keeps = Ui.label(
		body,
		"Keeps",
		"Keeps residents, the Monster Book, Moon Shards, the Moon Tree, friendship and unlocked room types. Resets cash, rooms and floors.",
		UDim2.new(1, 0, 0, 44),
		15,
		Ui.Colour.Muted
	)
	keeps.LayoutOrder = 6
	local move = Ui.button(
		body,
		"Move",
		if r.ready
			then `Move now: +{r.shards} Moon Shards`
			else `Not yet (would give {r.shards} shards)`,
		UDim2.new(1, 0, 0, 48),
		function()
			if r.ready then
				Net.send("Rebirth")
			end
		end,
		if r.ready then Ui.Colour.Pumpkin else Ui.Colour.Ink
	)
	move.LayoutOrder = 7
	local treeTitle = Ui.label(
		body,
		"TreeTitle",
		"Moon Tree: permanent, kept on every move",
		UDim2.new(1, 0, 0, 30),
		22,
		Ui.Colour.Gold
	)
	treeTitle.LayoutOrder = 8
	local grid = Ui.frame(body, "Tree", UDim2.new(1, 0, 0, 200))
	grid.BackgroundTransparency = 1
	grid.LayoutOrder = 9
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
	local gui = Ui.screen("Panels", 4)
	window, body =
		Ui.window(gui, "ProgressionPanel", "Move & Moon Tree", UDim2.fromScale(0.6, 0.78))
	Ui.list(body, Enum.FillDirection.Vertical, 6)
end

function ProgressionPanel.Start()
	Hud.button("ProgressionButton", "🌙 Moon", "Right", function()
		window.Visible = not window.Visible
		if window.Visible then
			draw()
		end
	end, 1)
	State.changed:Connect(function()
		if window.Visible then
			draw()
		end
	end)
end

return ProgressionPanel
