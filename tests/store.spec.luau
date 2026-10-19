-- The store's catalog (GDD §10): rules that hold whatever the prices become.
local Store = require(Shared.Store)

describe("Store", function()
	it("every pass has exactly one gift product, at the pass's price (§10.1 point 4)", function()
		for _, e in Store.Entries do
			if e.kind == "Pass" then
				local g = Store.ByKey[`Gift_{e.key}`]
				expect.truthy(g, `a gift for {e.key}`)
				expect.eq(g.kind, "Product", `{g.key} kind`)
				expect.eq(g.gift, e.key, `{g.key} gives`)
				expect.eq(g.price, e.price, `{g.key} price`)
			end
		end
	end)

	it("every gift product gives a pass that exists", function()
		for _, e in Store.Entries do
			if e.gift then
				local pass = Store.ByKey[e.gift]
				expect.truthy(pass and pass.kind == "Pass", `{e.key} gives a pass`)
			end
		end
	end)

	it("every key is unique", function()
		local seen = {}
		for _, e in Store.Entries do
			expect.truthy(not seen[e.key], `{e.key} once`)
			seen[e.key] = true
		end
	end)
end)
