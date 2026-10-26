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

	ONE WORLD (GDD §3, §6.4, his ruling 2026-10-20: "Each street's Night Bus
	carries its own location's family"): every street with a hotel played on
	it gets its own bus, on one timetable for the whole server. Each street's
	bus is drawn, sized, guaranteed and announced on its own: its location's
	species only, 40 % of that street's vacant rooms within 2–4 per player on
	it, its guests browsing and choosing among that street's hotels only, and
	its rare guest told to the players on that street. A street nobody plays
	on has no bus.

	VIP CONTRACTS (A.11.1, his call WAITING §2.38, the recommendation built):
	a contract's VIP rides its hotel's street's bus as an EXTRA SEAT, added
	after the bus is sized, so it is not counted in the 40 % of vacant rooms
	or the cap (its room is held, not Vacant, from Ready); it steps off
	booked to that hotel (`setVips`: ContractService's source and arrival).

	Published on `workspace`: `NextBusAt` and `BusArrivedAt` (server time), so
	every client draws the bus and the countdown, and `BusStreets` (the
	streets with a bus, "1,3").
]]

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
-- `street`: an extra guest's street (a booked one's is its hotel's; else its species' location's).
type Passenger = {
	species: string,
	mutation: string?, -- the look (A.11.5)
	size: string?, -- Tiny or Giant, stacked with the look (A.11.5)
	booked: Player?,
	happyFloor: number?,
	tutorialFor: Player?,
	street: number?,
	vip: number?, -- a VIP contract's id (A.11.1): an extra seat, booked to `booked`
	onBooked: ((reached: boolean) -> ())?, -- a booked guest's fate at step-off: walking to its hotel, or home
}

-- One street's next bus: drawn a bus ahead, so its rare guest can be announced.
type Line = {
	nextList: { Passenger }?,
	nextGuaranteed: number, -- how many of nextList's first passengers are its guarantees
	announced: string?, -- the species announced for its next bus, Legendary and up (§4.3)
}

local rng = Random.new()
local busIndex = 0
local lastArrival = 0 -- server clock (os.time) of the previous bus
local nextAt = 0 -- os.clock() of the next bus
local lines: { [number]: Line } = {} -- by street
local drive = Bus.drive()
local busScoreProviders: { (Player) -> number } = {}
local extraGuests: { Passenger } = {} -- added to the next bus (the tutorial, Hunter Night's thank-you)
local arrivedHandlers: { (number) -> () } = {}
local tutorialHotels: () -> { Player } = function()
	return {}
end
local tutorialGuests: { [number]: Player } = {} -- guest id → the hotel the tutorial brought it for
-- VIP contracts (A.11.1): who rides a street's next bus as an extra seat, and what a VIP does stepping off.
local vipSource: (number) -> { Passenger } = function()
	return {}
end
local vipArrival: (GuestService.Guest, Passenger) -> () = function() end

local function line(street: number): Line
	local l = lines[street]
	if not l then
		l = { nextList = nil, nextGuaranteed = 0, announced = nil }
		lines[street] = l
	end
	return l
end

-- The streets with a hotel played on them (each gets a bus), in order.
local function liveStreets(): { number }
	local set = {}
	for _, plot in PlotService.all() do
		if plot.owner then
			set[plot.street] = true
		end
	end
	local out = {}
	for street = 1, StreetLayout.Streets do
		if set[street] then
			table.insert(out, street)
		end
	end
	return out
end

-- The players playing a hotel on `street`.
local function playersOn(street: number): { Player }
	local out = {}
	for _, plot in PlotService.all() do
		if plot.owner and plot.street == street then
			table.insert(out, plot.owner)
		end
	end
	return out
end

local function fireStreet(street: number, ...: any)
	for _, player in playersOn(street) do
		Net.fire(player, ...)
	end
end

-- A provider of a hotel's bus-score bonus as a fraction (the Moon Tree's +5 %, §6.5).
function BusService.addScoreBonus(provider: (Player) -> number)
	table.insert(busScoreProviders, provider)
end

-- The hotels whose tutorial brings them Commons on the next bus (§11 1:45): TutorialService's.
function BusService.setTutorialHotels(provider: () -> { Player })
	tutorialHotels = provider
end

--[[ VIP contracts (A.11.1): `source(street)` gives the VIPs riding that
	street's bus now (extra seats, each with `vip` and `booked`), and
	`arrival(guest, passenger)` books one stepping off into its held room. ]]
function BusService.setVips(
	source: (number) -> { Passenger },
	arrival: (GuestService.Guest, Passenger) -> ()
)
	vipSource = source
	vipArrival = arrival
end

function BusService.onArrived(handler: (number) -> ())
	table.insert(arrivedHandlers, handler)
end

--[[ Adds a guest to the next bus; `opts.booked` sends it straight to that
	player's hotel. It rides the bus of its booked hotel's street, else of
	`opts.street`, else of its species' location's street. ]]
function BusService.addToNext(
	speciesId: string,
	mutation: string?,
	opts: {
		booked: Player?,
		happyFloor: number?,
		street: number?,
		onBooked: ((reached: boolean) -> ())?,
	}?
)
	table.insert(extraGuests, {
		species = speciesId,
		mutation = mutation,
		booked = opts and opts.booked,
		happyFloor = opts and opts.happyFloor,
		street = opts and opts.street,
		onBooked = opts and opts.onBooked,
	})
end

-- A street's own location (street s is location s's): its bus carries that family only.
local function locationsPresent(street: number): { [number]: boolean }
	return { [street] = true }
end

-- The rooms vacant on a street now (§4.3: its bus's size follows them).
local function vacantRooms(street: number): number
	local n = 0
	for _, plot in PlotService.all() do
		local hotel = plot.street == street and plot.owner and HotelService.get(plot.owner)
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

local function size(street: number): number
	return Bus.size(vacantRooms(street), #playersOn(street))
end

local function drawIds(street: number, flags: Bus.Flags, n: number, at: number): { Passenger }
	local ids = Bus.passengers(flags, n, locationsPresent(street), function()
		return rng:NextNumber()
	end, Events.weights(at))
	local list = {}
	for _, id in ids do
		local sz, look = Events.rollMutations(rng:NextNumber(), rng:NextNumber(), at)
		table.insert(list, { species = id, mutation = look, size = sz })
	end
	return list
end

-- A bus's passengers, drawn a bus ahead: its guarantees first, then as many as the street's vacancies ask for now.
local function draw(
	street: number,
	index: number,
	previous: number,
	at: number
): ({ Passenger }, number)
	local flags = Bus.flags(index, previous, at)
	local guaranteed = (if flags.mythic then 1 else 0)
		+ (if flags.legendary then 1 else 0)
		+ (if flags.epic then 1 else 0)
	return drawIds(street, flags, size(street), at), guaranteed
end

-- At the bus's arrival: as many as the street's vacancies ask for now, never dropping a guarantee
-- or the guest announced to the street (2026-10-26 review: a drawn Legendary, told of a bus
-- ahead, was cut when the street's vacancies fell).
local function fit(
	street: number,
	list: { Passenger },
	guaranteed: number,
	announced: string?,
	at: number
): { Passenger }
	local want = size(street)
	while #list > math.max(want, guaranteed) do
		local cut = #list
		while cut > guaranteed and list[cut].species == announced do
			cut -= 1
		end
		if cut <= guaranteed then
			break
		end
		table.remove(list, cut)
	end
	if #list < want then
		local none = { epic = false, legendary = false, mythic = false }
		for _, p in drawIds(street, none, want - #list, at) do
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

-- Tells the street about its next bus's rare guest (§4.3), Legendary and up.
local function announceNext(street: number, list: { Passenger })
	local l = line(street)
	l.announced = nil
	local p = rarest(list)
	local sp = p and Species.get(p.species)
	if not p or not sp then
		return
	end
	local rank = table.find(Constants.RarityOrder, sp.rarity) or 0
	if rank >= (table.find(Constants.RarityOrder, "Legendary") :: number) then
		l.announced = p.species
		local mutation = Mutations.prefix(p.size, p.mutation)
		fireStreet(
			street,
			"Announce",
			`A {sp.rarity} {mutation}{sp.name} is on the next bus! {wishText(p)}`,
			"Rare"
		)
	end
end

-- Where a guest goes when its browse ends: the best-scoring hotel on its street with a vacant room of its type.
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
		if owner and plot.street == g.street then
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
				distance = (StreetLayout.pavementFront(plot.index, plot.street) - here).Magnitude,
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
	-- Announced and counted only once it is on its way: a room with no way to
	-- it from the desk sends the guest home instead (GuestService.assign).
	if not GuestService.assign(g, owner, offer.pieceId) then
		return
	end
	if sp.rarity == "Legendary" or sp.rarity == "Mythic" or sp.rarity == "Epic" then
		fireStreet(g.street, "Announce", `The {sp.name} chose {owner.DisplayName}'s hotel!`, "Rare")
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
				decide,
				p.size
			)
			if p.tutorialFor then
				tutorialGuests[g.id] = p.tutorialFor
			end
			if p.vip then
				g.config:SetAttribute("Wish", nil)
				g.onDecide = nil
				local ok, err = pcall(vipArrival, g, p)
				if not ok then
					warn(`[bus] VIP: {err}`)
					GuestService.leaveStreet(g)
				end
				return
			end
			-- A booked guest (the tutorial's Vampire Count, §11) walks to its hotel
			-- or goes home: it never browses, so it never checks in at another
			-- player's hotel. Who booked it hears which (`onBooked`), so the
			-- tutorial offers its Vampire again on a later bus when it missed.
			local booked = p.booked
			if booked then
				g.config:SetAttribute("Wish", nil)
				g.onDecide = nil
				local offer = booked.Parent and HotelService.vacantFor(booked, p.species)
				local reached = false
				if offer then
					g.happyFloor = p.happyFloor
					reached = GuestService.assign(g, booked, offer.pieceId)
				else
					GuestService.leaveStreet(g)
				end
				local onBooked = p.onBooked
				if onBooked then
					local ok, err = pcall(onBooked, reached)
					if not ok then
						warn(`[bus] booked: {err}`)
					end
				end
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
			local rec = data.rooms[id]
			if room.state == "Vacant" and rec then
				out[rec.type] = (out[rec.type] or 0) + 1
			end
		end
	end
	return out
end

--[[ The tutorial's Commons (§11 1:45): for each hotel in its tutorial, Commons
	its vacant rooms can take, in place of the bus's drawn guests from the end
	of the list (its guarantees are first and stay, and so does a guest the
	street was told is coming), so the bus keeps its size. ]]
local function weightCommons(street: number, list: { Passenger }, guaranteed: number)
	for id in tutorialGuests do
		if not GuestService.get(id) then
			tutorialGuests[id] = nil
		end
	end
	local announced = line(street).announced
	local slot = #list
	for _, player in tutorialHotels() do
		local data = PlayerData.get(player)
		local plot = PlotService.of(player)
		if data and player.Parent and slot > guaranteed and plot and plot.street == street then
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

-- The street an extra guest rides to: its booked hotel's, the one it was given, or its species' location's.
local function extraStreet(p: Passenger): number
	local booked = p.booked
	local plot = booked and PlotService.of(booked)
	if plot then
		return plot.street
	end
	if p.street then
		return p.street
	end
	local sp = Species.get(p.species)
	return math.clamp(sp and sp.location or 1, 1, StreetLayout.Streets)
end

-- One street's bus arriving: its passengers off at its two stops, its waiting guests aboard.
local function arriveOn(street: number, now: number)
	local l = line(street)
	local guaranteed = l.nextGuaranteed
	local list: { Passenger }
	if l.nextList then
		list = fit(street, l.nextList :: { Passenger }, l.nextGuaranteed, l.announced, now)
	else
		list, guaranteed = draw(street, busIndex, lastArrival, now)
	end
	local ok, err = pcall(weightCommons, street, list, guaranteed)
	if not ok then
		warn(`[bus] tutorial Commons: {err}`)
	end
	for i = #extraGuests, 1, -1 do
		local extra = extraGuests[i]
		if extraStreet(extra) == street then
			table.insert(list, extra)
			table.remove(extraGuests, i)
		end
	end
	-- VIPs of contracts (A.11.1): extra seats, after the bus was sized.
	local ok2, vips = pcall(vipSource, street)
	if ok2 then
		for _, p in vips do
			table.insert(list, p)
		end
	else
		warn(`[bus] VIPs: {vips}`)
	end
	fireStreet(street, "Announce", "The Night Bus has arrived!", "Bus")
	-- Half off at each stop (his ruling), the first stop's half rounded up.
	local stops = StreetLayout.stops(street)
	local west, east = stops[1], stops[2]
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
end

local function arrive()
	busIndex += 1
	local now = os.time()
	local streets = liveStreets()
	for _, street in streets do
		local ok, err = pcall(arriveOn, street, now)
		if not ok then
			warn(`[bus] street {street}: {err}`)
		end
	end
	-- An extra for a street with no bus now (its hotel's player travelled) waits for the next.
	lastArrival = now
	workspace:SetAttribute("BusArrivedAt", workspace:GetServerTimeNow())
	workspace:SetAttribute("BusIndex", busIndex)
	for _, h in arrivedHandlers do
		task.spawn(h, busIndex)
	end
	-- Draw each street's next bus now, so its rare guest can be announced a bus ahead.
	-- A Monster Parade (§8.2) runs a bus a minute.
	local interval = if Events.parade(now) then Events.ParadeInterval else B.Interval
	nextAt = os.clock() + interval
	workspace:SetAttribute("NextBusAt", workspace:GetServerTimeNow() + interval)
	table.clear(lines)
	for _, street in streets do
		local l = line(street)
		l.nextList, l.nextGuaranteed = draw(street, busIndex + 1, now, now + interval)
		announceNext(street, l.nextList :: { Passenger })
	end
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

--[[ The species on a street a room could be wanted for (§7, "Need a
	Coffin Suite!"): every guest browsing there now, and its next bus's
	announced guest; every street's with none named. ]]
function BusService.wanted(street: number?): { string }
	local out = {}
	for _, g in GuestService.all() do
		if g.state == "Browsing" and (street == nil or g.street == street) then
			table.insert(out, g.species)
		end
	end
	for s, l in lines do
		if l.announced and (street == nil or s == street) then
			table.insert(out, l.announced)
		end
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
		local out = {}
		for street, l in lines do
			local names = {}
			for _, p in l.nextList or {} do
				table.insert(
					names,
					p.species
						.. (
							if p.size or p.mutation
								then "(" .. Mutations.prefix(p.size, p.mutation) .. ")"
								else ""
						)
				)
			end
			table.insert(out, `street {street}: {table.concat(names, ", ")}`)
		end
		return `in {math.floor(BusService.nextIn())}s ({workspace:GetAttribute("BusStreets")}): {table.concat(
			out,
			" | "
		)}`
	end)
	DevGrant.register("legendary", function(player)
		-- Puts a Legendary on the player's street's next bus and announces it, as a half-hour bus would.
		local plot = PlotService.of(player)
		local street = if plot then plot.street else 1
		local pool = Bus.pool("Legendary", locationsPresent(street))
		if #pool == 0 then
			return "no Legendary at this location"
		end
		local l = line(street)
		l.nextList = l.nextList or {}
		table.insert(l.nextList :: { Passenger }, 1, { species = pool[1], mutation = nil })
		l.nextGuaranteed += 1
		announceNext(street, l.nextList :: { Passenger })
		return `next bus on street {street}: {pool[1]}`
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
	workspace:SetAttribute("BusStreets", "1")
	task.spawn(function()
		while true do
			task.wait(0.5)
			-- The streets with a bus follow the hotels played (a Travel moves one); a new one's bus is drawn now.
			local streets = liveStreets()
			local list = {}
			for _, street in streets do
				table.insert(list, tostring(street))
				if not lines[street] then
					local l = line(street)
					local soon = os.time() + math.max(0, math.floor(nextAt - os.clock()))
					l.nextList, l.nextGuaranteed = draw(street, busIndex + 1, lastArrival, soon)
				end
			end
			-- A street left with no hotel played has no bus any more: its street guests go with the last one.
			local live = {}
			for _, street in streets do
				live[street] = true
			end
			for _, g in GuestService.all() do
				if not g.owner and not live[g.street] then
					GuestService.remove(g)
				end
			end
			local text = if #list > 0 then table.concat(list, ",") else "1"
			if workspace:GetAttribute("BusStreets") ~= text then
				workspace:SetAttribute("BusStreets", text)
			end
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
