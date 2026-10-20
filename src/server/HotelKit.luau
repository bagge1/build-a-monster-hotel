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
local Grid = require(ReplicatedStorage.Shared.Grid)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Locations = require(ReplicatedStorage.Shared.Locations)
local Cosmetics = require(ReplicatedStorage.Shared.Cosmetics)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)

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

-- A delivered model's clone with `Root` as its PrimaryPart. Rojo's live sync of a
-- changed .rbxm can drop the reference (DEVNOTES.md, "Rojo's live sync drops
-- PrimaryPart"); `Root` is the contract's (MODELS.md), so it is set again here.
local function rooted(found: Model): Model
	local m = found:Clone()
	local root = m:FindFirstChild("Root")
	if not m.PrimaryPart and root and root:IsA("BasePart") then
		m.PrimaryPart = root
	end
	return m
end

-- The kit's delivered model `name` for a location, uncloned, or nil.
local function delivered(location: number, name: string): Model?
	local kit = ServerStorage:FindFirstChild("HotelKit")
	local folder = kit and kit:FindFirstChild((string.gsub(Locations.get(location).name, " ", "")))
	local found = folder and folder:FindFirstChild(name)
	return if found and found:IsA("Model") then found else nil
end

local function template(location: number, name: string): Model?
	local found = delivered(location, name)
	return if found then rooted(found) else nil
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
	pieces apart round the door; the door opening 4 wide and 7 tall, on its
	other front cell when `mirrored` (Flip, A.1). ]]
local function blockoutPiece(id: string, mirrored: boolean?): Model
	local piece = assert(Pieces.get(id), id)
	assert(piece.kind == "Room" or piece.kind == "Amenity", `{id} has no room blockout`)
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
	local doorX = (Grid.doorAlong(piece.w, mirrored) + 0.5) * CELL - W / 2
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
	lamp(model, 1, Vector3.new(0, WALL - 1, D / 2 - 1), Color3.fromRGB(255, 200, 140))
	return model
end

--[[ The front desk (MODELS.md, "Front desk"): 24 × 12, served toward −Z, the
	counter's top at 3.8, the clerk behind it, the key rack at the back. ]]
local function blockoutDesk(location: number): Model
	local loc = Locations.get(location)
	local model, root = shell("FrontDesk", Vector3.new(24, 0.2, 12), Vector3.new(0, 0.1, 0))
	part(
		model,
		"Counter",
		Vector3.new(9, 3.5, 1.8),
		Vector3.new(0, 1.75, -3.1),
		{ Color = Color3.fromRGB(110, 70, 50) }
	)
	part(
		model,
		"Counter",
		Vector3.new(9.4, 0.3, 2.3),
		Vector3.new(0, 3.65, -3.05),
		{ Color = loc.trim }
	)
	part(
		model,
		"Till",
		Vector3.new(1.2, 1.1, 1.2),
		Vector3.new(3.4, 4.35, -3.1),
		{ Color = Color3.fromRGB(230, 200, 90) }
	)
	part(
		model,
		"KeyRack",
		Vector3.new(5.2, 9.5, 0.85),
		Vector3.new(0, 4.75, 5.575),
		{ Color = Color3.fromRGB(80, 55, 40) }
	)
	lamp(model, 1, Vector3.new(-3.8, 4.6, -3.1), Color3.fromRGB(255, 190, 120))
	attach(root, "Desk", Vector3.new(0, 3.8, -4.2), Vector3.new(0, 0, -1))
	attach(root, "Till", Vector3.new(3.4, 3.8, -4.2), Vector3.new(0, 0, -1))
	attach(root, "Clerk", Vector3.new(0, 0, 1.5), Vector3.new(0, 0, -1))
	for i = 1, 4 do
		attach(root, `Queue_{i}`, Vector3.new(0, 0, -5 - 3 * i), Vector3.new(0, 0, 1))
	end
	return model
end

--[[ Whether a room or an amenity can be placed mirrored (Flip, A.1;
	MODELS.md: `<PieceId>_Mirror`): its kit has the mirror, or it is still a
	blockout, which mirrors itself. Roblox cannot mirror a mesh. ]]
function HotelKit.mirrorable(id: string, location: number): boolean
	local piece = Pieces.get(id)
	if not piece or (piece.kind ~= "Room" and piece.kind ~= "Amenity") then
		return false
	end
	return delivered(location, `{id}_Mirror`) ~= nil or delivered(location, id) == nil
end

--[[ A piece of the layout (Pieces): a room, an amenity or the front desk,
	mirrored (`<PieceId>_Mirror`) when `mirrored` and `mirrorable`. Stairs are
	`HotelKit.stairs`. ]]
function HotelKit.piece(id: string, location: number, mirrored: boolean?): Model
	if mirrored and HotelKit.mirrorable(id, location) then
		return template(location, `{id}_Mirror`) or blockoutPiece(id, true)
	end
	local found = template(location, id)
	if found then
		return found
	end
	if id == "FrontDesk" then
		return blockoutDesk(location)
	end
	return blockoutPiece(id)
end

--[[ The wooden plaque over a room's door (MODELS.md, "Room plaque"), or nil
	until the kit's is imported (the room then keeps floating text). Visual
	only: nothing collides or is hit by a ray. ]]
function HotelKit.plaque(location: number): Model?
	local m = template(location, "RoomPlaque")
	if not m then
		return nil
	end
	for _, p in m:GetDescendants() do
		if p:IsA("BasePart") then
			p.Anchored = true
			p.CanCollide = false
			p.CanQuery = false
			p.CanTouch = false
		end
	end
	return m
end

--[[ A decor piece (MODELS.md, "Decor"): origin at the centre of its
	footprint's base, front toward −Z; the blockout fills the footprint less
	the 0.4 inset, a rug to its edges and flat, a wall piece against the back. ]]
function HotelKit.decor(id: string, location: number): Model
	local found = template(location, `Decor_{id}`)
	if found then
		return found
	end
	local d = assert(Pieces.decor(id), id)
	local S = CELL / G.Squares
	local W, D = d.w * S, d.d * S
	local model, _ = shell(`Decor_{id}`, Vector3.new(W, 0.2, D), Vector3.new(0, 0.1, 0))
	local props = { Color = d.colour, CanCollide = false }
	if d.layer == "Rug" then
		part(model, "Body", Vector3.new(W, 0.1, D), Vector3.new(0, 0.05, 0), props)
	elseif d.layer == "Wall" then
		local depth = math.min(0.8, D - 0.8)
		part(
			model,
			"Body",
			Vector3.new(W - 0.8, d.height, depth),
			Vector3.new(0, d.height / 2, D / 2 - 0.4 - depth / 2),
			props
		)
	else
		part(
			model,
			"Body",
			Vector3.new(W - 0.8, d.height, D - 0.8),
			Vector3.new(0, d.height / 2, 0),
			props
		)
	end
	return model
end

--[[ A plate over the plot's cells not owned (§5.4, A.1: "cells not owned
	are not walked on and carry a dark plate on floor 1"), w × d studs, its
	top a hair over the ground. Centred at its origin. ]]
function HotelKit.tilePlate(location: number, w: number, d: number): Part
	local loc = Locations.get(location)
	local p = Instance.new("Part")
	p.Name = "TilePlate"
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Size = Vector3.new(w - 0.4, 0.1, d - 0.4)
	p.Material = Enum.Material.Fabric
	p.Color = darker(loc.facade, 0.35)
	return p
end

--[[ One storey of the stair core (MODELS.md, "Stair core"), from a floor to
	the next: a switchback of 15 steps of 1.2 rise and 1.5 tread, eight up to
	the landing and seven on to the floor above, each flight 12 wide, the
	landing 11.5 deep (a 2-stud landing jammed a walker against the divider,
	2026-10-19). Origin at the core's footprint centre on the lower floor.
	`top` adds the railings the topmost floor needs round the open stairwell. ]]
function HotelKit.stairs(location: number, top: boolean): Model
	local found = template(location, if top then "StairCoreTop" else "StairCore")
	if found then
		return found
	end
	local loc = Locations.get(location)
	local S = 2 * CELL -- 24: a 2 × 2 piece (Pieces "Stairs")
	local model, root = shell("StairCore", Vector3.new(S, 0.2, S), Vector3.new(0, 0.1, 0))
	local stepColour = darker(loc.facade, 1.1)
	local wallColour = darker(loc.facade, 0.7)
	local up, down, tread = 8, 7, 1.5
	local rise = FLOOR / (up + down) -- 1.2
	-- In the core's frame: x −12..12, z −12..12. The flight up climbs +Z on the left half (x < 0)
	-- from z0, the flight down comes back −Z on the right half.
	local z0 = -S / 2 + 0.5
	local landingStart = z0 + tread * up
	local landingDepth = S / 2 - landingStart
	for i = 1, up do
		local zc = z0 + tread * (i - 0.5)
		part(
			model,
			`Step_Up_{i}`,
			Vector3.new(S / 2, 1, tread),
			Vector3.new(-S / 4, rise * i - 0.5, zc),
			{ Color = stepColour }
		)
	end
	local landingY = rise * up
	part(
		model,
		"Landing",
		Vector3.new(S, 1, landingDepth),
		Vector3.new(0, landingY - 0.5, landingStart + landingDepth / 2),
		{ Color = stepColour }
	)
	for i = 1, down do
		local zc = landingStart - tread * (i - 0.5)
		local h = landingY + rise * i
		-- The last step reaches back to the core's edge, under the upper slab's lip.
		local front = if i == down then -S / 2 else zc - tread / 2
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

export type Hole = { x0: number, z0: number, x1: number, z1: number }

--[[ A floor above the first: a slab over that floor's owned tiles (`tiles`,
	by Grid.tileKey) but its stairwells (`holes`, plot-local studs: each
	stair's footprint less the 1-stud lip at its front, MODELS.md "Stairs").
	Every edge of it has a facade wall (his ruling, 2026-10-20), so it needs
	no railing. Plot-local, as a Folder. ]]
function HotelKit.slab(
	location: number,
	floor: number,
	holes: { Hole },
	tiles: { [number]: boolean }
): Folder
	local loc = Locations.get(location)
	local folder = Instance.new("Folder")
	folder.Name = `Slab_{floor}`
	local P = G.Cells * CELL
	local y = (floor - 1) * FLOOR
	local th = G.SlabThickness
	local colour = darker(loc.facade, 0.9)
	-- The slab as strips: cut the plot at every cell edge and every hole's edges, and lay each row's runs.
	local xs, zs = {}, {}
	for i = 0, G.Cells do
		table.insert(xs, i * CELL)
		table.insert(zs, i * CELL)
	end
	for _, h in holes do
		table.insert(xs, h.x0)
		table.insert(xs, h.x1)
		table.insert(zs, h.z0)
		table.insert(zs, h.z1)
	end
	table.sort(xs)
	table.sort(zs)
	local function solid(x: number, z: number): boolean
		if not tiles[Grid.tileKey(floor, x // CELL, z // CELL)] then
			return false
		end
		for _, h in holes do
			if x > h.x0 and x < h.x1 and z > h.z0 and z < h.z1 then
				return false
			end
		end
		return true
	end
	local function lay(a: number, b: number, z0: number, z1: number)
		part(
			folder,
			"Slab",
			Vector3.new(b - a, th, z1 - z0),
			Vector3.new((a + b) / 2, y + th / 2, (z0 + z1) / 2),
			{ Color = colour }
		)
	end
	for j = 1, #zs - 1 do
		local z0, z1 = zs[j], zs[j + 1]
		if z1 - z0 > 0.01 then
			local runStart: number? = nil
			for i = 1, #xs - 1 do
				local x0, x1 = xs[i], xs[i + 1]
				if x1 - x0 > 0.01 then
					local here = solid((x0 + x1) / 2, (z0 + z1) / 2)
					if here and runStart == nil then
						runStart = x0
					elseif not here and runStart ~= nil then
						lay(runStart :: number, x0, z0, z1)
						runStart = nil
					end
				end
			end
			if runStart ~= nil then
				lay(runStart :: number, P, z0, z1)
			end
		end
	end
	return folder
end

--[[ The window openings of each type (MODELS.md, `Facade_Window_<Type>`): its
	rough shape as rectangles (x0, x1, y0, y1) within x −4..4, y 3..13, and
	its trim. A blockout until the kit's windows exist. ]]
local WINDOW_HOLES: { [string]: { { number } } } = {
	TwinSash = { { -3.75, -0.25, 3, 12 }, { 0.25, 3.75, 3, 12 } },
	Arched = { { -2.5, 2.5, 3, 10 }, { -1.5, 1.5, 10, 12 }, { -0.5, 0.5, 12, 13 } },
	Round = { { -1.5, 1.5, 5.5, 11.5 }, { -2.5, 2.5, 6.5, 10.5 }, { -3, 3, 7.5, 9.5 } },
	Wide = { { -4, 4, 4, 10 } },
}

--[[ A wall section with rectangular `holes` cut out of it, as strips: the
	wall cut at every hole's edges, each band's solid runs laid as parts. ]]
local function holedWall(model: Model, holes: { { number } }, colour: Color3, t: number, zc: number)
	local xs, ys = { -6, 6 }, { 0, WALL }
	for _, h in holes do
		table.insert(xs, h[1])
		table.insert(xs, h[2])
		table.insert(ys, h[3])
		table.insert(ys, h[4])
	end
	table.sort(xs)
	table.sort(ys)
	local function open(x: number, y: number): boolean
		for _, h in holes do
			if x > h[1] and x < h[2] and y > h[3] and y < h[4] then
				return true
			end
		end
		return false
	end
	for j = 1, #ys - 1 do
		local y0, y1 = ys[j], ys[j + 1]
		if y1 - y0 > 0.01 then
			local function lay(a: number, b: number)
				part(
					model,
					"Wall",
					Vector3.new(b - a, y1 - y0, t),
					Vector3.new((a + b) / 2, (y0 + y1) / 2, zc),
					{ Color = colour }
				)
			end
			local runStart: number? = nil
			for i = 1, #xs - 1 do
				local x0, x1 = xs[i], xs[i + 1]
				if x1 - x0 > 0.01 then
					local solid = not open((x0 + x1) / 2, (y0 + y1) / 2)
					if solid and runStart == nil then
						runStart = x0
					elseif not solid and runStart ~= nil then
						lay(runStart :: number, x0)
						runStart = nil
					end
				end
			end
			if runStart ~= nil then
				lay(runStart :: number, 6)
			end
		end
	end
end

--[[ The facade's pieces (MODELS.md, "Facade"): each is one cell edge (two
	for the entrance), origin at the middle of the edge on the walking
	surface, the owned cell toward +Z and the wall just outside it (z −0.02 to
	−0.62), up to the slab above. A plain `Wall`, or `Window_<Type>` with one
	window (A.1). Blockouts until the kit's or a cosmetic's pieces exist;
	`scheme` is a facade cosmetic's colours. ]]
local function blockoutFacade(
	kind: string,
	location: number,
	scheme: { facade: Color3, trim: Color3 }?
): Model
	local loc = Locations.get(location)
	local wall = darker(if scheme then scheme.facade else loc.facade, 0.85)
	local trim = if scheme then scheme.trim else loc.trim
	local t, zc = 0.6, -0.32
	if kind == "Corner" then
		local model, _ =
			shell("Facade_Corner", Vector3.new(0.64, 0.2, 0.64), Vector3.new(-0.32, 0.1, -0.32))
		part(
			model,
			"Post",
			Vector3.new(0.64, WALL, 0.64),
			Vector3.new(-0.32, WALL / 2, -0.32),
			{ Color = darker(wall, 0.8) }
		)
		return model
	elseif kind == "Entrance" then
		local model, root =
			shell("Facade_Entrance", Vector3.new(24, 0.2, t), Vector3.new(0, 0.1, zc))
		-- Solid to either side of the arch; over it (a door's height) the wall goes on up to the slab.
		local arch, top = 5.5, 9
		for _, side in { -1, 1 } do
			part(
				model,
				if side < 0 then "Wall_Left" else "Wall_Right",
				Vector3.new(12 - arch, WALL, t),
				Vector3.new(side * (12 + arch) / 2, WALL / 2, zc),
				{ Color = wall }
			)
		end
		part(
			model,
			"ArchTop",
			Vector3.new(2 * arch, WALL - top, t),
			Vector3.new(0, (top + WALL) / 2, zc),
			{ Color = trim }
		)
		-- The arch's jambs: the opening between them is 9 wide.
		part(
			model,
			"ArchLeft",
			Vector3.new(1, top, 0.8),
			Vector3.new(-5, top / 2, -0.42),
			{ Color = trim }
		)
		part(
			model,
			"ArchRight",
			Vector3.new(1, top, 0.8),
			Vector3.new(5, top / 2, -0.42),
			{ Color = trim }
		)
		lamp(model, 1, Vector3.new(0, top + 1.5, -1.4), Color3.fromRGB(255, 190, 120))
		attach(root, "Entrance", Vector3.new(0, 0, 0), Vector3.new(0, 0, -1))
		return model
	end
	local windowType = string.match(kind, "^Window_(%a+)$")
	local holes = windowType and WINDOW_HOLES[windowType]
	if not holes then
		-- A plain wall section (his ruling, 2026-10-20: windows are placed).
		local model, _ = shell("Facade_Wall", Vector3.new(12, 0.2, t), Vector3.new(0, 0.1, zc))
		part(
			model,
			"Wall",
			Vector3.new(12, WALL, t),
			Vector3.new(0, WALL / 2, zc),
			{ Color = wall }
		)
		return model
	end
	local model, _ = shell(`Facade_{kind}`, Vector3.new(12, 0.2, t), Vector3.new(0, 0.1, zc))
	holedWall(model, holes, wall, t, zc)
	-- The sill under the lowest opening, 0.06 proud of both faces (coplanar faces flicker).
	local x0, x1, y0 = math.huge, -math.huge, math.huge
	for _, h in holes do
		x0, x1, y0 = math.min(x0, h[1]), math.max(x1, h[2]), math.min(y0, h[3])
	end
	part(
		model,
		"Sill",
		Vector3.new(x1 - x0 + 0.6, 0.4, t + 0.12),
		Vector3.new(0, y0 - 0.2, zc),
		{ Color = trim }
	)
	if windowType == "Wide" then
		-- Three panes, and a flower box under them outside.
		for _, x in { -4 / 3, 4 / 3 } do
			part(
				model,
				"Mullion",
				Vector3.new(0.3, 6, 0.3),
				Vector3.new(x, 7, zc),
				{ Color = trim }
			)
		end
		part(
			model,
			"FlowerBox",
			Vector3.new(8.4, 0.9, 1),
			Vector3.new(0, 3.35, -1.12),
			{ Color = trim }
		)
		part(
			model,
			"Flowers",
			Vector3.new(8, 0.5, 0.7),
			Vector3.new(0, 4.05, -1.12),
			{ Color = Color3.fromRGB(150, 60, 120), CanCollide = false }
		)
	elseif windowType == "TwinSash" then
		for _, x in { -2, 2 } do
			part(
				model,
				"SashBar",
				Vector3.new(3.5, 0.25, 0.3),
				Vector3.new(x, 7.5, zc),
				{ Color = trim }
			)
		end
	end
	return model
end

-- A worn facade cosmetic's own piece (MODELS.md, "Cosmetics": a Folder of facade pieces), or nil.
local function cosmeticFacade(id: string, name: string): Model?
	local kit = ServerStorage:FindFirstChild("Cosmetics")
	local folder = kit and kit:FindFirstChild(id)
	local found = if folder and folder:IsA("Folder") then folder:FindFirstChild(name) else nil
	return if found and found:IsA("Model") then rooted(found) else nil
end

--[[ The facade (MODELS.md, "Facade"; his ruling, 2026-10-20: "It should only
	have walls where you have unlocked"): a piece on every edge and corner of
	the owned tiles' outline on every floor (`Grid.facade`), the entrance arch
	on floor 1's front edge, the street side open above floor 1, and on a wall
	section in `windows` (its edge key → type) that window (A.1). Each piece
	is a worn facade cosmetic's (`cosmetic`), else the kit's
	(`ServerStorage.HotelKit.<Location>`), else a blockout, in the
	cosmetic's colours when it has no pieces of its own. Plot-local, as a
	Folder. ]]
function HotelKit.facade(
	location: number,
	floors: number,
	tiles: { [number]: boolean },
	cosmetic: Cosmetics.Cosmetic?,
	windows: { [string]: string }?
): Folder
	local folder = Instance.new("Folder")
	folder.Name = "Facade"
	local scheme = if cosmetic
		then { facade = cosmetic.colour, trim = cosmetic.trim or cosmetic.colour }
		else nil
	local sources: { [string]: Model } = {}
	local function source(kind: string): Model
		local found = sources[kind]
		if found then
			return found
		end
		local name = `Facade_{kind}`
		local m = (cosmetic and cosmeticFacade(cosmetic.id, name))
			or template(location, name)
			or blockoutFacade(kind, location, scheme)
		for _, d in m:GetDescendants() do
			if d:IsA("BasePart") then
				d.Anchored = true
			end
		end
		sources[kind] = m
		return m
	end
	for _, f in Grid.facade(tiles, floors, windows) do
		local m = source(if f.window then `Window_{f.window}` else f.kind):Clone()
		m.PrimaryPart = m:FindFirstChild("Root") :: BasePart?
		m:PivotTo(CFrame.new(f.at) * CFrame.Angles(0, f.turn * math.pi / 2, 0))
		m:SetAttribute("Floor", f.floor)
		if f.kind == "Wall" then
			-- The build mode taps a wall section by it (A.1: windows).
			m:SetAttribute(
				"Edge",
				Grid.edgeKey(f.floor, f.x :: number, f.z :: number, f.side :: number)
			)
			m:SetAttribute("Window", f.window)
		end
		m.Parent = folder
	end
	for _, m in sources do
		m:Destroy()
	end
	return folder
end

--[[ The forecourt's yard (MODELS.md, "Forecourt"; his yes, 2026-10-19,
	GDD §5.4): the 16 studs between the pavement and the front wall, with the
	path to the arch, the sign's corner and the three trap squares. Origin at
	the entrance, the street toward −Z. ]]
function HotelKit.forecourt(location: number): Model
	local found = template(location, "Forecourt")
	if found then
		return found
	end
	local loc = Locations.get(location)
	local St = Constants.Street
	local P = G.Cells * CELL
	local depth = St.ForecourtDepth - St.PavementWidth -- 16: the pavement is the street's
	local th = G.SlabThickness
	local model, root =
		shell("Forecourt", Vector3.new(P, 0.2, depth), Vector3.new(0, 0.1, -depth / 2))
	part(model, "Yard", Vector3.new(P, th, depth), Vector3.new(0, -th / 2, -depth / 2), {
		Color = darker(loc.ground, 0.9),
		Material = Enum.Material.Grass,
	})
	-- The path to the arch, a hair proud of the yard (coplanar faces flicker).
	local w = St.PathWidth
	part(model, "Path", Vector3.new(w, 0.1, depth), Vector3.new(0, 0, -depth / 2), {
		Color = darker(loc.trim, 0.55),
		Material = Enum.Material.Cobblestone,
	})
	-- A low edging along the pavement either side of the path, never across it.
	for _, s in { -1, 1 } do
		local x0, x1 = w / 2 + 0.5, P / 2
		part(
			model,
			if s < 0 then "Edge_Left" else "Edge_Right",
			Vector3.new(x1 - x0, 0.5, 0.6),
			Vector3.new(s * (x0 + x1) / 2, 0.25, -depth + 0.3),
			{ Color = loc.trim }
		)
	end
	attach(root, "PathFoot", Vector3.new(0, 0, -depth), Vector3.new(0, 0, 1))
	attach(root, "SignBoard", Vector3.new(60, 0, -12), Vector3.new(0, 0, -1))
	for i, at in { Vector3.new(-8, 0, -12), Vector3.new(8, 0, -12), Vector3.new(-8, 0, -4) } do
		attach(root, `Trap_{i}`, at, Vector3.new(0, 0, -1))
	end
	return model
end

--[[ The ground: the plot's base, the Resident Wing's garden
	behind (Appendix A.1) and the forecourt's yard in front (§5.4). Plot-local,
	as a Folder. ]]
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
	local forecourt = HotelKit.forecourt(location)
	forecourt:PivotTo(CFrame.new(StreetLayout.EntranceLocal))
	forecourt.Parent = folder
	return folder
end

--[[ A sign or lobby cosmetic (MODELS.md, "Cosmetics"): its template, or a
	blockout. Origin per slot: a sign's at the Board's front-face centre, a
	lobby's at the Entrance threshold, front toward −Z. ]]
function HotelKit.cosmetic(c: Cosmetics.Cosmetic): Model
	local kit = ServerStorage:FindFirstChild("Cosmetics")
	local found = kit and kit:FindFirstChild(c.id)
	if found and found:IsA("Model") then
		local m = rooted(found)
		for _, p in m:GetDescendants() do
			if p:IsA("BasePart") then
				p.Anchored = true
				p.CanCollide, p.CanQuery, p.CanTouch = false, false, false
			end
		end
		return m
	end
	local props = { Color = c.colour, CanCollide = false, CanQuery = false, CanTouch = false }
	if c.slot == "Sign" then
		-- A frame round the board's top and sides, standing proud of its face.
		local model, _ = shell(c.id, Vector3.new(1, 0.2, 1), Vector3.new(0, 0, -0.3))
		part(model, "Top", Vector3.new(17, 1.2, 0.6), Vector3.new(0, 3.4, -0.3), props)
		part(model, "Left", Vector3.new(1, 6, 0.6), Vector3.new(-8.3, 0, -0.3), props)
		part(model, "Right", Vector3.new(1, 6, 0.6), Vector3.new(8.3, 0, -0.3), props)
		part(model, "Crest", Vector3.new(2.4, 2.4, 0.6), Vector3.new(0, 5, -0.3), props)
		return model
	end
	-- A lobby cosmetic: a garland across the entrance, its lowest part 9 studs up.
	local model, _ = shell(c.id, Vector3.new(1, 0.2, 1), Vector3.new(0, 0.1, 0))
	local glow = c.id == "Cosmetic_FairyLights"
	for i = -5, 5 do
		local sag = (25 - i * i) * 0.06
		local p = part(
			model,
			`Bit_{i + 6}`,
			Vector3.new(0.8, 0.8, 0.2),
			Vector3.new(i * 1.1, 10.5 - sag, -0.6),
			props
		)
		if glow then
			p.Material = Enum.Material.Neon
		end
	end
	return model
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
