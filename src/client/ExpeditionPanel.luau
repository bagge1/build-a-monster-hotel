--!strict
--[[
	The Expedition board (GDD A.11.2; UI.md "Expedition board"): pick a
	destination open in the run, a length and up to three residents from the
	Wing (**Best for this trip** fills the places), send them; while they are
	out, where they are and the time left; once back, **Collect**. Opened by
	the board's prompt in the Resident Wing (the server's Moment
	`ExpeditionBoard`). Also the Collect pop-up (`ExpeditionCollect`), shown
	once per trip as it comes back, and the timer on the HUD's Residents
	button.

	A copy for drawing: everything is the server's `expedition` and
	`collection` state sections; the clock counts down here between sends
	from the `left` it was sent. The client sends only `ExpeditionSend` and
	`ExpeditionCollect`, which the server checks again.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Expeditions = require(ReplicatedStorage.Shared.Expeditions)
local Format = require(ReplicatedStorage.Shared.Format)
local Locations = require(ReplicatedStorage.Shared.Locations)
local Mutations = require(ReplicatedStorage.Shared.Mutations)
local Net = require(ReplicatedStorage.Shared.Net)
local Species = require(ReplicatedStorage.Shared.Species)
local State = require(script.Parent.State)
local Ui = require(script.Parent.Ui)
local UiImages = require(script.Parent.UiImages)

local ExpeditionPanel = {}

local window: Frame
local body: Frame
local popup: Frame
local popupBody: Frame

local chosen: number? = nil -- the destination picked
local length: number? = nil -- the length picked, seconds
local slots: { string? } = {} -- the party being picked, resident ids
local sentAt = os.clock()
local leftLabel: TextLabel? = nil -- the trip's time left in the panel, redrawn each second
local shownFor: number? = nil -- the trip (its start) whose Collect pop-up was shown
local timer: TextLabel? = nil -- ExpeditionTimer on the HUD's Residents button
local drewTrip: boolean? = nil -- whether the last draw was the trip view; a switch scrolls back to the top

local function clear(f: Instance)
	for _, c in f:GetChildren() do
		if not c:IsA("UIListLayout") and not c:IsA("UIPadding") then
			c:Destroy()
		end
	end
end

local function clock(seconds: number): string
	local s = math.max(0, math.floor(seconds))
	if s >= 3600 then
		return string.format("%d:%02d:%02d", s // 3600, (s // 60) % 60, s % 60)
	end
	return string.format("%d:%02d", s // 60, s % 60)
end

local function lengthText(seconds: number): string
	return if seconds >= 3600 then `{seconds // 3600} h` else `{seconds // 60} min`
end

local function percent(p: number): string
	return `{math.floor(p * 100 + 0.5)}%`
end

local function nameOf(r: any): string
	local sp = Species.get(r.species)
	local mutation = Mutations.prefix(r.size, if r.mutation ~= "" then r.mutation else nil)
	return `{mutation}{if sp then sp.name else r.species}`
end

-- The time left on the trip now, counted down from the last send.
local function leftNow(trip: any): number
	return math.max(0, (trip.left or 0) - (os.clock() - sentAt))
end

-- The residents who may go (Expeditions.mayGo, from the collection section), by id.
local function home(): { any }
	local c = State.data.collection
	local out = {}
	for _, r in (if c then c.residents else {}) do
		if r.role == "" and not r.away and not r.trip then
			table.insert(out, r)
		end
	end
	table.sort(out, function(a, b)
		return a.id < b.id
	end)
	return out
end

-- The places as the server will read them: the picked ids still at home, in order.
local function party(): { string }
	local ok: { [string]: boolean } = {}
	for _, r in home() do
		ok[tostring(r.id)] = true
	end
	local out = {}
	for i = 1, Constants.Expeditions.Party do
		local id = slots[i]
		if id and ok[id] then
			table.insert(out, id)
		end
	end
	return out
end

local function residentById(id: string): any
	for _, r in home() do
		if tostring(r.id) == id then
			return r
		end
	end
	return nil
end

local draw: () -> ()

local function toggle(id: string)
	for i = 1, Constants.Expeditions.Party do
		if slots[i] == id then
			slots[i] = nil
			draw()
			return
		end
	end
	for i = 1, Constants.Expeditions.Party do
		if not slots[i] or not residentById(slots[i] :: string) then
			slots[i] = id
			draw()
			return
		end
	end
end

local function heading(parent: Instance, name: string, text: string, order: number)
	local l = Ui.label(parent, name, text, UDim2.new(1, -10, 0, 24), 18, Ui.Colour.Gold)
	l.LayoutOrder = order
end

local function row(parent: Instance, name: string, height: number, order: number): Frame
	local f = Ui.frame(parent, name, UDim2.new(1, -10, 0, height))
	f.BackgroundTransparency = 1
	f.LayoutOrder = order
	Ui.list(f, Enum.FillDirection.Horizontal, 8)
	return f
end

local function drawPlanner(ex: any)
	-- A destination open in the run, the one chosen if it still is.
	local open: { [number]: boolean } = {}
	for _, d in ex.destinations do
		open[d.id] = d.open
	end
	if not chosen or not open[chosen] then
		chosen = nil
		for _, d in ex.destinations do
			if d.open then
				chosen = d.id
				break
			end
		end
	end
	if not length then
		length = if ex.lengths[1] then ex.lengths[1].seconds else nil
	end

	heading(body, "DestinationsHead", "Where", 2)
	local dests = row(body, "Destinations", 120, 3)
	local share = UDim2.new(1 / math.max(1, #ex.destinations), -8, 1, 0)
	for i, d in ex.destinations do
		local loc = Locations.get(d.location)
		local card = Ui.button(dests, `Dest_{d.id}`, "", share, function()
			if d.open then
				chosen = d.id
				draw()
			end
		end, if d.open then loc.facade else Ui.Colour.Ink)
		card.LayoutOrder = i
		local image = UiImages[`Expedition_{d.id}`]
		if image and image ~= "" then
			local img = Instance.new("ImageLabel")
			img.Name = "Image"
			img.BackgroundTransparency = 1
			img.Image = image
			img.ImageTransparency = if d.open then 0.2 else 0.7
			img.Size = UDim2.fromScale(1, 1)
			img.ScaleType = Enum.ScaleType.Crop
			img.Parent = card
		end
		if d.id == chosen then
			Ui.stroke(card, Ui.Colour.Gold, 4)
		end
		local name = Ui.label(card, "Name", d.name, UDim2.new(1, -12, 0, 26), 18)
		name.Position = UDim2.fromOffset(6, 6)
		name.TextXAlignment = Enum.TextXAlignment.Center
		local likes = Ui.label(
			card,
			"Likes",
			if d.open
				then `likes {table.concat(d.likes, ", ")}`
				else `Open {Locations.get(d.location).name} first`,
			UDim2.new(1, -12, 1, -40),
			13,
			if d.open then Ui.Colour.Text else Ui.Colour.Muted
		)
		likes.Position = UDim2.fromOffset(6, 34)
		likes.TextXAlignment = Enum.TextXAlignment.Center
		likes.TextYAlignment = Enum.TextYAlignment.Top
	end

	heading(body, "LengthsHead", "How long", 4)
	local lens = row(body, "Lengths", 48, 5)
	for i, l in ex.lengths do
		local b = Ui.button(
			lens,
			`Len_{l.seconds}`,
			`{lengthText(l.seconds)} · {percent(l.chance)} find`,
			UDim2.new(1 / math.max(1, #ex.lengths), -8, 1, 0),
			function()
				length = l.seconds
				draw()
			end,
			if l.seconds == length then Ui.Colour.Pumpkin else Ui.Colour.PanelLight
		)
		b.LayoutOrder = i
	end

	heading(body, "PartyHead", `Who (up to {ex.party})`, 6)
	local places = row(body, "Party", 48, 7)
	for i = 1, ex.party do
		local r = slots[i] and residentById(slots[i] :: string)
		local b = Ui.button(
			places,
			`Slot_{i}`,
			if r then nameOf(r) else "Empty",
			UDim2.new(1 / ex.party, -8, 1, 0),
			function()
				slots[i] = nil
				draw()
			end,
			if r then Ui.Colour.Teal else Ui.Colour.Ink
		)
		b.LayoutOrder = i
	end

	local picked = party()
	local matches = 0
	for _, id in picked do
		local r = residentById(id)
		if r and chosen and Expeditions.matches(r.species, chosen) then
			matches += 1
		end
	end
	local actions = row(body, "Actions", 48, 8)
	local best = Ui.button(
		actions,
		"Best",
		"Best for this trip",
		UDim2.new(0.34, -8, 1, 0),
		function()
			if not chosen then
				return
			end
			local candidates = {}
			for _, r in home() do
				table.insert(
					candidates,
					{ id = tostring(r.id), species = r.species, level = r.level }
				)
			end
			local ids = Expeditions.best(candidates, chosen, ex.party)
			slots = {}
			for i, id in ids do
				slots[i] = id
			end
			draw()
		end,
		Ui.Colour.Moon
	)
	best.TextColor3 = Ui.Colour.Ink
	best.LayoutOrder = 1
	local ready = #picked > 0 and chosen ~= nil and length ~= nil and ex.ready
	local send = Ui.button(actions, "Send", `Send {#picked}`, UDim2.new(0.33, -8, 1, 0), function()
		if ready and chosen and length then
			Net.send("ExpeditionSend", chosen, length, table.concat(picked, ","))
			slots = {}
		end
	end, if ready then Ui.Colour.Good else Ui.Colour.Panel)
	send.LayoutOrder = 2
	local chance = Ui.label(
		actions,
		"Chance",
		if length
			then `Find {percent(Expeditions.findChance(length, matches))}{if matches > 0
				then ` (♥ {matches})`
				else ""}`
			else "",
		UDim2.new(0.33, -8, 1, 0),
		16,
		Ui.Colour.Muted
	)
	chance.LayoutOrder = 3

	heading(body, "ResidentsHead", "In the Wing", 9)
	local list = Ui.frame(body, "Residents", UDim2.new(1, -10, 0, 0))
	list.BackgroundTransparency = 1
	list.AutomaticSize = Enum.AutomaticSize.Y
	list.LayoutOrder = 10
	Ui.list(list, Enum.FillDirection.Vertical, 6)
	local inSlot: { [string]: boolean } = {}
	for _, id in picked do
		inSlot[id] = true
	end
	local residents = home()
	for i, r in residents do
		local id = tostring(r.id)
		local likes = chosen ~= nil and Expeditions.matches(r.species, chosen)
		local b = Ui.button(
			list,
			`Pick_{id}`,
			`{nameOf(r)}  ·  Lv {r.level}  ·  {Format.perSecond(r.pay)}{if likes
				then "  ·  ♥ likes it"
				else ""}`,
			UDim2.new(1, 0, 0, 48),
			function()
				toggle(id)
			end,
			if inSlot[id] then Ui.Colour.Teal else Ui.Colour.PanelLight
		)
		b.TextXAlignment = Enum.TextXAlignment.Left
		b.LayoutOrder = i
		local pad = Instance.new("UIPadding")
		pad.PaddingLeft = UDim.new(0, 12)
		pad.Parent = b
	end
	if #residents == 0 then
		local none = Ui.label(
			list,
			"Empty",
			"Nobody in the Wing can go: a resident on staff, in the Hunter Camp or away cannot.",
			UDim2.new(1, 0, 0, 48),
			16,
			Ui.Colour.Muted
		)
		none.LayoutOrder = 1
	end
end

local function drawTrip(ex: any)
	local trip = ex.trip
	local f = Ui.frame(body, "Trip", UDim2.new(1, -10, 0, 0), nil, Ui.Colour.PanelLight)
	f.AutomaticSize = Enum.AutomaticSize.Y
	f.LayoutOrder = 2
	Ui.corner(f, 12)
	Ui.padding(f, 10)
	Ui.list(f, Enum.FillDirection.Vertical, 6)
	local where = Ui.label(
		f,
		"Where",
		`{trip.name} · {lengthText(trip.length)}`,
		UDim2.new(1, 0, 0, 28),
		22,
		Ui.Colour.Gold
	)
	where.LayoutOrder = 1
	local names = {}
	for _, r in trip.party do
		table.insert(names, nameOf(r))
	end
	local who = Ui.label(f, "Who", table.concat(names, ", "), UDim2.new(1, 0, 0, 24), 18)
	who.LayoutOrder = 2
	local left = Ui.label(
		f,
		"Left",
		if trip.back then "Back!" else `{clock(leftNow(trip))} left`,
		UDim2.new(1, 0, 0, 26),
		20,
		if trip.back then Ui.Colour.Good else Ui.Colour.Text
	)
	left.LayoutOrder = 3
	leftLabel = if trip.back then nil else left
	local soFar = Ui.label(
		f,
		"SoFar",
		`Pays {Format.cash(trip.pay)} so far`,
		UDim2.new(1, 0, 0, 22),
		16,
		Ui.Colour.Muted
	)
	soFar.LayoutOrder = 4
	local chance = Ui.label(
		f,
		"Chance",
		if trip.guaranteed
			then "A find is sure on this trip"
			else `Find: {percent(trip.chance)} on Collect`,
		UDim2.new(1, 0, 0, 22),
		16,
		Ui.Colour.Moon
	)
	chance.LayoutOrder = 5
	if trip.back then
		local collect = Ui.button(f, "Collect", "Collect", UDim2.new(1, 0, 0, 48), function()
			Net.send("ExpeditionCollect")
		end, Ui.Colour.Good)
		collect.LayoutOrder = 6
	else
		local note = Ui.label(
			f,
			"Note",
			"They come home by themselves at the end and earn in the Wing again; Collect here for the pay and the find.",
			UDim2.new(1, 0, 0, 40),
			14,
			Ui.Colour.Muted
		)
		note.LayoutOrder = 6
	end
end

draw = function()
	clear(body)
	leftLabel = nil
	local ex = State.data.expedition
	if not ex or not State.data.collection then
		return
	end
	local head = Ui.label(
		body,
		"Head",
		`A trip pays {math.floor(ex.pay * 100 + 0.5)}% of what its residents would earn in the Wing meanwhile (the offline cap too), and a free roll for a find of its place.`,
		UDim2.new(1, -10, 0, 40),
		15,
		Ui.Colour.Muted
	)
	head.LayoutOrder = 1
	local onTrip = ex.trip ~= nil
	if onTrip ~= drewTrip then
		-- the planner is scrolled down to Send; the trip view is short and
		-- would otherwise open part-way down, its first line cut off
		(body :: any).CanvasPosition = Vector2.zero
		drewTrip = onTrip
	end
	if onTrip then
		drawTrip(ex)
	else
		drawPlanner(ex)
	end
end

function ExpeditionPanel.open()
	window.Visible = true
	draw()
end

local function showCollect(trip: any)
	clear(popupBody)
	local text = Ui.label(
		popupBody,
		"Text",
		`Your residents are back from the {trip.name}!\nPays {Format.cash(trip.pay)} · {if trip.guaranteed
			then "a find is sure"
			else `find {percent(trip.chance)}`}`,
		UDim2.new(1, 0, 0, 80),
		20,
		Ui.Colour.Gold
	)
	text.TextXAlignment = Enum.TextXAlignment.Center
	text.LayoutOrder = 1
	local buttons = Ui.frame(popupBody, "Buttons", UDim2.new(1, 0, 0, 48))
	buttons.BackgroundTransparency = 1
	buttons.LayoutOrder = 2
	Ui.list(buttons, Enum.FillDirection.Horizontal, 8)
	local collect = Ui.button(buttons, "Collect", "Collect", UDim2.new(0.5, -4, 1, 0), function()
		Net.send("ExpeditionCollect")
	end, Ui.Colour.Good)
	collect.LayoutOrder = 1
	local later = Ui.button(buttons, "Later", "Later", UDim2.new(0.5, -4, 1, 0), function()
		popup.Visible = false
	end, Ui.Colour.Panel)
	later.LayoutOrder = 2
	popup.Visible = true
end

-- The badge on the HUD's Residents button (UI.md): time left, "Back!", or hidden.
local function updateTimer()
	if not timer or not timer.Parent then
		local hud = Ui.screen("Hud", 1)
		local button = hud:FindFirstChild("ResidentsButton", true)
		if not button then
			return
		end
		local t = Ui.label(button, "ExpeditionTimer", "", UDim2.fromOffset(64, 18), 12)
		t.AnchorPoint = Vector2.new(1, 0)
		t.Position = UDim2.new(1, 6, 0, -8)
		t.BackgroundTransparency = 0
		t.BackgroundColor3 = Ui.Colour.Ink
		t.TextXAlignment = Enum.TextXAlignment.Center
		t.TextWrapped = false
		t.ZIndex = 5
		Ui.corner(t, 8)
		Ui.stroke(t, Ui.Colour.Teal, 1)
		timer = t
	end
	local ex = State.data.expedition
	local trip = ex and ex.trip
	local t = timer :: TextLabel
	t.Visible = trip ~= nil
	if trip then
		local back = trip.back or leftNow(trip) <= 0
		t.Text = if back then "Back!" else clock(leftNow(trip))
		t.TextColor3 = if back then Ui.Colour.Gold else Ui.Colour.Text
	end
end

function ExpeditionPanel.Init()
	local gui = Ui.screen("Expedition", 6)
	window, body =
		Ui.window(gui, "ExpeditionPanel", "Expedition board", UDim2.fromScale(0.66, 0.8), nil, true)
	Ui.list(body, Enum.FillDirection.Vertical, 6)
	popup, popupBody = Ui.window(gui, "ExpeditionCollect", "Back home!", UDim2.fromOffset(420, 220))
	Ui.list(popupBody, Enum.FillDirection.Vertical, 8)
end

function ExpeditionPanel.Start()
	State.changed:Connect(function()
		sentAt = os.clock()
		if window.Visible then
			draw()
		end
		local ex = State.data.expedition
		local trip = ex and ex.trip
		if trip and trip.back then
			if shownFor ~= trip.start then
				shownFor = trip.start
				showCollect(trip)
			elseif popup.Visible then
				showCollect(trip) -- the pay as last counted
			end
		elseif popup.Visible then
			popup.Visible = false
		end
		updateTimer()
	end)
	Net.listen("Moment", function(kind: string)
		if kind == "ExpeditionBoard" then
			ExpeditionPanel.open()
		elseif kind == "ExpeditionCollected" then
			popup.Visible = false
		end
	end)
	task.spawn(function()
		while true do
			task.wait(1)
			local ex = State.data.expedition
			local trip = ex and ex.trip
			if leftLabel and leftLabel.Parent and trip and not trip.back then
				leftLabel.Text = `{clock(leftNow(trip))} left`
			end
			updateTimer()
		end
	end)
end

return ExpeditionPanel
