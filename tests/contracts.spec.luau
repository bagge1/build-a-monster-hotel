local Constants = require(Shared.Constants)
local Contracts = require(Shared.Contracts)
local Species = require(Shared.Species)
local Mutations = require(Shared.Mutations)

local C = Constants.Contracts

describe("VIP contracts (A.11.1)", function()
	local rng = Random.new(1021)
	local function rand(): number
		return rng:NextNumber()
	end

	-- Every room type of a location's species, buildable.
	local function allBuildable(location: number): { [string]: boolean }
		local out = {}
		for _, sp in Species.ofLocation(location) do
			out[sp.room] = true
		end
		return out
	end

	-- A random hotel: some types built, their best bars anywhere in 0..1 (often a threshold exactly).
	local function randomBest(location: number): { [string]: any }
		local out = {}
		local steps = { 0, 0.25, 0.5, 0.75, 1 }
		for t in allBuildable(location) do
			if rand() < 0.6 then
				out[t] = {
					size = steps[rng:NextInteger(1, #steps)],
					furniture = steps[rng:NextInteger(1, #steps)],
					decor = steps[rng:NextInteger(1, #steps)],
				}
			end
		end
		return out
	end

	local function ctx(rating: number, location: number?, best: any?): Contracts.Context
		local loc = location or 1
		return {
			location = loc,
			rating = rating,
			buildable = allBuildable(loc),
			best = best or {},
		}
	end

	it("the ledger is shut below its stars and offers nothing there", function()
		local low = C.UnlockStars - 0.5
		expect.truthy(not Contracts.unlocked(low), "unlocked below")
		expect.truthy(Contracts.unlocked(C.UnlockStars), "unlocked at")
		expect.eq(Contracts.maxRarity(low), 0)
		local L = Contracts.newLedger()
		expect.eq(Contracts.fill(L, ctx(low), rand), 0)
		local ok, why = Contracts.canAccept(L, low)
		expect.truthy(not ok and why == "Stars", "accept below the stars")
		local o = Contracts.draw(ctx(low), 1, rand)
		expect.truthy(o == nil, "a draw below the stars")
	end)

	it("a better rating never draws rarer VIPs less, runs fewer at once or asks fewer bars", function()
		local last = { 0, 0, 0 }
		for tenth = 10, 50 do
			local r = tenth / 10
			local now = { Contracts.maxRarity(r), Contracts.activeCap(r), Contracts.barCount(r) }
			for i = 1, 3 do
				expect.truthy(now[i] >= last[i], `rule {i} at {r}`)
			end
			last = now
		end
		expect.truthy(Contracts.maxRarity(5) > Contracts.maxRarity(C.UnlockStars), "5★ draws rarer than the unlock")
	end)

	it("every offer is its location's, within the rating's rarity, of a buildable type, and asks for a change", function()
		for n = 1, 400 do
			local location = if n % 2 == 0 then 1 else 2
			local rating = C.UnlockStars + rand() * (5 - C.UnlockStars)
			local best = randomBest(location)
			local c = ctx(rating, location, best)
			local o = Contracts.draw(c, n, rand)
			if o then
				local sp = assert(Species.get(o.species))
				expect.eq(sp.location, location, "location")
				expect.eq(o.location, location, "offer's location")
				expect.eq(o.type, sp.room, "its species' room")
				expect.truthy(c.buildable[o.type], "buildable")
				local rank = table.find(Constants.RarityOrder, sp.rarity) :: number
				expect.atMost(rank, Contracts.maxRarity(rating), "rarity")
				expect.truthy(Contracts.asksChange(o.needs, best[o.type]), `asks a change ({n})`)
				if best[o.type] then
					expect.truthy(not Contracts.meets(o.needs, best[o.type]), "the best room does not meet it")
				end
				local bars = 0
				for _, name in Contracts.BarNames do
					local need = (o.needs :: any)[name]
					if need then
						bars += 1
						expect.truthy(need > 0 and need <= 1, "a need is a share of a bar")
					end
				end
				expect.eq(bars, Contracts.barCount(rating), "bars asked")
				expect.truthy(Contracts.meets(o.needs, { size = 1, furniture = 1, decor = 1 }), "full bars meet it")
				if o.mutation then
					local m = Mutations.ById[o.mutation]
					expect.truthy(m and m.group == "Look" and not m.event, "a plain look, never a season's or month's")
				end
			end
		end
	end)

	it("an offer a room has come to meet is dropped, and its slot drawn anew", function()
		local L = Contracts.newLedger()
		local c = ctx(3, 1)
		Contracts.fill(L, c, rand)
		local before = {}
		for _, o in Contracts.offersAt(L, 1) do
			before[o.id] = true
		end
		local met = Contracts.offersAt(L, 1)[1]
		local built = table.clone(c.best)
		built[met.type] = { size = 1, furniture = 1, decor = 1 }
		local after = ctx(3, 1, built)
		expect.truthy(Contracts.prune(L, after) >= 1, "pruned")
		for _, o in Contracts.offersAt(L, 1) do
			expect.truthy(Contracts.asksChange(o.needs, built[o.type]), "every offer left asks a change")
		end
		Contracts.fill(L, after, rand)
		for _, o in Contracts.offersAt(L, 1) do
			expect.truthy(Contracts.asksChange(o.needs, built[o.type]), "every new one too")
			if not before[o.id] then
				expect.truthy(o.id > met.id, "a new draw")
			end
		end
	end)

	it("a type whose rooms are full on every bar is never asked for", function()
		local full = {}
		for t in allBuildable(1) do
			full[t] = { size = 1, furniture = 1, decor = 1 }
		end
		expect.truthy(Contracts.draw(ctx(5, 1, full), 1, rand) == nil, "nothing left to ask")
		local ok, why = Contracts.eligible(ctx(5, 1, full), "Slime")
		expect.truthy(not ok and why == "Built", "Built")
	end)

	it("meeting a spec is never undone by better bars", function()
		for _ = 1, 200 do
			local needs = Contracts.spec(nil, 5, rand) :: Contracts.Needs
			local bars = { size = rand(), furniture = rand(), decor = rand() }
			if Contracts.meets(needs, bars) then
				local up = {
					size = math.min(1, bars.size + rand() * 0.3),
					furniture = math.min(1, bars.furniture + rand() * 0.3),
					decor = math.min(1, bars.decor + rand() * 0.3),
				}
				expect.truthy(Contracts.meets(needs, up), "raised bars")
			end
		end
	end)

	it("the reward grows with the VIP's rarity and the income, and is never negative", function()
		local byRarity = {}
		for _, sp in Species.ofLocation(1) do
			byRarity[sp.rarity] = sp.id
		end
		local last = 0
		for _, rarity in Constants.RarityOrder do
			local id = byRarity[rarity]
			if id then
				local r = Contracts.reward(100, id)
				expect.truthy(r >= last, `{rarity}`)
				expect.truthy(Contracts.reward(200, id) >= r, "more income")
				last = r
			end
		end
		expect.eq(Contracts.reward(-5, "Slime"), 0)
	end)

	it("the clock runs only at the contract's own hotel, only before Ready, and a miss loses the offer", function()
		local L = Contracts.newLedger()
		local c = ctx(3, 1)
		Contracts.fill(L, c, rand)
		local offers = Contracts.offersAt(L, 1)
		expect.eq(#offers, C.Offers, "a full ledger")
		local first = offers[1].id
		local k = assert(Contracts.accept(L, 1, first, 3))
		expect.eq(#Contracts.offersAt(L, 1), C.Offers - 1, "its slot is the contract's")
		expect.eq(Contracts.fill(L, c, rand), 0, "no refill while it runs")
		Contracts.tick(L, 2, C.Deadline * 2)
		expect.eq(k.played, 0, "another hotel's play")
		k.state = "Booked"
		Contracts.tick(L, 1, C.Deadline * 2)
		expect.eq(k.played, 0, "booked: the VIP is coming")
		k.state = "Accepted"
		local missed = Contracts.tick(L, 1, C.Deadline - 1)
		expect.eq(#missed, 0, "not before the deadline")
		missed = Contracts.tick(L, 1, 1)
		expect.eq(#missed, 1, "missed at the deadline")
		expect.truthy(Contracts.find(L, first) == nil, "gone")
		expect.eq(Contracts.fill(L, c, rand), 1, "its slot drawn anew")
		for _, o in Contracts.offersAt(L, 1) do
			expect.truthy(o.id ~= first, "the missed offer is not re-listed")
		end
	end)

	it("never more than the daily cap completed, and none accepted that could pass it", function()
		local L = Contracts.newLedger()
		Contracts.rollDay(L, 100)
		local c = ctx(5, 1)
		local completed = 0
		for _ = 1, 50 do
			Contracts.fill(L, c, rand)
			local offers = Contracts.offersAt(L, 1)
			if #offers > 0 then
				Contracts.accept(L, 1, offers[1].id, 5)
			end
			expect.atMost(L.done + #L.active, C.DailyCap, "done and running")
			local running = L.active[1]
			if running then
				Contracts.complete(L, running.id)
				completed += 1
			end
		end
		expect.eq(completed, C.DailyCap, "completions in a day")
		local ok, why = Contracts.canAccept(L, 5)
		expect.truthy(not ok and why == "Tomorrow", "new contracts tomorrow")
		Contracts.rollDay(L, 101)
		expect.truthy((Contracts.canAccept(L, 5)), "a new day")
	end)

	it("running contracts are capped by the rating", function()
		for _, rating in { C.UnlockStars, 5 } do
			local L = Contracts.newLedger()
			local c = ctx(rating, 1)
			Contracts.fill(L, c, rand)
			for _, o in table.clone(Contracts.offersAt(L, 1)) do
				Contracts.accept(L, 1, o.id, rating)
			end
			expect.eq(#L.active, math.min(Contracts.activeCap(rating), C.DailyCap), `at {rating}`)
		end
	end)

	it("a swap or a Book page's request costs one of the day's swaps, and a request is that species", function()
		local L = Contracts.newLedger()
		local c = ctx(5, 1)
		Contracts.fill(L, c, rand)
		local swaps = Contracts.swapsLeft(L, false)
		expect.truthy(swaps >= 1, "a swap a day")
		expect.eq(Contracts.swapsLeft(L, true), swaps + 1, "VIP Lobby's one more")
		local before = #Contracts.offersAt(L, 1)
		local why = Contracts.request(L, c, "VampireCount", rand, false)
		expect.truthy(why == nil, `request: {why}`)
		local found = false
		for _, o in Contracts.offersAt(L, 1) do
			found = found or o.species == "VampireCount"
		end
		expect.truthy(found, "the species requested")
		expect.eq(#Contracts.offersAt(L, 1), before, "it takes an offer's place")
		expect.eq(Contracts.swapsLeft(L, false), swaps - 1, "a swap spent")
		while Contracts.swapsLeft(L, false) > 0 do
			Contracts.swap(L, c, Contracts.offersAt(L, 1)[1].id, rand, false)
		end
		expect.eq(Contracts.swap(L, c, Contracts.offersAt(L, 1)[1].id, rand, false), "NoSwaps")
		expect.eq(Contracts.request(L, c, "Slime", rand, false), "NoSwaps")
		-- A species the rating does not reach is refused.
		local L2 = Contracts.newLedger()
		local low = ctx(C.UnlockStars, 1)
		Contracts.fill(L2, low, rand)
		expect.eq(Contracts.request(L2, low, "GrandBanshee", rand, false), "Rarity")
		expect.truthy((Contracts.starsFor("GrandBanshee") or 99) > C.UnlockStars, "its stars named")
	end)

	it("a rejoin puts every contract back to Accepted, and only a species' first completion is first", function()
		local L = Contracts.newLedger()
		local c = ctx(5, 1)
		Contracts.fill(L, c, rand)
		local k = assert(Contracts.accept(L, 1, Contracts.offersAt(L, 1)[1].id, 5))
		k.state = "Staying"
		k.room = "7"
		Contracts.loaded(L)
		expect.eq(k.state, "Accepted")
		expect.truthy(k.room == nil, "no room held")
		local done, first = Contracts.complete(L, k.id)
		expect.truthy(done ~= nil and first, "first")
		L.done = 0
		Contracts.fill(L, c, rand)
		Contracts.request(L, c, k.species, rand, true)
		for _, o in table.clone(Contracts.offersAt(L, 1)) do
			if o.species == k.species then
				local again = assert(Contracts.accept(L, 1, o.id, 5))
				local _, second = Contracts.complete(L, again.id)
				expect.truthy(not second, "not first again")
				break
			end
		end
	end)
end)
