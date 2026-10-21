local Constants = require(Shared.Constants)
local Economy = require(Shared.Economy)
local Events = require(Shared.Events)
local Mutations = require(Shared.Mutations)

-- 2026-03-16, 2026-08-03 and 2026-10-19 (Mondays: a month with a mutation, none, Halloween), noon UTC.
local MARCH = 1773662400
local AUGUST = 1785758400
local HALLOWEEN = 1792411200

describe("Deeper mutations (A.11.5)", function()
	it("every mutation is a size or a look; sizes only scale, looks never scale", function()
		for _, m in Mutations.List do
			expect.truthy(m.group == "Size" or m.group == "Look", m.id)
			if m.group == "Size" then
				expect.truthy(m.scale ~= 1 and not m.colour and not m.event, m.id)
			else
				expect.eq(m.scale, 1, m.id)
			end
		end
	end)

	it("the size roll gives a size and the look roll a look, independently", function()
		for i = 0, 999 do
			local s = Mutations.rollSize(i / 1000)
			local l = Mutations.rollLook(i / 1000)
			expect.truthy(s == nil or Mutations.ById[s].group == "Size", `size {i}`)
			expect.truthy(l == nil or Mutations.ById[l].group == "Look", `look {i}`)
		end
		local size, look = Events.rollMutations(0, 0, AUGUST)
		expect.truthy(size ~= nil and look ~= nil, "both at once: a stack can happen")
	end)

	it("stacked pay is added, never multiplied, and never less than either alone", function()
		for _, s in Mutations.List do
			for _, l in Mutations.List do
				if s.group == "Size" and l.group == "Look" then
					local both = Mutations.payMultiplier(s.id, l.id)
					expect.near(both, s.pay + l.pay - 1, 1e-9, `{s.id} {l.id}`)
					expect.truthy(both >= Mutations.payMultiplier(s.id, nil), "over the size")
					expect.truthy(both >= Mutations.payMultiplier(nil, l.id), "over the look")
				end
			end
		end
		expect.eq(Mutations.payMultiplier(nil, nil), 1)
		expect.eq(
			Economy.residentPay("Slime", "Golden", 1, "Giant"),
			Economy.residentPay("Slime", nil, 1) * Mutations.payMultiplier("Giant", "Golden")
		)
	end)

	it("the month's mutation is a row of the look table in its month only", function()
		expect.eq(Events.monthly(MARCH), Constants.Mutations.Monthly[3])
		expect.eq(Events.monthly(AUGUST), nil)
		local monthly, plain = 0, {}
		for i = 0, 999 do
			local l = Events.rollMutation(i / 1000, MARCH)
			if l == Constants.Mutations.Monthly[3] then
				monthly += 1
			elseif l then
				plain[l] = true
			end
			local a = Events.rollMutation(i / 1000, AUGUST)
			expect.truthy(a == nil or not Mutations.ById[a].event, `august {i}`)
		end
		expect.truthy(monthly > 0, "the month's comes in its month")
		for _, id in { "Shadow", "Golden" } do
			expect.truthy(plain[id], `{id} still comes in the month`)
		end
		local h = Events.rollMutation(0, HALLOWEEN)
		expect.eq(h, "Pumpkin")
	end)

	it("every month's mutation is a seasonal look with no set title", function()
		for month, id in Constants.Mutations.Monthly do
			local m = Mutations.ById[id]
			expect.truthy(m and m.event and m.group == "Look" and m.month == month, id)
			expect.truthy(table.find(Mutations.Seasonal, m), `{id} in the Seasons row`)
			expect.truthy(not table.find(Mutations.Rollable, m), `{id} not in the set`)
		end
	end)

	it("a stack's words name the size first", function()
		expect.eq(Mutations.prefix("Giant", "Golden"), "Giant Golden ")
		expect.eq(Mutations.prefix(nil, "Golden"), "Golden ")
		expect.eq(Mutations.prefix(nil, nil), "")
	end)
end)
