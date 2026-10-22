-- Built rooms wired into the game (GDD §5.4, A.12, 2026-10-21): the start hotel,
-- desks, stairs and decor among the walls, tiles bought beside a room, posts.
local Rooms = require(Shared.Rooms)
local Grid = require(Shared.Grid)
local Constants = require(Shared.Constants)
local Pieces = require(Shared.Pieces)

local G = Constants.Grid
local Q = G.Squares
local HC = Rooms.HalfCells

local function placed(id, floor, x, z, r)
	local p = Pieces.get(id)
	return { item = id, kind = p.kind, floor = floor, x = x, z = z, r = r, w = p.w, d = p.d }
end

local function decor(id, floor, x, z, r, rid)
	local d = Pieces.decor(id)
	return {
		item = id,
		layer = d.layer,
		floor = floor,
		x = x,
		z = z,
		r = r,
		w = d.w,
		d = d.d,
		id = rid,
	}
end

-- A new hotel as PlayerData builds it: the start square, the desk, the start room.
local function startHotel()
	local tiles = {}
	for _, c in Grid.startTiles() do
		tiles[Grid.tileKey(1, c.x, c.z)] = true
	end
	local S = Constants.Rooms.Start
	local walls = {}
	for _, w in S.walls do
		for _, e in Rooms.cellEdges(1, w[1], w[2], w[3]) do
			walls[e] = { paid = 0 }
		end
	end
	walls[Rooms.edgeKey(1, S.door.hx, S.door.hz, S.door.o)] = { door = true, paid = 0 }
	local d = G.DeskStart
	local world = {
		floors = 1,
		tiles = tiles,
		pieces = { placed("FrontDesk", 1, d.x, d.z, d.r) },
		decor = {},
		walls = walls,
		rooms = { ["2"] = { type = S.type, floor = 1, hx = S.seed.hx, hz = S.seed.hz } },
	}
	world.pieces[1].id = "1"
	for i, f in S.furniture do
		table.insert(world.decor, decor(f.item, 1, f.x, f.z, f.r, tostring(10 + i)))
	end
	return world
end

describe("Built rooms in the game", function()
	it(
		"a new hotel's start room is ready, its walls each allowed, its guest's route open",
		function()
			local w = startHotel()
			local ok, missing = Rooms.ready(w, "2")
			expect.truthy(ok, `start room ready: {missing and table.concat(missing, ",") or ""}`)
			-- Every wall of it could have been drawn one by one.
			local bare = startHotel()
			bare.walls = {}
			bare.rooms = {}
			bare.decor = {}
			for e, rec in w.walls do
				local fine, why = Rooms.canWall(bare, e, rec.door)
				expect.truthy(fine, `{e}: {why}`)
				bare.walls[e] = rec
			end
			-- From the desk's queue to the bed.
			local desk = w.pieces[1]
			local from = Rooms.spotSquare(w, Grid.doors(desk)[1])
			local to = Rooms.keySpot(w, "2")
			expect.truthy(from and to, "spots")
			expect.truthy(Rooms.route(w, from, to), "a route from the desk to the bed")
			expect.truthy(Rooms.bars(w, "2").furniture > 0, "a bed counts toward Furniture")
		end
	)

	it("a desk or a stair never stands on a wall, nor cuts a room off", function()
		local w = startHotel()
		-- A second desk across the start room's wall: refused.
		local desk2 = placed("FrontDesk", 1, 6, 3, 0)
		local ok, why = Rooms.canPlacePiece(w, desk2)
		expect.truthy(not ok, "a desk inside the room")
		expect.truthy(why ~= nil, "with a reason")
		-- Taking the only desk away is never allowed.
		local ok2 = Rooms.canRemovePiece(w, w.pieces[1])
		expect.truthy(not ok2, "the last desk stays")
	end)

	it("a second desk guests reach may be sold again (its own queue is not cut off)", function()
		local w = startHotel()
		for z = 0, Constants.Grid.Cells - 1 do -- the whole floor bought, so there is room for it
			for x = 0, Constants.Grid.Cells - 1 do
				w.tiles[Grid.tileKey(1, x, z)] = true
			end
		end
		local second
		for z = 0, Constants.Grid.Cells - 1 do
			for x = 0, Constants.Grid.Cells - 1 do
				local d = placed("FrontDesk", 1, x, z, 0)
				if not second and Rooms.canPlacePiece(w, d) then
					second = d
				end
			end
		end
		expect.truthy(second ~= nil, "somewhere for a second desk")
		table.insert(w.pieces, second)
		local ok, why = Rooms.canRemovePiece(w, second)
		expect.truthy(ok, `sold: {tostring(why)}`)
	end)

	it("a half edge sent as -0 is the same half edge as 0", function()
		expect.eq(Rooms.edgeKey(1, -0, 3, 0), "1:0:3:0", "-0 normalised")
	end)

	it("decor stands on whole squares only", function()
		local w = startHotel()
		local ok, why = Rooms.canPlaceDecor(w, decor("Nightstand", 1, 4.5, 2, 0))
		expect.truthy(not ok, "half a square")
		expect.eq(why, "OutOfBounds", "why")
	end)

	it("decor never stands across a wall or in a doorway; a rug may", function()
		local w = startHotel()
		local S = Constants.Rooms.Start
		-- Across the room's front wall at x cells 5..6, z between cell rows 2 and 3.
		local across = decor("Nightstand", 1, 0, 0, 0)
		across = decor("WritingDesk", 1, 5 * Q, 3 * Q - 1, 1) -- 1 wide, 2 deep at r 1: z 11..12
		local ok, why = Rooms.canPlaceDecor(w, across)
		expect.truthy(not ok, "across a wall")
		expect.eq(why, "Across", "why")
		-- In the doorway, on the hallway side.
		local sx, sz = S.door.hx * (Q // HC), S.door.hz * (Q // HC) - 1
		local ok2, why2 = Rooms.canPlaceDecor(w, decor("Nightstand", 1, sx, sz, 0))
		expect.truthy(not ok2, "in a doorway")
		expect.eq(why2, "Doorway", "why")
		-- A rug may lie there.
		for _, d in Pieces.DecorList do
			if d.layer == "Rug" and d.w == 1 and d.d == 1 then
				expect.truthy(
					Rooms.canPlaceDecor(w, decor(d.id, 1, sx, sz, 0)),
					"a rug in a doorway"
				)
				break
			end
		end
		-- A nightstand inside the room, beside the bed: fine.
		expect.truthy(
			Rooms.canPlaceDecor(w, decor("Nightstand", 1, 16, 15, 0)),
			"a nightstand in the room"
		)
	end)

	it("a wall piece needs a wall or the facade behind it", function()
		local w = startHotel()
		local hung
		for _, d in Pieces.DecorList do
			if d.layer == "Wall" and d.location == 1 and d.w == 1 then
				hung = d
				break
			end
		end
		if not hung then
			return
		end
		-- r 0: front toward −z, back toward +z. Against the facade at the back of cell row 3.
		local back = decor(hung.id, 1, 6 * Q, 4 * Q - hung.d, 0)
		expect.truthy(Rooms.canPlaceDecor(w, back), "against the facade")
		-- In the open hallway (cell 4, 1): nothing behind it.
		local open = decor(hung.id, 1, 4 * Q + 1, 1 * Q + 1, 0)
		local ok, why = Rooms.canPlaceDecor(w, open)
		expect.truthy(not ok, "nothing behind")
		expect.eq(why, "NoWall", "why")
	end)

	it("a tile bought beside a room is walled off from it, so the room stays as it was", function()
		local w = startHotel()
		local before = Rooms.roomArea(w, "2").size
		-- Cell (3, 2) beside the room's (4, 2).
		local auto = Rooms.autoWalls(w, 1, 3, 2)
		expect.truthy(#auto == HC, "a whole cell edge of walls")
		local after = table.clone(w)
		after.tiles = table.clone(w.tiles)
		after.tiles[Grid.tileKey(1, 3, 2)] = true
		after.walls = table.clone(w.walls)
		for _, e in auto do
			after.walls[e] = { paid = 0 }
		end
		expect.truthy(Rooms.check(w, after), "allowed")
		expect.eq(Rooms.roomArea(after, "2").size, before, "the room unchanged")
		-- A tile beside the hallway only: no walls.
		expect.eq(#Rooms.autoWalls(w, 1, 8, 0), 0, "none beside a hallway")
	end)

	it("posts stand at corners and ends, never in the middle of a straight run", function()
		local walls = {}
		for _, e in Rooms.cellEdges(1, 2, 2, 0) do
			walls[e] = { paid = 0 }
		end
		for _, e in Rooms.cellEdges(1, 3, 2, 0) do
			walls[e] = { paid = 0 }
		end
		-- A straight run of four half edges: posts at its two ends only.
		local posts = Rooms.posts(walls)
		expect.eq(#posts, 2, "two ends")
		-- Turn a corner: the corner gets one.
		for _, e in Rooms.cellEdges(1, 2, 2, 1) do
			walls[e] = { paid = 0 }
		end
		local ends = 0
		for _, p in Rooms.posts(walls) do
			if p.vx == 2 * HC and p.vz == 2 * HC then
				ends += 1
			end
		end
		expect.eq(ends, 1, "a post at the corner")
	end)
end)
