local Grid = require(Shared.Grid)
local Layout = require(Shared.Layout)
local Pieces = require(Shared.Pieces)

-- Any decor row will do: the rules below hold for every one.
local DECOR = Pieces.DecorList[1].id

local PIECES_MAP = {
	["4"] = { item = "FrontDesk", floor = 1, x = 2, z = 3, r = 0 },
	["7"] = { item = "Stairs", floor = 1, x = 0, z = 0, r = 1 },
	["9"] = { item = "NoSuchPiece", floor = 1, x = 5, z = 5, r = 0 },
}
local DECOR_MAP = {
	["11"] = { item = DECOR, floor = 1, x = 4, z = 4, r = 0, room = "" },
	["12"] = { item = DECOR, floor = 2, x = 1, z = 2, r = 2, room = "4" },
	["13"] = { item = "NoSuchDecor", floor = 1, x = 0, z = 0, r = 0, room = "" },
}

-- The same records as the state sends them: lists, each carrying its id.
local function asList(map)
	local out = {}
	for id, rec in map do
		local r = table.clone(rec)
		r.id = tonumber(id)
		table.insert(out, r)
	end
	return out
end

local function byId(list)
	local out = {}
	for _, x in list do
		out[x.id] = x
	end
	return out
end

describe("Layout", function()
	it("a profile's maps and the state's lists make the same world", function()
		local tiles = { [tostring(Grid.tileKey(1, 0, 0))] = true }
		local a = Layout.world(1, tiles, PIECES_MAP, DECOR_MAP)
		local b = Layout.world(1, tiles, asList(PIECES_MAP), asList(DECOR_MAP))
		for name, pair in { pieces = { a.pieces, b.pieces }, decor = { a.decor, b.decor } } do
			local x, y = byId(pair[1]), byId(pair[2])
			for id, p in x do
				local q = y[id]
				expect.truthy(q ~= nil, `{name} {id} in both`)
				for _, k in { "item", "floor", "x", "z", "r", "w", "d", "room" } do
					expect.eq((q :: any)[k], (p :: any)[k], `{name} {id}'s {k}`)
				end
			end
			for id in y do
				expect.truthy(x[id] ~= nil, `{name} {id} in both`)
			end
		end
	end)

	it("an unknown item is left out, and every piece takes its row's footprint and kind", function()
		local w = Layout.world(1, {}, PIECES_MAP, DECOR_MAP)
		expect.eq(#w.pieces, 2, "two known pieces")
		expect.eq(#w.decor, 2, "two known decor")
		for _, p in w.pieces do
			local row = Pieces.get(p.item) :: any
			expect.eq(p.w, row.w, `{p.item}'s width`)
			expect.eq(p.d, row.d, `{p.item}'s depth`)
			expect.eq(p.kind, row.kind, `{p.item}'s kind`)
			expect.eq(Layout.find(w, p.id), p, `{p.id} found`)
		end
		for _, d in w.decor do
			local row = Pieces.decor(d.item) :: any
			expect.eq(d.w, row.w, `{d.item}'s width`)
			expect.eq(d.layer, row.layer, `{d.item}'s layer`)
			expect.eq(Layout.findDecor(w, d.id), d, `{d.id} found`)
		end
		expect.eq(Layout.find(w, "9"), nil, "the unknown piece")
		expect.eq(Layout.findDecor(w, "13"), nil, "the unknown decor")
	end)

	it("hallway decor has no room, and a room's items are the decor in it", function()
		local w = Layout.world(1, {}, PIECES_MAP, DECOR_MAP)
		expect.eq((Layout.findDecor(w, "11") :: any).room, nil, "hallway decor")
		expect.eq((Layout.findDecor(w, "12") :: any).room, "4", "decor in room 4")
		local items = Layout.roomItems(w, "4")
		expect.eq(#items, 1, "one item in room 4")
		expect.eq(items[1], DECOR)
		expect.eq(#Layout.roomItems(w, "7"), 0, "none in another")
	end)

	it("a tile is owned only when true, whether its key is a string or a number", function()
		local k1, k2, k3 = Grid.tileKey(1, 0, 0), Grid.tileKey(1, 1, 0), Grid.tileKey(2, 3, 4)
		local w = Layout.world(
			2,
			{ [tostring(k1)] = true, [k2] = true, [tostring(k3)] = false },
			{},
			{}
		)
		expect.truthy(w.tiles[k1], "a string key")
		expect.truthy(w.tiles[k2], "a number key")
		expect.truthy(not w.tiles[k3], "a tile not owned")
		expect.eq(w.floors, 2, "its floors")
	end)

	it("built rooms' walls and rooms are found by key whether sent as maps or lists", function()
		local wall = { edge = "1:3:4:0", door = true }
		local fromMap = Layout.world(
			1,
			{},
			{},
			{},
			{ ["1:3:4:0"] = wall },
			{ ["5"] = { type = "StandardRoom" } }
		)
		local fromList = Layout.world(
			1,
			{},
			{},
			{},
			{ wall },
			{ { id = 5, type = "StandardRoom" } }
		)
		for _, w in { fromMap, fromList } do
			expect.eq(w.walls["1:3:4:0"], wall, "the wall by its edge")
			expect.truthy(w.rooms["5"] ~= nil, "the room by its id")
		end
	end)
end)
