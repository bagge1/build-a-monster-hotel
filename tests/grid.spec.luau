local Grid = require(Shared.Grid)
local Constants = require(Shared.Constants)
local Pieces = require(Shared.Pieces)

local G = Constants.Grid
local N = G.Cells
local Q = G.Squares

local function placed(id, floor, x, z, r)
	local p = Pieces.get(id)
	return { item = id, kind = p.kind, floor = floor, x = x, z = z, r = r, w = p.w, d = p.d }
end

local function decor(id, floor, x, z, r)
	local d = Pieces.decor(id)
	return { item = id, layer = d.layer, floor = floor, x = x, z = z, r = r, w = d.w, d = d.d }
end

-- A hotel as it starts (§5.4, A.1): the start square's tiles (`tiles` on every
-- floor up to `floors`), the desk across from the arch.
local function world(floors, tiles, pieces)
	local owned = {}
	for f = 1, floors or 1 do
		for _, c in tiles or Grid.startTiles() do
			owned[Grid.tileKey(f, c.x, c.z)] = true
		end
	end
	local d = G.DeskStart
	return {
		floors = floors or 1,
		tiles = owned,
		pieces = pieces or { placed("FrontDesk", 1, d.x, d.z, d.r) },
		decor = {},
	}
end

local function allTiles()
	local out = {}
	for z = 0, N - 1 do
		for x = 0, N - 1 do
			table.insert(out, { x = x, z = z })
		end
	end
	return out
end

-- The start square and `extra` cells.
local function startPlus(extra)
	local out = Grid.startTiles()
	for _, c in extra do
		table.insert(out, c)
	end
	return out
end

-- Whether a straight-legged run of cells steps on a cell `bad` says is bad.
local function steps(cells, bad)
	for i = 2, #cells do
		local a, b = cells[i - 1], cells[i]
		local dx, dz = math.sign(b.x - a.x), math.sign(b.z - a.z)
		local x, z = a.x, a.z
		while true do
			if bad(x, z) then
				return true
			end
			if x == b.x and z == b.z then
				break
			end
			x += dx
			z += dz
		end
	end
	return false
end

describe("Grid", function()
	it("a door opens next to its own footprint, for every size and rotation", function()
		for _, size in { { 2, 2 }, { 2, 3 }, { 3, 3 } } do
			for r = 0, 3 do
				local p = { x = 4, z = 4, r = r, w = size[1], d = size[2] }
				local inside = Grid.doorInside(p)
				local outside = Grid.doorCell(p)
				local inFoot = false
				for _, c in Grid.cells(p) do
					if c.x == inside.x and c.z == inside.z then
						inFoot = true
					end
					expect.truthy(
						not (c.x == outside.x and c.z == outside.z),
						"door cell outside the footprint"
					)
				end
				expect.truthy(
					inFoot,
					`door's inner cell in the footprint ({size[1]}x{size[2]} r{r})`
				)
				expect.eq(
					math.abs(inside.x - outside.x) + math.abs(inside.z - outside.z),
					1,
					"adjacent"
				)
				local f = Grid.doorFacing(r)
				expect.eq(outside.x - inside.x, f.X, "facing x")
				expect.eq(outside.z - inside.z, f.Z, "facing z")
			end
		end
	end)

	it(
		"a new hotel owns the 4 × 4 square on the entrance, and only a neighbour tile can be bought",
		function()
			local w = world()
			local S = G.StartTiles
			local owned = 0
			for z = 0, N - 1 do
				for x = 0, N - 1 do
					local inSquare = x >= S.x and x < S.x + S.w and z >= S.z and z < S.z + S.d
					expect.eq(Grid.isOpen(w, 1, x, z), inSquare, `start tile {x},{z}`)
					if inSquare then
						owned += 1
					end
				end
			end
			expect.eq(owned, 16, "the start square's tiles")
			for _, c in Grid.entrance() do
				expect.truthy(Grid.isOpen(w, 1, c.x, c.z), "the mouth is owned")
			end
			for z = -1, N do
				for x = -1, N do
					local ok, why = Grid.canBuyTile(w.tiles, 1, 1, x, z)
					local beside = Grid.inBounds(x, z)
						and not Grid.isOpen(w, 1, x, z)
						and (
							Grid.isOpen(w, 1, x - 1, z)
							or Grid.isOpen(w, 1, x + 1, z)
							or Grid.isOpen(w, 1, x, z - 1)
							or Grid.isOpen(w, 1, x, z + 1)
						)
					expect.eq(ok, beside, `tile {x},{z} buyable`)
					if not Grid.inBounds(x, z) then
						expect.eq(why, "Unknown", "off the plot")
					elseif Grid.isOpen(w, 1, x, z) then
						expect.eq(why, "Owned", "owned")
					end
				end
			end
			expect.eq(
				#Grid.buyable(w.tiles, 1, 1),
				12,
				"the square's neighbours: 4 a side, none in front"
			)
			local _, why = Grid.canBuyTile(w.tiles, 1, 1, 0, 11)
			expect.eq(why, "NotNext", "a tile far from the hotel")
		end
	)

	it("tiles are bought on each floor apart, upstairs over owned tiles below", function()
		-- Floor 2 built, no tiles on it yet: no walls there either.
		local w = world(1)
		w.floors = 2
		local t = w.tiles
		for _, f in Grid.facade(t, 2) do
			expect.eq(f.floor, 1, "nothing drawn on a floor with no tiles")
		end
		local ok, why = Grid.canBuyTile(t, 2, 2, 4, 2)
		expect.truthy(ok, "a floor's first tile anywhere over an owned one")
		_, why = Grid.canBuyTile(t, 2, 2, 8, 2)
		expect.eq(why, "NoTileBelow", "not over a tile not owned")
		_, why = Grid.canBuyTile(t, 2, 3, 4, 2)
		expect.eq(why, "NoFloor", "not on a floor not built")
		expect.eq(#Grid.buyable(t, 2, 2), 16, "any of the 16 below")
		t[Grid.tileKey(2, 4, 2)] = true
		_, why = Grid.canBuyTile(t, 2, 2, 7, 3)
		expect.eq(why, "NotNext", "then only next to its floor's own")
		expect.truthy(Grid.canBuyTile(t, 2, 2, 5, 2), "beside it")
		expect.eq(#Grid.buyable(t, 2, 2), 3, "the three over owned tiles beside it")
		expect.truthy(Grid.canBuyTile(t, 2, 1, 8, 2), "floor 1 still buys on its own")
		-- A stair needs the tiles above its well.
		local open = world(1)
		open.floors = 2
		open.pieces = {}
		_, why = Grid.canPlace(open, placed("Stairs", 1, 6, 2, 0))
		expect.eq(why, "TileAbove", "no tiles above it")
		local free = world(1)
		free.floors = 2
		free.pieces = {}
		for _, c in Grid.startTiles() do
			free.tiles[Grid.tileKey(2, c.x, c.z)] = true
		end
		expect.truthy(Grid.canPlace(free, placed("Stairs", 1, 6, 2, 0)), "with the tiles above it")
	end)

	it(
		"anything stands on any owned tile, never on a tile not owned or the entrance's mouth",
		function()
			local w = world(
				1,
				startPlus({ { x = 8, z = 0 }, { x = 9, z = 0 }, { x = 8, z = 1 }, { x = 9, z = 1 } })
			)
			expect.truthy(
				Grid.canPlace(w, placed("StandardRoom", 1, 4, 2, 0)),
				"a room in the start square"
			)
			expect.truthy(
				Grid.canPlace(w, placed("StandardRoom", 1, 8, 0, 3)),
				"a room on the front row, where the lobby strip was"
			)
			local _, why = Grid.canPlace(w, placed("StandardRoom", 1, 0, 5, 0))
			expect.eq(why, "Tile", "a room on tiles not owned")
			_, why = Grid.canPlace(w, placed("StandardRoom", 1, 9, 0, 3))
			expect.eq(why, "Tile", "a room half on a tile not owned")
			local e = Grid.entrance()[1]
			_, why = Grid.canPlace(world(2), placed("Stairs", 1, e.x, e.z, 2))
			expect.eq(why, "Entrance", "a stair on the entrance's mouth")
			_, why = Grid.canPlace(w, placed("StandardRoom", 1, e.x, e.z, 2))
			expect.eq(why, "Entrance", "a room on the entrance's mouth")
		end
	)

	it("a new hotel fits the desk across from the arch and a Standard Room", function()
		-- Greedy fill of the start square: every cell, every rotation.
		local w = world()
		local desk = w.pieces[1]
		for _, s in Grid.doors(desk) do
			expect.eq(s.z, 0, "the desk's queue stands in the entrance's mouth")
			expect.truthy(s.x == 5 or s.x == 6, "the desk's queue stands in the entrance's mouth")
		end
		expect.eq(Grid.doorFacing(desk.r).Z, -1, "the desk is served toward the street")
		local n = 0
		local S = G.StartTiles
		for z = S.z, S.z + S.d - 1 do
			for x = S.x, S.x + S.w - 1 do
				for r = 0, 3 do
					local p = placed("StandardRoom", 1, x, z, r)
					if Grid.canPlace(w, p) then
						table.insert(w.pieces, p)
						n += 1
						break
					end
				end
			end
		end
		expect.atLeast(n, 1, "rooms in the start square")
		expect.truthy(Grid.allServed(w), "every door served")
	end)

	it("one or more desks on floor 1, each queue reached; the last cannot go", function()
		local w = world(2)
		local desk = w.pieces[1]
		expect.truthy(Grid.allServed(w), "the start desk is served")
		local second = placed("FrontDesk", 1, 4, 2, 1)
		expect.truthy(Grid.canPlace(w, second), "a second desk")
		table.insert(w.pieces, second)
		expect.truthy(Grid.allServed(w), "both desks served")
		expect.truthy(Grid.canRemove(w, desk), "one of two desks sold")
		table.remove(w.pieces, 1)
		local _, why = Grid.canRemove(w, second)
		expect.eq(why, "LastDesk", "the last desk sold")
		expect.truthy(Grid.canPlace(w, placed("FrontDesk", 1, 6, 2, 3), second), "the desk moved")
		_, why = Grid.canPlace(w, placed("FrontDesk", 2, 4, 2, 1), second)
		expect.eq(why, "DeskFloor", "a desk upstairs")
		-- Its queue cells off the plot's front edge: nowhere to stand.
		local all = world(1, allTiles())
		_, why = Grid.canPlace(all, placed("FrontDesk", 1, 2, 0, 0))
		expect.eq(why, "DoorBlocked", "a desk served from outside the plot")
	end)

	it(
		"windows go on outer walls only, and move out along their line when a tile is bought",
		function()
			local w = world(2)
			local t = w.tiles
			expect.truthy(Grid.isWall(t, 2, 1, 4, 0, 0), "the front wall beside the arch")
			expect.truthy(not Grid.isWall(t, 2, 1, 5, 0, 0), "not the arch")
			expect.truthy(Grid.isWall(t, 2, 2, 4, 0, 0), "the street side upstairs is walled too")
			expect.truthy(Grid.isWall(t, 2, 2, 5, 0, 0), "and over the arch")
			expect.truthy(Grid.isWall(t, 2, 2, 4, 1, 1), "a side wall upstairs")
			expect.truthy(not Grid.isWall(t, 2, 1, 5, 1, 1), "not between two owned tiles")
			expect.truthy(not Grid.isWall(t, 2, 3, 4, 1, 1), "not on a floor not built")
			for _, s in Constants.Windows.Start do
				expect.truthy(
					Grid.isWall(t, 1, s.floor, s.x, s.z, s.side),
					"a start window on a wall"
				)
			end
			local windows = {
				[Grid.edgeKey(1, 7, 1, 3)] = "Round",
				[Grid.edgeKey(2, 7, 1, 3)] = "Wide",
				[Grid.edgeKey(1, 7, 2, 3)] = "Arched",
				[Grid.edgeKey(1, 6, 3, 2)] = "TwinSash",
				[Grid.edgeKey(1, 4, 0, 0)] = "TwinSash",
			}
			local owned = world(2, startPlus({ { x = 8, z = 1 }, { x = 6, z = 4 } })).tiles
			local moved, refunded = Grid.moveWindows(owned, 2, windows)
			expect.eq(#refunded, 0, "nothing refunded")
			expect.eq(moved[Grid.edgeKey(1, 8, 1, 3)], "Round", "out along its line, floor 1")
			expect.eq(moved[Grid.edgeKey(2, 8, 1, 3)], "Wide", "out along its line, floor 2")
			expect.eq(moved[Grid.edgeKey(1, 6, 4, 2)], "TwinSash", "the back one moved back")
			expect.eq(
				moved[Grid.edgeKey(1, 7, 2, 3)],
				"Arched",
				"a wall still a wall keeps its window"
			)
			expect.eq(moved[Grid.edgeKey(1, 4, 0, 0)], "TwinSash", "the front one stays")
			expect.eq(moved[Grid.edgeKey(1, 7, 1, 3)], nil, "nothing left inside")
			-- Onto a wall that has a window already: refunded.
			local crowded =
				{ [Grid.edgeKey(1, 7, 1, 3)] = "Round", [Grid.edgeKey(1, 8, 1, 3)] = "Wide" }
			moved, refunded = Grid.moveWindows(owned, 2, crowded)
			expect.eq(#refunded, 1, "one refunded")
			expect.eq(refunded[1].window, "Round", "the one that moved")
			expect.eq(moved[Grid.edgeKey(1, 8, 1, 3)], "Wide", "the outer one kept")
			-- The facade draws a window where one is placed.
			local found = 0
			for _, f in Grid.facade(owned, 2, moved) do
				if f.window then
					found += 1
					expect.eq(f.kind, "Wall", "a window is on a wall")
					expect.eq(
						moved[Grid.edgeKey(f.floor, f.x, f.z, f.side)],
						f.window,
						"its own window"
					)
				end
			end
			expect.eq(found, 1, "one window drawn")
		end
	)

	it(
		"the facade walls exactly each floor's outline of owned tiles, the street side too",
		function()
			local function check(tiles, floors)
				local owned = {}
				for f = 1, floors do
					for _, c in tiles do
						owned[Grid.tileKey(f, c.x, c.z)] = true
					end
				end
				local function isOwned(x, z)
					return Grid.inBounds(x, z) and owned[Grid.tileKey(1, x, z)] == true
				end
				local walls, corners, entrances = {}, {}, 0
				for _, f in Grid.facade(owned, floors) do
					local key = `{f.floor}:{f.at.X},{f.at.Z}`
					if f.kind == "Wall" then
						expect.eq(walls[key], nil, `one wall at {key}`)
						walls[key] = f
					elseif f.kind == "Corner" then
						corners[key] = (corners[key] or 0) + 1
					else
						entrances += 1
						expect.eq(f.floor, 1, "the arch on floor 1")
						expect.eq(f.at.X, 6 * G.CellSize, "the arch over the mouth")
						expect.eq(f.at.Z, 0, "the arch on the front edge")
					end
				end
				expect.eq(entrances, 1, "one arch")
				local C = G.CellSize
				local wanted = 0
				for floor = 1, floors do
					for _, c in tiles do
						for _, side in { { 0, -1, 0 }, { -1, 0, 1 }, { 0, 1, 2 }, { 1, 0, 3 } } do
							local nx, nz = c.x + side[1], c.z + side[2]
							local key =
								`{floor}:{(c.x + 0.5 + side[1] / 2) * C},{(c.z + 0.5 + side[2] / 2) * C}`
							local edge = not isOwned(nx, nz)
							local arch = floor == 1 and nz < 0 and (c.x == 5 or c.x == 6)
							if edge and not arch then
								wanted += 1
								local w = walls[key]
								expect.truthy(w ~= nil, `a wall at {key}`)
								expect.eq(w and w.turn, side[3], `the wall at {key} faces out`)
							else
								expect.eq(walls[key], nil, `no wall at {key}`)
							end
						end
					end
				end
				local count = 0
				for _ in walls do
					count += 1
				end
				expect.eq(count, wanted, "walls")
				return count, corners
			end
			local count, corners = check(Grid.startTiles(), 2)
			expect.eq(
				count,
				14 + 16,
				"the start square: 14 walls and the arch on floor 1, 16 above (the street side walled)"
			)
			local posts = 0
			for _, n in corners do
				posts += n
			end
			expect.eq(posts, 8, "a post at each of the square's corners on both floors")
			-- A tile bought beside the square: two concave corners and two convex ones more.
			count, corners = check(startPlus({ { x = 8, z = 1 } }), 1)
			expect.eq(count, 16, "the outline moved out")
			posts = 0
			for _, n in corners do
				posts += n
			end
			expect.eq(
				posts,
				8,
				"four corners of the square, two concave and two convex at the new tile"
			)
		end
	)

	it("a floor above is reached only by a stair, and its last stair cannot go", function()
		local w = world(2, allTiles())
		local x0, z0 = 4, 2
		local up = placed("StandardRoom", 2, x0, z0 + 1, 0)
		local _, why = Grid.canPlace(w, up)
		expect.eq(why, "DoorUnreachable", "a room upstairs with no stair")
		local stair = placed("Stairs", 1, x0 + 2, z0 + 3, 0)
		expect.truthy(Grid.canPlace(w, stair), "a stair in the start area")
		table.insert(w.pieces, stair)
		-- Its well: nothing upstairs on its cells; its head walkable.
		_, why = Grid.canPlace(w, placed("StandardRoom", 2, x0 + 2, z0 + 3, 0))
		expect.eq(why, "Overlap", "a room on the stairwell")
		expect.truthy(not Grid.walkable(w, 2, x0 + 2, z0 + 3), "the well is no hallway")
		local head = Grid.stairHead(stair)
		expect.eq(head.floor, 2, "the head is upstairs")
		expect.truthy(Grid.walkable(w, 2, head.x, head.z), "the head is a hallway")
		up = placed("StandardRoom", 2, x0, z0, 0)
		expect.truthy(Grid.canPlace(w, up), "a room upstairs by the stair")
		table.insert(w.pieces, up)
		_, why = Grid.canRemove(w, stair)
		expect.eq(why, "CutsOff", "the last stair to a floor with rooms")
		-- On the front row beside the entrance.
		local second = placed("Stairs", 1, x0 + 4, 0, 3)
		expect.truthy(Grid.canPlace(w, second), "a second stair on the front row")
		table.insert(w.pieces, second)
		expect.truthy(Grid.canRemove(w, stair), "the first stair, once a second serves the floor")
		_, why = Grid.canPlace(w, placed("Stairs", 2, x0, z0, 0))
		expect.eq(why, "NoFloorAbove", "a stair from the top floor")
	end)

	it("a stair continues another only on the same cells and turn", function()
		local w = world(3, allTiles())
		local s1 = placed("Stairs", 1, 4, 4, 0)
		expect.truthy(Grid.canPlace(w, s1), "the first storey")
		table.insert(w.pieces, s1)
		expect.truthy(Grid.canPlace(w, placed("Stairs", 2, 4, 4, 0)), "stacked on it")
		local _, why = Grid.canPlace(w, placed("Stairs", 2, 4, 4, 2))
		expect.eq(why, "Overlap", "turned on its well")
		_, why = Grid.canPlace(w, placed("Stairs", 2, 5, 4, 0))
		expect.eq(why, "Overlap", "half on its well")
	end)

	it("hallway decor in a cell's corner leaves it walkable; in its middle it takes it", function()
		local w = world(1, allTiles())
		local x0, z0 = 4, 4
		local corner = decor("Candles", 1, x0 * Q, z0 * Q, 0)
		expect.truthy(Grid.canPlaceDecor(w, corner), "candles in a corner")
		table.insert(w.decor, corner)
		expect.truthy(Grid.walkable(w, 1, x0, z0), "the cell stays a hallway")
		local middle = decor("Candles", 1, (x0 + 1) * Q + 1, z0 * Q + 1, 0)
		expect.truthy(Grid.canPlaceDecor(w, middle), "candles in the middle")
		table.insert(w.decor, middle)
		expect.truthy(not Grid.walkable(w, 1, x0 + 1, z0), "the cell is taken")
		local rug = decor("RugSquare", 1, (x0 + 2) * Q, z0 * Q, 0)
		expect.truthy(Grid.canPlaceDecor(w, rug), "a rug")
		table.insert(w.decor, rug)
		expect.truthy(Grid.walkable(w, 1, x0 + 2, z0), "a rug takes nothing")
		local _, why = Grid.canPlaceDecor(w, decor("Candles", 1, x0 * Q, z0 * Q, 0))
		expect.eq(why, "Overlap", "two pieces on one square")
		expect.truthy(
			Grid.canPlaceDecor(w, decor("Candles", 1, (x0 + 2) * Q + 1, z0 * Q + 1, 0)),
			"on a rug"
		)
		_, why = Grid.canPlace(w, placed("StandardRoom", 1, x0 + 1, z0, 0))
		expect.eq(why, "Decor", "a room over hallway decor")
		_, why = Grid.canPlaceDecor(w, decor("BlackoutCurtains", 1, x0 * Q, (z0 + 2) * Q, 0))
		expect.eq(why, "Wall", "wall decor needs a room's wall")
		local mid = (N // 2) * Q
		_, why = Grid.canPlaceDecor(w, decor("Candles", 1, mid - 1, 0, 0))
		expect.eq(why, "Entrance", "nothing in the entrance's mouth")
		_, why = Grid.canPlaceDecor(w, decor("Candles", 1, mid + Q - 1, Q - 1, 0))
		expect.eq(why, "Entrance", "nothing anywhere in the mouth's two cells")
		expect.truthy(
			Grid.canPlaceDecor(w, decor("RugRunner", 1, mid - 2, 0, 1)),
			"a rug in the mouth"
		)
	end)

	it("hallway decor that would cut a door off is refused", function()
		local w = world()
		-- A room in the start square, its door onto the cell beside the mouth.
		local room = placed("StandardRoom", 1, 4, 2, 0)
		expect.truthy(Grid.canPlace(w, room), "the room")
		table.insert(w.pieces, room)
		local door = Grid.doorCell(room)
		local _, why = Grid.canPlaceDecor(w, decor("Candles", 1, door.x * Q + 1, door.z * Q + 1, 0))
		expect.eq(why, "CutsOff", "candles on the door cell's middle")
	end)

	it("no accepted change ever cuts a door off, and every door has a route in", function()
		local rng = Random.new(7)
		local ids =
			{ "StandardRoom", "SarcophagusSuite", "DenRoom", "SnackBar", "Stairs", "Stairs" }
		local w = world(3, allTiles())
		local desk = w.pieces[1]
		for _ = 1, 900 do
			local p = placed(
				ids[rng:NextInteger(1, #ids)],
				rng:NextInteger(1, 3),
				rng:NextInteger(0, N - 1),
				rng:NextInteger(0, N - 1),
				rng:NextInteger(0, 3)
			)
			if Grid.canPlace(w, p) then
				table.insert(w.pieces, p)
			end
			if rng:NextInteger(1, 25) == 1 then
				local victim = w.pieces[rng:NextInteger(1, #w.pieces)]
				if Grid.canRemove(w, victim) then
					table.remove(w.pieces, table.find(w.pieces, victim))
				end
			end
			if rng:NextInteger(1, 12) == 1 then
				local d = decor(
					"AntiqueWardrobe",
					rng:NextInteger(1, 3),
					rng:NextInteger(0, N * Q - 1),
					rng:NextInteger(0, N * Q - 1),
					rng:NextInteger(0, 3)
				)
				if Grid.canPlaceDecor(w, d) then
					table.insert(w.decor, d)
				end
			end
		end
		expect.truthy(Grid.allServed(w), "every door served after the run")
		local rooms, upstairs = 0, 0
		local q = Grid.doors(desk)[1]
		for _, p in w.pieces do
			if p.kind == "Room" or p.kind == "Amenity" then
				rooms += 1
				local door = Grid.doorCell(p)
				local legs = Grid.route(w, q, { floor = p.floor, x = door.x, z = door.z })
				expect.truthy(legs ~= nil, `a route to {p.item} at {p.floor}:{p.x},{p.z}`)
				local floorNow, climbs = 1, 0
				for _, leg in legs or {} do
					if leg.stair then
						expect.eq(
							leg.stair.floor,
							if leg.up then floorNow else floorNow - 1,
							"a stair from here"
						)
						floorNow += if leg.up then 1 else -1
						climbs += 1
					else
						expect.eq(leg.floor, floorNow, "a leg on the floor reached")
						local cells = leg.cells :: { any }
						for i = 2, #cells do
							expect.truthy(
								cells[i - 1].x == cells[i].x or cells[i - 1].z == cells[i].z,
								"straight legs"
							)
						end
						expect.truthy(not steps(cells, function(x, z)
							return not Grid.walkable(w, floorNow, x, z)
						end), "legs keep to hallways")
					end
				end
				expect.eq(floorNow, p.floor, "the route ends on the room's floor")
				if p.floor > 1 then
					upstairs += 1
					expect.atLeast(climbs, p.floor - 1, "stairs climbed")
				end
			end
		end
		expect.atLeast(rooms, 6, "rooms placed")
		expect.atLeast(upstairs, 1, "rooms upstairs")
	end)

	it("an edge a client names has one key, or none", function()
		-- 2026-10-26 night: "01:4:0:0" bought a second window on the section "1:4:0:0".
		local key = Grid.edgeKey(1, 4, 0, 0)
		for _, sent in { "1:4:0:0", "01:4:0:0", "1:4.0:0:0", "1:4:-0:0" } do
			expect.eq(Grid.canonicalEdge(sent), key, sent)
		end
		for _, sent in { "1:4:0", "1:4.5:0:0", "a:4:0:0", "1:4:0:0:0", "" } do
			expect.eq(Grid.canonicalEdge(sent), nil, sent)
		end
	end)
end)
