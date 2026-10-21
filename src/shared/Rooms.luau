--!strict
--[[
	Built rooms (GDD §5.4, his rulings of 2026-10-21; Appendix A.12, the
	contract): walls and doors on half-cell edges, the areas they enclose,
	rooms made of those areas, what a room needs to be ready, its three bars
	and their bonuses, and how a guest walks the 3-stud squares between the
	walls. Pure: no services, no instances. The server validates every wall
	and door with it, the build mode asks it the same question, and the
	specs hold it to its rules.

	HALF CELLS. A cell is `HalfCells` × `HalfCells` half cells (6 studs), so
	a floor is `Cells × HalfCells` of them on a side; half cell (hx, hz) lies
	in cell (hx // HalfCells, hz // HalfCells). A half edge is `edgeKey(floor,
	hx, hz, o)`: o 0 runs along x at hz, between (hx, hz − 1) and (hx, hz);
	o 1 runs along z at hx, between (hx − 1, hz) and (hx, hz). A wall stands
	only inside the hotel: both half cells owned on that floor, neither in the
	entrance's mouth, under a stair or its well, or under another piece (the
	desk), and no decor standing across it. The facade is the outer wall;
	inner walls never stand on it. A door is a wall record with `door`.

	AREAS. Each floor's owned half cells fall into areas: a flood fill across
	every half edge with no wall, a door counting as a wall (so a room is not
	part of the corridor outside its door). An area holding the mouth, a
	stair's cells, its well or a desk is hallway; any other area with a door
	in its boundary may be made a room.

	ROOMS are `{ type, floor, hx, hz }`, the half cell its seed: a room is the
	area holding its seed. A change is refused when it would put two rooms'
	seeds in one area (`MergesRooms`), make a room's area hallway
	(`RoomTaken`), or cut a desk's queue or a stair's foot or head off from
	the entrance (`CutsOff`, the same promise `Grid` keeps for pieces).
	Removing a room's last door is allowed: the room is kept, not ready.

	SQUARES. Guests walk the decor grid (`Constants.Grid.Squares` to a cell,
	3 studs): a square is walkable on an owned cell not under a piece or a
	well and not under decor or furniture (rugs excepted); a step between two
	half cells is blocked by a wall without a door on that half edge; stairs
	join their foot to their head as in `Grid.route`.
]]

local Constants = require(script.Parent.Constants)
local Furnish = require(script.Parent.Furnish)
local Grid = require(script.Parent.Grid)
local Pieces = require(script.Parent.Pieces)
local Species = require(script.Parent.Species)
local Unlocks = require(script.Parent.Unlocks)

local G = Constants.Grid
local R = Constants.Rooms
local N = G.Cells
local HC = R.HalfCells
local H = N * HC -- half cells on a floor's side
local Q = G.Squares
local NQ = N * Q -- squares on a floor's side
local SQ = Q // HC -- squares on a half cell's side
local W1 = H + 1 -- half-edge positions on a side

export type Edge = string
export type WallRecord = { door: boolean?, paid: number }
export type RoomRecord = { type: string, floor: number, hx: number, hz: number }
export type World = Grid.World & { walls: { [Edge]: WallRecord }, rooms: { [string]: RoomRecord } }
export type Area = {
	floor: number,
	cells: { number }, -- half cells, by `Rooms.halfKey`
	doors: { Edge }, -- doors between this area and another
	hallway: boolean,
	size: number, -- in cells: half cells / HalfCells²
	room: string?, -- the room whose seed is here (the first by id if, wrongly, several)
	rooms: { string }, -- every room whose seed is here, sorted
}
export type Refusal =
	"Unknown"
	| "NoFloor"
	| "NotInside"
	| "Mouth"
	| "Stair"
	| "Piece"
	| "Decor"
	| "Exists"
	| "NoWall"
	| "MergesRooms"
	| "RoomTaken"
	| "CutsOff"
	| "UnknownType"
	| "Hallway"
	| "NoDoor"
	| "Taken"
export type Requirement = {
	minCells: number,
	fullCells: number,
	keys: { string }, -- decor ids of its key furniture: any one makes it ready
	furnitureTarget: number,
	decorTarget: (cells: number) -> number,
}
export type TypeInfo = {
	id: string,
	name: string,
	kind: string, -- "Room" | "Amenity"
	locked: string?, -- why it cannot be chosen yet (Unlocks), nil when it can
	minCells: number,
	fullCells: number,
	keys: { string },
	species: { string }, -- who stays in it (a room type)
	tags: { string }, -- the preference tags it gives (an amenity)
}
export type Contents = { furniture: { Grid.DecorPlaced }, decor: { Grid.DecorPlaced } }
export type Bars = { size: number, furniture: number, decor: number }
export type Bonuses = { pay: number, stay: number, satisfaction: number, friendship: number }
export type Spot = Grid.Spot -- in squares for `walkable`, `route`, `keySpot`
export type Leg = Grid.Leg -- as Grid's, but `cells` are squares

local Rooms = {}

Rooms.HalfCells = HC
Rooms.Size = H

-- ===== Keys =====

function Rooms.halfKey(hx: number, hz: number): number
	return hz * H + hx
end

function Rooms.halfOf(k: number): (number, number)
	return k % H, k // H
end

function Rooms.edgeKey(floor: number, hx: number, hz: number, o: number): Edge
	return `{floor}:{hx}:{hz}:{o}`
end

function Rooms.edgeOf(e: Edge): (number, number, number, number)
	local parts = string.split(e, ":")
	return tonumber(parts[1]) or -1,
		tonumber(parts[2]) or -1,
		tonumber(parts[3]) or -1,
		tonumber(parts[4]) or -1
end

-- A half edge as one number (for indexing walls in a search).
local function ekey(floor: number, hx: number, hz: number, o: number): number
	return ((floor * W1 + hz) * W1 + hx) * 2 + o
end

-- The half cells either side of a half edge: (ax, az) before it, (bx, bz) after.
local function sides(hx: number, hz: number, o: number): (number, number, number, number)
	if o == 0 then
		return hx, hz - 1, hx, hz
	end
	return hx - 1, hz, hx, hz
end
Rooms.sides = sides

--[[ The two half edges of a whole cell edge, `side` as Grid's: 0 its front
	(−z), 1 its −x side, 2 its back (+z), 3 its +x side. ]]
function Rooms.cellEdges(floor: number, x: number, z: number, side: number): { Edge }
	local hx, hz = x * HC, z * HC
	local out = {}
	for i = 0, HC - 1 do
		if side == 0 then
			table.insert(out, Rooms.edgeKey(floor, hx + i, hz, 0))
		elseif side == 2 then
			table.insert(out, Rooms.edgeKey(floor, hx + i, hz + HC, 0))
		elseif side == 1 then
			table.insert(out, Rooms.edgeKey(floor, hx, hz + i, 1))
		else
			table.insert(out, Rooms.edgeKey(floor, hx + HC, hz + i, 1))
		end
	end
	return out
end

-- ===== What stands where =====

type WallIndex = {
	any: { [number]: boolean }, -- every wall, door or not (areas)
	shut: { [number]: boolean }, -- walls without a door (walking)
	door: { [number]: boolean },
}

local function indexWalls(walls: { [Edge]: WallRecord }): WallIndex
	local idx: WallIndex = { any = {}, shut = {}, door = {} }
	for e, rec in walls do
		local floor, hx, hz, o = Rooms.edgeOf(e)
		local k = ekey(floor, hx, hz, o)
		idx.any[k] = true
		if rec.door then
			idx.door[k] = true
		else
			idx.shut[k] = true
		end
	end
	return idx
end

local function cellKey(floor: number, x: number, z: number): number
	return (floor * N + z) * N + x
end

local function isMouth(floor: number, x: number, z: number): boolean
	if floor ~= 1 then
		return false
	end
	for _, c in Grid.entrance() do
		if c.x == x and c.z == z then
			return true
		end
	end
	return false
end

type Marks = {
	stair: { [number]: boolean }, -- a stair's cells and its well, by cellKey
	desk: { [number]: boolean },
	other: { [number]: boolean }, -- any other piece
}

local function marks(world: World): Marks
	local m: Marks = { stair = {}, desk = {}, other = {} }
	for _, p in world.pieces do
		for _, c in Grid.cells(p) do
			if p.kind == "Stairs" then
				m.stair[cellKey(p.floor, c.x, c.z)] = true
				m.stair[cellKey(p.floor + 1, c.x, c.z)] = true
			elseif p.kind == "Desk" then
				m.desk[cellKey(p.floor, c.x, c.z)] = true
			else
				m.other[cellKey(p.floor, c.x, c.z)] = true
			end
		end
	end
	return m
end

local function ownedHalf(world: World, floor: number, hx: number, hz: number): boolean
	return hx >= 0
		and hz >= 0
		and hx < H
		and hz < H
		and Grid.isOpen(world, floor, hx // HC, hz // HC)
end

-- ===== Areas =====

local STEPS = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } }

-- The half edge between a half cell and its neighbour one step away.
local function between(floor: number, hx: number, hz: number, dx: number, dz: number): number
	if dx ~= 0 then
		return ekey(floor, math.max(hx, hx + dx), hz, 1)
	end
	return ekey(floor, hx, math.max(hz, hz + dz), 0)
end

local function betweenEdge(floor: number, hx: number, hz: number, dx: number, dz: number): Edge
	if dx ~= 0 then
		return Rooms.edgeKey(floor, math.max(hx, hx + dx), hz, 1)
	end
	return Rooms.edgeKey(floor, hx, math.max(hz, hz + dz), 0)
end

-- A floor's areas, and which area each half cell is in (halfKey -> index).
local function computeAreas(
	world: World,
	floor: number,
	idx: WallIndex,
	m: Marks
): ({ Area }, { [number]: number })
	local seeds: { [number]: { string } } = {}
	local ids = {}
	for id in world.rooms do
		table.insert(ids, id)
	end
	table.sort(ids)
	for _, id in ids do
		local r = world.rooms[id]
		if r.floor == floor then
			local k = Rooms.halfKey(r.hx, r.hz)
			seeds[k] = seeds[k] or {}
			table.insert(seeds[k], id)
		end
	end
	local areas: { Area } = {}
	local of: { [number]: number } = {}
	for hz = 0, H - 1 do
		for hx = 0, H - 1 do
			local start = Rooms.halfKey(hx, hz)
			if of[start] == nil and ownedHalf(world, floor, hx, hz) then
				local n = #areas + 1
				local cells = { start }
				of[start] = n
				local head = 1
				while head <= #cells do
					local cx, cz = Rooms.halfOf(cells[head])
					head += 1
					for _, s in STEPS do
						local nx, nz = cx + s[1], cz + s[2]
						local nk = Rooms.halfKey(nx, nz)
						if
							ownedHalf(world, floor, nx, nz)
							and of[nk] == nil
							and not idx.any[between(floor, cx, cz, s[1], s[2])]
						then
							of[nk] = n
							table.insert(cells, nk)
						end
					end
				end
				local hallway = false
				local rooms: { string } = {}
				for _, k in cells do
					local cx, cz = Rooms.halfOf(k)
					local x, z = cx // HC, cz // HC
					local ck = cellKey(floor, x, z)
					if isMouth(floor, x, z) or m.stair[ck] or m.desk[ck] then
						hallway = true
					end
					local here = seeds[k]
					if here then
						for _, id in here do
							table.insert(rooms, id)
						end
					end
				end
				table.sort(rooms)
				table.insert(areas, {
					floor = floor,
					cells = cells,
					doors = {},
					hallway = hallway,
					size = #cells / (HC * HC),
					room = rooms[1],
					rooms = rooms,
				})
			end
		end
	end
	-- Doors: a door between an area and another (never one standing inside an area).
	for n, a in areas do
		local seen = {}
		for _, k in a.cells do
			local cx, cz = Rooms.halfOf(k)
			for _, s in STEPS do
				local nx, nz = cx + s[1], cz + s[2]
				local e = between(floor, cx, cz, s[1], s[2])
				if idx.door[e] and not seen[e] and of[Rooms.halfKey(nx, nz)] ~= n then
					seen[e] = true
					table.insert(a.doors, betweenEdge(floor, cx, cz, s[1], s[2]))
				end
			end
		end
		table.sort(a.doors)
	end
	return areas, of
end

-- Every area of a floor, in the order their first half cell is met (hz, then hx).
function Rooms.areas(world: World, floor: number): { Area }
	local areas = computeAreas(world, floor, indexWalls(world.walls), marks(world))
	return areas
end

function Rooms.areaAt(world: World, floor: number, hx: number, hz: number): Area?
	if not ownedHalf(world, floor, hx, hz) then
		return nil
	end
	local areas, of = computeAreas(world, floor, indexWalls(world.walls), marks(world))
	local n = of[Rooms.halfKey(hx, hz)]
	return if n then areas[n] else nil
end

function Rooms.roomArea(world: World, roomId: string): Area?
	local r = world.rooms[roomId]
	if not r then
		return nil
	end
	return Rooms.areaAt(world, r.floor, r.hx, r.hz)
end

-- ===== Walking on squares =====

local function sqKey(floor: number, sx: number, sz: number): number
	return (floor * NQ + sz) * NQ + sx
end

local function sqOf(k: number): Spot
	return { floor = k // (NQ * NQ), z = (k // NQ) % NQ, x = k % NQ }
end

type Walk = {
	world: World,
	idx: WallIndex,
	piece: { [number]: boolean }, -- cells under a piece or a well, by cellKey
	blocked: { [number]: boolean }, -- squares under decor or furniture, by sqKey
}

local function walkOf(world: World): Walk
	local m = marks(world)
	local piece = {}
	for _, t in { m.stair, m.desk, m.other } do
		for k in t do
			piece[k] = true
		end
	end
	local blocked = {}
	for _, d in world.decor do
		if d.layer ~= "Rug" then
			for _, s in Grid.squares(d) do
				blocked[sqKey(d.floor, s.x, s.z)] = true
			end
		end
	end
	return { world = world, idx = indexWalls(world.walls), piece = piece, blocked = blocked }
end

local function canStand(w: Walk, floor: number, sx: number, sz: number): boolean
	if floor < 1 or floor > w.world.floors or sx < 0 or sz < 0 or sx >= NQ or sz >= NQ then
		return false
	end
	local x, z = sx // Q, sz // Q
	return Grid.isOpen(w.world, floor, x, z)
		and not w.piece[cellKey(floor, x, z)]
		and not w.blocked[sqKey(floor, sx, sz)]
end

-- Whether a step of one square crosses a wall without a door.
local function shutBetween(
	w: Walk,
	floor: number,
	sx: number,
	sz: number,
	dx: number,
	dz: number
): boolean
	local ax, az = sx // SQ, sz // SQ
	local bx, bz = (sx + dx) // SQ, (sz + dz) // SQ
	if ax == bx and az == bz then
		return false
	end
	return w.idx.shut[between(floor, ax, az, bx - ax, bz - az)] == true
end

-- A cell's squares, nearest its middle first: where a stair is stepped on and off.
local ORDER: { { number } } = {}
do
	local mid = (Q - 1) / 2
	for z = 0, Q - 1 do
		for x = 0, Q - 1 do
			table.insert(ORDER, { x, z, (x - mid) ^ 2 + (z - mid) ^ 2 })
		end
	end
	table.sort(ORDER, function(a, b)
		if a[3] ~= b[3] then
			return a[3] < b[3]
		end
		if a[2] ~= b[2] then
			return a[2] < b[2]
		end
		return a[1] < b[1]
	end)
end

local function anchor(w: Walk, s: Grid.Spot): number?
	for _, o in ORDER do
		local sx, sz = s.x * Q + o[1], s.z * Q + o[2]
		if canStand(w, s.floor, sx, sz) then
			return sqKey(s.floor, sx, sz)
		end
	end
	return nil
end

type Hop = { to: number, stair: Grid.Placed, up: boolean }

local function flood(w: Walk, from: { number }): ({ [number]: number }, { [number]: Hop })
	local hops: { [number]: { Hop } } = {}
	for _, p in w.world.pieces do
		if p.kind == "Stairs" then
			local a, b = anchor(w, Grid.stairFoot(p)), anchor(w, Grid.stairHead(p))
			if a and b then
				hops[a] = hops[a] or {}
				table.insert(hops[a], { to = b, stair = p, up = true })
				hops[b] = hops[b] or {}
				table.insert(hops[b], { to = a, stair = p, up = false })
			end
		end
	end
	local parent: { [number]: number } = {}
	local via: { [number]: Hop } = {}
	local queue: { number } = {}
	for _, k in from do
		local s = sqOf(k)
		if parent[k] == nil and canStand(w, s.floor, s.x, s.z) then
			parent[k] = -1
			table.insert(queue, k)
		end
	end
	local head = 1
	while head <= #queue do
		local k = queue[head]
		head += 1
		local s = sqOf(k)
		for _, step in STEPS do
			local nx, nz = s.x + step[1], s.z + step[2]
			if
				canStand(w, s.floor, nx, nz)
				and not shutBetween(w, s.floor, s.x, s.z, step[1], step[2])
			then
				local nk = sqKey(s.floor, nx, nz)
				if parent[nk] == nil then
					parent[nk] = k
					table.insert(queue, nk)
				end
			end
		end
		local out = hops[k]
		if out then
			for _, hop in out do
				if parent[hop.to] == nil then
					parent[hop.to] = k
					via[hop.to] = hop
					table.insert(queue, hop.to)
				end
			end
		end
	end
	return parent, via
end

-- The squares guests come in on: the mouth's.
local function entranceSquares(): { number }
	local out = {}
	for _, c in Grid.entrance() do
		for dz = 0, Q - 1 do
			for dx = 0, Q - 1 do
				table.insert(out, sqKey(1, c.x * Q + dx, c.z * Q + dz))
			end
		end
	end
	return out
end

local function fromEntrance(w: Walk): { [number]: number }
	local parent = flood(w, entranceSquares())
	return parent
end

-- Whether a guest can stand on square (sx, sz) of `floor` now.
function Rooms.walkable(world: World, floor: number, sx: number, sz: number): boolean
	return canStand(walkOf(world), floor, sx, sz)
end

-- Keeps a run of squares' ends and every turn.
local function turns(cells: { Grid.Cell }): { Grid.Cell }
	local out: { Grid.Cell } = { cells[1] }
	for i = 2, #cells - 1 do
		local a, b, c = cells[i - 1], cells[i], cells[i + 1]
		if (b.x - a.x) ~= (c.x - b.x) or (b.z - a.z) ~= (c.z - b.z) then
			table.insert(out, b)
		end
	end
	if #cells > 1 then
		table.insert(out, cells[#cells])
	end
	return out
end

--[[ The way a guest walks from square `from` to square `to` (A.12
	"Guests"): legs as `Grid.route`'s, each a floor's run of squares (its
	turns, both ends included) or a stair to climb (`up`) or descend; nil
	when there is no way. ]]
function Rooms.route(world: World, from: Spot, to: Spot): { Leg }?
	local w = walkOf(world)
	local parent, via = flood(w, { sqKey(from.floor, from.x, from.z) })
	local k = sqKey(to.floor, to.x, to.z)
	if parent[k] == nil then
		return nil
	end
	local chain: { number } = {}
	while k ~= -1 do
		table.insert(chain, 1, k)
		k = parent[k]
	end
	local legs: { Leg } = {}
	local run: { Grid.Cell } = {}
	local runFloor = from.floor
	for i, ck in chain do
		local hop = via[ck]
		if hop and i > 1 then
			table.insert(legs, { floor = runFloor, cells = turns(run) })
			table.insert(legs, { stair = hop.stair, up = hop.up })
			run = {}
		end
		local s = sqOf(ck)
		runFloor = s.floor
		table.insert(run, { x = s.x, z = s.z })
	end
	table.insert(legs, { floor = runFloor, cells = turns(run) })
	return legs
end

-- The labels of the places guests must reach (desk queues, stair feet and heads) that are reached now.
local function reachedTargets(world: World): { [string]: boolean }
	local w = walkOf(world)
	local reach = fromEntrance(w)
	local out = {}
	for _, p in world.pieces do
		local spots: { Grid.Spot } = {}
		if p.kind == "Desk" or p.kind == "Stairs" then
			spots = Grid.doors(p)
		end
		for _, s in spots do
			local a = anchor(w, s)
			if a and reach[a] ~= nil then
				out[`{s.floor}:{s.x}:{s.z}`] = true
			end
		end
	end
	return out
end

-- ===== Changes =====

-- Each room in trouble: "MergesRooms" when it shares its area, "RoomTaken" when its area is hallway.
local function trouble(world: World): { [string]: Refusal }
	local out: { [string]: Refusal } = {}
	local idx, m = indexWalls(world.walls), marks(world)
	for floor = 1, world.floors do
		for _, a in computeAreas(world, floor, idx, m) do
			for _, id in a.rooms do
				if #a.rooms > 1 then
					out[id] = "MergesRooms"
				elseif a.hallway then
					out[id] = "RoomTaken"
				end
			end
		end
	end
	return out
end

--[[ Whether the change from `before` to `after` keeps the rooms' rules: no
	two rooms in one area, no room's area hallway, nothing guests reached cut
	off. Only what the change breaks is refused. The server may call it for
	any change (a stair or desk placed, decor moved), not only walls. ]]
function Rooms.check(before: World, after: World): (boolean, Refusal?)
	local was, now = trouble(before), trouble(after)
	local ids = {}
	for id in now do
		table.insert(ids, id)
	end
	table.sort(ids)
	for _, id in ids do
		if was[id] == nil then
			return false, now[id]
		end
	end
	local reachedBefore = reachedTargets(before)
	local reachedAfter = reachedTargets(after)
	for label in reachedBefore do
		if not reachedAfter[label] then
			return false, "CutsOff"
		end
	end
	return true, nil
end

local function withWalls(world: World, walls: { [Edge]: WallRecord }): World
	local after = table.clone(world)
	after.walls = walls
	return after
end

-- The half edge parsed and checked for shape: (floor, hx, hz, o, canonical key) or a refusal.
local function parse(
	world: World,
	edge: Edge
): (boolean, Refusal?, number, number, number, number, Edge)
	local floor, hx, hz, o = Rooms.edgeOf(edge)
	if floor % 1 ~= 0 or hx % 1 ~= 0 or hz % 1 ~= 0 or (o ~= 0 and o ~= 1) then
		return false, "Unknown", floor, hx, hz, o, edge
	end
	if floor < 1 or floor > world.floors then
		return false, "NoFloor", floor, hx, hz, o, edge
	end
	return true, nil, floor, hx, hz, o, Rooms.edgeKey(floor, hx, hz, o)
end

--[[ Whether a wall (with a door in it when `door`) may stand on half edge
	`edge` (A.12): inside the hotel, off the mouth, stairs, wells and pieces,
	not through decor, not there already, and not a change that merges two
	rooms, takes one for hallway or cuts a guest's way off. ]]
function Rooms.canWall(world: World, edge: Edge, door: boolean?): (boolean, Refusal?)
	local ok, why, floor, hx, hz, o, e = parse(world, edge)
	if not ok then
		return false, why
	end
	local ax, az, bx, bz = sides(hx, hz, o)
	if not ownedHalf(world, floor, ax, az) or not ownedHalf(world, floor, bx, bz) then
		return false, "NotInside"
	end
	local m = marks(world)
	for _, h in { { ax, az }, { bx, bz } } do
		local x, z = h[1] // HC, h[2] // HC
		local ck = cellKey(floor, x, z)
		if isMouth(floor, x, z) then
			return false, "Mouth"
		end
		if m.stair[ck] then
			return false, "Stair"
		end
		if m.desk[ck] or m.other[ck] then
			return false, "Piece"
		end
	end
	if world.walls[e] then
		return false, "Exists"
	end
	-- Decor or furniture standing across the half edge: two of its squares
	-- meeting over it (rugs lie under walls).
	local dx, dz = if o == 1 then 1 else 0, if o == 0 then 1 else 0
	for _, d in world.decor do
		if d.layer ~= "Rug" and d.floor == floor then
			local mine = {}
			for _, s in Grid.squares(d) do
				mine[sqKey(floor, s.x, s.z)] = true
			end
			for _, s in Grid.squares(d) do
				local nx, nz = s.x + dx, s.z + dz
				if
					s.x // SQ == ax
					and s.z // SQ == az
					and nx // SQ == bx
					and nz // SQ == bz
					and mine[sqKey(floor, nx, nz)]
				then
					return false, "Decor"
				end
			end
		end
	end
	local walls = table.clone(world.walls)
	walls[e] = { door = if door then true else nil, paid = 0 }
	return Rooms.check(world, withWalls(world, walls))
end

-- Whether the wall on `edge` may be taken away: there is one, and it merges no rooms nor takes one for hallway.
function Rooms.canRemoveWall(world: World, edge: Edge): (boolean, Refusal?)
	local ok, why, _, _, _, _, e = parse(world, edge)
	if not ok then
		return false, why
	end
	if not world.walls[e] then
		return false, "NoWall"
	end
	local walls = table.clone(world.walls)
	walls[e] = nil
	return Rooms.check(world, withWalls(world, walls))
end

-- Whether the wall on `edge` may have its door put in (`door`) or walled up.
function Rooms.canDoor(world: World, edge: Edge, door: boolean): (boolean, Refusal?)
	local ok, why, _, _, _, _, e = parse(world, edge)
	if not ok then
		return false, why
	end
	local rec = world.walls[e]
	if not rec then
		return false, "NoWall"
	end
	if (rec.door == true) == door then
		return false, "Exists"
	end
	local walls = table.clone(world.walls)
	local changed = table.clone(rec)
	changed.door = if door then true else nil
	walls[e] = changed
	return Rooms.check(world, withWalls(world, walls))
end

-- ===== Types =====

local function isType(id: string): boolean
	local p = Pieces.get(id)
	return p ~= nil and (p.kind == "Room" or p.kind == "Amenity")
end

-- What a room type or amenity needs (A.12), or nil for an unknown type.
function Rooms.requirement(typeId: string): Requirement?
	local p = Pieces.get(typeId)
	if not p or not isType(typeId) then
		return nil
	end
	local keys = {}
	for _, d in Pieces.DecorList do
		if d.furniture and d.keyFor and table.find(d.keyFor, typeId) then
			table.insert(keys, d.id)
		end
	end
	local minCells = p.w * p.d
	return {
		minCells = minCells,
		fullCells = minCells * R.FullSizeFactor,
		keys = keys,
		furnitureTarget = math.max(p.cost * R.FurnitureTargetFactor, R.FurnitureTargetMin),
		decorTarget = function(cells: number): number
			return R.DecorTargetPer4Cells * cells / 4
		end,
	}
end

--[[ The types a player at `c.location` can choose for a room, locked ones
	with the reason (Unlocks, as the build panel shows today), each with its
	tooltip: who stays in it, its key furniture and its sizes. ]]
function Rooms.typesFor(c: Unlocks.Context): { TypeInfo }
	local out: { TypeInfo } = {}
	for _, p in Pieces.List do
		if isType(p.id) and p.location == c.location then
			local ok, why = Unlocks.buildable(p.id, c)
			local req = Rooms.requirement(p.id) :: Requirement
			local species = {}
			if p.kind == "Room" then
				for _, sp in Species.List do
					if sp.room == p.id then
						table.insert(species, sp.id)
					end
				end
			end
			table.insert(out, {
				id = p.id,
				name = p.name,
				kind = p.kind,
				locked = if ok then nil else (why or "Locked"),
				minCells = req.minCells,
				fullCells = req.fullCells,
				keys = req.keys,
				species = species,
				tags = if p.kind == "Amenity" then table.clone(p.tags or {}) else {},
			})
		end
	end
	return out
end

-- `typesFor` with the context spelled out.
function Rooms.types(
	location: number,
	unlocked: { [string]: boolean },
	rating: number,
	rooms: number?,
	floors: number?,
	legendaryResident: boolean?,
	tutorial: { [string]: boolean }?
): { TypeInfo }
	return Rooms.typesFor({
		location = location,
		unlocked = unlocked,
		rating = rating,
		rooms = rooms or 0,
		floors = floors or 1,
		legendaryResident = legendaryResident == true,
		tutorial = tutorial,
	})
end

-- Rooms of a room type (not amenities), for Unlocks' `rooms`.
function Rooms.roomCount(world: World): number
	local n = 0
	for _, r in world.rooms do
		local p = Pieces.get(r.type)
		if p and p.kind == "Room" then
			n += 1
		end
	end
	return n
end

--[[ Whether the area holding half cell (hx, hz) may be made a room of
	`typeId`: a type, not hallway, with a door, holding no other room
	(`skip`, a room being retyped, aside). ]]
function Rooms.canMakeRoom(
	world: World,
	floor: number,
	hx: number,
	hz: number,
	typeId: string,
	skip: string?
): (boolean, Refusal?)
	if not isType(typeId) then
		return false, "UnknownType"
	end
	local a = Rooms.areaAt(world, floor, hx, hz)
	if not a then
		return false, "NotInside"
	end
	if a.hallway then
		return false, "Hallway"
	end
	if #a.doors == 0 then
		return false, "NoDoor"
	end
	for _, id in a.rooms do
		if id ~= skip then
			return false, "Taken"
		end
	end
	return true, nil
end

-- ===== What is in a room =====

local function inArea(a: Area): { [number]: boolean }
	local set = {}
	for _, k in a.cells do
		set[k] = true
	end
	return set
end

--[[ The furniture and the decor standing in a room: a record is in it when
	every square it covers lies in the room's half cells. ]]
function Rooms.contents(world: World, roomId: string): Contents
	local out: Contents = { furniture = {}, decor = {} }
	local a = Rooms.roomArea(world, roomId)
	if not a then
		return out
	end
	local set = inArea(a)
	for _, d in world.decor do
		if d.floor == a.floor then
			local inside = true
			for _, s in Grid.squares(d) do
				if
					s.x < 0
					or s.z < 0
					or s.x >= NQ
					or s.z >= NQ
					or not set[Rooms.halfKey(s.x // SQ, s.z // SQ)]
				then
					inside = false
					break
				end
			end
			if inside then
				local row = Pieces.decor(d.item)
				table.insert(if row and row.furniture then out.furniture else out.decor, d)
			end
		end
	end
	return out
end

local function keyPieces(world: World, roomId: string): { Grid.DecorPlaced }
	local r = world.rooms[roomId]
	local req = if r then Rooms.requirement(r.type) else nil
	local out = {}
	if not req then
		return out
	end
	for _, d in Rooms.contents(world, roomId).furniture do
		if table.find(req.keys, d.item) then
			table.insert(out, d)
		end
	end
	return out
end

--[[ A square in the room beside one of its key furniture, where a booked
	guest walks to (A.12 "Guests"), or nil. ]]
function Rooms.keySpot(world: World, roomId: string): Spot?
	local a = Rooms.roomArea(world, roomId)
	if not a then
		return nil
	end
	local set = inArea(a)
	local w = walkOf(world)
	for _, d in keyPieces(world, roomId) do
		for _, s in Grid.squares(d) do
			for _, step in STEPS do
				local nx, nz = s.x + step[1], s.z + step[2]
				if
					set[Rooms.halfKey(nx // SQ, nz // SQ)]
					and canStand(w, a.floor, nx, nz)
					and not shutBetween(w, a.floor, s.x, s.z, step[1], step[2])
				then
					return { floor = a.floor, x = nx, z = nz }
				end
			end
		end
	end
	return nil
end

--[[ Whether a room is ready for guests (A.12): its key furniture in it, at
	least its minimum size, a door, and reached from the entrance; if not,
	what it lacks ("Type", "Area", "Hallway", "KeyFurniture", "MinSize",
	"Door", "Unreached"). ]]
function Rooms.ready(world: World, roomId: string): (boolean, { string }?)
	local r = world.rooms[roomId]
	local req = if r then Rooms.requirement(r.type) else nil
	if not r or not req then
		return false, { "Type" }
	end
	local a = Rooms.roomArea(world, roomId)
	if not a then
		return false, { "Area" }
	end
	local missing = {}
	if a.hallway or #a.rooms > 1 then
		table.insert(missing, "Hallway")
	end
	if #keyPieces(world, roomId) == 0 then
		table.insert(missing, "KeyFurniture")
	end
	if a.size < req.minCells then
		table.insert(missing, "MinSize")
	end
	if #a.doors == 0 then
		table.insert(missing, "Door")
	else
		local w = walkOf(world)
		local reach = fromEntrance(w)
		local reached = false
		for _, k in a.cells do
			local hx, hz = Rooms.halfOf(k)
			for dz = 0, SQ - 1 do
				for dx = 0, SQ - 1 do
					if reach[sqKey(a.floor, hx * SQ + dx, hz * SQ + dz)] ~= nil then
						reached = true
						break
					end
				end
				if reached then
					break
				end
			end
			if reached then
				break
			end
		end
		if not reached then
			table.insert(missing, "Unreached")
		end
	end
	if #missing > 0 then
		return false, missing
	end
	return true, nil
end

-- ===== Pieces, decor and tiles among the walls (wiring, 2026-10-21) =====

-- The square of a cell nearest its middle a guest can stand on (where a desk's queue or a stair's foot is stood on).
function Rooms.spotSquare(world: World, s: Grid.Spot): Spot?
	local k = anchor(walkOf(world), s)
	return if k then sqOf(k) else nil
end

-- Whether a wall stands on a half edge with either side in one of `cells` (cellKeys).
local function wallTouches(world: World, cells: { [number]: boolean }): boolean
	for e in world.walls do
		local floor, hx, hz, o = Rooms.edgeOf(e)
		local ax, az, bx, bz = sides(hx, hz, o)
		if
			cells[cellKey(floor, ax // HC, az // HC)]
			or cells[cellKey(floor, bx // HC, bz // HC)]
		then
			return true
		end
	end
	return false
end

local function withoutPiece(world: World, skip: Grid.Placed?): World
	local out = table.clone(world)
	out.pieces = {}
	for _, p in world.pieces do
		if not (skip and (p == skip or (p.id ~= nil and p.id == skip.id))) then
			table.insert(out.pieces, p)
		end
	end
	return out
end

--[[ Whether a desk or a stair may stand where `piece` says, among the walls
	(`skip` a piece being moved): Grid's rules for the cells (bounds, tiles,
	overlap, the mouth), no decor and no wall on its cells (a stair's well
	too), no room taken or merged, nothing guests reached cut off, and its
	own spots (the queue, the foot and head) reached on the squares. ]]
function Rooms.canPlacePiece(
	world: World,
	piece: Grid.Placed,
	skip: Grid.Placed?
): (boolean, string?)
	local bare = table.clone(world)
	bare.decor = {}
	local ok, why = Grid.canPlace(bare, piece, skip)
	if not ok then
		return false, why
	end
	local mine: { [number]: boolean } = {}
	for _, c in Grid.cells(piece) do
		mine[cellKey(piece.floor, c.x, c.z)] = true
		if piece.kind == "Stairs" then
			mine[cellKey(piece.floor + 1, c.x, c.z)] = true
		end
	end
	for _, d in world.decor do
		for _, s in Grid.squares(d) do
			if mine[cellKey(d.floor, s.x // Q, s.z // Q)] then
				return false, "Decor"
			end
		end
	end
	if wallTouches(world, mine) then
		return false, "Wall"
	end
	local before = withoutPiece(world, skip)
	local after = withoutPiece(world, skip)
	table.insert(after.pieces, piece)
	local fine, refusal = Rooms.check(before, after)
	if not fine then
		return false, refusal
	end
	local reached = reachedTargets(after)
	for _, s in Grid.doors(piece) do
		if not reached[`{s.floor}:{s.x}:{s.z}`] then
			return false, "DoorUnreachable"
		end
	end
	return true, nil
end

-- Whether a desk or a stair may be taken away: Grid's (never the last desk) and nothing cut off among the walls.
function Rooms.canRemovePiece(world: World, piece: Grid.Placed): (boolean, string?)
	local bare = table.clone(world)
	bare.decor = {}
	local ok, why = Grid.canRemove(bare, piece)
	if not ok then
		return false, why
	end
	return Rooms.check(world, withoutPiece(world, piece))
end

-- The squares beside a door's half edge, on both sides: kept clear of anything but rugs.
local function doorwaySquares(world: World): { [number]: boolean }
	local out = {}
	for e, rec in world.walls do
		if rec.door then
			local floor, hx, hz, o = Rooms.edgeOf(e)
			local ax, az, bx, bz = sides(hx, hz, o)
			for _, h in { { ax, az }, { bx, bz } } do
				for dz = 0, SQ - 1 do
					for dx = 0, SQ - 1 do
						local sx, sz = h[1] * SQ + dx, h[2] * SQ + dz
						-- Only the row of squares touching the edge.
						local touching = if o == 0
							then (h[2] == az and dz == SQ - 1) or (h[2] == bz and dz == 0)
							else (h[1] == ax and dx == SQ - 1) or (h[1] == bx and dx == 0)
						if touching then
							out[sqKey(floor, sx, sz)] = true
						end
					end
				end
			end
		end
	end
	return out
end

--[[ Whether decor or furniture `d` may stand where it is (A.12 "Furniture":
	on the decor grid like decor; `skip` a record's id being moved): on owned
	cells, off pieces and stairwells, nothing but a rug in the entrance's
	mouth or a doorway, never across a wall (rugs lie under walls), two of a
	layer never overlapping (rugs under the rest), a `Wall` piece with its
	back on a wall without a door or on the facade, and nothing guests
	reached cut off. ]]
function Rooms.canPlaceDecor(world: World, d: Grid.DecorPlaced, skip: string?): (boolean, string?)
	if d.floor < 1 or d.floor > world.floors or d.floor % 1 ~= 0 then
		return false, "NoFloor"
	end
	if d.r < 0 or d.r > 3 or d.r % 1 ~= 0 then
		return false, "OutOfBounds"
	end
	local m = marks(world)
	local rug = d.layer == "Rug"
	local doorway = if rug then {} else doorwaySquares(world)
	local mine: { [number]: boolean } = {}
	for _, s in Grid.squares(d) do
		if s.x < 0 or s.z < 0 or s.x >= NQ or s.z >= NQ then
			return false, "OutOfBounds"
		end
		local cx, cz = s.x // Q, s.z // Q
		if not Grid.isOpen(world, d.floor, cx, cz) then
			return false, "Tile"
		end
		local ck = cellKey(d.floor, cx, cz)
		if m.stair[ck] or m.desk[ck] or m.other[ck] then
			return false, "Overlap"
		end
		if not rug and isMouth(d.floor, cx, cz) then
			return false, "Entrance"
		end
		if doorway[sqKey(d.floor, s.x, s.z)] then
			return false, "Doorway"
		end
		mine[sqKey(d.floor, s.x, s.z)] = true
	end
	local idx = indexWalls(world.walls)
	if not rug then
		-- Never across a wall: two of its squares on either side of a half edge with a wall.
		for _, s in Grid.squares(d) do
			for _, step in { { 1, 0 }, { 0, 1 } } do
				local nx, nz = s.x + step[1], s.z + step[2]
				if mine[sqKey(d.floor, nx, nz)] then
					local ax, az, bx, bz = s.x // SQ, s.z // SQ, nx // SQ, nz // SQ
					if
						(ax ~= bx or az ~= bz)
						and idx.any[between(d.floor, ax, az, bx - ax, bz - az)]
					then
						return false, "Across"
					end
				end
			end
		end
	end
	-- Two of a layer never overlap; rugs lie under the rest.
	for _, o in world.decor do
		local skipped = skip ~= nil and o.id == skip
		if not skipped and o.floor == d.floor and (o.layer == "Rug") == rug then
			for _, s in Grid.squares(o) do
				if mine[sqKey(o.floor, s.x, s.z)] then
					return false, "Overlap"
				end
			end
		end
	end
	if d.layer == "Wall" then
		-- Its back (opposite its front, Grid.doorFacing) against a wall without a door, or the facade.
		local ex, ez = Grid.extent(d.w, d.d, d.r)
		local back: { { number } } = {}
		if d.r == 0 then
			for x = d.x, d.x + ex - 1 do
				table.insert(back, { x, d.z + ez - 1, 0, 1 })
			end
		elseif d.r == 2 then
			for x = d.x, d.x + ex - 1 do
				table.insert(back, { x, d.z, 0, -1 })
			end
		elseif d.r == 1 then
			for z = d.z, d.z + ez - 1 do
				table.insert(back, { d.x, z, -1, 0 })
			end
		else
			for z = d.z, d.z + ez - 1 do
				table.insert(back, { d.x + ex - 1, z, 1, 0 })
			end
		end
		for _, b in back do
			local sx, sz, dx, dz = b[1], b[2], b[3], b[4]
			local nx, nz = sx + dx, sz + dz
			local outside = nx < 0
				or nz < 0
				or nx >= NQ
				or nz >= NQ
				or not Grid.isOpen(world, d.floor, nx // Q, nz // Q)
			local ax, az, bx, bz = sx // SQ, sz // SQ, nx // SQ, nz // SQ
			local walled = (ax ~= bx or az ~= bz)
				and idx.shut[between(d.floor, ax, az, bx - ax, bz - az)] == true
			if not outside and not walled then
				return false, "NoWall"
			end
		end
	end
	if not rug then
		local before = table.clone(world)
		before.decor = {}
		for _, o in world.decor do
			if not (skip ~= nil and o.id == skip) then
				table.insert(before.decor, o)
			end
		end
		local after = table.clone(before)
		after.decor = table.clone(before.decor)
		table.insert(after.decor, d)
		local ok, why = Rooms.check(before, after)
		if not ok then
			return false, why
		end
	end
	return true, nil
end

--[[ The walls a tile bought puts up by itself (his "the facade counts as a
	wall"): on every half edge between the new tile and a room's area on its
	floor, so a room never runs out into the new tile. `world` is before the
	purchase. ]]
function Rooms.autoWalls(world: World, floor: number, x: number, z: number): { Edge }
	local areas, of = computeAreas(world, floor, indexWalls(world.walls), marks(world))
	local out = {}
	for hz = z * HC, z * HC + HC - 1 do
		for hx = x * HC, x * HC + HC - 1 do
			for _, s in STEPS do
				local nx, nz = hx + s[1], hz + s[2]
				local inside = nx // HC == x and nz // HC == z
				local n = if inside then nil else of[Rooms.halfKey(nx, nz)]
				if
					n
					and nx >= 0
					and nz >= 0
					and nx < H
					and nz < H
					and #areas[n].rooms > 0
					and not areas[n].hallway
				then
					local e = betweenEdge(floor, hx, hz, s[1], s[2])
					if not world.walls[e] and not table.find(out, e) then
						table.insert(out, e)
					end
				end
			end
		end
	end
	table.sort(out)
	return out
end

--[[ Where `Wall_Post` stands (MODELS.md "Walls"): every vertex an inner wall
	or door touches but where exactly two meet in a straight line, as
	{ floor, vx, vz } in half-cell units (the vertex at half cell (vx, vz)'s
	lowest corner). ]]
function Rooms.posts(walls: { [Edge]: WallRecord }): { { floor: number, vx: number, vz: number } }
	local dirs: { [string]: { floor: number, vx: number, vz: number, e: number } } = {}
	local function add(floor: number, vx: number, vz: number, bit: number)
		local k = `{floor}:{vx}:{vz}`
		local v = dirs[k]
		if not v then
			v = { floor = floor, vx = vx, vz = vz, e = 0 }
			dirs[k] = v
		end
		v.e = bit32.bor(v.e, bit)
	end
	for e in walls do
		local floor, hx, hz, o = Rooms.edgeOf(e)
		if o == 0 then
			add(floor, hx, hz, 1) -- +x from its start
			add(floor, hx + 1, hz, 2) -- −x from its end
		else
			add(floor, hx, hz, 4) -- +z
			add(floor, hx, hz + 1, 8) -- −z
		end
	end
	local out = {}
	for _, v in dirs do
		if v.e ~= 3 and v.e ~= 12 then
			table.insert(out, { floor = v.floor, vx = v.vx, vz = v.vz })
		end
	end
	table.sort(out, function(a, b)
		if a.floor ~= b.floor then
			return a.floor < b.floor
		end
		if a.vz ~= b.vz then
			return a.vz < b.vz
		end
		return a.vx < b.vx
	end)
	return out
end

--[[ A room's door: the first door of its area (by key), and whether the room
	lies on the half edge's "a" side (before it, `sides`); nil without one. ]]
function Rooms.roomDoor(world: World, roomId: string): (Edge?, boolean)
	local a = Rooms.roomArea(world, roomId)
	if not a or #a.doors == 0 then
		return nil, false
	end
	local e = a.doors[1]
	local _, hx, hz, o = Rooms.edgeOf(e)
	local ax, az = sides(hx, hz, o)
	return e, table.find(a.cells, Rooms.halfKey(ax, az)) ~= nil
end

--[[ The squares either side of a room's door, at the middle of its half
	edge: (outside, inside); nil without a door. Staff stop outside it. ]]
function Rooms.doorSquares(world: World, roomId: string): (Spot?, Spot?)
	local e, insideA = Rooms.roomDoor(world, roomId)
	if not e then
		return nil, nil
	end
	local floor, hx, hz, o = Rooms.edgeOf(e)
	local a, b
	if o == 0 then
		a = { floor = floor, x = hx * SQ, z = hz * SQ - 1 }
		b = { floor = floor, x = hx * SQ, z = hz * SQ }
	else
		a = { floor = floor, x = hx * SQ - 1, z = hz * SQ }
		b = { floor = floor, x = hx * SQ, z = hz * SQ }
	end
	if insideA then
		return b, a
	end
	return a, b
end

-- The room whose area holds square (sx, sz) of `floor`, or nil.
function Rooms.roomAtSquare(world: World, floor: number, sx: number, sz: number): string?
	local a = Rooms.areaAt(world, floor, sx // SQ, sz // SQ)
	return if a and not a.hallway then a.room else nil
end

-- ===== Bars and bonuses =====

local function clamp01(v: number): number
	return math.clamp(v, 0, 1)
end

-- A room's three bars (A.12), each 0..1; all 0 for a room that is not there.
function Rooms.bars(world: World, roomId: string): Bars
	local r = world.rooms[roomId]
	local req = if r then Rooms.requirement(r.type) else nil
	local a = Rooms.roomArea(world, roomId)
	if not req or not a then
		return { size = 0, furniture = 0, decor = 0 }
	end
	local span = req.fullCells - req.minCells
	local size = if span > 0
		then clamp01((a.size - req.minCells) / span)
		else (if a.size >= req.minCells then 1 else 0)
	local c = Rooms.contents(world, roomId)
	local fp, dp = 0, 0
	for _, d in c.furniture do
		fp += Furnish.points(d.item)
	end
	for _, d in c.decor do
		dp += Furnish.points(d.item)
	end
	local decorTarget = req.decorTarget(a.size)
	return {
		size = size,
		furniture = if req.furnitureTarget > 0 then clamp01(fp / req.furnitureTarget) else 1,
		decor = if decorTarget > 0 then clamp01(dp / decorTarget) else 0,
	}
end

-- What a room's bars give (A.12, his yes to the mapping): each linear in its bar.
function Rooms.bonuses(bars: Bars): Bonuses
	local s, f, d = clamp01(bars.size), clamp01(bars.furniture), clamp01(bars.decor)
	return {
		pay = (1 + R.SizePay * s) * (1 + R.FurniturePay * f),
		stay = 1 + R.SizeStay * s,
		satisfaction = R.FurnitureSatisfaction * f + R.DecorSatisfaction * d,
		friendship = 1 + R.DecorFriendship * d,
	}
end

--[[ Comfort's room part (A.12, his "no room deducts points"): what each
	READY room's bars add, summed, to the cap. Adding a room never lowers it. ]]
function Rooms.comfortPoints(ready: { Bars }): number
	local sum = 0
	for _, b in ready do
		sum += (clamp01(b.size) + clamp01(b.furniture) + clamp01(b.decor)) / 3 * R.ComfortPerRoom
	end
	return math.min(sum, R.ComfortRoomsCap)
end

return Rooms
