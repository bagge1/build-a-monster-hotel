local Grid = require(Shared.Grid)
local Constants = require(Shared.Constants)
local Pieces = require(Shared.Pieces)

local N = Constants.Grid.Cells

local function placed(id, floor, x, z, r)
	local p = Pieces.get(id)
	return { item = id, floor = floor, x = x, z = z, r = r, w = p.w, d = p.d }
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

	it("the lobby and the stair core are never built on", function()
		expect.truthy(not Grid.canPlace({}, 1, placed("StandardRoom", 1, 0, 0, 2)), "lobby")
		local s = Constants.Grid.StairCore
		expect.truthy(
			not Grid.canPlace({}, 2, placed("StandardRoom", 2, s.x, s.z, 0)),
			"stair core"
		)
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
				for i = 2, #path do
					local a, b = path[i - 1], path[i]
					expect.truthy(a.x == b.x or a.z == b.z, "path legs are straight")
				end
			end
		end
	end)
end)
