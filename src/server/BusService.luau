--!strict
--[[
	The Night Bus (GDD §4.3): the shared arrivals six hotels compete for.

	Every `Interval` seconds a bus drives out of the forest and stops twice on
	Creepy Lane (x = −90 and 90, his ruling 2026-10-19), letting half its
	guests off at each. It carries 40 % of the street's vacant rooms (`Bus.size`),
	including its guarantees (an Epic every third bus, a Legendary on the half
	hours, a Mythic on the Midnight Bus). Each guest browses the pavements for
	about a minute, pausing at every hotel's entrance and showing its wish
	list; players **pitch** guests they want (+15 % toward their hotel, one
	pitch per player per guest). Then each guest scores every hotel
	(`Scoring`) and walks to the best one with a vacant room of its type, or
	back to a stop to leave on the next bus. At each stop the bus also takes
	away the guests waiting there.

	ONE BUS AHEAD, the rare guest is announced to the whole server (§4.3), so
	players can build or free the room it wants. The next bus's passengers are
	drawn when the previous bus arrives, which is what makes that possible.

	THE TUTORIAL'S COMMONS (§11 1:45, "The tutorial weights Commons toward
	your hotel"): on the first `Tutorial.CommonBuses` buses of a new player's
	tutorial (the hotels `setTutorialHotels` names), Commons their vacant
	rooms can take ride in place of the bus's drawn guests, never its
	guarantees and never more than the bus's size (his 40 %). They browse like
	any guest, so the player can pitch one, and score `TutorialBoost` toward
	that hotel (`Scoring`). Each bus that brought a hotel some counts in its
	`tutorialCommonBuses` stat.

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

-- `booked`: a guest coming to one hotel (the tutorial's Vampire Count, §11), which skips browsing.
-- `tutorialFor`: a Common the tutorial brought for that hotel (§11 1:45), which browses and scores toward it.
type Passenger = {
	species: string,
	mutation: string?,
	booked: Player?,
	happyFloor: number?,
	tutorialFor: Player?,
}

local rng = Random.new()
local busIndex = 0
local lastArrival = 0 -- server clock (os.time) of the previous bus
local nextAt = 0 -- os.clock() of the next bus
local nextList: { Passenger }? = nil
local nextGuaranteed = 0 -- how many of nextList's first passengers are its guarantees
local drive = Bus.drive()
local busScoreProviders: { (Player) -> number } = {}
local extraGuests: { Passenger } = {} -- added to the next bus (the tutorial, Hunter Night's thank-you)
local arrivedHandlers: { (number) -> () } = {}
local tutorialHotels: () -> { Player } = function()
	return {}
end
local tutorialGuests: { [number]: Player } = {} -- guest id → the hotel the tutorial brought it for
local announced: string? = nil -- the species announced for the next bus, Legendary and up (§4.3)

-- A provider of a hotel's bus-score bonus as a fraction (the Moon Tree's +5 %, §6.5).
function BusService.addScoreBonus(provider: (Player) -> number)
	table.insert(busScoreProviders, provider)
end

-- The hotels whose tutorial brings them Commons on the next bus (§11 1:45): TutorialService's.
function BusService.setTutorialHotels(provider: () -> { Player })
	tutorialHotels = provider
end

function BusService.onArrived(handler: (number) -> ())
	table.insert(arrivedHandlers, handler)
end

-- Adds a guest to the next bus; `opts.booked` sends it straight to that player's hotel.
function BusService.addToNext(
	speciesId: string,
	mutation: string?,
	opts: { booked: Player?, happyFloor: number? }?
)
	table.insert(extraGuests, {
		species = speciesId,
		mutation = mutation,
		booked = opts and opts.booked,
		happyFloor = opts and opts.happyFloor,
	})
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

-- The rooms vacant on the whole street now (§4.3: the bus's size follows them).
local function vacantRooms(): number
	local n = 0
	for _, plot in PlotService.all() do
		local hotel = plot.owner and HotelService.get(plot.owner)
		if hotel then
			for _, room in hotel.rooms do
				if room.state == "Vacant" then
					n += 1
				end
			end
		end
	end
	return n
end

local function size(): number
	return Bus.size(vacantRooms(), #Players:GetPlayers())
end

local function drawIds(flags: Bus.Flags, n: number, at: number): { Passenger }
	local ids = Bus.passengers(flags, n, locationsPresent(), function()
		return rng:NextNumber()
	end, Events.weights(at))
	local list = {}
	for _, id in ids do
		table.insert(list, { species = id, mutation = Events.rollMutation(rng:NextNumber(), at) })
	end
	return list
end

-- A bus's passengers, drawn a bus ahead: its guarantees first, then as many as the street's vacancies ask for now.
local function draw(index: number, previous: number, at: number): ({ Passenger }, number)
	local flags = Bus.flags(index, previous, at)
	local guaranteed = (if flags.mythic then 1 else 0)
		+ (if flags.legendary then 1 else 0)
		+ (if flags.epic then 1 else 0)
	return drawIds(flags, size(), at), guaranteed
end

-- At the bus's arrival: as many as the street's vacancies ask for now, never dropping a guarantee.
local function fit(list: { Passenger }, guaranteed: number, at: number): { Passenger }
	local want = size()
	while #list > math.max(want, guaranteed) do
		table.remove(list)
	end
	if #list < want then
		local none = { epic = false, legendary = false, mythic = false }
		for _, p in drawIds(none, want - #list, at) do
			table.insert(list, p)
		end
	end
	return list
end

local function wishText(p: Passenger): string
	local sp = assert(Species.get(p.species))
	local room = Pieces.get(sp.room)
	return `Wants: {room and room.name or sp.room} · {table.concat(sp.prefs, " · ")}`
end

local function rarest(list: { Passenger }): Passenger?
	local ids = {}
	for _, p in list do
		table.insert(ids, p.species)
	end
	local id = Bus.rarest(ids)
	return if id then list[table.find(ids, id) :: number] else nil
end

-- Tells the street about the next bus's rare guest (§4.3), Legendary and up.
local function announceNext(list: { Passenger })
	announced = nil
	local p = rarest(list)
	local sp = p and Species.get(p.species)
	if not p or not sp then
		return
	end
	local rank = table.find(Constants.RarityOrder, sp.rarity) or 0
	if rank >= (table.find(Constants.RarityOrder, "Legendary") :: number) then
		announced = p.species
		local mutation = if p.mutation then Mutations.ById[p.mutation].name .. " " else ""
		Net.fireAll(
			"Announce",
			`A {sp.rarity} {mutation}{sp.name} is on the next bus! {wishText(p)}`,
			"Rare"
		)
	end
end

-- Where a guest goes when its browse ends: the best-scoring hotel with a vacant room of its type.
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
				distance = (StreetLayout.pavementFront(plot.index) - here).Magnitude,
				tutorial = tutorialGuests[g.id] == owner,
			})
			table.insert(jitters, Scoring.jitter(rng:NextNumber()))
		end
	end
	tutorialGuests[g.id] = nil
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

-- Guests step off at a stop, one after another; a booked one walks straight to its hotel.
local function stepOff(stop: StreetLayout.Stop, list: { Passenger }, first: number)
	for i, p in list do
		task.delay((i - 1) * B.StepOff, function()
			-- Every fourth guest the same way: north or south pavement, east or west.
			local g = GuestService.spawnBrowsing(
				p.species,
				p.mutation,
				stop,
				(first + i) % 4,
				wishText(p),
				decide
			)
			if p.tutorialFor then
				tutorialGuests[g.id] = p.tutorialFor
			end
			local booked = p.booked
			local offer = booked and booked.Parent and HotelService.vacantFor(booked, p.species)
			if booked and offer then
				g.config:SetAttribute("Wish", nil)
				g.onDecide = nil
				g.happyFloor = p.happyFloor
				GuestService.assign(g, booked, offer.pieceId)
			end
		end)
	end
end

-- A hotel's vacant rooms by room type (piece id → how many).
local function vacantByRoom(player: Player): { [string]: number }
	local out = {}
	local hotel = HotelService.get(player)
	local data = PlayerData.get(player)
	if hotel and data then
		for id, room in hotel.rooms do
			local rec = data.layout[id]
			if room.state == "Vacant" and rec then
				out[rec.item] = (out[rec.item] or 0) + 1
			end
		end
	end
	return out
end

--[[ The tutorial's Commons (§11 1:45): for each hotel in its tutorial, Commons
	its vacant rooms can take, in place of the bus's drawn guests from the end
	of the list (its guarantees are first and stay, and so does a guest the
	street was told is coming), so the bus keeps its size. ]]
local function weightCommons(list: { Passenger }, guaranteed: number)
	for id in tutorialGuests do
		if not GuestService.get(id) then
			tutorialGuests[id] = nil
		end
	end
	local slot = #list
	for _, player in tutorialHotels() do
		local data = PlayerData.get(player)
		if data and player.Parent and slot > guaranteed then
			local n = math.min(Constants.Tutorial.CommonsPerBus, slot - guaranteed)
			local ids = Bus.commonsFor(
				vacantByRoom(player),
				n,
				{ [data.location] = true },
				function()
					return rng:NextNumber()
				end
			)
			local placed = 0
			for _, id in ids do
				while slot > guaranteed and list[slot].species == announced do
					slot -= 1
				end
				if slot <= guaranteed then
					break
				end
				list[slot] = { species = id, mutation = nil, tutorialFor = player }
				slot -= 1
				placed += 1
			end
			if placed > 0 then
				PlayerData.stat(player, "tutorialCommonBuses")
			end
		end
	end
end

local function arrive()
	busIndex += 1
	local now = os.time()
	local guaranteed = nextGuaranteed
	local list: { Passenger }
	if nextList then
		list = fit(nextList, nextGuaranteed, now)
	else
		list, guaranteed = draw(busIndex, lastArrival, now)
	end
	local ok, err = pcall(weightCommons, list, guaranteed)
	if not ok then
		warn(`[bus] tutorial Commons: {err}`)
	end
	for _, extra in extraGuests do
		table.insert(list, extra)
	end
	table.clear(extraGuests)
	lastArrival = now
	workspace:SetAttribute("BusArrivedAt", workspace:GetServerTimeNow())
	workspace:SetAttribute("BusIndex", busIndex)
	Net.fireAll("Announce", "The Night Bus has arrived!", "Bus")
	-- Half off at each stop (his ruling), the first stop's half rounded up.
	local west, east = StreetLayout.Stops[1], StreetLayout.Stops[2]
	local half = math.ceil(#list / 2)
	local first, second = {}, {}
	for i, p in list do
		table.insert(if i <= half then first else second, p)
	end
	GuestService.board(west.name)
	stepOff(west, first, 0)
	task.delay(drive.eastAt, function()
		GuestService.board(east.name)
		stepOff(east, second, half)
	end)
	for _, h in arrivedHandlers do
		task.spawn(h, busIndex)
	end
	-- Draw the next bus now, so its rare guest can be announced a bus ahead.
	-- A Monster Parade (§8.2) runs a bus a minute.
	local interval = if Events.parade(now) then Events.ParadeInterval else B.Interval
	nextAt = os.clock() + interval
	workspace:SetAttribute("NextBusAt", workspace:GetServerTimeNow() + interval)
	nextList, nextGuaranteed = draw(busIndex + 1, now, now + interval)
	announceNext(nextList :: { Passenger })
end

-- Brings the next bus now (Call the Bus, §10.2: "for the whole server"): it drives in out of the forest.
function BusService.callNow(byName: string?)
	if byName then
		Net.fireAll("Announce", `{byName} called the bus!`, "Bus")
	end
	local soon = -drive.start
	if nextAt - os.clock() > soon then
		nextAt = os.clock() + soon
		workspace:SetAttribute("NextBusAt", workspace:GetServerTimeNow() + soon)
	end
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

--[[ The species on the street a room could be wanted for (§7, "Need a
	Coffin Suite!"): every guest browsing now, and the next bus's announced
	guest. ]]
function BusService.wanted(): { string }
	local out = {}
	for _, g in GuestService.all() do
		if g.state == "Browsing" then
			table.insert(out, g.species)
		end
	end
	if announced then
		table.insert(out, announced)
	end
	return out
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
	DevGrant.register("legendary", function()
		-- Puts a Legendary on the next bus and announces it, as a half-hour bus would.
		local pool = Bus.pool("Legendary", locationsPresent())
		if #pool == 0 then
			return "no Legendary at these locations"
		end
		nextList = nextList or {}
		table.insert(nextList :: { Passenger }, 1, { species = pool[1], mutation = nil })
		nextGuaranteed += 1
		announceNext(nextList :: { Passenger })
		return `next bus: {pool[1]}`
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
	nextList, nextGuaranteed = draw(1, lastArrival, lastArrival + B.FirstBusDelay)
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
