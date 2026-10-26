local Visits = require(Shared.Visits)
local Pieces = require(Shared.Pieces)
local Constants = require(Shared.Constants)

local C = Constants.Visits

-- `n` spots' keys on one piece of furniture, decor id `decor` ("p" by default).
local function keys(n, decor)
	local out = {}
	for i = 1, n do
		table.insert(out, Visits.spotKey(decor or "p", i))
	end
	return out
end

-- An activity room as the server would describe it: `spots` usable spots, on a piece named after the room.
local function room(id, type, spots, ready, reachable)
	return {
		id = id,
		type = type,
		spots = keys(spots, `{id}1`),
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
			local taken = { g = { [Visits.spotKey("g1", 1)] = "someone" } } -- g full
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
		local r = keys(3)
		expect.eq(Visits.freeSpot(taken, "r", r), r[1], "the first spot")
		expect.truthy(Visits.take(taken, "r", r[1], r, "g1"), "taken")
		expect.truthy(not Visits.take(taken, "r", r[1], r, "g2"), "not twice")
		expect.truthy(not Visits.take(taken, "r", r[2], r, "g1"), "one spot a guest")
		expect.truthy(
			not Visits.take(taken, "s", "q:1", { "q:1" }, "g1"),
			"one spot a guest, any room"
		)
		expect.truthy(not Visits.take(taken, "r", "p:4", r, "g2"), "not a spot of the room")
		expect.truthy(not Visits.take(taken, "r", "x:1", r, "g2"), "nor another piece's")
		expect.eq(Visits.freeSpot(taken, "r", r), r[2], "the next one")
		expect.truthy(Visits.take(taken, "r", r[2], r, "g2"), "g2")
		expect.truthy(Visits.take(taken, "r", r[3], r, "g3"), "g3")
		expect.eq(Visits.inUse(taken, "r", r), 3, "3/3 in use")
		expect.eq(Visits.freeSpot(taken, "r", r), nil, "full")
		local rid, k = Visits.spotOf(taken, "g2")
		expect.eq(rid, "r")
		expect.eq(k, r[2])
		expect.truthy(Visits.free(taken, "g2"), "freed")
		expect.truthy(not Visits.free(taken, "g2"), "nothing to free twice")
		expect.eq(Visits.inUse(taken, "r", r), 2, "2/3 in use")
		expect.eq(Visits.freeSpot(taken, "r", r), r[2], "the freed spot")
		Visits.free(taken, "g1")
		Visits.free(taken, "g3")
		expect.eq(Visits.inUse(taken, "r", r), 0, "empty")
		expect.eq(next(taken), nil, "an empty room leaves no entry")
	end)

	it(
		"a spot is its piece's and number's, so another piece sold or moved never shifts it",
		function()
			expect.eq(Visits.pieceOf(Visits.spotKey("12", 3)), "12", "the piece a spot is on")
			expect.eq(Visits.pieceOf("nonsense"), nil, "not a spot's key")
			-- A room of two seats (pieces 5 and 9), each one spot; a guest sits on piece 9's.
			local taken, visitors = {}, {}
			local before = { Visits.spotKey("5", 1), Visits.spotKey("9", 1) }
			local seat9 = Visits.spotKey("9", 1)
			expect.truthy(
				Visits.begin(
					taken,
					visitors,
					"sitter",
					{ room = "r", spot = seat9, pref = "fun" },
					before
				),
				"sits on 9"
			)
			-- Piece 5 is sold: the spots now are 9's alone, and a piece 7 is bought.
			local after = { Visits.spotKey("7", 1), seat9 }
			expect.eq(
				Visits.inUse(taken, "r", after),
				1,
				"still one in use, never more than the spots"
			)
			local next_ = Visits.freeSpot(taken, "r", after)
			expect.eq(
				next_,
				Visits.spotKey("7", 1),
				"a new visitor gets the free seat, not the sitter's"
			)
			expect.truthy(
				not Visits.take(taken, "r", seat9, after, "newcomer"),
				"never on the sitter"
			)
			expect.eq(
				#Visits.stranded(visitors, { r = true }, { r = after }),
				0,
				"the sitter stays"
			)
			-- Its own seat sold: it is sent back, and the view never counts a spot gone.
			local without = { Visits.spotKey("7", 1) }
			local home = Visits.stranded(visitors, { r = true }, { r = without })
			expect.eq(#home, 1, "the sitter of a sold seat")
			expect.eq(home[1], "sitter")
			expect.eq(Visits.inUse(taken, "r", without), 0, "0/1, never 1/1 or 2/1")
			-- Its own seat moved: the visitors on that piece are sent back.
			local on = Visits.onPiece(visitors, "9")
			expect.eq(#on, 1, "the visitor on the piece moved")
			expect.eq(#Visits.onPiece(visitors, "5"), 0, "nobody on another piece")
			visitors.sitter.phase = "Back"
			expect.eq(#Visits.onPiece(visitors, "9"), 0, "one walking back is not")
		end
	)

	it("a visit begun takes its spot and records the visitor together, or neither", function()
		local taken, visitors = {}, {}
		local r = keys(2)
		local c = { room = "r", spot = r[1], pref = "fun" }
		expect.truthy(Visits.begin(taken, visitors, "g1", c, r), "begun")
		expect.eq(visitors.g1.spot, r[1], "recorded on its spot")
		expect.eq(visitors.g1.phase, "Going")
		expect.truthy(not Visits.begin(taken, visitors, "g2", c, r), "the spot is held")
		expect.eq(visitors.g2, nil, "a refused visit records nobody")
		expect.truthy(
			not Visits.begin(taken, visitors, "g1", { room = "r", spot = r[2], pref = "fun" }, r),
			"a visitor begins no second visit"
		)
		expect.eq(Visits.inUse(taken, "r", r), 1, "and holds no second spot")
		-- Every spot taken has a visitor behind it.
		for _, t in taken do
			for _, guest in t do
				expect.truthy(visitors[guest] ~= nil, `{guest} recorded`)
			end
		end
	end)

	it(
		"a visit is begun only when the stay has time for the walk and the shortest action",
		function()
			expect.truthy(Visits.fits(nil, 30), "no end set")
			expect.truthy(Visits.fits(30 + C.DoMin, 30), "just enough")
			expect.truthy(not Visits.fits(30 + C.DoMin - 0.1, 30), "a moment short")
			expect.truthy(not Visits.fits(C.DoMin, 1), "the walk counts")
			expect.truthy(not Visits.fits(0, 0), "the stay is over")
		end
	)

	it("the rooms open to visits have a usable spot; one without draws nobody", function()
		local rooms = {
			room("a", "GameRoom", 2),
			room("b", "GameRoom", 0), -- no usable spot
			room("c", "GameRoom", 2, false),
			room("d", "StandardRoom", 2),
		}
		local open = Visits.open(rooms)
		expect.eq(#open, 1, "only a")
		expect.eq(open[1].id, "a")
	end)

	it("a full room is never chosen; its freed spot is", function()
		local rooms = { room("a", "GameRoom", 2) }
		local taken = {}
		for n = 1, 2 do
			local c = Visits.choose({ "fun" }, rooms, taken, 0.3) :: any
			expect.truthy(c, `visitor {n}`)
			expect.truthy(
				Visits.take(taken, c.room, c.spot, rooms[1].spots, `g{n}`),
				`takes spot {c.spot}`
			)
		end
		expect.eq(Visits.choose({ "fun" }, rooms, taken, 0.3), nil, "full")
		Visits.free(taken, "g1")
		local c = Visits.choose({ "fun" }, rooms, taken, 0.3) :: any
		expect.truthy(c and c.spot == rooms[1].spots[1], "the freed spot")
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
					{ room = "a", spot = `p:{n}`, phase = if n % 2 == 0 then "Going" else "Back" }
			end
			visitors.there = { room = "a", spot = "p:99", phase = "There" }
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
			visitors.last = { room = "b", spot = "b1:1", phase = "Going" }
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
			a = { room = "r1", spot = "p:1", phase = "Going" },
			b = { room = "r2", spot = "p:1", phase = "There" },
			c = { room = "r3", spot = "p:1", phase = "Back" },
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
			a = { room = "r1", spot = "p:1", phase = "Going" },
			b = { room = "r1", spot = "p:2", phase = "There" },
			c = { room = "r1", spot = "p:3", phase = "Back" },
			d = { room = "r2", spot = "p:1", phase = "There" },
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
