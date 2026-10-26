local Constants = require(Shared.Constants)
local Locations = require(Shared.Locations)
local Pieces = require(Shared.Pieces)
local Species = require(Shared.Species)

local ROLES = {
	FrontDesk = true,
	Housekeeping = true,
	RoomService = true,
	Bellhop = true,
	Entertainment = true,
	Security = true,
}
local SHAPES = { Blob = true, Biped = true, Float = true, Quadruped = true, Serpent = true }

describe("Species", function()
	it(
		"every species has a unique id, a playable location, a known rarity, role and shape",
		function()
			local seen = {}
			for _, sp in Species.List do
				expect.truthy(not seen[sp.id], `{sp.id} once`)
				seen[sp.id] = true
				expect.eq(Species.get(sp.id), sp, `{sp.id} found by id`)
				local l = Locations.List[sp.location]
				expect.truthy(
					l and l.id == sp.location and l.playable,
					`{sp.id}'s location {sp.location}`
				)
				expect.truthy(Constants.Rarity[sp.rarity] ~= nil, `{sp.id}'s rarity`)
				expect.truthy(ROLES[sp.staff], `{sp.id}'s role {sp.staff}`)
				expect.truthy(SHAPES[sp.look.shape], `{sp.id}'s shape`)
				expect.truthy(sp.look.height > 0, `{sp.id}'s height`)
			end
		end
	)

	-- §5.2, A.6: a species stays in a room type of its own location.
	it("every species' room is a room in Pieces, of its own location", function()
		for _, sp in Species.List do
			local room = Pieces.get(sp.room)
			expect.truthy(room and room.kind == "Room", `{sp.id}'s room {sp.room}`)
			expect.eq((room :: any).location, sp.location, `{sp.id}'s room's location`)
		end
	end)

	it("every species has distinct preferences, each one some decor or amenity gives", function()
		local given = {}
		for _, d in Pieces.DecorList do
			for _, t in d.tags do
				given[t] = true
			end
		end
		for _, p in Pieces.List do
			for _, t in p.tags or {} do
				given[t] = true
			end
		end
		for _, sp in Species.List do
			expect.truthy(#sp.prefs > 0, `{sp.id} has preferences`)
			local seen = {}
			for _, pref in sp.prefs do
				expect.truthy(not seen[pref], `{sp.id} wants {pref} once`)
				seen[pref] = true
				expect.truthy(given[pref], `{sp.id}'s {pref} is given by something`)
			end
		end
	end)

	it(
		"a location's family is its species in roster order, and every playable location has one",
		function()
			local total = 0
			for _, l in Locations.List do
				local family = Species.ofLocation(l.id)
				total += #family
				local lastIndex = 0
				for _, sp in family do
					expect.eq(sp.location, l.id, `{sp.id} in {l.name}`)
					local index = table.find(Species.List, sp) :: number
					expect.truthy(index > lastIndex, `{sp.id} in roster order`)
					lastIndex = index
				end
				if l.playable then
					expect.truthy(#family > 0, `{l.name} has a family`)
				end
			end
			expect.eq(total, #Species.List, "every species in one family")
		end
	)
end)
