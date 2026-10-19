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

	it("the bus follows the street's vacant rooms, within its bounds per player", function()
		local B = Constants.Bus
		for players = 1, 6 do
			local prev = 0
			for vacant = 0, 60 do
				local s = Bus.size(vacant, players)
				expect.atLeast(s, B.MinPerPlayer * players, "lower bound")
				expect.atMost(s, B.MaxPerPlayer * players, "upper bound")
				expect.atLeast(s, prev, "more vacant rooms never make a smaller bus")
				expect.atLeast(
					s,
					Bus.size(vacant, math.max(1, players - 1)),
					"more players never a smaller bus"
				)
				-- One bus never fills every room, unless the lower bound asks for more.
				if vacant >= 2 and s > B.MinPerPlayer * players then
					expect.truthy(s < vacant, `{s} guests for {vacant} vacant rooms`)
				end
				prev = s
			end
		end
	end)

	it("the bus drives out of the forest to the west stop, the east stop, and away", function()
		local StreetLayout = require(Shared.StreetLayout)
		local d = Bus.drive()
		expect.truthy(d.start < 0 and 0 < d.eastAt and d.eastAt < d.finish, "in order")
		expect.near(d.at(d.start), 0, 1e-6, "starts at the road's start")
		expect.near(d.at(d.finish), StreetLayout.RouteLength, 1e-3, "ends at the road's end")
		for i, stop in StreetLayout.Stops do
			local at = d.stops[i]
			local p = StreetLayout.routePoint(d.at(at))
			expect.near(p.X, stop.x, 1e-3, `{stop.name} stop's x`)
			expect.near(
				d.at(at + Constants.Bus.StopTime * 0.9),
				d.at(at),
				1e-6,
				`standing at {stop.name}`
			)
		end
		local prev = -1
		for t = d.start, d.finish, 0.1 do
			local s = d.at(t)
			expect.atLeast(s, prev, "never backs up")
			expect.atMost(s - prev, Constants.Bus.Speed * 0.1 + 1e-6, "never over its speed")
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
