local Visits = require(Shared.Visits)
local Pieces = require(Shared.Pieces)
local Constants = require(Shared.Constants)

local C = Constants.Visits

-- An activity room as the server would describe it.
local function room(id, type, spots, ready, reachable)
	return {
		id = id,
		type = type,
		spots = spots,
		ready = ready ~= false,
		reachable = reachable ~= false,
	}
end

local function activityTypes()
	local out = {}
	for _, p in Pieces.List do
		if p.kind == "Amenity" then
			table.insert(out, p)
		end
	end
	return out
end

describe("Visits", function()
	it("guests visit amenities and activity rooms, never a bedroom, stairs or the desk", function()
		for _, p in Pieces.List do
			expect.eq(Visits.isActivity(p.id), p.kind == "Amenity", p.id)
			if p.kind ~= "Amenity" then
				expect.eq(
					#Visits.meets(p.tags or { "fun", "snacks" }, p.id),
					0,
					`{p.id} meets nothing`
				)
			end
		end
		expect.truthy(not Visits.isActivity("NoSuchType"), "an unknown type")
	end)

	it("a visit meets exactly the preferences the room's tags hold", function()
		for _, p in activityTypes() do
			local prefs = { (p.tags or {})[1] or "x", "no such tag" }
			local hits = Visits.meets(prefs, p.id)
			for _, h in hits do
				expect.truthy(table.find(prefs, h) and table.find(p.tags or {}, h), `{p.id}: {h}`)
			end
			expect.eq(#hits, if p.tags and #p.tags > 0 then 1 else 0, p.id)
		end
		expect.eq(#Visits.meets({ "fun" }, "GameRoom"), 1, "a guest who wants fun, a Game Room")
	end)

	it(
		"only ready, reachable activity rooms with a free spot that meet a preference are chosen",
		function()
			local prefs = { "fun", "snacks" }
			local rooms = {
				room("a", "GameRoom", 2),
				room("b", "GameRoom", 2, false), -- not ready
				room("c", "GameRoom", 2, true, false), -- not reachable
				room("d", "StandardRoom", 2), -- a bedroom
				room("e", "Cinema", 2), -- film: no match
				room("f", "SnackBar", 0), -- no spots
				room("g", "SnackBar", 1),
			}
			local taken = { g = { [1] = "someone" } } -- g full
			local list = Visits.candidates(prefs, rooms, taken)
			expect.eq(#list, 1, "only a")
			expect.eq(list[1].room, "a")
			expect.eq(list[1].pref, "fun")
			for k = 0, 9 do
				local c = Visits.choose(prefs, rooms, taken, k / 10)
				expect.truthy(c and c.room == "a", "every roll picks a candidate")
			end
			-- No match, no visit.
			expect.eq(
				Visits.choose({ "silence", "cold" }, rooms, {}, 0.5),
				nil,
				"a guest with no match"
			)
			expect.eq(Visits.choose(prefs, {}, {}, 0.5), nil, "no rooms")
		end
	)

	it("a guest goes first where a preference is not yet met, and any match otherwise", function()
		local prefs = { "fun", "snacks" }
		local rooms = { room("a", "GameRoom", 4), room("b", "SnackBar", 4) }
		for k = 0, 9 do
			local c = Visits.choose(prefs, rooms, {}, k / 10, { fun = true })
			expect.truthy(c and c.room == "b" and c.pref == "snacks", "the unmet one")
		end
		local all = Visits.candidates(prefs, rooms, {}, { fun = true, snacks = true })
		expect.eq(#all, 2, "both met: any match")
		-- Every roll lands on a candidate, and the draw reaches each.
		local seen = {}
		for k = 0, 99 do
			local c = Visits.choose(prefs, rooms, {}, k / 100)
			expect.truthy(c ~= nil, "a choice")
			seen[(c :: any).room] = true
		end
		expect.truthy(seen.a and seen.b, "each room drawn")
	end)

	it("a spot is one guest's, a guest holds one spot, and a freed spot is free again", function()
		local taken = {}
		expect.eq(Visits.freeSpot(taken, "r", 3), 1, "the first spot")
		expect.truthy(Visits.take(taken, "r", 1, 3, "g1"), "taken")
		expect.truthy(not Visits.take(taken, "r", 1, 3, "g2"), "not twice")
		expect.truthy(not Visits.take(taken, "r", 2, 3, "g1"), "one spot a guest")
		expect.truthy(not Visits.take(taken, "s", 1, 3, "g1"), "one spot a guest, any room")
		expect.truthy(not Visits.take(taken, "r", 4, 3, "g2"), "not a spot of the room")
		expect.truthy(not Visits.take(taken, "r", 0, 3, "g2"), "spots count from 1")
		expect.eq(Visits.freeSpot(taken, "r", 3), 2, "the next one")
		expect.truthy(Visits.take(taken, "r", 2, 3, "g2"), "g2")
		expect.truthy(Visits.take(taken, "r", 3, 3, "g3"), "g3")
		expect.eq(Visits.inUse(taken, "r"), 3, "3/3 in use")
		expect.eq(Visits.freeSpot(taken, "r", 3), nil, "full")
		local rid, i = Visits.spotOf(taken, "g2")
		expect.eq(rid, "r")
		expect.eq(i, 2)
		expect.truthy(Visits.free(taken, "g2"), "freed")
		expect.truthy(not Visits.free(taken, "g2"), "nothing to free twice")
		expect.eq(Visits.inUse(taken, "r"), 2, "2/3 in use")
		expect.eq(Visits.freeSpot(taken, "r", 3), 2, "the freed spot")
		Visits.free(taken, "g1")
		Visits.free(taken, "g3")
		expect.eq(Visits.inUse(taken, "r"), 0, "empty")
		expect.eq(next(taken), nil, "an empty room leaves no entry")
	end)

	it("a full room is never chosen; its freed spot is", function()
		local rooms = { room("a", "GameRoom", 2) }
		local taken = {}
		for n = 1, 2 do
			local c = Visits.choose({ "fun" }, rooms, taken, 0.3) :: any
			expect.truthy(c, `visitor {n}`)
			expect.truthy(Visits.take(taken, c.room, c.spot, 2, `g{n}`), `takes spot {c.spot}`)
		end
		expect.eq(Visits.choose({ "fun" }, rooms, taken, 0.3), nil, "full")
		Visits.free(taken, "g1")
		local c = Visits.choose({ "fun" }, rooms, taken, 0.3) :: any
		expect.truthy(c and c.spot == 1, "the freed spot")
	end)

	it("a visit is due 90–150 s after the last, later for a larger roll", function()
		local last = -math.huge
		for k = 0, 10 do
			local at = Visits.nextAt(100, k / 10)
			expect.atLeast(at, 100 + C.EveryMin, "not before the least")
			expect.atMost(at, 100 + C.EveryMax, "not after the most")
			expect.atLeast(at, last, "monotonic in the roll")
			last = at
		end
		expect.atMost(Visits.nextAt(0, 5), C.EveryMax, "a roll past 1 clamped")
		expect.atLeast(Visits.nextAt(0, -5), C.EveryMin, "a roll under 0 clamped")
	end)

	it("a guest decides only once due, and at most once per gap", function()
		expect.truthy(not Visits.mayDecide(10, 20, nil), "not before due")
		expect.truthy(Visits.mayDecide(20, 20, nil), "due")
		expect.truthy(not Visits.mayDecide(25, 20, 20), "within the gap")
		expect.truthy(Visits.mayDecide(20 + C.DecisionGap, 20, 20), "after the gap")
		-- A guest with nowhere to go, ticked every 0.5 s for 200 s: decisions spaced by the gap.
		local rooms = { room("a", "Cinema", 2) }
		local lastDecision, decisions = nil, 0
		local t = 0
		while t <= 200 do
			local c, decided = Visits.decide({
				now = t,
				dueAt = 0,
				lastDecision = lastDecision,
				prefs = { "fun" },
				rooms = rooms,
				taken = {},
				visitors = {},
				roll = 0.5,
			})
			expect.eq(c, nil, "nowhere to go")
			if decided then
				if lastDecision then
					expect.atLeast(t - lastDecision, C.DecisionGap, "spaced")
				end
				lastDecision = t
				decisions += 1
			end
			t += 0.5
		end
		expect.atMost(decisions, math.floor(200 / C.DecisionGap) + 1, "at most one per gap")
		expect.atLeast(decisions, 1, "it does decide")
	end)

	it(
		"no visitor sets out while the hotel's walkers are at the cap; one in a room is not walking",
		function()
			local visitors = {}
			for n = 1, C.MaxWalking - 1 do
				visitors[`w{n}`] =
					{ room = "a", spot = n, phase = if n % 2 == 0 then "Going" else "Back" }
			end
			visitors.there = { room = "a", spot = 99, phase = "There" }
			expect.eq(Visits.walking(visitors), C.MaxWalking - 1, "There is not walking")
			expect.truthy(Visits.canSetOut(visitors), "one more may")
			local input = {
				now = 100,
				dueAt = 0,
				lastDecision = nil,
				prefs = { "fun" },
				rooms = { room("b", "GameRoom", 4) },
				taken = {},
				visitors = visitors,
				roll = 0.2,
			}
			local c = Visits.decide(input)
			expect.truthy(c and c.room == "b", "under the cap: goes")
			visitors.last = { room = "b", spot = 1, phase = "Going" }
			expect.truthy(not Visits.canSetOut(visitors), "at the cap")
			local c2, decided = Visits.decide(input)
			expect.eq(c2, nil, "at the cap: stays")
			expect.truthy(decided, "it counts as a decision, so it waits the gap")
		end
	)

	it("a visit lasts 20–40 s", function()
		for k = 0, 10 do
			local d = Visits.duration(k / 10)
			expect.atLeast(d, C.DoMin)
			expect.atMost(d, C.DoMax)
		end
	end)

	it("a visit meeting a preference counts it met and adds satisfaction once a stay", function()
		local prefs = { "fun", "snacks" }
		local met, bonus = Visits.gives(prefs, "GameRoom", false)
		expect.eq(#met, 1, "fun met")
		expect.eq(met[1], "fun")
		expect.atLeast(bonus, 1, "a bonus the first time")
		local _, again = Visits.gives(prefs, "SnackBar", true)
		expect.eq(again, 0, "not twice a stay")
		local none, zero = Visits.gives({ "silence" }, "GameRoom", false)
		expect.eq(#none, 0, "no match meets nothing")
		expect.eq(zero, 0, "and gives nothing")
		local _, bedroom = Visits.gives(prefs, "StandardRoom", false)
		expect.eq(bedroom, 0, "a bedroom gives no visit's bonus")
	end)

	it("a visitor on its way or in a room makes it busy; one walking back does not", function()
		local visitors = {
			a = { room = "r1", spot = 1, phase = "Going" },
			b = { room = "r2", spot = 1, phase = "There" },
			c = { room = "r3", spot = 1, phase = "Back" },
		}
		local busy = Visits.busyRooms(visitors)
		expect.truthy(busy.r1 and busy.r2, "going and there")
		expect.eq(busy.r3, nil, "walking back")
		local booked = Visits.busyRooms(visitors, { bed = true })
		expect.truthy(booked.bed and booked.r1 and booked.r2, "added to the booked rooms")
		expect.eq(next(Visits.busyRooms({})), nil, "no visitors, nothing busy")
	end)

	it("visitors whose room stops being ready are sent home; those walking back are not", function()
		local visitors = {
			a = { room = "r1", spot = 1, phase = "Going" },
			b = { room = "r1", spot = 2, phase = "There" },
			c = { room = "r1", spot = 3, phase = "Back" },
			d = { room = "r2", spot = 1, phase = "There" },
		}
		local home = Visits.stranded(visitors, { r2 = true })
		expect.eq(#home, 2, "a and b")
		expect.eq(home[1], "a")
		expect.eq(home[2], "b")
		expect.eq(#Visits.stranded(visitors, { r1 = true, r2 = true }), 0, "all ready")
	end)

	it(
		"the tuning in Constants.Visits keeps its ranges and caps sane, whatever the numbers",
		function()
			expect.truthy(C.EveryMin > 0 and C.EveryMin <= C.EveryMax, "between visits")
			expect.truthy(C.DoMin > 0 and C.DoMin <= C.DoMax, "a visit's action")
			expect.truthy(C.DecisionGap > 0, "a decision gap")
			expect.truthy(
				C.DecisionGap <= C.EveryMin,
				"a due visit is decided before the next is due"
			)
			expect.truthy(C.MaxWalking >= 1 and C.MaxWalking % 1 == 0, "at least one walker")
			expect.truthy(C.Satisfaction >= 0, "a visit never makes a guest less happy")
		end
	)
end)
