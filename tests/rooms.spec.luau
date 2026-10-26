local Rooms = require(Shared.Rooms)
local Grid = require(Shared.Grid)
local Constants = require(Shared.Constants)
local Pieces = require(Shared.Pieces)
local Species = require(Shared.Species)
local Visits = require(Shared.Visits)

local G = Constants.Grid
local N = G.Cells
local Q = G.Squares
local HC = Rooms.HalfCells
local SQ = Q // HC

local function placed(id, floor, x, z, r)
	local p = Pieces.get(id)
	return { item = id, kind = p.kind, floor = floor, x = x, z = z, r = r, w = p.w, d = p.d }
end

local function decor(id, floor, x, z, r)
	local d = Pieces.decor(id)
	return { item = id, layer = d.layer, floor = floor, x = x, z = z, r = r, w = d.w, d = d.d }
end

-- A hotel owning every tile of `floors` floors, the desk across from the arch.
local function world(floors, pieces)
	local owned = {}
	for f = 1, floors or 1 do
		for z = 0, N - 1 do
			for x = 0, N - 1 do
				owned[Grid.tileKey(f, x, z)] = true
			end
		end
	end
	local d = G.DeskStart
	return {
		floors = floors or 1,
		tiles = owned,
		pieces = pieces or { placed("FrontDesk", 1, d.x, d.z, d.r) },
		decor = {},
		walls = {},
		rooms = {},
	}
end

-- Two floors, the desk, and a stair from floor 1 at cells (1..2, 6..7): its foot (1, 5), its head (2, 5) upstairs.
local function stairWorld()
	return world(
		2,
		{ placed("FrontDesk", 1, G.DeskStart.x, G.DeskStart.z, 0), placed("Stairs", 1, 1, 6, 0) }
	)
end

-- A wall put up only if the rules allow it.
local function wall(w, e, door)
	local ok, why = Rooms.canWall(w, e, door)
	expect.truthy(ok, `wall {e}: {why}`)
	w.walls[e] = { door = door or nil, paid = 0 }
end

-- Walls round the w × d cells at (x, z) on `floor`, with a door in the first half
-- edge of its front when `door`; returns that half edge.
local function box(wd, floor, x, z, w, d, door)
	local doorEdge = Rooms.cellEdges(floor, x, z, 0)[1]
	for cx = x, x + w - 1 do
		for _, e in Rooms.cellEdges(floor, cx, z, 0) do
			wall(wd, e, door and e == doorEdge)
		end
		for _, e in Rooms.cellEdges(floor, cx, z + d - 1, 2) do
			wall(wd, e)
		end
	end
	for cz = z, z + d - 1 do
		for _, e in Rooms.cellEdges(floor, x, cz, 1) do
			wall(wd, e)
		end
		for _, e in Rooms.cellEdges(floor, x + w - 1, cz, 3) do
			wall(wd, e)
		end
	end
	return doorEdge
end

-- A room of `type` in a box at (x, z), seeded at its first half cell.
local function room(wd, id, type, x, z, w, d)
	local doorEdge = box(wd, 1, x, z, w, d, true)
	local ok, why = Rooms.canMakeRoom(wd, 1, x * HC, z * HC, type)
	expect.truthy(ok, `room {id}: {why}`)
	wd.rooms[id] = { type = type, floor = 1, hx = x * HC, hz = z * HC }
	return doorEdge
end

-- Every square a route steps on, its turns filled in, per floor leg.
local function stepsOf(legs)
	local out = {}
	for _, leg in legs do
		if leg.cells then
			local run = { floor = leg.floor, squares = { leg.cells[1] } }
			for i = 2, #leg.cells do
				local a, b = leg.cells[i - 1], leg.cells[i]
				local dx, dz = math.sign(b.x - a.x), math.sign(b.z - a.z)
				local x, z = a.x, a.z
				while x ~= b.x or z ~= b.z do
					x += dx
					z += dz
					table.insert(run.squares, { x = x, z = z })
				end
			end
			table.insert(out, run)
		end
	end
	return out
end

-- The half edge a step of one square crosses, or nil inside one half cell.
local function crossed(floor, a, b)
	local ax, az, bx, bz = a.x // SQ, a.z // SQ, b.x // SQ, b.z // SQ
	if ax == bx and az == bz then
		return nil
	end
	if ax ~= bx then
		return Rooms.edgeKey(floor, math.max(ax, bx), az, 1)
	end
	return Rooms.edgeKey(floor, ax, math.max(az, bz), 0)
end

local function entranceSquare()
	local c = Grid.entrance()[1]
	return { floor = 1, x = c.x * Q + 1, z = c.z * Q + 1 }
end

local function bedIn(wd, x, z)
	-- A Bed (a Standard Room's key piece) in the middle of the cell (x, z)'s box.
	table.insert(wd.decor, decor("Bed", 1, x * Q + 1, z * Q + 1, 0))
end

-- Non-furniture floor decor of the location, small enough to set down anywhere.
local function smallDecor()
	local out = {}
	for _, d in Pieces.DecorList do
		if not d.furniture and d.layer == "Floor" and d.w == 1 and d.d == 1 and d.cost > 0 then
			table.insert(out, d.id)
		end
	end
	return out
end

describe("Rooms", function()
	it("an edge key reads back, and a cell edge is two distinct half edges", function()
		local e = Rooms.edgeKey(2, 7, 9, 1)
		local f, hx, hz, o = Rooms.edgeOf(e)
		expect.eq(f, 2)
		expect.eq(hx, 7)
		expect.eq(hz, 9)
		expect.eq(o, 1)
		for side = 0, 3 do
			local es = Rooms.cellEdges(1, 3, 4, side)
			expect.eq(#es, HC, "half edges to a cell edge")
			expect.truthy(es[1] ~= es[2], "distinct")
		end
		-- A cell's front is its front neighbour's back.
		expect.eq(Rooms.cellEdges(1, 3, 4, 0)[1], Rooms.cellEdges(1, 3, 3, 2)[1])
		expect.eq(Rooms.cellEdges(1, 3, 4, 1)[1], Rooms.cellEdges(1, 2, 4, 3)[1])
	end)

	it(
		"a closed 2×2 box with one door is an area that is not hallway, and may be a room",
		function()
			local wd = world()
			local doorEdge = box(wd, 1, 8, 4, 2, 2, true)
			local a = Rooms.areaAt(wd, 1, 8 * HC, 4 * HC)
			expect.truthy(a, "area")
			expect.truthy(not a.hallway, "not hallway")
			expect.eq(a.size, 4, "cells")
			expect.eq(#a.doors, 1, "doors")
			expect.eq(a.doors[1], doorEdge)
			expect.truthy(Rooms.canMakeRoom(wd, 1, 8 * HC, 4 * HC, "StandardRoom"), "may be a room")
		end
	)

	it("without a door it cannot be a room", function()
		local wd = world()
		box(wd, 1, 8, 4, 2, 2, false)
		local a = Rooms.areaAt(wd, 1, 8 * HC, 4 * HC)
		expect.truthy(not a.hallway, "not hallway")
		expect.eq(#a.doors, 0)
		local ok, why = Rooms.canMakeRoom(wd, 1, 8 * HC, 4 * HC, "StandardRoom")
		expect.truthy(not ok, "refused")
		expect.eq(why, "NoDoor")
	end)

	it(
		"the area holding the entrance, a desk, a stair or its well is hallway and never a room",
		function()
			local wd = stairWorld()
			local mouth = Grid.entrance()[1]
			local d = G.DeskStart
			expect.truthy(Rooms.areaAt(wd, 1, mouth.x * HC, mouth.z * HC).hallway, "mouth")
			expect.truthy(Rooms.areaAt(wd, 1, d.x * HC, d.z * HC).hallway, "desk")
			expect.truthy(Rooms.areaAt(wd, 1, 1 * HC, 6 * HC).hallway, "stair")
			expect.truthy(Rooms.areaAt(wd, 2, 1 * HC, 6 * HC).hallway, "well")
			local ok, why = Rooms.canMakeRoom(wd, 1, mouth.x * HC, 0, "StandardRoom")
			expect.truthy(not ok)
			expect.eq(why, "Hallway")
		end
	)

	it("a wall stands only inside the hotel, off the mouth and stairs, and once", function()
		local wd = stairWorld()
		-- Unowned on floor 2 at its back row: a wall on floor 2 there is outside.
		for x = 0, N - 1 do
			wd.tiles[Grid.tileKey(2, x, N - 1)] = nil
		end
		local function refused(e, wanted)
			local ok, why = Rooms.canWall(wd, e)
			expect.truthy(not ok, `{e} refused`)
			expect.eq(why, wanted, e)
		end
		refused(Rooms.cellEdges(1, 0, 0, 1)[1], "NotInside") -- the plot's edge: the facade
		refused(Rooms.cellEdges(2, 3, N - 2, 2)[1], "NotInside") -- against an unowned tile
		local mouth = Grid.entrance()[1]
		refused(Rooms.cellEdges(1, mouth.x, mouth.z, 2)[1], "Mouth")
		refused(Rooms.cellEdges(1, 1, 6, 0)[1], "Stair") -- the stair's own front
		refused(Rooms.cellEdges(2, 1, 6, 1)[1], "Stair") -- beside its well
		refused(Rooms.edgeKey(9, 4, 4, 0), "NoFloor")
		local e = Rooms.cellEdges(1, 9, 9, 0)[1]
		wall(wd, e)
		refused(e, "Exists")
		local ok, why = Rooms.canRemoveWall(wd, Rooms.cellEdges(1, 9, 9, 1)[1])
		expect.truthy(not ok)
		expect.eq(why, "NoWall")
		ok, why = Rooms.canDoor(wd, Rooms.cellEdges(1, 9, 9, 1)[1], true)
		expect.truthy(not ok)
		expect.eq(why, "NoWall")
		expect.truthy(Rooms.canDoor(wd, e, true), "a door in a wall")
		expect.truthy(Rooms.canRemoveWall(wd, e), "a wall comes down")
	end)

	it("a wall never stands through furniture", function()
		local wd = world()
		bedIn(wd, 8, 4) -- squares 33..34 × 17..19: across the half edge at hx 17
		local ok, why = Rooms.canWall(wd, Rooms.edgeKey(1, 17, 9, 1))
		expect.truthy(not ok)
		expect.eq(why, "Decor")
	end)

	it("a change that would merge two rooms, or open one onto the hallway, is refused", function()
		local wd = world()
		room(wd, "a", "StandardRoom", 8, 4, 2, 2)
		-- Its neighbour shares its +x wall (already standing).
		local doorB = Rooms.cellEdges(1, 10, 4, 0)[1]
		for cx = 10, 11 do
			for _, e in Rooms.cellEdges(1, cx, 4, 0) do
				wall(wd, e, e == doorB)
			end
			for _, e in Rooms.cellEdges(1, cx, 5, 2) do
				wall(wd, e)
			end
		end
		-- Its +x side is the facade (cell 11 is the plot's last).
		expect.truthy(Rooms.canMakeRoom(wd, 1, 10 * HC, 4 * HC, "StandardRoom"), "room b")
		wd.rooms.b = { type = "StandardRoom", floor = 1, hx = 10 * HC, hz = 4 * HC }
		local shared = Rooms.cellEdges(1, 9, 4, 3)[1]
		local ok, why = Rooms.canRemoveWall(wd, shared)
		expect.truthy(not ok)
		expect.eq(why, "MergesRooms")
		-- A door between them keeps them apart: allowed.
		expect.truthy(Rooms.canDoor(wd, shared, true), "a door between rooms")
		-- Its front wall down: the room joins the hallway holding the desk.
		ok, why = Rooms.canRemoveWall(wd, Rooms.cellEdges(1, 8, 4, 0)[2])
		expect.truthy(not ok)
		expect.eq(why, "RoomTaken")
		-- Walling up its last door is allowed: the room is kept, not ready.
		expect.truthy(Rooms.canDoor(wd, Rooms.cellEdges(1, 8, 4, 0)[1], false), "last door walled")
	end)

	it("a wall never cuts a stair off from the entrance, but a door in it may stand", function()
		local wd = stairWorld()
		-- A line across the floor between cell rows 2 and 3: the stair's foot (row 5) beyond it.
		local H = N * HC
		for hx = 0, H - 2 do
			wall(wd, Rooms.edgeKey(1, hx, 3 * HC, 0))
		end
		local last = Rooms.edgeKey(1, H - 1, 3 * HC, 0)
		local ok, why = Rooms.canWall(wd, last)
		expect.truthy(not ok)
		expect.eq(why, "CutsOff")
		expect.truthy(Rooms.canWall(wd, last, true), "with a door")
		wall(wd, last, true)
		ok, why = Rooms.canDoor(wd, last, false)
		expect.truthy(not ok)
		expect.eq(why, "CutsOff")
	end)

	it("areas never overlap and cover every owned half cell of a floor", function()
		local rng = Random.new(7)
		for trial = 1, 4 do
			local wd = world()
			-- Some tiles not owned, so the floor is not square.
			for _ = 1, 10 do
				local x, z = rng:NextInteger(0, N - 1), rng:NextInteger(4, N - 1)
				if x < 7 or x > 10 or z < 5 or z > 8 then
					wd.tiles[Grid.tileKey(1, x, z)] = nil
				end
			end
			room(wd, "r", "StandardRoom", 8, 6, 2, 2)
			local H = N * HC
			for _ = 1, 120 do
				local e = Rooms.edgeKey(
					1,
					rng:NextInteger(0, H),
					rng:NextInteger(0, H),
					rng:NextInteger(0, 1)
				)
				if Rooms.canWall(wd, e) then
					wd.walls[e] =
						{ paid = 0, door = if rng:NextInteger(0, 3) == 0 then true else nil }
				end
			end
			local seen, total = {}, 0
			for _, a in Rooms.areas(wd, 1) do
				expect.eq(a.size, #a.cells / (HC * HC), "size in cells")
				for _, k in a.cells do
					expect.truthy(not seen[k], `trial {trial}: half cell {k} in two areas`)
					seen[k] = true
					total += 1
				end
			end
			local owned = 0
			for hz = 0, H - 1 do
				for hx = 0, H - 1 do
					if Grid.isOpen(wd, 1, hx // HC, hz // HC) then
						owned += 1
						expect.truthy(seen[Rooms.halfKey(hx, hz)], `half cell {hx},{hz} in an area`)
					end
				end
			end
			expect.eq(total, owned, "covered")
			-- The room kept its own area, never hallway, never shared.
			local a = Rooms.roomArea(wd, "r")
			expect.truthy(a and not a.hallway and #a.rooms == 1, "room intact")
		end
	end)

	it(
		"a room is ready with its key furniture, its size and a door, and says what it lacks",
		function()
			local wd = world()
			local doorEdge = room(wd, "r", "StandardRoom", 8, 4, 2, 2)
			local ok, missing = Rooms.ready(wd, "r")
			expect.truthy(not ok)
			expect.truthy(table.find(missing, "KeyFurniture"), "lacks its key furniture")
			bedIn(wd, 8, 4)
			expect.truthy(Rooms.ready(wd, "r"), "ready")
			wd.walls[doorEdge].door = nil
			ok, missing = Rooms.ready(wd, "r")
			expect.truthy(not ok)
			expect.truthy(table.find(missing, "Door"), "lacks a door")
			-- A 2×3 type in a 2×2 box is too small.
			local small = world()
			room(small, "s", "SarcophagusSuite", 8, 4, 2, 2)
			local _, lacks = Rooms.ready(small, "s")
			expect.truthy(table.find(lacks, "MinSize"), "lacks its size")
		end
	)

	it("bars are 0..1 and never fall as what they measure grows", function()
		-- Size: bigger boxes.
		local last = -1
		for _, s in { { 2, 2 }, { 2, 3 }, { 3, 3 }, { 3, 4 }, { 4, 4 }, { 5, 5 } } do
			local wd = world()
			room(wd, "r", "StandardRoom", 3, 4, s[1], s[2])
			local b = Rooms.bars(wd, "r")
			expect.atLeast(b.size, 0)
			expect.atMost(b.size, 1)
			expect.atLeast(b.size, last, "size bar with size")
			last = b.size
		end
		expect.near(last, 1, 1e-9, "a room past its full size is full")
		-- Furniture and decor: more of it.
		local wd = world()
		room(wd, "r", "StandardRoom", 6, 4, 4, 4)
		local lastF, lastD = Rooms.bars(wd, "r").furniture, Rooms.bars(wd, "r").decor
		local furniture = {}
		for _, d in Pieces.DecorList do
			if d.furniture and d.location == 1 and d.layer == "Floor" and d.w <= 3 and d.d <= 3 then
				table.insert(furniture, d.id)
			end
		end
		local slot = 0
		local function nextSlot()
			-- 4 × 4 squares apart inside the 4 × 4-cell room at cell (6, 4).
			local i = slot
			slot += 1
			return 6 * Q + (i % 4) * Q, 4 * Q + (i // 4) * Q
		end
		for i = 1, math.min(#furniture, 6) do
			local x, z = nextSlot()
			table.insert(wd.decor, decor(furniture[i], 1, x, z, 0))
			local b = Rooms.bars(wd, "r")
			expect.atMost(b.furniture, 1)
			expect.atLeast(b.furniture, lastF, "furniture bar with furniture")
			expect.near(b.decor, lastD, 1e-9, "furniture leaves the decor bar")
			lastF = b.furniture
		end
		for _, id in smallDecor() do
			if slot >= 16 then
				break
			end
			local x, z = nextSlot()
			table.insert(wd.decor, decor(id, 1, x, z, 0))
			local b = Rooms.bars(wd, "r")
			expect.atMost(b.decor, 1)
			expect.atLeast(b.decor, lastD, "decor bar with decor")
			lastD = b.decor
		end
		expect.truthy(lastF > 0 and lastD > 0, "furnishing moved both bars")
		-- Decor outside the room counts for nothing in it.
		local before = Rooms.bars(wd, "r").decor
		table.insert(wd.decor, decor(smallDecor()[1], 1, 1, 30, 0))
		expect.near(Rooms.bars(wd, "r").decor, before, 1e-9, "outside decor")
	end)

	it("no bonus ever falls as a bar rises", function()
		local fields = { "pay", "stay", "satisfaction", "friendship" }
		for _, bar in { "size", "furniture", "decor" } do
			for _, base in { 0, 0.5, 1 } do
				local prev = nil
				for i = 0, 10 do
					local b = { size = base, furniture = base, decor = base }
					b[bar] = i / 10
					local out = Rooms.bonuses(b)
					if prev then
						for _, f in fields do
							expect.atLeast(out[f], prev[f], `{f} as {bar} rises`)
						end
					end
					expect.atLeast(out.pay, 1, "pay never below base")
					expect.atLeast(out.stay, 1)
					expect.atLeast(out.friendship, 1)
					expect.atLeast(out.satisfaction, 0)
					prev = out
				end
			end
		end
	end)

	it("comfort never falls when a ready room is added, and is capped", function()
		local rng = Random.new(11)
		local list = {}
		local last = Rooms.comfortPoints(list)
		expect.eq(last, 0, "no rooms, no comfort")
		for _ = 1, 30 do
			table.insert(
				list,
				{ size = rng:NextNumber(), furniture = rng:NextNumber(), decor = rng:NextNumber() }
			)
			local now = Rooms.comfortPoints(list)
			expect.atLeast(now, last, "adding a room")
			expect.atMost(now, Constants.Rooms.ComfortRoomsCap)
			last = now
		end
		-- An empty room adds nothing and takes nothing.
		table.insert(list, { size = 0, furniture = 0, decor = 0 })
		expect.near(Rooms.comfortPoints(list), last, 1e-9, "an empty room")
	end)

	it(
		"a guest walks from the entrance through the door to the key furniture, and not once it is walled",
		function()
			local wd = world()
			local doorEdge = room(wd, "r", "StandardRoom", 8, 4, 2, 2)
			bedIn(wd, 8, 4)
			local spot = Rooms.keySpot(wd, "r")
			expect.truthy(spot, "a spot by the bed")
			local legs = Rooms.route(wd, entranceSquare(), spot)
			expect.truthy(legs, "a way in")
			local throughDoor = false
			for _, run in stepsOf(legs) do
				for i = 2, #run.squares do
					local e = crossed(run.floor, run.squares[i - 1], run.squares[i])
					if e == doorEdge then
						throughDoor = true
					end
					if e then
						local w = wd.walls[e]
						expect.truthy(w == nil or w.door, `crossed the wall {e}`)
					end
					expect.truthy(
						Rooms.walkable(wd, run.floor, run.squares[i].x, run.squares[i].z),
						"on walkable squares"
					)
				end
			end
			expect.truthy(throughDoor, "through its door")
			local last = legs[#legs].cells
			expect.eq(last[#last].x, spot.x)
			expect.eq(last[#last].z, spot.z)
			expect.truthy(Rooms.canDoor(wd, doorEdge, false), "walled up")
			wd.walls[doorEdge].door = nil
			expect.eq(Rooms.route(wd, entranceSquare(), spot), nil, "no way in")
		end
	)

	it(
		"furniture never walls a ready room's key furniture off from its door; a room cut off so is not ready and says why",
		function()
			local wd = world()
			room(wd, "r", "StandardRoom", 8, 4, 2, 2)
			local x0, z0 = 8 * Q, 4 * Q
			-- The bed at the back, the door at the front.
			table.insert(wd.decor, decor("Bed", 1, x0 + 1, z0 + 5, 0))
			expect.truthy(Rooms.ready(wd, "r"), "ready")
			-- A row across the room between the door and the bed: its last piece would close it.
			local item = smallDecor()[1]
			local blocker, why = nil, nil
			for x = x0, x0 + 2 * Q - 1 do
				local d = decor(item, 1, x, z0 + 4, 0)
				d.id = `row{x}`
				local ok, refusal = Rooms.canPlaceDecor(wd, d)
				if not ok then
					blocker, why = d, refusal
					break
				end
				table.insert(wd.decor, d)
			end
			expect.eq(why, "KeyCutOff")
			expect.truthy(Rooms.ready(wd, "r"), "still ready")
			local spot = Rooms.keySpot(wd, "r")
			expect.truthy(spot, "a spot by the bed")
			local _, inside = Rooms.doorSquares(wd, "r")
			expect.truthy(Rooms.route(wd, inside, spot), "a way from the door to the bed")
			-- Forced in anyway (as a save from before the rule could hold): not ready, and why.
			table.insert(wd.decor, blocker)
			local ok, missing = Rooms.ready(wd, "r")
			expect.truthy(not ok, "not ready")
			expect.truthy(
				missing and table.find(missing, "KeyUnreached"),
				"its key furniture cut off"
			)
			expect.eq(Rooms.keySpot(wd, "r"), nil, "no spot guests reach")
		end
	)

	it(
		"a ready room always has a guest route from its door to its key spot, and no accepted decor takes it",
		function()
			local rng = Random.new(11)
			local items = smallDecor()
			local x0, z0 = 8 * Q, 4 * Q
			local cutSeen, refusedSeen = false, false
			for _ = 1, 12 do
				local accepted = world()
				room(accepted, "r", "StandardRoom", 8, 4, 2, 2)
				table.insert(
					accepted.decor,
					decor("Bed", 1, x0 + rng:NextInteger(1, 2), z0 + rng:NextInteger(2, 5), 0)
				)
				local forced = table.clone(accepted)
				forced.decor = table.clone(accepted.decor)
				for n = 1, 40 do
					local d = decor(
						items[rng:NextInteger(1, #items)],
						1,
						x0 + rng:NextInteger(0, 2 * Q - 1),
						z0 + rng:NextInteger(1, 2 * Q - 1),
						0
					)
					d.id = `d{n}`
					-- Through the rules: a ready room stays ready.
					local was = Rooms.ready(accepted, "r")
					local ok, why = Rooms.canPlaceDecor(accepted, d)
					if ok then
						table.insert(accepted.decor, d)
						if was then
							expect.truthy(
								Rooms.ready(accepted, "r"),
								"an accepted piece kept it ready"
							)
						end
					elseif why == "KeyCutOff" then
						refusedSeen = true
					end
					-- Forced past the rules: ready only with a way to the key furniture.
					local overlaps = false
					for _, o in forced.decor do
						for _, a in Grid.squares(o) do
							if a.x == d.x and a.z == d.z then
								overlaps = true
							end
						end
					end
					if not overlaps then
						table.insert(forced.decor, d)
					end
					for _, wd in { accepted, forced } do
						local ready, missing = Rooms.ready(wd, "r")
						local spot = Rooms.keySpot(wd, "r")
						if ready then
							expect.truthy(spot, "a ready room has a key spot")
							expect.truthy(
								Rooms.route(wd, entranceSquare(), spot),
								"reached from the entrance"
							)
							local _, inside = Rooms.doorSquares(wd, "r")
							if inside and Rooms.walkable(wd, inside.floor, inside.x, inside.z) then
								expect.truthy(
									Rooms.route(wd, inside, spot),
									"reached from inside its door"
								)
							end
						elseif missing and table.find(missing, "KeyUnreached") then
							cutSeen = true
							expect.eq(spot, nil, "no key spot when it is cut off")
						end
					end
				end
			end
			expect.truthy(refusedSeen, "some placements refused for cutting the key off")
			expect.truthy(cutSeen, "some forced rooms cut off")
		end
	)

	it("a route crosses floors by the stairs and never a wall without a door", function()
		local rng = Random.new(5)
		local wd = stairWorld()
		local H = N * HC
		for _ = 1, 150 do
			local e = Rooms.edgeKey(
				rng:NextInteger(1, 2),
				rng:NextInteger(0, H),
				rng:NextInteger(0, H),
				rng:NextInteger(0, 1)
			)
			if Rooms.canWall(wd, e) then
				wd.walls[e] = { paid = 0, door = if rng:NextInteger(0, 2) == 0 then true else nil }
			end
		end
		local found, upstairs = 0, false
		for _ = 1, 60 do
			local to = {
				floor = rng:NextInteger(1, 2),
				x = rng:NextInteger(0, N * Q - 1),
				z = rng:NextInteger(0, N * Q - 1),
			}
			local legs = Rooms.route(wd, entranceSquare(), to)
			if legs then
				found += 1
				for _, leg in legs do
					if leg.stair then
						upstairs = true
					end
				end
				for _, run in stepsOf(legs) do
					for i = 2, #run.squares do
						local e = crossed(run.floor, run.squares[i - 1], run.squares[i])
						if e then
							local w = wd.walls[e]
							expect.truthy(w == nil or w.door, `crossed the wall {e}`)
						end
					end
				end
				local last = legs[#legs].cells
				expect.eq(last[#last].x, to.x)
				expect.eq(last[#last].z, to.z)
				expect.eq(legs[#legs].floor, to.floor)
			end
		end
		expect.truthy(found > 0, "some places reached")
		expect.truthy(upstairs, "some by the stair")
	end)

	it("the type list is every room type and amenity of the location, with its tooltip", function()
		local list = Rooms.types(1, {}, 1, 0, 1, false)
		local byId = {}
		for _, t in list do
			byId[t.id] = t
			expect.truthy(#t.keys > 0, `{t.id} has key furniture`)
			expect.atLeast(t.fullCells, t.minCells, `{t.id} full size`)
			for _, k in t.keys do
				expect.truthy(Pieces.decor(k).furniture, `{k} is furniture`)
			end
		end
		for _, p in Pieces.List do
			if (p.kind == "Room" or p.kind == "Amenity") and p.location == 1 then
				local t = byId[p.id]
				expect.truthy(t, `{p.id} listed`)
				expect.eq(t.locked ~= nil, p.unlock ~= nil, `{p.id} locked as its unlock says`)
				expect.eq(t.minCells, p.w * p.d, `{p.id} minimum is its old footprint`)
				if p.kind == "Amenity" then
					expect.eq(#t.tags, #(p.tags or {}), `{p.id} tags`)
				end
			end
		end
		for _, sp in Species.List do
			if sp.location == 1 then
				expect.truthy(
					byId[sp.room] and table.find(byId[sp.room].species, sp.id),
					`{sp.id} in its room's tooltip`
				)
			end
		end
		-- Everything unlocked: nothing locked.
		local all = {}
		for _, p in Pieces.List do
			all[p.id] = true
		end
		for _, t in Rooms.types(1, all, 1) do
			expect.eq(t.locked, nil, t.id)
		end
	end)
	it("moving the only stair never strands a ready room upstairs", function()
		local wd = stairWorld()
		-- Floor 2 cut in two at cell column 5: the stair's head (2, 5) on the west side.
		for hz = 0, N * HC - 1 do
			wall(wd, Rooms.edgeKey(2, 5 * HC, hz, 1))
		end
		-- A ready room on the west side, its door onto row 0.
		box(wd, 2, 1, 1, 2, 2, true)
		local ok, why = Rooms.canMakeRoom(wd, 2, 1 * HC, 1 * HC, "StandardRoom")
		expect.truthy(ok, `room: {why}`)
		wd.rooms.r = { type = "StandardRoom", floor = 2, hx = 1 * HC, hz = 1 * HC }
		table.insert(wd.decor, decor("Bed", 2, 1 * Q + 1, 1 * Q + 5, 0))
		expect.truthy(Rooms.ready(wd, "r"), "ready")
		local stair = wd.pieces[2]
		-- Moved east, its head lands beyond the wall: the room is cut off.
		local east = placed("Stairs", 1, 8, 6, 0)
		ok, why = Rooms.canPlacePiece(wd, east, stair)
		expect.truthy(not ok, "the stair moved away from the room")
		expect.eq(why, "CutsOff")
		-- Moved along the west side, it still serves the room.
		local west = placed("Stairs", 1, 1, 8, 0)
		ok, why = Rooms.canPlacePiece(wd, west, stair)
		expect.truthy(ok, `moved on the west side: {tostring(why)}`)
	end)

	-- A ready Standard Room at cells (3..4, 4..5), its door on row 4's front, its Bed in the back row.
	local function readyRoomWorld()
		local wd = world(1)
		room(wd, "r", "StandardRoom", 3, 4, 2, 2)
		table.insert(wd.decor, decor("Bed", 1, 3 * Q + 1, 5 * Q, 0))
		expect.truthy(Rooms.ready(wd, "r"), "ready")
		return wd
	end

	it(
		"readiness and key spots say of every room what ready and keySpot say, as the hotel changes",
		function()
			local wd = readyRoomWorld()
			room(wd, "s", "StandardRoom", 6, 4, 2, 2) -- no Bed: not ready
			local function agree(label)
				local all = Rooms.readiness(wd)
				for id in wd.rooms do
					local ok, missing = Rooms.ready(wd, id)
					expect.eq(all[id].ok, ok, `{label}: {id}`)
					expect.eq(
						table.concat(all[id].missing or {}, ","),
						table.concat(missing or {}, ","),
						`{label}: {id}`
					)
				end
			end
			agree("built")
			local spots = Rooms.keySpots(wd)
			for id in wd.rooms do
				local one, all = Rooms.keySpot(wd, id), spots[id]
				expect.eq(
					one and `{one.floor}:{one.x}:{one.z}`,
					all and `{all.floor}:{all.x}:{all.z}`,
					`key spot {id}`
				)
			end
			for hx = 0, N * HC - 2 do
				wall(wd, Rooms.edgeKey(1, hx, 3 * HC, 0))
			end
			agree("corridor nearly shut")
			wd.walls[Rooms.edgeKey(1, N * HC - 1, 3 * HC, 0)] = { paid = 0 }
			agree("corridor shut")
		end
	)

	it("withAreas keeps a world's areas only while it runs, even when it fails", function()
		local wd = readyRoomWorld()
		local before = assert(Rooms.roomArea(wd, "r")).size
		local fine = pcall(Rooms.withAreas, wd, function()
			Rooms.roomArea(wd, "r")
			error("a failing pass")
		end)
		expect.eq(fine, false, "the error comes through")
		-- Split the room in two: its area must shrink, not be read from a kept memo.
		for hx = 3 * HC, 5 * HC - 1 do
			wd.walls[Rooms.edgeKey(1, hx, 5 * HC, 0)] = { paid = 0 }
		end
		local after = assert(Rooms.roomArea(wd, "r")).size
		expect.truthy(after < before, `area {before} -> {after}`)
		-- Nested, each world keeps its own.
		local other = readyRoomWorld()
		Rooms.withAreas(wd, function()
			Rooms.withAreas(other, function()
				expect.eq(assert(Rooms.roomArea(wd, "r")).size, after, "the split world")
				expect.eq(assert(Rooms.roomArea(other, "r")).size, before, "the whole one")
			end)
		end)
	end)

	it(
		"a wall across the corridor to a ready room is refused (CutsOff), a door in it is not",
		function()
			local wd = readyRoomWorld()
			-- A wall the floor's width at half row 6 (cell row 3's front), between the entrance and the room.
			local last = Rooms.edgeKey(1, N * HC - 1, 3 * HC, 0)
			for hx = 0, N * HC - 2 do
				wall(wd, Rooms.edgeKey(1, hx, 3 * HC, 0))
			end
			expect.truthy(Rooms.ready(wd, "r"), "still reached round the wall's open end")
			local ok, why = Rooms.canWall(wd, last, false)
			expect.truthy(not ok, "the wall closing the corridor")
			expect.eq(why, "CutsOff")
			ok, why = Rooms.canWall(wd, last, true)
			expect.truthy(ok, `a door closing it: {tostring(why)}`)
			-- The same cut made by taking the door out again.
			wall(wd, last, true)
			ok, why = Rooms.canDoor(wd, last, false)
			expect.truthy(not ok, "the door taken out of the corridor wall")
			expect.eq(why, "CutsOff")
		end
	)

	it("a wall splitting a ready room's Bed off into a pocket is refused (KeyCutOff)", function()
		local wd = readyRoomWorld()
		-- Across the room at half row 10, between the door's half (rows 8..9) and the Bed's (10..11).
		local first, last = 3 * HC, 5 * HC - 1
		for hx = first, last - 1 do
			wall(wd, Rooms.edgeKey(1, hx, 5 * HC, 0))
		end
		expect.truthy(Rooms.ready(wd, "r"), "still ready round the wall's open end")
		local ok, why = Rooms.canWall(wd, Rooms.edgeKey(1, last, 5 * HC, 0), false)
		expect.truthy(not ok, "the wall closing the pocket")
		expect.eq(why, "KeyCutOff")
	end)

	it(
		"moving a ready room's Bed behind furniture that cuts it off is refused (KeyCutOff)",
		function()
			-- 2026-10-26 night (a code review): a move judged the room without the piece
			-- being moved, so a moved Bed was never "before" ready and the rule was skipped.
			local wd = world()
			room(wd, "r", "StandardRoom", 8, 4, 2, 2)
			local x0, z0 = 8 * Q, 4 * Q
			local bed = decor("Bed", 1, x0 + 5, z0, 0) -- at the front, beside the door's corner
			bed.id = "bed"
			table.insert(wd.decor, bed)
			expect.truthy(Rooms.ready(wd, "r"), "ready with the Bed at the front")
			-- A row right across the room behind the Bed: it cuts off only the empty back.
			local item = smallDecor()[1]
			for x = x0, x0 + 2 * Q - 1 do
				local d = decor(item, 1, x, z0 + 4, 0)
				d.id = `row{x}`
				local ok, why = Rooms.canPlaceDecor(wd, d)
				expect.truthy(ok, `row piece at {x}: {why}`)
				table.insert(wd.decor, d)
			end
			expect.truthy(Rooms.ready(wd, "r"), "still ready")
			local moved = decor("Bed", 1, x0 + 1, z0 + 5, 0)
			moved.id = "bed"
			local ok, why = Rooms.canPlaceDecor(wd, moved, "bed")
			expect.truthy(not ok, "the Bed moved behind the row")
			expect.eq(why, "KeyCutOff")
			local along = decor("Bed", 1, x0 + 2, z0, 0)
			along.id = "bed"
			expect.truthy(
				Rooms.canPlaceDecor(wd, along, "bed"),
				"moved along the front, still reached"
			)
		end
	)
	-- A.13.2 and his yes (§18 2026-10-26): activity rooms are ready on their key furniture as any room.
	it(
		"a Game Room is ready with a Pool Table, the Snack Bar with a Salad Bar, the Graveyard Garden with a Fountain",
		function()
			for _, case in
				{
					{ "GameRoom", "PoolTable" },
					{ "SnackBar", "SaladBar" },
					{ "SnackBar", "DessertTrolley" },
					{ "GraveyardGarden", "Fountain" },
					{ "GraveyardGarden", "GardenBench" },
				}
			do
				local wd = world()
				room(wd, "r", case[1], 8, 4, 2, 2)
				local ok0 = Rooms.ready(wd, "r")
				expect.truthy(not ok0, `{case[1]} not ready before its key`)
				local d = Pieces.decor(case[2]) :: any
				-- At the back of the room, the door at the front.
				local key = decor(case[2], 1, 8 * Q + 1, 4 * Q + 2 * Q - 1 - d.d, 0)
				local okPlace, why = Rooms.canPlaceDecor(wd, key)
				expect.truthy(okPlace, `{case[2]} placed: {why}`)
				table.insert(wd.decor, key)
				local ok, lacks = Rooms.ready(wd, "r")
				expect.truthy(
					ok,
					`{case[1]} ready with a {case[2]}: {table.concat(lacks or {}, ", ")}`
				)
			end
		end
	)

	it("the activity rooms are every location's; a location's own stay its own", function()
		local function ids(location)
			local out = {}
			for _, t in Rooms.types(location, {}, 1, 0, 1, false) do
				out[t.id] = t
			end
			return out
		end
		local manor, frost = ids(1), ids(2)
		for _, p in Pieces.List do
			if p.kind == "Amenity" or p.kind == "Room" then
				expect.eq(
					manor[p.id] ~= nil,
					p.location == 0 or p.location == 1,
					`{p.id} at the Manor`
				)
				expect.eq(
					frost[p.id] ~= nil,
					p.location == 0 or p.location == 2,
					`{p.id} at Frostfang`
				)
			end
		end
		for _, t in Rooms.types(2, {}, 1, 0, 1, false) do
			expect.truthy(#t.keys > 0, `{t.id} has key furniture`)
			expect.eq(t.fullCells, t.minCells * Constants.Rooms.FullSizeFactor, `{t.id} full size`)
			for _, k in t.keys do
				local d = Pieces.decor(k) :: any
				expect.truthy(d.furniture, `{k} is furniture`)
				expect.truthy(Pieces.decorHere(d, 2, {}), `{k} placeable at Frostfang`)
			end
		end
	end)

	-- A.13.1 "Rules kept": a room with a visitor in it or on the way is busy, as a booked one.
	it(
		"a visitor on its way to or in an activity room keeps it ready; one walking back does not",
		function()
			local wd = world()
			room(wd, "g", "GameRoom", 8, 4, 2, 2)
			local pool = decor("PoolTable", 1, 8 * Q + 2, 4 * Q + 5, 0)
			pool.id = "pool"
			table.insert(wd.decor, pool)
			expect.truthy(Rooms.ready(wd, "g"), "the Game Room ready")
			local sold = table.clone(wd)
			sold.decor = {}
			for _, phase in { "Going", "There" } do
				local busy = Visits.busyRooms({ v = { room = "g", spot = "p:1", phase = phase } })
				expect.truthy(
					not Rooms.keepsBusy(wd, sold, busy),
					`selling its key with a visitor {phase}`
				)
			end
			local back = Visits.busyRooms({ v = { room = "g", spot = "p:1", phase = "Back" } })
			expect.truthy(Rooms.keepsBusy(wd, sold, back), "the visitor walking back")
		end
	)
end)
