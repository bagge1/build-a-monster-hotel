local Economy = require(Shared.Economy)
local Constants = require(Shared.Constants)
local Pieces = require(Shared.Pieces)
local Species = require(Shared.Species)
local Mutations = require(Shared.Mutations)

describe("Economy", function()
	it("each piece of a kind costs more than the one before", function()
		for _, p in Pieces.List do
			for n = 0, 30 do
				expect.truthy(
					Economy.pieceCost(p.id, n + 1) >= Economy.pieceCost(p.id, n),
					`{p.id} n={n}`
				)
			end
		end
	end)

	it("selling never refunds more than was paid, nor less than nothing", function()
		for _, paid in { 0, 1, 50, 999, 250000 } do
			expect.atMost(Economy.refund(paid), paid, `paid {paid}`)
			expect.atLeast(Economy.refund(paid), 0, `paid {paid}`)
		end
	end)

	it(
		"each tile costs at least the one before, and the whole plot about the six areas' $72,000",
		function()
			expect.eq(Economy.tileCost(1, 0), Constants.Economy.TileCost, "the first tile")
			for n = 0, 20 do
				expect.eq(
					Economy.tileCost(2, n),
					math.floor(
						Constants.Economy.TileCost * 2 * Constants.Economy.TileGrowth ^ n + 0.5
					),
					"floor 2 twice floor 1's ladder"
				)
				expect.atLeast(Economy.tileCost(3, n), Economy.tileCost(2, n), "dearer a floor up")
			end
			local G = Constants.Grid
			local total = 0
			for n = 0, G.Cells * G.Cells - G.StartTiles.w * G.StartTiles.d - 1 do
				if n > 0 then
					expect.atLeast(
						Economy.tileCost(1, n),
						Economy.tileCost(1, n - 1),
						`tile {n + 1}`
					)
				end
				total += Economy.tileCost(1, n)
			end
			expect.atLeast(total, 60000, "the whole plot")
			expect.atMost(total, 85000, "the whole plot")
		end
	)

	it("a higher tier, more rooms of a type, a mutation and a bonus never pay less", function()
		for _, sp in Species.List do
			local base = Economy.guestPay(sp.id, 1, nil, 1, 1)
			expect.truthy(base > 0, sp.id)
			expect.truthy(Economy.guestPay(sp.id, 2, nil, 1, 1) > base, "tier")
			expect.atLeast(Economy.guestPay(sp.id, 1, nil, 30, 1), base, "milestones")
			for _, m in Mutations.List do
				expect.atLeast(Economy.guestPay(sp.id, 1, m.id, 1, 1), base, m.id)
			end
			expect.truthy(Economy.guestPay(sp.id, 1, nil, 1, 1.2) > base, "bonus")
		end
	end)

	it("a rarer species pays more than a commoner one of its location", function()
		for _, a in Species.List do
			for _, b in Species.List do
				if a.location == b.location then
					local ra = table.find(Constants.RarityOrder, a.rarity) :: number
					local rb = table.find(Constants.RarityOrder, b.rarity) :: number
					if ra > rb then
						expect.truthy(
							Economy.speciesPay(a.id) > Economy.speciesPay(b.id),
							`{a.id} > {b.id}`
						)
					end
				end
			end
		end
	end)

	it("a later location's species pay more than an earlier one's of the same rarity", function()
		for _, a in Species.List do
			for _, b in Species.List do
				if a.rarity == b.rarity and a.location > b.location then
					expect.truthy(
						Economy.speciesPay(a.id) > Economy.speciesPay(b.id),
						`{a.id} > {b.id}`
					)
				end
			end
		end
	end)

	it("bonuses add within a category and multiply across", function()
		local a = Economy.incomeMultiplier({ permanent = 0.1 })
		local b = Economy.incomeMultiplier({ permanent = 0.15 })
		expect.truthy(b > a, "more permanent bonus")
		local f = Economy.incomeMultiplier({ permanent = 0.1, friends = true })
		expect.near(f / a, 1 + Constants.Social.FriendBonus, 1e-9, "friends multiply")
		expect.near(Economy.incomeMultiplier({ boost = 2 }), 2, 1e-9, "a boost multiplies")
	end)

	it("offline earnings stop at the cap and are never negative", function()
		local cap = Constants.Residents.OfflineCap
		expect.eq(Economy.offline(10, cap * 3, cap), Economy.offline(10, cap, cap), "capped")
		expect.eq(Economy.offline(10, -50, cap), 0, "never negative")
		expect.truthy(Economy.offline(10, cap, cap) < 10 * cap, "less than online")
	end)

	-- WAITING §2.48 (his yes 2026-10-26).
	it("offline earnings never carry the friend bonus, and keep every other", function()
		local b = { permanent = 0.2, friends = true, boost = 2 }
		local away = Economy.incomeMultiplier(Economy.offlineBonuses(b))
		local plain = Economy.incomeMultiplier({ permanent = 0.2, boost = 2 })
		expect.near(away, plain, 1e-9, "no friend bonus")
		expect.truthy(away < Economy.incomeMultiplier(b), "less than with friends online")
		expect.near(
			Economy.incomeMultiplier(Economy.offlineBonuses({ permanent = 0.2, boost = 2 })),
			away,
			1e-9,
			"the same without friends online"
		)
	end)

	it("rebirth shards grow with run cash, and 4x the cash doubles them", function()
		local prev = -1
		for _, cash in { 0, 1e5, 1e6, 2e6, 4e6, 1e8 } do
			local s = Economy.rebirthShards(cash)
			expect.atLeast(s, prev, `cash {cash}`)
			prev = s
		end
		local one = Economy.rebirthShards(Constants.Rebirth.ShardDivisor)
		expect.near(
			Economy.rebirthShards(4 * Constants.Rebirth.ShardDivisor),
			2 * one,
			1,
			"square root"
		)
	end)
end)
