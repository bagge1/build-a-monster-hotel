-- A door goes only in a wall that stands, and the Door tool takes the wall the pointer is on (his ruling 2026-10-23, A.12).
local Rooms = require(Shared.Rooms)
local Grid = require(Shared.Grid)
local Constants = require(Shared.Constants)
local Pieces = require(Shared.Pieces)

local G = Constants.Grid
local N = G.Cells
local HALF = G.CellSize / Rooms.HalfCells

local function world(floors)
	local owned = {}
	for f = 1, floors do
		for z = 0, N - 1 do
			for x = 0, N - 1 do
				owned[Grid.tileKey(f, x, z)] = true
			end
		end
	end
	local p = Pieces.get("FrontDesk")
	local d = G.DeskStart
	return {
		floors = floors,
		tiles = owned,
		pieces = { { item = "FrontDesk", kind = p.kind, floor = 1, x = d.x, z = d.z, r = d.r, w = p.w, d = p.d } },
		decor = {},
		walls = {},
		rooms = {},
	}
end

describe("Doors (A.12, his ruling 2026-10-23)", function()
	it("a door goes only in a standing wall", function()
		local w = world(1)
		local e = Rooms.edgeKey(1, 4, 12, 0)
		local ok, why = Rooms.canDoor(w, e, true)
		expect.eq(ok, false)
		expect.eq(why, "NoWall")
		w.walls[e] = { paid = 0 }
		expect.truthy(Rooms.canDoor(w, e, true), "a door in the wall")
	end)

	it("the pointer's ray takes the first wall it meets, never one behind it", function()
		local w = world(1)
		local y = Grid.floorY(1)
		-- Two walls along x, one behind the other: z = 8 half cells and z = 10.
		local front, back = Rooms.edgeKey(1, 4, 8, 0), Rooms.edgeKey(1, 4, 10, 0)
		w.walls[front] = { paid = 0 }
		w.walls[back] = { paid = 0 }
		-- A camera in front (low z), high up, looking down past the front wall's top: the
		-- floor point is behind the back wall, but the ray meets the front wall first.
		local target = Vector3.new(4.5 * HALF, y + 4, 8 * HALF)
		local origin = Vector3.new(4.5 * HALF, y + 30, 8 * HALF - 40)
		expect.eq(Rooms.wallOnRay(w, 1, origin, target - origin), front)
		-- Aimed over the front wall's top at the back one: the back one.
		local high = Vector3.new(4.5 * HALF, y + 40, 8 * HALF - 8)
		local onBack = Vector3.new(4.5 * HALF, y + 2, 10 * HALF)
		expect.eq(Rooms.wallOnRay(w, 1, high, onBack - high), back)
	end)

	it("a ray past every wall takes none, and a wall on another floor is not this floor's", function()
		local w = world(2)
		local y = Grid.floorY(1)
		w.walls[Rooms.edgeKey(2, 4, 8, 0)] = { paid = 0 }
		local origin = Vector3.new(4.5 * HALF, y + 6, 0)
		local dir = Vector3.new(0, 0, 1)
		expect.eq(Rooms.wallOnRay(w, 1, origin, dir), nil)
		-- Along z, the wall at x = 3 half cells: met by a ray across it.
		local side = Rooms.edgeKey(1, 3, 5, 1)
		w.walls[side] = { paid = 0 }
		local from = Vector3.new(0, y + 3, 5.5 * HALF)
		expect.eq(Rooms.wallOnRay(w, 1, from, Vector3.new(1, 0, 0)), side)
		-- Beside the half edge, not on it: missed.
		local beside = Vector3.new(0, y + 3, 6.5 * HALF)
		expect.eq(Rooms.wallOnRay(w, 1, beside, Vector3.new(1, 0, 0)), nil)
	end)
end)
