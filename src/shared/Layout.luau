--!strict
--[[
	A hotel's saved layout as the pure rules see it (GDD §5.4): the pieces and
	the decor as a `Grid.World`, and what a room's decor makes of it (its
	points, tier and tags, `Furnish`). Shared, so the server (from the
	profile) and the build mode (from the state's copy) ask the same question.

	A record is `{ id, item, floor, x, z, r }`, a piece also `m` (mirrored,
	Flip), decor also `room` ("" on hallway floor). The server keeps them in
	maps keyed by id, the state sends lists; both are accepted.
]]

local Furnish = require(script.Parent.Furnish)
local Grid = require(script.Parent.Grid)
local Pieces = require(script.Parent.Pieces)

local Layout = {}

export type Record = { item: string, floor: number, x: number, z: number, r: number, m: boolean? }

local function each(records: { [any]: any }, fn: (string, any) -> ())
	for k, rec in records do
		local id = if rec.id ~= nil then tostring(rec.id) else tostring(k)
		fn(id, rec)
	end
end

function Layout.piece(id: string, rec: Record): Grid.Placed?
	local p = Pieces.get(rec.item)
	if not p then
		return nil
	end
	return {
		item = rec.item,
		kind = p.kind :: string,
		floor = rec.floor,
		x = rec.x,
		z = rec.z,
		r = rec.r,
		w = p.w,
		d = p.d,
		m = if rec.m and (p.kind == "Room" or p.kind == "Amenity") then true else nil,
		id = id,
	}
end

function Layout.decor(id: string, rec: Record & { room: string? }): Grid.DecorPlaced?
	local d = Pieces.decor(rec.item)
	if not d then
		return nil
	end
	return {
		item = rec.item,
		layer = d.layer :: string,
		floor = rec.floor,
		x = rec.x,
		z = rec.z,
		r = rec.r,
		w = d.w,
		d = d.d,
		room = if rec.room and rec.room ~= "" then tostring(rec.room) else nil,
		id = id,
	}
end

--[[ The world: `tiles` keyed by `Grid.tileKey` (floor and cell) as a string (the profile's) or
	a number; `pieces` and `decor` maps or lists of records. ]]
function Layout.world(
	floors: number,
	tiles: { [any]: boolean },
	pieces: { [any]: any },
	decor: { [any]: any },
	walls: { [string]: any }?,
	rooms: { [any]: any }?
): Grid.World & { walls: { [string]: any }, rooms: { [string]: any } }
	local owned = {}
	for k, v in tiles do
		if v then
			owned[tonumber(k) :: number] = true
		end
	end
	-- Built rooms (A.12): the inner walls by edge key, the rooms by id (maps, or the state's lists).
	local wallMap: { [string]: any } = {}
	for k, rec in walls or {} do
		if typeof(k) == "string" then
			wallMap[k] = rec
		elseif rec.edge then
			wallMap[rec.edge] = rec
		end
	end
	local roomMap: { [string]: any } = {}
	each(rooms or {}, function(id, rec)
		roomMap[id] = rec
	end)
	local world: Grid.World & { walls: { [string]: any }, rooms: { [string]: any } } = {
		floors = floors,
		tiles = owned,
		pieces = {},
		decor = {},
		walls = wallMap,
		rooms = roomMap,
	}
	each(pieces, function(id, rec)
		local p = Layout.piece(id, rec)
		if p then
			table.insert(world.pieces, p)
		end
	end)
	each(decor, function(id, rec)
		local d = Layout.decor(id, rec)
		if d then
			table.insert(world.decor, d)
		end
	end)
	return world
end

function Layout.find(world: Grid.World, id: string): Grid.Placed?
	for _, p in world.pieces do
		if p.id == id then
			return p
		end
	end
	return nil
end

function Layout.findDecor(world: Grid.World, id: string): Grid.DecorPlaced?
	for _, d in world.decor do
		if d.id == id then
			return d
		end
	end
	return nil
end

-- The decor inside a room, as items.
function Layout.roomItems(world: Grid.World, roomId: string): { string }
	local out = {}
	for _, d in world.decor do
		if d.room == roomId then
			table.insert(out, d.item)
		end
	end
	return out
end

-- A room's decor points, tier (§5.4: T1..T3) and the points its next tier needs.
function Layout.roomTier(world: Grid.World, roomId: string): (number, number, number?)
	local room = Layout.find(world, roomId)
	if not room then
		return 1, 0, nil
	end
	local points = 0
	for _, item in Layout.roomItems(world, roomId) do
		points += Furnish.points(item)
	end
	return Furnish.tier(room.w, room.d, points), points, Furnish.nextTier(room.w, room.d, points)
end

-- A room's decor tags (§5.4).
function Layout.roomTags(world: Grid.World, roomId: string): { [string]: boolean }
	return Furnish.tags(Layout.roomItems(world, roomId))
end

--[[ Where decor `d` would stand: in a room (its id), on hallway floor (""),
	or nowhere (nil, with why: across a wall or on a piece that takes none). ]]
function Layout.container(world: Grid.World, d: Grid.DecorPlaced): (string?, string?)
	for _, p in world.pieces do
		if p.floor == d.floor and Furnish.touches(p, d) then
			if p.kind == "Room" and Furnish.inside(p, d) then
				return p.id, nil
			end
			return nil, if p.kind == "Room" then "Across" else "Overlap"
		end
	end
	return "", nil
end

--[[ Whether decor `d` may stand where it is (in its room or on hallway
	floor), `skip` the id of decor being moved; `blocked` gives a room
	item's furniture squares (Furnish.blocked). Returns the room's id ("" for
	hallway floor) when it may. ]]
function Layout.canPlaceDecor(
	world: Grid.World,
	d: Grid.DecorPlaced,
	skip: string?,
	blocked: (string) -> { [number]: boolean }?
): (boolean, string?, string?)
	local roomId, why = Layout.container(world, d)
	if roomId == nil then
		return false, why, nil
	end
	if roomId == "" then
		local skipped = if skip then Layout.findDecor(world, skip) else nil
		local hallway = table.clone(d)
		hallway.room = nil
		local ok, refusal = Grid.canPlaceDecor(world, hallway, skipped)
		return ok, refusal, ""
	end
	local room = Layout.find(world, roomId) :: Grid.Placed
	local others = {}
	for _, o in world.decor do
		if o.room == roomId then
			local l = Furnish.toRoom(room, o)
			table.insert(
				others,
				{ x = l.x, z = l.z, r = l.r, w = o.w, d = o.d, layer = o.layer, id = o.id }
			)
		end
	end
	local l = Furnish.toRoom(room, d)
	local item = { x = l.x, z = l.z, r = l.r, w = d.w, d = d.d, layer = d.layer }
	local squares = if blocked then blocked(room.item) else nil
	if squares and room.m then
		squares = Furnish.mirrorSquares(room, squares)
	end
	local ok, refusal = Furnish.canPlace(room, others, item, squares, skip)
	return ok, refusal, roomId
end

return Layout
