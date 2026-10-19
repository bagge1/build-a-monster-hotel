local Events = require(Shared.Events)
local Constants = require(Shared.Constants)
local Mutations = require(Shared.Mutations)

-- 2026-10-19 (a Monday in Halloween) and 2026-08-03 (a Monday in no season), noon UTC.
local HALLOWEEN = 1792411200
local SUMMER = 1785758400

describe("Events", function()
	it("a season's mutation is rolled only in its season", function()
		for i = 0, 999 do
			local r = i / 1000
			local m = Events.rollMutation(r, SUMMER)
			expect.truthy(m == nil or not Mutations.ById[m].event, `summer roll {r}`)
		end
		local pumpkins = 0
		for i = 0, 999 do
			if Events.rollMutation(i / 1000, HALLOWEEN) == "Pumpkin" then
				pumpkins += 1
			end
		end
		expect.truthy(pumpkins > 0, "Pumpkins at Halloween")
	end)

	it("outside a season the usual mutations keep their odds", function()
		for i = 0, 999 do
			expect.eq(Events.rollMutation(i / 1000, SUMMER), Mutations.roll(i / 1000), `roll {i}`)
		end
	end)

	it("an event never makes a rarity rarer than the GDD's weights", function()
		for day = 0, 6 do
			for hour = 0, 23 do
				local t = SUMMER + day * 86400 + (hour - 12) * 3600
				local w = Events.weights(t)
				for _, id in { "Rare", "Epic", "Legendary" } do
					expect.atLeast(
						w[id],
						Constants.Rarity[id].weight,
						`{id} at day {day} hour {hour}`
					)
				end
				expect.eq(w.Mythic, 0, "Mythic stays scheduled only")
			end
		end
	end)

	it("the Parade and the Hunt each happen once a week, on their own days", function()
		local parades, hunts = 0, 0
		local lastP, lastH = nil, nil
		for hour = 0, 7 * 24 - 1 do
			local t = SUMMER + hour * 3600
			local p = Events.paradeStart(t)
			if p and p ~= lastP then
				parades += 1
				lastP = p
			end
			local h = Events.huntStart(t)
			if h and h ~= lastH then
				hunts += 1
				lastH = h
			end
		end
		expect.eq(parades, 1, "parades a week")
		expect.eq(hunts, 1, "hunts a week")
	end)
end)
