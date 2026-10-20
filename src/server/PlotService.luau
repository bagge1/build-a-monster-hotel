--!strict
--[[
	Creepy Lane's six plots (GDD §3, Appendix A.1); the lane itself is
	`StreetService`'s.

	On joining, a player gets the nearest free plot (`StreetLayout.ClaimOrder`)
	and their saved hotel is rebuilt there: the layout is saved relative to the
	plot (§3), so any plot works. On leaving the plot is cleared for the next.

	This file BUILDS; it decides nothing. Where a piece may go is `Grid`'s and
	`BuildService`'s, what a guest does is `GuestService`'s. It owns the plot
	models in `workspace.Plots`, their prompts (the desk, the till, each room's
	door), and the owner's spawn, and it answers where things are by the
	models' attachments (MODELS.md), never by a measurement of its own.

	Published: each `Plot_<i>` model carries `Index`, `OwnerId`, `OwnerName`
	and `Origin` (its frame); each piece model `PieceId`, `Item`, `Kind`,
	`Floor`, `Tier`; each decor model (in `Decor`) `DecorId`, `Item`, `Floor`,
	`Room`. The client's build mode reads those.

	FREE BUILDING (§5.4): the lobby is a shell, the front desk and the stairs
	are pieces of the layout, decor stands on its squares, areas not yet
	bought carry a plate, and floor finishes are laid on the `Floor` parts and
	the hallways' slabs (MODELS.md, "Floor finishes"). The desk's points are
	mirrored onto the lobby's `Root` (MODELS.md, "Lobby: the shell"), so
	everything that finds the desk through the lobby keeps finding it.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Furnish = require(ReplicatedStorage.Shared.Furnish)
local Grid = require(ReplicatedStorage.Shared.Grid)
local Layout = require(ReplicatedStorage.Shared.Layout)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Locations = require(ReplicatedStorage.Shared.Locations)
local Cosmetics = require(ReplicatedStorage.Shared.Cosmetics)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)
local HotelKit = require(ServerScriptService.Server.HotelKit)
local PlayerData = require(ServerScriptService.Server.PlayerData)

local G = Constants.Grid

local PlotService = {}

export type Plot = {
	index: number,
	owner: Player?,
	model: Model,
	frame: CFrame,
	location: number,
	lobby: Model?,
	sign: Model?,
	pieces: { [string]: Model }, -- by piece id (rooms, amenities, stairs, the desk)
	decor: { [string]: Model }, -- by decor id
	floors: number,
}

local plots: { Plot } = {}
local byPlayer: { [Player]: Plot } = {}
local plotsFolder: Folder

type PromptHandler = (player: Player, plot: Plot, kind: string, pieceId: string?) -> ()
local promptHandlers: { PromptHandler } = {}
local builtHandlers: { (plot: Plot) -> () } = {}

-- Moves every part of a folder built in plot-local coordinates into the plot's frame.
local function placeLocal(folder: Instance, frame: CFrame)
	for _, d in folder:GetDescendants() do
		if d:IsA("BasePart") then
			d.CFrame = frame * d.CFrame
		end
	end
end

-- The layout as the pure rules see it (Grid, Layout).
function PlotService.world(data: PlayerData.Data): Grid.World
	return Layout.world(data.floors, data.areas, data.layout, data.decor)
end

-- A piece's pivot in the plot's frame: its footprint's centre, turned so its door faces the right way.
function PlotService.pieceFrame(
	plot: Plot,
	rec: { floor: number, x: number, z: number, r: number, item: string }
): CFrame
	local piece = assert(Pieces.get(rec.item), rec.item)
	local centre = Grid.pieceCentre({
		floor = rec.floor,
		x = rec.x,
		z = rec.z,
		r = rec.r,
		w = piece.w,
		d = piece.d,
	})
	return plot.frame * CFrame.new(centre) * CFrame.Angles(0, -rec.r * math.pi / 2, 0)
end

local function makePrompt(
	parent: Instance,
	action: string,
	objectText: string,
	hold: number,
	plot: Plot,
	kind: string,
	pieceId: string?
): ProximityPrompt
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = `Prompt_{kind}`
	prompt.ActionText = action
	prompt.ObjectText = objectText
	prompt.HoldDuration = hold
	prompt.MaxActivationDistance = 10
	prompt.RequiresLineOfSight = false
	prompt.KeyboardKeyCode = Enum.KeyCode.E
	prompt:SetAttribute("OwnerId", if plot.owner then plot.owner.UserId else 0)
	prompt.Parent = parent
	prompt.Triggered:Connect(function(player: Player)
		if plot.owner ~= player then
			return
		end
		for _, handler in promptHandlers do
			local ok, err = pcall(handler, player, plot, kind, pieceId)
			if not ok then
				warn(`[plot] prompt {kind} failed: {err}`)
			end
		end
	end)
	return prompt
end

-- The prompts a room's door carries: cleaning and a request, both off until GuestService turns them on.
local function roomPrompts(plot: Plot, model: Model, pieceId: string)
	local root = model.PrimaryPart
	local door = root and root:FindFirstChild("Door")
	if not door then
		warn(`[plot] {model.Name} has no Door attachment (MODELS.md, "Rooms and amenities")`)
		return
	end
	local clean =
		makePrompt(door, "Clean", model.Name, Constants.Stay.CleanHold, plot, "Clean", pieceId)
	clean.Enabled = false
	local help = makePrompt(door, "Help", model.Name, 0, plot, "Request", pieceId)
	help.Enabled = false
	help.UIOffset = Vector2.new(0, 60)
end

--[[ What a room model says about itself, once per item and location: the
	squares its own furniture covers (MODELS.md: `Bed`, `Furniture`,
	`Centrepiece`) and its `Floor`'s top, both in the piece's own frame. ]]
type RoomInfo = { blocked: { [number]: boolean }, floorTop: number }
local roomInfos: { [string]: RoomInfo } = {}

function PlotService.roomInfo(item: string, location: number): RoomInfo
	local cacheKey = `{location}:{item}`
	local cached = roomInfos[cacheKey]
	if cached then
		return cached
	end
	local piece = assert(Pieces.get(item), item)
	local model = HotelKit.piece(item, location)
	local pivot = model:GetPivot()
	local boxes, floorTop = {}, 0
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") then
			local cf = pivot:ToObjectSpace(d.CFrame)
			local half = d.Size / 2
			local lo, hi = cf.Position - half, cf.Position + half
			if d.Name == "Bed" or d.Name == "Furniture" or d.Name == "Centrepiece" then
				table.insert(boxes, { min = lo, max = hi })
			elseif d.Name == "Floor" then
				floorTop = math.max(floorTop, hi.Y)
			end
		end
	end
	model:Destroy()
	local info = { blocked = Furnish.blocked(piece, boxes), floorTop = floorTop }
	roomInfos[cacheKey] = info
	return info
end

--[[ Lays a floor finish on a part (MODELS.md, "Floor finishes"): its texture
	goes, the finish's material and colour come. A part keeps its own look
	when the finish is "" (it is built fresh). ]]
local function lay(part: BasePart, finishId: string?)
	local f = if finishId and finishId ~= "" then Pieces.finish(finishId) else nil
	if not f then
		return
	end
	for _, c in part:GetChildren() do
		if c:IsA("SurfaceAppearance") or c:IsA("Texture") or c:IsA("Decal") then
			c:Destroy()
		end
	end
	if part:IsA("MeshPart") then
		pcall(function()
			(part :: any).TextureID = ""
		end)
	end
	part.Material = f.material
	part.Color = f.colour
end

local function layOn(model: Instance, finishId: string?)
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") and d.Name == "Floor" then
			lay(d, finishId)
		end
	end
end

-- The front desk's points, copied onto the lobby's Root under the same names (MODELS.md).
local DESK_POINTS = { "Desk", "Clerk", "Till", "Queue_1", "Queue_2", "Queue_3", "Queue_4" }
local function mirrorDesk(plot: Plot, desk: Model)
	local lobbyRoot = plot.lobby and plot.lobby.PrimaryPart
	local root = desk.PrimaryPart
	if not lobbyRoot or not root then
		return
	end
	for _, name in DESK_POINTS do
		local old = lobbyRoot:FindFirstChild(name)
		if old then
			old:Destroy()
		end
		local a = root:FindFirstChild(name)
		if a and a:IsA("Attachment") then
			local m = Instance.new("Attachment")
			m.Name = name
			m.Parent = lobbyRoot
			m.WorldCFrame = a.WorldCFrame
		end
	end
end

-- Whether a stair on the floor above continues this one (same cells and turn).
local function continued(data: PlayerData.Data, rec: PlayerData.PieceRecord): boolean
	for _, other in data.layout do
		if
			other.item == "Stairs"
			and other.floor == rec.floor + 1
			and other.x == rec.x
			and other.z == rec.z
			and other.r == rec.r
		then
			return true
		end
	end
	return false
end

local function buildPiece(
	plot: Plot,
	id: string,
	rec: PlayerData.PieceRecord,
	data: PlayerData.Data
): Model?
	local piece = Pieces.get(rec.item)
	if not piece then
		return nil
	end
	local model = if piece.kind == "Stairs"
		then HotelKit.stairs(plot.location, not continued(data, rec))
		else HotelKit.piece(rec.item, plot.location)
	model.Name = `P_{id}`
	model:SetAttribute("PieceId", id)
	model:SetAttribute("Item", rec.item)
	model:SetAttribute("Kind", piece.kind)
	model:SetAttribute("Floor", rec.floor)
	model:PivotTo(PlotService.pieceFrame(plot, rec))
	local root = model.PrimaryPart
	if piece.kind == "Room" or piece.kind == "Amenity" then
		layOn(model, rec.finish)
		local tier = Layout.roomTier(PlotService.world(data), id)
		model:SetAttribute("Tier", tier)
		-- Its name over the door: on the kit's wooden plaque (his ask,
		-- 2026-10-19), else as floating text until the plaque is imported.
		local sign = root and root:FindFirstChild("Sign")
		local plaque = sign and sign:IsA("Attachment") and HotelKit.plaque(plot.location)
		local face = plaque and plaque:FindFirstChild("Face", true)
		if plaque and face and face:IsA("BasePart") and sign and sign:IsA("Attachment") then
			plaque:PivotTo(sign.WorldCFrame)
			plaque.Parent = model
			local gui = Instance.new("SurfaceGui")
			gui.Name = "Label"
			gui.Face = Enum.NormalId.Front
			gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
			gui.PixelsPerStud = 60
			gui.LightInfluence = 0.6
			gui.MaxDistance = 80
			local function line(name: string, y: number, h: number, colour: Color3, text: string)
				local l = Instance.new("TextLabel")
				l.Name = name
				l.BackgroundTransparency = 1
				l.Position = UDim2.fromScale(0.05, y)
				l.Size = UDim2.fromScale(0.9, h)
				l.Font = Enum.Font.FredokaOne
				l.TextScaled = true
				l.TextColor3 = colour
				l.Text = text
				l.Parent = gui
			end
			line("Text", 0.06, 0.56, Color3.fromRGB(255, 232, 180), `{piece.name} · T{tier}`)
			line("Status", 0.62, 0.32, Color3.fromRGB(255, 190, 120), "")
			gui.Parent = face
		elseif sign then
			local gui = Instance.new("BillboardGui")
			gui.Name = "Label"
			gui.Size = UDim2.fromOffset(160, 40)
			gui.MaxDistance = 60
			gui.LightInfluence = 0
			local text = Instance.new("TextLabel")
			text.Name = "Text"
			text.Size = UDim2.fromScale(1, 1)
			text.BackgroundTransparency = 1
			text.Font = Enum.Font.FredokaOne
			text.TextScaled = true
			text.TextColor3 = Color3.fromRGB(255, 240, 220)
			text.TextStrokeTransparency = 0.4
			text.Text = `{piece.name} T{tier}`
			text.Parent = gui
			gui.Parent = sign
		end
	end
	model.Parent = plot.model:FindFirstChild("Pieces")
	if piece.kind == "Room" then
		roomPrompts(plot, model, id)
	elseif piece.kind == "Desk" and root then
		local desk = root:FindFirstChild("Desk")
		local till = root:FindFirstChild("Till")
		if desk then
			makePrompt(
				desk,
				"Check in",
				"Front Desk",
				Constants.Stay.CheckInHold,
				plot,
				"Desk",
				nil
			)
		end
		if till then
			makePrompt(till, "Collect", "Till", 0, plot, "Till", nil)
		end
		mirrorDesk(plot, model)
	end
	plot.pieces[id] = model
	return model
end

-- Where a decor piece stands, in the plot's frame: on its room's floor, or on the hallway's.
local function decorFrame(plot: Plot, data: PlayerData.Data, rec: PlayerData.DecorRecord): CFrame?
	local d = Pieces.decor(rec.item)
	if not d then
		return nil
	end
	local placed = { floor = rec.floor, x = rec.x, z = rec.z, r = rec.r, w = d.w, d = d.d }
	local lift = 0.02
	local room = if rec.room ~= "" then data.layout[rec.room] else nil
	if room then
		lift += PlotService.roomInfo(room.item, plot.location).floorTop
	elseif rec.floor == 1 and Grid.isLobbyRow(rec.z // Grid.Squares) and plot.lobby then
		for _, part in plot.lobby:GetDescendants() do
			if part:IsA("BasePart") and part.Name == "Floor" then
				local top = plot.lobby:GetPivot():ToObjectSpace(part.CFrame).Position.Y
					+ part.Size.Y / 2
				lift = math.max(lift, top + 0.02)
			end
		end
	end
	return plot.frame
		* CFrame.new(Grid.decorCentre(placed) + Vector3.new(0, lift, 0))
		* CFrame.Angles(0, -rec.r * math.pi / 2, 0)
end

local function buildDecor(
	plot: Plot,
	id: string,
	rec: PlayerData.DecorRecord,
	data: PlayerData.Data
)
	local at = decorFrame(plot, data, rec)
	local folder = plot.model:FindFirstChild("Decor")
	if not at or not folder then
		return
	end
	local model = HotelKit.decor(rec.item, plot.location)
	model.Name = `D_{id}`
	model:SetAttribute("DecorId", id)
	model:SetAttribute("Item", rec.item)
	model:SetAttribute("Floor", rec.floor)
	model:SetAttribute("Room", rec.room)
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.Anchored = true
			part.CanCollide = false
			part.CanTouch = false
		end
	end
	model:PivotTo(at)
	model.Parent = folder
	plot.decor[id] = model
end

-- The plates over the areas not yet bought, on every floor (§5.4).
local function buildAreas(plot: Plot, data: PlayerData.Data)
	local old = plot.model:FindFirstChild("Areas")
	if old then
		old:Destroy()
	end
	local folder = Instance.new("Folder")
	folder.Name = "Areas"
	for i = 1, Grid.areaCount() do
		if not data.areas[tostring(i)] then
			local x0, z0, w, d = Grid.areaRect(i)
			for floor = 1, data.floors do
				local plate = HotelKit.areaPlate(plot.location, w * G.CellSize, d * G.CellSize)
				plate.CFrame = plot.frame
					* CFrame.new(
						(x0 + w / 2) * G.CellSize,
						Grid.floorY(floor) + 0.05,
						(z0 + d / 2) * G.CellSize
					)
				plate:SetAttribute("Area", i)
				plate:SetAttribute("Floor", floor)
				plate.Parent = folder
			end
		end
	end
	folder.Parent = plot.model
end

-- The hallways' and the lobby's floor finishes (§5.4).
local function layHallways(plot: Plot, data: PlayerData.Data)
	local hall = data.finishes.Hallway
	local base = plot.model:FindFirstChild("Base")
	local ground = base and base:FindFirstChild("Ground")
	if ground and ground:IsA("BasePart") then
		lay(ground, hall)
	end
	for floor = 2, data.floors do
		local slab = plot.model:FindFirstChild(`Slab_{floor}`)
		if slab then
			for _, p in slab:GetChildren() do
				if p:IsA("BasePart") and p.Name == "Slab" then
					lay(p, hall)
				end
			end
		end
	end
	if plot.lobby then
		layOn(plot.lobby, data.finishes.Lobby)
	end
end

-- Builds everything of a plot from its owner's data, from scratch.
local drawCosmetics: (Plot, PlayerData.Data) -> ()

local function buildHotel(plot: Plot, data: PlayerData.Data?)
	for _, child in plot.model:GetChildren() do
		child:Destroy()
	end
	plot.pieces = {}
	plot.decor = {}
	plot.lobby = nil
	plot.sign = nil
	plot.location = if data then data.location else 1
	plot.floors = if data then data.floors else 1
	plot.model:SetAttribute("Location", plot.location)

	local base = HotelKit.base(plot.location)
	placeLocal(base, plot.frame)
	base.Parent = plot.model

	local piecesFolder = Instance.new("Folder")
	piecesFolder.Name = "Pieces"
	piecesFolder.Parent = plot.model

	if not data then
		return
	end

	local lobby = HotelKit.lobby(plot.location)
	lobby:PivotTo(plot.frame * CFrame.new(StreetLayout.EntranceLocal))
	lobby.Parent = plot.model
	plot.lobby = lobby

	local sign = HotelKit.sign(plot.location)
	local board = PlotService.forecourtPoint(plot, "SignBoard")
	if board then
		sign:PivotTo(board)
	end
	sign.Parent = plot.model
	plot.sign = sign

	drawCosmetics(plot, data)

	-- Each floor above the first, with a hole over every stair coming up to it.
	local C = G.CellSize
	for floor = 2, data.floors do
		local holes = {}
		for _, rec in data.layout do
			if rec.item == "Stairs" and rec.floor == floor - 1 then
				local ex, ez = Grid.extent(2, 2, rec.r)
				local h =
					{ x0 = rec.x * C, z0 = rec.z * C, x1 = (rec.x + ex) * C, z1 = (rec.z + ez) * C }
				-- The 1-stud lip along its front (MODELS.md, "Stairs").
				if rec.r == 0 then
					h.z0 += 1
				elseif rec.r == 1 then
					h.x1 -= 1
				elseif rec.r == 2 then
					h.z1 -= 1
				else
					h.x0 += 1
				end
				table.insert(holes, h)
			end
		end
		local slab = HotelKit.slab(plot.location, floor, holes)
		placeLocal(slab, plot.frame)
		slab.Parent = plot.model
	end
	buildAreas(plot, data)

	for id, rec in data.layout do
		buildPiece(plot, id, rec, data)
	end
	local decorFolder = Instance.new("Folder")
	decorFolder.Name = "Decor"
	decorFolder.Parent = plot.model
	for id, rec in data.decor do
		buildDecor(plot, id, rec, data)
	end
	layHallways(plot, data)
	if plot.owner then
		PlotService.refreshTraps(plot.owner)
	end
	for _, handler in builtHandlers do
		task.spawn(handler, plot)
	end
end

-- The cosmetic its owner wears in `slot`, if they own it (MODELS.md, "Cosmetics").
local function worn(data: PlayerData.Data, slot: string): Cosmetics.Cosmetic?
	local id = data.equipped[slot]
	local c = id and Cosmetics.get(id)
	return if c and c.slot == slot and Cosmetics.owns(data, id) then c else nil
end

--[[ The facade, in its cosmetic's colours, and the sign and lobby cosmetics at
	their origins (MODELS.md, "Cosmetics"): the sign's Board front face and the
	lobby's Entrance. Drawn again whole on every change. ]]
function drawCosmetics(plot: Plot, data: PlayerData.Data)
	for _, name in { "Facade", "Cosmetics" } do
		local old = plot.model:FindFirstChild(name)
		if old then
			old:Destroy()
		end
	end
	local f = worn(data, "Facade")
	local facade = HotelKit.facade(
		plot.location,
		data.floors,
		if f then { facade = f.colour, trim = f.trim or f.colour } else nil
	)
	placeLocal(facade, plot.frame)
	facade.Parent = plot.model

	local folder = Instance.new("Folder")
	folder.Name = "Cosmetics"
	local sign = worn(data, "Sign")
	local board = plot.sign and plot.sign:FindFirstChild("Board", true) :: BasePart?
	if sign and board then
		local m = HotelKit.cosmetic(sign)
		m:PivotTo(board.CFrame * CFrame.new(0, 0, -board.Size.Z / 2))
		m.Parent = folder
	end
	local lobby = worn(data, "Lobby")
	local root = plot.lobby and plot.lobby.PrimaryPart
	local entrance = root and root:FindFirstChild("Entrance") :: Attachment?
	if lobby and entrance then
		local m = HotelKit.cosmetic(lobby)
		m:PivotTo(entrance.WorldCFrame)
		m.Parent = folder
	end
	folder.Parent = plot.model
end

function PlotService.refreshCosmetics(player: Player)
	local plot = byPlayer[player]
	local data = PlayerData.get(player)
	if plot and data and plot.lobby then
		drawCosmetics(plot, data)
	end
end

-- The forecourt's traps (§8.1, §5.4), drawn at its `Trap_n` attachments (a blockout until the kit has them).
function PlotService.refreshTraps(player: Player)
	local plot = byPlayer[player]
	local data = PlayerData.get(player)
	if not plot or not data then
		return
	end
	local old = plot.model:FindFirstChild("Traps")
	if old then
		old:Destroy()
	end
	local folder = Instance.new("Folder")
	folder.Name = "Traps"
	for slot, id in data.traps do
		local a = PlotService.forecourtPoint(plot, `Trap_{slot}`)
		local trap = nil
		for _, t in Constants.Traps do
			if t.id == id then
				trap = t
			end
		end
		if a and trap then
			local part = Instance.new("Part")
			part.Name = `Trap_{slot}`
			part.Anchored = true
			part.CanCollide = false
			part.Size = Vector3.new(3, 0.3, 3)
			part.Color = trap.colour
			part.Material = Enum.Material.SmoothPlastic
			part.CFrame = a * CFrame.new(0, 0.15, 0)
			part:SetAttribute("Trap", trap.id)
			part.Parent = folder
		end
	end
	folder.Parent = plot.model
end

function PlotService.rebuild(player: Player)
	local plot = byPlayer[player]
	if plot then
		buildHotel(plot, PlayerData.get(player))
	end
end

function PlotService.addPiece(player: Player, id: string)
	local plot = byPlayer[player]
	local data = PlayerData.get(player)
	if plot and data and data.layout[id] then
		local old = plot.pieces[id]
		if old then
			old:Destroy()
		end
		buildPiece(plot, id, data.layout[id], data)
	end
end

function PlotService.removePiece(player: Player, id: string)
	local plot = byPlayer[player]
	if plot and plot.pieces[id] then
		plot.pieces[id]:Destroy()
		plot.pieces[id] = nil
	end
end

-- Draws one decor piece again (placed or moved), or takes it away when its record is gone.
function PlotService.drawDecor(player: Player, id: string)
	local plot = byPlayer[player]
	local data = PlayerData.get(player)
	if not plot or not data then
		return
	end
	local old = plot.decor[id]
	if old then
		old:Destroy()
		plot.decor[id] = nil
	end
	local rec = data.decor[id]
	if rec then
		buildDecor(plot, id, rec, data)
	end
end

function PlotService.of(player: Player): Plot?
	return byPlayer[player]
end

function PlotService.all(): { Plot }
	return plots
end

function PlotService.onPrompt(handler: PromptHandler)
	table.insert(promptHandlers, handler)
end

-- Called after a hotel has been built from scratch (its prompts and pieces are new).
function PlotService.onBuilt(handler: (Plot) -> ())
	table.insert(builtHandlers, handler)
end

-- The world frame of an attachment on a plot's lobby, or nil.
function PlotService.lobbyPoint(plot: Plot, name: string): CFrame?
	local root = plot.lobby and plot.lobby.PrimaryPart
	local a = root and root:FindFirstChild(name)
	return if a and a:IsA("Attachment") then a.WorldCFrame else nil
end

-- The world frame of an attachment on a plot's forecourt (MODELS.md, "Forecourt"), or nil.
function PlotService.forecourtPoint(plot: Plot, name: string): CFrame?
	local base = plot.model:FindFirstChild("Base")
	local forecourt = base and base:FindFirstChild("Forecourt")
	local root = if forecourt and forecourt:IsA("Model") then forecourt.PrimaryPart else nil
	local a = root and root:FindFirstChild(name)
	return if a and a:IsA("Attachment") then a.WorldCFrame else nil
end

-- The world frame of an attachment on one of a plot's pieces, or nil.
function PlotService.piecePoint(plot: Plot, pieceId: string, name: string): CFrame?
	local model = plot.pieces[pieceId]
	local root = model and model.PrimaryPart
	local a = root and root:FindFirstChild(name)
	return if a and a:IsA("Attachment") then a.WorldCFrame else nil
end

-- The guests' glide up one stair (a piece's id): Bottom, Path_n..., Top. Reverse it to come down.
function PlotService.stairPath(plot: Plot, stairId: string): { Vector3 }
	local model = plot.pieces[stairId]
	local root = model and model.PrimaryPart
	if not root then
		return {}
	end
	local out = {}
	local bottom = root:FindFirstChild("Bottom") :: Attachment?
	if bottom then
		table.insert(out, bottom.WorldPosition)
	end
	local i = 1
	while root:FindFirstChild(`Path_{i}`) do
		table.insert(out, (root:FindFirstChild(`Path_{i}`) :: Attachment).WorldPosition)
		i += 1
	end
	local top = root:FindFirstChild("Top") :: Attachment?
	if top then
		table.insert(out, top.WorldPosition)
	end
	return out
end

-- A prompt on a piece's door (`Clean` or `Request`), or nil.
function PlotService.roomPrompt(plot: Plot, pieceId: string, kind: string): ProximityPrompt?
	local model = plot.pieces[pieceId]
	local root = model and model.PrimaryPart
	local door = root and root:FindFirstChild("Door")
	local p = door and door:FindFirstChild(`Prompt_{kind}`)
	return if p and p:IsA("ProximityPrompt") then p else nil
end

local function spawnAt(player: Player)
	local plot = byPlayer[player]
	local character = player.Character
	local at = plot and PlotService.lobbyPoint(plot, "Spawn")
	if character and at then
		character:PivotTo(at + Vector3.new(0, 3, 0))
	end
end

local function claim(player: Player, data: PlayerData.Data)
	if byPlayer[player] then
		return
	end
	for _, index in StreetLayout.ClaimOrder do
		local plot = plots[index]
		if plot and not plot.owner then
			plot.owner = player
			byPlayer[player] = plot
			plot.model:SetAttribute("OwnerId", player.UserId)
			plot.model:SetAttribute("OwnerName", player.DisplayName)
			player:SetAttribute("Plot", index)
			buildHotel(plot, data)
			spawnAt(player)
			return
		end
	end
	warn(`[plot] no free plot for {player.Name}`)
end

local function release(player: Player)
	local plot = byPlayer[player]
	if not plot then
		return
	end
	byPlayer[player] = nil
	plot.owner = nil
	plot.model:SetAttribute("OwnerId", 0)
	plot.model:SetAttribute("OwnerName", "")
	buildHotel(plot, nil)
end

function PlotService.Init()
	local old = workspace:FindFirstChild("Plots")
	if old then
		old:Destroy()
	end
	plotsFolder = Instance.new("Folder")
	plotsFolder.Name = "Plots"
	plotsFolder.Parent = workspace
	for i = 1, Constants.Street.Plots do
		local model = Instance.new("Model")
		model.Name = `Plot_{i}`
		model.ModelStreamingMode = Enum.ModelStreamingMode.Atomic
		local frame = StreetLayout.plotFrame(i)
		model:SetAttribute("Index", i)
		model:SetAttribute("OwnerId", 0)
		model:SetAttribute("OwnerName", "")
		model:SetAttribute("Origin", frame)
		model.Parent = plotsFolder
		local plot: Plot = {
			index = i,
			owner = nil,
			model = model,
			frame = frame,
			location = 1,
			lobby = nil,
			sign = nil,
			pieces = {},
			decor = {},
			floors = 1,
		}
		plots[i] = plot
		buildHotel(plot, nil)
	end
end

function PlotService.Start()
	-- One player per plot (§3): the place's server size (Experience Settings → Places) must not exceed it.
	if Players.MaxPlayers > Constants.Street.Plots then
		warn(
			`[plot] server size is {Players.MaxPlayers} but the street has {Constants.Street.Plots} plots: players past the sixth get no hotel`
		)
	end
	PlayerData.onLoaded(function(player, data)
		claim(player, data)
		player.CharacterAdded:Connect(function()
			task.wait()
			spawnAt(player)
		end)
		if player.Character then
			spawnAt(player)
		end
	end)
	PlayerData.onDeparted(release)
	Players.PlayerRemoving:Connect(release)
end

PlotService.Locations = Locations

return PlotService
