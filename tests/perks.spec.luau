local Perks = require(Shared.Perks)
local Species = require(Shared.Species)

describe("Perks", function()
	it("every species gives a perk", function()
		for _, sp in Species.List do
			expect.truthy(Perks.BySpecies[sp.id], sp.id)
		end
	end)

	it("perks of a kind add up, and a resident away in the Hunter Camp gives none", function()
		local now = 1000
		local two = { { species = "Ghost", campUntil = 0 }, { species = "Ghost", campUntil = 0 } }
		local one = Perks.total({ { species = "Ghost", campUntil = 0 } }, "Cleanliness", now)
		expect.near(Perks.total(two, "Cleanliness", now), 2 * one, 1e-9, "two Ghosts")
		expect.eq(
			Perks.total({ { species = "Ghost", campUntil = now + 60 } }, "Cleanliness", now),
			0,
			"away"
		)
		expect.eq(Perks.total(two, "Income", now), 0, "another kind")
	end)
end)
