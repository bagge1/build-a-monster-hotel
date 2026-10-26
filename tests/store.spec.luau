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

	-- A gift bought through Buy would give the pass to whoever was picked last.
	it("Buy prompts what the player buys for himself, never a gift nor the ad's", function()
		for _, e in Store.Entries do
			if e.gift then
				expect.truthy(not Store.buyable(e.key), `{e.key} only through Gift`)
			elseif e.kind == "Pass" then
				expect.truthy(Store.buyable(e.key), `{e.key} is bought`)
			end
		end
		expect.truthy(not Store.buyable("AdCash2x15"), "the ad's is granted, not bought")
		expect.truthy(not Store.buyable("NoSuchKey"), "an unknown key")
	end)

	it("every key is unique", function()
		local seen = {}
		for _, e in Store.Entries do
			expect.truthy(not seen[e.key], `{e.key} once`)
			seen[e.key] = true
		end
	end)
end)
