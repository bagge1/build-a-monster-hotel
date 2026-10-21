local Species = require(Shared.Species)
local Pieces = require(Shared.Pieces)
local Mutations = require(Shared.Mutations)
local Constants = require(Shared.Constants)
local Locations = require(Shared.Locations)
local Format = require(Shared.Format)
local Net = require(Shared.Net)

describe("Data tables", function()
	it("every species needs a room that exists, of its own location, and a staff role", function()
		local roles = {
			FrontDesk = true,
			Housekeeping = true,
			RoomService = true,
			Bellhop = true,
			Entertainment = true,
			Security = true,
		}
		for _, sp in Species.List do
			local room = Pieces.get(sp.room)
			expect.truthy(room and room.kind == "Room", `{sp.id}'s room {sp.room}`)
			expect.eq((room :: any).location, sp.location, `{sp.id}'s room location`)
			expect.truthy(roles[sp.staff], `{sp.id}'s role {sp.staff}`)
			expect.truthy(Constants.Rarity[sp.rarity], `{sp.id}'s rarity`)
			expect.eq(#sp.prefs, 2, `{sp.id} has 2 preferences`)
		end
	end)

	it("every preference can be met by some decor or amenity of the species' location", function()
		for _, sp in Species.List do
			for _, pref in sp.prefs do
				local found = false
				for _, d in Pieces.DecorList do
					if d.location <= sp.location and table.find(d.tags, pref) then
						found = true
					end
				end
				for _, p in Pieces.List do
					if p.tags and p.location <= sp.location and table.find(p.tags, pref) then
						found = true
					end
				end
				expect.truthy(found, `{sp.id} wants {pref}`)
			end
		end
	end)

	it("every room type serves somebody", function()
		for _, p in Pieces.List do
			if p.kind == "Room" then
				local served = false
				for _, sp in Species.List do
					if sp.room == p.id then
						served = true
					end
				end
				expect.truthy(served, p.id)
			end
		end
	end)

	it("every playable location has a rebirth resident of its own family", function()
		for _, loc in Locations.List do
			if loc.playable then
				local sp = Species.get(loc.rebirthResident :: string)
				expect.truthy(sp and sp.location == loc.id, loc.name)
			end
		end
	end)

	it("only event mutations are never rolled", function()
		for i = 0, 999 do
			for _, m in { Mutations.rollSize(i / 1000), Mutations.rollLook(i / 1000) } do
				expect.truthy(not Mutations.ById[m].event, m)
			end
		end
		expect.eq(Mutations.rollSize(0.9999), nil, "most guests are plain")
		expect.eq(Mutations.rollLook(0.9999), nil, "most guests are plain")
	end)

	it("money is written with at most one decimal and a suffix past a thousand", function()
		for _, n in { 0, 999, 1000, 1234, 999999, 1e6, 5.6e9, 7.8e12, 9.1e15 } do
			local s = Format.number(n)
			expect.truthy(not string.find(s, "%.%d%d"), s)
			if n >= 1000 then
				expect.truthy(string.find(s, "%a") ~= nil, s)
			end
		end
	end)

	it("the remote layer drops wrong types, NaN and long strings", function()
		local def = { dir = "C2S", args = { "string", "number" } }
		expect.truthy(Net._valid(def, { "a", 1 }), "good")
		expect.truthy(not Net._valid(def, { 1, 1 }), "wrong type")
		expect.truthy(not Net._valid(def, { "a", 0 / 0 }), "NaN")
		expect.truthy(not Net._valid(def, { "a", math.huge }), "inf")
		expect.truthy(not Net._valid(def, { string.rep("x", 999), 1 }), "long")
		expect.truthy(not Net._valid(def, { "a", 1, 3 }), "extra")
	end)
end)
