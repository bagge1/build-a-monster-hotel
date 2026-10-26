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

	it("the rarest guest is never outranked by another aboard, and none means nil", function()
		local order = Constants.RarityOrder
		local function rank(id)
			return table.find(order, (Species.get(id) :: any).rarity)
		end
		local ids = {}
		for _, sp in Species.List do
			table.insert(ids, sp.id)
		end
		local rng = Random.new(7)
		for _ = 1, 50 do
			local some = {}
			for _ = 1, 1 + math.floor(rng:NextNumber() * 6) do
				table.insert(some, ids[1 + math.floor(rng:NextNumber() * #ids)])
			end
			local best = Bus.rarest(some)
			expect.truthy(best ~= nil and table.find(some, best) ~= nil, "one of them")
			for _, id in some do
				expect.atMost(rank(id), rank(best), `{id} outranks {best}`)
			end
		end
		expect.eq(Bus.rarest({}), nil, "nobody on the street")
	end)

	it("the tutorial's Commons are Commons the hotel's vacant rooms take, never more", function()
		local locs = { [1] = true }
		local rng = Random.new(11)
		local rand = function()
			return rng:NextNumber()
		end
		local rooms = {}
		for _, sp in Species.List do
			if sp.location == 1 then
				rooms[sp.room] = true
			end
		end
		local roomIds = {}
		for room in rooms do
			table.insert(roomIds, room)
		end
		for _ = 1, 100 do
			local vacant = {}
			for _, room in roomIds do
				if rng:NextNumber() < 0.5 then
					vacant[room] = math.floor(rng:NextNumber() * 3)
				end
			end
			local n = math.floor(rng:NextNumber() * 5)
			local got = Bus.commonsFor(vacant, n, locs, rand)
			expect.atMost(#got, n, "never more than asked")
			local per = {}
			for _, id in got do
				local sp = Species.get(id) :: any
				expect.eq(sp.rarity, "Common", id)
				expect.truthy(locs[sp.location], `{id} of the street's locations`)
				per[sp.room] = (per[sp.room] or 0) + 1
			end
			local roomsTaken = 0
			for room, k in per do
				expect.atMost(k, vacant[room] or 0, `no more for {room} than stand vacant`)
				roomsTaken += 1
			end
			-- Every vacant type a Common takes gets one before any gets two.
			local takeable = 0
			for room, k in vacant do
				if k > 0 and #Bus.commonsFor({ [room] = 1 }, 1, locs, rand) == 1 then
					takeable += 1
				end
			end
			expect.eq(roomsTaken, math.min(takeable, #got), "round the room types in turn")
		end
		expect.eq(#Bus.commonsFor({ CoffinSuite = 3 }, 2, locs, rand), 0, "no Common takes it")
		expect.eq(#Bus.commonsFor({}, 2, locs, rand), 0, "no vacant room")
	end)

	-- §11: one that missed its hotel at step-off is owed until it arrives, never two at once.
	it(
		"the tutorial's Vampire rides from the third bus until it has reached its hotel, one at a time",
		function()
			local function due(over: { [string]: any }): boolean
				local t =
					{ goal = true, arrived = false, onBus = false, busesSince = 2, vacant = true }
				for k, v in over do
					(t :: any)[k] = v
				end
				return Bus.tutorialVampire(t)
			end
			expect.truthy(due({}), "owed, its room vacant, the third bus")
			expect.truthy(due({ busesSince = 9 }), "a later bus after one that missed")
			expect.truthy(not due({ goal = false }), "before the goal card")
			expect.truthy(not due({ busesSince = 1 }), "before the third bus")
			expect.truthy(not due({ vacant = false }), "no room for it")
			expect.truthy(not due({ onBus = true }), "one already on a bus")
			expect.truthy(not due({ arrived = true }), "once it has reached its hotel")
		end
	)

	-- §11 "in 3 buses": the same on any server, not this server's bus index (2026-10-26).
	it("the buses since the goal card count by the clock on another server", function()
		expect.eq(Bus.busesSince(1000, 1000, 180, nil), 0, "the goal card's own moment")
		expect.eq(Bus.busesSince(1000, 1000 + 359, 180, nil), 1, "short of two intervals")
		expect.eq(Bus.busesSince(1000, 1000 + 360, 180, nil), 2, "two intervals: the next rides")
		expect.eq(Bus.busesSince(1000, 900, 180, nil), 0, "a clock behind never counts back")
		expect.eq(Bus.busesSince(0, 1000000, 180, nil) >= 2, true, "no goal time: long owed")
		expect.eq(Bus.busesSince(1000, 1000 + 100, 180, 2), 2, "this server's buses, called early")
		expect.eq(Bus.busesSince(1000, 1000 + 400, 180, 1), 2, "never fewer than by the clock")
	end)

	it("weights are drawn from the whole of [0, 1)", function()
		expect.eq(Bus.rollRarity(0), "Common")
		expect.truthy(Bus.rollRarity(0.99999) ~= "Mythic", "Mythic is scheduled only")
	end)
end)
