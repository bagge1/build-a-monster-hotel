local MoonTree = require(Shared.MoonTree)

describe("MoonTree", function()
	it("every node has a unique id, at least one level and a positive base cost", function()
		local seen = {}
		for _, n in MoonTree.Nodes do
			expect.truthy(not seen[n.id], `{n.id} once`)
			seen[n.id] = true
			expect.eq(MoonTree.ById[n.id], n, `{n.id} found by id`)
			expect.atLeast(n.levels, 1, `{n.id}'s levels`)
			expect.truthy(n.baseCost > 0, `{n.id}'s base cost`)
			expect.truthy(n.per > 0, `{n.id} gives something per level`)
		end
	end)

	it(
		"a node's next level always has a price, never falls with its level, and none at the top",
		function()
			for _, n in MoonTree.Nodes do
				local last = 0
				for level = 0, n.levels - 1 do
					local c = MoonTree.cost(n.id, level)
					expect.truthy(c ~= nil, `{n.id} level {level} has a price`)
					expect.truthy((c :: number) > 0, `{n.id} level {level} is not free`)
					expect.atLeast(c :: number, last, `{n.id} level {level}`)
					last = c :: number
				end
				expect.eq(MoonTree.cost(n.id, n.levels), nil, `{n.id} at the top`)
				expect.eq(MoonTree.cost(n.id, n.levels + 3), nil, `{n.id} past the top`)
			end
			expect.eq(MoonTree.cost("NoSuchNode", 0), nil, "an unknown node")
		end
	)

	it("a level never gives less, nothing at level 0, and nothing past the top", function()
		for _, n in MoonTree.Nodes do
			expect.eq(MoonTree.effect(n.id, 0), 0, `{n.id} at 0`)
			expect.eq(MoonTree.effect(n.id, -2), 0, `{n.id} below 0`)
			local last = 0
			for level = 1, n.levels do
				local e = MoonTree.effect(n.id, level)
				expect.truthy(e > last, `{n.id} level {level} gives more`)
				last = e
			end
			expect.eq(MoonTree.effect(n.id, n.levels + 5), last, `{n.id} capped at its top`)
		end
		expect.eq(MoonTree.effect("NoSuchNode", 3), 0, "an unknown node")
	end)

	-- §6.5: "no levels beyond +1 h, so the Night Manager pass stays meaningful".
	it("the offline node never adds more than an hour", function()
		local n = MoonTree.ById.Offline
		expect.truthy(n ~= nil, "an offline node")
		expect.atMost(MoonTree.effect("Offline", 999), 3600, "its top")
	end)
end)
