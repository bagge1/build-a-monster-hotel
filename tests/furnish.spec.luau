local Furnish = require(Shared.Furnish)
local Grid = require(Shared.Grid)
local Constants = require(Shared.Constants)
local Pieces = require(Shared.Pieces)

local Q = Constants.Grid.Squares

local function item(id, x, z, r)
	local d = Pieces.decor(id)
	return { x = x, z = z, r = r, w = d.w, d = d.d, layer = d.layer, id = id }
end

describe("Furnish", function()
	it("decor turned into a room's frame and back lands where it was, for every turn", function()
		for _, size in { { 2, 2 }, { 2, 3 }, { 3, 3 } } do
			for rr = 0, 3 do
				local room = { x = 3, z = 4, r = rr, w = size[1], d = size[2] }
				local ex, ez = Grid.extent(room.w, room.d, rr)
				for _, id in { "Candles", "AntiqueWardrobe", "RugRunner", "GrandPiano" } do
					local d = Pieces.decor(id)
					for dr = 0, 3 do
						local dx, dz = Grid.extent(d.w, d.d, dr)
						for x = room.x * Q, (room.x + ex) * Q - dx do
							for z = room.z * Q, (room.z + ez) * Q - dz do
								local it = { x = x, z = z, r = dr, w = d.w, d = d.d }
								expect.truthy(Furnish.inside(room, it), "inside")
								local l = Furnish.toRoom(room, it)
								local lx, lz = Grid.extent(d.w, d.d, l.r)
								expect.truthy(
									l.x >= 0
										and l.z >= 0
										and l.x + lx <= room.w * Q
										and l.z + lz <= room.d * Q,
									`{id} inside the room's frame ({size[1]}x{size[2]} r{rr})`
								)
								local back = Furnish.fromRoom(room, l, d.w, d.d)
								expect.eq(back.x, x, "x back")
								expect.eq(back.z, z, "z back")
								expect.eq(back.r, dr, "r back")
							end
						end
					end
				end
			end
		end
	end)

	it("the room's frame turns with the room: its door side is the side the door faces", function()
		for rr = 0, 3 do
			local room = { x = 2, z = 2, r = rr, w = 2, d = 2 }
			-- A square on the room's door side (local z = 0) sits next to the door's cell.
			local along = math.floor((room.w - 1) / 2)
			local l = { x = along * Q + 1, z = 0, r = 0 }
			local p = Furnish.fromRoom(room, l, 1, 1)
			local cell = { x = p.x // Q, z = p.z // Q }
			local inside = Grid.doorInside(room)
			expect.eq(cell.x, inside.x, `door side x, r{rr}`)
			expect.eq(cell.z, inside.z, `door side z, r{rr}`)
		end
	end)

	it(
		"decor keeps out of the doorway, off the furniture and off itself; rugs lie under",
		function()
			local room = { w = 2, d = 2 }
			local along = math.floor((room.w - 1) / 2)
			local doorX = along * Q + 1
			local ok, why = Furnish.canPlace(room, {}, item("Candles", doorX, 0, 0))
			expect.eq(why, "Doorway", "candles in the doorway")
			expect.truthy(
				Furnish.canPlace(room, {}, item("RugCorner", doorX, 0, 0)),
				"a rug in the doorway"
			)
			local blocked = { [Furnish.squareKey(5, 6)] = true }
			ok, why = Furnish.canPlace(room, {}, item("Candles", 5, 6, 0), blocked)
			expect.eq(why, "Furniture", "on the bed")
			local others = { item("Armchair", 0, 6, 0) }
			ok, why = Furnish.canPlace(room, others, item("Candles", 0, 6, 0))
			expect.eq(why, "Overlap", "on the armchair")
			expect.truthy(
				Furnish.canPlace(room, others, item("RugSquare", 0, 4, 0)),
				"a rug under it"
			)
			ok, why =
				Furnish.canPlace(room, { item("RugSquare", 0, 4, 0) }, item("RugCorner", 2, 6, 0))
			expect.eq(why, "Overlap", "a rug on a rug")
			ok, why = Furnish.canPlace(room, {}, item("Candles", room.w * Q, 0, 0))
			expect.eq(why, "Outside", "past the wall")
			expect.truthy(ok == false, "refused")
		end
	)

	it("wall decor stands only with its back against a wall", function()
		local room = { w = 2, d = 2 }
		local W, D = room.w * Q, room.d * Q
		local d = Pieces.decor("Bookshelf")
		local _, why = Furnish.canPlace(room, {}, item("Bookshelf", 2, 3, 0))
		expect.eq(why, "NoWall", "in the middle of the room")
		expect.truthy(
			Furnish.canPlace(room, {}, item("Bookshelf", 2, D - d.d, 0)),
			"back wall, facing in"
		)
		_, why = Furnish.canPlace(room, {}, item("Bookshelf", 2, D - d.d, 2))
		expect.eq(why, "NoWall", "back wall, facing it")
		expect.truthy(Furnish.canPlace(room, {}, item("Bookshelf", 0, 2, 1)), "left wall")
		expect.truthy(Furnish.canPlace(room, {}, item("Bookshelf", W - d.d, 2, 3)), "right wall")
		expect.truthy(
			Furnish.canPlace(room, {}, item("Bookshelf", W - d.w, 0, 2)),
			"the door's wall, beside the door"
		)
	end)

	it("more decor never lowers a tier; a bigger room needs more; T1 to the top", function()
		for _, size in { { 2, 2 }, { 2, 3 }, { 3, 3 } } do
			local last = 1
			for points = 0, 2000, 10 do
				local t = Furnish.tier(size[1], size[2], points)
				expect.atLeast(t, last, "monotonic")
				expect.atMost(t, Constants.Economy.MaxTier, "at most the top")
				last = t
			end
			expect.eq(Furnish.tier(size[1], size[2], 0), 1, "bare is T1")
			expect.eq(last, Constants.Economy.MaxTier, "enough reaches the top")
			expect.eq(Furnish.nextTier(size[1], size[2], 1e9), nil, "nothing past the top")
		end
		local small, big = Furnish.thresholds(2, 2), Furnish.thresholds(3, 3)
		for i in small do
			expect.atLeast(big[i], small[i], "a 3x3 needs at least a 2x2's points")
		end
	end)

	it("dearer decor is worth more points, and a room's tags are its decor's", function()
		for _, a in Pieces.DecorList do
			for _, b in Pieces.DecorList do
				if a.cost > b.cost then
					expect.atLeast(Furnish.points(a.id), Furnish.points(b.id), `{a.id} over {b.id}`)
				end
			end
		end
		local tags = Furnish.tags({ "Candles", "Planter" })
		expect.truthy(tags.candles and tags.darkness and tags.garden, "both items' tags")
		expect.truthy(next(Furnish.tags({})) == nil, "no decor, no tags")
	end)

	it("every decor has a footprint, a layer, and fits a 2x2 room", function()
		for _, d in Pieces.DecorList do
			expect.truthy(
				d.w >= 1 and d.d >= 1 and d.w % 1 == 0 and d.d % 1 == 0,
				`{d.id} footprint`
			)
			expect.truthy(
				d.layer == "Floor" or d.layer == "Rug" or d.layer == "Wall",
				`{d.id} layer`
			)
			expect.atMost(d.w, 2 * Q, `{d.id} width`)
			expect.atMost(d.d, 2 * Q - 2, `{d.id} depth leaves the doorway`)
			if d.layer == "Rug" then
				expect.atMost(d.height, 0.15, `{d.id} lies flat`)
			else
				expect.atMost(d.height, 7, `{d.id} height`)
			end
		end
	end)

	-- §5.4: the finish a floor has already is never laid, nor paid for, again.
	it("a floor finish changes a floor only to another finish", function()
		local f = Pieces.Finishes[1]
		expect.truthy(f ~= nil, "a finish")
		expect.truthy(not Pieces.finishChanges(f.id, f.id), "the same finish again")
		expect.truthy(not Pieces.finishChanges(nil, ""), "the slab's own again")
		expect.truthy(not Pieces.finishChanges("", ""), "the slab's own again, stored")
		expect.truthy(Pieces.finishChanges(nil, f.id), "a finish on the slab")
		expect.truthy(Pieces.finishChanges(f.id, ""), "back to the slab's own")
		local other = Pieces.Finishes[2]
		if other then
			expect.truthy(Pieces.finishChanges(f.id, other.id), "another finish")
		end
	end)
end)
