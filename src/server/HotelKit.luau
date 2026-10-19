--!strict
--[[
	The hotel kit (MODELS.md, "Hotel kit"): every piece a hotel is built from.

	A delivered model wins: `ServerStorage.HotelKit.<Location>.<Name>` is cloned
	when it exists. Until the kit is modelled (WAITING.md §0), this file builds
	a **Luau blockout** of each piece (CLAUDE.md, "A blockout in Luau is
	allowed"): grey boxes in the piece's colour carrying exactly the attachments
	MODELS.md names, so a delivered model replaces geometry and nothing else.

	EVERY MEASUREMENT OF A BLOCKOUT STAYS IN THIS FILE. Everything else finds
	what it needs through the attachments (`Door`, `Bed`, `Desk`, `Queue_1`,
	`Path_1`, ...), never through a part's position or size.

	Frames are MODELS.md's: a piece is authored at rotation 0 with its door
	toward −Z and its pivot at the centre of its footprint on the walking
	surface (y = 0 is where feet stand).
]]

local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Locations = require(ReplicatedStorage.Shared.Locations)

local G = Constants.Grid
local CELL = G.CellSize
local WALL = G.WallHeight
local FLOOR = G.FloorHeight

local HotelKit = {}

type Props = { [string]: any }

local function part(parent: Instance, name: string, size: Vector3, at: Vector3, props: Props?): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Anchored = true
	p.Size = size
	p.CFrame = CFrame.new(at)
	p.Material = Enum.Material.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	for k, v in props or {} do
		(p :: any)[k] = v
	end
	p.Parent = parent
	return p
end

local function attach(root: BasePart, name: string, at: Vector3, look: Vector3?): Attachment
	local a = Instance.new("Attachment")
	a.Name = name
	local cf = if look then CFrame.lookAt(at, at + look) else CFrame.new(at)
	a.CFrame = root.CFrame:ToObjectSpace(cf)
	a.Parent = root
	return a
end

-- A model with an invisible `Root` part of `size`, its pivot at the origin.
local function shell(name: string, size: Vector3, centre: Vector3): (Model, Part)
	local model = Instance.new("Model")
	model.Name = name
	local root = part(model, "Root", size, centre, {
		Transparency = 1,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
	})
	model.PrimaryPart = root
	root.PivotOffset = root.CFrame:Inverse()
	return model, root
end

local function template(location: number, name: string): Model?
	local kit = ServerStorage:FindFirstChild("HotelKit")
	local folder = kit and kit:FindFirstChild(Locations.get(location).name:gsub(" ", ""))
	local found = folder and folder:FindFirstChild(name)
	if found and found:IsA("Model") then
		return found:Clone()
	end
	return nil
end

local function darker(c: Color3, f: number): Color3
	return Color3.new(c.R * f, c.G * f, c.B * f)
end

-- A lamp: a glow part (MODELS.md rule 1) with a light the code owns.
local function lamp(model: Model, n: number, at: Vector3, colour: Color3)
	local g = part(model, `Glow_Warm_{n}`, Vector3.new(0.8, 0.8, 0.8), at, {
		Shape = Enum.PartType.Ball,
		Material = Enum.Material.Neon,
		Color = colour,
		CanCollide = false,
		CastShadow = false,
	})
	local light = Instance.new("PointLight")
	light.Range = 12
	light.Brightness = 0.6
	light.Color = colour
	light.Shadows = false
	light.Parent = g
end

--[[ A room or an amenity (MODELS.md, "Rooms and amenities"). Walls in
	pieces apart round the door; the door opening 4 wide and 7 tall. ]]
local function blockoutPiece(id: string): Model
	local piece = assert(Pieces.get(id), id)
	local W, D = piece.w * CELL, piece.d * CELL
	local model, root = shell(id, Vector3.new(W, 0.2, D), Vector3.new(0, 0.1, 0))
	local colour = piece.colour
	local wallColour = darker(colour, 0.75)
	local t = 0.4

	part(
		model,
		"Floor",
		Vector3.new(W - 0.2, 0.2, D - 0.2),
		Vector3.new(0, 0.1, 0),
		{ Color = darker(colour, 0.55) }
	)
	part(
		model,
		"Wall_Back",
		Vector3.new(W, WALL, t),
		Vector3.new(0, WALL / 2, D / 2 - t / 2),
		{ Color = wallColour }
	)
	part(
		model,
		"Wall_Left",
		Vector3.new(t, WALL, D - 2 * t),
		Vector3.new(-W / 2 + t / 2, WALL / 2, 0),
		{ Color = wallColour }
	)
	part(
		model,
		"Wall_Right",
		Vector3.new(t, WALL, D - 2 * t),
		Vector3.new(W / 2 - t / 2, WALL / 2, 0),
		{ Color = wallColour }
	)

	-- The front wall, round the door.
	local doorX = (math.floor((piece.w - 1) / 2) + 0.5) * CELL - W / 2
	local doorW, doorH = 4, 7
	local leftEnd, rightStart = doorX - doorW / 2, doorX + doorW / 2
	local z = -D / 2 + t / 2
	if leftEnd > -W / 2 then
		local len = leftEnd + W / 2
		part(
			model,
			"Wall_FrontLeft",
			Vector3.new(len, WALL, t),
			Vector3.new(-W / 2 + len / 2, WALL / 2, z),
			{ Color = wallColour }
		)
	end
	if rightStart < W / 2 then
		local len = W / 2 - rightStart
		part(
			model,
			"Wall_FrontRight",
			Vector3.new(len, WALL, t),
			Vector3.new(W / 2 - len / 2, WALL / 2, z),
			{ Color = wallColour }
		)
	end
	part(
		model,
		"Wall_Lintel",
		Vector3.new(doorW, WALL - doorH, t),
		Vector3.new(doorX, doorH + (WALL - doorH) / 2, z),
		{ Color = wallColour }
	)

	if piece.kind == "Room" then
		-- A bed against the back wall, and the guest's spot beside it.
		part(
			model,
			"Bed",
			Vector3.new(4, 1.6, 5.5),
			Vector3.new(0, 0.8, D / 2 - 3.4),
			{ Color = colour }
		)
		part(
			model,
			"Pillow",
			Vector3.new(3, 0.6, 1.2),
			Vector3.new(0, 1.9, D / 2 - 1.4),
			{ Color = Color3.fromRGB(240, 235, 250) }
		)
		attach(root, "Bed", Vector3.new(0, 0, D / 2 - 7), Vector3.new(0, 0, -1))
	else
		-- An amenity's centrepiece.
		part(
			model,
			"Centrepiece",
			Vector3.new(W * 0.45, 3, D * 0.3),
			Vector3.new(0, 1.5, D / 6),
			{ Color = colour }
		)
		attach(root, "Bed", Vector3.new(0, 0, -D / 6), Vector3.new(0, 0, 1))
	end

	attach(root, "Door", Vector3.new(doorX, 0, -D / 2), Vector3.new(0, 0, -1))
	attach(root, "Sign", Vector3.new(doorX, doorH + 1.2, -D / 2 - 0.3), Vector3.new(0, 0, -1))
	attach(root, "Decor_1", Vector3.new(-W / 2 + 2, 0, D / 2 - 2), Vector3.new(1, 0, -1))
	attach(root, "Decor_2", Vector3.new(W / 2 - 2, 0, D / 2 - 2), Vector3.new(-1, 0, -1))
	attach(root, "Decor_3", Vector3.new(-W / 2 + 2, 0, 0), Vector3.new(1, 0, 0))
	lamp(model, 1, Vector3.new(0, WALL - 1, D / 2 - 1), Color3.fromRGB(255, 200, 140))
	return model
end

function HotelKit.piece(id: string, location: number): Model
	return template(location, id) or blockoutPiece(id)
end

-- A decor piece (MODELS.md, "Decor"): origin at the centre of its base.
function HotelKit.decor(id: string, location: number): Model
	local found = template(location, `Decor_{id}`)
	if found then
		return found
	end
	local d = assert(Pieces.decor(id), id)
	local model, _ = shell(`Decor_{id}`, Vector3.new(2.5, 0.2, 2.5), Vector3.new(0, 0.1, 0))
	part(
		model,
		"Body",
		Vector3.new(2.5, 2.5, 2.5),
		Vector3.new(0, 1.25, 0),
		{ Color = d.colour, CanCollide = false }
	)
	return model
end

--[[ The lobby (MODELS.md, "Lobby"): the front two rows of floor 1, origin at
	the middle of its front edge, the street toward −Z. ]]
function HotelKit.lobby(location: number): Model
	local found = template(location, "Lobby")
	if found then
		return found
	end
	local loc = Locations.get(location)
	local L, Dp = G.Cells * CELL, G.LobbyRows * CELL
	local model, root = shell("Lobby", Vector3.new(L, 0.2, Dp), Vector3.new(0, 0.1, Dp / 2))
	part(
		model,
		"Rug",
		Vector3.new(L - 1, 0.1, Dp - 1),
		Vector3.new(0, 0.05, Dp / 2),
		{ Color = darker(loc.facade, 0.8), CanCollide = false }
	)
	part(
		model,
		"Desk",
		Vector3.new(10, 3.5, 2),
		Vector3.new(-12, 1.75, 9),
		{ Color = Color3.fromRGB(110, 70, 50) }
	)
	part(
		model,
		"DeskTop",
		Vector3.new(10.4, 0.3, 2.4),
		Vector3.new(-12, 3.65, 9),
		{ Color = loc.trim }
	)
	part(
		model,
		"Till",
		Vector3.new(3, 3.5, 2),
		Vector3.new(12, 1.75, 9),
		{ Color = Color3.fromRGB(70, 60, 50) }
	)
	part(
		model,
		"TillTop",
		Vector3.new(2, 1.2, 1.4),
		Vector3.new(12, 4.1, 9),
		{ Color = Color3.fromRGB(230, 200, 90) }
	)
	-- The front arch.
	part(model, "ArchLeft", Vector3.new(1, 9, 1), Vector3.new(-5, 4.5, 0.5), { Color = loc.trim })
	part(model, "ArchRight", Vector3.new(1, 9, 1), Vector3.new(5, 4.5, 0.5), { Color = loc.trim })
	part(model, "ArchTop", Vector3.new(11, 1, 1), Vector3.new(0, 9.5, 0.5), { Color = loc.trim })
	lamp(model, 1, Vector3.new(0, 8.5, 1.5), Color3.fromRGB(255, 190, 120))
	lamp(model, 2, Vector3.new(-12, 6, 10), Color3.fromRGB(255, 190, 120))

	attach(root, "Entrance", Vector3.new(0, 0, 0), Vector3.new(0, 0, -1))
	attach(root, "Desk", Vector3.new(-12, 3.8, 7.8), Vector3.new(0, 0, -1))
	for i = 1, 4 do
		attach(root, `Queue_{i}`, Vector3.new(-12 - 4 * (i - 1), 0, 5.5), Vector3.new(0, 0, 1))
	end
	attach(root, "Till", Vector3.new(12, 3.8, 7.8), Vector3.new(0, 0, -1))
	attach(root, "Spawn", Vector3.new(4, 0, 8), Vector3.new(0, 0, -1))
	attach(root, "SignBoard", Vector3.new(0, 0, -7), Vector3.new(0, 0, -1))
	for i = 1, 3 do
		attach(root, `Trap_{i}`, Vector3.new(-24 + 16 * i, 0, 3), Vector3.new(0, 0, -1))
	end
	return model
end

--[[ One storey of the stair core (MODELS.md, "Stair core"), from a floor to
	the next: a switchback of two flights of five 1.2-stud steps, 1.5 deep and
	6 wide, with a landing 4 deep between them (the first draft's 2-stud
	landing jammed a walker against the divider, 2026-10-19). Origin at the
	core's footprint centre on the lower floor. `top` adds the railings the
	topmost floor needs round the open stairwell. ]]
function HotelKit.stairs(location: number, top: boolean): Model
	local found = template(location, if top then "StairCoreTop" else "StairCore")
	if found then
		return found
	end
	local loc = Locations.get(location)
	local S = G.StairCore.w * CELL -- 12
	local model, root = shell("StairCore", Vector3.new(S, 0.2, S), Vector3.new(0, 0.1, 0))
	local stepColour = darker(loc.facade, 1.1)
	local wallColour = darker(loc.facade, 0.7)
	local steps, tread = 5, 1.5
	local rise = FLOOR / 2 / steps
	-- In the core's frame: x −6..6, z −6..6. The flight up climbs +Z on the left half (x < 0)
	-- from z0, the flight down comes back −Z on the right half.
	local z0 = -S / 2 + 0.5
	local landingStart = z0 + tread * steps
	local landingDepth = S / 2 - landingStart
	for i = 1, steps do
		local zc = z0 + tread * (i - 0.5)
		part(
			model,
			`Step_Up_{i}`,
			Vector3.new(S / 2, 1, tread),
			Vector3.new(-S / 4, rise * i - 0.5, zc),
			{ Color = stepColour }
		)
	end
	local landingY = rise * steps
	part(
		model,
		"Landing",
		Vector3.new(S, 1, landingDepth),
		Vector3.new(0, landingY - 0.5, landingStart + landingDepth / 2),
		{ Color = stepColour }
	)
	for i = 1, steps do
		local zc = landingStart - tread * (i - 0.5)
		local h = landingY + rise * i
		-- The last step reaches back to the core's edge, under the upper slab's lip.
		local front = if i == steps then -S / 2 else zc - tread / 2
		local back = zc + tread / 2
		part(
			model,
			`Step_Down_{i}`,
			Vector3.new(S / 2, 1, back - front),
			Vector3.new(S / 4, h - 0.5, (front + back) / 2),
			{ Color = stepColour }
		)
	end
	-- Walls: the outer sides and the back, and the divider between the flights.
	local h = FLOOR + (if top then 3.5 else 0)
	local t = 0.4
	part(
		model,
		"Wall_Left",
		Vector3.new(t, h, S),
		Vector3.new(-S / 2 + t / 2, h / 2, 0),
		{ Color = wallColour }
	)
	part(
		model,
		"Wall_Right",
		Vector3.new(t, h, S),
		Vector3.new(S / 2 - t / 2, h / 2, 0),
		{ Color = wallColour }
	)
	part(
		model,
		"Wall_Back",
		Vector3.new(S, h, t),
		Vector3.new(0, h / 2, S / 2 - t / 2),
		{ Color = wallColour }
	)
	part(
		model,
		"Divider",
		Vector3.new(t, h, landingStart - z0),
		Vector3.new(0, h / 2, (z0 + landingStart) / 2),
		{ Color = wallColour }
	)
	if top then
		-- The topmost floor has no flight up: rail the stairwell's open edge above the flight up.
		part(
			model,
			"Rail_Top",
			Vector3.new(S / 2, 3.5, t),
			Vector3.new(-S / 4, FLOOR + 1.75, -S / 2 + 1),
			{ Color = wallColour }
		)
	end
	-- The guests' glide: bottom, the turn at the landing, the top.
	local mid = landingStart + landingDepth / 2
	attach(root, "Bottom", Vector3.new(-S / 4, 0, z0 - 0.25))
	attach(root, "Path_1", Vector3.new(-S / 4, landingY, mid))
	attach(root, "Path_2", Vector3.new(S / 4, landingY, mid))
	attach(root, "Top", Vector3.new(S / 4, FLOOR, z0 - 0.25))
	return model
end

--[[ A floor above the first: a slab over the whole grid but the stairwell,
	railings round its edge, and corner posts. Plot-local, as a Folder. ]]
function HotelKit.slab(location: number, floor: number): Folder
	local loc = Locations.get(location)
	local folder = Instance.new("Folder")
	folder.Name = `Slab_{floor}`
	local P = G.Cells * CELL
	local y = (floor - 1) * FLOOR
	local th = G.SlabThickness
	local sc = G.StairCore
	local hx0, hx1 = sc.x * CELL, (sc.x + sc.w) * CELL
	local hz0, hz1 = sc.z * CELL + 1, (sc.z + sc.d) * CELL
	local colour = darker(loc.facade, 0.9)
	local function slabPart(name: string, x0: number, x1: number, z0: number, z1: number)
		if x1 > x0 and z1 > z0 then
			part(
				folder,
				name,
				Vector3.new(x1 - x0, th, z1 - z0),
				Vector3.new((x0 + x1) / 2, y + th / 2, (z0 + z1) / 2),
				{ Color = colour }
			)
		end
	end
	slabPart("Slab_A", 0, hx0, 0, P)
	slabPart("Slab_B", hx0, hx1, 0, hz0)
	slabPart("Slab_C", hx0, hx1, hz1, P)
	slabPart("Slab_D", hx1, P, 0, P)
	-- Railings round the edge, 3.5 studs (against the 5-stud person).
	local rh, rt = 3.5, 0.4
	local top = y + th
	part(
		folder,
		"Rail_Front",
		Vector3.new(P, rh, rt),
		Vector3.new(P / 2, top + rh / 2, rt / 2),
		{ Color = loc.trim }
	)
	part(
		folder,
		"Rail_Back",
		Vector3.new(P, rh, rt),
		Vector3.new(P / 2, top + rh / 2, P - rt / 2),
		{ Color = loc.trim }
	)
	part(
		folder,
		"Rail_Left",
		Vector3.new(rt, rh, P),
		Vector3.new(rt / 2, top + rh / 2, P / 2),
		{ Color = loc.trim }
	)
	part(
		folder,
		"Rail_Right",
		Vector3.new(rt, rh, P),
		Vector3.new(P - rt / 2, top + rh / 2, P / 2),
		{ Color = loc.trim }
	)
	for _, c in
		{
			Vector2.new(0.5, 0.5),
			Vector2.new(P - 0.5, 0.5),
			Vector2.new(0.5, P - 0.5),
			Vector2.new(P - 0.5, P - 0.5),
		}
	do
		part(
			folder,
			"Post",
			Vector3.new(1, FLOOR - th, 1),
			Vector3.new(c.X, y - (FLOOR - th) / 2, c.Y),
			{ Color = darker(loc.facade, 0.6) }
		)
	end
	return folder
end

--[[ The ground: the plot's base, its lobby floor and the Resident Wing's
	garden behind (Appendix A.1). Plot-local, as a Folder. ]]
function HotelKit.base(location: number): Folder
	local loc = Locations.get(location)
	local folder = Instance.new("Folder")
	folder.Name = "Base"
	local P = G.Cells * CELL
	local th = G.SlabThickness
	part(
		folder,
		"Ground",
		Vector3.new(P, th, P),
		Vector3.new(P / 2, th / 2, P / 2),
		{ Color = loc.ground }
	)
	local wing = part(
		folder,
		"Wing",
		Vector3.new(P, th, G.WingDepth),
		Vector3.new(P / 2, th / 2, P + G.WingDepth / 2),
		{
			Color = Color3.fromRGB(70, 110, 70),
			Material = Enum.Material.Grass,
		}
	)
	wing:SetAttribute("Wing", true)
	local fh = 2.5
	part(
		folder,
		"Fence_Back",
		Vector3.new(P, fh, 0.4),
		Vector3.new(P / 2, th + fh / 2, P + G.WingDepth - 0.2),
		{ Color = loc.trim }
	)
	part(
		folder,
		"Fence_Left",
		Vector3.new(0.4, fh, G.WingDepth),
		Vector3.new(0.2, th + fh / 2, P + G.WingDepth / 2),
		{ Color = loc.trim }
	)
	part(
		folder,
		"Fence_Right",
		Vector3.new(0.4, fh, G.WingDepth),
		Vector3.new(P - 0.2, th + fh / 2, P + G.WingDepth / 2),
		{ Color = loc.trim }
	)
	return folder
end

--[[ The hotel sign (MODELS.md, "Facade and sign"): posts and a `Board`
	whose Front face (−Z) takes the sign's SurfaceGui. Origin at its base. ]]
function HotelKit.sign(location: number): Model
	local found = template(location, "HotelSign")
	if found then
		return found
	end
	local loc = Locations.get(location)
	local model, _ = shell("HotelSign", Vector3.new(16, 0.2, 1), Vector3.new(0, 0.1, 0))
	part(
		model,
		"PostLeft",
		Vector3.new(0.8, 6, 0.8),
		Vector3.new(-7, 3, 0),
		{ Color = darker(loc.facade, 0.6) }
	)
	part(
		model,
		"PostRight",
		Vector3.new(0.8, 6, 0.8),
		Vector3.new(7, 3, 0),
		{ Color = darker(loc.facade, 0.6) }
	)
	part(
		model,
		"Board",
		Vector3.new(16, 6, 0.6),
		Vector3.new(0, 8, 0),
		{ Color = darker(loc.facade, 0.5) }
	)
	return model
end

return HotelKit
