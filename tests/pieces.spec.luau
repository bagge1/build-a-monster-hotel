local Locations = require(Shared.Locations)
local Pieces = require(Shared.Pieces)
local Species = require(Shared.Species)
local Store = require(Shared.Store)

local KINDS = { Room = true, Amenity = true, Stairs = true, Desk = true }

local function locationExists(id: number): boolean
	if id == 0 then
		return true
	end
	for _, l in Locations.List do
		if l.id == id then
			return true
		end
	end
	return false
end

local function isWhole(n: number): boolean
	return n == math.floor(n)
end

describe("Pieces", function()
	it(
		"every piece has a unique id, a positive whole footprint, a known kind and a location that exists",
		function()
			local seen = {}
			for _, p in Pieces.List do
				expect.truthy(not seen[p.id], `{p.id} once`)
				seen[p.id] = true
				expect.eq(Pieces.get(p.id), p, `{p.id} found by id`)
				expect.truthy(
					p.w >= 1 and p.d >= 1 and isWhole(p.w) and isWhole(p.d),
					`{p.id}'s footprint`
				)
				expect.truthy(KINDS[p.kind], `{p.id}'s kind {p.kind}`)
				expect.truthy(locationExists(p.location), `{p.id}'s location {p.location}`)
				expect.atLeast(p.cost, 0, `{p.id}'s cost`)
			end
			local d = {}
			for _, x in Pieces.DecorList do
				expect.truthy(not d[x.id], `decor {x.id} once`)
				d[x.id] = true
				expect.eq(Pieces.decor(x.id), x, `decor {x.id} found by id`)
				expect.truthy(locationExists(x.location), `decor {x.id}'s location {x.location}`)
				expect.atLeast(x.cost, 0, `decor {x.id}'s cost`)
			end
			local f = {}
			for _, x in Pieces.Finishes do
				expect.truthy(not f[x.id], `finish {x.id} once`)
				f[x.id] = true
				expect.truthy(locationExists(x.location), `finish {x.id}'s location`)
			end
		end
	)

	-- §5.2: an unlock is something a hotel can reach.
	it(
		"every unlock asks something reachable: rooms and floors at least 1, a rating on the 1-5 scale",
		function()
			for _, p in Pieces.List do
				local u = p.unlock
				if u then
					expect.truthy(
						u.rooms or u.floor or u.rating or u.legendaryResident,
						`{p.id}'s unlock asks something`
					)
					if u.rooms then
						expect.atLeast(u.rooms, 1, `{p.id}'s rooms`)
					end
					if u.floor then
						expect.atLeast(u.floor, 1, `{p.id}'s floor`)
					end
					if u.rating then
						expect.atLeast(u.rating, 1, `{p.id}'s rating`)
						expect.atMost(u.rating, 5, `{p.id}'s rating`)
						expect.eq((u.rating * 2) % 1, 0, `{p.id}'s rating in half stars`)
					end
				end
			end
		end
	)

	it("every playable location has a room it can build from the start", function()
		for _, l in Locations.List do
			if l.playable then
				local found = false
				for _, p in Pieces.List do
					if p.kind == "Room" and p.location == l.id and p.unlock == nil then
						found = true
					end
				end
				expect.truthy(found, `{l.name} has a starting room`)
			end
		end
	end)

	it(
		"every rare set names decor that exists, is found, is its location's and names the set back",
		function()
			local inSet = {}
			for _, s in Pieces.Sets do
				expect.eq(Pieces.SetById[s.id], s, `set {s.id} found by id`)
				expect.truthy(#s.pieces > 0, `set {s.id} has pieces`)
				for _, id in s.pieces do
					local d = Pieces.decor(id)
					expect.truthy(d ~= nil, `set {s.id}'s {id} exists`)
					local dd = d :: any
					expect.truthy(dd.found, `{id} is found, not sold`)
					expect.eq(dd.set, s.id, `{id} names its set`)
					expect.eq(dd.location, s.location, `{id}'s location`)
					expect.truthy(not inSet[id], `{id} in one set`)
					inSet[id] = true
				end
			end
			for _, d in Pieces.DecorList do
				if d.set then
					expect.truthy(inSet[d.id], `{d.id} is listed in its set {d.set}`)
				end
			end
		end
	)

	it("every key piece, furniture set, souvenir and pass names something that exists", function()
		local souvenirs = {}
		for _, d in Pieces.DecorList do
			for _, t in d.keyFor or {} do
				local p = Pieces.get(t)
				expect.truthy(
					p and (p.kind == "Room" or p.kind == "Amenity"),
					`{d.id} is key for {t}`
				)
			end
			for _, s in d.sets or {} do
				expect.truthy(Pieces.FurnitureSetById[s] ~= nil, `{d.id}'s furniture set {s}`)
			end
			if d.souvenir then
				expect.truthy(Species.get(d.souvenir) ~= nil, `{d.id}'s species`)
				expect.truthy(not souvenirs[d.souvenir], `one souvenir of {d.souvenir}`)
				souvenirs[d.souvenir] = true
			end
			if d.pass then
				local e = Store.ByKey[d.pass]
				expect.truthy(e and e.kind == "Pass", `{d.id}'s pass {d.pass}`)
			end
		end
		for _, sp in Species.List do
			expect.truthy(souvenirs[sp.id], `a souvenir of {sp.id}`)
		end
	end)

	-- A.13.3 names the Outdoor Pool, with no row yet (Pieces.luau): every other type served exists.
	it("every type a furniture set serves is a room type or amenity", function()
		for _, s in Pieces.FurnitureSets do
			for _, t in s.serves do
				local p = Pieces.get(t)
				expect.truthy(p and (p.kind == "Room" or p.kind == "Amenity"), `{s.id} serves {t}`)
			end
		end
	end)
end)
