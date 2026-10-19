--!strict
--[[
	The Night Bus (GDD §4.3): the shared arrivals six hotels compete for.

	Every `Interval` seconds a bus stops at the west end of Creepy Lane with
	6–10 guests (`Bus.size`), including its guarantees (an Epic every third
	bus, a Legendary on the half hours, a Mythic on the Midnight Bus). Each
	guest walks the lane east showing its wish list; players **pitch** guests
	they want (+15 % toward their hotel, one pitch per player per guest). At the
	lane's end each guest scores every hotel (`Scoring`) and walks to the best
	one with a vacant room of its type, or leaves the street.

	ONE BUS AHEAD, the rare guest is announced to the whole server (§4.3), so
	players can build or free the room it wants. The next bus's passengers are
	drawn when the previous bus arrives, which is what makes that possible.

	Published on `workspace`: `NextBusAt` and `BusArrivedAt` (server time), so
	every client draws the bus and the countdown.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Bus = require(ReplicatedStorage.Shared.Bus)
local Constants = require(ReplicatedStorage.Shared.Constants)
local Events = require(ReplicatedStorage.Shared.Events)
local Mutations = require(ReplicatedStorage.Shared.Mutations)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Scoring = require(ReplicatedStorage.Shared.Scoring)
local Species = require(ReplicatedStorage.Shared.Species)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local GuestService = require(ServerScriptService.Server.GuestService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local B = Constants.Bus

local BusService = {}

type Passenger = { species: string, mutation: string? }

local rng = Random.new()
local busIndex = 0
local lastArrival = 0 -- server clock (os.time) of the previous bus
local nextAt = 0 -- os.clock() of the next bus
local nextList: { Passenger }? = nil
local busScoreProviders: { (Player) -> number } = {}
local extraGuests: { Passenger } = {} -- added to the next bus (the tutorial, Hunter Night's thank-you)
local arrivedHandlers: { (number) -> () } = {}

-- A provider of a hotel's bus-score bonus as a fraction (the Moon Tree's +5 %, §6.5).
function BusService.addScoreBonus(provider: (Player) -> number)
	table.insert(busScoreProviders, provider)
end

function BusService.onArrived(handler: (number) -> ())
	table.insert(arrivedHandlers, handler)
end

-- Adds guests to the next bus.
function BusService.addToNext(speciesId: string, mutation: string?)
	table.insert(extraGuests, { species = speciesId, mutation = mutation })
end

local function locationsPresent(): { [number]: boolean }
	local set = {}
	for _, data in PlayerData.loaded() do
		set[data.location] = true
	end
	if next(set) == nil then
		set[1] = true
	end
	return set
end

local function draw(index: number, previous: number, at: number): { Passenger }
	local flags = Bus.flags(index, previous, at)
	local ids = Bus.passengers(
		flags,
		Bus.size(#Players:GetPlayers()),
		locationsPresent(),
		function()
			return rng:NextNumber()
		end,
		Events.weights(at)
	)
	local list = {}
	for _, id in ids do
		table.insert(list, { species = id, mutation = Events.rollMutation(rng:NextNumber(), at) })
	end
	return list
end

local function wishText(p: Passenger): string
	local sp = assert(Species.get(p.species))
	local room = Pieces.get(sp.room)
	return `Wants: {room and room.name or sp.room} · {table.concat(sp.prefs, " · ")}`
end

local function rarest(list: { Passenger }): Passenger?
	local best, bestRank = nil, 0
	for _, p in list do
		local sp = Species.get(p.species)
		local rank = sp and table.find(Constants.RarityOrder, sp.rarity) or 0
		if rank > bestRank then
			best, bestRank = p, rank
		end
	end
	return best
end

-- Tells the street about the next bus's rare guest (§4.3), Legendary and up.
local function announceNext(list: { Passenger })
	local p = rarest(list)
	local sp = p and Species.get(p.species)
	if not p or not sp then
		return
	end
	local rank = table.find(Constants.RarityOrder, sp.rarity) or 0
	if rank >= (table.find(Constants.RarityOrder, "Legendary") :: number) then
		local mutation = if p.mutation then Mutations.ById[p.mutation].name .. " " else ""
		Net.fireAll(
			"Announce",
			`A {sp.rarity} {mutation}{sp.name} is on the next bus! {wishText(p)}`,
			"Rare"
		)
	end
end

-- Where a guest goes at the lane's end: the best-scoring hotel with a vacant room of its type.
local function decide(g: GuestService.Guest)
	local sp = Species.get(g.species)
	if not sp then
		GuestService.leaveStreet(g)
		return
	end
	local candidates: { Scoring.Candidate } = {}
	local jitters = {}
	local here = GuestService.positionOf(g)
	for _, plot in PlotService.all() do
		local owner = plot.owner
		if owner then
			local offer = HotelService.vacantFor(owner, g.species)
			local bonus = 0
			for _, f in busScoreProviders do
				local ok, v = pcall(f, owner)
				if ok and typeof(v) == "number" then
					bonus += v
				end
			end
			table.insert(candidates, {
				id = owner,
				eligible = offer ~= nil,
				rating = HotelService.rating(owner),
				prefsMatched = if offer then offer.prefsMatched else 0,
				amenityBonus = if offer then offer.amenities else 0,
				pitched = g.pitches[owner.UserId] ~= nil,
				busBonus = bonus,
				distance = (StreetLayout.laneFront(plot.index) - here).Magnitude,
			})
			table.insert(jitters, Scoring.jitter(rng:NextNumber()))
		end
	end
	local best = Scoring.pick(candidates, sp.rarity, jitters)
	if not best then
		GuestService.leaveStreet(g)
		return
	end
	local owner = best.id :: Player
	local offer = HotelService.vacantFor(owner, g.species)
	if not offer then
		GuestService.leaveStreet(g)
		return
	end
	g.config:SetAttribute("Wish", nil)
	GuestService.assign(g, owner, offer.pieceId)
	if sp.rarity == "Legendary" or sp.rarity == "Mythic" or sp.rarity == "Epic" then
		Net.fireAll("Announce", `The {sp.name} chose {owner.DisplayName}'s hotel!`, "Rare")
	end
	PlayerData.stat(owner, "busGuests")
end

local function arrive()
	busIndex += 1
	local now = os.time()
	local list = nextList or draw(busIndex, lastArrival, now)
	for _, extra in extraGuests do
		table.insert(list, extra)
	end
	table.clear(extraGuests)
	lastArrival = now
	workspace:SetAttribute("BusArrivedAt", workspace:GetServerTimeNow())
	workspace:SetAttribute("BusIndex", busIndex)
	Net.fireAll("Announce", "The Night Bus has arrived!", "Bus")
	for i, p in list do
		local at = StreetLayout.BusStop
			+ Vector3.new(-(i - 1) * B.GuestSpacing * 0.3, 0, ((i % 3) - 1) * 2)
		task.delay((i - 1) * 0.6, function()
			local g = GuestService.spawnBrowsing(p.species, p.mutation, at, wishText(p), decide)
			local _ = g
		end)
	end
	for _, h in arrivedHandlers do
		task.spawn(h, busIndex)
	end
	-- Draw the next bus now, so its rare guest can be announced a bus ahead.
	-- A Monster Parade (§8.2) runs a bus a minute.
	local interval = if Events.parade(now) then Events.ParadeInterval else B.Interval
	nextAt = os.clock() + interval
	workspace:SetAttribute("NextBusAt", workspace:GetServerTimeNow() + interval)
	nextList = draw(busIndex + 1, now, now + interval)
	announceNext(nextList :: { Passenger })
end

-- Brings the next bus now (Call the Bus, §10.2: "for the whole server").
function BusService.callNow(byName: string?)
	if byName then
		Net.fireAll("Announce", `{byName} called the bus!`, "Bus")
	end
	nextAt = os.clock()
end

-- A pitch (§4.3): toward the pitcher's hotel, once per player per guest, within reach.
local function pitch(player: Player, guestId: number)
	local g = GuestService.get(guestId)
	local plot = PlotService.of(player)
	local character = player.Character
	if not g or not plot or not character or g.state ~= "Browsing" then
		return
	end
	if g.pitches[player.UserId] then
		return
	end
	local d = (character:GetPivot().Position - GuestService.positionOf(g)).Magnitude
	if d > Constants.Scoring.PitchRange + 4 then -- a little slack for the client's drawing
		Net.fire(player, "Refused", "Pitch", "Too far away")
		return
	end
	g.pitches[player.UserId] = plot.index
	PlayerData.stat(player, "pitches")
	Net.fire(player, "Toast", "Pitched! +15% toward your hotel", "Good")
end

function BusService.nextIn(): number
	return math.max(0, nextAt - os.clock())
end

function BusService.Init()
	Net.on("Pitch", pitch)
end

function BusService.Start()
	DevGrant.register("bus", function()
		BusService.callNow(nil)
		return "bus called"
	end)
	DevGrant.register("nextbus", function()
		local names = {}
		for _, p in nextList or {} do
			table.insert(names, p.species .. (if p.mutation then "(" .. p.mutation .. ")" else ""))
		end
		return `in {math.floor(BusService.nextIn())}s: {table.concat(names, ", ")}`
	end)
	DevGrant.register("decide", function()
		-- Ends every browse now (to see the choices without waiting for the walk).
		for _, g in GuestService.all() do
			if g.state == "Browsing" then
				g.arriveAt = os.clock()
			end
		end
		return "ok"
	end)
	lastArrival = os.time()
	nextAt = os.clock() + B.FirstBusDelay
	workspace:SetAttribute("NextBusAt", workspace:GetServerTimeNow() + B.FirstBusDelay)
	nextList = draw(1, lastArrival, lastArrival + B.FirstBusDelay)
	task.spawn(function()
		while true do
			task.wait(0.5)
			if os.clock() >= nextAt then
				local ok, err = pcall(arrive)
				if not ok then
					warn(`[bus] arrival failed: {err}`)
					nextAt = os.clock() + B.Interval
				end
			end
		end
	end)
end

return BusService
