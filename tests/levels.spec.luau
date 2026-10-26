local Constants = require(Shared.Constants)
local ResidentLevels = require(Shared.ResidentLevels)

describe("Residents level up (A.11.6)", function()
	local cap = Constants.Residents.LevelCap

	it("a record without a level is level 1 with no XP, and never past the cap", function()
		expect.eq(ResidentLevels.level({}), 1)
		expect.eq(ResidentLevels.xp({}), 0)
		expect.eq(ResidentLevels.level({ level = cap + 5 }), cap)
	end)

	it("each bar is longer than the last, and there is none at the cap", function()
		for l = 2, cap - 1 do
			expect.truthy(ResidentLevels.need(l) > ResidentLevels.need(l - 1), `bar {l}`)
		end
		expect.eq(ResidentLevels.need(cap), 0)
	end)

	it("XP fills the bar and stops there; none at the cap", function()
		local need = ResidentLevels.need(1)
		local xp = ResidentLevels.gain(1, 0, 60)
		expect.truthy(xp > 0, "a minute at work gives XP")
		expect.eq(ResidentLevels.gain(1, 0, 1e9), need)
		expect.truthy(ResidentLevels.ready(1, need), "a full bar is ready")
		expect.truthy(not ResidentLevels.ready(1, need - 0.01), "not before")
		expect.eq(ResidentLevels.gain(cap, 0, 1e9), 0)
		expect.truthy(not ResidentLevels.ready(cap, 1e9), "nothing past the cap")
	end)

	it("a level never lowers Wing earnings or efficiency, and level 1 changes nothing", function()
		expect.eq(ResidentLevels.wing(1), 1)
		expect.eq(ResidentLevels.efficiency(1), 1)
		for l = 2, cap do
			expect.truthy(ResidentLevels.wing(l) > ResidentLevels.wing(l - 1), `wing {l}`)
			expect.truthy(
				ResidentLevels.efficiency(l) > ResidentLevels.efficiency(l - 1),
				`eff {l}`
			)
		end
	end)

	it("the price is in the resident's own Wing rate and each level pays back slower", function()
		local rate = 2
		expect.eq(
			ResidentLevels.price(1, rate * 3),
			math.ceil(ResidentLevels.price(1, rate) * 3 - 1e-6) // 1
		)
		local last = 0
		for l = 1, cap - 1 do
			local gain = rate * (ResidentLevels.wing(l + 1) - ResidentLevels.wing(l))
			local payback = ResidentLevels.price(l, rate) / gain
			expect.truthy(payback > last, `payback {l}`)
			last = payback
		end
	end)

	-- WAITING §2.48 (his yes 2026-10-26): A.11.6's "the same rate in the Wing and at a staff post".
	it("a resident learns in the Wing and on staff at any hotel of the chain, not in the Hunter Camp", function()
		local now = 1e6
		expect.truthy(ResidentLevels.learning({ role = "", campUntil = 0 }, now), "in the Wing")
		expect.truthy(ResidentLevels.learning({ role = "FrontDesk", hotel = 1, campUntil = 0 }, now), "on staff")
		expect.truthy(
			ResidentLevels.learning({ role = "Housekeeping", hotel = 2, campUntil = 0 }, now),
			"on staff at a hotel not played"
		)
		expect.truthy(not ResidentLevels.learning({ role = "", campUntil = now + 60 }, now), "not in the Hunter Camp")
	end)
end)
