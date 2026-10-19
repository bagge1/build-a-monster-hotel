--!strict
--[[
	Build mode (GDD §5, §13.2 "Building": the client draws the ghost, snaps
	and rotates; the server validates). The client sends only
	`{item, floor, cell, rotation}`; `Grid.canPlace` runs here too, on the
	state's copy of the layout, so the ghost turns red before the server
	would refuse.

	One thumb (§11): tap a piece card, tap the grid to put the ghost there,
	press Place. With a mouse, the ghost follows the cursor and a click
	places; R rotates. Tapping a built piece (no card chosen) opens its menu:
	upgrade, decorate, move, sell.

	The camera looks down on the plot while building, and floors above the
	one being built on are hidden locally (`LocalTransparencyModifier`).
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Format = require(ReplicatedStorage.Shared.Format)
local Grid = require(ReplicatedStorage.Shared.Grid)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local State = require(script.Parent.State)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)

local G = Constants.Grid

local BuildController = {}

local me = Players.LocalPlayer
local camera = workspace.CurrentCamera

local active = false
local floor = 1
local rotation = 0
local selected: string? = nil -- a piece id to place
local moving: number? = nil -- a built piece being moved
local cell: Grid.Cell? = nil
local yaw = 0 -- which way round the camera looks, radians (0: from the street)
local zoom = 1 -- the camera's distance, 1 = the whole plot in view

local gui: ScreenGui
local strip: Frame
local cards: ScrollingFrame
local info: TextLabel
local tools: Frame
local floorLabel: TextLabel
local placeButton: TextButton
local menu: Frame
local menuBody: Frame
local tab = "Room"
-- What the strip says while nothing is being placed: that a placed piece is
-- tapped to change it (his report, 2026-10-19: no way to remove or replace a room).
local HINT = "Choose a piece to build, or tap a room to upgrade, move or sell it"
local hover: Highlight? = nil
local stopPlacing: () -> ()
local rightDownAt: Vector2? = nil
local redrawCards: () -> ()
local ghost: Model? = nil
local hidden: { [BasePart]: boolean } = {}

local function plotModel(): Model?
	local index = me:GetAttribute("Plot")
	local plots = workspace:FindFirstChild("Plots")
	local m = plots and plots:FindFirstChild(`Plot_{index}`)
	return if m and m:IsA("Model") then m else nil
end

local function plotFrame(): CFrame?
	local m = plotModel()
	local f = m and m:GetAttribute("Origin")
	return if typeof(f) == "CFrame" then f else nil
end

local function build(): any
	return State.data.build
		or { layout = {}, floors = 1, buildable = {}, costs = {}, maxFloors = 3, location = 1 }
end

local function layoutPlaced(skipId: number?): ({ Grid.Placed }, Grid.Placed?)
	local out, skip = {}, nil
	for _, rec in build().layout do
		local p = Pieces.get(rec.item)
		if p then
			local placed = {
				item = rec.item,
				floor = rec.floor,
				x = rec.x,
				z = rec.z,
				r = rec.r,
				w = p.w,
				d = p.d,
			}
			table.insert(out, placed)
			if rec.id == skipId then
				skip = placed
			end
		end
	end
	return out, skip
end

local function record(id: number): any
	for _, rec in build().layout do
		if rec.id == id then
			return rec
		end
	end
	return nil
end

-- ===== The camera and hidden floors =====

local function updateCamera()
	local frame = plotFrame()
	if not frame or not active then
		return
	end
	local size = G.Cells * G.CellSize
	local centre = frame:PointToWorldSpace(Vector3.new(size / 2, Grid.floorY(floor), size / 2))
	local back = frame:VectorToWorldSpace(Vector3.new(math.sin(yaw), 0, -math.cos(yaw)))
	camera.CameraType = Enum.CameraType.Scriptable
	-- At zoom 1 the whole plot is in view: the distance grows with the plot
	-- (50 back, 62 up for 72 studs). Zooming keeps the same downward angle.
	camera.CFrame = CFrame.lookAt(
		centre + back * (size * 0.7 * zoom) + Vector3.new(0, size * 0.86 * zoom, 0),
		centre
	)
end

local function setHidden()
	for p in hidden do
		p.LocalTransparencyModifier = 0
	end
	table.clear(hidden)
	if not active then
		return
	end
	local m = plotModel()
	if not m then
		return
	end
	-- The facade's parts carry their floor in their names (`Left_2_Post`).
	local facade = m:FindFirstChild("Facade")
	for _, p in (if facade then facade:GetChildren() else {}) do
		local f = tonumber(string.match(p.Name, "^%a+_(%d+)_"))
		if p:IsA("BasePart") and f and f > floor then
			p.LocalTransparencyModifier = 1
			hidden[p] = true
		end
	end
	for _, child in m:GetDescendants() do
		if child:IsA("Model") or child:IsA("Folder") then
			local f = child:GetAttribute("Floor") :: number?
			local name = child.Name
			local slab = string.match(name, "^Slab_(%d+)$")
			local stairs = string.match(name, "^Stairs_(%d+)$")
			local hide = (f and f > floor)
				or (slab and tonumber(slab) :: number > floor)
				or (stairs and tonumber(stairs) :: number >= floor)
			if hide then
				for _, p in child:GetDescendants() do
					if p:IsA("BasePart") then
						p.LocalTransparencyModifier = 1
						hidden[p] = true
					end
				end
			end
		end
	end
end

local hidePending = false
local function scheduleHide()
	if hidePending then
		return
	end
	hidePending = true
	task.delay(0.15, function()
		hidePending = false
		setHidden()
	end)
end

-- ===== The ghost =====

local function clearGhost()
	if ghost then
		ghost:Destroy()
		ghost = nil
	end
end

local function pieceBeingPlaced(): Pieces.Piece?
	if moving then
		local rec = record(moving)
		return rec and Pieces.get(rec.item)
	end
	return if selected then Pieces.get(selected) else nil
end

local function drawGhost()
	clearGhost()
	local piece = pieceBeingPlaced()
	local frame = plotFrame()
	if not piece or not cell or not frame then
		placeButton.Visible = false
		return
	end
	local candidate: Grid.Placed = {
		item = piece.id,
		floor = floor,
		x = cell.x,
		z = cell.z,
		r = rotation,
		w = piece.w,
		d = piece.d,
	}
	local layout, skip = layoutPlaced(moving)
	local ok, why = Grid.canPlace(layout, build().floors, candidate, skip)
	local ex, ez = Grid.extent(piece.w, piece.d, rotation)
	local model = Instance.new("Model")
	model.Name = "BuildGhost"
	local box = Instance.new("Part")
	box.Anchored = true
	box.CanCollide = false
	box.CanQuery = false
	box.CanTouch = false
	-- Plain and see-through: ForceField drew in stripes from above and as a
	-- bare outline from the side (his report, 2026-10-19).
	box.Material = Enum.Material.SmoothPlastic
	box.Transparency = 0.55
	box.CastShadow = false
	box.Color = if ok then Ui.Colour.Good else Ui.Colour.Bad
	box.Size = Vector3.new(ex * G.CellSize - 0.4, 6, ez * G.CellSize - 0.4)
	box.CFrame = frame * CFrame.new(Grid.pieceCentre(candidate) + Vector3.new(0, 3, 0))
	box.Parent = model
	local door = Instance.new("Part")
	door.Anchored = true
	door.CanCollide = false
	door.CanQuery = false
	door.Material = Enum.Material.Neon
	door.Color = Ui.Colour.Gold
	door.Size = Vector3.new(2, 0.4, 2)
	door.CFrame = frame
		* CFrame.new(Grid.cellCentre(floor, Grid.doorCell(candidate)) + Vector3.new(0, 0.3, 0))
	door.Parent = model
	model.Parent = workspace
	ghost = model
	local cost = if moving then 0 else (build().costs[piece.id] or Economy.pieceCost(piece.id, 0))
	info.Text = if ok
		then `{piece.name}{if moving then " (move)" else " · " .. Format.cash(cost)}  ·  R / ⟳ to rotate`
		else `{piece.name}: ` .. (({
			Overlap = "something is already there",
			Reserved = "keep the lobby and stairs clear",
			OutOfBounds = "that doesn't fit",
			DoorBlocked = "the door would open into a wall",
			DoorUnreachable = "guests couldn't reach the door",
			CutsOff = "that blocks another room's door",
			NoFloor = "build that floor first",
		}) :: any)[why or ""] or tostring(why)
	placeButton.Visible = ok
end

local function screenToCell(x: number, y: number): Grid.Cell?
	local frame = plotFrame()
	if not frame then
		return nil
	end
	local ray = camera:ScreenPointToRay(x, y)
	local planeY = frame:PointToWorldSpace(Vector3.new(0, Grid.floorY(floor), 0)).Y
	if math.abs(ray.Direction.Y) < 1e-4 then
		return nil
	end
	local t = (planeY - ray.Origin.Y) / ray.Direction.Y
	if t < 0 then
		return nil
	end
	local hit = ray.Origin + ray.Direction * t
	local l = frame:PointToObjectSpace(hit)
	local piece = pieceBeingPlaced()
	local ex, ez = 1, 1
	if piece then
		ex, ez = Grid.extent(piece.w, piece.d, rotation)
	end
	-- The anchor is the footprint's lowest cell; centre the footprint on the pointer.
	local cx = math.floor(l.X / G.CellSize - ex / 2 + 0.5)
	local cz = math.floor(l.Z / G.CellSize - ez / 2 + 0.5)
	if cx < -2 or cz < -2 or cx > G.Cells + 1 or cz > G.Cells + 1 then
		return nil
	end
	return { x = cx, z = cz }
end

local function place()
	local piece = pieceBeingPlaced()
	if not piece or not cell then
		return
	end
	if moving then
		Net.send("Move", moving, floor, cell.x, cell.z, rotation)
		moving = nil
		clearGhost()
		info.Text = HINT
	else
		Net.send("Place", piece.id, floor, cell.x, cell.z, rotation)
	end
end

-- ===== The piece menu =====

local function pieceUnderPointer(x: number, y: number): number?
	local ray = camera:ScreenPointToRay(x, y)
	local params = RaycastParams.new()
	local m = plotModel()
	if not m then
		return nil
	end
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = { m:FindFirstChild("Pieces") :: Instance }
	local result = workspace:Raycast(ray.Origin, ray.Direction * 400, params)
	local inst = result and result.Instance
	while inst and inst ~= m do
		local id = inst:GetAttribute("PieceId")
		if id then
			local f = inst:GetAttribute("Floor") :: number?
			if f and f > floor then
				return nil
			end
			return tonumber(id)
		end
		inst = inst.Parent
	end
	return nil
end

-- Whether the pointer is over the build mode's own buttons and strip: a
-- tap there is for them, never for the grid under them (a tap on a card
-- placed a room under it, 2026-10-19).
local function overUi(x: number, y: number): boolean
	for _, g in me.PlayerGui:GetGuiObjectsAtPosition(x, y) do
		if g.Visible and g:IsDescendantOf(gui) and (g:IsA("GuiButton") or g.Name == "Strip") then
			return true
		end
	end
	return false
end

-- Lights the piece `id` (nil: none) with an outline.
local function showHover(id: number?)
	local target: Instance? = nil
	local m = plotModel()
	local pieces = m and m:FindFirstChild("Pieces")
	if id and pieces then
		for _, c in pieces:GetChildren() do
			if c:GetAttribute("PieceId") == id then
				target = c
				break
			end
		end
	end
	if not target then
		if hover then
			hover.Adornee = nil
		end
		return
	end
	if not hover then
		local h = Instance.new("Highlight")
		h.Name = "BuildHover"
		h.FillColor = Ui.Colour.Gold
		h.FillTransparency = 0.85
		h.OutlineColor = Ui.Colour.Gold
		h.DepthMode = Enum.HighlightDepthMode.Occluded
		h.Parent = workspace
		hover = h
	end
	(hover :: Highlight).Adornee = target
end

local function openMenu(id: number)
	local rec = record(id)
	local piece = rec and Pieces.get(rec.item)
	if not rec or not piece then
		return
	end
	for _, c in menuBody:GetChildren() do
		if not c:IsA("UIListLayout") then
			c:Destroy()
		end
	end
	(menu:FindFirstChild("Title") :: TextLabel).Text = `{piece.name} · T{rec.tier}`
	local upCost = Economy.tierCost(rec.item, rec.tier)
	local row = Ui.frame(menuBody, "Actions", UDim2.new(1, 0, 0, 50))
	row.BackgroundTransparency = 1
	Ui.list(row, Enum.FillDirection.Horizontal, 8)
	Ui.button(
		row,
		"Upgrade",
		if upCost then `Upgrade {Format.cash(upCost)}` else "Top tier",
		UDim2.fromOffset(170, 46),
		function()
			Net.send("Upgrade", id)
			menu.Visible = false
		end,
		Ui.Colour.Teal
	)
	Ui.button(row, "Move", "Move", UDim2.fromOffset(90, 46), function()
		moving = id
		selected = nil
		rotation = rec.r
		floor = rec.floor
		menu.Visible = false
		floorLabel.Text = `Floor {floor}`
		setHidden()
		updateCamera()
		info.Text = "Tap where it should go · right-click to stop"
	end)
	local owned = 0
	for _, other in build().layout do
		if other.item == rec.item then
			owned += 1
		end
	end
	Ui.button(
		row,
		"Sell",
		`Sell +{Format.cash(Economy.sellValue(rec.item, math.max(0, owned - 1), rec.tier))}`,
		UDim2.fromOffset(150, 46),
		function()
			Net.send("Sell", id)
			menu.Visible = false
		end,
		Ui.Colour.Bad
	)
	if piece.kind == "Room" then
		Ui.label(
			menuBody,
			"DecorTitle",
			"Decor slots: tap one, then a decor piece",
			UDim2.new(1, 0, 0, 24),
			18,
			Ui.Colour.Muted
		)
		local slots = Ui.frame(menuBody, "Slots", UDim2.new(1, 0, 0, 50))
		slots.BackgroundTransparency = 1
		Ui.list(slots, Enum.FillDirection.Horizontal, 8)
		local chosenSlot = 1
		local slotButtons = {}
		for s = 1, Pieces.DecorSlots do
			local current = rec.decor[s]
			local d = if current and current ~= "" then Pieces.decor(current) else nil
			slotButtons[s] = Ui.button(
				slots,
				`Slot_{s}`,
				if d then d.name else `Slot {s} (empty)`,
				UDim2.fromOffset(170, 46),
				function()
					chosenSlot = s
					for i, b in slotButtons do
						b.BackgroundColor3 = if i == s
							then Ui.Colour.Pumpkin
							else Ui.Colour.PanelLight
					end
				end
			)
		end
		slotButtons[1].BackgroundColor3 = Ui.Colour.Pumpkin
		local list = Ui.scroll(menuBody, "Decor", UDim2.new(1, 0, 0, 220))
		Ui.list(list, Enum.FillDirection.Vertical, 6)
		for i, d in Pieces.DecorList do
			if d.location == build().location or (build().unlockedDecor or {})[d.id] then
				local b = Ui.button(
					list,
					d.id,
					`{d.name}  ·  {table.concat(d.tags, ", ")}  ·  {Format.cash(d.cost)}`,
					UDim2.new(1, -10, 0, 44),
					function()
						Net.send("Decorate", id, chosenSlot, d.id)
						menu.Visible = false
					end
				)
				b.LayoutOrder = i
				b.TextXAlignment = Enum.TextXAlignment.Left
			end
		end
	end
	menu.Visible = true
end

-- ===== Traps (§8.1): the lobby's three trap slots =====

local function openTraps()
	for _, c in menuBody:GetChildren() do
		if not c:IsA("UIListLayout") then
			c:Destroy()
		end
	end
	(menu:FindFirstChild("Title") :: TextLabel).Text = "Lobby traps"
	local hint = Ui.label(
		menuBody,
		"Hint",
		"Each trap scares the first hunter that comes near it, once a Hunter Night.",
		UDim2.new(1, 0, 0, 40),
		16,
		Ui.Colour.Muted
	)
	hint.LayoutOrder = 0
	local traps = build().traps or { "", "", "" }
	for slot = 1, #traps do
		local row = Ui.frame(menuBody, `Slot_{slot}`, UDim2.new(1, 0, 0, 50))
		row.BackgroundTransparency = 1
		row.LayoutOrder = slot
		Ui.list(row, Enum.FillDirection.Horizontal, 6)
		local label = Ui.label(row, "Label", `Slot {slot}`, UDim2.fromOffset(70, 46), 18)
		label.LayoutOrder = 0
		for i, t in Constants.Traps do
			local b = Ui.button(
				row,
				t.id,
				`{t.name}\n{Format.cash(t.cost)}`,
				UDim2.fromOffset(150, 46),
				function()
					Net.send("Trap", slot, t.id)
					menu.Visible = false
				end,
				if traps[slot] == t.id then Ui.Colour.Pumpkin else Ui.Colour.PanelLight
			)
			b.LayoutOrder = i
			b.TextSize = 14
		end
	end
	menu.Visible = true
end

-- ===== Style: the hotel's cosmetics, one per slot (Cosmetics.luau) =====

local function openStyle()
	for _, c in menuBody:GetChildren() do
		if not c:IsA("UIListLayout") then
			c:Destroy()
		end
	end
	(menu:FindFirstChild("Title") :: TextLabel).Text = "Hotel style"
	local b = build()
	local equipped = b.equipped or {}
	local order = 0
	for _, slot in { "Sign", "Lobby", "Facade" } do
		order += 1
		-- A slot's cosmetics wrap onto more lines: six or more do not fit one (a phone fits three).
		local row = Ui.frame(menuBody, `Slot_{slot}`, UDim2.new(1, 0, 0, 50))
		row.BackgroundTransparency = 1
		row.LayoutOrder = order
		row.AutomaticSize = Enum.AutomaticSize.Y
		Ui.list(row, Enum.FillDirection.Horizontal, 6).Wraps = true
		local label = Ui.label(row, "Label", slot, UDim2.fromOffset(70, 46), 18)
		label.LayoutOrder = 0
		local none = Ui.button(row, "None", "None", UDim2.fromOffset(90, 46), function()
			Net.send("Equip", slot, "")
			menu.Visible = false
		end, if (equipped[slot] or "") == "" then Ui.Colour.Pumpkin else Ui.Colour.PanelLight)
		none.LayoutOrder = 1
		for i, c in b.cosmetics or {} do
			if c.slot == slot then
				local btn = Ui.button(
					row,
					c.id,
					if c.owned then c.name else `🔒 {c.name}`,
					UDim2.fromOffset(150, 46),
					function()
						if not c.owned then
							Hud.toast(`{c.name}: from {c.from}`, Ui.Colour.Bad)
							return
						end
						Net.send("Equip", slot, c.id)
						menu.Visible = false
					end,
					if equipped[slot] == c.id
						then Ui.Colour.Pumpkin
						elseif c.owned then Ui.Colour.PanelLight
						else Ui.Colour.Panel
				)
				btn.LayoutOrder = 1 + i
				btn.TextSize = 14
			end
		end
	end
	menu.Visible = true
end

-- ===== The strip of piece cards =====

-- Stops placing or moving: the ghost goes, and a tap opens a piece's menu again.
function stopPlacing()
	selected, moving = nil, nil
	clearGhost()
	placeButton.Visible = false
	info.Text = HINT
	redrawCards()
end

function redrawCards()
	for _, c in cards:GetChildren() do
		if c:IsA("GuiButton") then
			c:Destroy()
		end
	end
	local b = build()
	for i, p in Pieces.List do
		if p.kind == tab and (p.location == b.location or b.buildable[p.id] == true) then
			local can = b.buildable[p.id] == true
			local cost = b.costs[p.id] or p.cost
			local text = `{p.name}\n{p.w}×{p.d} · {Format.cash(cost)}`
			if not can then
				text = `{p.name}\n🔒 {b.buildable[p.id]}`
			end
			local card = Ui.button(
				cards,
				p.id,
				text,
				UDim2.fromOffset(150, 70),
				function()
					if not can then
						Hud.toast(`{p.name}: {b.buildable[p.id]}`, Ui.Colour.Bad)
						return
					end
					-- Tapping the chosen card again puts it down.
					if selected == p.id then
						stopPlacing()
						return
					end
					selected = p.id
					moving = nil
					showHover(nil)
					info.Text = `{p.name}: tap the grid · tap the card again to stop`
					redrawCards()
					drawGhost()
				end,
				if selected == p.id
					then Ui.Colour.Pumpkin
					elseif can then Ui.Colour.PanelLight
					else Ui.Colour.Ink
			)
			card.LayoutOrder = i
			card.TextSize = 16
		end
	end
	floorLabel.Text = `Floor {floor}/{b.floors}`
	local buy = tools:FindFirstChild("BuyFloor", true) :: TextButton?
	if buy then
		buy.Visible = b.floors < b.maxFloors
		buy.Text = if b.floorCost then `+ Floor {Format.cash(b.floorCost)}` else "+ Floor"
	end
end

local function setActive(on: boolean)
	active = on
	strip.Visible = on
	tools.Visible = on
	local hud = me.PlayerGui:FindFirstChild("Hud")
	local leftColumn = hud and hud:FindFirstChild("Left")
	if leftColumn and leftColumn:IsA("GuiObject") then
		leftColumn.Visible = not on
	end
	-- Gloom steps aside while building: the strip says what to do.
	local tutorial = me.PlayerGui:FindFirstChild("Tutorial")
	if tutorial and tutorial:IsA("ScreenGui") then
		tutorial.Enabled = not on
	end
	menu.Visible = false
	selected, moving, cell = nil, nil, nil
	clearGhost()
	showHover(nil)
	if on then
		floor = 1
		updateCamera()
		redrawCards()
	else
		camera.CameraType = Enum.CameraType.Custom
		local character = me.Character
		local hum = character and character:FindFirstChildOfClass("Humanoid")
		if hum then
			camera.CameraSubject = hum
		end
	end
	setHidden()
end

function BuildController.isActive(): boolean
	return active
end

function BuildController.open()
	setActive(true)
end

function BuildController.Init()
	gui = Ui.screen("Build", 3)
	-- The strip: bottom centre, between a phone's thumbstick and jump button (§11).
	strip = Ui.panel(
		gui,
		"Strip",
		UDim2.new(0.55, 0, 0, 132),
		UDim2.new(0.5, 0, 1, -8),
		Vector2.new(0.5, 1)
	)
	local stripCap = Instance.new("UISizeConstraint")
	stripCap.MinSize = Vector2.new(380, 0)
	stripCap.Parent = strip
	strip.Visible = false
	info = Ui.label(strip, "Info", HINT, UDim2.new(1, -24, 0, 26), 18, Ui.Colour.Gold)
	info.Position = UDim2.fromOffset(12, 4)
	cards = Ui.scroll(strip, "Cards", UDim2.new(1, -24, 0, 86), UDim2.fromOffset(12, 36), true)
	Ui.list(cards, Enum.FillDirection.Horizontal, 8)

	-- The tools, top-left where the HUD's menu column is while not building
	-- (hidden meanwhile), above a phone's thumbstick (§11). One row per group,
	-- each group its own colour (his report, 2026-10-19: "the same colour on
	-- nearly all, group them better"): what to build, which floor, the camera
	-- and placing, the extras and leaving.
	tools = Ui.frame(gui, "Tools", UDim2.fromOffset(380, 206), UDim2.fromOffset(10, 56))
	tools.BackgroundTransparency = 1
	tools.Visible = false
	Ui.list(tools, Enum.FillDirection.Vertical, 10)
	local FLOOR_BLUE = Color3.fromRGB(58, 78, 150)
	local EXTRA_VIOLET = Color3.fromRGB(110, 62, 150)
	local rows = 0
	local function row(): Frame
		rows += 1
		local r = Ui.frame(tools, `Row_{rows}`, UDim2.new(1, 0, 0, 44))
		r.BackgroundTransparency = 1
		r.LayoutOrder = rows
		Ui.list(r, Enum.FillDirection.Horizontal, 6)
		return r
	end
	local function tool(
		parent: Frame,
		name: string,
		text: string,
		width: number,
		fn: () -> (),
		colour: Color3?
	): TextButton
		local b = Ui.button(parent, name, text, UDim2.fromOffset(width, 44), fn, colour)
		b.LayoutOrder = #parent:GetChildren()
		return b
	end

	-- What to build: the open tab lit, as the cards are.
	local what = row()
	local roomsTab, amenitiesTab
	local function paintTabs()
		roomsTab.BackgroundColor3 = if tab == "Room" then Ui.Colour.Pumpkin else Ui.Colour.Panel
		amenitiesTab.BackgroundColor3 = if tab == "Amenity"
			then Ui.Colour.Pumpkin
			else Ui.Colour.Panel
	end
	roomsTab = tool(what, "Rooms", "Rooms", 114, function()
		tab = "Room"
		paintTabs()
		redrawCards()
	end)
	amenitiesTab = tool(what, "Amenities", "Amenities", 114, function()
		tab = "Amenity"
		paintTabs()
		redrawCards()
	end)
	paintTabs()

	-- Which floor: down, the floor, up, and buying the next.
	local floors = row()
	tool(floors, "Down", "▼", 50, function()
		floor = math.max(1, floor - 1)
		redrawCards()
		setHidden()
		updateCamera()
		drawGhost()
	end, FLOOR_BLUE)
	floorLabel = Ui.label(floors, "FloorLabel", "Floor 1", UDim2.fromOffset(90, 44), 18)
	floorLabel.LayoutOrder = 2
	floorLabel.TextXAlignment = Enum.TextXAlignment.Center
	tool(floors, "Up", "▲", 50, function()
		floor = math.min(build().floors, floor + 1)
		redrawCards()
		setHidden()
		updateCamera()
		drawGhost()
	end, FLOOR_BLUE)
	tool(floors, "BuyFloor", "+ Floor", 150, function()
		Net.send("BuyFloor")
	end, Ui.Colour.Teal)

	-- The camera and placing.
	local placing = row()
	tool(placing, "Rotate", "⟳ Rotate", 114, function()
		rotation = (rotation + 1) % 4
		drawGhost()
	end)
	tool(placing, "Turn", "↻ View", 114, function()
		-- A quarter turn, to the next side square on.
		yaw = (math.floor(yaw / (math.pi / 2) + 0.5) + 1) * math.pi / 2
		updateCamera()
	end)
	placeButton = tool(placing, "Place", "✔ Place", 114, place, Ui.Colour.Good)
	placeButton.Visible = false

	-- The extras, and leaving.
	local extras = row()
	tool(extras, "Traps", "Traps", 114, openTraps, EXTRA_VIOLET)
	tool(extras, "Style", "🎨 Style", 114, openStyle, EXTRA_VIOLET)
	tool(extras, "Done", "Done", 114, function()
		setActive(false)
	end, Ui.Colour.Bad)

	-- Where the HUD's menu column starts (Hud's `placeTop`).
	Ui.onTopRow(function(up: boolean)
		tools.Position = UDim2.fromOffset(10, if up then 6 else 56)
	end)

	menu, menuBody = Ui.window(gui, "PieceMenu", "Piece", UDim2.fromScale(0.5, 0.6))
	Ui.list(menuBody, Enum.FillDirection.Vertical, 8)
end

function BuildController.Start()
	Hud.button("BuildButton", "🔨 Build", "Left", function()
		setActive(not active)
	end, 1)
	State.changed:Connect(function()
		if active then
			redrawCards()
			drawGhost()
			scheduleHide()
		end
	end)
	-- Looking round the plot (his ask, 2026-10-19): the mouse wheel or a pinch
	-- zooms; the right mouse button dragged, a two-finger twist, or the , and .
	-- keys turn the camera (E is the prompts' key); ↻ View still turns a quarter.
	local function zoomBy(factor: number)
		zoom = math.clamp(zoom * factor, 0.35, 1.4)
		updateCamera()
	end
	local function turnBy(radians: number)
		yaw += radians
		updateCamera()
	end
	local pinchStart = 1
	UserInputService.TouchPinch:Connect(function(_, scale, _, state, processed)
		if not active or processed then
			return
		end
		if state == Enum.UserInputState.Begin then
			pinchStart = zoom
		end
		zoom = math.clamp(pinchStart / math.max(scale, 0.05), 0.35, 1.4)
		updateCamera()
	end)
	local twistLast = 0
	UserInputService.TouchRotate:Connect(function(_, twist, _, state, processed)
		if not active or processed then
			return
		end
		if state == Enum.UserInputState.Begin then
			twistLast = 0
		end
		turnBy(math.rad(twist - twistLast))
		twistLast = twist
	end)
	RunService.RenderStepped:Connect(function(dt)
		if not active or UserInputService:GetFocusedTextBox() then
			return
		end
		local turn = (if UserInputService:IsKeyDown(Enum.KeyCode.Period) then 1 else 0)
			- (if UserInputService:IsKeyDown(Enum.KeyCode.Comma) then 1 else 0)
		if turn ~= 0 then
			turnBy(turn * dt * 1.5)
		end
	end)
	UserInputService.InputChanged:Connect(function(input, processed)
		if not active or processed then
			return
		end
		if
			input.UserInputType == Enum.UserInputType.MouseMovement
			and overUi(input.Position.X, input.Position.Y)
		then
			return
		end
		if input.UserInputType == Enum.UserInputType.MouseWheel then
			zoomBy(1 - 0.12 * input.Position.Z)
			return
		end
		if
			input.UserInputType == Enum.UserInputType.MouseMovement
			and UserInputService:IsMouseButtonPressed(Enum.UserInputType.MouseButton2)
		then
			turnBy(-input.Delta.X * 0.008)
		end
		-- With nothing being placed, the piece under the mouse lights up: it can be tapped.
		if input.UserInputType == Enum.UserInputType.MouseMovement and not pieceBeingPlaced() then
			showHover(pieceUnderPointer(input.Position.X, input.Position.Y))
		end
		if input.UserInputType == Enum.UserInputType.MouseMovement and pieceBeingPlaced() then
			local c = screenToCell(input.Position.X, input.Position.Y)
			if c and (not cell or c.x ~= cell.x or c.z ~= cell.z) then
				cell = c
				drawGhost()
			end
		end
	end)
	UserInputService.InputBegan:Connect(function(input, processed)
		if not active or processed then
			return
		end
		if input.UserInputType == Enum.UserInputType.MouseButton2 then
			rightDownAt = Vector2.new(input.Position.X, input.Position.Y)
		elseif input.KeyCode == Enum.KeyCode.B then
			setActive(false) -- B opens build mode from the HUD (Hud's KEYS) and closes it here
		elseif input.KeyCode == Enum.KeyCode.R then
			rotation = (rotation + 1) % 4
			drawGhost()
		elseif
			input.UserInputType == Enum.UserInputType.MouseButton1
			or input.UserInputType == Enum.UserInputType.Touch
		then
			local pos = input.Position
			if overUi(pos.X, pos.Y) then
				return
			end
			if pieceBeingPlaced() then
				local c = screenToCell(pos.X, pos.Y)
				if c then
					cell = c
					drawGhost()
					if
						input.UserInputType == Enum.UserInputType.MouseButton1
						and placeButton.Visible
					then
						place()
					end
				end
			else
				local id = pieceUnderPointer(pos.X, pos.Y)
				if id then
					openMenu(id)
				end
			end
		end
	end)
	-- A right-click that did not drag the camera round stops placing.
	UserInputService.InputEnded:Connect(function(input)
		if not active or input.UserInputType ~= Enum.UserInputType.MouseButton2 then
			return
		end
		local down = rightDownAt
		rightDownAt = nil
		local at = Vector2.new(input.Position.X, input.Position.Y)
		if down and (at - down).Magnitude < 6 and (selected or moving) then
			stopPlacing()
		end
	end)
	RunService.RenderStepped:Connect(function()
		if active and camera.CameraType ~= Enum.CameraType.Scriptable then
			updateCamera()
		end
	end)
	-- A rebuilt hotel (a new floor) makes new parts: hide them again.
	local function watchPlot()
		local m = plotModel()
		if m then
			m.DescendantAdded:Connect(function()
				if active then
					scheduleHide()
				end
			end)
		end
	end
	me:GetAttributeChangedSignal("Plot"):Connect(watchPlot)
	watchPlot()
end

return BuildController
