local Grid = require(Shared.Grid)
local Constants = require(Shared.Constants)
local Pieces = require(Shared.Pieces)

local N = Constants.Grid.Cells

local function placed(id, floor, x, z, r)
	local p = Pieces.get(id)
	return { item = id, floor = floor, x = x, z = z, r = r, w = p.w, d = p.d }
end

-- Whether a path (its turns) steps on a stair core cell anywhere along its legs.
local function throughCore(path)
	for i = 2, #path do
		local a, b = path[i - 1], path[i]
		local dx, dz = math.sign(b.x - a.x), math.sign(b.z - a.z)
		local x, z = a.x, a.z
		while true do
			if Grid.isStairCore(x, z) then
				return true
			end
			if x == b.x and z == b.z then
				break
			end
			x += dx
			z += dz
		end
	end
	return #path == 1 and Grid.isStairCore(path[1].x, path[1].z)
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
					"door cells adjacent"
				)
				local f = Grid.doorFacing(r)
				expect.eq(outside.x - inside.x, f.X, "facing x")
				expect.eq(outside.z - inside.z, f.Z, "facing z")
			end
		end
	end)

	it("the stair landing above floor 1 is never built on", function()
		local s = Constants.Grid.StairCore
		for floor = 2, 3 do
			for x = s.x, s.x + s.w - 1 do
				expect.truthy(Grid.isReserved(floor, x, s.z - 1), `landing {x} on floor {floor}`)
			end
		end
	end)

	it("the lobby and the stair core are never built on", function()
		expect.truthy(not Grid.canPlace({}, 1, placed("StandardRoom", 1, 0, 0, 2)), "lobby")
		local s = Constants.Grid.StairCore
		expect.truthy(
			not Grid.canPlace({}, 2, placed("StandardRoom", 2, s.x, s.z, 0)),
			"stair core"
		)
	end)

	it("a door onto the stair core's back or side opens into a wall", function()
		-- The core (x 10–11, z 2–3) is walled at the back and sides; x 12 is off the plot.
		for floor = 1, 2 do
			for _, case in
				{
					{ "CoffinSuite", 9, 4, 0, "back" }, -- TESTRUN phase 11's suite
					{ "StandardRoom", 10, 4, 0, "back" },
					{ "StandardRoom", 8, 2, 1, "side" },
				}
			do
				local ok, why =
					Grid.canPlace({}, 2, placed(case[1], floor, case[2], case[3], case[4]))
				expect.truthy(not ok, `{case[1]} onto the core's {case[5]}, floor {floor}`)
				expect.eq(why, "DoorBlocked", `{case[1]} refused as a wall, floor {floor}`)
			end
			expect.truthy(
				Grid.canPlace({}, 2, placed("StandardRoom", floor, 8, 2, 0)),
				`beside the core, its door to the front, floor {floor}`
			)
		end
	end)

	it("a guest's path goes round the stair core, never through it", function()
		local s = Constants.Grid.StairCore
		local landing = { x = s.x + 1, z = s.z - 1 }
		for floor = 1, 2 do
			local behind = placed("StandardRoom", floor, s.x, s.z + s.d + 1, 0)
			expect.truthy(Grid.canPlace({}, 2, behind), `a room behind the core, floor {floor}`)
			local path = Grid.path({ behind }, floor, landing, Grid.doorCell(behind))
			expect.truthy(path ~= nil, `a path behind the core, floor {floor}`)
			expect.truthy(
				path and not throughCore(path),
				`the path behind the core goes round it, floor {floor}`
			)
			expect.truthy(
				Grid.path({}, floor, landing, { x = s.x, z = s.z }) == nil,
				`the core's cells are no hallway, floor {floor}`
			)
		end
		for _, c in Grid.wayIn(2) do
			expect.truthy(not Grid.isStairCore(c.x, c.z), "floor 2 is entered from the landing")
		end
	end)

	it(
		"nothing is placed out of bounds, on a floor the hotel lacks, or on another piece",
		function()
			expect.truthy(
				not Grid.canPlace({}, 1, placed("StandardRoom", 1, N - 1, 5, 0)),
				"off the edge"
			)
			expect.truthy(
				not Grid.canPlace({}, 1, placed("StandardRoom", 2, 2, 5, 0)),
				"no floor 2"
			)
			local a = placed("StandardRoom", 1, 2, 3, 0)
			expect.truthy(Grid.canPlace({}, 1, a), "first room")
			expect.truthy(
				not Grid.canPlace({ a }, 1, placed("StandardRoom", 1, 3, 3, 0)),
				"overlap"
			)
		end
	)

	it("a door that faces the plot's edge is refused", function()
		expect.truthy(
			not Grid.canPlace({}, 2, placed("StandardRoom", 2, 2, 0, 0)),
			"door off the plot"
		)
	end)

	it("a piece moved onto its own cells is legal", function()
		local a = placed("StandardRoom", 1, 2, 3, 0)
		expect.truthy(Grid.canPlace({ a }, 1, a, a), "itself")
	end)

	it("no accepted placement ever cuts a door off, and every door has a path in", function()
		local rng = Random.new(7)
		local ids = { "StandardRoom", "SarcophagusSuite", "DenRoom", "SnackBar" }
		for floor = 1, 2 do
			local layout = {}
			for _ = 1, 400 do
				local p = placed(
					ids[rng:NextInteger(1, #ids)],
					floor,
					rng:NextInteger(0, N - 1),
					rng:NextInteger(0, N - 1),
					rng:NextInteger(0, 3)
				)
				if Grid.canPlace(layout, 2, p) then
					table.insert(layout, p)
				end
			end
			expect.truthy(#layout >= 4, `several pieces fit on floor {floor} ({#layout})`)
			local start = Grid.wayIn(floor)[1]
			for _, p in layout do
				local path = Grid.path(layout, floor, start, Grid.doorCell(p))
				expect.truthy(path ~= nil, `a path to {p.item} at {p.x},{p.z} r{p.r}`)
				expect.truthy(
					path and not throughCore(path),
					`the path to {p.item} at {p.x},{p.z} keeps out of the stair core`
				)
				for i = 2, #path do
					local a, b = path[i - 1], path[i]
					expect.truthy(a.x == b.x or a.z == b.z, "path legs are straight")
				end
			end
		end
	end)
end)
