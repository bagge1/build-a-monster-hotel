--!strict
--[[
	The plot's grid (GDD §3, §5.1, §5.4, Appendix A.1): where a piece may
	stand, where its doors are, and how a guest walks to it. Pure: the server
	validates every placement with it, the client's ghost asks it the same
	question, and the specs hold it to its rules.

	THE FRAME. Cell (x, z): x 0..Cells-1 along the street, z 0..Cells-1 away
	from it; floor 1 at ground level. A piece's anchor is its footprint's
	lowest cell. Its rotation `r` (0..3) says which way its front faces: 0
	toward −z (the street), 1 toward +x, 2 toward +z, 3 toward −x. A piece
	w × d at r 0 or 2 covers w cells along x and d along z; at r 1 or 3 the
	other way round.

	WHAT IS THE HOTEL'S (§5.4, A.1, his rulings 2026-10-20). The plot is
	bought one cell at a time, a TILE, on each floor apart. A tile on floor
	f > 1 stands on an owned tile of the floor below, and can be bought when
	it shares an edge with an owned tile of its floor (a floor's first: over
	any owned tile below). A new floor has no tiles. A new hotel owns the
	square `StartTiles` on floor 1. Anything may stand on any owned cell:
	there is no lobby strip, no gallery and no area. The entrance's mouth,
	the two cells inside the arch (x 5–6, z 0), is never built on; a desk's
	queue may stand there. There may be several desks; the last cannot go.

	THE FACADE follows each floor's own outline of owned tiles
	(`Grid.facade`): a wall on each edge between an owned cell and one not
	owned (or the plot's edge), the street side included on every floor, a
	corner post where the outline turns, and the entrance arch on floor 1's
	front edge at the mouth. A wall section may carry one
	window the player placed (A.1), keyed by `edgeKey`; when a tile bought
	makes a windowed wall an inside one, the window moves out along its line
	(`moveWindows`).

	HALLWAYS ARE THE FREE CELLS of the hotel: not under a piece, not a
	stairwell, not furnished down the middle (decor in a cell's middle takes
	it; decor in its corners leaves it walkable, `Grid.blocks`). A stair on
	floor f takes its cells on f and, as its well, on f + 1; it joins the
	cell in front of its flight up (its foot, front-left, on f) to the cell in
	front of its flight down (its head, front-right, on f + 1). Guests walk
	in at the entrance; every piece's doors (a room's door cell, the desk's
	two front cells where the queue stands, a stair's foot and head) must be
	walkable and reached from it, over every floor and stair (`Grid.reach`).
	A change is refused if it would cut off a door that was reached before
	(the last stair to a floor with rooms cannot go). The same graph is the
	path a guest walks (§13.6, `Grid.route`).

	DECOR stands on squares, `Squares` to a cell side (3 studs): (x, z) are
	squares, from the plot's corner; w × d squares at rotation 0. Hallway
	decor is checked here; decor inside a room is `Furnish`'s.
]]

local Constants = require(script.Parent.Constants)

local G = Constants.Grid
local N = G.Cells
local Q = G.Squares
local NQ = N * Q

export type Placed = {
	item: string,
	kind: string, -- Pieces.Kind: "Room" | "Amenity" | "Stairs" | "Desk"
	floor: number,
	x: number,
	z: number,
	r: number,
	w: number,
	d: number,
	id: string?,
}
export type DecorPlaced = {
	item: string,
	layer: string, -- Pieces.Layer: "Floor" | "Rug" | "Wall"
	floor: number,
	x: number, -- squares
	z: number,
	r: number,
	w: number,
	d: number,
	room: string?, -- the room it stands in; nil or "" on hallway floor
	id: string?,
}
export type World = {
	floors: number,
	tiles: { [number]: boolean }, -- owned cells per floor, by `Grid.tileKey`
	pieces: { Placed },
	decor: { DecorPlaced },
}
export type Cell = { x: number, z: number }
export type Spot = { floor: number, x: number, z: number }
export type Leg = { floor: number?, cells: { Cell }?, stair: Placed?, up: boolean? }
export type Refusal =
	"OutOfBounds"
	| "Overlap"
	| "Tile"
	| "TileAbove"
	| "Entrance"
	| "Decor"
	| "DoorBlocked"
	| "DoorUnreachable"
	| "CutsOff"
	| "NoFloor"
	| "NoFloorAbove"
	| "DeskFloor"
	| "LastDesk"
	| "Wall"

local Grid = {}

Grid.Squares = Q

local function key(x: number, z: number): number
	return z * N + x
end

-- A cell on a floor as one number (floors from 1).
local function fkey(floor: number, x: number, z: number): number
	return (floor * N + z) * N + x
end

local function unkey(k: number): Spot
	return { floor = k // (N * N), z = (k // N) % N, x = k % N }
end

-- The footprint's size along x and z for a piece w × d at rotation r.
function Grid.extent(w: number, d: number, r: number): (number, number)
	if r % 2 == 0 then
		return w, d
	end
	return d, w
end

function Grid.inBounds(x: number, z: number): boolean
	return x >= 0 and z >= 0 and x < N and z < N
end

-- ===== Tiles (§5.4, A.1) =====

-- A floor's cell as one number: the key of `World.tiles` (and of the profile's, as a string).
function Grid.tileKey(floor: number, x: number, z: number): number
	return fkey(floor, x, z)
end

function Grid.tileOf(k: number): Spot
	return unkey(k)
end

-- A new hotel's tiles: the square `StartTiles` on floor 1 (his pick, 2026-10-20).
function Grid.startTiles(): { Cell }
	local s = G.StartTiles
	local out = {}
	for z = s.z, s.z + s.d - 1 do
		for x = s.x, s.x + s.w - 1 do
			table.insert(out, { x = x, z = z })
		end
	end
	return out
end

local function ownedTile(tiles: { [number]: boolean }, floor: number, x: number, z: number): boolean
	return Grid.inBounds(x, z) and tiles[fkey(floor, x, z)] == true
end

--[[ Whether a tile can be bought on `floor` (of `floors` built): on the plot,
	not owned, over an owned tile below (floor > 1), and sharing an edge with
	an owned tile of its floor unless it is the floor's first. ]]
function Grid.canBuyTile(
	tiles: { [number]: boolean },
	floors: number,
	floor: number,
	x: number,
	z: number
): (boolean, string?)
	if x % 1 ~= 0 or z % 1 ~= 0 or floor % 1 ~= 0 or not Grid.inBounds(x, z) then
		return false, "Unknown"
	end
	if floor < 1 or floor > floors then
		return false, "NoFloor"
	end
	if tiles[fkey(floor, x, z)] then
		return false, "Owned"
	end
	if floor > 1 and not tiles[fkey(floor - 1, x, z)] then
		return false, "NoTileBelow"
	end
	for _, n in { { x - 1, z }, { x + 1, z }, { x, z - 1 }, { x, z + 1 } } do
		if ownedTile(tiles, floor, n[1], n[2]) then
			return true, nil
		end
	end
	-- A floor's first tile stands anywhere over the floor below.
	for cz = 0, N - 1 do
		for cx = 0, N - 1 do
			if tiles[fkey(floor, cx, cz)] then
				return false, "NotNext"
			end
		end
	end
	return floor > 1, if floor > 1 then nil else "NotNext"
end

-- Every tile that can be bought now on `floor`.
function Grid.buyable(tiles: { [number]: boolean }, floors: number, floor: number): { Cell }
	local out = {}
	for z = 0, N - 1 do
		for x = 0, N - 1 do
			if Grid.canBuyTile(tiles, floors, floor, x, z) then
				table.insert(out, { x = x, z = z })
			end
		end
	end
	return out
end

-- Whether the cell is the hotel's on `floor`: an owned tile there.
function Grid.isOpen(world: World, floor: number, x: number, z: number): boolean
	return ownedTile(world.tiles, floor, x, z)
end

-- The entrance's mouth (floor 1), the two cells inside the arch: guests come in here.
function Grid.entrance(): { Cell }
	return { { x = N // 2 - 1, z = 0 }, { x = N // 2, z = 0 } }
end

local function isEntrance(floor: number, x: number, z: number): boolean
	return floor == 1 and z == 0 and (x == N // 2 - 1 or x == N // 2)
end

-- ===== A piece's cells and doors =====

--[[ The cell just outside the front edge, `along` cells from the piece's
	own left (its local −X). It can be out of bounds. ]]
function Grid.edgeCell(
	p: { x: number, z: number, r: number, w: number, d: number },
	along: number
): Cell
	local ex, ez = Grid.extent(p.w, p.d, p.r)
	if p.r == 0 then
		return { x = p.x + along, z = p.z - 1 }
	elseif p.r == 2 then
		return { x = p.x + ex - 1 - along, z = p.z + ez }
	elseif p.r == 1 then
		return { x = p.x + ex, z = p.z + along }
	end
	return { x = p.x - 1, z = p.z + ez - 1 - along }
end

--[[ Which cell along its front edge, from its own left, a piece's door is
	on: the middle (the left of the two middles on an even edge). ]]
function Grid.doorAlong(w: number): number
	return math.floor((w - 1) / 2)
end

--[[ The cell a room's door opens onto, just outside its front edge at
	`doorAlong`. ]]
function Grid.doorCell(p: { x: number, z: number, r: number, w: number, d: number }): Cell
	return Grid.edgeCell(p, Grid.doorAlong(p.w))
end

-- The cell inside the piece that the door belongs to (its threshold's inner side).
function Grid.doorInside(p: { x: number, z: number, r: number, w: number, d: number }): Cell
	local c = Grid.doorCell(p)
	if p.r == 0 then
		return { x = c.x, z = c.z + 1 }
	elseif p.r == 2 then
		return { x = c.x, z = c.z - 1 }
	elseif p.r == 1 then
		return { x = c.x - 1, z = c.z }
	end
	return { x = c.x + 1, z = c.z }
end

function Grid.cells(p: { x: number, z: number, r: number, w: number, d: number }): { Cell }
	local ex, ez = Grid.extent(p.w, p.d, p.r)
	local out = {}
	for dx = 0, ex - 1 do
		for dz = 0, ez - 1 do
			table.insert(out, { x = p.x + dx, z = p.z + dz })
		end
	end
	return out
end

-- A stair's foot (on its floor, before the flight up) and head (on the floor above).
function Grid.stairFoot(p: Placed): Spot
	local c = Grid.edgeCell(p, 0)
	return { floor = p.floor, x = c.x, z = c.z }
end

function Grid.stairHead(p: Placed): Spot
	local c = Grid.edgeCell(p, p.w - 1)
	return { floor = p.floor + 1, x = c.x, z = c.z }
end

--[[ The cells a piece needs walkable and reached: a room's or an amenity's
	door cell, the desk's two front cells (the queue), a stair's foot and head. ]]
function Grid.doors(p: Placed): { Spot }
	if p.kind == "Stairs" then
		return { Grid.stairFoot(p), Grid.stairHead(p) }
	elseif p.kind == "Desk" then
		local out = {}
		for along = 0, p.w - 1 do
			local c = Grid.edgeCell(p, along)
			table.insert(out, { floor = p.floor, x = c.x, z = c.z })
		end
		return out
	end
	local c = Grid.doorCell(p)
	return { { floor = p.floor, x = c.x, z = c.z } }
end

-- ===== Decor on squares =====

function Grid.squares(d: { x: number, z: number, r: number, w: number, d: number }): { Cell }
	return Grid.cells(d)
end

-- Whether a square, in its cell, is off the lanes guests walk down the middle of each cell.
local function inCorner(sx: number, sz: number): boolean
	local lx, lz = sx % Q, sz % Q
	return (lx == 0 or lx == Q - 1) and (lz == 0 or lz == Q - 1)
end

--[[ The cells a hallway decor piece takes from walking: those it reaches
	into the middle of. Rugs take none. ]]
function Grid.blocks(d: DecorPlaced): { Cell }
	local out, seen = {}, {}
	if d.layer == "Rug" then
		return out
	end
	for _, s in Grid.squares(d) do
		if not inCorner(s.x, s.z) then
			local cx, cz = s.x // Q, s.z // Q
			local k = key(cx, cz)
			if not seen[k] then
				seen[k] = true
				table.insert(out, { x = cx, z = cz })
			end
		end
	end
	return out
end

local function onHallway(d: DecorPlaced): boolean
	return d.room == nil or d.room == ""
end

-- ===== What is taken =====

type Occupancy = {
	piece: { [number]: Placed }, -- a piece's own cells
	well: { [number]: Placed }, -- a stair's cells on the floor above
	decor: { [number]: boolean }, -- hallway cells a decor piece takes
	decorAny: { [number]: boolean }, -- hallway cells holding any decor at all
	stairs: { Placed },
}

local function same(a: Placed?, b: Placed?): boolean
	if a == nil or b == nil then
		return false
	end
	return a == b or (a.id ~= nil and a.id == b.id)
end

local function occupy(
	world: World,
	skip: Placed?,
	extra: Placed?,
	decorSkip: DecorPlaced?,
	decorExtra: DecorPlaced?
): Occupancy
	local occ: Occupancy = { piece = {}, well = {}, decor = {}, decorAny = {}, stairs = {} }
	local function add(p: Placed)
		for _, c in Grid.cells(p) do
			occ.piece[fkey(p.floor, c.x, c.z)] = p
			if p.kind == "Stairs" then
				occ.well[fkey(p.floor + 1, c.x, c.z)] = p
			end
		end
		if p.kind == "Stairs" then
			table.insert(occ.stairs, p)
		end
	end
	for _, p in world.pieces do
		if not same(p, skip) then
			add(p)
		end
	end
	if extra then
		add(extra)
	end
	local function addDecor(d: DecorPlaced)
		if not onHallway(d) then
			return
		end
		for _, s in Grid.squares(d) do
			occ.decorAny[fkey(d.floor, s.x // Q, s.z // Q)] = true
		end
		for _, c in Grid.blocks(d) do
			occ.decor[fkey(d.floor, c.x, c.z)] = true
		end
	end
	for _, d in world.decor do
		if not (decorSkip and (d == decorSkip or (d.id ~= nil and d.id == decorSkip.id))) then
			addDecor(d)
		end
	end
	if decorExtra then
		addDecor(decorExtra)
	end
	return occ
end

local function walkable(world: World, occ: Occupancy, floor: number, x: number, z: number): boolean
	if floor < 1 or floor > world.floors or not Grid.isOpen(world, floor, x, z) then
		return false
	end
	local k = fkey(floor, x, z)
	return occ.piece[k] == nil and occ.well[k] == nil and not occ.decor[k]
end

local STEPS = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } }

type Hop = { to: number, stair: Placed, up: boolean }

--[[ Breadth-first over every floor from `from`, along hallways and up and
	down stairs: the parent map (key -> previous key, a start mapping to -1)
	and the stair taken into each key reached by one. ]]
local function flood(
	world: World,
	occ: Occupancy,
	from: { Spot }
): ({ [number]: number }, { [number]: Hop })
	local hops: { [number]: { Hop } } = {}
	for _, s in occ.stairs do
		local foot, head = Grid.stairFoot(s), Grid.stairHead(s)
		if
			walkable(world, occ, foot.floor, foot.x, foot.z)
			and walkable(world, occ, head.floor, head.x, head.z)
		then
			local a, b = fkey(foot.floor, foot.x, foot.z), fkey(head.floor, head.x, head.z)
			hops[a] = hops[a] or {}
			table.insert(hops[a], { to = b, stair = s, up = true })
			hops[b] = hops[b] or {}
			table.insert(hops[b], { to = a, stair = s, up = false })
		end
	end
	local parent: { [number]: number } = {}
	local via: { [number]: Hop } = {}
	local queue: { number } = {}
	for _, s in from do
		local k = fkey(s.floor, s.x, s.z)
		if walkable(world, occ, s.floor, s.x, s.z) and parent[k] == nil then
			parent[k] = -1
			table.insert(queue, k)
		end
	end
	local head = 1
	while head <= #queue do
		local k = queue[head]
		head += 1
		local c = unkey(k)
		for _, step in STEPS do
			local nx, nz = c.x + step[1], c.z + step[2]
			if walkable(world, occ, c.floor, nx, nz) then
				local nk = fkey(c.floor, nx, nz)
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

local function fromEntrance(world: World, occ: Occupancy): { [number]: number }
	local starts = {}
	for _, c in Grid.entrance() do
		table.insert(starts, { floor = 1, x = c.x, z = c.z })
	end
	local parent = flood(world, occ, starts)
	return parent
end

-- Whether every door of `p` is walkable and reached.
local function served(
	world: World,
	occ: Occupancy,
	reach: { [number]: number },
	p: Placed
): (boolean, boolean)
	local open, reached = true, true
	for _, s in Grid.doors(p) do
		if not walkable(world, occ, s.floor, s.x, s.z) then
			open = false
		end
		if reach[fkey(s.floor, s.x, s.z)] == nil then
			reached = false
		end
	end
	return open, reached
end

--[[ Whether every piece whose doors were reached before is still reached
	after (`skip` and `extra` describe the change). ]]
local function nothingCutOff(
	world: World,
	before: Occupancy,
	after: Occupancy,
	ignore: Placed?
): boolean
	local was = fromEntrance(world, before)
	local now = fromEntrance(world, after)
	for _, p in world.pieces do
		if not same(p, ignore) then
			local _, wasReached = served(world, before, was, p)
			if wasReached then
				local open, reached = served(world, after, now, p)
				if not open or not reached then
					return false
				end
			end
		end
	end
	return true
end

-- ===== Placing and removing pieces =====

--[[ Whether `piece` may be placed in `world`, and if not, why. `skip` is a
	piece being moved (left out while it is checked). ]]
function Grid.canPlace(world: World, piece: Placed, skip: Placed?): (boolean, Refusal?)
	local floor = piece.floor
	if piece.kind == "Stairs" then
		if floor < 1 or floor >= world.floors then
			return false, "NoFloorAbove"
		end
	elseif floor < 1 or floor > world.floors then
		return false, "NoFloor"
	end
	if piece.r < 0 or piece.r > 3 or piece.r % 1 ~= 0 then
		return false, "OutOfBounds"
	end
	if piece.kind == "Desk" and floor ~= 1 then
		return false, "DeskFloor"
	end
	local before = occupy(world, nil, nil)
	local occ = occupy(world, skip, nil)
	local function stacked(other: Placed?): boolean
		return piece.kind == "Stairs"
			and other ~= nil
			and other.kind == "Stairs"
			and other.x == piece.x
			and other.z == piece.z
			and other.r == piece.r
	end
	for _, c in Grid.cells(piece) do
		if not Grid.inBounds(c.x, c.z) then
			return false, "OutOfBounds"
		end
		if isEntrance(floor, c.x, c.z) then
			return false, "Entrance"
		end
		if not Grid.isOpen(world, floor, c.x, c.z) then
			return false, "Tile"
		end
		-- A stair rises into the floor above: its well needs that floor's tiles too.
		if piece.kind == "Stairs" and not Grid.isOpen(world, floor + 1, c.x, c.z) then
			return false, "TileAbove"
		end
		local k = fkey(floor, c.x, c.z)
		if occ.piece[k] then
			return false, "Overlap"
		end
		local well = occ.well[k]
		if well and not (stacked(well) and well.floor == floor - 1) then
			return false, "Overlap"
		end
		if occ.decorAny[k] then
			return false, "Decor"
		end
		if piece.kind == "Stairs" then
			-- Its well on the floor above.
			local k2 = fkey(floor + 1, c.x, c.z)
			local above = occ.piece[k2]
			if above and not (stacked(above) and above.floor == floor + 1) then
				return false, "Overlap"
			end
			if occ.decorAny[k2] then
				return false, "Decor"
			end
		end
	end
	local after = occupy(world, skip, piece)
	local reach = fromEntrance(world, after)
	for _, s in Grid.doors(piece) do
		if not walkable(world, after, s.floor, s.x, s.z) then
			return false, "DoorBlocked"
		end
	end
	local _, reached = served(world, after, reach, piece)
	if not reached then
		return false, "DoorUnreachable"
	end
	if not nothingCutOff(world, before, after, skip) then
		return false, "CutsOff"
	end
	return true, nil
end

--[[ Whether `piece` may be taken away (sold): never the last desk; never a
	stair (or anything) whose going would cut a door off, such as the last
	stair to a floor with rooms (§5.4). ]]
function Grid.canRemove(world: World, piece: Placed): (boolean, Refusal?)
	if piece.kind == "Desk" then
		local others = 0
		for _, p in world.pieces do
			if p.kind == "Desk" and not same(p, piece) then
				others += 1
			end
		end
		if others == 0 then
			return false, "LastDesk"
		end
	end
	local before = occupy(world, nil, nil)
	local after = occupy(world, piece, nil)
	if not nothingCutOff(world, before, after, piece) then
		return false, "CutsOff"
	end
	return true, nil
end

-- ===== Hallway decor =====

--[[ Whether hallway decor `d` (on hallway floor, in no room) may stand
	there. `skip` is decor being moved. ]]
function Grid.canPlaceDecor(world: World, d: DecorPlaced, skip: DecorPlaced?): (boolean, Refusal?)
	if d.floor < 1 or d.floor > world.floors then
		return false, "NoFloor"
	end
	if d.r < 0 or d.r > 3 or d.r % 1 ~= 0 then
		return false, "OutOfBounds"
	end
	if d.layer == "Wall" then
		return false, "Wall"
	end
	local occ = occupy(world, nil, nil, skip)
	for _, s in Grid.squares(d) do
		if s.x < 0 or s.z < 0 or s.x >= NQ or s.z >= NQ then
			return false, "OutOfBounds"
		end
		local cx, cz = s.x // Q, s.z // Q
		if not Grid.isOpen(world, d.floor, cx, cz) then
			return false, "Tile"
		end
		local k = fkey(d.floor, cx, cz)
		if occ.piece[k] or occ.well[k] then
			return false, "Overlap"
		end
		-- Nothing but a rug in the entrance's mouth (A.1).
		if d.layer ~= "Rug" and isEntrance(d.floor, cx, cz) then
			return false, "Entrance"
		end
	end
	-- Two of a layer never overlap; rugs lie under the rest.
	local mine = {}
	for _, s in Grid.squares(d) do
		mine[s.z * NQ + s.x] = true
	end
	for _, other in world.decor do
		local skipped = skip and (other == skip or (other.id ~= nil and other.id == skip.id))
		if
			not skipped
			and onHallway(other)
			and other.floor == d.floor
			and (other.layer == "Rug") == (d.layer == "Rug")
		then
			for _, s in Grid.squares(other) do
				if mine[s.z * NQ + s.x] then
					return false, "Overlap"
				end
			end
		end
	end
	if d.layer ~= "Rug" then
		local before = occupy(world, nil, nil)
		local after = occupy(world, nil, nil, skip, d)
		for _, c in Grid.entrance() do
			if not walkable(world, after, 1, c.x, c.z) then
				return false, "Entrance"
			end
		end
		if not nothingCutOff(world, before, after, nil) then
			return false, "CutsOff"
		end
	end
	return true, nil
end

-- ===== Paths =====

-- Keeps a run of cells' ends and every turn.
local function turns(cells: { Cell }): { Cell }
	local out: { Cell } = { cells[1] }
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

--[[ The way a guest walks from `from` to `to`, over floors and stairs: a
	list of legs, each a floor's cells (their turns, both ends included) or a
	stair to climb (`up`) or descend; nil if there is no way. ]]
function Grid.route(world: World, from: Spot, to: Spot): { Leg }?
	local occ = occupy(world, nil, nil)
	local parent, via = flood(world, occ, { from })
	local k = fkey(to.floor, to.x, to.z)
	if parent[k] == nil then
		return nil
	end
	local chain: { number } = {}
	while k ~= -1 do
		table.insert(chain, 1, k)
		k = parent[k]
	end
	local legs: { Leg } = {}
	local run: { Cell } = {}
	local runFloor = from.floor
	for i, ck in chain do
		local hop = via[ck]
		if hop and i > 1 then
			table.insert(legs, { floor = runFloor, cells = turns(run) })
			table.insert(legs, { stair = hop.stair, up = hop.up })
			run = {}
		end
		local s = unkey(ck)
		runFloor = s.floor
		table.insert(run, { x = s.x, z = s.z })
	end
	table.insert(legs, { floor = runFloor, cells = turns(run) })
	return legs
end

-- The cells a guest walks on one floor (a route that stays on it), or nil.
function Grid.path(world: World, floor: number, from: Cell, to: Cell): { Cell }?
	local legs = Grid.route(
		world,
		{ floor = floor, x = from.x, z = from.z },
		{ floor = floor, x = to.x, z = to.z }
	)
	if not legs or #legs ~= 1 then
		return nil
	end
	return legs[1].cells
end

-- Whether a cell on a floor is a hallway now (for drawing and the specs).
function Grid.walkable(world: World, floor: number, x: number, z: number): boolean
	return walkable(world, occupy(world, nil, nil), floor, x, z)
end

-- Every piece's doors walkable and reached (the invariant every accepted change keeps).
function Grid.allServed(world: World): boolean
	local occ = occupy(world, nil, nil)
	local reach = fromEntrance(world, occ)
	for _, p in world.pieces do
		local open, reached = served(world, occ, reach, p)
		if not open or not reached then
			return false
		end
	end
	return true
end

-- ===== The facade's outline (§5.4, A.1; MODELS.md "Facade") =====

export type FacadePiece = {
	kind: "Wall" | "Entrance" | "Corner",
	window: string?, -- a wall's window type (A.1), nil for a plain wall
	x: number?, -- a wall's cell and side, for its `edgeKey`
	z: number?,
	side: number?,
	floor: number,
	at: Vector3, -- plot-local: the middle of the cell edge (a corner's vertex), on the floor's walking surface
	turn: number, -- quarter turns about +Y (CFrame.Angles(0, turn * π/2, 0)) from the piece's authored frame
}

-- The four sides of a cell (`side` 0..3): the step to the cell beyond it, and the turn that faces a piece's −Z out of it.
local SIDES = {
	{ dx = 0, dz = -1, turn = 0 }, -- the front, toward the street
	{ dx = -1, dz = 0, turn = 1 },
	{ dx = 0, dz = 1, turn = 2 },
	{ dx = 1, dz = 0, turn = 3 },
}

-- The quadrants round a vertex (x and z signs) and the turn that puts a corner post's −X −Z quadrant there.
local QUADRANTS = { { -1, -1, 0 }, { -1, 1, 1 }, { 1, 1, 2 }, { 1, -1, 3 } }

-- A wall section's key in the profile's `windows`: floor, cell and side (0 front, 1 −x, 2 back, 3 +x).
function Grid.edgeKey(floor: number, x: number, z: number, side: number): string
	return `{floor}:{x}:{z}:{side}`
end

function Grid.edgeOf(edge: string): (number, number, number, number)
	local parts = string.split(edge, ":")
	return tonumber(parts[1]) or 0,
		tonumber(parts[2]) or 0,
		tonumber(parts[3]) or 0,
		tonumber(parts[4]) or 0
end

--[[ Whether the edge on `side` of cell (x, z) on `floor` is a facade wall
	section, which can carry a window: the cell owned on that floor, the one
	beyond not, not the entrance's arch. ]]
function Grid.isWall(
	tiles: { [number]: boolean },
	floors: number,
	floor: number,
	x: number,
	z: number,
	side: number
): boolean
	local s = SIDES[side + 1]
	if not s or floor < 1 or floor > floors or floor % 1 ~= 0 then
		return false
	end
	local nx, nz = x + s.dx, z + s.dz
	if not ownedTile(tiles, floor, x, z) or ownedTile(tiles, floor, nx, nz) then
		return false
	end
	if nz < 0 and isEntrance(floor, x, z) then
		return false
	end
	return true
end

--[[ The windows after tiles are bought (A.1, his pick): a window whose wall is
	no longer a wall moves out along its line, on its floor and side, to the
	first wall it meets; one that meets none, or a wall that has a window
	already, comes back as `refunded` (its key and record). ]]
function Grid.moveWindows<T>(
	tiles: { [number]: boolean },
	floors: number,
	windows: { [string]: T }
): ({ [string]: T }, { { key: string, window: T } })
	local out: { [string]: T } = {}
	local moving: { { key: string, window: T } } = {}
	local keys = {}
	for k in windows do
		table.insert(keys, k)
	end
	table.sort(keys)
	for _, k in keys do
		local floor, x, z, side = Grid.edgeOf(k)
		if Grid.isWall(tiles, floors, floor, x, z, side) then
			out[k] = windows[k]
		else
			table.insert(moving, { key = k, window = windows[k] })
		end
	end
	local refunded = {}
	for _, m in moving do
		local floor, x, z, side = Grid.edgeOf(m.key)
		local s = SIDES[side + 1]
		local landed = false
		while s and ownedTile(tiles, floor, x, z) do
			if Grid.isWall(tiles, floors, floor, x, z, side) then
				local k = Grid.edgeKey(floor, x, z, side)
				if out[k] == nil then
					out[k] = m.window
					landed = true
				end
				break
			end
			x += s.dx
			z += s.dz
		end
		if not landed then
			table.insert(refunded, m)
		end
	end
	return out, refunded
end

--[[ Every facade piece round the owned tiles on floors 1..`floors`: a
	`Wall` on each edge between an owned cell and one not owned or off the
	plot, the `Entrance` (one piece over both cells) on floor 1's front edge
	at the mouth, and a `Corner` at each vertex where the outline turns,
	filling the empty cell's quadrant there. Each floor has its own outline,
	and its street side is walled too (his ruling, 2026-10-20). A wall whose
	`edgeKey` is in `windows` carries that window type. ]]
function Grid.facade(
	tiles: { [number]: boolean },
	floors: number,
	windows: { [string]: string }?
): { FacadePiece }
	local C = G.CellSize
	local out: { FacadePiece } = {}
	local mouth = Grid.entrance()
	for floor = 1, floors do
		local y = Grid.floorY(floor)
		local function owned(x: number, z: number): boolean
			return ownedTile(tiles, floor, x, z)
		end
		for z = 0, N - 1 do
			for x = 0, N - 1 do
				if owned(x, z) then
					for sideIndex, side in SIDES do
						local nx, nz = x + side.dx, z + side.dz
						if not owned(nx, nz) then
							if floor == 1 and nz < 0 and isEntrance(1, x, z) then
								-- One arch over the mouth's two cells, drawn once at its middle.
								if x == mouth[1].x and owned(mouth[2].x, mouth[2].z) then
									table.insert(out, {
										kind = "Entrance",
										floor = floor,
										at = Vector3.new((x + 1) * C, y, 0),
										turn = 0,
									})
								end
							else
								table.insert(out, {
									kind = "Wall",
									window = if windows
										then windows[Grid.edgeKey(floor, x, z, sideIndex - 1)]
										else nil,
									x = x,
									z = z,
									side = sideIndex - 1,
									floor = floor,
									at = Vector3.new(
										(x + 0.5 + side.dx / 2) * C,
										y,
										(z + 0.5 + side.dz / 2) * C
									),
									turn = side.turn,
								})
							end
						end
					end
				end
			end
		end
		-- A vertex has four cells round it. A post fills an empty one when both
		-- its edge neighbours are owned (a concave corner), or when both are
		-- empty and the cell across the vertex is owned (a convex one).
		for vz = 0, N do
			for vx = 0, N do
				local function at(sx: number, sz: number): boolean
					return owned(vx + (if sx < 0 then -1 else 0), vz + (if sz < 0 then -1 else 0))
				end
				for _, q in QUADRANTS do
					local sx, sz = q[1], q[2]
					if not at(sx, sz) then
						local a, b = at(-sx, sz), at(sx, -sz)
						if (a and b) or (not a and not b and at(-sx, -sz)) then
							table.insert(out, {
								kind = "Corner",
								floor = floor,
								at = Vector3.new(vx * C, y, vz * C),
								turn = q[3],
							})
						end
					end
				end
			end
		end
	end
	return out
end

-- ===== Frames =====

-- A cell's centre in plot-local studs, on its floor's slab.
function Grid.cellCentre(floor: number, c: Cell): Vector3
	return Vector3.new((c.x + 0.5) * G.CellSize, Grid.floorY(floor), (c.z + 0.5) * G.CellSize)
end

-- The height of a floor's walking surface, plot-local.
function Grid.floorY(floor: number): number
	return (floor - 1) * G.FloorHeight + G.SlabThickness
end

-- The footprint's centre, plot-local, on its floor.
function Grid.pieceCentre(p: {
	floor: number,
	x: number,
	z: number,
	r: number,
	w: number,
	d: number,
}): Vector3
	local ex, ez = Grid.extent(p.w, p.d, p.r)
	return Vector3.new(
		(p.x + ex / 2) * G.CellSize,
		Grid.floorY(p.floor),
		(p.z + ez / 2) * G.CellSize
	)
end

-- A decor piece's footprint centre, plot-local, on its floor's slab.
function Grid.decorCentre(d: {
	floor: number,
	x: number,
	z: number,
	r: number,
	w: number,
	d: number,
}): Vector3
	local ex, ez = Grid.extent(d.w, d.d, d.r)
	local size = G.CellSize / Q
	return Vector3.new((d.x + ex / 2) * size, Grid.floorY(d.floor), (d.z + ez / 2) * size)
end

-- The middle of the door's threshold, plot-local: between doorInside and doorCell.
function Grid.doorPoint(p: {
	floor: number,
	x: number,
	z: number,
	r: number,
	w: number,
	d: number,
}): Vector3
	local a = Grid.cellCentre(p.floor, Grid.doorInside(p))
	local b = Grid.cellCentre(p.floor, Grid.doorCell(p))
	return (a + b) / 2
end

-- The unit vector the door faces, plot-local.
function Grid.doorFacing(r: number): Vector3
	if r == 0 then
		return Vector3.new(0, 0, -1)
	elseif r == 1 then
		return Vector3.new(1, 0, 0)
	elseif r == 2 then
		return Vector3.new(0, 0, 1)
	end
	return Vector3.new(-1, 0, 0)
end

return Grid
