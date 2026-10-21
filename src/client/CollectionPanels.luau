--!strict
--[[
	The collection's panels (GDD §4.6): **Residents** (who lives in the Wing,
	what each earns, a staff role for each, or a holiday for Moon Shards) and
	the **Monster Book** (a page per species with its mutations found, and the
	friendship meter toward its next move-in). Drawn from the `collection` and
	`book` state sections; every button sends an intent the server rechecks.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Format = require(ReplicatedStorage.Shared.Format)
local Locations = require(ReplicatedStorage.Shared.Locations)
local Mutations = require(ReplicatedStorage.Shared.Mutations)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Perks = require(ReplicatedStorage.Shared.Perks)
local Species = require(ReplicatedStorage.Shared.Species)
local State = require(script.Parent.State)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)

local CollectionPanels = {}

local ROLE_NAMES = {
	[""] = "Wing (earns)",
	FrontDesk = "Front Desk",
	Housekeeping = "Housekeeping",
	RoomService = "Room Service",
	Bellhop = "Bellhop",
	Entertainment = "Entertainment",
	Security = "Security",
}
local ROLE_ORDER =
	{ "", "FrontDesk", "Housekeeping", "RoomService", "Bellhop", "Entertainment", "Security" }

local residentsWindow: Frame
local residentsBody: Frame
local bookWindow: Frame
local bookBody: Frame
local bookLocation = 1

local function clear(f: Instance)
	for _, c in f:GetChildren() do
		if not c:IsA("UIListLayout") and not c:IsA("UIGridLayout") then
			c:Destroy()
		end
	end
end

local function rarityColour(rarity: string): Color3
	return ({
		Common = Ui.Colour.Text,
		Uncommon = Ui.Colour.Good,
		Rare = Ui.Colour.Moon,
		Epic = Color3.fromRGB(200, 120, 255),
		Legendary = Ui.Colour.Gold,
		Mythic = Ui.Colour.Pumpkin,
	} :: any)[rarity] or Ui.Colour.Text
end

-- A role button's text at 14, smaller where the button is narrow (a phone), never broken mid-word.
local function fitText(b: TextButton)
	b.TextScaled = true
	local cap = Instance.new("UITextSizeConstraint")
	cap.MaxTextSize = 14
	cap.Parent = b
end

local function drawResidents()
	clear(residentsBody)
	local c = State.data.collection
	if not c then
		return
	end
	local head = Ui.label(
		residentsBody,
		"Head",
		`Resident Wing {#c.residents}/{c.capacity}  ·  in the Wing a resident earns; on staff it works`,
		UDim2.new(1, 0, 0, 28),
		18,
		Ui.Colour.Muted
	)
	head.LayoutOrder = 0
	local list = Ui.scroll(residentsBody, "List", UDim2.new(1, 0, 1, -36))
	list.LayoutOrder = 1
	Ui.list(list, Enum.FillDirection.Vertical, 8)
	table.sort(c.residents, function(a, b)
		return a.id < b.id
	end)
	for i, r in c.residents do
		local sp = Species.get(r.species)
		if sp then
			local row =
				Ui.frame(list, `R_{r.id}`, UDim2.new(1, -10, 0, 140), nil, Ui.Colour.PanelLight)
			row.LayoutOrder = i
			Ui.corner(row, 12)
			local mutation = if r.mutation ~= "" then Mutations.ById[r.mutation].name .. " " else ""
			local best = ROLE_NAMES[sp.staff]
			local perk = Perks.BySpecies[sp.id]
			local perkText = if perk then `  ·  {perk.text}` else ""
			local name = Ui.label(
				row,
				"Name",
				`{mutation}{sp.name}  ·  {sp.rarity}  ·  best at {best}{perkText}{if r.away
					then "  ·  in the Hunter Camp!"
					else ""}`,
				UDim2.new(1, -20, 0, 26),
				18,
				rarityColour(sp.rarity)
			)
			name.Position = UDim2.fromOffset(10, 4)
			-- A.11.6: its level, the XP bar, and Level up once the bar is full.
			local lv = Ui.frame(row, "Level", UDim2.new(1, -20, 0, 40), UDim2.fromOffset(10, 32))
			lv.BackgroundTransparency = 1
			local atCap = r.level >= Constants.Residents.LevelCap
			local lvText = Ui.label(
				lv,
				"Value",
				if atCap then `Lv {r.level} (top)` else `Lv {r.level}`,
				UDim2.fromOffset(90, 40),
				18,
				Ui.Colour.Gold
			)
			lvText.Position = UDim2.fromOffset(0, 0)
			local track = Ui.frame(
				lv,
				"Track",
				UDim2.new(1, -310, 0, 14),
				UDim2.new(0, 96, 0.5, -7),
				Ui.Colour.Ink
			)
			Ui.corner(track, 7)
			local fill = Ui.frame(
				track,
				"Fill",
				UDim2.fromScale(
					if atCap or r.need <= 0 then 1 else math.clamp(r.xp / r.need, 0, 1),
					1
				),
				nil,
				if r.ready or atCap then Ui.Colour.Gold else Ui.Colour.Teal
			)
			Ui.corner(fill, 7)
			local xpText = Ui.label(
				lv,
				"Xp",
				if atCap then "" else `{r.xp}/{r.need} XP`,
				UDim2.fromOffset(90, 40),
				14,
				Ui.Colour.Muted
			)
			xpText.Position = UDim2.new(1, -210, 0, 0)
			local up = Ui.button(
				lv,
				"LevelUp",
				if atCap
					then "Top level"
					elseif r.ready then `Level up {Format.cash(r.price)}`
					else "Working…",
				UDim2.fromOffset(116, 40),
				function()
					if r.ready then
						Net.send("LevelUp", r.id)
					end
				end,
				if r.ready then Ui.Colour.Good else Ui.Colour.Panel
			)
			up.Position = UDim2.new(1, -116, 0, 0)
			fitText(up)
			local roles = Ui.frame(row, "Roles", UDim2.new(1, -20, 0, 56), UDim2.fromOffset(10, 78))
			roles.BackgroundTransparency = 1
			Ui.list(roles, Enum.FillDirection.Horizontal, 4)
			-- Seven roles and Holiday share the row's width, so a phone's narrow
			-- window keeps every button on it (TESTRUN, the phone).
			local share = UDim2.new(1 / (#ROLE_ORDER + 1), -4, 0, 48)
			for j, role in ROLE_ORDER do
				local label = if role == ""
					then `Wing {Format.perSecond(r.pay)}`
					else ROLE_NAMES[role]
				local b = Ui.button(
					roles,
					role ~= "" and role or "Wing",
					label,
					share,
					function()
						Net.send("Assign", r.id, role)
					end,
					if r.role == role
						then Ui.Colour.Pumpkin
						elseif role == sp.staff then Ui.Colour.Teal
						else Ui.Colour.Panel
				)
				b.LayoutOrder = j
				fitText(b)
			end
			local holiday = Ui.button(
				roles,
				"Holiday",
				`Holiday +{Constants.Rarity[sp.rarity].releaseShards}🌙`,
				share,
				function()
					Net.send("Release", r.id)
				end,
				Ui.Colour.Bad
			)
			holiday.LayoutOrder = 99
			fitText(holiday)
		end
	end
	if #c.residents == 0 then
		local hint = Ui.label(
			list,
			"Empty",
			"No residents yet. Every happy stay (satisfaction 80+) is +1 friendship; fill a species' meter in the Monster Book and it moves in.",
			UDim2.new(1, -10, 0, 60),
			18,
			Ui.Colour.Muted
		)
		hint.LayoutOrder = 1
	end
end

local function drawBook()
	clear(bookBody)
	local book = State.data.book
	local c = State.data.collection
	if not book or not c then
		return
	end
	local tabs = Ui.frame(bookBody, "Tabs", UDim2.new(1, 0, 0, 48))
	tabs.BackgroundTransparency = 1
	tabs.LayoutOrder = 0
	Ui.list(tabs, Enum.FillDirection.Horizontal, 6)
	for _, loc in Locations.List do
		if loc.playable then
			local b = Ui.button(
				tabs,
				`Loc_{loc.id}`,
				loc.name,
				UDim2.fromOffset(170, 44),
				function()
					bookLocation = loc.id
					drawBook()
				end,
				if loc.id == bookLocation then Ui.Colour.Pumpkin else Ui.Colour.PanelLight
			)
			b.LayoutOrder = loc.id
		end
	end
	local titles = Ui.label(
		bookBody,
		"Titles",
		if #book.titles > 0
			then "Titles: " .. table.concat(book.titles, ", ")
			else "Find every species of a family in one mutation for a title.",
		UDim2.new(1, 0, 0, 24),
		16,
		Ui.Colour.Muted
	)
	titles.LayoutOrder = 1
	local grid = Ui.scroll(bookBody, "Pages", UDim2.new(1, 0, 1, -84))
	grid.LayoutOrder = 2
	-- Room round the pages (his report, 2026-10-19: "cramped"): the grid is
	-- inset so the pages' outlines are not cut off at its edges, and the
	-- pages share the width, 4 across where there is room, 2 on a phone.
	local inset = Instance.new("UIPadding")
	inset.PaddingTop = UDim.new(0, 4)
	inset.PaddingBottom = UDim.new(0, 4)
	inset.PaddingLeft = UDim.new(0, 4)
	inset.PaddingRight = UDim.new(0, 14) -- the scroll bar's lane
	inset.Parent = grid
	local layout = Instance.new("UIGridLayout")
	layout.CellPadding = UDim2.fromOffset(12, 12)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = grid
	local function columns()
		local n = math.clamp(math.floor((grid.AbsoluteSize.X - 18) / 200), 2, 4)
		layout.CellSize = UDim2.new(1 / n, -12 * (n - 1) / n, 0, 142)
	end
	columns()
	grid:GetPropertyChangedSignal("AbsoluteSize"):Connect(columns)
	for i, sp in Species.ofLocation(bookLocation) do
		local found = book.pages[sp.id] or {}
		local page = Ui.frame(
			grid,
			sp.id,
			UDim2.new(),
			nil,
			if #found > 0 then Ui.Colour.PanelLight else Ui.Colour.Ink
		)
		page.LayoutOrder = i
		Ui.corner(page, 12)
		Ui.stroke(page, rarityColour(sp.rarity), 2)
		local title = Ui.label(
			page,
			"Name",
			if #found > 0 then sp.name else "???",
			UDim2.new(1, -20, 0, 22),
			20,
			rarityColour(sp.rarity)
		)
		title.Position = UDim2.fromOffset(10, 8)
		local room = Pieces.get(sp.room)
		local info = Ui.label(
			page,
			"Info",
			`{sp.rarity} · {room and room.name or ""}\nlikes {table.concat(sp.prefs, ", ")}`,
			UDim2.new(1, -20, 0, 40),
			14,
			Ui.Colour.Muted
		)
		info.Position = UDim2.fromOffset(10, 34)
		info.TextWrapped = true
		info.TextYAlignment = Enum.TextYAlignment.Top
		local muts = {}
		for _, m in Mutations.Rollable do
			table.insert(muts, if table.find(found, m.id) then m.name else "·")
		end
		local mutLine = Ui.label(
			page,
			"Mutations",
			table.concat(muts, " "),
			UDim2.new(1, -20, 0, 18),
			14,
			Ui.Colour.Gold
		)
		mutLine.Position = UDim2.fromOffset(10, 80)
		local f = c.friendship[sp.id] or { have = 0, need = 1 }
		local bar = Ui.frame(
			page,
			"Friendship",
			UDim2.new(1, -20, 0, 10),
			UDim2.fromOffset(10, 122),
			Ui.Colour.Ink
		)
		Ui.corner(bar, 6)
		local fill = Ui.frame(
			bar,
			"Fill",
			UDim2.fromScale(math.clamp(f.have / math.max(1, f.need), 0, 1), 1),
			nil,
			Ui.Colour.Pumpkin
		)
		Ui.corner(fill, 6)
		local fl =
			Ui.label(page, "FriendshipText", `♥ {f.have}/{f.need}`, UDim2.new(1, -20, 0, 16), 14)
		fl.Position = UDim2.fromOffset(10, 102)
		fl.TextXAlignment = Enum.TextXAlignment.Right
	end
end

function CollectionPanels.Init()
	local gui = Ui.screen("Panels", 6)
	residentsWindow, residentsBody =
		Ui.window(gui, "ResidentsPanel", "Residents", UDim2.fromScale(0.7, 0.7))
	Ui.list(residentsBody, Enum.FillDirection.Vertical, 6)
	bookWindow, bookBody = Ui.window(gui, "BookPanel", "Monster Book", UDim2.fromScale(0.7, 0.75))
	Ui.list(bookBody, Enum.FillDirection.Vertical, 6)
end

function CollectionPanels.Start()
	Hud.button("ResidentsButton", "🏠 Residents", "Left", function()
		residentsWindow.Visible = not residentsWindow.Visible
		bookWindow.Visible = false
		if residentsWindow.Visible then
			drawResidents()
		end
	end, 3)
	Hud.button("BookButton", "📖 Book", "Left", function()
		bookWindow.Visible = not bookWindow.Visible
		residentsWindow.Visible = false
		if bookWindow.Visible then
			drawBook()
		end
	end, 4)
	State.changed:Connect(function()
		if residentsWindow.Visible then
			drawResidents()
		end
		if bookWindow.Visible then
			drawBook()
		end
	end)
	Net.listen("Moment", function(kind: string, data: any)
		if kind == "MoveIn" then
			local sp = Species.get(data.species)
			Hud.toast(
				`♥ {sp and sp.name or data.species} moved into your Resident Wing!`,
				Ui.Colour.Pumpkin
			)
		end
	end)
end

function CollectionPanels.openBook()
	bookWindow.Visible = true
	drawBook()
end

return CollectionPanels
