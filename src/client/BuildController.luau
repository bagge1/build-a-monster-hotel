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
local view = 0 -- which side the camera looks from, 0..3

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
	local angle = view * math.pi / 2
	local back = frame:VectorToWorldSpace(Vector3.new(math.sin(angle), 0, -math.cos(angle)))
	camera.CameraType = Enum.CameraType.Scriptable
	camera.CFrame = CFrame.lookAt(centre + back * 50 + Vector3.new(0, 62, 0), centre)
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
	box.Material = Enum.Material.ForceField
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
		info.Text = "Moved."
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
		info.Text = "Tap where it should go"
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
		local row = Ui.frame(menuBody, `Slot_{slot}`, UDim2.new(1, 0, 0, 50))
		row.BackgroundTransparency = 1
		row.LayoutOrder = order
		Ui.list(row, Enum.FillDirection.Horizontal, 6)
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

local function redrawCards()
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
					selected = p.id
					moving = nil
					info.Text = `{p.name}: tap the grid`
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
	local buy = tools:FindFirstChild("BuyFloor") :: TextButton?
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
	info = Ui.label(strip, "Info", "Choose a piece", UDim2.new(1, -24, 0, 26), 18, Ui.Colour.Gold)
	info.Position = UDim2.fromOffset(12, 4)
	cards = Ui.scroll(strip, "Cards", UDim2.new(1, -24, 0, 86), UDim2.fromOffset(12, 36), true)
	Ui.list(cards, Enum.FillDirection.Horizontal, 8)

	-- The tools: three columns top-left, where the HUD's menu column is while
	-- not building (hidden meanwhile), so eleven tools fit a phone's height above
	-- its thumbstick (§11).
	tools = Ui.frame(gui, "Tools", UDim2.fromOffset(360, 210), UDim2.fromOffset(10, 56))
	tools.BackgroundTransparency = 1
	tools.Visible = false
	local grid = Instance.new("UIGridLayout")
	grid.CellSize = UDim2.fromOffset(114, 44)
	grid.CellPadding = UDim2.fromOffset(6, 6)
	grid.SortOrder = Enum.SortOrder.LayoutOrder
	grid.Parent = tools
	local function tool(
		name: string,
		text: string,
		order: number,
		fn: () -> (),
		colour: Color3?
	): TextButton
		local b = Ui.button(tools, name, text, UDim2.fromOffset(114, 44), fn, colour)
		b.LayoutOrder = order
		return b
	end
	tool("Rooms", "Rooms", 1, function()
		tab = "Room"
		redrawCards()
	end)
	tool("Amenities", "Amenities", 2, function()
		tab = "Amenity"
		redrawCards()
	end)
	tool("Up", "▲ Floor", 3, function()
		floor = math.min(build().floors, floor + 1)
		redrawCards()
		setHidden()
		updateCamera()
		drawGhost()
	end)
	floorLabel = Ui.label(tools, "FloorLabel", "Floor 1", UDim2.fromOffset(114, 44), 18)
	floorLabel.LayoutOrder = 4
	floorLabel.TextXAlignment = Enum.TextXAlignment.Center
	tool("Down", "▼ Floor", 5, function()
		floor = math.max(1, floor - 1)
		redrawCards()
		setHidden()
		updateCamera()
		drawGhost()
	end)
	tool("BuyFloor", "+ Floor", 6, function()
		Net.send("BuyFloor")
	end, Ui.Colour.Teal)
	tool("Rotate", "⟳ Rotate", 7, function()
		rotation = (rotation + 1) % 4
		drawGhost()
	end)
	tool("Turn", "↻ View", 8, function()
		view = (view + 1) % 4
		updateCamera()
	end)
	placeButton = tool("Place", "✔ Place", 9, place, Ui.Colour.Good)
	placeButton.Visible = false
	tool("Traps", "Traps", 9.5, openTraps)
	tool("Style", "🎨 Style", 9.7, openStyle)
	tool("Done", "Done", 10, function()
		setActive(false)
	end, Ui.Colour.Bad)

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
	UserInputService.InputChanged:Connect(function(input, processed)
		if not active or processed then
			return
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
		if input.KeyCode == Enum.KeyCode.R then
			rotation = (rotation + 1) % 4
			drawGhost()
		elseif
			input.UserInputType == Enum.UserInputType.MouseButton1
			or input.UserInputType == Enum.UserInputType.Touch
		then
			local pos = input.Position
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
