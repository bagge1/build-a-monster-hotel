--!strict
--[[
	VIP contracts (GDD A.11.1), on the draft's scrutinized recommendations
	(his calls, WAITING §2.38; built as reversible PLACEHOLDERs). The rules
	are `Shared/Contracts` (pure, specced); this runs them for each player.

	THE FLOW. From `UnlockStars` the front desk's **VIP ledger** (a prompt on
	every desk, and the HUD's VIP button) offers `Offers` contracts for the
	hotel being played. **Accept** one: its clock (play time at that hotel
	only) starts. Build or refurnish a room of its type to its bars and tap
	**Ready**: a ready, vacant room that meets it is HELD (Reserved, no guest)
	and the clock stops. The VIP rides the street's next Night Bus as an
	EXTRA SEAT (BusService: not counted in its size), steps off booked to the
	hotel (no browse, no Pitch; "VIP for <name>" and a glow over it), waits
	at the desk as long as it takes, and pays `VipPay` × for its stay. A
	HAPPY stay in a room that met the spec at check-in completes it: cash
	(`Contracts.reward`, minutes of income by its rarity) and, the first time
	for a species, its souvenir (`onSouvenir`, A.11.3: `FindService` gives
	it). An unhappy
	stay, or a room that no longer met it, ends it without the reward. A
	contract that runs out is missed: gone, and its slot drawn anew. At most
	`DailyCap` are completed a UTC day.

	A Book page can ask for a species' contract (a swap); a swap redraws an
	offer (1 a day, +1 with VIP Lobby).

	What only the session knows (a held room, a VIP on its way) goes back to
	Accepted on a rejoin or a travel, so a contract is never lost to them;
	its clock is kept. A rebirth ends the contracts and offers of the hotels
	it takes apart, every one, without penalty (`Contracts.endHotels`,
	WAITING §2.48, his yes 2026-10-26), and lets their held rooms go.

	State section `vip`; remote `Vip`; Moments `VipLedger` (open the panel,
	from the desk's prompt) and `VipDone`.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Contracts = require(ReplicatedStorage.Shared.Contracts)
local Format = require(ReplicatedStorage.Shared.Format)
local Locations = require(ReplicatedStorage.Shared.Locations)
local Mutations = require(ReplicatedStorage.Shared.Mutations)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Species = require(ReplicatedStorage.Shared.Species)
local Stay = require(ReplicatedStorage.Shared.Stay)
local Unlocks = require(ReplicatedStorage.Shared.Unlocks)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local BuildService = require(ServerScriptService.Server.BuildService)
local GuestService = require(ServerScriptService.Server.GuestService)
local BusService = require(ServerScriptService.Server.BusService)
local StoreService = require(ServerScriptService.Server.StoreService)
local StateService = require(ServerScriptService.Server.StateService)
local ProgressionService = require(ServerScriptService.Server.ProgressionService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local C = Constants.Contracts

local ContractService = {}

local rng = Random.new()
local function rand(): number
	return rng:NextNumber()
end

-- The session's side of a running contract: its VIP's guest id, and when the bus took it.
type Session = { guest: number?, since: number? }
local sessions: { [Player]: { [number]: Session } } = {}
local devStars: { [Player]: number } = {} -- Studio only (`vipstars`): the rating the ledger reads
local souvenirHandlers: { (Player, string) -> () } = {}

-- Called the first time a species' contract is completed: A.11.3's souvenir (`FindService`).
function ContractService.onSouvenir(handler: (Player, string) -> ())
	table.insert(souvenirHandlers, handler)
end

local function session(player: Player, id: number): Session
	local s = sessions[player]
	if not s then
		s = {}
		sessions[player] = s
	end
	local one = s[id]
	if not one then
		one = {}
		s[id] = one
	end
	return one
end

local function today(): number
	return Contracts.day(os.time())
end

local function ledger(data: PlayerData.Data): Contracts.Ledger
	local L = data.contracts
	Contracts.rollDay(L, today())
	return L
end

local function rating(player: Player): number
	return devStars[player] or HotelService.rating(player)
end

local function speciesName(c: { species: string, mutation: string? }): string
	local sp = Species.get(c.species)
	return Mutations.prefix(nil, c.mutation) .. (if sp then sp.name else c.species)
end

local function typeName(typeId: string): string
	local p = Pieces.get(typeId)
	return if p then p.name else typeId
end

-- Each room type's best bars in the played hotel (per bar, over every room of it), and each room's own.
local function bestBars(
	data: PlayerData.Data
): ({ [string]: Contracts.Bars }, { [string]: { Contracts.Bars } })
	local out: { [string]: Contracts.Bars } = {}
	local rooms: { [string]: { Contracts.Bars } } = {}
	for id, rec in data.rooms do
		local bars = HotelService.roomBars(data, id)
		if bars then
			rooms[rec.type] = rooms[rec.type] or {}
			table.insert(
				rooms[rec.type],
				{ size = bars.size, furniture = bars.furniture, decor = bars.decor }
			)
			local b = out[rec.type]
			if not b then
				out[rec.type] = { size = bars.size, furniture = bars.furniture, decor = bars.decor }
			else
				b.size = math.max(b.size, bars.size)
				b.furniture = math.max(b.furniture, bars.furniture)
				b.decor = math.max(b.decor, bars.decor)
			end
		end
	end
	return out, rooms
end

local function context(player: Player, data: PlayerData.Data): Contracts.Context
	local ctx = BuildService.context(player, data)
	local buildable = {}
	for _, sp in Species.ofLocation(data.location) do
		if buildable[sp.room] == nil then
			buildable[sp.room] = (Unlocks.buildable(sp.room, ctx))
		end
	end
	local best, rooms = bestBars(data)
	return {
		location = data.location,
		rating = rating(player),
		buildable = buildable,
		best = best,
		rooms = rooms,
	}
end

local WHY: { [string]: string } = {
	Stars = `The VIP ledger opens at {C.UnlockStars}★`,
	Tomorrow = "That's today's VIPs: new contracts tomorrow",
	Busy = "Finish the contract you have first",
	Unknown = "That contract isn't there any more",
	NoSwaps = "No swaps left today",
	Rarity = "Your hotel's rating doesn't draw that VIP yet",
	Location = "That monster stays at another hotel",
	Locked = "You can't build its room yet",
	Built = "Your rooms of that type are already as good as a VIP asks",
}

local function refuse(player: Player, why: string)
	Net.fire(player, "Refused", "Vip", WHY[why] or why)
end

-- The room held for a contract, if it is still held for it: ready, Reserved, with no guest yet or its VIP.
local function holdOk(player: Player, c: Contracts.Contract): boolean
	local hotel = HotelService.get(player)
	local room = hotel and c.room and hotel.rooms[c.room]
	if not room or not c.room or not HotelService.ready(player, c.room) then
		return false
	end
	local s = session(player, c.id)
	return room.state == "Reserved" and (room.guest == nil or room.guest == s.guest)
end

-- Releases a held room nobody is in or coming to.
local function release(player: Player, c: Contracts.Contract)
	local hotel = HotelService.get(player)
	local room = hotel and c.room and hotel.rooms[c.room]
	if room and c.room and room.state == "Reserved" and room.guest == nil then
		HotelService.setRoom(player, c.room, "Vacant")
	end
end

-- Back to Accepted (its clock runs again): the hold is let go, the session forgotten.
local function reopen(player: Player, c: Contracts.Contract, why: string?)
	release(player, c)
	c.state = "Accepted"
	c.room = nil
	c.met = nil
	local s = sessions[player]
	if s then
		s[c.id] = nil
	end
	if why then
		Net.fire(player, "Toast", why, "Bad")
	end
	StateService.mark(player)
end

-- A ready, vacant room of the contract's type that meets it; else nil and what is wrong, in words.
local function roomFor(
	player: Player,
	data: PlayerData.Data,
	c: Contracts.Contract
): (string?, string?)
	local hotel = HotelService.get(player)
	if not hotel then
		return nil, "Your hotel isn't loaded"
	end
	local name = typeName(c.type)
	local any, meets = false, false
	local pick: string? = nil
	for id, rec in data.rooms do
		if rec.type == c.type and HotelService.ready(player, id) then
			any = true
			local bars = HotelService.roomBars(data, id)
			if bars and Contracts.meets(c.needs, bars) then
				meets = true
				local room = hotel.rooms[id]
				if
					room
					and room.state == "Vacant"
					and (pick == nil or tonumber(id) < tonumber(pick))
				then
					pick = id
				end
			end
		end
	end
	if pick then
		return pick, nil
	end
	if not any then
		return nil, `Build a ready {name} first`
	elseif not meets then
		return nil, `No {name} meets it yet: {Contracts.needsText(c.needs)}`
	end
	return nil, `Your {name} that meets it isn't free: wait till it's clean and empty`
end

--[[ The income a reward is minutes of (as the dailies', StoreService's), without
	what VIPs staying now pay: a VIP's doubled pay never raises its own reward. ]]
local function baseRate(player: Player): number
	local rate = StoreService.incomeRate(player)
	for _, g in GuestService.of(player) do
		if g.vip and (g.state == "InRoom" or g.state == "Visiting") then -- a visitor pays too (A.13.1)
			rate -= g.payRate
		end
	end
	return math.max(Constants.Economy.BasePay * Constants.Economy.RewardFloor, rate)
end

-- ===== The player's intents =====

local function accept(player: Player, data: PlayerData.Data, id: number)
	local L = ledger(data)
	-- An offer a room meets already is free money (A.11.1 decision 2): dropped, and its slot drawn anew.
	if Contracts.prune(L, context(player, data)) > 0 then
		local still = false
		for _, o in Contracts.offersAt(L, data.location) do
			still = still or o.id == id
		end
		if not still then
			refuse(player, "A room of yours meets that one already: here's a new offer")
			return
		end
	end
	local c, why = Contracts.accept(L, data.location, id, rating(player))
	if not c then
		refuse(player, why or "Unknown")
		return
	end
	Net.fire(
		player,
		"Toast",
		`VIP {speciesName(c)} booked! Build its {typeName(c.type)}, then press Ready.`,
		"Unlock"
	)
	PlayerData.stat(player, "vipAccepted")
end

local function ready(player: Player, data: PlayerData.Data, id: number)
	local c = Contracts.find(ledger(data), id)
	if not c or c.state ~= "Accepted" then
		refuse(player, "Unknown")
		return
	end
	if c.location ~= data.location then
		local loc = Locations.List[c.location]
		refuse(player, `That VIP is coming to your {loc and loc.name or "other hotel"}`)
		return
	end
	local roomId, why = roomFor(player, data, c)
	if not roomId then
		refuse(player, why or "Not ready")
		return
	end
	HotelService.setRoom(player, roomId, "Reserved", nil)
	c.state = "Booked"
	c.room = roomId
	Net.fire(
		player,
		"Toast",
		`Room held. Your VIP {speciesName(c)} comes on the next Night Bus.`,
		"Good"
	)
end

local function cancel(player: Player, data: PlayerData.Data, id: number)
	local c = Contracts.find(ledger(data), id)
	if not c or c.state ~= "Booked" then
		refuse(player, "Unknown")
		return
	end
	reopen(player, c, nil)
end

local function onIntent(player: Player, what: string, arg: string)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local L = ledger(data)
	local id = tonumber(arg) or -1
	local vipLobby = data.passes.VIPLobby == true
	if what == "Accept" then
		accept(player, data, id)
	elseif what == "Ready" then
		ready(player, data, id)
	elseif what == "Cancel" then
		cancel(player, data, id)
	elseif what == "Swap" then
		local why = Contracts.swap(L, context(player, data), id, rand, vipLobby)
		if why then
			refuse(player, why)
		end
	elseif what == "Request" then
		-- A Book page (decision 4): that species' contract in place of an offer, for a swap.
		local why = Contracts.request(L, context(player, data), arg, rand, vipLobby)
		if why then
			local stars = if why == "Rarity" then Contracts.starsFor(arg) else nil
			refuse(player, if stars then `A VIP {arg} needs a {stars}★ hotel` else why)
		else
			local sp = Species.get(arg)
			Net.fire(
				player,
				"Toast",
				`A VIP {sp and sp.name or arg} is in your VIP ledger.`,
				"Unlock"
			)
		end
	end
	StateService.mark(player)
end

-- ===== The bus: extra seats, and stepping off booked =====

local function vipsFor(street: number): { any }
	local out = {}
	for player, data in PlayerData.loaded() do
		local plot = PlotService.of(player)
		if plot and plot.street == street and player.Parent then
			for _, c in ledger(data).active do
				if c.state == "Booked" and c.location == data.location and holdOk(player, c) then
					c.state = "Arriving"
					local s = session(player, c.id)
					s.since = os.clock()
					s.guest = nil
					table.insert(out, {
						species = c.species,
						mutation = c.mutation,
						size = nil,
						booked = player,
						vip = c.id,
						street = street,
					})
					Net.fire(player, "Toast", `Your VIP {speciesName(c)} is on this bus!`, "Rare")
					StateService.mark(player)
				end
			end
		end
	end
	return out
end

local function vipArrives(g: GuestService.Guest, p: any)
	local player = p.booked :: Player?
	local data = player and PlayerData.get(player)
	local c = data and Contracts.find(ledger(data), p.vip)
	if not player or not data or not c or c.state ~= "Arriving" or not holdOk(player, c) then
		GuestService.leaveStreet(g)
		if player and c then
			reopen(player, c, "Your VIP's room wasn't held any more: press Ready again")
		end
		return
	end
	local s = session(player, c.id)
	s.guest = g.id
	GuestService.markVip(g, player)
	GuestService.assign(g, player, c.room :: string)
end

-- The running contract whose VIP is guest `id`.
local function byGuest(player: Player, data: PlayerData.Data, id: number): Contracts.Contract?
	local s = sessions[player]
	if not s then
		return nil
	end
	for _, c in ledger(data).active do
		local one = s[c.id]
		if one and one.guest == id then
			return c
		end
	end
	return nil
end

local function checkedIn(player: Player, g: GuestService.Guest)
	if not g.vip then
		return
	end
	local data = PlayerData.get(player)
	local c = data and byGuest(player, data, g.id)
	if not data or not c or not g.room then
		return
	end
	c.state = "Staying"
	local bars = HotelService.roomBars(data, g.room)
	c.met = bars ~= nil and Contracts.meets(c.needs, bars)
	if not c.met then
		Net.fire(player, "Toast", "Your VIP's room no longer meets its ask: no reward", "Bad")
	end
	StateService.mark(player)
end

local function checkedOut(player: Player, g: GuestService.Guest, satisfaction: number)
	if not g.vip then
		return
	end
	local data = PlayerData.get(player)
	local c = data and byGuest(player, data, g.id)
	if not data or not c then
		return
	end
	local L = ledger(data)
	local s = sessions[player]
	if s then
		s[c.id] = nil
	end
	if not (c.met and Stay.isHappy(satisfaction)) then
		Contracts.fail(L, c.id)
		Net.fire(
			player,
			"Toast",
			if c.met
				then `Your VIP {speciesName(c)} left unhappy ({math.floor(satisfaction)}): no reward`
				else `Your VIP {speciesName(c)}'s room didn't meet its ask: no reward`,
			"Bad"
		)
		PlayerData.stat(player, "vipFailed")
		StateService.mark(player)
		return
	end
	local reward = Contracts.reward(baseRate(player), c.species)
	local done, first = Contracts.complete(L, c.id)
	if not done then
		return
	end
	PlayerData.earn(player, reward)
	PlayerData.stat(player, "vipContracts")
	Net.fire(player, "Moment", "VipDone", {
		species = c.species,
		name = speciesName(c),
		reward = reward,
		first = first,
		done = L.done,
		cap = C.DailyCap,
	})
	Net.fire(player, "Toast", `VIP contract done! +{Format.cash(reward)}`, "Unlock")
	if first then
		-- A.11.3's souvenir: FindService gives it (whichever first: this or the species' 3rd move-in).
		PlayerData.stat(player, `vipFirst_{c.species}`)
		for _, h in souvenirHandlers do
			task.spawn(h, player, c.species)
		end
	end
	StateService.mark(player)
end

-- ===== Each second =====

local function tickPlayer(player: Player, data: PlayerData.Data, dt: number)
	local L = ledger(data)
	for _, c in Contracts.tick(L, data.location, dt) do
		Net.fire(player, "Toast", `Your VIP contract for {speciesName(c)} ran out.`, "Bad")
		PlayerData.stat(player, "vipMissed")
		StateService.mark(player)
	end
	for _, c in table.clone(L.active) do
		local s = sessions[player] and (sessions[player] :: any)[c.id]
		if c.state == "Booked" then
			if c.location ~= data.location then
				reopen(player, c, nil) -- travelled or reborn: the hotel's rooms are another's
			elseif not holdOk(player, c) then
				local hotel = HotelService.get(player)
				local room = hotel and c.room and hotel.rooms[c.room]
				if
					room
					and room.state == "Vacant"
					and c.room
					and HotelService.ready(player, c.room)
				then
					-- Rebuilt (a sync makes a new room Vacant): hold it again.
					HotelService.setRoom(player, c.room, "Reserved", nil)
				else
					reopen(player, c, "Your VIP's room isn't ready any more: press Ready again")
				end
			end
		elseif c.state == "Arriving" then
			local guest = s and s.guest
			if guest then
				-- Gone, or sent home on the way in (no path to its room, the held room sold): a guest walking
				-- back to the bus still exists, so its state says it is not coming.
				local g = GuestService.get(guest)
				if
					not g
					or g.state == "Leaving"
					or g.state == "Waiting"
					or g.state == "Boarding"
				then
					reopen(player, c, "Your VIP had to leave: press Ready again")
				end
			elseif not s or os.clock() - (s.since or 0) > C.ArrivalGrace then
				reopen(player, c, nil)
			end
		elseif c.state == "Staying" then
			local guest = s and s.guest
			if not guest or not GuestService.get(guest) then
				reopen(player, c, "Your VIP had to leave: press Ready again")
			end
		end
	end
end

-- ===== What the panel draws =====

local function offerRow(o: any, rate: number): { [string]: any }
	local sp = Species.get(o.species)
	return {
		id = o.id,
		species = o.species,
		name = speciesName(o),
		rarity = if sp then sp.rarity else "Common",
		prefs = if sp then sp.prefs else {},
		type = o.type,
		typeName = typeName(o.type),
		needs = o.needs,
		needsText = Contracts.needsText(o.needs),
		reward = Contracts.reward(rate, o.species),
		location = o.location,
	}
end

local function provide(player: Player, data: PlayerData.Data): { [string]: any }
	local L = ledger(data)
	local ctx = context(player, data)
	Contracts.prune(L, ctx)
	Contracts.fill(L, ctx, rand)
	local rate = baseRate(player)
	local offers = {}
	for _, o in Contracts.offersAt(L, data.location) do
		table.insert(offers, offerRow(o, rate))
	end
	local active = {}
	for _, c in L.active do
		local row = offerRow(c, rate)
		row.state = c.state
		row.left = Contracts.left(c)
		row.room = c.room
		row.here = c.location == data.location
		local loc = Locations.List[c.location]
		row.locationName = loc and loc.name or ""
		local best = ctx.best[c.type]
		row.best = if best and row.here then Contracts.needsText(best :: any) else ""
		if c.state == "Accepted" and row.here then
			local roomId, why = roomFor(player, data, c)
			row.canReady = roomId ~= nil
			row.why = why or ""
		end
		table.insert(active, row)
	end
	local requestable = {}
	if Contracts.unlocked(ctx.rating) then
		for _, sp in Species.ofLocation(data.location) do
			if Contracts.eligible(ctx, sp.id) then
				requestable[sp.id] = true
			end
		end
	end
	local canAccept, why = Contracts.canAccept(L, ctx.rating)
	return {
		unlocked = Contracts.unlocked(ctx.rating),
		stars = ctx.rating,
		unlockStars = C.UnlockStars,
		done = L.done,
		cap = C.DailyCap,
		swaps = Contracts.swapsLeft(L, data.passes.VIPLobby == true),
		activeCap = Contracts.activeCap(ctx.rating),
		canAccept = canAccept,
		why = if why then WHY[why] or why else "",
		deadline = C.Deadline,
		offers = offers,
		active = active,
		requestable = requestable,
	}
end

function ContractService.Init()
	Net.on("Vip", onIntent)
end

function ContractService.Start()
	PlayerData.onLoaded(function(_player, data)
		Contracts.loaded(data.contracts)
	end)
	PlayerData.onDeparted(function(player)
		sessions[player] = nil
		devStars[player] = nil
	end)
	StateService.provide("vip", provide)
	--[[ A rebirth takes every hotel of the chain apart, Haunted Manor's too (its
		rooms, its rating from the start), so no hotel of the ledger is kept: its
		contracts and offers end without penalty (no `vipMissed`, nothing toward
		the day's cap), and a held room is let go while it is still the hotel's.
		WAITING §2.48, his yes 2026-10-26. ]]
	ProgressionService.onRebirthStart(function(player)
		local data = PlayerData.get(player)
		if not data then
			return
		end
		local s = sessions[player]
		for _, c in Contracts.endHotels(ledger(data), {}) do
			release(player, c)
			if s then
				s[c.id] = nil
			end
		end
		StateService.mark(player)
	end)
	BusService.setVips(vipsFor :: any, vipArrives)
	GuestService.onCheckIn(checkedIn)
	GuestService.onCheckout(checkedOut)
	PlotService.onPrompt(function(player, _plot, kind)
		if kind == "Vip" then
			StateService.mark(player)
			Net.fire(player, "Moment", "VipLedger", {})
		end
	end)
	task.spawn(function()
		local last = os.clock()
		while true do
			task.wait(1)
			local now = os.clock()
			local dt = now - last
			last = now
			for player, data in PlayerData.loaded() do
				local ok, err = pcall(tickPlayer, player, data, dt)
				if not ok then
					warn(`[vip] {player.Name}: {err}`)
				end
			end
		end
	end)
	-- The ledger's clocks and rewards move: the panel is sent again now and then.
	task.spawn(function()
		while true do
			task.wait(20)
			for player, data in PlayerData.loaded() do
				if #data.contracts.active > 0 then
					StateService.mark(player)
				end
			end
		end
	end)

	-- Studio only (DevGrant): see and steer the ledger without waiting for a rating or 45 minutes.
	DevGrant.register("vip", function(player)
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		local L = ledger(data)
		local out = { `rating {rating(player)} done {L.done}/{C.DailyCap} swaps used {L.swaps}` }
		for _, o in Contracts.offersAt(L, data.location) do
			table.insert(
				out,
				`offer {o.id} {speciesName(o)} {o.type} {Contracts.needsText(o.needs)}`
			)
		end
		for _, c in L.active do
			table.insert(
				out,
				`active {c.id} {speciesName(c)} {c.type} {Contracts.needsText(c.needs)} {c.state} played {math.floor(
					c.played
				)} room {c.room or "-"} guest {(
					sessions[player] and (sessions[player] :: any)[c.id] or {}
				).guest or "-"}`
			)
		end
		return table.concat(out, " | ")
	end)
	DevGrant.register("vipstars", function(player, args)
		devStars[player] = tonumber(args[1])
		StateService.mark(player)
		return `ledger reads {rating(player)}★`
	end)
	DevGrant.register("vipclock", function(player, args)
		-- `vipclock <seconds>`: that much play at the played hotel, now.
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		tickPlayer(player, data, tonumber(args[1]) or 60)
		return `ok, {#data.contracts.active} running`
	end)
	DevGrant.register("vipoffer", function(player, args)
		-- `vipoffer <species> <bar>=<share> ...`: offer 1 replaced by exactly that (a known test).
		local data = PlayerData.get(player)
		local sp = Species.get(args[1] or "")
		if not data or not sp then
			return "no such species"
		end
		local needs = {}
		for i = 2, #args do
			local bar, v = string.match(args[i], "^(%a+)=([%d%.]+)$")
			if bar then
				(needs :: any)[bar] = tonumber(v)
			end
		end
		local L = ledger(data)
		local list = Contracts.offersAt(L, data.location)
		local offer = {
			id = L.nextId,
			species = sp.id,
			mutation = nil,
			type = sp.room,
			needs = needs,
			location = data.location,
		}
		L.nextId += 1
		list[1] = offer
		StateService.mark(player)
		return `offer {offer.id} {sp.id} {Contracts.needsText(needs)}`
	end)
	DevGrant.register("vipdone", function(player, args)
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		ledger(data).done = tonumber(args[1]) or 0
		StateService.mark(player)
		return `done {data.contracts.done}`
	end)
	DevGrant.register("vipreset", function(player)
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		for _, c in data.contracts.active do
			release(player, c)
		end
		data.contracts = Contracts.newLedger()
		sessions[player] = nil
		StateService.mark(player)
		return "ledger reset"
	end)
end

return ContractService
