local Bus = require(Shared.Bus)
local Constants = require(Shared.Constants)
local Species = require(Shared.Species)

describe("Bus", function()
	it("a Legendary comes exactly once per half hour, and a Mythic once per two hours", function()
		local interval = Constants.Bus.Interval
		local legendary, mythic = 0, 0
		local t = 0
		local hours = 6
		for i = 1, math.floor(hours * 3600 / interval) do
			local f = Bus.flags(i, t, t + interval)
			t += interval
			if f.legendary then
				legendary += 1
			end
			if f.mythic then
				mythic += 1
			end
		end
		expect.eq(legendary, hours * 3600 / Constants.Bus.LegendaryEvery, "legendaries")
		expect.eq(mythic, hours * 3600 / Constants.Bus.MythicEvery, "mythics")
	end)

	it("an Epic every third bus", function()
		for i = 1, 30 do
			expect.eq(Bus.flags(i, 0, 1).epic, i % Constants.Bus.EpicEvery == 0, `bus {i}`)
		end
	end)

	it("the bus grows with players, within its bounds", function()
		local prev = 0
		for players = 1, 12 do
			local s = Bus.size(players)
			expect.atLeast(s, Constants.Bus.BaseSize)
			expect.atMost(s, Constants.Bus.MaxSize)
			expect.atLeast(s, prev)
			prev = s
		end
	end)

	it("it carries as many guests as its size, and the guarantees are aboard", function()
		local rng = Random.new(3)
		local rand = function()
			return rng:NextNumber()
		end
		local locs = { [1] = true }
		for _ = 1, 50 do
			local list =
				Bus.passengers({ epic = true, legendary = true, mythic = false }, 8, locs, rand)
			expect.eq(#list, 8, "size")
			local rarities = {}
			for _, id in list do
				local sp = Species.get(id)
				expect.truthy(sp and sp.location == 1, "a species of the street's locations")
				rarities[(sp :: any).rarity] = true
			end
			expect.truthy(rarities.Legendary and rarities.Epic, "guarantees aboard")
			expect.truthy(not rarities.Mythic, "no Mythic without the Midnight Bus")
		end
	end)

	it("weights are drawn from the whole of [0, 1)", function()
		expect.eq(Bus.rollRarity(0), "Common")
		expect.truthy(Bus.rollRarity(0.99999) ~= "Mythic", "Mythic is scheduled only")
	end)
end)
