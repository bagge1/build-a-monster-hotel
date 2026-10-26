-- Expeditions (GDD A.11.2; his ruling on the pay, §18 2026-10-26): who goes, the pay by staying's
-- rules and cap, the find with the match bonus, XP as in the Wing, coming home, collect and recall.
-- Rules only: every number is Constants.Expeditions (PLACEHOLDER but Pay).
local Constants = require(Shared.Constants)
local Economy = require(Shared.Economy)
local Expeditions = require(Shared.Expeditions)
local Finds = require(Shared.Finds)
local Perks = require(Shared.Perks)
local ResidentLevels = require(Shared.ResidentLevels)
local Species = require(Shared.Species)

local X = Constants.Expeditions
local R = Constants.Residents

describe("Expeditions (A.11.2)", function()
	local now = 1000000
	local lengths = Expeditions.lengths()
	local short, long = lengths[1], lengths[#lengths]
	local opened = { [1] = true }

	local function always(v: number): () -> number
		return function()
			return v
		end
	end
	local miss = always(0.999999)

	local function wing(n: number): { [string]: any }
		local out = {}
		for i = 1, n do
			out[tostring(i)] = { species = "Slime", mutation = "", role = "", campUntil = 0 }
		end
		return out
	end

	local function ids(n: number): { string }
		local out = {}
		for i = 1, n do
			table.insert(out, tostring(i))
		end
		return out
	end

	it("one destination per launch location, each with likes some species has", function()
		for _, d in Expeditions.Destinations do
			expect.eq(Expeditions.destination(d.id), d, `{d.name} found by its id`)
			local liked = false
			for _, sp in Species.List do
				if Expeditions.matches(sp.id, d.id) then
					liked = true
				end
			end
			expect.truthy(liked, `some species matches {d.name}`)
		end
	end)

	it("a destination is offered only while its location is open in the run", function()
		for _, d in Expeditions.Destinations do
			expect.truthy(Expeditions.offered(d.id, { [d.location] = true }), `{d.name} when open`)
			expect.truthy(not Expeditions.offered(d.id, {}), `{d.name} not when closed`)
		end
	end)

	it(
		"only Wing residents at home may go; on staff, in the camp or on a trip they may not",
		function()
			expect.truthy(
				Expeditions.mayGo({ species = "Slime", role = "", campUntil = 0 }, now),
				"in the Wing"
			)
			expect.truthy(
				not Expeditions.mayGo({ species = "Slime", role = "FrontDesk", campUntil = 0 }, now),
				"on staff"
			)
			expect.truthy(
				not Expeditions.mayGo({ species = "Slime", role = "", campUntil = now + 60 }, now),
				"in the Hunter Camp"
			)
			expect.truthy(
				not Expeditions.mayGo(
					{ species = "Slime", role = "", campUntil = 0, expedition = now + 60 },
					now
				),
				"on a trip"
			)
		end
	)

	it("a party is 1 to Party different residents who may go, one trip at a time", function()
		local rec = Expeditions.newRecord()
		local res = wing(X.Party + 1)
		expect.truthy(Expeditions.check(rec, res, {}, 1, short, opened, now) ~= nil, "nobody")
		expect.truthy(
			Expeditions.check(rec, res, ids(X.Party + 1), 1, short, opened, now) ~= nil,
			"too many"
		)
		expect.truthy(
			Expeditions.check(rec, res, { "1", "1" }, 1, short, opened, now) ~= nil,
			"twice"
		)
		expect.truthy(
			Expeditions.check(rec, res, { "99" }, 1, short, opened, now) ~= nil,
			"no such resident"
		)
		expect.truthy(
			Expeditions.check(rec, res, { "1" }, 1, short + 1, opened, now) ~= nil,
			"not a listed length"
		)
		expect.truthy(Expeditions.check(rec, res, { "1" }, 2, short, opened, now) ~= nil, "closed")
		expect.eq(Expeditions.check(rec, res, ids(X.Party), 1, short, opened, now), nil, "a party")
		Expeditions.start(rec, res, ids(X.Party), 1, short, now)
		expect.truthy(
			Expeditions.check(rec, res, { tostring(X.Party + 1) }, 1, short, opened, now) ~= nil,
			"a second trip"
		)
	end)

	it("the party is away until the trip ends, then home without collecting", function()
		local rec = Expeditions.newRecord()
		local res = wing(2)
		local trip = Expeditions.start(rec, res, { "1" }, 1, short, now)
		expect.truthy(Expeditions.away(res["1"], now + short - 1), "away during the trip")
		expect.truthy(not Expeditions.away(res["2"], now), "the one left home is not")
		expect.truthy(not Expeditions.back(trip, now + short - 1), "not back before the end")
		expect.truthy(Expeditions.back(trip, now + short), "back at the end")
		expect.truthy(not Expeditions.away(res["1"], now + short), "home at the end")
		expect.eq(Expeditions.left(trip, now + short + 50), 0, "no time left once back")
	end)

	it("an away resident gives no perk, and learns as in the Wing (§18)", function()
		local away = { species = "Ghost", role = "", campUntil = 0, expedition = now + 60 }
		local home = { species = "Ghost", role = "", campUntil = 0 }
		expect.eq(Perks.total({ away }, "Cleanliness", now), 0, "no perk away")
		expect.truthy(Perks.total({ home }, "Cleanliness", now) > 0, "a perk at home")
		expect.truthy(ResidentLevels.learning(away, now), "a trip learns as the Wing does")
	end)

	it("Best for this trip: matching first, then level, then rarity, at most n", function()
		local d = Expeditions.Destinations[2]
		local likes, other
		for _, sp in Species.List do
			if Expeditions.matches(sp.id, d.id) then
				likes = likes or sp.id
			else
				other = other or sp.id
			end
		end
		assert(likes and other, "a species that matches and one that does not")
		local picked = Expeditions.best({
			{ id = "1", species = other, level = 9 },
			{ id = "2", species = likes, level = 1 },
			{ id = "3", species = other, level = 3 },
		}, d.id, 2)
		expect.eq(#picked, 2, "two of three")
		expect.eq(picked[1], "2", "the matching one first, whatever its level")
		expect.eq(picked[2], "1", "then the higher level")
		local common, rare
		for _, sp in Species.List do
			if not Expeditions.matches(sp.id, d.id) then
				if sp.rarity == "Common" then
					common = common or sp.id
				elseif sp.rarity == "Legendary" then
					rare = rare or sp.id
				end
			end
		end
		if common and rare then
			local tie = Expeditions.best({
				{ id = "1", species = common, level = 2 },
				{ id = "2", species = rare, level = 2 },
			}, d.id, 1)
			expect.eq(tie[1], "2", "at the same level the rarer")
		end
		expect.eq(#Expeditions.best({}, d.id, 3), 0, "nobody to pick")
	end)

	it("the pay is Pay × staying's earnings while playing (his ruling)", function()
		local rec = Expeditions.newRecord()
		local trip = Expeditions.start(rec, wing(1), { "1" }, 1, short, now)
		Expeditions.countOnline(trip, 10, now + 60)
		Expeditions.countOnline(trip, 10, now + 60) -- counted once
		expect.near(trip.earned, 600, 1e-6, "a minute at $10/s, counted once")
		expect.eq(Expeditions.pay(trip), math.floor(X.Pay * 600), "Pay × staying")
		Expeditions.countOnline(trip, 10, now + short + 3600)
		expect.near(trip.earned, 10 * short, 1e-6, "nothing past the trip's end")
	end)

	it(
		"the time away is counted as staying counts: the offline rate, never past the cap",
		function()
			local cap = R.OfflineCap
			for _, length in lengths do
				for _, away in { 60, cap / 2, cap, cap * 3, length * 2 } do
					local rec = Expeditions.newRecord()
					local trip = Expeditions.start(rec, wing(1), { "1" }, 1, length, now)
					-- The player logs out as the trip leaves and comes back `away` later.
					Expeditions.countOffline(trip, 10, now, away, cap, now + away)
					local stay = Economy.offline(10, math.min(away, length), cap)
					expect.near(trip.earned, stay, 1e-6, `{length}s trip, {away}s away`)
					expect.atMost(trip.earned, Economy.offline(10, cap, cap), "never past the cap")
					expect.atMost(
						Expeditions.pay(trip),
						Economy.offline(10, away, cap),
						"never beats staying"
					)
				end
			end
		end
	)

	it("a trip never pays more than staying would over the same time, online or away", function()
		local cap = R.OfflineCap
		local rec = Expeditions.newRecord()
		local trip = Expeditions.start(rec, wing(1), { "1" }, 1, long, now)
		-- Plays 20 min, away 3 h, back for the rest.
		Expeditions.countOnline(trip, 5, now + 1200)
		Expeditions.countOffline(trip, 5, now + 1200, 3 * 3600, cap, now + 1200 + 3 * 3600)
		Expeditions.countOnline(trip, 5, now + long)
		local stay = 5 * 1200 + Economy.offline(5, 3 * 3600, cap) + 5 * (long - 1200 - 3 * 3600)
		expect.near(trip.earned, stay, 1, "staying's earnings, segment by segment")
		expect.atMost(Expeditions.pay(trip), stay, "Pay × that")
	end)

	it("a trip back before the login does not also fill the offline till (§18)", function()
		local cap = R.NightManagerCap
		local since, away = now, 6 * 3600
		local ends = now + 2 * 3600
		expect.eq(
			Expeditions.homeSeconds(since, away, cap, 0),
			math.min(away, cap),
			"never on a trip: the whole window"
		)
		expect.eq(Expeditions.homeSeconds(since, away, cap, ends), 4 * 3600, "only after it ended")
		expect.eq(
			Expeditions.homeSeconds(since, away, cap, now + away + 60),
			0,
			"still out: nothing"
		)
		expect.eq(
			Expeditions.homeSeconds(since, away, cap, now - 60),
			math.min(away, cap),
			"back before the logout: the whole window"
		)
		-- The trip's counted part and the till's part never overlap: together at most staying.
		for _, length in lengths do
			local rec = Expeditions.newRecord()
			local trip = Expeditions.start(rec, wing(1), { "1" }, 1, length, since)
			Expeditions.countOffline(trip, 1, since, away, cap, since + away)
			local till =
				Economy.offline(1, Expeditions.homeSeconds(since, away, cap, trip.ends), cap)
			expect.atMost(
				trip.earned + till,
				Economy.offline(1, away, cap) + 1,
				`{length}s: never both`
			)
		end
	end)

	it(
		"the find's chance grows with length and matches (on the find, not the pay), at most 1",
		function()
			for i = 2, #lengths do
				expect.truthy(
					Expeditions.findChance(lengths[i], 0)
						>= Expeditions.findChance(lengths[i - 1], 0),
					`{lengths[i]}s no less than {lengths[i - 1]}s`
				)
			end
			for m = 1, X.Party do
				expect.truthy(
					Expeditions.findChance(short, m) >= Expeditions.findChance(short, m - 1),
					`{m} matches`
				)
				expect.atMost(Expeditions.findChance(long, m * 100), 1, "a chance")
			end
			-- The pay does not read the matches.
			local a, b = Expeditions.newRecord(), Expeditions.newRecord()
			local plain = Expeditions.start(a, wing(1), { "1" }, 1, short, now)
			local liked = Expeditions.start(b, wing(1), { "1" }, 1, short, now)
			liked.matches = X.Party
			Expeditions.countOnline(plain, 7, now + short)
			Expeditions.countOnline(liked, 7, now + short)
			expect.eq(Expeditions.pay(liked), Expeditions.pay(plain), "the same pay")
		end
	)

	it(
		"a long trip's find is guaranteed after PityTrips in a row without one; short ones never count",
		function()
			local rec = Expeditions.newRecord()
			for i = 1, X.PityTrips * 2 do
				local trip = Expeditions.start(rec, wing(1), { "1" }, 1, short, now)
				expect.truthy(
					short >= X.PityMin or not Expeditions.roll(rec, trip, miss),
					`short trip {i} misses`
				)
				rec.trip = nil
			end
			if short < X.PityMin then
				expect.eq(rec.longMisses, 0, "short trips leave the run alone")
			end
			local found = 0
			for i = 1, X.PityTrips do
				local trip = Expeditions.start(rec, wing(1), { "1" }, 1, long, now)
				if Expeditions.roll(rec, trip, miss) then
					found += 1
					expect.eq(i, X.PityTrips, "the guarantee, on its trip")
				end
				rec.trip = nil
			end
			expect.eq(found, 1, "one guaranteed find")
			expect.eq(rec.longMisses, 0, "the run starts again")
		end
	)

	it(
		"a trip's find is a piece of its destination not found yet, and leaves the stays' pity alone",
		function()
			for _, d in Expeditions.Destinations do
				local rec = Finds.newRecord()
				local pool = Finds.pool(d.location)
				rec.misses[tostring(d.location)] = 7
				local seen: { [string]: boolean } = {}
				for i = 1, #pool do
					local out, id = Finds.draw(rec, d.location, always((i - 1) / #pool), now)
					expect.eq(out, "Piece", `{d.name} draw {i}`)
					expect.truthy(
						id and table.find(pool, id) and not seen[id],
						`{d.name}: a new piece`
					)
					seen[id :: string] = true
				end
				if #pool > 0 then
					expect.eq(
						Finds.draw(rec, d.location, miss, now),
						"Duplicate",
						"all found: a duplicate"
					)
				else
					expect.eq(Finds.draw(rec, d.location, miss, now), "None", "no set: nothing")
				end
				expect.eq(rec.misses[tostring(d.location)], 7, "the pity untouched")
			end
		end
	)

	it("Collect waits for the end; it pays, rolls once and frees the board", function()
		local rec = Expeditions.newRecord()
		local res = wing(2)
		local trip = Expeditions.start(rec, res, { "1", "2" }, 1, short, now)
		Expeditions.countOnline(trip, 3, now + short)
		local cash, found, got = Expeditions.collect(rec, res, miss, now + short - 1)
		expect.truthy(cash == 0 and not found and got == nil, "nothing before the end")
		cash, found, got = Expeditions.collect(rec, res, always(0), now + short)
		expect.eq(cash, math.floor(X.Pay * 3 * short), "its pay")
		expect.truthy(found and got == trip, "its roll and the trip")
		expect.eq(rec.trip, nil, "the board is free")
		expect.eq(rec.trips, 1, "one trip collected")
		expect.truthy(res["1"].expedition == nil and res["2"].expedition == nil, "the party home")
		expect.eq(Expeditions.collect(rec, res, always(0), now + short), 0, "collected once")
	end)

	it("a rebirth calls the party home: what was counted so far, no roll", function()
		local rec = Expeditions.newRecord()
		local res = wing(1)
		local trip = Expeditions.start(rec, res, { "1" }, 1, long, now)
		Expeditions.countOnline(trip, 4, now + 100)
		local misses = rec.longMisses
		local cash, got = Expeditions.recall(rec, res)
		expect.eq(cash, math.floor(X.Pay * 400), "the elapsed part")
		expect.truthy(got == trip and rec.trip == nil, "the trip ended")
		expect.truthy(not Expeditions.away(res["1"], now + 101), "home at once")
		expect.eq(rec.longMisses, misses, "no roll")
		expect.eq(rec.trips, 0, "not a collected trip")
		expect.eq(Expeditions.recall(rec, res), 0, "nothing out: nothing")
	end)

	it("a resident on a new trip is not sent home by an old trip's end", function()
		local rec = Expeditions.newRecord()
		local res = wing(1)
		local first = Expeditions.start(rec, res, { "1" }, 1, short, now)
		local cash = Expeditions.collect(rec, res, miss, now + short)
		expect.atLeast(cash, 0, "collected")
		Expeditions.start(rec, res, { "1" }, 1, long, now + short)
		-- An old trip's record ending again must not touch the new one.
		Expeditions.recall({ trip = first, longMisses = 0, trips = 0 }, res)
		expect.truthy(Expeditions.away(res["1"], now + short + 1), "still on its new trip")
	end)
end)
