-- Rare decor sets and souvenirs (GDD A.11.3): the rolls, the pity, souvenirs and the set bonus.
-- Rules only: every number is Constants.Finds (PLACEHOLDER).
local Constants = require(Shared.Constants)
local Finds = require(Shared.Finds)
local Grid = require(Shared.Grid)
local Pieces = require(Shared.Pieces)
local Rooms = require(Shared.Rooms)
local Species = require(Shared.Species)

local F = Constants.Finds

describe("Rare decor finds (A.11.3)", function()
	local function always(v: number): () -> number
		return function()
			return v
		end
	end
	local miss = always(0.999999)
	local hit = always(0)

	-- A location with a set, and one without (or nil when every location has one).
	local withSet = Pieces.Sets[1].location
	local without: number? = nil
	for loc = 1, Constants.Chain.Locations do
		if #Finds.pool(loc) == 0 then
			without = loc
			break
		end
	end

	it(
		"every set piece is a found decor row of its set's location, never sold in the shop",
		function()
			for _, s in Pieces.Sets do
				expect.truthy(#s.pieces > 0, `{s.id} has pieces`)
				for _, id in s.pieces do
					local d = Pieces.decor(id)
					expect.truthy(d ~= nil, `{id} is a decor row`)
					if d then
						expect.truthy(d.found == true and d.set == s.id, `{id} found and in {s.id}`)
						expect.eq(d.location, s.location, `{id}'s location`)
						expect.truthy(
							not d.furniture and not d.keyFor,
							`{id} is decor, not furniture`
						)
						expect.truthy(
							not Pieces.decorHere(d, s.location, {}, {}),
							`{id} not placeable before it is found`
						)
						expect.truthy(
							Pieces.decorHere(d, s.location, {}, { [id] = 1 }),
							`{id} placeable once found`
						)
					end
				end
			end
		end
	)

	it(
		"every species has one souvenir, placeable at any hotel once found and not before",
		function()
			for _, sp in Species.List do
				local d = Pieces.decor(Finds.souvenirId(sp.id))
				expect.truthy(
					d ~= nil and d.found == true and d.souvenir == sp.id,
					`{sp.id}'s souvenir`
				)
				if d then
					for loc = 1, Constants.Chain.Locations do
						expect.truthy(not Pieces.decorHere(d, loc, {}, {}), "not before")
						expect.truthy(
							Pieces.decorHere(d, loc, {}, { [d.id] = 1 }),
							"at every hotel"
						)
					end
				end
			end
		end
	)

	it("a roll never finds a piece already found, nor one of another location", function()
		local rng = Random.new(1021)
		local function rand(): number
			return rng:NextNumber()
		end
		local pool = Finds.pool(withSet)
		local rec = Finds.newRecord()
		local seen = {}
		for _ = 1, 2000 do
			local before = table.clone(rec.found)
			local out, id = Finds.roll(rec, withSet, 0.3, rand, 1)
			if out == "Piece" then
				expect.truthy(id ~= nil and before[id :: string] == nil, "a new piece")
				expect.truthy(table.find(pool, id :: string) ~= nil, "of the location")
				seen[id :: string] = true
			elseif out == "Duplicate" then
				expect.truthy(
					#Finds.unfound(rec, withSet) == 0,
					"a duplicate only when all are found"
				)
			end
		end
		for _, id in pool do
			expect.truthy(seen[id], `{id} found in the end`)
		end
	end)

	it(
		"the pity gives the next unfound piece after its run of misses, and a hit resets the run",
		function()
			local rec = Finds.newRecord()
			local order = Finds.unfound(rec, withSet)
			for i, want in order do
				for n = 1, F.Pity do
					local out = Finds.roll(rec, withSet, F.StayChance, miss, 1)
					expect.eq(out, "Miss", `roll {n} before piece {i}`)
				end
				local out, id = Finds.roll(rec, withSet, F.StayChance, miss, 1)
				expect.eq(out, "Piece", `the pity's roll for piece {i}`)
				expect.eq(id, want, "the next unfound piece")
				expect.eq(rec.misses[tostring(withSet)], 0, "the run starts again")
			end
			local out = Finds.roll(rec, withSet, F.StayChance, hit, 1)
			expect.eq(out, "Duplicate", "a hit once all are found")
			local rec2 = Finds.newRecord()
			Finds.roll(rec2, withSet, F.StayChance, miss, 1)
			Finds.roll(rec2, withSet, F.StayChance, hit, 1)
			expect.eq(rec2.misses[tostring(withSet)], 0, "a hit resets the run")
		end
	)

	it("a location without a set rolls nothing and counts no miss", function()
		if not without then
			return
		end
		local rec = Finds.newRecord()
		local out = Finds.roll(rec, without :: number, 1, hit, 1)
		expect.eq(out, "None")
		expect.truthy(rec.misses[tostring(without)] == nil, "no miss counted")
	end)

	it("only guests of the minimum rarity or rarer roll", function()
		local min = table.find(Constants.RarityOrder, F.MinRarity :: any) :: number
		for i, r in Constants.RarityOrder do
			expect.eq(Finds.rolls(r), i >= min, r)
		end
	end)

	it(
		"a souvenir comes once, by the move-in milestone or a first contract, whichever first",
		function()
			local sp = Species.List[1].id
			local rec = Finds.newRecord()
			for n = 1, F.SouvenirMoveIns - 1 do
				expect.truthy(not Finds.moveIn(rec, sp, 1), `move-in {n}`)
			end
			expect.truthy(Finds.moveIn(rec, sp, 1), "the milestone's move-in")
			expect.truthy(not Finds.moveIn(rec, sp, 1), "not again")
			expect.truthy(
				not Finds.giveSouvenir(rec, sp, 1),
				"a contract after it gives nothing new"
			)
			local rec2 = Finds.newRecord()
			expect.truthy(Finds.giveSouvenir(rec2, sp, 1), "a first contract")
			for _ = 1, F.SouvenirMoveIns + 2 do
				expect.truthy(not Finds.moveIn(rec2, sp, 1), "no second souvenir by move-ins")
			end
			expect.truthy(
				not Finds.giveSouvenir(rec2, "NoSuchSpecies", 1),
				"no souvenir for no species"
			)
		end
	)

	it(
		"the set bonus counts once per set per hotel, in the oldest room holding the whole set",
		function()
			local s = Pieces.Sets[1]
			local whole = table.clone(s.pieces)
			local part = table.clone(s.pieces)
			table.remove(part)
			local doubled = table.clone(whole)
			for _, id in s.pieces do
				table.insert(doubled, id)
			end
			local b = Finds.bonusRooms({ ["9"] = whole, ["10"] = doubled, ["3"] = part })
			expect.eq(b[s.id], "9", "the oldest room holding all of it (by number)")
			local n = 0
			for _ in b do
				n += 1
			end
			expect.eq(n, 1, "one room per set")
			expect.eq(#Finds.complete(part), 0, "four of five is no set")
			expect.eq(#Finds.complete(doubled), 1, "two copies in one room are one set")
			for _, v in { 0, 0.3, 0.9, 1 } do
				expect.atLeast(Finds.withBonus(v, 1), v, "never lowers the bar")
				expect.atMost(Finds.withBonus(v, 1), 1, "never past full")
			end
		end
	)

	it("a room's Decor bar carries the bonus for a whole set and not for part of one", function()
		local S = Constants.Rooms.Start
		local tiles = {}
		for _, c in Grid.startTiles() do
			tiles[Grid.tileKey(1, c.x, c.z)] = true
		end
		local walls = {}
		for _, w in S.walls do
			for _, e in Rooms.cellEdges(1, w[1], w[2], w[3]) do
				walls[e] = { paid = 0 }
			end
		end
		walls[Rooms.edgeKey(1, S.door.hx, S.door.hz, S.door.o)] = { door = true, paid = 0 }
		local function world(items: { string })
			local list = {}
			-- Along the room's back row of cells (z squares 12..15), each piece after the last.
			local x = 16
			for i, id in items do
				local d = Pieces.decor(id) :: any
				table.insert(list, {
					item = id,
					layer = d.layer,
					floor = 1,
					x = x,
					z = if d.layer == "Wall" then 15 else 12,
					r = 0,
					w = d.w,
					d = d.d,
					id = tostring(100 + i),
				})
				x += d.w
			end
			return {
				floors = 1,
				tiles = tiles,
				pieces = {},
				decor = list,
				walls = walls,
				rooms = { ["2"] = { type = S.type, floor = 1, hx = S.seed.hx, hz = S.seed.hz } },
			}
		end
		local s = Pieces.Sets[1]
		local part = table.clone(s.pieces)
		table.remove(part)
		local barsPart = Rooms.bars(world(part) :: any, "2")
		local barsWhole = Rooms.bars(world(s.pieces) :: any, "2")
		expect.truthy(barsPart.sets == nil, "no bonus for part of a set")
		expect.truthy(
			barsWhole.sets ~= nil
				and #(barsWhole.sets :: any) == 1
				and (barsWhole.sets :: any)[1] == s.id,
			"the whole set's bonus"
		)
		expect.atLeast(
			barsWhole.decor,
			math.min(1, barsPart.decor + F.SetBonus) - 1e-9,
			"the bonus on top of the pieces' points"
		)
	end)
end)
