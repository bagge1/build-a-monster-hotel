--!strict
--[[
	VIP contracts (GDD A.11.1), the pure rules: what the ledger offers, what a
	contract asks, its clock, the daily cap and the reward. Built on the
	draft's scrutinized recommendations (his calls, WAITING §2.38, reversible);
	every number is `Constants.Contracts`, PLACEHOLDER.

	A VIP books ahead: a species of the played hotel's location (sometimes
	with a look), the room it wants (its species' room type) and one or two
	of that room's bars (A.12: Size, Furniture, Decor) at a threshold. The
	ledger offers `Offers` at a time for the hotel being played. The player
	accepts one, builds a room to it and taps Ready; the VIP then rides the
	next Night Bus as an extra seat, booked to that hotel (the service's).

	THE RULES THE SCRUTINY ADDED (A.11.1, "Scrutiny 2026-10-21"):
	- A spec is drawn above the hotel's best room of that type on at least
	  one bar (or the type is not built there), so every contract asks for a
	  change and none is free money (decision 2); an offer a room has come to
	  meet since it was drawn is dropped and drawn anew (`prune`).
	- The clock is play time at the contract's own hotel only: it stands
	  still while the player is at another hotel of the chain (decision 3),
	  and from Ready on (the room is held, the VIP is coming).
	- A missed contract is gone: it is not re-listed, and its slot gets a
	  new draw (decision 3, finding 2).
	- At most `DailyCap` contracts are completed per UTC day, all hotels
	  together; none is accepted that could pass it ("new contracts
	  tomorrow").
	- A Book page may ask for a species' contract (decision 4): it takes the
	  place of an offer and costs one of the day's swaps.

	A LEDGER is what the profile keeps (`PlayerData`'s `contracts`): the offers
	by location, the contracts running, the UTC day's completions and swaps,
	the species whose first contract is done (the souvenir's hook, A.11.3).
	`state` past Accepted (Booked, Arriving, Staying) is the session's: a
	rejoin puts it back to Accepted (`Contracts.loaded`).
]]

local Constants = require(script.Parent.Constants)
local Mutations = require(script.Parent.Mutations)
local Species = require(script.Parent.Species)

local C = Constants.Contracts

local Contracts = {}

export type BarName = "size" | "furniture" | "decor"
export type Bars = { size: number, furniture: number, decor: number }
export type Needs = { size: number?, furniture: number?, decor: number? }
export type Offer = {
	id: number,
	species: string,
	mutation: string?, -- a look (never a season's or a month's), or nil
	type: string, -- the room type (the species' room)
	needs: Needs,
	location: number,
}
export type State = "Accepted" | "Booked" | "Arriving" | "Staying"
export type Contract = {
	id: number,
	species: string,
	mutation: string?,
	type: string,
	needs: Needs,
	location: number,
	state: State,
	played: number, -- seconds of play at its hotel since it was accepted
	room: string?, -- the room held for it (Booked on), a room id
	met: boolean?, -- its room met the spec at check-in
}
export type Ledger = {
	offers: { [string]: { Offer } }, -- by location (tostring)
	active: { Contract },
	day: number, -- the UTC day `done` and `swaps` count
	done: number,
	swaps: number,
	nextId: number,
	first: { [string]: boolean }, -- species whose first contract is done (A.11.3's souvenir)
}
export type Context = {
	location: number,
	rating: number,
	buildable: { [string]: boolean }, -- room types that can be built now (Unlocks)
	best: { [string]: Bars }, -- per room type, each bar's best among the hotel's rooms of it; absent: none built
	-- per room type, each room's own bars: what `prune` asks of a single room (absent: `best` stands in)
	rooms: { [string]: { Bars } }?,
}
export type Refusal =
	"Stars"
	| "Tomorrow"
	| "Busy"
	| "Unknown"
	| "NoSwaps"
	| "Rarity"
	| "Location"
	| "Locked"
	| "Built"

Contracts.BarNames = { "size", "furniture", "decor" } :: { BarName }
Contracts.BarWords = { size = "Size", furniture = "Furniture", decor = "Decor" }

local EPS = 1e-9
local DAY = 86400

function Contracts.day(t: number): number
	return t // DAY
end

function Contracts.newLedger(): Ledger
	return { offers = {}, active = {}, day = 0, done = 0, swaps = 0, nextId = 1, first = {} }
end

-- ===== What the rating opens =====

function Contracts.unlocked(rating: number): boolean
	return rating >= C.UnlockStars
end

-- The rarest VIP's rank (Constants.RarityOrder) drawn at `rating`; 0 below the unlock.
function Contracts.maxRarity(rating: number): number
	if not Contracts.unlocked(rating) then
		return 0
	end
	local best = 0
	for stars, rarity in C.RarityByStars do
		if rating >= stars then
			best = math.max(best, table.find(Constants.RarityOrder, rarity :: any) or 0)
		end
	end
	return best
end

-- How many contracts may run at once (decision 5b).
function Contracts.activeCap(rating: number): number
	return if rating >= C.ActiveFromStars then C.ActiveMore else C.Active
end

-- How many bars a spec asks for.
function Contracts.barCount(rating: number): number
	return if rating >= C.SecondBarStars then 2 else 1
end

-- ===== Specs =====

-- Whether bars meet every need.
function Contracts.meets(needs: Needs, bars: Bars): boolean
	for _, name in Contracts.BarNames do
		local need = (needs :: any)[name]
		if need and (bars :: any)[name] + EPS < need then
			return false
		end
	end
	return true
end

-- Whether a spec asks for more than `best` (each bar's best now) on at least one bar: no room of it meets it.
function Contracts.asksChange(needs: Needs, best: Bars?): boolean
	if not best then
		return true
	end
	for _, name in Contracts.BarNames do
		local need = (needs :: any)[name]
		if need and need > (best :: any)[name] + EPS then
			return true
		end
	end
	return false
end

-- The thresholds of the first bar above `have` (all of them with no room built).
local function above(have: number?): { number }
	local out = {}
	for _, t in C.Thresholds do
		if have == nil or t > have + EPS then
			table.insert(out, t)
		end
	end
	return out
end

-- Whether a spec can still be drawn for a type: some bar of its best room is below the top threshold.
function Contracts.canAsk(best: Bars?): boolean
	if not best then
		return true
	end
	for _, name in Contracts.BarNames do
		if #above((best :: any)[name]) > 0 then
			return true
		end
	end
	return false
end

--[[ A spec for a type whose rooms' best bars are `best` (nil: none built):
	one bar set to a threshold above its best now, and from `SecondBarStars`
	a second bar at `SecondThreshold`. Nil when no bar can be raised. ]]
function Contracts.spec(best: Bars?, rating: number, rand: () -> number): Needs?
	local open: { BarName } = {}
	for _, name in Contracts.BarNames do
		if #above(if best then (best :: any)[name] else nil) > 0 then
			table.insert(open, name)
		end
	end
	if #open == 0 then
		return nil
	end
	local first = open[math.floor(rand() * #open) + 1] or open[1]
	local options = above(if best then (best :: any)[first] else nil)
	local needs: any = {}
	needs[first] = options[math.floor(rand() * #options) + 1] or options[1]
	if Contracts.barCount(rating) >= 2 then
		local others = {}
		for _, name in Contracts.BarNames do
			if name ~= first then
				table.insert(others, name)
			end
		end
		local second = others[math.floor(rand() * #others) + 1] or others[1]
		needs[second] = C.SecondThreshold
	end
	return needs
end

-- A spec in words: "Furniture 50 % · Decor 100 %".
function Contracts.needsText(needs: Needs): string
	local out = {}
	for _, name in Contracts.BarNames do
		local need = (needs :: any)[name]
		if need then
			table.insert(out, `{Contracts.BarWords[name]} {math.floor(need * 100 + 0.5)} %`)
		end
	end
	return table.concat(out, " · ")
end

-- ===== Drawing =====

--[[ Whether `speciesId` can be a VIP for the context, and if not why:
	its location's, no rarer than the rating draws, its room buildable, and
	a spec left to ask of its room. ]]
function Contracts.eligible(ctx: Context, speciesId: string): (boolean, Refusal?)
	local sp = Species.get(speciesId)
	if not sp then
		return false, "Unknown"
	end
	if sp.location ~= ctx.location then
		return false, "Location"
	end
	local rank = table.find(Constants.RarityOrder, sp.rarity) or 99
	if rank > Contracts.maxRarity(ctx.rating) then
		return false, if Contracts.unlocked(ctx.rating) then "Rarity" else "Stars"
	end
	if not ctx.buildable[sp.room] then
		return false, "Locked"
	end
	if not Contracts.canAsk(ctx.best[sp.room]) then
		return false, "Built"
	end
	return true, nil
end

-- The stars a species' VIP needs (the lowest rating that draws its rarity), or nil if none does.
function Contracts.starsFor(speciesId: string): number?
	local sp = Species.get(speciesId)
	local rank = sp and table.find(Constants.RarityOrder, sp.rarity)
	if not rank then
		return nil
	end
	local out: number? = nil
	for stars, rarity in C.RarityByStars do
		local r = table.find(Constants.RarityOrder, rarity :: any) or 0
		if r >= rank and (out == nil or stars < out) then
			out = stars
		end
	end
	return out
end

-- A look for a VIP, sometimes: a plain one (Shadow, Golden, Glitched) by their own odds against each other.
local function look(rand: () -> number): string?
	if rand() >= C.MutationChance then
		return nil
	end
	local rows, total = {}, 0
	for _, m in Mutations.Rollable do
		if m.group == "Look" and m.chance > 0 then
			table.insert(rows, m)
			total += m.chance
		end
	end
	local r = rand() * total
	for _, m in rows do
		r -= m.chance
		if r < 0 then
			return m.id
		end
	end
	return if rows[1] then rows[1].id else nil
end

--[[ One offer for the context, with id `id`: of `speciesId` when given (a
	Book page's request), else a species drawn by `RarityWeights` among the
	eligible. Nil, with the reason, when there is none. ]]
function Contracts.draw(
	ctx: Context,
	id: number,
	rand: () -> number,
	speciesId: string?
): (Offer?, Refusal?)
	local pick: string? = nil
	if speciesId then
		local ok, why = Contracts.eligible(ctx, speciesId)
		if not ok then
			return nil, why
		end
		pick = speciesId
	else
		local pool, total = {}, 0
		for _, sp in Species.ofLocation(ctx.location) do
			if Contracts.eligible(ctx, sp.id) then
				local w = C.RarityWeights[sp.rarity] or 0
				if w > 0 then
					table.insert(pool, { id = sp.id, w = w })
					total += w
				end
			end
		end
		if #pool == 0 then
			return nil, if Contracts.unlocked(ctx.rating) then "Built" else "Stars"
		end
		local r = rand() * total
		for _, e in pool do
			r -= e.w
			if r < 0 then
				pick = e.id
				break
			end
		end
		pick = pick or pool[#pool].id
	end
	local sp = assert(Species.get(pick :: string))
	local needs = Contracts.spec(ctx.best[sp.room], ctx.rating, rand)
	if not needs then
		return nil, "Built"
	end
	return {
		id = id,
		species = sp.id,
		mutation = look(rand),
		type = sp.room,
		needs = needs,
		location = ctx.location,
	},
		nil
end

-- ===== The reward =====

-- `RewardMinutes` of income (`rate`, $/s) × the VIP's rarity's factor.
function Contracts.reward(rate: number, speciesId: string): number
	local sp = Species.get(speciesId)
	local factor = if sp then C.RarityReward[sp.rarity] or 1 else 1
	return math.floor(math.max(0, rate) * C.RewardMinutes * 60 * factor)
end

-- ===== The ledger =====

local function key(location: number): string
	return tostring(location)
end

-- The offers at a location (made when missing).
function Contracts.offersAt(L: Ledger, location: number): { Offer }
	local list = L.offers[key(location)]
	if not list then
		list = {}
		L.offers[key(location)] = list
	end
	return list
end

local function activeAt(L: Ledger, location: number): number
	local n = 0
	for _, c in L.active do
		if c.location == location then
			n += 1
		end
	end
	return n
end

-- A new UTC day: its completions and swaps start at 0.
function Contracts.rollDay(L: Ledger, today: number)
	if L.day ~= today then
		L.day = today
		L.done = 0
		L.swaps = 0
	end
end

-- A rejoin: what the session held (a room, a VIP on its way) is gone, so every contract is Accepted again.
function Contracts.loaded(L: Ledger)
	for _, c in L.active do
		c.state = "Accepted"
		c.room = nil
		c.met = nil
	end
end

local function newId(L: Ledger): number
	local id = L.nextId
	L.nextId += 1
	return id
end

--[[ Tops the played location's offers up to `Offers` less the contracts
	running there, each a new draw. Nothing below the unlock. Returns how
	many were drawn. ]]
function Contracts.fill(L: Ledger, ctx: Context, rand: () -> number): number
	if not Contracts.unlocked(ctx.rating) then
		return 0
	end
	local list = Contracts.offersAt(L, ctx.location)
	local n = 0
	while #list + activeAt(L, ctx.location) < C.Offers do
		local offer = Contracts.draw(ctx, L.nextId, rand)
		if not offer then
			break
		end
		L.nextId += 1
		table.insert(list, offer)
		n += 1
	end
	return n
end

--[[ Drops the offers at the played location that a room of the hotel meets
	now (built since they were drawn, say for a contract like them), so no
	offer is ever free money; `fill` draws their slots anew. Returns how
	many went. ]]
function Contracts.prune(L: Ledger, ctx: Context): number
	local list = Contracts.offersAt(L, ctx.location)
	local n = 0
	for i = #list, 1, -1 do
		local o = list[i]
		-- Met by one room, all of it (A.11.1): two rooms each full on another bar
		-- meet nothing (2026-10-26 review: the bars' best over all rooms dropped those).
		local rooms = ctx.rooms and ctx.rooms[o.type]
		local met = false
		if rooms then
			for _, bars in rooms do
				met = met or Contracts.meets(o.needs, bars)
			end
		else
			met = not Contracts.asksChange(o.needs, ctx.best[o.type])
		end
		if met then
			table.remove(list, i)
			n += 1
		end
	end
	return n
end

-- Whether another contract may be accepted now, and if not why.
function Contracts.canAccept(L: Ledger, rating: number): (boolean, Refusal?)
	if not Contracts.unlocked(rating) then
		return false, "Stars"
	end
	if L.done + #L.active >= C.DailyCap then
		return false, "Tomorrow"
	end
	if #L.active >= Contracts.activeCap(rating) then
		return false, "Busy"
	end
	return true, nil
end

-- Takes offer `id` at `location`: it leaves the offers and runs, its clock at 0.
function Contracts.accept(
	L: Ledger,
	location: number,
	id: number,
	rating: number
): (Contract?, Refusal?)
	local list = Contracts.offersAt(L, location)
	local index: number? = nil
	for i, o in list do
		if o.id == id then
			index = i
		end
	end
	if not index then
		return nil, "Unknown"
	end
	local ok, why = Contracts.canAccept(L, rating)
	if not ok then
		return nil, why
	end
	local o = table.remove(list, index) :: Offer
	local c: Contract = {
		id = o.id,
		species = o.species,
		mutation = o.mutation,
		type = o.type,
		needs = o.needs,
		location = o.location,
		state = "Accepted",
		played = 0,
		room = nil,
		met = nil,
	}
	table.insert(L.active, c)
	return c, nil
end

-- Free swaps left today (`vipLobby`: the pass's +1, as the daily reroll's).
function Contracts.swapsLeft(L: Ledger, vipLobby: boolean): number
	return math.max(0, C.Swaps + (if vipLobby then 1 else 0) - L.swaps)
end

local function replace(
	L: Ledger,
	ctx: Context,
	index: number,
	rand: () -> number,
	speciesId: string?
): Refusal?
	local list = Contracts.offersAt(L, ctx.location)
	local offer, why = Contracts.draw(ctx, L.nextId, rand, speciesId)
	if not offer then
		return why or "Built"
	end
	newId(L)
	if index > #list then
		table.insert(list, offer)
	else
		list[index] = offer
	end
	L.swaps += 1
	return nil
end

-- Swaps offer `id` for a new draw, with one of the day's swaps.
function Contracts.swap(
	L: Ledger,
	ctx: Context,
	id: number,
	rand: () -> number,
	vipLobby: boolean
): Refusal?
	if Contracts.swapsLeft(L, vipLobby) <= 0 then
		return "NoSwaps"
	end
	for i, o in Contracts.offersAt(L, ctx.location) do
		if o.id == id then
			return replace(L, ctx, i, rand, nil)
		end
	end
	return "Unknown"
end

--[[ A Book page's request (decision 4): a contract of `speciesId` takes the
	last offer's place (or an open slot), with one of the day's swaps. ]]
function Contracts.request(
	L: Ledger,
	ctx: Context,
	speciesId: string,
	rand: () -> number,
	vipLobby: boolean
): Refusal?
	if not Contracts.unlocked(ctx.rating) then
		return "Stars"
	end
	if Contracts.swapsLeft(L, vipLobby) <= 0 then
		return "NoSwaps"
	end
	local list = Contracts.offersAt(L, ctx.location)
	for _, o in list do
		if o.species == speciesId then
			return nil -- already offered
		end
	end
	local open = #list + activeAt(L, ctx.location) < C.Offers
	if not open and #list == 0 then
		return "Busy"
	end
	return replace(L, ctx, if open then #list + 1 else #list, rand, speciesId)
end

--[[ `dt` seconds of play at `location`: the clock of each Accepted contract
	there runs (nowhere else, and not from Ready on). A contract past its
	`Deadline` is missed: it is gone, not re-listed. Returns the missed. ]]
function Contracts.tick(L: Ledger, location: number, dt: number): { Contract }
	local missed = {}
	for i = #L.active, 1, -1 do
		local c = L.active[i]
		if c.state == "Accepted" and c.location == location then
			c.played += dt
			if c.played >= C.Deadline then
				table.insert(missed, table.remove(L.active, i) :: Contract)
			end
		end
	end
	return missed
end

-- Seconds of play left on a contract.
function Contracts.left(c: Contract): number
	return math.max(0, C.Deadline - c.played)
end

function Contracts.find(L: Ledger, id: number): Contract?
	for _, c in L.active do
		if c.id == id then
			return c
		end
	end
	return nil
end

local function take(L: Ledger, id: number): Contract?
	for i, c in L.active do
		if c.id == id then
			return table.remove(L.active, i)
		end
	end
	return nil
end

--[[ A happy stay in a room that met the spec: the contract is done and
	counts toward the day's cap. Returns it, and whether it was its
	species' first (the souvenir's hook, A.11.3). ]]
function Contracts.complete(L: Ledger, id: number): (Contract?, boolean)
	local c = take(L, id)
	if not c then
		return nil, false
	end
	L.done += 1
	local first = not L.first[c.species]
	L.first[c.species] = true
	return c, first
end

-- A contract ended without its reward (an unhappy stay, a room that no longer met it): gone, as a missed one.
function Contracts.fail(L: Ledger, id: number): Contract?
	return take(L, id)
end

--[[ A rebirth (§6.4: it takes the chain apart; WAITING §2.48, his yes
	2026-10-26): the offers and the contracts of every hotel not in `kept`
	(by location) end, without penalty. Not missed, not failed: the hotel
	they were for is gone, not the player's doing, and a contract kept for
	it would hold a place in the ledger and the day's cap, its clock never
	running, and an offer drawn at the old rating (a Mythic at 2★) would
	wait for a hotel that no longer earns it. The day's completions and
	swaps and the species' firsts stay. Returns the contracts ended, so the
	service can let their held rooms go. ]]
function Contracts.endHotels(L: Ledger, kept: { [number]: boolean }): { Contract }
	for k in L.offers do
		local location = tonumber(k)
		if not (location and kept[location]) then
			L.offers[k] = nil
		end
	end
	local ended = {}
	for i = #L.active, 1, -1 do
		if not kept[L.active[i].location] then
			table.insert(ended, table.remove(L.active, i) :: Contract)
		end
	end
	return ended
end

return Contracts
