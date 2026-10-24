--!strict
--[[
	Build mode (GDD §5, §5.4, §13.2 "Building": the client draws the ghost,
	snaps and rotates; the server validates). The client sends only an intent
	(`{item, floor, cell, rotation}`, squares for decor and furniture, half
	edges for walls); `Grid`, `Rooms` and `Layout` run here too, on the
	state's copy of the hotel, so the ghost turns red before the server would
	refuse.

	One thumb (§11): tap a card, tap the grid to put the ghost there, press
	Place. With a mouse, the ghost follows the cursor and a click places; R
	rotates. With nothing chosen, tapping a stair, a desk or a piece of decor
	opens its menu (move, sell), tapping a built room opens the room view,
	tapping a walled space with a door opens the type list, and tapping a gold
	tile beside the hotel buys it (§5.4, A.1).

	BUILT ROOMS (§5.4, A.12, his rulings 2026-10-21): the Walls tab draws inner
	walls along the cell edges, or the half cells with its "Half cells"
	toggle: a tap puts up one edge, a drag a straight run (`WallRun`); Door
	puts a door in a wall or takes it out (`Door`); Remove takes walls down. A
	tap on an enclosed area with a door lists the location's room types and
	amenities, each with its tooltip (who stays in it or what it gives, its
	key furniture, its minimum and full size; locked ones with their unlock),
	and choosing one makes it that room (`MakeRoom`). The Furniture tab
	places furniture like decor. Tapping a room flies the camera into it (the
	room view): the walls toward the camera fade, and a panel shows its type,
	its tooltip, whether it is ready (or what it lacks) and its three bars
	(Size, Furniture, Decor) with what each gives. No ready-made rooms, no
	Flip.

	Tabs: Walls, Rooms (the rooms built; a tap on one is its view), Furniture,
	Decor (on a grid of 3-stud squares, in rooms and on hallway floor), Stairs
	and desks, Floors (a finish: choose one, then tap a room or a hallway) and
	Windows (A.1).

	The camera is free (his ruling 2026-10-21), and floors above the one being
	built on are hidden locally (`LocalTransparencyModifier`).

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
local Contracts = require(ReplicatedStorage.Shared.Contracts)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Format = require(ReplicatedStorage.Shared.Format)
local Grid = require(ReplicatedStorage.Shared.Grid)
local Layout = require(ReplicatedStorage.Shared.Layout)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Rooms = require(ReplicatedStorage.Shared.Rooms)
local Species = require(ReplicatedStorage.Shared.Species)
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
-- Built rooms (A.12): the Walls tab's tool ("Wall", "Door", "Remove"), its step, a drag's start.
local wallMode: string? = nil
local halfCells = false
local wallFrom: Vector3? = nil -- the drag's start vertex, in half-cell units (x, 0, z)
local wallGhost: Folder? = nil
local roomView: number? = nil -- the room in the room view
local openRoomView: (number) -> ()
local closeRoomView: () -> ()
local clearWallGhost: () -> ()
local typesWindow: Frame
local selected: string? = nil -- a piece id to place
local selectedDecor: string? = nil -- a decor id to place
local selectedFinish: string? = nil -- a finish to lay ("" the model's own)
local selectedWindow: string? = nil -- a window type to put on a wall (A.1)
local movingWindow: string? = nil -- a placed window being moved, by its wall's edge key
local moving: number? = nil -- a built piece being moved
local movingDecor: number? = nil -- a piece of decor being moved
local cell: Grid.Cell? = nil -- where the ghost's anchor is: a cell, or a square for decor
local yaw = 0 -- which way round the camera looks, radians (0: from the street)
local zoom = 1 -- the camera's distance, 1 = the whole plot in view
--[[ The free camera (GDD §5.4, his ruling 2026-10-21: "it shouldnt center
	around the midpoint of the plot"): it looks at `focus`, a plot-local
	point kept inside the hotel's owned area, from `pitch` above the level
	(top view to nearly level). ]]
local DEFAULT_PITCH = math.atan2(0.86, 0.7) -- the old fixed angle, 51°
local PITCH_MIN, PITCH_MAX = math.rad(12), math.rad(89)
local pitch = DEFAULT_PITCH
local focus: Vector3? = nil -- plot-local (x, 0, z); nil until the camera first moves: the plot's middle

local gui: ScreenGui
local strip: Frame
local cards: ScrollingFrame
local info: TextLabel
local tools: ScrollingFrame
local floorLabel: TextLabel
local placeButton: TextButton
local menu: Frame
local menuBody: Frame
local tab = "Wall"
-- Each tab's button name (UI.md "Build mode").
local tabNames: { [string]: string } = { Wall = "Walls", Room = "Rooms" }
local paintTabs: () -> ()
-- What the strip says while nothing is being placed: that a placed piece is
-- tapped to change it (his report, 2026-10-19: no way to remove or replace a room).
local function idleHint(): string
	if tab == "Room" then
		return Controls.hint(
			"Tap a walled space with a door to choose its type, or a room to see it",
			"A on a walled space or a room"
		)
	end
	return Controls.hint(
		"Choose something to build, tap a room or decor, or a gold tile to buy it",
		"Y for the cards, or A on a room, decor or a gold tile"
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
local outline: (Instance?) -> ()
local stopPlacing: () -> ()
local rightDownAt: Vector2? = nil
local rightDragX: number? = nil -- the cursor's last x in a right-drag
local rightDragY: number? = nil -- and its last y: the drag tilts the camera too
local redrawCards: () -> ()
local chooseDecor: (Pieces.Decor) -> ()
local FOUND_GOLD = Color3.fromRGB(150, 110, 40) -- a found rare piece's card (A.11.3)
local ghost: Model? = nil
local hidden: { [BasePart]: boolean } = {}
local tilePlates: { [number]: BasePart } = {} -- the buyable tiles' plates, by Grid.tileKey
local tileFolder: Folder? = nil
local tileDrawn: string? = nil -- what the plates were drawn for: the floor, the price, the tiles
local litTile: number? = nil

-- The gamepad (§11): a cursor on the plot in place of the pointer.
local pad: Vector3? = nil -- plot-local, on the floor in view
local padMarker: BasePart? = nil
-- The plot's width the cursor crosses in a second at full zoom.
local PAD_SPEED = 0.45
local buildKeys: InputContext -- while building: rotate, leave, the camera
local padKeys: InputContext -- while building with nothing selected: the cursor, A, the D-pad
local cursorAction: InputAction
local cameraAction: InputAction
local panAction: InputAction -- W/S A/D move the free camera (GDD §5.4)
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
			tiles = {},
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
	local tiles = {}
	for _, k in b.tiles or {} do
		tiles[k] = true
	end
	if next(tiles) == nil then
		for _, c in Grid.startTiles() do
			tiles[Grid.tileKey(1, c.x, c.z)] = true
		end
	end
	return Layout.world(b.floors, tiles, b.layout, b.decor or {}, b.walls or {}, b.rooms or {})
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

-- The hotel's area, plot-local: the owned tiles' bounds on every floor, a cell round them.
local function hotelBounds(): (Vector3, Vector3)
	local cs = G.CellSize
	local lo, hi = Vector3.new(math.huge, 0, math.huge), Vector3.new(-math.huge, 0, -math.huge)
	for _, k in build().tiles or {} do
		local t = Grid.tileOf(tonumber(k) or 0)
		lo = Vector3.new(math.min(lo.X, t.x * cs), 0, math.min(lo.Z, t.z * cs))
		hi = Vector3.new(math.max(hi.X, (t.x + 1) * cs), 0, math.max(hi.Z, (t.z + 1) * cs))
	end
	local size = G.Cells * cs
	if lo.X > hi.X then
		return Vector3.zero, Vector3.new(size, 0, size)
	end
	return Vector3.new(math.max(lo.X - cs, 0), 0, math.max(lo.Z - cs, 0)),
		Vector3.new(math.min(hi.X + cs, size), 0, math.min(hi.Z + cs, size))
end

local function updateCamera()
	local frame = plotFrame()
	if not frame or not active then
		return
	end
	local size = G.Cells * G.CellSize
	local lo, hi = hotelBounds()
	local f = focus or (lo + hi) / 2
	f = Vector3.new(math.clamp(f.X, lo.X, hi.X), 0, math.clamp(f.Z, lo.Z, hi.Z))
	focus = f
	local centre = frame:PointToWorldSpace(Vector3.new(f.X, Grid.floorY(floor), f.Z))
	local back = frame:VectorToWorldSpace(Vector3.new(math.sin(yaw), 0, -math.cos(yaw)))
	camera.CameraType = Enum.CameraType.Scriptable
	-- At zoom 1 and the old angle the whole plot is in view, as before:
	-- the distance grows with the plot.
	local dist = size * 1.109 * zoom
	camera.CFrame = CFrame.lookAt(
		centre + back * (dist * math.cos(pitch)) + Vector3.new(0, dist * math.sin(pitch), 0),
		centre
	)
end

-- Moves the free camera's focus by `v` (x right, y forward on the screen), in studs.
local function panBy(v: Vector2)
	local frame = plotFrame()
	if not frame then
		return
	end
	local look = camera.CFrame.LookVector
	local fwd = Vector3.new(look.X, 0, look.Z)
	if fwd.Magnitude < 1e-3 then
		fwd = Vector3.new(camera.CFrame.UpVector.X, 0, camera.CFrame.UpVector.Z) -- straight down
	end
	fwd = fwd.Unit
	local right = fwd:Cross(Vector3.yAxis)
	local move = right * v.X + fwd * v.Y
	local size = G.Cells * G.CellSize
	focus = (focus or Vector3.new(size / 2, 0, size / 2)) + frame:VectorToObjectSpace(move)
	updateCamera()
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

-- ===== The tiles for sale (§5.4, A.1) =====

local function clearTiles()
	if tileFolder then
		tileFolder:Destroy()
		tileFolder = nil
	end
	table.clear(tilePlates)
	tileDrawn = nil
	litTile = nil
end

local TILE_DIM, TILE_LIT = 0.6, 0.25

--[[ A gold plate with its price over each tile that can be bought now on the
	floor in view (one sharing an edge with an owned one there; upstairs, over
	an owned tile below): a tap buys it for that floor (A.1). Drawn locally, only while building, and again
	only when the floor, the price or the tiles change (the state changes
	every second). ]]
local function drawTiles()
	local frame = plotFrame()
	if not active or not frame then
		clearTiles()
		return
	end
	local b = build()
	local keys = table.clone(b.tiles or {})
	table.sort(keys)
	local cost = (b.tileCosts or {})[floor]
	local drawn = `{floor}|{cost}|{table.concat(keys, ",")}`
	if drawn == tileDrawn and tileFolder then
		return
	end
	clearTiles()
	tileDrawn = drawn
	local folder = Instance.new("Folder")
	folder.Name = "BuildTiles"
	local price = if cost then Format.cash(cost) else ""
	for _, c in Grid.buyable(world().tiles, b.floors, floor) do
		local plate = Instance.new("Part")
		plate.Name = "TileForSale"
		plate.Anchored = true
		plate.CanCollide = false
		plate.CanQuery = false
		plate.CanTouch = false
		plate.CastShadow = false
		plate.Material = Enum.Material.SmoothPlastic
		plate.Color = Ui.Colour.Gold
		plate.Transparency = TILE_DIM
		plate.Size = Vector3.new(G.CellSize - 1, 0.2, G.CellSize - 1)
		plate.CFrame = frame * CFrame.new(Grid.cellCentre(floor, c) + Vector3.new(0, 0.15, 0))
		local face = Instance.new("SurfaceGui")
		face.Face = Enum.NormalId.Top
		face.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		face.PixelsPerStud = 20
		face.LightInfluence = 0
		local text = Ui.label(face, "Price", `+ {price}`, UDim2.fromScale(1, 1), 40, Ui.Colour.Text)
		text.TextXAlignment = Enum.TextXAlignment.Center
		text.TextStrokeTransparency = 0.3
		face.Parent = plate
		plate.Parent = folder
		tilePlates[Grid.tileKey(floor, c.x, c.z)] = plate
	end
	folder.Parent = workspace
	tileFolder = folder
end

-- The cell under the pointer on the floor in view, or nil off the plot.
local pointerLocal: (number, number) -> Vector3?
local judgeDoor: (number, number) -> (string?, boolean, boolean, string?)
local fitTools: () -> ()
local showDoor: (number, number) -> ()
local function cellUnder(x: number, y: number): Grid.Cell?
	local l = pointerLocal(x, y)
	if not l then
		return nil
	end
	local c = { x = math.floor(l.X / G.CellSize), z = math.floor(l.Z / G.CellSize) }
	return if Grid.inBounds(c.x, c.z) then c else nil
end

-- Lights the tile for sale under the pointer, if any.
local function lightTile(x: number, y: number)
	local c = cellUnder(x, y)
	local k = if c then Grid.tileKey(floor, c.x, c.z) else nil
	if k == litTile then
		return
	end
	local old = litTile and tilePlates[litTile]
	if old then
		old.Transparency = TILE_DIM
	end
	litTile = if k and tilePlates[k] then k else nil
	local now = litTile and tilePlates[litTile]
	if now then
		now.Transparency = TILE_LIT
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
		ok, why = Rooms.canPlacePiece(w :: any, candidate, skip)
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
		candidate.id = if movingDecor then tostring(movingDecor) else nil
		ok, why = Rooms.canPlaceDecor(w :: any, candidate, candidate.id)
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
function pointerLocal(x: number, y: number): Vector3?
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

--[[ The facade wall section (a `Facade` model with `Edge`) on the floor in
	view under the pointer, or nil; with `piecesFirst` a piece or decor in
	front of it wins (nil). `windowsOnly` takes only walls with a window. ]]
local function wallUnder(x: number, y: number, piecesFirst: boolean, windowsOnly: boolean?): Model?
	local m = plotModel()
	local facade = m and m:FindFirstChild("Facade")
	if not m or not facade then
		return nil
	end
	local include: { Instance } = {}
	for _, w in facade:GetChildren() do
		if
			w:IsA("Model")
			and w:GetAttribute("Edge")
			and w:GetAttribute("Floor") == floor
			and (not windowsOnly or w:GetAttribute("Window"))
		then
			table.insert(include, w)
		end
	end
	if piecesFirst then
		for _, name in { "Pieces", "Decor" } do
			local f = m:FindFirstChild(name)
			if f then
				table.insert(include, f)
			end
		end
	end
	local ray = camera:ScreenPointToRay(x, y)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = include
	local hit = workspace:Raycast(ray.Origin, ray.Direction * 400, params)
	local inst = hit and hit.Instance
	while inst and inst ~= facade and inst ~= m do
		if inst:IsA("Model") and inst:GetAttribute("Edge") then
			return inst
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
	outline(target)
end

-- Outlines a model (nil: none) in gold.
function outline(target: Instance?)
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
	lightTile(s.X, s.Y)
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

local function startMoving(id: number, rec: any)
	moving = id
	movingDecor = nil
	selected, selectedDecor, selectedFinish, selectedWindow, movingWindow = nil, nil, nil, nil, nil
	rotation = rec.r
	floor = rec.floor
	menu.Visible = false
	floorLabel.Text = `Floor {floor}`
	setHidden()
	updateCamera()
	drawTiles()
	info.Text = moveHint()
	toPlot()
end

local function openMenu(id: number)
	local rec = record(id)
	local piece = rec and Pieces.get(rec.item)
	if not rec or not piece then
		return
	end
	clearMenu(piece.name)
	if piece.kind == "Stairs" then
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
			"Guests queue in front of it, at the desk with the shortest line. Put desks anywhere on floor 1 the guests can reach.",
			UDim2.new(1, 0, 0, 44),
			17,
			Ui.Colour.Muted
		)
	end
	local row = actionRow()
	Ui.button(row, "Move", "Move", UDim2.fromOffset(110, 46), function()
		startMoving(id, rec)
	end, Ui.Colour.Teal)
	Ui.button(
		row,
		"Sell",
		`Sell +{Format.cash(Economy.refund(rec.paid or 0))}`,
		UDim2.fromOffset(160, 46),
		function()
			Net.send("Sell", id)
			menu.Visible = false
		end,
		Ui.Colour.Bad
	)
	menu.Visible = true
end

-- A placed window (A.1): move it, swap it for another type, or sell it.
local function openWindowMenu(edge: string)
	local w = nil
	for _, rec in build().windows or {} do
		if rec.edge == edge then
			w = rec
		end
	end
	if not w then
		return
	end
	local W = Constants.Windows
	clearMenu(`{W.Names[w.type] or w.type} window`)
	local row = actionRow()
	Ui.button(row, "Move", "Move", UDim2.fromOffset(110, 46), function()
		stopPlacing()
		movingWindow = edge
		menu.Visible = false
		info.Text = Controls.hint(
			"Tap the wall it should go on",
			"A on the wall it should go on · B to stop"
		)
		toPlot()
	end, Ui.Colour.Teal)
	Ui.button(row, "Sell", `Sell +{Format.cash(w.paid or 0)}`, UDim2.fromOffset(160, 46), function()
		Net.send("SellWindow", edge)
		menu.Visible = false
	end, Ui.Colour.Bad)
	Ui.label(menuBody, "SwapTitle", "Another kind", UDim2.new(1, 0, 0, 24), 18, Ui.Colour.Muted)
	local swaps = actionRow()
	for _, kind in W.Types do
		if kind ~= w.type then
			Ui.button(swaps, kind, W.Names[kind], UDim2.fromOffset(120, 44), function()
				Net.send("PlaceWindow", kind, edge)
				menu.Visible = false
			end)
		end
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
	local inRoom = false
	local w: any = world()
	local a = Rooms.areaAt(
		w,
		rec.floor,
		rec.x // (G.Squares // Rooms.HalfCells),
		rec.z // (G.Squares // Rooms.HalfCells)
	)
	inRoom = a ~= nil and not a.hallway and a.room ~= nil
	local where = if inRoom
		then (if d.furniture
			then "In a room: it counts toward the room's Furniture bar and tags."
			else "In a room: it counts toward the room's Decor bar and tags.")
		else "On the hallway floor."
	local tags = if #d.tags > 0 then table.concat(d.tags, ", ") else "no tags"
	Ui.label(menuBody, "About", `{tags} · {where}`, UDim2.new(1, 0, 0, 44), 17, Ui.Colour.Muted)
	local row = actionRow()
	Ui.button(row, "Move", "Move", UDim2.fromOffset(110, 46), function()
		movingDecor = id
		moving = nil
		selected, selectedDecor, selectedFinish, selectedWindow, movingWindow =
			nil, nil, nil, nil, nil
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
	selected, selectedDecor, selectedFinish, selectedWindow, movingWindow = nil, nil, nil, nil, nil
	moving, movingDecor = nil, nil
	wallMode, wallFrom = nil, nil
	if wallGhost then
		wallGhost:Destroy()
		wallGhost = nil
	end
	clearGhost()
	outline(nil)
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
	c.NextSelectionUp = tools:FindFirstChild(tabNames[tab] or tab, true) :: GuiObject?
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

-- A decor card's tap: choose it to place (or, chosen already, stop).
function chooseDecor(d: Pieces.Decor)
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
end

function redrawCards()
	for _, c in cards:GetChildren() do
		if c:IsA("GuiButton") then
			c:Destroy()
		end
	end
	local b = build()
	if tab == "Wall" then
		-- The wall tools (A.12): put up, a door, take down, and the half-cell toggle.
		local tools3 = {
			{ "Wall", `Walls\n{Format.cash(b.wallCost or 5)} a half edge` },
			{ "Door", `Door\n{Format.cash(b.doorCost or 10)} · tap a wall` },
			{ "Remove", "Remove\nwalls" },
		}
		for i, t in tools3 do
			card(`Tool_{t[1]}`, t[2], i, wallMode == t[1], true, function()
				if wallMode == t[1] then
					stopPlacing()
					return
				end
				stopPlacing()
				wallMode = t[1]
				info.Text = if t[1] == "Door"
					then Controls.hint(
						"Point at a wall: the outline shows where the door goes; tap to put it in or take it out",
						"A on a wall"
					)
					else Controls.hint(
						"Tap an edge, or drag along the grid · tap the card again to stop",
						"A on an edge · B to stop"
					)
				redrawCards()
				toPlot()
			end)
		end
		card(
			"HalfCells",
			`Half cells\n{if halfCells then "On" else "Off"}`,
			9,
			halfCells,
			true,
			function()
				halfCells = not halfCells
				redrawCards()
			end
		)
	elseif tab == "Room" then
		-- The rooms built on this floor (A.12): a tap flies to the room's view.
		local list = {}
		for _, rec in b.rooms or {} do
			if rec.floor == floor then
				table.insert(list, rec)
			end
		end
		table.sort(list, function(x, y)
			return x.id < y.id
		end)
		for i, rec in list do
			local p = Pieces.get(rec.type)
			card(
				`Room_{rec.id}`,
				`{if p then p.name else rec.type}\n{if rec.ready then "ready" else rec.missingText}`,
				i,
				roomView == rec.id,
				true,
				function()
					openRoomView(rec.id)
				end
			)
		end
	elseif tab == "Decor" or tab == "Furniture" then
		local furnitureTab = tab == "Furniture"
		local unlocked = b.unlockedDecor or {}
		--[[ The Decor tab's Found cards first (GDD A.11.3, UI.md "Build mode"):
			rare pieces and souvenirs found ("★", gold), then this location's
			set pieces and its species' souvenirs not found yet, as dark cards
			saying where they come from, then the shop. ]]
		if not furnitureTab then
			local finds = State.data.finds or {}
			local found = {}
			for _, id in finds.found or {} do
				found[id] = true
			end
			local need = finds.souvenirMoveIns or 3
			local order = 0
			for _, d in Pieces.DecorList do
				if d.found and unlocked[d.id] then
					order += 1
					card(
						d.id,
						`★ {d.name}\n{d.w}×{d.d} · {Format.cash(d.cost)}`,
						order,
						selectedDecor == d.id,
						true,
						function()
							chooseDecor(d)
						end
					)
					local c = cards:FindFirstChild(d.id) :: TextButton?
					if c and selectedDecor ~= d.id then
						c.BackgroundColor3 = FOUND_GOLD
					end
				end
			end
			for _, d in Pieces.DecorList do
				if d.found and d.location == b.location and not found[d.id] then
					order += 1
					local from = if d.souvenir
						then `move-in no. {need}\nor first VIP`
						else "rare stays,\nHunter Night"
					card(`Unfound_{d.id}`, `? {d.name}\n{from}`, order, false, false, function()
						local sp = d.souvenir and Species.get(d.souvenir)
						info.Text = if sp
							then `{d.name}: found when a {sp.name} moves in for the time no. {need}, or at its first VIP contract`
							else `{d.name}: found on a happy stay of a Rare or rarer guest, or a defended Hunter Night `
								.. `({finds.misses or 0}/{finds.pity or 0} toward a sure find)`
					end)
					local c = cards:FindFirstChild(`Unfound_{d.id}`) :: TextButton?
					if c then
						c.TextColor3 = Ui.Colour.Muted
					end
				end
			end
		end
		for i, d in Pieces.DecorList do
			if unlocked[d.id] and not d.found and (d.furniture == true) == furnitureTab then
				local free = false
				for _, t in d.keyFor or {} do
					if (b.vouchers or {})[t] then
						free = true
					end
				end
				local text = `{d.name}\n{d.w}×{d.d} · {if free
					then "free"
					elseif d.cost > 0 then Format.cash(d.cost)
					else "owned"}`
				card(d.id, text, 1000 + i, selectedDecor == d.id, true, function()
					chooseDecor(d)
				end)
			end
		end
	elseif tab == "Window" then
		local W = Constants.Windows
		for i, kind in W.Types do
			local name = W.Names[kind]
			card(
				`Window_{kind}`,
				`{name}\n{Format.cash(b.windowCost or 0)}`,
				i,
				selectedWindow == kind,
				true,
				function()
					if selectedWindow == kind then
						stopPlacing()
						return
					end
					stopPlacing()
					selectedWindow = kind
					info.Text = `{name} window: {Controls.hint(
						"tap an outer wall · a wall with a window swaps it",
						"A on an outer wall · B to stop"
					)}`
					redrawCards()
					toPlot()
				end
			)
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
					"tap a room or a hallway to lay it",
					"A on a room or a hallway to lay it"
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
			-- The Stairs tab holds the desks (§5.4, A.1: one or more, anywhere on floor 1);
			-- rooms are built from walls now (A.12), never placed.
			local shown = p.kind == "Stairs" or p.kind == "Desk"
			if
				shown
				and (p.location == b.location or p.location == 0 or b.buildable[p.id] == true)
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
			then `Stairs, desks ({b.freeStairs} free)`
			else "Stairs, desks"
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

-- A phone in landscape (Ui's and Hud's rule for a short screen).
local function shortScreen(): boolean
	return camera.ViewportSize.Y < 500
end

--[[ The tools' height: on a short screen they end 8 px above the strip and
	scroll, so no row covers the strip's cards; elsewhere all five rows. ]]
function fitTools()
	if not tools or not strip then
		return
	end
	local height = 260
	if shortScreen() then
		local top = tools.AbsolutePosition.Y
		local stripTop = strip.AbsolutePosition.Y
		if stripTop > top then
			-- Whole rows only (44 high, 10 apart), never a row cut in half.
			local rows = math.clamp(math.floor((stripTop - top - 8 + 10) / 54), 2, 5)
			height = rows * 54 - 10
		end
	end
	tools.Size = UDim2.fromOffset(380, height)
end

local function setActive(on: boolean)
	active = on
	strip.Visible = on
	tools.Visible = on
	fitTools()
	local hud = me.PlayerGui:FindFirstChild("Hud")
	local leftColumn = hud and hud:FindFirstChild("Left")
	if leftColumn and leftColumn:IsA("GuiObject") then
		leftColumn.Visible = not on
	end
	-- On a phone the right menu would lie over the strip too: it steps aside while building.
	local rightColumn = hud and hud:FindFirstChild("Right")
	if rightColumn and rightColumn:IsA("GuiObject") then
		rightColumn.Visible = not (on and shortScreen())
	end
	-- Gloom steps aside while building: the strip says what to do.
	local tutorial = me.PlayerGui:FindFirstChild("Tutorial")
	if tutorial and tutorial:IsA("ScreenGui") then
		tutorial.Enabled = not on
	end
	menu.Visible = false
	typesWindow.Visible = false
	closeRoomView()
	selected, selectedDecor, selectedFinish, selectedWindow, movingWindow = nil, nil, nil, nil, nil
	moving, movingDecor, cell = nil, nil, nil
	wallMode, wallFrom = nil, nil
	clearWallGhost()
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
						firstCard() or tools:FindFirstChild("Walls", true) :: GuiObject?
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
	drawTiles()
end

function BuildController.isActive(): boolean
	return active
end

function BuildController.open()
	setActive(true)
end

-- Build mode open on the Decor tab with this piece chosen to place (a find's pop-up, A.11.3).
function BuildController.placeDecor(id: string)
	local d = Pieces.decor(id)
	if not d then
		return
	end
	if not active then
		setActive(true)
	end
	tab = if d.furniture then "Furniture" else "Decor"
	stopPlacing()
	paintTabs()
	if selectedDecor ~= id then
		chooseDecor(d)
	end
end

-- ===== Built rooms (GDD §5.4, A.12, his rulings 2026-10-21) =====

local HALF = G.CellSize / Rooms.HalfCells -- a half edge, 6 studs

-- A built room of the state, by id.
local function roomRecord(id: number): any
	for _, rec in build().rooms or {} do
		if rec.id == id then
			return rec
		end
	end
	return nil
end

-- The walls' step: a cell edge by default, a half edge with "Half cells" on (his ruling).
local function wallUnit(): number
	return if halfCells then HALF else G.CellSize
end

-- The lattice vertex nearest a plot-local point, in half-cell units.
local function vertexAt(l: Vector3): (number, number)
	local u = wallUnit()
	local k = u // HALF
	return math.round(l.X / u) * k, math.round(l.Z / u) * k
end

--[[ The wall segment nearest a plot-local point, as a run (hx, hz, o,
	count) of half edges: a cell edge (two), or one half edge with `half`. ]]
local function edgeAt(l: Vector3, half: boolean?): (number, number, number, number)
	local u = if half then HALF else wallUnit()
	local k = u // HALF
	local zLine, xLine = math.round(l.Z / u), math.round(l.X / u)
	if math.abs(l.Z - zLine * u) <= math.abs(l.X - xLine * u) then
		return math.floor(l.X / u) * k, zLine * k, 0, k
	end
	return xLine * k, math.floor(l.Z / u) * k, 1, k
end

local function runEdges(hx: number, hz: number, o: number, count: number): { string }
	local out = {}
	for i = 0, count - 1 do
		table.insert(
			out,
			Rooms.edgeKey(floor, hx + (if o == 0 then i else 0), hz + (if o == 1 then i else 0), o)
		)
	end
	return out
end

--[[ Each half edge of a run judged as the server will, one after another on
	the hotel as the run leaves it (`on`: put up; else taken down): whether
	it goes, and the first refusal. ]]
local function judgeRun(edges: { string }, on: boolean): ({ boolean }, string?, number)
	local w: any = world()
	w.walls = table.clone(w.walls)
	local oks, first, built = {}, nil, 0
	for i, e in edges do
		local ok, why
		if on and w.walls[e] then
			ok = true -- standing already: left as it is
		elseif on then
			ok, why = Rooms.canWall(w, e, false)
			if ok then
				w.walls[e] = { paid = 0 }
				built += 1
			end
		else
			ok, why = Rooms.canRemoveWall(w, e)
			if ok then
				w.walls[e] = nil
				built += 1
			end
		end
		oks[i] = ok == true
		if not ok and not first then
			first = why
		end
	end
	return oks, first, built
end

function clearWallGhost()
	if wallGhost then
		wallGhost:Destroy()
		wallGhost = nil
	end
end

-- A ghost of each half edge of the run: green where it goes, red where it is refused.
local function drawWallGhost(edges: { string }, oks: { boolean })
	clearWallGhost()
	local frame = plotFrame()
	if not frame then
		return
	end
	local folder = Instance.new("Folder")
	folder.Name = "WallGhost"
	for i, e in edges do
		local f, hx, hz, o = Rooms.edgeOf(e)
		local p = Instance.new("Part")
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.CastShadow = false
		p.Material = Enum.Material.SmoothPlastic
		p.Transparency = 0.35
		p.Color = if oks[i] then Ui.Colour.Good else Ui.Colour.Bad
		p.Size = Vector3.new(HALF - 0.3, 6, 0.7)
		local at = if o == 0
			then Vector3.new(hx * HALF + HALF / 2, Grid.floorY(f) + 3, hz * HALF)
			else Vector3.new(hx * HALF, Grid.floorY(f) + 3, hz * HALF + HALF / 2)
		p.CFrame = frame * CFrame.new(at) * CFrame.Angles(0, if o == 1 then math.pi / 2 else 0, 0)
		p.Parent = folder
	end
	folder.Parent = workspace
	wallGhost = folder
end

-- What the run under the pointer would do: its ghost and its price or refusal in the strip.
local function showRun(edges: { string })
	local on = wallMode ~= "Remove"
	local oks, why, n = judgeRun(edges, on)
	drawWallGhost(edges, oks)
	local cost = (build().wallCost or 5) * n
	if why and n == 0 then
		info.Text = Hud.refusal(why)
	elseif on then
		info.Text = `{n} wall{if n == 1 then "" else "s"} · {Format.cash(cost)}{if why
			then " (" .. Hud.refusal(why) .. " for some)"
			else ""}`
	else
		info.Text = `Take down {n} wall{if n == 1 then "" else "s"}`
	end
end

--[[ The Door tool (his ruling 2026-10-23): the standing wall the pointer is
	on (`Rooms.wallOnRay`, the first wall the camera's ray meets, never a half
	edge behind it), whether a door goes in (`on`) or comes out, and whether
	the rules allow it. No wall under the pointer: nil. ]]
function judgeDoor(x: number, y: number): (string?, boolean, boolean, string?)
	local frame = plotFrame()
	if not frame then
		return nil, false, false, nil
	end
	local ray = camera:ScreenPointToRay(x, y)
	local w: any = world()
	local e = Rooms.wallOnRay(
		w,
		floor,
		frame:PointToObjectSpace(ray.Origin),
		frame:VectorToObjectSpace(ray.Direction)
	)
	if not e then
		return nil, false, false, "DoorNeedsWall"
	end
	local on = not w.walls[e].door
	local ok, why = Rooms.canDoor(w, e, on)
	return e, on, ok == true, why
end

-- The outline of the doorway on the wall the pointer is on (MODELS.md: Wall_Door's opening, x −2..2, y 0..7.2).
function showDoor(x: number, y: number)
	clearWallGhost()
	local e, on, ok, why = judgeDoor(x, y)
	local frame = plotFrame()
	if not e or not frame then
		info.Text = Hud.refusal(why or "DoorNeedsWall")
		return
	end
	local f, hx, hz, o = Rooms.edgeOf(e)
	local folder = Instance.new("Folder")
	folder.Name = "WallGhost"
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = false, false, false, false
	p.Material = Enum.Material.SmoothPlastic
	p.Transparency = 0.6
	p.Color = if ok then Ui.Colour.Good else Ui.Colour.Bad
	p.Size = Vector3.new(4, 7.2, 0.6)
	local at = if o == 0
		then Vector3.new(hx * HALF + HALF / 2, Grid.floorY(f) + 3.6, hz * HALF)
		else Vector3.new(hx * HALF, Grid.floorY(f) + 3.6, hz * HALF + HALF / 2)
	p.CFrame = frame * CFrame.new(at) * CFrame.Angles(0, if o == 1 then math.pi / 2 else 0, 0)
	local box = Instance.new("SelectionBox")
	box.Adornee = p
	box.Color3 = p.Color
	box.LineThickness = 0.08
	box.Parent = p
	p.Parent = folder
	folder.Parent = workspace
	wallGhost = folder
	info.Text = if not ok
		then Hud.refusal(why or "")
		elseif on then `A door here · {Format.cash(build().doorCost or 10)}`
		else "Wall up this door"
end

-- The run from the drag's start vertex to the pointer's, along the longer axis; nil on the start vertex.
local function dragRun(l: Vector3): (number?, number?, number?, number?)
	local start = wallFrom
	if not start then
		return nil, nil, nil, nil
	end
	local bx, bz = vertexAt(l)
	local ax, az = start.X, start.Z
	if bx == ax and bz == az then
		return nil, nil, nil, nil
	end
	if math.abs(bx - ax) >= math.abs(bz - az) then
		return math.min(ax, bx), az, 0, math.abs(bx - ax)
	end
	return ax, math.min(az, bz), 1, math.abs(bz - az)
end

-- The pointer moved with the wall tool: the run being dragged, or the edge a tap would take.
local function wallHover(x: number, y: number)
	local l = pointerLocal(x, y)
	if not l or not wallMode then
		clearWallGhost()
		return
	end
	if wallMode == "Door" then
		showDoor(x, y)
		return
	end
	local hx, hz, o, count = dragRun(l)
	if not hx then
		hx, hz, o, count = edgeAt(l)
	end
	showRun(runEdges(hx :: number, hz :: number, o :: number, count :: number))
end

-- A tap (or the end of a drag) with the wall tool.
local function wallRelease(x: number, y: number)
	local l = pointerLocal(x, y)
	if not l or not wallMode then
		wallFrom = nil
		return
	end
	if wallMode == "Door" then
		local e, on, ok, why = judgeDoor(x, y)
		if e and ok then
			Net.send("Door", e, on)
		else
			info.Text = Hud.refusal(why or "DoorNeedsWall")
		end
		wallFrom = nil
		return
	end
	local hx, hz, o, count = dragRun(l)
	if not hx then
		hx, hz, o, count = edgeAt(l)
	end
	wallFrom = nil
	Net.send("WallRun", floor, hx, hz, o, count, wallMode ~= "Remove")
end

local function wallPress(x: number, y: number)
	local l = pointerLocal(x, y)
	if not l then
		return
	end
	local vx, vz = vertexAt(l)
	wallFrom = Vector3.new(vx, 0, vz)
end

-- The half cell under the pointer on the floor in view, or nil off the plot.
local function halfCellUnder(x: number, y: number): (number?, number?)
	local l = pointerLocal(x, y)
	if not l then
		return nil, nil
	end
	local hx, hz = math.floor(l.X / HALF), math.floor(l.Z / HALF)
	if hx < 0 or hz < 0 or hx >= Rooms.Size or hz >= Rooms.Size then
		return nil, nil
	end
	return hx, hz
end

-- ===== The type list: an enclosed area's type (A.12, his "you should choose it") =====

local typesBody: Frame
local typeTarget: { floor: number, hx: number, hz: number }? = nil

local function names(ids: { string }, getName: (string) -> string?): string
	local out = {}
	for _, id in ids do
		table.insert(out, getName(id) or id)
	end
	return table.concat(out, ", ")
end

-- A type's tooltip (A.12): who stays in it or what it gives, its key furniture and its sizes.
local function typeTooltip(t: any): string
	local who = if t.kind == "Room"
		then "Stays: " .. (if #t.species > 0
			then names(t.species, function(id)
				local sp = Species.get(id)
				return sp and sp.name
			end)
			else "nobody yet")
		else "Gives: " .. table.concat(t.tags, ", ")
	local keys = names(t.keys, function(id)
		local d = Pieces.decor(id)
		return d and d.name
	end)
	return `{who}\nNeeds: {if keys ~= "" then keys else "nothing"} · at least {t.minCells} cells (full at {t.fullCells})`
end

--[[ Opens the list of types for the area holding half cell (hx, hz): every
	type of the location with its tooltip, the locked ones with their unlock.
	Choosing one makes the area that room (`MakeRoom`), or retypes it. ]]
local function openTypes(f: number, hx: number, hz: number)
	local w: any = world()
	local a = Rooms.areaAt(w, f, hx, hz)
	if not a then
		return
	end
	if a.hallway then
		info.Text = Hud.refusal("Hallway")
		return
	end
	if #a.doors == 0 then
		info.Text = Hud.refusal("NoDoor")
		return
	end
	typeTarget = { floor = f, hx = hx, hz = hz }
	for _, c in typesBody:GetChildren() do
		if c:IsA("GuiObject") then
			c:Destroy()
		end
	end
	local title = typesWindow:FindFirstChild("Title") :: TextLabel
	title.Text = `Choose a type · this space {a.size} cells`
	for i, t in build().types or {} do
		local row = Ui.frame(typesBody, t.id, UDim2.new(1, -8, 0, 84), nil, Ui.Colour.PanelLight)
		row.LayoutOrder = i
		Ui.corner(row, 10)
		local nameLabel =
			Ui.label(row, "Name", t.name, UDim2.new(1, -150, 0, 26), 20, Ui.Colour.Gold)
		nameLabel.Position = UDim2.fromOffset(10, 4)
		local tip =
			Ui.label(row, "Tooltip", typeTooltip(t), UDim2.new(1, -150, 0, 50), 14, Ui.Colour.Muted)
		tip.Position = UDim2.fromOffset(10, 30)
		tip.TextYAlignment = Enum.TextYAlignment.Top
		local small = a.size < t.minCells
		local b = Ui.button(
			row,
			"Choose",
			if t.locked then `🔒 {t.locked}` elseif small then "Choose\n(too small)" else "Choose",
			UDim2.fromOffset(128, 64),
			function()
				if t.locked then
					Hud.toast(`{t.name}: {t.locked}`, Ui.Colour.Bad)
					return
				end
				local target = typeTarget
				if target then
					Net.send("MakeRoom", target.floor, target.hx, target.hz, t.id)
				end
				typesWindow.Visible = false
			end,
			if t.locked then Ui.Colour.Ink elseif small then Ui.Colour.Panel else Ui.Colour.Teal
		)
		b.Position = UDim2.new(1, -138, 0, 10)
		b.TextSize = 15
	end
	menu.Visible = false
	typesWindow.Visible = true
end

-- ===== The room view (A.12: the camera flies in, the near wall fades, the bars) =====

local viewPanel: Frame
local viewScale: UIScale

--[[ Where the room view sits (UI.md "RoomView"): on the right on a tall
	screen; on a short one (a phone in landscape) top-left under the HUD's
	row, scaled to fit, the tools hidden while it is open and the strip moved
	beside it, so the room, the panel and the cards are all in view. ]]
local function layoutView()
	if not viewPanel then
		return
	end
	local h = gui.AbsoluteSize.Y
	local short = h < 500
	local scale = if short then math.clamp((h - 60) / 372, 0.55, 1) else 1
	viewScale.Scale = scale
	if short and roomView then
		tools.Visible = false
		viewPanel.AnchorPoint = Vector2.zero
		viewPanel.Position = UDim2.fromOffset(8, 52)
		strip.AnchorPoint = Vector2.new(0, 1)
		strip.Position = UDim2.new(0, 16 + math.ceil(250 * scale), 1, -8)
	else
		tools.Visible = active
		viewPanel.AnchorPoint = Vector2.new(1, 0.5)
		viewPanel.Position = UDim2.new(1, -10, 0.5, 30)
		strip.AnchorPoint = Vector2.new(0.5, 1)
		strip.Position = UDim2.new(0.5, 0, 1, -8)
	end
end
local faded: { [BasePart]: boolean } = {}
local flight: { from: { Vector3 | number }, to: { Vector3 | number }, t0: number }? = nil
local viewBounds: { lo: Vector3, hi: Vector3 }? = nil
local savedView: { focus: Vector3?, zoom: number, pitch: number }? = nil

local function unfade()
	for p in faded do
		if p.Parent then
			p.LocalTransparencyModifier = 0
		end
	end
	table.clear(faded)
end

--[[ Fades the walls between the camera and the room in view: inner walls,
	doors, posts and facade pieces on its floor whose pivot lies on or inside
	the room's bounds, on the camera's side of its middle. ]]
local function fadeNearWalls()
	local frame = plotFrame()
	local b = viewBounds
	local m = plotModel()
	if not frame or not b or not m or not roomView then
		unfade()
		return
	end
	local centre = (b.lo + b.hi) / 2
	local eye = frame:PointToObjectSpace(camera.CFrame.Position)
	local toEye = Vector3.new(eye.X - centre.X, 0, eye.Z - centre.Z)
	if toEye.Magnitude < 1e-3 then
		unfade()
		return
	end
	toEye = toEye.Unit
	local keep: { [BasePart]: boolean } = {}
	for _, folderName in { "Walls", "Facade" } do
		local f = m:FindFirstChild(folderName)
		for _, w in if f then f:GetChildren() else {} do
			if w:IsA("Model") and w:GetAttribute("Floor") == floor then
				local p = frame:PointToObjectSpace(w:GetPivot().Position)
				local inside = p.X >= b.lo.X - 1.5
					and p.X <= b.hi.X + 1.5
					and p.Z >= b.lo.Z - 1.5
					and p.Z <= b.hi.Z + 1.5
				local rel = Vector3.new(p.X - centre.X, 0, p.Z - centre.Z)
				if inside and rel:Dot(toEye) > 1 then
					for _, part in w:GetDescendants() do
						if part:IsA("BasePart") then
							part.LocalTransparencyModifier = 0.85
							keep[part] = true
						end
					end
				end
			end
		end
	end
	for p in faded do
		if not keep[p] and p.Parent then
			p.LocalTransparencyModifier = 0
		end
	end
	faded = keep
end

-- One bar of the room view: its fill and its words.
local function paintBar(name: string, value: number, words: string)
	local row = viewPanel:FindFirstChild(name, true)
	if not row then
		return
	end
	local fill = row:FindFirstChild("Fill", true) :: Frame?
	local text = row:FindFirstChild("Value", true) :: TextLabel?
	local bonus = row:FindFirstChild("Bonus", true) :: TextLabel?
	if fill then
		fill.Size = UDim2.fromScale(math.clamp(value, 0, 1), 1)
	end
	if text then
		text.Text = `{math.floor(math.clamp(value, 0, 1) * 100 + 0.5)}%`
	end
	if bonus then
		bonus.Text = words
	end
end

-- Fills the room view from the state's copy of the room.
local function paintRoomView()
	local rec = roomView and roomRecord(roomView)
	if not rec then
		if roomView then
			closeRoomView()
		end
		return
	end
	local p = Pieces.get(rec.type)
	local t = nil
	for _, ty in build().types or {} do
		if ty.id == rec.type then
			t = ty
		end
	end
	local title = viewPanel:FindFirstChild("Title", true) :: TextLabel
	title.Text = if p then p.name else rec.type
	local tip = viewPanel:FindFirstChild("Tooltip", true) :: TextLabel
	tip.Text = if t then typeTooltip(t) else ""
	local status = viewPanel:FindFirstChild("Status", true) :: TextLabel
	local state = if rec.state == "Dirty"
		then " · needs cleaning"
		elseif rec.state == "Occupied" then " · a guest is in"
		elseif rec.state == "Reserved" then " · a guest is coming"
		else ""
	local R = Constants.Rooms
	local bars = rec.bars or { size = 0, furniture = 0, decor = 0 }
	-- A.11.1: a "VIP" tag when the room is held for a VIP or meets a running contract's ask.
	local vipTag = ""
	local vip = State.data.vip
	for _, c in if vip then vip.active else {} do
		if c.room == tostring(rec.id) then
			vipTag = " · 👑 held for your VIP"
			state = ""
			break
		elseif
			c.here
			and c.state == "Accepted"
			and c.type == rec.type
			and Contracts.meets(c.needs, bars)
		then
			vipTag = " · 👑 meets your VIP's ask"
		end
	end
	status.Text = if rec.ready
		then `Ready for guests · {rec.size} cells{state}{vipTag}`
		else `Not ready: {rec.missingText}`
	status.TextColor3 = if rec.ready then Ui.Colour.Good else Ui.Colour.Bad
	local function pct(v: number): string
		return `+{math.floor(v * 100 + 0.5)}%`
	end
	paintBar(
		"SizeBar",
		bars.size,
		`{pct(R.SizePay * bars.size)} pay · {pct(R.SizeStay * bars.size)} stay`
	)
	paintBar(
		"FurnitureBar",
		bars.furniture,
		`{pct(R.FurniturePay * bars.furniture)} pay · +{math.floor(
			R.FurnitureSatisfaction * bars.furniture + 0.5
		)} happiness`
	)
	-- A.11.3: a rare set in the room, its pieces here and whether this room has its bonus.
	local setWords = ""
	for _, s in rec.sets or {} do
		local set = Pieces.SetById[s.id]
		local name = if set then set.name else s.id
		setWords ..= if s.bonus
			then ` · ★ {name} {pct(Constants.Finds.SetBonus)}`
			elseif s.have >= s.total then ` · {name}: bonus in another room`
			else ` · {name} {s.have}/{s.total}`
	end
	paintBar(
		"DecorBar",
		bars.decor,
		`+{math.floor(R.DecorSatisfaction * bars.decor + 0.5)} happiness · {pct(
			R.DecorFriendship * bars.decor
		)} friendship{setWords}`
	)
end

local function setCameraTarget(f: Vector3?, z: number, p: number)
	local fromFocus = focus or Vector3.new(G.Cells * G.CellSize / 2, 0, G.Cells * G.CellSize / 2)
	flight = {
		from = { fromFocus, zoom, pitch },
		to = { f or fromFocus, z, p },
		t0 = os.clock(),
	}
end

function closeRoomView()
	if not roomView then
		return
	end
	roomView = nil
	viewBounds = nil
	viewPanel.Visible = false
	layoutView()
	unfade()
	local back = savedView
	savedView = nil
	if back then
		setCameraTarget(back.focus, back.zoom, back.pitch)
	end
end

--[[ Flies the camera to room `id` (A.12 "The room view"): it frames the
	room from above at an angle, the walls toward the camera fade, and the
	panel shows its type, its tooltip and its three bars. ]]
function openRoomView(id: number)
	local rec = roomRecord(id)
	local w: any = world()
	local a = rec and Rooms.roomArea(w, tostring(id))
	if not rec or not a then
		return
	end
	menu.Visible = false
	typesWindow.Visible = false
	if rec.floor ~= floor then
		floor = rec.floor
		setHidden()
		drawTiles()
	end
	local lo = Vector3.new(math.huge, 0, math.huge)
	local hi = Vector3.new(-math.huge, 0, -math.huge)
	for _, k in a.cells do
		local hx, hz = Rooms.halfOf(k)
		lo = Vector3.new(math.min(lo.X, hx * HALF), 0, math.min(lo.Z, hz * HALF))
		hi = Vector3.new(math.max(hi.X, (hx + 1) * HALF), 0, math.max(hi.Z, (hz + 1) * HALF))
	end
	viewBounds = { lo = lo, hi = hi }
	if not roomView then
		savedView = { focus = focus, zoom = zoom, pitch = pitch }
	end
	roomView = id
	local size = G.Cells * G.CellSize
	local extent = math.max(hi.X - lo.X, hi.Z - lo.Z)
	setCameraTarget(
		(lo + hi) / 2,
		math.clamp(extent * 1.9 / (size * 1.109), 0.1, 1.4),
		math.rad(58)
	)
	paintRoomView()
	viewPanel.Visible = true
	layoutView()
	floorLabel.Text = `Floor {floor}/{build().floors}`
end

-- The built room (its id) whose area holds the point under the pointer, or nil.
local function roomUnder(x: number, y: number): number?
	local hx, hz = halfCellUnder(x, y)
	if not hx or not hz then
		return nil
	end
	local w: any = world()
	local a = Rooms.areaAt(w, floor, hx, hz)
	if a and not a.hallway and a.room then
		return tonumber(a.room)
	end
	return nil
end

--[[ A tap on an area with nothing chosen (A.12): a room opens its room
	view; a closed space with a door opens the type list; true when taken. ]]
local function tapArea(x: number, y: number): boolean
	local id = roomUnder(x, y)
	if id then
		openRoomView(id)
		return true
	end
	local hx, hz = halfCellUnder(x, y)
	if not hx or not hz then
		return false
	end
	local w: any = world()
	local a = Rooms.areaAt(w, floor, hx, hz)
	if a and not a.hallway and #a.doors > 0 then
		openTypes(floor, hx, hz)
		return true
	end
	if tab == "Room" and a then
		info.Text = Hud.refusal(if a.hallway then "Hallway" else "NoDoor")
		return true
	end
	return false
end

-- A tap on the plot with no card chosen, or with a floor finish chosen.
local function tapPlot(x: number, y: number)
	if selectedWindow or movingWindow then
		local wall = wallUnder(x, y, false)
		local edge = wall and wall:GetAttribute("Edge") :: string?
		if not edge then
			info.Text = Hud.refusal("NotWall")
		elseif movingWindow then
			Net.send("MoveWindow", movingWindow, edge)
			stopPlacing()
		else
			Net.send("PlaceWindow", selectedWindow :: string, edge)
		end
		return
	end
	local windowed = wallUnder(x, y, true, true)
	if windowed and not selectedFinish then
		openWindowMenu(windowed:GetAttribute("Edge") :: string)
		return
	end
	local id, kind = underPointer(x, y)
	if selectedFinish then
		local f = selectedFinish :: string
		local room = roomUnder(x, y)
		if room then
			Net.send("Finish", tostring(room), f)
			return
		end
		if pointerLocal(x, y) then
			Net.send("Finish", "Hallway", f)
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
	-- A built room, or a walled space to choose a type for (A.12).
	if tapArea(x, y) then
		return
	end
	-- A tile not owned: bought at once if it is next to the hotel (they are cheap, §5.4).
	local c = cellUnder(x, y)
	if c then
		local can, why = Grid.canBuyTile(world().tiles, build().floors, floor, c.x, c.z)
		if can then
			Net.send("BuyTile", floor, c.x, c.z)
		elseif why == "NotNext" or why == "NoTileBelow" then
			info.Text = Hud.refusal(why)
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
	-- On a short screen (a phone in landscape) the rows end above the strip and scroll (2026-10-24: they covered it).
	tools = Ui.scroll(gui, "Tools", UDim2.fromOffset(380, 260), UDim2.fromOffset(10, 56))
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
		tabs[name] = tool(parent, tabNames[name] or name, text, width, function()
			tab = name
			stopPlacing()
			paintTabs()
		end)
	end
	-- Built rooms first (A.12): walls, the rooms, their furniture; then the rest.
	local what = row()
	tabButton(what, "Wall", "Walls", 90)
	tabButton(what, "Room", "Rooms", 90)
	tabButton(what, "Furniture", "Furniture", 104)
	tabButton(what, "Decor", "Decor", 80)
	local what2 = row()
	tabButton(what2, "Stairs", "Stairs, desks", 140)
	tabButton(what2, "Floor", "Floors", 104)
	tabButton(what2, "Window", "Windows", 114)
	paintTabs()

	-- Which floor: down, the floor, up, and buying the next.
	local floors = row()
	function toFloor(f: number)
		floor = math.clamp(f, 1, build().floors)
		redrawCards()
		setHidden()
		updateCamera()
		drawGhost()
		drawTiles()
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
	tool(placingRow, "TopView", "⬇ Top", 114, function()
		pitch = if pitch > math.rad(80) then DEFAULT_PITCH else PITCH_MAX
		updateCamera()
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
		fitTools()
	end)
	camera:GetPropertyChangedSignal("ViewportSize"):Connect(fitTools)

	menu, menuBody = Ui.window(gui, "PieceMenu", "Piece", UDim2.fromScale(0.5, 0.6))
	Ui.list(menuBody, Enum.FillDirection.Vertical, 8)

	-- The type list (A.12): a window of rows, each a type with its tooltip and Choose.
	typesWindow, typesBody =
		Ui.window(gui, "RoomTypes", "Choose a type", UDim2.fromScale(0.56, 0.72), nil, true)
	Ui.list(typesBody, Enum.FillDirection.Vertical, 8)

	--[[ The room view's panel (A.12): on the right, clear of the strip and the
		tools, so the room stays in view; its type, tooltip, readiness, the
		three bars with their bonuses, and what to do next. ]]
	viewPanel = Ui.panel(
		gui,
		"RoomView",
		UDim2.new(0.3, 0, 0, 372),
		UDim2.new(1, -10, 0.5, 30),
		Vector2.new(1, 0.5)
	)
	local viewCap = Instance.new("UISizeConstraint")
	viewCap.MinSize = Vector2.new(250, 0)
	viewCap.MaxSize = Vector2.new(340, 372)
	viewCap.Parent = viewPanel
	viewScale = Instance.new("UIScale")
	viewScale.Parent = viewPanel
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(layoutView)
	viewPanel.Visible = false
	Ui.padding(viewPanel, 10)
	Ui.list(viewPanel, Enum.FillDirection.Vertical, 6)
	local top = Ui.frame(viewPanel, "Top", UDim2.new(1, 0, 0, 40))
	top.BackgroundTransparency = 1
	top.LayoutOrder = 1
	local viewTitle = Ui.label(top, "Title", "", UDim2.new(1, -50, 1, 0), 22, Ui.Colour.Gold)
	viewTitle.TextScaled = false
	local closeView = Ui.button(top, "Close", "X", UDim2.fromOffset(40, 40), function()
		closeRoomView()
	end, Ui.Colour.Bad)
	closeView.Position = UDim2.new(1, -40, 0, 0)
	local tip = Ui.label(viewPanel, "Tooltip", "", UDim2.new(1, 0, 0, 52), 13, Ui.Colour.Muted)
	tip.LayoutOrder = 2
	tip.TextYAlignment = Enum.TextYAlignment.Top
	local status = Ui.label(viewPanel, "Status", "", UDim2.new(1, 0, 0, 22), 15, Ui.Colour.Good)
	status.LayoutOrder = 3
	for i, bar in
		{
			{ "SizeBar", "Size", Ui.Colour.Moon },
			{ "FurnitureBar", "Furniture", Ui.Colour.Pumpkin },
			{ "DecorBar", "Decor", Ui.Colour.Teal },
		}
	do
		local barRow = Ui.frame(viewPanel, bar[1], UDim2.new(1, 0, 0, 52))
		barRow.BackgroundTransparency = 1
		barRow.LayoutOrder = 3 + i
		local name = Ui.label(barRow, "Name", bar[2], UDim2.fromOffset(90, 20), 16)
		name.Position = UDim2.fromOffset(0, 0)
		local value = Ui.label(barRow, "Value", "0%", UDim2.fromOffset(50, 20), 16, bar[3])
		value.Position = UDim2.new(1, -50, 0, 0)
		value.TextXAlignment = Enum.TextXAlignment.Right
		local track = Ui.frame(
			barRow,
			"Track",
			UDim2.new(1, 0, 0, 12),
			UDim2.fromOffset(0, 22),
			Ui.Colour.Ink
		)
		Ui.corner(track, 6)
		local fill = Ui.frame(track, "Fill", UDim2.fromScale(0, 1), nil, bar[3])
		Ui.corner(fill, 6)
		local bonus = Ui.label(barRow, "Bonus", "", UDim2.new(1, 0, 0, 16), 13, Ui.Colour.Muted)
		bonus.Position = UDim2.fromOffset(0, 36)
		-- A rare set's words (A.11.3) can run long: shrink to the line, never past 13.
		bonus.TextScaled = true
		local most = Instance.new("UITextSizeConstraint")
		most.MaxTextSize = 13
		most.Parent = bonus
	end
	local actions = Ui.frame(viewPanel, "Actions", UDim2.new(1, 0, 0, 46))
	actions.BackgroundTransparency = 1
	actions.LayoutOrder = 10
	Ui.list(actions, Enum.FillDirection.Horizontal, 6)
	local function viewButton(
		name: string,
		text: string,
		order: number,
		fn: () -> (),
		colour: Color3?
	)
		local b = Ui.button(actions, name, text, UDim2.new(0.33, -4, 1, 0), fn, colour)
		b.LayoutOrder = order
		b.TextSize = 15
	end
	viewButton("Retype", "Change type", 1, function()
		local rec = roomView and roomRecord(roomView)
		if rec then
			openTypes(rec.floor, rec.hx, rec.hz)
		end
	end, Ui.Colour.Teal)
	viewButton("Furnish", "Furnish", 2, function()
		tab = "Furniture"
		stopPlacing()
		paintTabs()
	end, Ui.Colour.Pumpkin)
	viewButton("Hallway", "Make hallway", 3, function()
		local id = roomView
		if id then
			Net.send("ClearRoom", id)
			closeRoomView()
		end
	end, Ui.Colour.Bad)

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
	panAction = Controls.direction(buildKeys, "Pan", nil, {
		Left = Enum.KeyCode.A,
		Right = Enum.KeyCode.D,
		Up = Enum.KeyCode.W,
		Down = Enum.KeyCode.S,
	})
	padKeys = Controls.context("BuildPad", 2000, true, false)
	cursorAction = Controls.direction(padKeys, "Cursor", Enum.KeyCode.Thumbstick1)
	-- A: what a click does where the cursor is.
	Controls.press(padKeys, "Act", { Enum.KeyCode.ButtonA }, function()
		local s = padScreen()
		if not active or not s or Controls.selectedRecently() then
			return
		end
		if wallMode then
			wallFrom = nil
			wallRelease(s.X, s.Y)
		elseif placing() then
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
			drawTiles()
		end
	end)
	-- Looking round the plot (his ask, 2026-10-19): the mouse wheel or a pinch
	-- zooms; the right mouse button dragged, a two-finger twist, or the , and .
	-- keys turn the camera (E is the prompts' key); ↻ View still turns a quarter.
	local function zoomBy(factor: number)
		zoom = math.clamp(zoom * factor, math.min(0.35, zoom), 1.4)
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
	UserInputService.TouchPan:Connect(function(touches, _, velocity, _, processed)
		if not active or processed or #touches ~= 1 or placing() or wallMode then
			return
		end
		local dt = 1 / 60
		local scale = G.Cells * G.CellSize * zoom / math.max(camera.ViewportSize.Y, 1) * 1.5
		panBy(Vector2.new(-velocity.X, velocity.Y) * dt * scale)
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
	local lastFade = 0
	RunService.RenderStepped:Connect(function(dt)
		if not active then
			return
		end
		-- The room view's flight (A.12): the free camera's focus, zoom and tilt eased to their targets.
		local fl = flight
		if fl then
			local t = math.clamp((os.clock() - fl.t0) / 0.6, 0, 1)
			local e = t * t * (3 - 2 * t)
			focus = (fl.from[1] :: Vector3):Lerp(fl.to[1] :: Vector3, e)
			zoom = (fl.from[2] :: number) + ((fl.to[2] :: number) - (fl.from[2] :: number)) * e
			pitch = (fl.from[3] :: number) + ((fl.to[3] :: number) - (fl.from[3] :: number)) * e
			updateCamera()
			if t >= 1 then
				flight = nil
			end
		end
		if roomView and os.clock() - lastFade > 0.15 then
			lastFade = os.clock()
			fadeNearWalls()
			paintRoomView()
		end
		local pan = Controls.read(panAction)
		if pan ~= Vector2.zero then
			panBy(pan * (G.Cells * G.CellSize * 0.5 * zoom * dt))
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
			firstCard() or tools:FindFirstChild(tabNames[tab] or tab, true) :: GuiObject?
		)
		return true
	end)
	-- ButtonB with no panel open: stop placing, else leave the cards, else leave build mode.
	Controls.onBack(function()
		if not active then
			return false
		end
		if
			selected
			or selectedDecor
			or selectedFinish
			or selectedWindow
			or movingWindow
			or moving
			or movingDecor
			or wallMode
		then
			stopPlacing()
			padRefresh()
		elseif roomView then
			closeRoomView()
		elseif Controls.selectedRecently() then
			Controls.select(nil)
			padRefresh()
		else
			setActive(false)
		end
		return true
	end)
	UserInputService.InputChanged:Connect(function(input, processed)
		if not active then
			return
		end
		-- A right-drag that began on the plot turns the camera wherever the
		-- cursor goes and whatever else marks the move as taken (his report,
		-- 2026-10-20: "you cant rotate the camera in build mode").
		if
			input.UserInputType == Enum.UserInputType.MouseMovement
			and rightDownAt
			and UserInputService:IsMouseButtonPressed(Enum.UserInputType.MouseButton2)
		then
			-- By the cursor's own travel: `Delta` is zero for injected input
			-- (the Studio MCP's), and the position is right for both.
			local x, y = input.Position.X, input.Position.Y
			pitch = math.clamp(pitch + (y - (rightDragY or y)) * 0.006, PITCH_MIN, PITCH_MAX)
			turnBy(-(x - (rightDragX or x)) * 0.008)
			rightDragX, rightDragY = x, y
			return
		end
		if processed then
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
		-- The wall tool (A.12): the edge a tap would take, or the run being dragged.
		if
			(
				input.UserInputType == Enum.UserInputType.MouseMovement
				or input.UserInputType == Enum.UserInputType.Touch
			) and wallMode
		then
			wallHover(input.Position.X, input.Position.Y)
			return
		end
		-- A window being placed or moved lights the wall it would go on.
		if
			input.UserInputType == Enum.UserInputType.MouseMovement
			and (selectedWindow or movingWindow)
		then
			outline(wallUnder(input.Position.X, input.Position.Y, false))
			return
		end
		-- With nothing being placed, what is under the mouse lights up: it can be tapped.
		if input.UserInputType == Enum.UserInputType.MouseMovement and not placing() then
			showHover(underPointer(input.Position.X, input.Position.Y))
			lightTile(input.Position.X, input.Position.Y)
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
		if not active then
			return
		end
		-- The right button starts a turn anywhere but on the build mode's own buttons.
		if input.UserInputType == Enum.UserInputType.MouseButton2 then
			if not overUi(input.Position.X, input.Position.Y) then
				rightDownAt = Vector2.new(input.Position.X, input.Position.Y)
				rightDragX, rightDragY = input.Position.X, input.Position.Y
			end
			return
		end
		if processed then
			return
		end
		if
			input.UserInputType == Enum.UserInputType.MouseButton1
			or input.UserInputType == Enum.UserInputType.Touch
		then
			local pos = input.Position
			if overUi(pos.X, pos.Y) then
				return
			end
			if wallMode then
				wallPress(pos.X, pos.Y)
				wallHover(pos.X, pos.Y)
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
		if
			active
			and wallMode
			and wallFrom
			and (
				input.UserInputType == Enum.UserInputType.MouseButton1
				or input.UserInputType == Enum.UserInputType.Touch
			)
		then
			wallRelease(input.Position.X, input.Position.Y)
			return
		end
		if not active or input.UserInputType ~= Enum.UserInputType.MouseButton2 then
			return
		end
		local down = rightDownAt
		rightDownAt = nil
		rightDragX, rightDragY = nil, nil
		local at = Vector2.new(input.Position.X, input.Position.Y)
		if
			down
			and (at - down).Magnitude < 6
			and (
				selected
				or selectedDecor
				or selectedFinish
				or selectedWindow
				or movingWindow
				or moving
				or movingDecor
				or wallMode
			)
		then
			stopPlacing()
		end
	end)
	RunService.RenderStepped:Connect(function()
		if active and camera.CameraType ~= Enum.CameraType.Scriptable then
			updateCamera()
		end
	end)
	-- A rebuilt hotel (a new floor, a tile, a stair) makes new parts: hide them again.
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
