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

local function template(location: number, name: string): Model?
	local kit = ServerStorage:FindFirstChild("HotelKit")
	local folder = kit and kit:FindFirstChild((string.gsub(Locations.get(location).name, " ", "")))
	local found = folder and folder:FindFirstChild(name)
	if found and found:IsA("Model") then
		return rooted(found)
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

--[[ The lobby (MODELS.md, "Lobby"): the front two rows of floor 1, 144 × 24
	studs, origin at the middle of its front edge, the street toward −Z. An
	indoor reception (his pick, 2026-10-19, at the doubled scale of the same
	evening): a front wall up to the slab round the entrance arch, the desk
	across the −X end served toward +X, the back row (z 12–24) clear for the
	floor-1 doors, benches in the front row on the stair side. The arch, the
	counter and the benches are a person's size, not the grid's. ]]
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
		Vector3.new(L, 0.1, Dp),
		Vector3.new(0, 0.05, Dp / 2),
		{ Color = darker(loc.facade, 0.8), CanCollide = false }
	)
	-- The front wall up to the slab, two pieces apart round the arch (each exactly the kit's box).
	local wallColour = darker(loc.facade, 0.85)
	local half, arch, top, t = L / 2, 5.5, WALL, 0.8
	for _, side in { -1, 1 } do
		part(
			model,
			if side < 0 then "Wall_FrontLeft" else "Wall_FrontRight",
			Vector3.new(half - arch, top, t),
			Vector3.new(side * (half + arch) / 2, top / 2, t / 2),
			{ Color = wallColour }
		)
	end
	part(model, "ArchLeft", Vector3.new(1, 9, 1), Vector3.new(-5, 4.5, 0.5), { Color = loc.trim })
	part(model, "ArchRight", Vector3.new(1, 9, 1), Vector3.new(5, 4.5, 0.5), { Color = loc.trim })
	-- Over the arch (a door's height) the wall goes on up to the slab.
	part(
		model,
		"ArchTop",
		Vector3.new(11, top - 9, 1),
		Vector3.new(0, (9 + top) / 2, 0.5),
		{ Color = loc.trim }
	)
	-- The desk: the counter x −63..−61.2, z 1.5..10.5, its top 3.8; the till on its far end.
	part(
		model,
		"Desk",
		Vector3.new(1.8, 3.5, 9),
		Vector3.new(-62.1, 1.75, 6),
		{ Color = Color3.fromRGB(110, 70, 50) }
	)
	part(
		model,
		"DeskTop",
		Vector3.new(2.3, 0.3, 9.4),
		Vector3.new(-62.05, 3.65, 6),
		{ Color = loc.trim }
	)
	part(
		model,
		"Till",
		Vector3.new(1.2, 1.1, 1.2),
		Vector3.new(-62, 4.35, 8.5),
		{ Color = Color3.fromRGB(230, 200, 90) }
	)
	-- The key rack against the −X end, behind the clerk.
	part(
		model,
		"KeyRack",
		Vector3.new(0.8, 9.6, 5.2),
		Vector3.new(-71.6, 4.8, 6),
		{ Color = Color3.fromRGB(80, 55, 40) }
	)
	-- Benches in the front row on the stair side, their backs to the wall.
	for i, span in { { 25.6, 32.4 }, { 40, 47 }, { 50, 57 } } do
		part(
			model,
			`Bench_{i}`,
			Vector3.new(span[2] - span[1], 1.8, 1.9),
			Vector3.new((span[1] + span[2]) / 2, 0.9, 1.95),
			{ Color = Color3.fromRGB(90, 60, 45) }
		)
	end
	lamp(model, 1, Vector3.new(0, 8.5, 1.5), Color3.fromRGB(255, 190, 120))
	lamp(model, 2, Vector3.new(-62.3, 6, 2.3), Color3.fromRGB(255, 190, 120))

	attach(root, "Entrance", Vector3.new(0, 0, 0), Vector3.new(0, 0, -1))
	attach(root, "Desk", Vector3.new(-60.8, 3.8, 5), Vector3.new(1, 0, 0))
	attach(root, "Clerk", Vector3.new(-66, 0, 6), Vector3.new(1, 0, 0))
	for i, x in { -58, -54.5, -51, -47.5 } do
		attach(root, `Queue_{i}`, Vector3.new(x, 0, 5), Vector3.new(-1, 0, 0))
	end
	attach(root, "Till", Vector3.new(-60.8, 3.8, 9.4), Vector3.new(1, 0, 0))
	attach(root, "Spawn", Vector3.new(8, 0, 18), Vector3.new(0, 0, -1))
	return model
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
	local S = G.StairCore.w * CELL -- 24
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
	-- Along an edge the stair core touches, the rail stops at the core: its
	-- own walls rise to the same height there, and a rail in the same plane
	-- flickered against them (his report, 2026-10-19).
	local function rail(name: string, alongX: boolean, fixed: number, gap: { number }?)
		local runs = if gap then { { 0, gap[1] }, { gap[2], P } } else { { 0, P } }
		for _, r in runs do
			local a0, a1 = r[1], r[2]
			if a1 - a0 > 0.05 then
				local mid = (a0 + a1) / 2
				part(
					folder,
					name,
					if alongX then Vector3.new(a1 - a0, rh, rt) else Vector3.new(rt, rh, a1 - a0),
					if alongX
						then Vector3.new(mid, top + rh / 2, fixed)
						else Vector3.new(fixed, top + rh / 2, mid),
					{ Color = loc.trim }
				)
			end
		end
	end
	local coreX = { sc.x * CELL, (sc.x + sc.w) * CELL }
	local coreZ = { sc.z * CELL, (sc.z + sc.d) * CELL }
	rail("Rail_Front", true, rt / 2, if sc.z == 0 then coreX else nil)
	rail("Rail_Back", true, P - rt / 2, if sc.z + sc.d == G.Cells then coreX else nil)
	rail("Rail_Left", false, rt / 2, if sc.x == 0 then coreZ else nil)
	rail("Rail_Right", false, P - rt / 2, if sc.x + sc.w == G.Cells then coreZ else nil)
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

--[[ The facade (MODELS.md, "Facade and sign"; GDD §5.1): walls on the left,
	right and back edges of every floor, just outside the grid so they never
	take a cell or block a door, with window openings, and on floor 1 a
	doorway at the back to the Resident Wing, and solid along the lobby. The
	street side is the lobby's own front wall on floor 1 and stays open above. Plot-local, as a Folder (a blockout until the kit has
	`Facade_Wall` pieces). A facade cosmetic (MODELS.md, "Cosmetics") gives
	its own colours as `scheme`. ]]
function HotelKit.facade(
	location: number,
	floors: number,
	scheme: { facade: Color3, trim: Color3 }?
): Folder
	local loc = Locations.get(location)
	local folder = Instance.new("Folder")
	folder.Name = "Facade"
	local P = G.Cells * CELL
	local t = 0.6
	local wall = darker(if scheme then scheme.facade else loc.facade, 0.85)
	local trim = if scheme then scheme.trim else loc.trim
	-- One side: a run of `length` studs along `axis`, outside the grid at `offset`.
	local function side(
		name: string,
		floor: number,
		axis: "X" | "Z",
		fixed: number,
		gapFrom: number?,
		gapTo: number?
	)
		local y0 = (floor - 1) * FLOOR + G.SlabThickness
		local function at(
			along: number,
			height: number,
			centreY: number,
			length: number,
			thick: number
		): (Vector3, Vector3)
			if axis == "X" then
				return Vector3.new(length, height, thick), Vector3.new(along, centreY, fixed)
			end
			return Vector3.new(thick, height, length), Vector3.new(fixed, centreY, along)
		end
		local function piece(
			partName: string,
			a0: number,
			a1: number,
			h0: number,
			h1: number,
			colour: Color3,
			thick: number?
		)
			if a1 - a0 < 0.05 then
				return
			end
			local size, centre = at((a0 + a1) / 2, h1 - h0, y0 + (h0 + h1) / 2, a1 - a0, thick or t)
			part(folder, partName, size, centre, { Color = colour })
		end
		local top = FLOOR - G.SlabThickness
		local function band(
			partName: string,
			h0: number,
			h1: number,
			colour: Color3,
			thick: number?
		)
			if gapFrom and gapTo then
				piece(partName, 0, gapFrom, h0, h1, colour, thick)
				piece(partName, gapTo, P, h0, h1, colour, thick)
			else
				piece(partName, 0, P, h0, h1, colour, thick)
			end
		end
		-- Windows 4 wide and 9 tall (y 3..12) over a person's sill, two to a cell.
		local winLow, winHigh = 3, 12
		band(`{name}_Low`, 0, winLow, wall)
		piece(`{name}_High`, 0, P, winHigh, top, wall)
		-- Floor 1's sides are solid along the lobby: its end walls, the key rack's back.
		local solid = if axis == "Z" and floor == 1 then G.LobbyRows * CELL else 0
		if solid > 0 then
			piece(`{name}_Lobby`, 0, solid, winLow, winHigh, wall)
		end
		-- Posts between the window openings, every half cell, 2 wide.
		for c = 0, 2 * G.Cells do
			local x = c * CELL / 2
			local a0, a1 = math.max(solid, x - 1), math.min(P, x + 1)
			if a1 > a0 and not (gapFrom and gapTo and a1 > gapFrom and a0 < gapTo) then
				piece(`{name}_Post`, a0, a1, winLow, winHigh, wall)
			end
		end
		-- A doorway is a door's height (9), not the window band's: a lintel over the gap.
		if gapFrom and gapTo then
			piece(`{name}_Lintel`, gapFrom, gapTo, 9, winHigh, wall)
		end
		-- The sill stands 0.06 proud of both faces: flush with the wall it
		-- flickered against it (his report, 2026-10-19, the lobby's end wall),
		-- and it stops at a doorway instead of barring it.
		band(`{name}_Sill`, winLow - 0.2, winLow + 0.2, trim, t + 0.12)
	end
	for floor = 1, floors do
		side(`Left_{floor}`, floor, "Z", -t / 2)
		side(`Right_{floor}`, floor, "Z", P + t / 2)
		if floor == 1 then
			side(`Back_{floor}`, floor, "X", P + t / 2, P / 2 - 4, P / 2 + 4)
		else
			side(`Back_{floor}`, floor, "X", P + t / 2)
		end
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

--[[ The ground: the plot's base, its lobby floor, the Resident Wing's garden
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
