--!strict
--[[
	Creepy Lane and its six plots (GDD §3, Appendix A.1).

	On joining, a player gets the nearest free plot (`StreetLayout.ClaimOrder`)
	and their saved hotel is rebuilt there: the layout is saved relative to the
	plot (§3), so any plot works. On leaving the plot is cleared for the next.

	This file BUILDS; it decides nothing. Where a piece may go is `Grid`'s and
	`BuildService`'s, what a guest does is `GuestService`'s. It owns the plot
	models in `workspace.Plots`, their prompts (the desk, the till, each room's
	door), and the owner's spawn, and it answers where things are by the
	models' attachments (MODELS.md), never by a measurement of its own.

	Published: each `Plot_<i>` model carries `Index`, `OwnerId`, `OwnerName`
	and `Origin` (its frame); each piece model `PieceId`, `Item`, `Floor`,
	`Tier`. The client's build mode reads those.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")
local Lighting = game:GetService("Lighting")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Grid = require(ReplicatedStorage.Shared.Grid)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Locations = require(ReplicatedStorage.Shared.Locations)
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
	stairs: { [number]: Model }, -- by the lower floor
	pieces: { [string]: Model }, -- by piece id
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

local function pieceRecordToPlaced(id: string, rec: PlayerData.PieceRecord): Grid.Placed?
	local piece = Pieces.get(rec.item)
	if not piece then
		return nil
	end
	return {
		item = rec.item,
		floor = rec.floor,
		x = rec.x,
		z = rec.z,
		r = rec.r,
		w = piece.w,
		d = piece.d,
		id = id,
	} :: any
end

-- The layout as Grid wants it.
function PlotService.placed(data: PlayerData.Data): { Grid.Placed }
	local out = {}
	for id, rec in data.layout do
		local p = pieceRecordToPlaced(id, rec)
		if p then
			table.insert(out, p)
		end
	end
	return out
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

local function buildPiece(plot: Plot, id: string, rec: PlayerData.PieceRecord): Model?
	local piece = Pieces.get(rec.item)
	if not piece then
		return nil
	end
	local model = HotelKit.piece(rec.item, plot.location)
	model.Name = `P_{id}`
	model:SetAttribute("PieceId", id)
	model:SetAttribute("Item", rec.item)
	model:SetAttribute("Kind", piece.kind)
	model:SetAttribute("Floor", rec.floor)
	model:SetAttribute("Tier", rec.tier)
	model:PivotTo(PlotService.pieceFrame(plot, rec))
	-- Decor in its slots.
	local root = model.PrimaryPart
	for slot, decorId in rec.decor do
		local at = root and root:FindFirstChild(`Decor_{slot}`)
		if decorId ~= "" and at and at:IsA("Attachment") and Pieces.decor(decorId) then
			local d = HotelKit.decor(decorId, plot.location)
			d:PivotTo(at.WorldCFrame)
			d.Parent = model
		end
	end
	-- Its name over the door.
	local sign = root and root:FindFirstChild("Sign")
	if sign then
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
		text.Text = `{piece.name} T{rec.tier}`
		text.Parent = gui
		gui.Parent = sign
	end
	model.Parent = plot.model:FindFirstChild("Pieces")
	if piece.kind == "Room" then
		roomPrompts(plot, model, id)
	end
	plot.pieces[id] = model
	return model
end

-- Builds everything of a plot from its owner's data, from scratch.
local function buildHotel(plot: Plot, data: PlayerData.Data?)
	for _, child in plot.model:GetChildren() do
		child:Destroy()
	end
	plot.pieces = {}
	plot.stairs = {}
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
	local root = lobby.PrimaryPart :: BasePart
	local desk = root:FindFirstChild("Desk")
	local till = root:FindFirstChild("Till")
	if desk then
		makePrompt(desk, "Check in", "Front Desk", Constants.Stay.CheckInHold, plot, "Desk", nil)
	end
	if till then
		makePrompt(till, "Collect", "Till", 0, plot, "Till", nil)
	end

	local sign = HotelKit.sign(plot.location)
	local board = root:FindFirstChild("SignBoard") :: Attachment?
	if board then
		sign:PivotTo(board.WorldCFrame)
	end
	sign.Parent = plot.model
	plot.sign = sign

	local facade = HotelKit.facade(plot.location, data.floors)
	placeLocal(facade, plot.frame)
	facade.Parent = plot.model

	for floor = 2, data.floors do
		local slab = HotelKit.slab(plot.location, floor)
		placeLocal(slab, plot.frame)
		slab.Parent = plot.model
	end
	local sc = G.StairCore
	local coreCentre =
		Vector3.new((sc.x + sc.w / 2) * G.CellSize, 0, (sc.z + sc.d / 2) * G.CellSize)
	for floor = 1, data.floors - 1 do
		local stairs = HotelKit.stairs(plot.location, floor == data.floors - 1)
		stairs.Name = `Stairs_{floor}`
		stairs:PivotTo(plot.frame * CFrame.new(coreCentre + Vector3.new(0, Grid.floorY(floor), 0)))
		stairs.Parent = plot.model
		plot.stairs[floor] = stairs
	end

	for id, rec in data.layout do
		buildPiece(plot, id, rec)
	end
	if plot.owner then
		PlotService.refreshTraps(plot.owner)
	end
	for _, handler in builtHandlers do
		task.spawn(handler, plot)
	end
end

-- The lobby's traps (§8.1), drawn at its `Trap_n` attachments (a blockout until the kit has them).
function PlotService.refreshTraps(player: Player)
	local plot = byPlayer[player]
	local data = PlayerData.get(player)
	local root = plot and plot.lobby and plot.lobby.PrimaryPart
	if not plot or not data or not root then
		return
	end
	local old = plot.model:FindFirstChild("Traps")
	if old then
		old:Destroy()
	end
	local folder = Instance.new("Folder")
	folder.Name = "Traps"
	for slot, id in data.traps do
		local a = root:FindFirstChild(`Trap_{slot}`) :: Attachment?
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
			part.CFrame = a.WorldCFrame * CFrame.new(0, 0.15, 0)
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
		buildPiece(plot, id, data.layout[id])
	end
end

function PlotService.removePiece(player: Player, id: string)
	local plot = byPlayer[player]
	if plot and plot.pieces[id] then
		plot.pieces[id]:Destroy()
		plot.pieces[id] = nil
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

-- The world frame of an attachment on one of a plot's pieces, or nil.
function PlotService.piecePoint(plot: Plot, pieceId: string, name: string): CFrame?
	local model = plot.pieces[pieceId]
	local root = model and model.PrimaryPart
	local a = root and root:FindFirstChild(name)
	return if a and a:IsA("Attachment") then a.WorldCFrame else nil
end

-- The guests' glide up one flight of stairs, from the lower floor: Bottom, Path_n..., Top.
function PlotService.stairPath(plot: Plot, lowerFloor: number): { Vector3 }
	local model = plot.stairs[lowerFloor]
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

local function buildStreet()
	local old = workspace:FindFirstChild("Street")
	if old then
		old:Destroy()
	end
	local street = Instance.new("Folder")
	street.Name = "Street"
	local half = Constants.Street.LaneHalfLength
	local th = G.SlabThickness
	local function block(
		name: string,
		size: Vector3,
		at: Vector3,
		colour: Color3,
		material: Enum.Material?
	)
		local p = Instance.new("Part")
		p.Name = name
		p.Anchored = true
		p.Size = size
		p.CFrame = CFrame.new(at)
		p.Color = colour
		p.Material = material or Enum.Material.Cobblestone
		p.TopSurface = Enum.SurfaceType.Smooth
		p.Parent = street
		return p
	end
	local front = Constants.Street.FrontOffset
	block(
		"Lane",
		Vector3.new(2 * half + 40, th, 2 * front),
		Vector3.new(0, th / 2, 0),
		Color3.fromRGB(75, 70, 90)
	)
	block(
		"Kerb_North",
		Vector3.new(2 * half + 40, 0.3, 1),
		Vector3.new(0, th + 0.15, front - 0.5),
		Color3.fromRGB(120, 110, 140),
		Enum.Material.SmoothPlastic
	)
	block(
		"Kerb_South",
		Vector3.new(2 * half + 40, 0.3, 1),
		Vector3.new(0, th + 0.15, -front + 0.5),
		Color3.fromRGB(120, 110, 140),
		Enum.Material.SmoothPlastic
	)
	local stop = block(
		"BusStop",
		Vector3.new(8, 0.4, 6),
		StreetLayout.BusStop + Vector3.new(0, 0.2, -10),
		Color3.fromRGB(240, 150, 60),
		Enum.Material.SmoothPlastic
	)
	stop:SetAttribute("BusStop", true)
	block(
		"BusStopSign",
		Vector3.new(0.6, 8, 0.6),
		StreetLayout.BusStop + Vector3.new(3, 4, -12),
		Color3.fromRGB(60, 50, 70),
		Enum.Material.Metal
	)
	-- Lamps along the lane, both sides.
	for x = -half, half, 32 do
		for _, side in { 1, -1 } do
			local post = block(
				"LampPost",
				Vector3.new(0.6, 10, 0.6),
				Vector3.new(x, th + 5, side * (front - 3)),
				Color3.fromRGB(40, 35, 50),
				Enum.Material.Metal
			)
			local bulb = block(
				"Glow_Warm_1",
				Vector3.new(1.4, 1.4, 1.4),
				Vector3.new(x, th + 10.5, side * (front - 3)),
				Color3.fromRGB(255, 190, 110),
				Enum.Material.Neon
			)
			bulb.Shape = Enum.PartType.Ball
			bulb.CanCollide = false
			local light = Instance.new("PointLight")
			light.Range = 24
			light.Brightness = 0.9
			light.Color = Color3.fromRGB(255, 190, 120)
			light.Parent = bulb
			post.CanCollide = true
		end
	end
	street.Parent = workspace

	-- Cozy-creepy night (GDD §12): moonlight blue and purple, never black.
	Lighting.ClockTime = 0.5
	Lighting.Brightness = 2
	Lighting.Ambient = Color3.fromRGB(105, 95, 140)
	Lighting.OutdoorAmbient = Color3.fromRGB(125, 115, 165)
	Lighting.FogColor = Color3.fromRGB(40, 30, 70)
	Lighting.FogStart = 250
	Lighting.FogEnd = 900
end

function PlotService.Init()
	buildStreet()
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
			stairs = {},
			pieces = {},
			floors = 1,
		}
		plots[i] = plot
		buildHotel(plot, nil)
	end
	-- The place's own spawn and baseplate stay; the baseplate becomes night ground.
	local baseplate = workspace:FindFirstChild("Baseplate")
	if baseplate and baseplate:IsA("BasePart") then
		baseplate.Color = Color3.fromRGB(45, 55, 50)
		baseplate.Material = Enum.Material.Grass
	end
end

function PlotService.Start()
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
