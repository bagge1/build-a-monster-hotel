local Locations = require(Shared.Locations)

describe("Locations", function()
	it("every location's id is its place in the list, and its name is its own", function()
		local names = {}
		for i, l in Locations.List do
			expect.eq(l.id, i, `{l.name}'s id`)
			expect.eq(Locations.get(i), l, `{l.name} found by id`)
			expect.truthy(not names[l.name], `{l.name} once`)
			names[l.name] = true
		end
	end)

	-- §6.4: the chain opens in order (Haunted Manor → Frostfang Lodge → Bayou Spa); later ones are a preview.
	it(
		"the playable locations come first, the first is playable, and the last is the chain's end",
		function()
			expect.truthy(Locations.List[1].playable, "the first location is playable")
			local ended = false
			for _, l in Locations.List do
				if not l.playable then
					ended = true
				end
				expect.truthy(not (ended and l.playable), `{l.name} playable after a preview`)
			end
			local last = Locations.last()
			expect.truthy(Locations.get(last).playable, "the last is playable")
			local next = Locations.List[last + 1]
			expect.truthy(next == nil or not next.playable, "nothing playable past it")
		end
	)

	it("an unknown location reads as the first, never nil", function()
		for _, id in { 0, -1, #Locations.List + 1, 99 } do
			expect.eq(Locations.get(id), Locations.List[1], `location {id}`)
		end
	end)
end)
