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

-- A hotel as it starts (§5.4): the start area owned, the desk at the lobby's end.
local function world(floors, areas, pieces)
	local owned = {}
	for _, a in areas or { G.StartArea } do
		owned[a] = true
	end
	return {
		floors = floors or 1,
		areas = owned,
		pieces = pieces or { placed("FrontDesk", 1, 0, 0, 1) },
		decor = {},
	}
end

local function allAreas()
	local out = {}
	for i = 1, Grid.areaCount() do
		table.insert(out, i)
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

	it("the areas split everything behind the lobby, and only a neighbour can be bought", function()
		local seen = {}
		for z = 0, N - 1 do
			for x = 0, N - 1 do
				local a = Grid.areaOf(x, z)
				if Grid.isLobbyRow(z) then
					expect.eq(a, nil, `lobby row {x},{z} is no area`)
				else
					expect.truthy(a ~= nil, `cell {x},{z} has an area`)
					seen[a] = (seen[a] or 0) + 1
				end
			end
		end
		for i = 1, Grid.areaCount() do
			expect.eq(seen[i], G.AreaW * G.AreaD, `area {i}'s cells`)
			local x0, z0 = Grid.areaRect(i)
			expect.eq(Grid.areaOf(x0, z0), i, `area {i}'s corner`)
		end
		local start = { [G.StartArea] = true }
		expect.truthy(not Grid.canBuyArea(start, G.StartArea), "the start area is owned")
		for i = 1, Grid.areaCount() do
			local ok = Grid.canBuyArea(start, i)
			local _, z0 = Grid.areaRect(i)
			local x0 = Grid.areaRect(i)
			local sx0 = Grid.areaRect(G.StartArea)
			local besideStart = z0 > G.LobbyRows and x0 == sx0
			if i ~= G.StartArea then
				expect.eq(ok, z0 == G.LobbyRows or besideStart, `area {i} buyable from the start`)
			end
		end
	end)

	it("rooms stand only in owned areas, never in the lobby or on the entrance", function()
		local w = world()
		local x0, z0 = Grid.areaRect(G.StartArea)
		expect.truthy(
			Grid.canPlace(w, placed("StandardRoom", 1, x0, z0, 0)),
			"a room in the start area"
		)
		local _, why = Grid.canPlace(w, placed("StandardRoom", 1, 0, z0, 0))
		expect.eq(why, "Area", "a room in an area not owned")
		_, why = Grid.canPlace(w, placed("StandardRoom", 1, x0, 0, 2))
		expect.eq(why, "Lobby", "a room in the lobby")
		local e = Grid.entrance()[1]
		_, why = Grid.canPlace(w, placed("Stairs", 1, e.x, e.z, 2), nil)
		expect.truthy(why == "Entrance" or why == "NoFloorAbove", "nothing on the entrance")
		_, why = Grid.canPlace(world(2), placed("Stairs", 1, e.x, e.z, 2))
		expect.eq(why, "Entrance", "a stair on the entrance")
	end)

	it("a new hotel has room for two to four Standard Rooms", function()
		-- Greedy fill of the start area: every cell, every rotation.
		local w = world()
		local n = 0
		local x0, z0 = Grid.areaRect(G.StartArea)
		for z = z0, z0 + G.AreaD - 1 do
			for x = x0, x0 + G.AreaW - 1 do
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
		expect.atLeast(n, 2, "rooms in the start area")
		expect.atMost(n, 4, "rooms in the start area")
		expect.truthy(Grid.allServed(w), "every door served")
	end)

	it("there is exactly one desk, on floor 1, its queue reached from the entrance", function()
		local w = world(2)
		local desk = w.pieces[1]
		expect.truthy(Grid.allServed(w), "the start desk is served")
		local _, why = Grid.canPlace(w, placed("FrontDesk", 1, 9, 0, 3))
		expect.eq(why, "OneDesk", "a second desk")
		expect.truthy(Grid.canPlace(w, placed("FrontDesk", 1, 9, 0, 3), desk), "the desk moved")
		_, why = Grid.canPlace(w, placed("FrontDesk", 2, 9, 0, 3), desk)
		expect.eq(why, "DeskFloor", "the desk upstairs")
		_, why = Grid.canRemove(w, desk)
		expect.eq(why, "OneDesk", "the desk sold")
		-- Its queue cells against the front wall's edge: nowhere to stand.
		_, why = Grid.canPlace(w, placed("FrontDesk", 1, 2, 0, 0), desk)
		expect.eq(why, "DoorBlocked", "the desk served from outside the plot")
	end)

	it("a floor above is reached only by a stair, and its last stair cannot go", function()
		local w = world(2)
		local x0, z0 = Grid.areaRect(G.StartArea)
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
		-- In the lobby beyond the entrance, coming up into the gallery above it.
		local second = placed("Stairs", 1, x0 + 4, 0, 3)
		expect.truthy(Grid.canPlace(w, second), "a second stair in the lobby")
		table.insert(w.pieces, second)
		expect.truthy(Grid.canRemove(w, stair), "the first stair, once a second serves the floor")
		_, why = Grid.canPlace(w, placed("Stairs", 2, x0, z0, 0))
		expect.eq(why, "NoFloorAbove", "a stair from the top floor")
	end)

	it("a stair continues another only on the same cells and turn", function()
		local w = world(3, allAreas())
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
		local w = world(1, allAreas())
		local x0, z0 = Grid.areaRect(G.StartArea)
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
		expect.truthy(
			Grid.canPlaceDecor(w, decor("RugRunner", 1, mid - 2, 0, 1)),
			"a rug in the mouth"
		)
	end)

	it("hallway decor that would cut a door off is refused", function()
		local w = world()
		local x0, z0 = Grid.areaRect(G.StartArea)
		-- A room at the back of the start area, its door down a one-cell hallway.
		local room = placed("StandardRoom", 1, x0, z0 + 3, 0)
		table.insert(w.pieces, placed("StandardRoom", 1, x0 + 1, z0, 1))
		expect.truthy(Grid.canPlace(w, room), "the back room")
		table.insert(w.pieces, room)
		local door = Grid.doorCell(room)
		local _, why = Grid.canPlaceDecor(w, decor("Candles", 1, door.x * Q + 1, door.z * Q + 1, 0))
		expect.eq(why, "CutsOff", "candles on the door cell's middle")
	end)

	it("no accepted change ever cuts a door off, and every door has a route in", function()
		local rng = Random.new(7)
		local ids =
			{ "StandardRoom", "SarcophagusSuite", "DenRoom", "SnackBar", "Stairs", "Stairs" }
		local w = world(3, allAreas())
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
end)
