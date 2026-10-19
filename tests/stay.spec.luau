local Stay = require(Shared.Stay)
local Constants = require(Shared.Constants)

local function inputs(over)
	local i = {
		prefsMatched = 0,
		tier = 1,
		amenities = 0,
		requestsPlayer = 0,
		requestsStaff = 0,
		requestsMissed = 0,
		deskWait = 0,
	}
	for k, v in over or {} do
		i[k] = v
	end
	return i
end

describe("Stay", function()
	it("satisfaction stays within 0 and 100", function()
		expect.atMost(
			Stay.satisfaction(
				inputs({ prefsMatched = 2, tier = 5, amenities = 9, requestsPlayer = 5 })
			),
			100
		)
		expect.atLeast(Stay.satisfaction(inputs({ requestsMissed = 9, deskWait = 9999 })), 0)
	end)

	it("a matched preference, a tier, an amenity or a fulfilled request never lowers it", function()
		local base = Stay.satisfaction(inputs())
		for _, over in
			{
				{ prefsMatched = 1 },
				{ tier = 2 },
				{ amenities = 1 },
				{ requestsPlayer = 1 },
				{ requestsStaff = 1 },
			}
		do
			expect.atLeast(Stay.satisfaction(inputs(over)), base)
		end
	end)

	it("the player fulfilling a request pleases at least as much as staff", function()
		expect.atLeast(
			Stay.satisfaction(inputs({ requestsPlayer = 1 })),
			Stay.satisfaction(inputs({ requestsStaff = 1 }))
		)
	end)

	it("waiting longer and missing requests never raise it", function()
		local prev = 101
		for wait = 0, 300, 5 do
			local s = Stay.satisfaction(inputs({ prefsMatched = 2, deskWait = wait }))
			expect.atMost(s, prev, `wait {wait}`)
			prev = s
		end
		expect.atMost(
			Stay.satisfaction(inputs({ requestsMissed = 1 })),
			Stay.satisfaction(inputs())
		)
	end)

	it("reviews are 1-5 and never fall as satisfaction rises", function()
		local prev = 0
		for s = 0, 100 do
			local r = Stay.review(s)
			expect.atLeast(r, 1)
			expect.atMost(r, 5)
			expect.atLeast(r, prev)
			prev = r
		end
	end)

	it("a happier guest tips at least as much, and nobody tips less than nothing", function()
		local prev = -1
		for s = 0, 100, 10 do
			local t = Stay.tip(5, 90, s)
			expect.atLeast(t, 0)
			expect.atLeast(t, prev)
			prev = t
		end
	end)

	it("happy means at or above the threshold", function()
		expect.truthy(Stay.isHappy(Constants.Stay.Happy))
		expect.truthy(not Stay.isHappy(Constants.Stay.Happy - 1))
	end)

	it("matching counts each preference once", function()
		expect.eq(
			Stay.matched({ "damp", "snacks" }, { damp = true, snacks = true, music = true }),
			2
		)
		expect.eq(Stay.matched({ "damp", "snacks" }, {}), 0)
	end)
end)
