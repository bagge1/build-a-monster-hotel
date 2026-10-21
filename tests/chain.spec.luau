local Chain = require(Shared.Chain)
local Constants = require(Shared.Constants)

describe("Chain", function()
	it("opens the locations in order, and the first is never bought", function()
		expect.eq(Chain.nextToOpen({}), 1, "nothing opened")
		expect.eq(Chain.nextToOpen({ [1] = true }), 2, "after the first")
		expect.eq(Chain.nextToOpen({ [1] = true, [2] = true }), 3, "after the second")
		local all = {}
		for id = 1, Constants.Chain.Locations do
			all[id] = true
		end
		expect.eq(Chain.nextToOpen(all), nil, "the chain is whole")
		expect.eq(Chain.openCost(1), nil, "the first location")
	end)

	it("each next location costs more to open than the one before", function()
		for id = 3, Constants.Chain.Locations do
			expect.truthy((Chain.openCost(id) :: number) > (Chain.openCost(id - 1) :: number), id)
		end
	end)

	it("odd rebirths unlock a floor until the cap, even ones never do", function()
		expect.eq(Chain.floorCap(0), Constants.Chain.StartFloorCap, "before any rebirth")
		for n = 1, 30 do
			local gained = Chain.floorCap(n) - Chain.floorCap(n - 1)
			if n % 2 == 0 then
				expect.eq(gained, 0, `rebirth {n}`)
			else
				expect.truthy(gained == 1 or Chain.floorCap(n - 1) == Constants.Chain.FloorCapMax, `rebirth {n}`)
			end
			expect.truthy(Chain.floorCap(n) <= Constants.Chain.FloorCapMax, `cap at {n}`)
		end
	end)

	it("a rebirth gives either a floor or a Prestige Star, and even ones always a star", function()
		for n = 1, 30 do
			local floor = Chain.floorCap(n) > Chain.floorCap(n - 1)
			expect.truthy(floor ~= Chain.givesPrestige(n), `rebirth {n}`)
			if n % 2 == 0 then
				expect.truthy(Chain.givesPrestige(n), `even {n}`)
			end
		end
		expect.eq(Chain.prestige(0), 0, "none before a rebirth")
		for n = 1, 30 do
			expect.truthy(Chain.prestige(n) >= Chain.prestige(n - 1), `never fewer at {n}`)
		end
	end)

	it("Prestige Stars never lower income or rarity, and stop adding past their cap", function()
		local cap = Constants.Chain.PrestigeEffectCap
		for s = 1, cap + 5 do
			expect.truthy(Chain.prestigeIncome(s) >= Chain.prestigeIncome(s - 1), `income {s}`)
			expect.truthy(Chain.prestigeRarity(s) >= Chain.prestigeRarity(s - 1), `rarity {s}`)
		end
		expect.eq(Chain.prestigeIncome(cap + 5), Chain.prestigeIncome(cap), "income past the cap")
	end)

	it("rebirth needs every hotel of the chain at the rating, none missing", function()
		local R = Constants.Chain.RebirthRating
		local full = {}
		for id = 1, Constants.Chain.Locations do
			full[id] = R
		end
		expect.truthy(Chain.rebirthReady(full), "all at the rating")
		local short = table.clone(full)
		short[Constants.Chain.Locations] = nil
		expect.truthy(not Chain.rebirthReady(short), "the last not opened")
		local low = table.clone(full)
		low[1] = R - 0.5
		expect.truthy(not Chain.rebirthReady(low), "one below")
	end)

	it("a hotel not played earns less than when played, and nothing at no rate", function()
		expect.truthy(Chain.background(10, 60) < 10 * 60, "a share")
		expect.truthy(Chain.background(10, 60) > 0, "something")
		expect.eq(Chain.background(0, 60), 0, "no rate")
		expect.eq(Chain.background(0 / 0, 60), 0, "NaN")
	end)

	it("the measured rate moves toward what is earned and never past it", function()
		local r = Chain.updateRate(0, 600, 60) -- $10/s for a minute
		expect.truthy(r > 0 and r < 10, "toward 10 from 0")
		local steady = 10
		for _ = 1, 200 do
			steady = Chain.updateRate(steady, 600, 60)
		end
		expect.near(steady, 10, 1e-6, "steady")
		expect.eq(Chain.updateRate(5, 100, 0), 5, "no time")
	end)
end)
