local Scoring = require(Shared.Scoring)

local function cand(over)
	local c = {
		id = 1,
		eligible = true,
		rating = 3,
		prefsMatched = 1,
		amenityBonus = 1,
		pitched = false,
		distance = 10,
	}
	for k, v in over or {} do
		c[k] = v
	end
	return c
end

describe("Scoring", function()
	it("an ineligible hotel is never picked", function()
		local a = cand({ id = "a", eligible = false, rating = 5, prefsMatched = 2 })
		local b = cand({ id = "b", rating = 1, prefsMatched = 0 })
		expect.eq((Scoring.pick({ a, b }, "Rare", { 1, 1 }) :: any).id, "b")
		expect.eq(Scoring.pick({ a }, "Rare", { 1 }), nil, "nobody eligible")
	end)

	it(
		"a pitch, a better rating, a matched preference or an amenity never lowers a score",
		function()
			local base = Scoring.score(cand(), "Rare", 1)
			for _, over in
				{
					{ pitched = true },
					{ rating = 4 },
					{ prefsMatched = 2 },
					{ amenityBonus = 3 },
					{ busBonus = 0.1 },
				}
			do
				expect.atLeast(Scoring.score(cand(over), "Rare", 1), base)
			end
		end
	)

	it("the newcomer boost helps only Common and Uncommon guests", function()
		local low = cand({ rating = 1 })
		expect.truthy(
			Scoring.score(low, "Common", 1) > Scoring.score(low, "Rare", 1),
			"Common boosted"
		)
		expect.truthy(
			Scoring.score(low, "Uncommon", 1) > Scoring.score(low, "Epic", 1),
			"Uncommon boosted"
		)
		expect.eq(
			Scoring.score(low, "Legendary", 1),
			Scoring.score(low, "Mythic", 1),
			"rares never"
		)
	end)

	it(
		"the tutorial's weight helps only a Common, toward its hotel, never an ineligible one",
		function()
			local plain = cand()
			local brought = cand({ tutorial = true })
			expect.truthy(
				Scoring.score(brought, "Common", 1) > Scoring.score(plain, "Common", 1),
				"a Common weighted toward the hotel it came for"
			)
			for _, rarity in { "Uncommon", "Rare", "Epic", "Legendary", "Mythic" } do
				expect.eq(
					Scoring.score(brought, rarity, 1),
					Scoring.score(plain, rarity, 1),
					`never a {rarity}`
				)
			end
			local shut = cand({ id = "new", eligible = false, tutorial = true, rating = 1 })
			local other = cand({ id = "other", rating = 1, prefsMatched = 0 })
			expect.eq((Scoring.pick({ shut, other }, "Common", { 1, 1 }) :: any).id, "other")
			local pitched = cand({ tutorial = true, pitched = true })
			expect.atLeast(
				Scoring.score(pitched, "Common", 1),
				Scoring.score(brought, "Common", 1),
				"a pitch still counts on top"
			)
		end
	)

	it("ties go to the nearest", function()
		local far = cand({ id = "far", distance = 50 })
		local near = cand({ id = "near", distance = 5 })
		expect.eq((Scoring.pick({ far, near }, "Rare", { 1, 1 }) :: any).id, "near")
	end)

	it("the jitter stays within its bounds", function()
		expect.near(Scoring.jitter(0), 0.9, 1e-9)
		expect.atMost(Scoring.jitter(0.9999), 1.1)
	end)
end)
