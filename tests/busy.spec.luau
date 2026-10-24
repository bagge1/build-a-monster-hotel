-- A room a guest is in or due at stays ready and the same size through every change (GDD §5.4, A.12).
local Rooms = require(Shared.Rooms)
local Grid = require(Shared.Grid)
local Constants = require(Shared.Constants)
local Pieces = require(Shared.Pieces)

local G = Constants.Grid
local N = G.Cells
local HC = Rooms.HalfCells
local H = N * HC

local function placed(id, floor, x, z, r)
	local p = Pieces.get(id)
	return { item = id, kind = p.kind, floor = floor, x = x, z = z, r = r, w = p.w, d = p.d }
end

-- A new hotel as PlayerData builds it: the start square, the desk, the start room "2" with its Bed.
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
	local desk = placed("FrontDesk", 1, d.x, d.z, d.r)
	desk.id = "1"
	local world = {
		floors = 1,
		tiles = tiles,
		pieces = { desk },
		decor = {},
		walls = walls,
		rooms = { ["2"] = { type = S.type, floor = 1, hx = S.seed.hx, hz = S.seed.hz } },
	}
	for i, f in S.furniture do
		local p = Pieces.decor(f.item)
		table.insert(world.decor, {
			item = f.item,
			layer = p.layer,
			floor = 1,
			x = f.x,
			z = f.z,
			r = f.r,
			w = p.w,
			d = p.d,
			id = tostring(10 + i),
		})
	end
	return world
end

local function withWalls(w, change)
	local after = table.clone(w)
	after.walls = table.clone(w.walls)
	change(after.walls)
	return after
end

-- A tile bought as the server buys it: its auto walls with it.
local function withTile(w, floor, x, z, auto)
	local after = table.clone(w)
	after.tiles = table.clone(w.tiles)
	after.tiles[Grid.tileKey(floor, x, z)] = true
	after.walls = table.clone(w.walls)
	for _, e in auto or {} do
		after.walls[e] = { paid = 0 }
	end
	return after
end

describe("Busy rooms (§5.4, A.12)", function()
	it("the start room is ready, so a guest can be booked into it", function()
		expect.truthy(Rooms.ready(startHotel(), "2"))
	end)

	it("walling up a busy room's door, or opening its wall, does not keep its guest", function()
		local w = startHotel()
		local S = Constants.Rooms.Start
		local door = Rooms.edgeKey(1, S.door.hx, S.door.hz, S.door.o)
		local shut = withWalls(w, function(walls)
			walls[door] = { paid = 0 }
		end)
		expect.eq(Rooms.keepsBusy(w, shut, { ["2"] = true }), false)
		local open = withWalls(w, function(walls)
			walls[door] = nil
		end)
		expect.eq(Rooms.keepsBusy(w, open, { ["2"] = true }), false)
		-- Not busy: the same changes are no business of keepsBusy.
		expect.eq(Rooms.keepsBusy(w, shut, {}), true)
	end)

	it("a tile beside a busy room keeps it only with its auto walls", function()
		local w = startHotel()
		-- The start room runs to the start square's left edge: the tile on its left meets it.
		local S = G.StartTiles
		local x, z = S.x - 1, S.z + S.d - 1
		local auto = Rooms.autoWalls(w, 1, x, z)
		expect.truthy(#auto > 0, "the tile beside the room gets walls")
		expect.eq(Rooms.keepsBusy(w, withTile(w, 1, x, z, auto), { ["2"] = true }), true)
		expect.eq(Rooms.keepsBusy(w, withTile(w, 1, x, z, nil), { ["2"] = true }), false)
	end)

	it("no wall, door or tile change the server would allow leaves a busy room unready", function()
		local rng = Random.new(7)
		local busy = { ["2"] = true }
		for trial = 1, 25 do
			local w = startHotel()
			for step = 1, 50 do
				local op = rng:NextInteger(1, 4)
				local after
				if op == 1 then
					local x, z = rng:NextInteger(0, N - 1), rng:NextInteger(0, N - 1)
					if Grid.canBuyTile(w.tiles, 1, 1, x, z) then
						local a = withTile(w, 1, x, z, Rooms.autoWalls(w, 1, x, z))
						if Rooms.check(w, a) then
							after = a
						end
					end
				else
					local e = Rooms.edgeKey(
						1,
						rng:NextInteger(0, H),
						rng:NextInteger(0, H),
						rng:NextInteger(0, 1)
					)
					local rec = w.walls[e]
					if op == 2 and not rec and Rooms.canWall(w, e, false) then
						after = withWalls(w, function(walls)
							walls[e] = { paid = 0 }
						end)
					elseif op == 3 and rec and Rooms.canRemoveWall(w, e) then
						after = withWalls(w, function(walls)
							walls[e] = nil
						end)
					elseif op == 4 then
						local put = not (rec and rec.door)
						local ok = if rec then Rooms.canDoor(w, e, put) else Rooms.canWall(w, e, true)
						if ok then
							after = withWalls(w, function(walls)
								walls[e] = { door = if put then true else nil, paid = 0 }
							end)
						end
					end
				end
				if after and Rooms.keepsBusy(w, after, busy) then
					w = after
				end
				local ok, missing = Rooms.ready(w, "2")
				expect.truthy(
					ok,
					`trial {trial} step {step}: busy room not ready ({table.concat(missing or {}, ",")})`
				)
			end
		end
	end)
end)
