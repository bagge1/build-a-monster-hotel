--!strict
--[[
	The plot's grid (GDD §3, §5.1, Appendix A.1): where a piece may stand, where
	its door is, and how a guest walks to it. Pure: the server validates every
	placement with it, the client's ghost preview asks it the same question,
	and the specs hold it to its rules.

	THE FRAME. Cell (x, z): x 0..Cells-1 along the street, z 0..Cells-1 away
	from it; floor 1 at ground level. A piece's anchor is its footprint's
	lowest cell. Its rotation `r` (0..3) says which way its door faces:
	0 toward −z (the street), 1 toward +x, 2 toward +z, 3 toward −x. A piece
	w × d at r 0 or 2 covers w cells along x and d along z; at r 1 or 3 the
	other way round.

	HALLWAYS ARE THE FREE CELLS. Floor 1's front `LobbyRows` rows are the
	lobby: walkable, never built on. The stair core is reserved on every floor
	and is no hallway: it is walled at the back and both sides (MODELS.md,
	"Stair core") and entered only across its front edge, from the lobby's
	back row on floor 1 and from its landing above, which is the way in to
	every upper floor. So a door onto the core opens into a wall, and a path
	goes round it, never through. A placement is legal only if every door
	(the new one and all the old) still opens onto a free cell connected to
	its floor's way in; the same graph is the path a guest walks (§13.6).
]]

local Constants = require(script.Parent.Constants)

local G = Constants.Grid
local N = G.Cells

export type Placed = {
	item: string,
	floor: number,
	x: number,
	z: number,
	r: number,
	w: number,
	d: number,
}
export type Cell = { x: number, z: number }

local Grid = {}

local function key(x: number, z: number): number
	return z * N + x
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

function Grid.isStairCore(x: number, z: number): boolean
	local s = G.StairCore
	return x >= s.x and x < s.x + s.w and z >= s.z and z < s.z + s.d
end

function Grid.isLobby(floor: number, _x: number, z: number): boolean
	return floor == 1 and z < G.LobbyRows
end

--[[ Above floor 1, the cells just in front of the stair core are its
	landing: the flight up starts and the flight down ends there, so nothing
	may stand on them (on floor 1 they are the lobby already). ]]
function Grid.isLanding(floor: number, x: number, z: number): boolean
	local s = G.StairCore
	return floor > 1 and z == s.z - 1 and x >= s.x and x < s.x + s.w
end

function Grid.isReserved(floor: number, x: number, z: number): boolean
	return Grid.isStairCore(x, z) or Grid.isLobby(floor, x, z) or Grid.isLanding(floor, x, z)
end

--[[ The cell a door opens onto, just outside the middle of the door's edge
	(the left of the two middles on an even edge). It can be out of bounds:
	a door facing the plot's edge has nowhere to open, and is refused. ]]
function Grid.doorCell(p: { x: number, z: number, r: number, w: number, d: number }): Cell
	local ex, ez = Grid.extent(p.w, p.d, p.r)
	local along = math.floor((p.w - 1) / 2)
	if p.r == 0 then
		return { x = p.x + along, z = p.z - 1 }
	elseif p.r == 2 then
		return { x = p.x + ex - 1 - along, z = p.z + ez }
	elseif p.r == 1 then
		return { x = p.x + ex, z = p.z + along }
	end
	return { x = p.x - 1, z = p.z + ez - 1 - along }
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

-- Which cells of one floor are taken by pieces (cell key -> true).
local function occupied(layout: { Placed }, floor: number, skip: Placed?): { [number]: boolean }
	local taken = {}
	for _, p in layout do
		if p.floor == floor and p ~= skip then
			for _, c in Grid.cells(p) do
				taken[key(c.x, c.z)] = true
			end
		end
	end
	return taken
end

-- A hallway cell: on the plot, not under a piece, not inside the stair core.
local function walkable(_floor: number, taken: { [number]: boolean }, x: number, z: number): boolean
	return Grid.inBounds(x, z) and not taken[key(x, z)] and not Grid.isStairCore(x, z)
end

--[[ The cells a floor is entered from: the lobby on floor 1 (its back row
	is the stair core's front), the landing in front of the core above. ]]
function Grid.wayIn(floor: number): { Cell }
	local out = {}
	local s = G.StairCore
	if floor > 1 then
		for x = s.x, s.x + s.w - 1 do
			table.insert(out, { x = x, z = s.z - 1 })
		end
	end
	if floor == 1 then
		for z = 0, G.LobbyRows - 1 do
			for x = 0, N - 1 do
				table.insert(out, { x = x, z = z })
			end
		end
	end
	return out
end

local STEPS = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } }

--[[ Breadth-first from `from` over free cells: returns the parent map (cell
	key -> previous cell key, the start mapping to -1). ]]
local function flood(
	floor: number,
	taken: { [number]: boolean },
	from: { Cell }
): { [number]: number }
	local parent: { [number]: number } = {}
	local queue: { Cell } = {}
	for _, c in from do
		if walkable(floor, taken, c.x, c.z) and parent[key(c.x, c.z)] == nil then
			parent[key(c.x, c.z)] = -1
			table.insert(queue, c)
		end
	end
	local head = 1
	while head <= #queue do
		local c = queue[head]
		head += 1
		for _, step in STEPS do
			local nx, nz = c.x + step[1], c.z + step[2]
			local k = key(nx, nz)
			if parent[k] == nil and walkable(floor, taken, nx, nz) then
				parent[k] = key(c.x, c.z)
				table.insert(queue, { x = nx, z = nz })
			end
		end
	end
	return parent
end

export type Refusal =
	"OutOfBounds"
	| "Overlap"
	| "Reserved"
	| "DoorBlocked"
	| "DoorUnreachable"
	| "CutsOff"
	| "NoFloor"

--[[ Whether `piece` may be placed on `layout`, and if not, why. `floors` is
	how many floors the hotel has. `skip` is a piece being moved (left out of
	the layout while it is checked). ]]
function Grid.canPlace(
	layout: { Placed },
	floors: number,
	piece: Placed,
	skip: Placed?
): (boolean, Refusal?)
	if piece.floor < 1 or piece.floor > floors then
		return false, "NoFloor"
	end
	if piece.r < 0 or piece.r > 3 or piece.r % 1 ~= 0 then
		return false, "OutOfBounds"
	end
	local taken = occupied(layout, piece.floor, skip)
	for _, c in Grid.cells(piece) do
		if not Grid.inBounds(c.x, c.z) then
			return false, "OutOfBounds"
		end
		if Grid.isReserved(piece.floor, c.x, c.z) then
			return false, "Reserved"
		end
		if taken[key(c.x, c.z)] then
			return false, "Overlap"
		end
	end
	-- Take the new piece's cells, then every door on the floor must still connect.
	local after = table.clone(taken)
	for _, c in Grid.cells(piece) do
		after[key(c.x, c.z)] = true
	end
	local reach = flood(piece.floor, after, Grid.wayIn(piece.floor))
	local door = Grid.doorCell(piece)
	if not walkable(piece.floor, after, door.x, door.z) then
		return false, "DoorBlocked"
	end
	if reach[key(door.x, door.z)] == nil then
		return false, "DoorUnreachable"
	end
	for _, p in layout do
		if p.floor == piece.floor and p ~= skip then
			local c = Grid.doorCell(p)
			if not walkable(piece.floor, after, c.x, c.z) or reach[key(c.x, c.z)] == nil then
				return false, "CutsOff"
			end
		end
	end
	return true, nil
end

--[[ The cells a guest walks on `floor`, from `from` to `to`, both
	included; nil if there is no way. Collinear cells are dropped, so the
	answer is the turns. ]]
function Grid.path(layout: { Placed }, floor: number, from: Cell, to: Cell): { Cell }?
	local taken = occupied(layout, floor, nil)
	local parent = flood(floor, taken, { from })
	if parent[key(to.x, to.z)] == nil then
		return nil
	end
	local cells: { Cell } = {}
	local k = key(to.x, to.z)
	while k ~= -1 do
		table.insert(cells, 1, { x = k % N, z = k // N })
		k = parent[k]
	end
	-- Keep the ends and every turn.
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

-- The middle of the door's threshold, plot-local: between doorInside and doorCell.
function Grid.doorPoint(
	p: { floor: number, x: number, z: number, r: number, w: number, d: number }
): Vector3
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
