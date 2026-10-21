--!strict
--[[
	Furnishing a room (GDD §5.4, his yes 2026-10-19), as pure functions: where
	decor may stand inside a room's walls, what a room's decor is worth, and
	the tier and preference tags it gives the room. The server checks every
	placement with it, the build mode's ghost asks it the same question, and
	the specs hold it to its rules. Hallway decor is `Grid`'s.

	THE ROOM'S FRAME. A room's decor is reasoned about in the room's own
	frame, as it was authored (MODELS.md, "Hotel kit"): rotation 0, squares
	(x, z) from its footprint's lowest corner, x 0..w·Squares−1 and
	z 0..d·Squares−1, the door on the z = 0 side. `toRoom` and `fromRoom` turn
	decor between that frame and the plot's, so decor moves with its room.

	BUILT ROOMS (A.12, 2026-10-21) replaced placed rooms: the game asks
	`Rooms` where decor and furniture stand. What it still uses here is a
	piece's points and tags (`points`, `tags`); the room-frame rules and the
	tiers stay, specced, for nothing in the game now.

	THE RULES. Decor stays inside the walls; never in the doorway (the middle
	two squares of the door's cell, two deep: 6 × 6 studs inside the door);
	`Floor` and `Wall` pieces never on the room's own furniture (`blocked`,
	read from the model's `Bed`, `Furniture` and `Centrepiece`) nor on each
	other; a `Rug` never on another rug but under anything; a `Wall` piece
	only with its back against a wall.

	THE TIER. Each decor item is worth its price in points
	(`Economy.PointsPerCash`); a room reaches T2 and T3 at `TierPoints`, scaled
	by its cells over a 2×2's. Its tags are its decor's.
]]

local Constants = require(script.Parent.Constants)
local Grid = require(script.Parent.Grid)
local Pieces = require(script.Parent.Pieces)

local E = Constants.Economy
local Q = Constants.Grid.Squares

local Furnish = {}

export type Room = { x: number, z: number, r: number, w: number, d: number }
export type Item = { x: number, z: number, r: number, w: number, d: number }
export type Local = { x: number, z: number, r: number }
export type Placed = {
	x: number,
	z: number,
	r: number,
	w: number,
	d: number,
	layer: string,
	id: string?,
}
export type Refusal = "Outside" | "Doorway" | "Furniture" | "Overlap" | "NoWall"

--[[ Decor in the plot's squares to the room's frame. Worked in doubled
	squares so a centre stays whole: one quarter turn takes the room's local
	(x, z) to the plot's (−z, x) (CFrame.Angles(0, −π/2, 0)). ]]
function Furnish.toRoom(room: Room, d: Item): Local
	local ex, ez = Grid.extent(d.w, d.d, d.r)
	local rex, rez = Grid.extent(room.w, room.d, room.r)
	local ox = 2 * d.x + ex - (2 * room.x * Q + rex * Q)
	local oz = 2 * d.z + ez - (2 * room.z * Q + rez * Q)
	for _ = 1, room.r do
		ox, oz = oz, -ox
	end
	local lr = (d.r - room.r) % 4
	local lex, lez = Grid.extent(d.w, d.d, lr)
	return {
		x = (ox + room.w * Q - lex) // 2,
		z = (oz + room.d * Q - lez) // 2,
		r = lr,
	}
end

-- The room's frame back to the plot's squares.
function Furnish.fromRoom(room: Room, l: Local, w: number, d: number): Local
	local lex, lez = Grid.extent(w, d, l.r)
	local ox = 2 * l.x + lex - room.w * Q
	local oz = 2 * l.z + lez - room.d * Q
	for _ = 1, room.r do
		ox, oz = -oz, ox
	end
	local r = (room.r + l.r) % 4
	local rex, rez = Grid.extent(room.w, room.d, room.r)
	local ex, ez = Grid.extent(w, d, r)
	return {
		x = (ox + 2 * room.x * Q + rex * Q - ex) // 2,
		z = (oz + 2 * room.z * Q + rez * Q - ez) // 2,
		r = r,
	}
end

-- Whether every square of `d` (plot squares) is inside the room's footprint.
function Furnish.inside(room: Room, d: Item): boolean
	local rex, rez = Grid.extent(room.w, room.d, room.r)
	local ex, ez = Grid.extent(d.w, d.d, d.r)
	return d.x >= room.x * Q
		and d.z >= room.z * Q
		and d.x + ex <= (room.x + rex) * Q
		and d.z + ez <= (room.z + rez) * Q
end

-- Whether any square of `d` is inside the room's footprint.
function Furnish.touches(room: Room, d: Item): boolean
	local rex, rez = Grid.extent(room.w, room.d, room.r)
	local ex, ez = Grid.extent(d.w, d.d, d.r)
	return d.x < (room.x + rex) * Q
		and d.z < (room.z + rez) * Q
		and d.x + ex > room.x * Q
		and d.z + ez > room.z * Q
end

local function squareKey(x: number, z: number): number
	return z * 256 + x
end
Furnish.squareKey = squareKey

-- The squares of an item in the room's frame.
local function localSquares(l: Local, w: number, d: number): { { x: number, z: number } }
	local ex, ez = Grid.extent(w, d, l.r)
	local out = {}
	for dx = 0, ex - 1 do
		for dz = 0, ez - 1 do
			table.insert(out, { x = l.x + dx, z = l.z + dz })
		end
	end
	return out
end

--[[ Whether decor `item` (in the room's frame, with its size and layer) may
	stand in a w × d room holding `others` (in the room's frame), with the
	room's own furniture on `blocked` squares. `skip` is an item being moved. ]]
function Furnish.canPlace(
	room: { w: number, d: number },
	others: { Placed },
	item: Placed,
	blocked: { [number]: boolean }?,
	skip: string?
): (boolean, Refusal?)
	local W, D = room.w * Q, room.d * Q
	local ex, ez = Grid.extent(item.w, item.d, item.r)
	if item.x < 0 or item.z < 0 or item.x + ex > W or item.z + ez > D then
		return false, "Outside"
	end
	local along = Grid.doorAlong(room.w)
	local door0, door1 = along * Q + 1, along * Q + Q - 2
	local mine = {}
	for _, s in localSquares(item, item.w, item.d) do
		mine[squareKey(s.x, s.z)] = true
		if item.layer ~= "Rug" then
			if s.z <= 1 and s.x >= door0 and s.x <= door1 then
				return false, "Doorway"
			end
			if blocked and blocked[squareKey(s.x, s.z)] then
				return false, "Furniture"
			end
		end
	end
	for _, o in others do
		if (skip == nil or o.id ~= skip) and (o.layer == "Rug") == (item.layer == "Rug") then
			for _, s in localSquares(o, o.w, o.d) do
				if mine[squareKey(s.x, s.z)] then
					return false, "Overlap"
				end
			end
		end
	end
	if item.layer == "Wall" then
		-- Its back (opposite its front, Grid.doorFacing) on a wall.
		local backed = (item.r == 0 and item.z + ez == D)
			or (item.r == 2 and item.z == 0)
			or (item.r == 1 and item.x == 0)
			or (item.r == 3 and item.x + ex == W)
		if not backed then
			return false, "NoWall"
		end
	end
	return true, nil
end

--[[ The squares a room's own furniture covers, in its frame, from boxes in
	the piece's own studs (origin at the footprint's centre, as authored). ]]
function Furnish.blocked(
	room: { w: number, d: number },
	boxes: { { min: Vector3, max: Vector3 } }
): { [number]: boolean }
	local size = Constants.Grid.CellSize / Q
	local x0, z0 = -room.w * Q * size / 2, -room.d * Q * size / 2
	local out = {}
	for _, b in boxes do
		local a = math.max(0, math.floor((b.min.X + 0.05 - x0) / size))
		local c = math.min(room.w * Q - 1, math.floor((b.max.X - 0.05 - x0) / size))
		local e = math.max(0, math.floor((b.min.Z + 0.05 - z0) / size))
		local f = math.min(room.d * Q - 1, math.floor((b.max.Z - 0.05 - z0) / size))
		for x = a, c do
			for z = e, f do
				out[squareKey(x, z)] = true
			end
		end
	end
	return out
end

-- A decor item's points (§5.4: from its price).
function Furnish.points(id: string): number
	local d = Pieces.decor(id)
	return if d then math.floor(d.cost * E.PointsPerCash) else 0
end

-- What a room of w × d cells needs for each tier above T1.
function Furnish.thresholds(w: number, d: number): { number }
	local scale = w * d / E.TierPointsCells
	local out = {}
	for i, need in E.TierPoints do
		out[i] = math.ceil(need * scale)
	end
	return out
end

-- The tier a room of w × d cells reaches with `points` of decor (§5.4: T1..T3).
function Furnish.tier(w: number, d: number, points: number): number
	local tier = 1
	for i, need in Furnish.thresholds(w, d) do
		if points >= need then
			tier = i + 1
		end
	end
	return math.min(tier, E.MaxTier)
end

-- The points the next tier needs, or nil at the top.
function Furnish.nextTier(w: number, d: number, points: number): number?
	for _, need in Furnish.thresholds(w, d) do
		if points < need then
			return need
		end
	end
	return nil
end

-- The preference tags a room's decor gives it (§5.4).
function Furnish.tags(items: { string }): { [string]: boolean }
	local out: { [string]: boolean } = {}
	for _, id in items do
		local d = Pieces.decor(id)
		if d then
			for _, t in d.tags do
				out[t] = true
			end
		end
	end
	return out
end

return Furnish
