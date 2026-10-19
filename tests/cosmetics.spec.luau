local Cosmetics = require(Shared.Cosmetics)
local Events = require(Shared.Events)
local Store = require(Shared.Store)

describe("Cosmetics", function()
	it("every cosmetic is named Cosmetic_<Id> and goes in a known slot", function()
		for _, c in Cosmetics.List do
			expect.truthy(string.match(c.id, "^Cosmetic_%w+$"), `{c.id} name`)
			expect.truthy(table.find(Cosmetics.Slots, c.slot), `{c.id} slot {c.slot}`)
		end
	end)

	it("a facade cosmetic carries its colours", function()
		for _, c in Cosmetics.List do
			if c.slot == "Facade" then
				expect.truthy(c.trim, `{c.id} trim`)
			end
		end
	end)

	it("every cosmetic an event shop sells can be worn", function()
		for id, shop in Events.Shops do
			for _, item in shop do
				if string.match(item.key, "^Cosmetic_") then
					expect.truthy(Cosmetics.get(item.key), `{id}: {item.key}`)
				end
			end
		end
	end)

	it("the built families' cosmetics can be worn", function()
		expect.truthy(Cosmetics.get(Cosmetics.family(1)), "Haunted Manor")
		expect.truthy(Cosmetics.get(Cosmetics.family(2)), "Frostfang")
	end)

	it("a cosmetic sold as a pass names a pass in the Store, and the pass is worn", function()
		for _, c in Cosmetics.List do
			if c.pass then
				local e = Store.ByKey[c.pass]
				expect.truthy(e and e.kind == "Pass", `{c.id} pass {c.pass}`)
				expect.truthy(
					Cosmetics.owns({ cosmetics = {}, passes = { [c.pass] = true } }, c.id),
					`{c.id} owned by its pass`
				)
				expect.truthy(
					not Cosmetics.owns({ cosmetics = {}, passes = {} }, c.id),
					`{c.id} not owned without it`
				)
			end
		end
	end)
end)
