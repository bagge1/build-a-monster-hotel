--!strict
--[[
	Build mode (GDD §5, §5.4, §13.2 "Building": the client draws the ghost,
	snaps and rotates; the server validates). The client sends only an intent
	(`{item, floor, cell, rotation}`, or squares for decor); `Grid`, `Furnish`
	and `Layout` run here too, on the state's copy of the hotel, so the ghost
	turns red before the server would refuse.

	One thumb (§11): tap a card, tap the grid to put the ghost there, press
	Place. With a mouse, the ghost follows the cursor and a click places; R
	rotates. With nothing chosen, tapping a built piece or a piece of decor
	opens its menu (move, sell; a room's tier, its decor points and its
	floor), and tapping an area of the plot not yet bought offers it (§5.4).

	Tabs (§5.4, free building): Rooms, Amenities, Stairs (a 2×2 piece joining
	a floor to the one above; a new floor's first is free), Decor (on a grid
	of 3-stud squares, in rooms and on hallway floor) and Floors (a finish:
	choose one, then tap a room, the lobby or a hallway).

	The camera looks down on the plot while building, and floors above the
	one being built on are hidden locally (`LocalTransparencyModifier`).

	The gamepad (§11, UI.md "Gamepad"): build mode opens on its cards (the
	selection, ButtonY to and from them); a chosen card hands the left stick
	to a cursor on the plot, which stands in for the pointer: A places or
	taps there, RB rotates (beside R), B steps back (stop placing, leave the
	cards, leave build mode), the D-pad changes floor (up, down) and turns
	the view a quarter (left, right), the right stick turns and zooms. The
	keys are input actions (`Controls`); the pointer's clicks, drags and
	pinches stay on UserInputService.
]]

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Format = require(ReplicatedStorage.Shared.Format)
local Grid = require(ReplicatedStorage.Shared.Grid)
local Layout = require(ReplicatedStorage.Shared.Layout)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Controls = require(script.Parent.Controls)
local State = require(script.Parent.State)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)

local G = Constants.Grid
local SQUARE = G.CellSize / G.Squares

local BuildController = {}

local me = Players.LocalPlayer
local camera = workspace.CurrentCamera

local active = false
local floor = 1
local rotation = 0
local selected: string? = nil -- a piece id to place
local selectedDecor: string? = nil -- a decor id to place
local selectedFinish: string? = nil -- a finish to lay ("" the model's own)
local moving: number? = nil -- a built piece being moved
local movingDecor: number? = nil -- a piece of decor being moved
local cell: Grid.Cell? = nil -- where the ghost's anchor is: a cell, or a square for decor
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
local paintTabs: () -> ()
-- What the strip says while nothing is being placed: that a placed piece is
-- tapped to change it (his report, 2026-10-19: no way to remove or replace a room).
local function idleHint(): string
	return Controls.hint(
		"Choose something to build, or tap a room, decor or a closed area",
		"Y for the cards, or A on a room, decor or a closed area"
	)
end
-- What the strip says while a placed piece or decor is being moved.
local function moveHint(): string
	return Controls.hint(
		"Tap where it should go · right-click to stop",
		"Steer it with the stick, A to put it down · B to stop"
	)
end
local hover: Highlight? = nil
local stopPlacing: () -> ()
local rightDownAt: Vector2? = nil
local redrawCards: () -> ()
local ghost: Model? = nil
local hidden: { [BasePart]: boolean } = {}
local areaLabels: { BillboardGui } = {}

-- The gamepad (§11): a cursor on the plot in place of the pointer.
local pad: Vector3? = nil -- plot-local, on the floor in view
local padMarker: BasePart? = nil
-- The plot's width the cursor crosses in a second at full zoom.
local PAD_SPEED = 0.45
local buildKeys: InputContext -- while building: rotate, leave, the camera
local padKeys: InputContext -- while building with nothing selected: the cursor, A, the D-pad
local cursorAction: InputAction
local cameraAction: InputAction
local toFloor: (number) -> ()
local turnQuarter: (number) -> ()

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
		or {
			layout = {},
			decor = {},
			areas = { G.StartArea },
			floors = 1,
			buildable = {},
			costs = {},
			blocked = {},
			maxFloors = 3,
			location = 1,
			freeStairs = 0,
			finishes = {},
		}
end

-- The hotel as the pure rules see it, from the state's copy.
local function world(): Grid.World
	local b = build()
	local areas = {}
	for _, i in b.areas or {} do
		areas[i] = true
	end
	return Layout.world(b.floors, areas, b.layout, b.decor or {})
end

local function blockedFn(item: string): { [number]: boolean }
	local out = {}
	for _, k in (build().blocked or {})[item] or {} do
		out[k] = true
	end
	return out
end

local function record(id: number): any
	for _, rec in build().layout do
		if rec.id == id then
			return rec
		end
	end
	return nil
end

local function decorRecord(id: number): any
	for _, rec in build().decor or {} do
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
	local function hide(p: BasePart)
		p.LocalTransparencyModifier = 1
		hidden[p] = true
	end
	-- The facade's parts carry their floor in their names (`Left_2_Post`).
	local facade = m:FindFirstChild("Facade")
	for _, p in (if facade then facade:GetChildren() else {}) do
		local f = tonumber(string.match(p.Name, "^%a+_(%d+)_"))
		if p:IsA("BasePart") and f and f > floor then
			hide(p)
		end
	end
	for _, child in m:GetDescendants() do
		local f = child:GetAttribute("Floor") :: number?
		if child:IsA("BasePart") and f and f > floor then
			hide(child)
		elseif child:IsA("Model") or child:IsA("Folder") then
			local slab = string.match(child.Name, "^Slab_(%d+)$")
			if (f and f > floor) or (slab and tonumber(slab) :: number > floor) then
				for _, p in child:GetDescendants() do
					if p:IsA("BasePart") then
						hide(p)
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

-- ===== The areas not yet bought (§5.4) =====

local function clearAreaLabels()
	for _, l in areaLabels do
		l:Destroy()
	end
	table.clear(areaLabels)
end

-- A label over each closed area of the floor in view: its price, or why it can't be bought yet.
local function drawAreaLabels()
	clearAreaLabels()
	local m = plotModel()
	local folder = m and m:FindFirstChild("Areas")
	if not active or not folder then
		return
	end
	local b = build()
	local owned = {}
	for _, i in b.areas or {} do
		owned[i] = true
	end
	for _, plate in folder:GetChildren() do
		if plate:IsA("BasePart") and plate:GetAttribute("Floor") == floor then
			local index = plate:GetAttribute("Area") :: number
			local can = Grid.canBuyArea(owned, index)
			local tag = Instance.new("BillboardGui")
			tag.Name = "AreaLabel"
			tag.Adornee = plate
			tag.Size = UDim2.fromOffset(150, 46)
			tag.StudsOffsetWorldSpace = Vector3.new(0, 2, 0)
			tag.AlwaysOnTop = true
			tag.LightInfluence = 0
			local text = Ui.label(
				tag,
				"Text",
				if can and b.areaCost
					then `Area for sale\n{Format.cash(b.areaCost)}`
					else "Closed area\nbuy one next to it",
				UDim2.fromScale(1, 1),
				16,
				if can then Ui.Colour.Gold else Ui.Colour.Muted
			)
			text.TextXAlignment = Enum.TextXAlignment.Center
			text.TextStrokeTransparency = 0.3
			tag.Parent = me.PlayerGui -- a billboard inside a ScreenGui is never drawn
			table.insert(areaLabels, tag)
		end
	end
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

local function decorBeingPlaced(): Pieces.Decor?
	if movingDecor then
		local rec = decorRecord(movingDecor)
		return rec and Pieces.decor(rec.item)
	end
	return if selectedDecor then Pieces.decor(selectedDecor) else nil
end

local function placing(): boolean
	return pieceBeingPlaced() ~= nil or decorBeingPlaced() ~= nil
end

local function ghostBox(model: Model, size: Vector3, at: CFrame, ok: boolean)
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
	box.Size = size
	box.CFrame = at
	box.Parent = model
end

local function marker(model: Model, at: CFrame)
	local door = Instance.new("Part")
	door.Anchored = true
	door.CanCollide = false
	door.CanQuery = false
	door.Material = Enum.Material.Neon
	door.Color = Ui.Colour.Gold
	door.Size = Vector3.new(2, 0.4, 2)
	door.CFrame = at
	door.Parent = model
end

local function drawGhost()
	clearGhost()
	local piece = pieceBeingPlaced()
	local d = decorBeingPlaced()
	local frame = plotFrame()
	if (not piece and not d) or not cell or not frame then
		placeButton.Visible = false
		return
	end
	local here = cell :: Grid.Cell
	local w = world()
	local model = Instance.new("Model")
	model.Name = "BuildGhost"
	local ok, why
	local name, cost
	if piece then
		local candidate = Layout.piece(
			"",
			{ item = piece.id, floor = floor, x = here.x, z = here.z, r = rotation }
		) :: Grid.Placed
		candidate.id = nil
		local skip = if moving then Layout.find(w, tostring(moving)) else nil
		ok, why = Grid.canPlace(w, candidate, skip)
		local ex, ez = Grid.extent(piece.w, piece.d, rotation)
		ghostBox(
			model,
			Vector3.new(ex * G.CellSize - 0.4, 6, ez * G.CellSize - 0.4),
			frame * CFrame.new(Grid.pieceCentre(candidate) + Vector3.new(0, 3, 0)),
			ok
		)
		for _, s in Grid.doors(candidate) do
			marker(model, frame * CFrame.new(Grid.cellCentre(s.floor, s) + Vector3.new(0, 0.3, 0)))
		end
		name = piece.name
		cost = if moving then nil else (build().costs[piece.id] or Economy.pieceCost(piece.id, 0))
	else
		local dec = d :: Pieces.Decor
		local candidate = Layout.decor(
			"",
			{ item = dec.id, floor = floor, x = here.x, z = here.z, r = rotation }
		) :: Grid.DecorPlaced
		candidate.id = nil
		ok, why = Layout.canPlaceDecor(
			w,
			candidate,
			if movingDecor then tostring(movingDecor) else nil,
			blockedFn
		)
		local ex, ez = Grid.extent(dec.w, dec.d, rotation)
		local h = math.max(0.3, dec.height)
		ghostBox(
			model,
			Vector3.new(ex * SQUARE - 0.2, h, ez * SQUARE - 0.2),
			frame * CFrame.new(Grid.decorCentre(candidate) + Vector3.new(0, h / 2, 0)),
			ok
		)
		-- Its front, so a turn can be seen.
		local front = Grid.doorFacing(rotation) * (math.max(ex, ez) * SQUARE / 2 + 0.6)
		marker(
			model,
			frame * CFrame.new(Grid.decorCentre(candidate) + front + Vector3.new(0, 0.3, 0))
		)
		name = dec.name
		cost = if movingDecor then nil else dec.cost
	end
	model.Parent = workspace
	ghost = model
	info.Text = if ok
		then `{name}{if cost
			then " · " .. (if cost == 0 then "free" else Format.cash(cost))
			else " (move)"}  ·  {Controls.hint("R / ⟳ to rotate", "RB / ⟳ to rotate")}`
		else `{name}: {Hud.refusal(why or "")}`
	placeButton.Visible = ok == true
end

-- The plot-local point under the pointer on the floor in view, or nil.
local function pointerLocal(x: number, y: number): Vector3?
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
	return frame:PointToObjectSpace(ray.Origin + ray.Direction * t)
end

-- The anchor under the pointer: a cell for a piece, a square for decor, the footprint centred on it.
local function screenToAnchor(x: number, y: number): Grid.Cell?
	local l = pointerLocal(x, y)
	if not l then
		return nil
	end
	local size, ex, ez, limit = G.CellSize, 1, 1, G.Cells
	local piece, d = pieceBeingPlaced(), decorBeingPlaced()
	if piece then
		ex, ez = Grid.extent(piece.w, piece.d, rotation)
	elseif d then
		size, limit = SQUARE, G.Cells * G.Squares
		ex, ez = Grid.extent(d.w, d.d, rotation)
	end
	local cx = math.floor(l.X / size - ex / 2 + 0.5)
	local cz = math.floor(l.Z / size - ez / 2 + 0.5)
	if cx < -2 or cz < -2 or cx > limit + 1 or cz > limit + 1 then
		return nil
	end
	return { x = cx, z = cz }
end

local function place()
	local piece, d = pieceBeingPlaced(), decorBeingPlaced()
	if not cell then
		return
	end
	if moving and piece then
		Net.send("Move", moving, floor, cell.x, cell.z, rotation)
		stopPlacing()
	elseif movingDecor and d then
		Net.send("MoveDecor", movingDecor, floor, cell.x, cell.z, rotation)
		stopPlacing()
	elseif piece then
		Net.send("Place", piece.id, floor, cell.x, cell.z, rotation)
	elseif d then
		Net.send("PlaceDecor", d.id, floor, cell.x, cell.z, rotation)
	end
end

-- ===== What is under the pointer =====

-- The piece (`PieceId`) or the decor (`DecorId`) under the pointer, on the floor in view.
local function underPointer(x: number, y: number): (number?, string?)
	local ray = camera:ScreenPointToRay(x, y)
	local m = plotModel()
	if not m then
		return nil, nil
	end
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	local include = {}
	for _, name in { "Pieces", "Decor" } do
		local f = m:FindFirstChild(name)
		if f then
			table.insert(include, f)
		end
	end
	params.FilterDescendantsInstances = include
	local result = workspace:Raycast(ray.Origin, ray.Direction * 400, params)
	local inst = result and result.Instance
	while inst and inst ~= m do
		local decorId = inst:GetAttribute("DecorId")
		local pieceId = inst:GetAttribute("PieceId")
		if decorId or pieceId then
			local f = inst:GetAttribute("Floor") :: number?
			if f and f > floor then
				return nil, nil
			end
			return tonumber(decorId or pieceId), if decorId then "Decor" else "Piece"
		end
		inst = inst.Parent
	end
	return nil, nil
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

-- Lights a piece or decor (nil: none) with an outline.
local function showHover(id: number?, kind: string?)
	local target: Instance? = nil
	local m = plotModel()
	local folder = m and m:FindFirstChild(if kind == "Decor" then "Decor" else "Pieces")
	local attr = if kind == "Decor" then "DecorId" else "PieceId"
	if id and folder then
		for _, c in folder:GetChildren() do
			if tonumber(c:GetAttribute(attr)) == id then
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

-- ===== The gamepad's cursor (§11) =====

-- Where the cursor is on the screen: the pointer's stand-in.
local function padScreen(): Vector2?
	local frame = plotFrame()
	local p = pad
	if not frame or not p then
		return nil
	end
	local s = camera:WorldToScreenPoint(
		frame:PointToWorldSpace(Vector3.new(p.X, Grid.floorY(floor), p.Z))
	)
	return Vector2.new(s.X, s.Y)
end

local function hidePadMarker()
	if padMarker and padMarker.Parent then
		padMarker.Parent = nil
	end
end

-- The ghost, the outline and the marker after the cursor (or the floor) moved;
-- `force` redraws the ghost where it stands.
local function padRefresh(force: boolean?)
	local s = padScreen()
	local frame = plotFrame()
	local p = pad
	if not s or not frame or not p or not active or not Controls.gamepad() then
		hidePadMarker()
		return
	end
	if placing() then
		hidePadMarker()
		local c = screenToAnchor(s.X, s.Y)
		if c and (force or not cell or c.x ~= cell.x or c.z ~= cell.z) then
			cell = c
			drawGhost()
		end
		return
	end
	showHover(underPointer(s.X, s.Y))
	if not padMarker then
		-- The door marker's look: where the cursor stands while nothing is placed.
		local m = Instance.new("Part")
		m.Name = "BuildCursor"
		m.Anchored = true
		m.CanCollide = false
		m.CanQuery = false
		m.CanTouch = false
		m.Material = Enum.Material.Neon
		m.Color = Ui.Colour.Gold
		m.Size = Vector3.new(2, 0.4, 2)
		padMarker = m
	end
	local m = padMarker :: BasePart
	m.CFrame = frame * CFrame.new(p.X, Grid.floorY(floor) + 0.3, p.Z)
	m.Parent = workspace
end

-- The left stick: the cursor moves the way the stick points on the screen.
local function movePad(v: Vector2, dt: number)
	local frame = plotFrame()
	if not frame then
		return
	end
	local size = G.Cells * G.CellSize
	local p = pad or Vector3.new(size / 2, 0, size / 2)
	local f = frame:VectorToObjectSpace(camera.CFrame.LookVector)
	local r = frame:VectorToObjectSpace(camera.CFrame.RightVector)
	f = Vector3.new(f.X, 0, f.Z)
	r = Vector3.new(r.X, 0, r.Z)
	if f.Magnitude < 1e-3 or r.Magnitude < 1e-3 then
		return
	end
	p += (r.Unit * v.X + f.Unit * v.Y) * size * PAD_SPEED * zoom * dt
	pad = Vector3.new(math.clamp(p.X, 0, size), 0, math.clamp(p.Z, 0, size))
	padRefresh()
end

-- A chosen card, or a piece to move, hands the stick to the cursor: the selection goes.
local function toPlot()
	if Controls.gamepad() then
		Controls.select(nil)
		padRefresh(true)
	end
end

-- ===== Menus =====

local function clearMenu(title: string)
	for _, c in menuBody:GetChildren() do
		if not c:IsA("UIListLayout") then
			c:Destroy()
		end
	end
	(menu:FindFirstChild("Title") :: TextLabel).Text = title
end

local function actionRow(): Frame
	local row = Ui.frame(menuBody, "Actions", UDim2.new(1, 0, 0, 50))
	row.BackgroundTransparency = 1
	Ui.list(row, Enum.FillDirection.Horizontal, 8)
	return row
end

-- The finishes of this location as a row of buttons; `pick` is called with the chosen id ("" the model's own).
local function finishRow(current: string, pick: (string) -> ())
	local row = Ui.frame(menuBody, "Finishes", UDim2.new(1, 0, 0, 50))
	row.BackgroundTransparency = 1
	row.AutomaticSize = Enum.AutomaticSize.Y
	Ui.list(row, Enum.FillDirection.Horizontal, 6).Wraps = true
	local own = Ui.button(row, "Own", "Its own", UDim2.fromOffset(110, 44), function()
		pick("")
	end, if current == "" then Ui.Colour.Pumpkin else Ui.Colour.PanelLight)
	own.TextSize = 15
	for i, f in Pieces.Finishes do
		if f.location == build().location then
			local b = Ui.button(row, f.id, f.name, UDim2.fromOffset(130, 44), function()
				pick(f.id)
			end, if current == f.id then Ui.Colour.Pumpkin else Ui.Colour.PanelLight)
			b.TextSize = 15
			b.LayoutOrder = i
		end
	end
end

local function startMoving(id: number, rec: any)
	moving = id
	movingDecor = nil
	selected, selectedDecor, selectedFinish = nil, nil, nil
	rotation = rec.r
	floor = rec.floor
	menu.Visible = false
	floorLabel.Text = `Floor {floor}`
	setHidden()
	updateCamera()
	drawAreaLabels()
	info.Text = moveHint()
	toPlot()
end

local function openMenu(id: number)
	local rec = record(id)
	local piece = rec and Pieces.get(rec.item)
	if not rec or not piece then
		return
	end
	local title = piece.name
	if piece.kind == "Room" then
		title = `{piece.name} · T{rec.tier or 1}`
	end
	clearMenu(title)
	if piece.kind == "Room" then
		local nextText = if rec.nextAt
			then `T{(rec.tier or 1) + 1} at {rec.nextAt} points`
			else "the top tier"
		local l = Ui.label(
			menuBody,
			"Tier",
			`Decor points {rec.points or 0} · {nextText}. Place decor inside it to raise its tier (+50 % pay per tier).`,
			UDim2.new(1, 0, 0, 44),
			17,
			Ui.Colour.Muted
		)
		l.LayoutOrder = 0
	elseif piece.kind == "Stairs" then
		Ui.label(
			menuBody,
			"About",
			`Joins floor {rec.floor} to floor {rec.floor + 1}. The last stair to a floor with rooms stays.`,
			UDim2.new(1, 0, 0, 44),
			17,
			Ui.Colour.Muted
		)
	elseif piece.kind == "Desk" then
		Ui.label(
			menuBody,
			"About",
			"Guests queue in front of it. Move it anywhere on floor 1 they can reach from the entrance.",
			UDim2.new(1, 0, 0, 44),
			17,
			Ui.Colour.Muted
		)
	end
	local row = actionRow()
	Ui.button(row, "Move", "Move", UDim2.fromOffset(110, 46), function()
		startMoving(id, rec)
	end, Ui.Colour.Teal)
	if piece.kind ~= "Desk" then
		local refund = Economy.refund(rec.paid or 0)
		for _, d in build().decor or {} do
			if tostring(d.room) == tostring(id) then
				refund += Economy.refund(d.paid or 0)
			end
		end
		Ui.button(row, "Sell", `Sell +{Format.cash(refund)}`, UDim2.fromOffset(160, 46), function()
			Net.send("Sell", id)
			menu.Visible = false
		end, Ui.Colour.Bad)
	end
	if piece.kind == "Room" or piece.kind == "Amenity" then
		Ui.label(menuBody, "FloorTitle", "Its floor", UDim2.new(1, 0, 0, 24), 18, Ui.Colour.Muted)
		finishRow(rec.finish or "", function(f)
			Net.send("Finish", tostring(id), f)
			menu.Visible = false
		end)
	end
	menu.Visible = true
end

local function openDecorMenu(id: number)
	local rec = decorRecord(id)
	local d = rec and Pieces.decor(rec.item)
	if not rec or not d then
		return
	end
	clearMenu(d.name)
	local where = if rec.room ~= ""
		then "In a room: it counts toward the room's tier and tags."
		else "On the hallway floor."
	local tags = if #d.tags > 0 then table.concat(d.tags, ", ") else "no tags"
	Ui.label(menuBody, "About", `{tags} · {where}`, UDim2.new(1, 0, 0, 44), 17, Ui.Colour.Muted)
	local row = actionRow()
	Ui.button(row, "Move", "Move", UDim2.fromOffset(110, 46), function()
		movingDecor = id
		moving = nil
		selected, selectedDecor, selectedFinish = nil, nil, nil
		rotation = rec.r
		floor = rec.floor
		menu.Visible = false
		floorLabel.Text = `Floor {floor}`
		setHidden()
		updateCamera()
		info.Text = moveHint()
		toPlot()
	end, Ui.Colour.Teal)
	Ui.button(
		row,
		"Sell",
		`Sell +{Format.cash(Economy.refund(rec.paid or 0))}`,
		UDim2.fromOffset(160, 46),
		function()
			Net.send("SellDecor", id)
			menu.Visible = false
		end,
		Ui.Colour.Bad
	)
	menu.Visible = true
end

local function openAreaMenu(index: number)
	local b = build()
	local owned = {}
	for _, i in b.areas or {} do
		owned[i] = true
	end
	local can, why = Grid.canBuyArea(owned, index)
	clearMenu("An area of the plot")
	Ui.label(
		menuBody,
		"About",
		"Buy it to build rooms on it, on every floor at once.",
		UDim2.new(1, 0, 0, 44),
		17,
		Ui.Colour.Muted
	)
	local row = actionRow()
	if can and b.areaCost then
		Ui.button(row, "Buy", `Buy {Format.cash(b.areaCost)}`, UDim2.fromOffset(180, 46), function()
			Net.send("BuyArea", index)
			menu.Visible = false
		end, Ui.Colour.Good)
	else
		Ui.label(
			row,
			"Why",
			Hud.refusal(why or "NotNext"),
			UDim2.fromOffset(320, 46),
			18,
			Ui.Colour.Bad
		)
	end
	menu.Visible = true
end

-- ===== Traps (§8.1): the forecourt's three trap slots (§5.4) =====

local function openTraps()
	clearMenu("Forecourt traps")
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
	clearMenu("Hotel style")
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

-- ===== The strip of cards =====

-- Stops placing or moving: the ghost goes, and a tap opens a piece's menu again.
function stopPlacing()
	selected, selectedDecor, selectedFinish = nil, nil, nil
	moving, movingDecor = nil, nil
	clearGhost()
	placeButton.Visible = false
	info.Text = idleHint()
	redrawCards()
end

local function card(
	name: string,
	text: string,
	order: number,
	chosen: boolean,
	can: boolean,
	onTap: () -> ()
)
	local c = Ui.button(
		cards,
		name,
		text,
		UDim2.fromOffset(150, 70),
		onTap,
		if chosen then Ui.Colour.Pumpkin elseif can then Ui.Colour.PanelLight else Ui.Colour.Ink
	)
	c.LayoutOrder = order
	c.TextSize = 16
	-- The gamepad (§11): up from a card is its tab, not the HUD beside the strip.
	c.NextSelectionUp =
		tools:FindFirstChild(if tab == "Room" then "Rooms" else tab, true) :: GuiObject?
end

-- The card the gamepad selects: the chosen one, else the first.
local function firstCard(): GuiObject?
	local name = selected
		or selectedDecor
		or (if selectedFinish ~= nil then `Finish_{selectedFinish}` else nil)
	local chosen = name and cards:FindFirstChild(name)
	if chosen and chosen:IsA("GuiButton") then
		return chosen
	end
	local best: GuiButton? = nil
	for _, c in cards:GetChildren() do
		if c:IsA("GuiButton") and (not best or c.LayoutOrder < best.LayoutOrder) then
			best = c
		end
	end
	return best
end

function redrawCards()
	for _, c in cards:GetChildren() do
		if c:IsA("GuiButton") then
			c:Destroy()
		end
	end
	local b = build()
	if tab == "Decor" then
		for i, d in Pieces.DecorList do
			if (b.unlockedDecor or {})[d.id] then
				local text = `{d.name}\n{d.w}×{d.d} · {if d.cost > 0
					then Format.cash(d.cost)
					else "owned"}`
				card(d.id, text, i, selectedDecor == d.id, true, function()
					if selectedDecor == d.id then
						stopPlacing()
						return
					end
					stopPlacing()
					selectedDecor = d.id
					showHover(nil)
					info.Text = `{d.name}: {Controls.hint(
						"tap a room or a hallway · tap the card again to stop",
						"A in a room or a hallway · B to stop"
					)}`
					redrawCards()
					drawGhost()
					toPlot()
				end)
			end
		end
	elseif tab == "Floor" then
		local function finishCard(id: string, name: string, order: number)
			card(`Finish_{id}`, name, order, selectedFinish == id, true, function()
				if selectedFinish == id then
					stopPlacing()
					return
				end
				stopPlacing()
				selectedFinish = id
				info.Text = `{name}: {Controls.hint(
					"tap a room, the lobby or a hallway to lay it",
					"A on a room, the lobby or a hallway to lay it"
				)}`
				redrawCards()
				toPlot()
			end)
		end
		finishCard("", "Its own floor", 0)
		for i, f in Pieces.Finishes do
			if f.location == b.location then
				finishCard(f.id, f.name, i)
			end
		end
	else
		for i, p in Pieces.List do
			local shown = if tab == "Stairs" then p.kind == "Stairs" else p.kind == tab
			if
				shown and (p.location == b.location or p.location == 0 or b.buildable[p.id] == true)
			then
				local can = b.buildable[p.id] == true
				local cost = b.costs[p.id] or p.cost
				local text =
					`{p.name}\n{p.w}×{p.d} · {if cost == 0 then "free" else Format.cash(cost)}`
				if not can then
					text = `{p.name}\n🔒 {b.buildable[p.id]}`
				end
				card(p.id, text, i, selected == p.id, can, function()
					if not can then
						Hud.toast(`{p.name}: {b.buildable[p.id]}`, Ui.Colour.Bad)
						return
					end
					-- Tapping the chosen card again puts it down.
					if selected == p.id then
						stopPlacing()
						return
					end
					stopPlacing()
					selected = p.id
					showHover(nil)
					info.Text = `{p.name}: {Controls.hint(
						"tap the grid · tap the card again to stop",
						"A on the plot · B to stop"
					)}`
					redrawCards()
					drawGhost()
					toPlot()
				end)
			end
		end
	end
	floorLabel.Text = `Floor {floor}/{b.floors}`
	local buy = tools:FindFirstChild("BuyFloor", true) :: TextButton?
	if buy then
		buy.Visible = b.floors < b.maxFloors
		buy.Text = if b.floorCost then `+ Floor {Format.cash(b.floorCost)}` else "+ Floor"
	end
	local stairsTab = tools:FindFirstChild("Stairs", true) :: TextButton?
	if stairsTab then
		stairsTab.Text = if (b.freeStairs or 0) > 0
			then `Stairs ({b.freeStairs} free)`
			else "Stairs"
	end
	-- The gamepad (§11): down from the tools' last row is the cards, far below them.
	local first = firstCard()
	for _, name in { "Traps", "Style", "Done" } do
		local t = tools:FindFirstChild(name, true)
		if t and t:IsA("GuiObject") then
			t.NextSelectionDown = first
		end
	end
end

-- With nothing selected, the gamepad's stick, A and D-pad act on the plot.
local function updatePad()
	padKeys.Enabled = active and GuiService.SelectedObject == nil
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
	selected, selectedDecor, selectedFinish = nil, nil, nil
	moving, movingDecor, cell = nil, nil, nil
	clearGhost()
	showHover(nil)
	buildKeys.Enabled = on
	updatePad()
	hidePadMarker()
	if on then
		floor = 1
		updateCamera()
		redrawCards()
		local size = G.Cells * G.CellSize
		pad = Vector3.new(size / 2, 0, size / 2)
		-- The gamepad opens on the cards (§11).
		if Controls.gamepad() then
			task.defer(function()
				if active then
					Controls.select(
						firstCard() or tools:FindFirstChild("Rooms", true) :: GuiObject?
					)
				end
			end)
		end
	else
		local sel = GuiService.SelectedObject
		if sel and sel:IsDescendantOf(gui) then
			Controls.select(nil)
		end
		camera.CameraType = Enum.CameraType.Custom
		local character = me.Character
		local hum = character and character:FindFirstChildOfClass("Humanoid")
		if hum then
			camera.CameraSubject = hum
		end
	end
	setHidden()
	drawAreaLabels()
end

function BuildController.isActive(): boolean
	return active
end

function BuildController.open()
	setActive(true)
end

-- A tap on the plot with no card chosen, or with a floor finish chosen.
local function tapPlot(x: number, y: number)
	local id, kind = underPointer(x, y)
	if selectedFinish then
		local f = selectedFinish :: string
		if id and kind == "Piece" then
			local rec = record(id)
			local piece = rec and Pieces.get(rec.item)
			if piece and (piece.kind == "Room" or piece.kind == "Amenity") then
				Net.send("Finish", tostring(id), f)
				return
			end
		end
		local l = pointerLocal(x, y)
		if l then
			local z = math.floor(l.Z / G.CellSize)
			Net.send("Finish", if floor == 1 and Grid.isLobbyRow(z) then "Lobby" else "Hallway", f)
		end
		return
	end
	if id and kind == "Decor" then
		openDecorMenu(id)
		return
	elseif id then
		openMenu(id)
		return
	end
	local l = pointerLocal(x, y)
	if l then
		local area = Grid.areaOf(math.floor(l.X / G.CellSize), math.floor(l.Z / G.CellSize))
		local owned = false
		for _, i in build().areas or {} do
			if i == area then
				owned = true
			end
		end
		if area and not owned then
			openAreaMenu(area)
		end
	end
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
	info = Ui.label(strip, "Info", idleHint(), UDim2.new(1, -24, 0, 26), 18, Ui.Colour.Gold)
	info.Position = UDim2.fromOffset(12, 4)
	cards = Ui.scroll(strip, "Cards", UDim2.new(1, -24, 0, 86), UDim2.fromOffset(12, 36), true)
	Ui.list(cards, Enum.FillDirection.Horizontal, 8)

	-- The tools, top-left where the HUD's menu column is while not building
	-- (hidden meanwhile), above a phone's thumbstick (§11). One row per group,
	-- each group its own colour (his report, 2026-10-19: "the same colour on
	-- nearly all, group them better"): what to build, which floor, the camera
	-- and placing, the extras and leaving.
	tools = Ui.frame(gui, "Tools", UDim2.fromOffset(380, 260), UDim2.fromOffset(10, 56))
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

	-- What to build: the open tab lit, as the cards are. Two rows of tabs.
	local tabs: { [string]: TextButton } = {}
	function paintTabs()
		for name, b in tabs do
			b.BackgroundColor3 = if tab == name then Ui.Colour.Pumpkin else Ui.Colour.Panel
		end
	end
	local function tabButton(parent: Frame, name: string, text: string, width: number)
		tabs[name] = tool(parent, if name == "Room" then "Rooms" else name, text, width, function()
			tab = name
			stopPlacing()
			paintTabs()
		end)
	end
	local what = row()
	tabButton(what, "Room", "Rooms", 114)
	tabButton(what, "Amenity", "Amenities", 114)
	tabButton(what, "Stairs", "Stairs", 140)
	local what2 = row()
	tabButton(what2, "Decor", "Decor", 114)
	tabButton(what2, "Floor", "Floors", 114)
	paintTabs()

	-- Which floor: down, the floor, up, and buying the next.
	local floors = row()
	function toFloor(f: number)
		floor = math.clamp(f, 1, build().floors)
		redrawCards()
		setHidden()
		updateCamera()
		drawGhost()
		drawAreaLabels()
	end
	tool(floors, "Down", "▼", 50, function()
		toFloor(floor - 1)
	end, FLOOR_BLUE)
	floorLabel = Ui.label(floors, "FloorLabel", "Floor 1", UDim2.fromOffset(90, 44), 18)
	floorLabel.LayoutOrder = 2
	floorLabel.TextXAlignment = Enum.TextXAlignment.Center
	tool(floors, "Up", "▲", 50, function()
		toFloor(floor + 1)
	end, FLOOR_BLUE)
	tool(floors, "BuyFloor", "+ Floor", 150, function()
		Net.send("BuyFloor")
	end, Ui.Colour.Teal)

	-- The camera and placing.
	local placingRow = row()
	tool(placingRow, "Rotate", "⟳ Rotate", 114, function()
		rotation = (rotation + 1) % 4
		drawGhost()
	end)
	-- A quarter turn (`dir` 1 or -1), to the next side square on.
	function turnQuarter(dir: number)
		yaw = (math.floor(yaw / (math.pi / 2) + 0.5) + dir) * math.pi / 2
		updateCamera()
	end
	tool(placingRow, "Turn", "↻ View", 114, function()
		turnQuarter(1)
	end)
	placeButton = tool(placingRow, "Place", "✔ Place", 114, place, Ui.Colour.Good)
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

	-- The keys and the gamepad (§11, `Controls`): above the HUD's keys (B, R)
	-- and the avatar's controls (the left stick, A), which they take while building.
	buildKeys = Controls.context("BuildKeys", 2000, true, false)
	Controls.press(buildKeys, "Rotate", { Enum.KeyCode.R, Enum.KeyCode.ButtonR1 }, function()
		rotation = (rotation + 1) % 4
		drawGhost()
	end)
	-- B opens build mode from the HUD (Hud's KEYS) and closes it here.
	Controls.press(buildKeys, "Leave", { Enum.KeyCode.B }, function()
		setActive(false)
	end)
	cameraAction = Controls.direction(
		buildKeys,
		"Camera",
		Enum.KeyCode.Thumbstick2,
		{ Left = Enum.KeyCode.Comma, Right = Enum.KeyCode.Period }
	)
	padKeys = Controls.context("BuildPad", 2000, true, false)
	cursorAction = Controls.direction(padKeys, "Cursor", Enum.KeyCode.Thumbstick1)
	-- A: what a click does where the cursor is.
	Controls.press(padKeys, "Act", { Enum.KeyCode.ButtonA }, function()
		local s = padScreen()
		if not active or not s or Controls.selectedRecently() then
			return
		end
		if placing() then
			local c = screenToAnchor(s.X, s.Y)
			if c then
				cell = c
				drawGhost()
				if placeButton.Visible then
					place()
				end
			end
		else
			tapPlot(s.X, s.Y)
		end
	end)
	Controls.press(padKeys, "FloorUp", { Enum.KeyCode.DPadUp }, function()
		toFloor(floor + 1)
		padRefresh(true)
	end)
	Controls.press(padKeys, "FloorDown", { Enum.KeyCode.DPadDown }, function()
		toFloor(floor - 1)
		padRefresh(true)
	end)
	Controls.press(padKeys, "ViewLeft", { Enum.KeyCode.DPadLeft }, function()
		turnQuarter(-1)
	end)
	Controls.press(padKeys, "ViewRight", { Enum.KeyCode.DPadRight }, function()
		turnQuarter(1)
	end)
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
			drawAreaLabels()
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
	-- The , and . keys and the right stick (`cameraAction`): its X turns, its Y zooms
	-- (up is in); the left stick moves the gamepad's cursor while nothing is selected.
	RunService.RenderStepped:Connect(function(dt)
		if not active then
			return
		end
		local look = Controls.read(cameraAction)
		if look.X ~= 0 then
			turnBy(look.X * dt * 1.5)
		end
		if look.Y ~= 0 then
			zoomBy(1 - look.Y * dt * 1.2)
		end
		local move = if padKeys.Enabled then Controls.read(cursorAction) else Vector2.zero
		if move ~= Vector2.zero then
			movePad(move, dt)
		elseif not Controls.gamepad() then
			hidePadMarker()
		end
	end)
	GuiService:GetPropertyChangedSignal("SelectedObject"):Connect(updatePad)
	-- ButtonY (Controls' menu) in build mode: the cards, else the open tab.
	Controls.onMenu(function()
		if not active then
			return false
		end
		Controls.select(
			firstCard()
				or tools:FindFirstChild(if tab == "Room" then "Rooms" else tab, true) :: GuiObject?
		)
		return true
	end)
	-- ButtonB with no panel open: stop placing, else leave the cards, else leave build mode.
	Controls.onBack(function()
		if not active then
			return false
		end
		if selected or selectedDecor or selectedFinish or moving or movingDecor then
			stopPlacing()
			padRefresh()
		elseif Controls.selectedRecently() then
			Controls.select(nil)
			padRefresh()
		else
			setActive(false)
		end
		return true
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
		-- With nothing being placed, what is under the mouse lights up: it can be tapped.
		if input.UserInputType == Enum.UserInputType.MouseMovement and not placing() then
			showHover(underPointer(input.Position.X, input.Position.Y))
		end
		if input.UserInputType == Enum.UserInputType.MouseMovement and placing() then
			local c = screenToAnchor(input.Position.X, input.Position.Y)
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
		elseif
			input.UserInputType == Enum.UserInputType.MouseButton1
			or input.UserInputType == Enum.UserInputType.Touch
		then
			local pos = input.Position
			if overUi(pos.X, pos.Y) then
				return
			end
			if placing() then
				local c = screenToAnchor(pos.X, pos.Y)
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
				tapPlot(pos.X, pos.Y)
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
		if
			down
			and (at - down).Magnitude < 6
			and (selected or selectedDecor or selectedFinish or moving or movingDecor)
		then
			stopPlacing()
		end
	end)
	RunService.RenderStepped:Connect(function()
		if active and camera.CameraType ~= Enum.CameraType.Scriptable then
			updateCamera()
		end
	end)
	-- A rebuilt hotel (a new floor, an area, a stair) makes new parts: hide them again.
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
