--!strict
--[[
	Guests (GDD §4.3, §4.4, §13.2). THE SERVER SIMULATES, THE CLIENT PAINTS:
	a guest here is a state machine and a path, never a model. Each one is
	published as a `Configuration` in `ReplicatedStorage.Guests` whose
	attributes say what it is and where it walks; every client draws it
	locally (`GuestRenderer`), so six hotels of guests cost a phone nothing in
	physics.

	States (§13.2): Browsing (a bus guest walking the lane) → ToHotel → Queued
	(at the desk) → ToRoom → InRoom (paying per second into the till, with one
	request) → Leaving. A guest that waits too long at the desk leaves
	unhappy. Walk-ins (§4.3 "never starved") come straight to a hotel.

	Published per guest: `Species`, `Mutation`, `State`, `Plot`, `Path`
	("x,y,z;..."), `T0` (server time the path starts), `Speed`, `Wish` (a bus
	guest's wish list), `Request`, `Happy`.

	What other systems hook: `onCheckout(player, guest, satisfaction)` for
	friendship (§4.6); `checkIn`, `clean`, `fulfil` for staff; `spawnWalkIn`
	for the tutorial; `spawnBrowsing` and `assign` for the bus.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Grid = require(ReplicatedStorage.Shared.Grid)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Species = require(ReplicatedStorage.Shared.Species)
local Stay = require(ReplicatedStorage.Shared.Stay)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)
local Mutations = require(ReplicatedStorage.Shared.Mutations)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local Income = require(ServerScriptService.Server.Income)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local G = Constants.Grid
local S = Constants.Stay

local GuestService = {}

export type State = "Browsing" | "ToHotel" | "Queued" | "ToRoom" | "InRoom" | "Leaving"
export type Guest = {
	id: number,
	species: string,
	mutation: string?,
	source: string, -- "WalkIn" | "Bus" | "Tutorial"
	owner: Player?,
	room: string?,
	state: State,
	arriveAt: number, -- os.clock() when the current path ends
	path: { Vector3 },
	speed: number,
	deskSince: number?,
	waited: number,
	payRate: number,
	tier: number,
	prefsMatched: number,
	amenities: number,
	stayEnd: number?,
	requestAt: number?,
	requestUntil: number?,
	requestsPlayer: number,
	requestsStaff: number,
	requestsMissed: number,
	happyFloor: number?, -- the tutorial's: a stay at least this happy (Appendix A.7)
	pitches: { [number]: number }, -- user id -> plot index (§4.3)
	wish: string?,
	config: Configuration,
	onDecide: ((Guest) -> ())?, -- a bus guest at the lane's end
}

local guests: { [number]: Guest } = {}
local nextId = 1
local folder: Folder
local rng = Random.new()
local checkoutHandlers: { (Player, Guest, number) -> () } = {}
local checkInHandlers: { (Player, Guest) -> () } = {}
local nextWalkIn: { [Player]: number } = {}
local walkInsOff: { [Player]: boolean } = {}
local speedBonus: { [Player]: number } = {}

local function encode(path: { Vector3 }): string
	local parts = table.create(#path)
	for i, p in path do
		parts[i] = string.format("%.1f,%.1f,%.1f", p.X, p.Y, p.Z)
	end
	return table.concat(parts, ";")
end

local function length(path: { Vector3 }): number
	local total = 0
	for i = 2, #path do
		total += (path[i] - path[i - 1]).Magnitude
	end
	return total
end

local function publish(g: Guest)
	local c = g.config
	c:SetAttribute("State", g.state)
	c:SetAttribute("Plot", if g.owner then (g.owner:GetAttribute("Plot") or 0) else 0)
	c:SetAttribute(
		"Request",
		if g.requestUntil then (Species.get(g.species) :: any).request else nil
	)
end

-- Sends the guest along `path` at its speed, from now.
local function walk(g: Guest, path: { Vector3 })
	g.path = path
	local speed = g.speed
	if g.owner and speedBonus[g.owner] and g.state ~= "Browsing" then
		speed *= 1 + speedBonus[g.owner]
	end
	g.arriveAt = os.clock() + length(path) / speed
	g.config:SetAttribute("Speed", speed)
	g.config:SetAttribute("T0", workspace:GetServerTimeNow())
	g.config:SetAttribute("Path", encode(path))
end

local function here(g: Guest): Vector3
	-- Where the guest is now along its path (the same arithmetic the client draws with).
	local path = g.path
	if #path == 0 then
		return Vector3.zero
	end
	local total = length(path)
	local remaining = math.max(0, g.arriveAt - os.clock())
		* (g.config:GetAttribute("Speed") :: number? or g.speed)
	local travelled = math.max(0, total - remaining)
	for i = 2, #path do
		local seg = (path[i] - path[i - 1]).Magnitude
		if travelled <= seg then
			return path[i - 1]:Lerp(path[i], if seg > 0 then travelled / seg else 1)
		end
		travelled -= seg
	end
	return path[#path]
end
GuestService.positionOf = function(g: Guest): Vector3
	return here(g)
end

local function newGuest(speciesId: string, mutation: string?, source: string): Guest
	local id = nextId
	nextId += 1
	local config = Instance.new("Configuration")
	config.Name = tostring(id)
	config:SetAttribute("Species", speciesId)
	config:SetAttribute("Mutation", mutation)
	local g: Guest = {
		id = id,
		species = speciesId,
		mutation = mutation,
		source = source,
		owner = nil,
		room = nil,
		state = "ToHotel",
		arriveAt = os.clock(),
		path = {},
		speed = Constants.Stay.WalkSpeed,
		deskSince = nil,
		waited = 0,
		payRate = 0,
		tier = 1,
		prefsMatched = 0,
		amenities = 0,
		stayEnd = nil,
		requestAt = nil,
		requestUntil = nil,
		requestsPlayer = 0,
		requestsStaff = 0,
		requestsMissed = 0,
		happyFloor = nil,
		pitches = {},
		wish = nil,
		config = config,
		onDecide = nil,
	}
	guests[id] = g
	return g
end

local function destroy(g: Guest)
	guests[g.id] = nil
	g.config:Destroy()
end

-- ===== Paths through a hotel =====

local function toWorld(plot: PlotService.Plot, floor: number, c: Grid.Cell): Vector3
	return plot.frame:PointToWorldSpace(Grid.cellCentre(floor, c))
end

local function cellOf(plot: PlotService.Plot, world: Vector3): Grid.Cell
	local localPos = plot.frame:PointToObjectSpace(world)
	return {
		x = math.clamp(math.floor(localPos.X / G.CellSize), 0, G.Cells - 1),
		z = math.clamp(math.floor(localPos.Z / G.CellSize), 0, G.Cells - 1),
	}
end

-- The walk from the desk queue to a room's bed: through the lobby, up the stairs, to the door.
local function roomPath(
	plot: PlotService.Plot,
	data: PlayerData.Data,
	from: Vector3,
	pieceId: string
): { Vector3 }?
	local rec = data.layout[pieceId]
	local piece = rec and Pieces.get(rec.item)
	if not rec or not piece then
		return nil
	end
	local layout = PlotService.placed(data)
	local doorCell = Grid.doorCell({ x = rec.x, z = rec.z, r = rec.r, w = piece.w, d = piece.d })
	local sc = G.StairCore
	local out: { Vector3 } = { from }
	local start = cellOf(plot, from)
	local function addCells(floor: number, cells: { Grid.Cell }?)
		if not cells then
			return false
		end
		for _, c in cells do
			table.insert(out, toWorld(plot, floor, c))
		end
		return true
	end
	if rec.floor == 1 then
		if not addCells(1, Grid.path(layout, 1, start, doorCell)) then
			return nil
		end
	else
		if not addCells(1, Grid.path(layout, 1, start, { x = sc.x, z = sc.z - 1 })) then
			return nil
		end
		for f = 1, rec.floor - 1 do
			for _, p in PlotService.stairPath(plot, f) do
				table.insert(out, p)
			end
		end
		if
			not addCells(
				rec.floor,
				Grid.path(layout, rec.floor, { x = sc.x + 1, z = sc.z - 1 }, doorCell)
			)
		then
			return nil
		end
	end
	local door = PlotService.piecePoint(plot, pieceId, "Door")
	local bed = PlotService.piecePoint(plot, pieceId, "Bed")
	if door then
		table.insert(out, door.Position)
	end
	if bed then
		table.insert(out, bed.Position)
	end
	return out
end

local function reversed(path: { Vector3 }): { Vector3 }
	local out = table.create(#path)
	for i = #path, 1, -1 do
		table.insert(out, path[i])
	end
	return out
end

-- Out of the hotel and off the street, toward the nearer end of the lane.
local function exitPath(plot: PlotService.Plot, from: { Vector3 }): { Vector3 }
	local out = from
	local entrance = PlotService.lobbyPoint(plot, "Entrance")
	if entrance then
		table.insert(out, entrance.Position)
	end
	local front = StreetLayout.laneFront(plot.index)
	table.insert(out, front)
	local endX = if front.X < 0
		then -Constants.Street.LaneHalfLength - 20
		else Constants.Street.LaneHalfLength + 20
	table.insert(out, Vector3.new(endX, front.Y, 0))
	return out
end

-- ===== The desk queue =====

local function queueSpot(plot: PlotService.Plot, k: number): Vector3?
	local at = PlotService.lobbyPoint(plot, `Queue_{math.min(k, 4)}`)
	if not at then
		return nil
	end
	if k > 4 then
		return (at * CFrame.new(-(k - 4) * 3, 0, 0)).Position
	end
	return at.Position
end

local function requeue(player: Player)
	local hotel = HotelService.get(player)
	local plot = PlotService.of(player)
	if not hotel or not plot then
		return
	end
	for k, id in hotel.queue do
		local g = guests[id]
		local spot = queueSpot(plot, k)
		if g and spot and g.state == "Queued" then
			local now = here(g)
			if (now - spot).Magnitude > 0.5 then
				walk(g, { now, spot })
			end
			g.config:SetAttribute("Queue", k)
		end
	end
end

local function leaveQueue(player: Player, g: Guest)
	local hotel = HotelService.get(player)
	if hotel then
		local i = table.find(hotel.queue, g.id)
		if i then
			table.remove(hotel.queue, i)
		end
	end
	g.config:SetAttribute("Queue", nil)
	requeue(player)
end

-- ===== Lifecycle =====

local function sendHome(g: Guest, plot: PlotService.Plot?)
	g.state = "Leaving"
	g.room = nil
	g.requestUntil = nil
	if plot then
		walk(g, exitPath(plot, { here(g) }))
	else
		local p = here(g)
		walk(g, { p, Vector3.new(Constants.Street.LaneHalfLength + 20, p.Y, 0) })
	end
	publish(g)
end

--[[ Points a guest at a hotel: reserves the room and walks it from where it
	stands to the desk queue. `via` are points to pass first (the lane). ]]
function GuestService.assign(g: Guest, player: Player, pieceId: string, via: { Vector3 }?)
	local plot = PlotService.of(player)
	local hotel = HotelService.get(player)
	if not plot or not hotel then
		sendHome(g, nil)
		return
	end
	g.owner = player
	g.room = pieceId
	HotelService.setRoom(player, pieceId, "Reserved", g.id)
	table.insert(hotel.queue, g.id)
	local k = #hotel.queue
	local path: { Vector3 } = { here(g) }
	for _, p in via or {} do
		table.insert(path, p)
	end
	table.insert(path, StreetLayout.laneFront(plot.index))
	local entrance = PlotService.lobbyPoint(plot, "Entrance")
	if entrance then
		table.insert(path, entrance.Position)
	end
	local spot = queueSpot(plot, k)
	if spot then
		table.insert(path, spot)
	end
	g.state = "ToHotel"
	g.config:SetAttribute("Queue", k)
	walk(g, path)
	publish(g)
end

-- A walk-in (§4.3): a Common or Uncommon of the hotel's family that it has a vacant room for.
function GuestService.spawnWalkIn(
	player: Player,
	speciesId: string?,
	opts: { happyFloor: number?, source: string? }?
): Guest?
	local data = PlayerData.get(player)
	local plot = PlotService.of(player)
	if not data or not plot then
		return nil
	end
	local chosen: string? = speciesId
	local offer: HotelService.Offer? = nil
	if chosen then
		offer = HotelService.vacantFor(player, chosen)
	else
		local options = {}
		for _, sp in Species.ofLocation(data.location) do
			if sp.rarity == "Common" or sp.rarity == "Uncommon" then
				local o = HotelService.vacantFor(player, sp.id)
				if o then
					table.insert(options, { id = sp.id, offer = o })
				end
			end
		end
		if #options > 0 then
			local pick = options[rng:NextInteger(1, #options)]
			chosen, offer = pick.id, pick.offer
		end
	end
	if not chosen or not offer then
		return nil
	end
	local mutation = Mutations.roll(rng:NextNumber())
	local g = newGuest(chosen, mutation, if opts and opts.source then opts.source else "WalkIn")
	g.happyFloor = opts and opts.happyFloor
	-- From the lane beside the plot.
	local front = StreetLayout.laneFront(plot.index)
	local side = if rng:NextNumber() < 0.5 then -1 else 1
	g.path = { front + Vector3.new(side * 40, 0, 0) }
	g.arriveAt = os.clock()
	g.config.Parent = folder
	GuestService.assign(g, player, offer.pieceId)
	return g
end

--[[ A bus guest (§4.3): on the lane at `at`, walking east to its end while it
	browses; `onDecide` is called when it gets there. ]]
function GuestService.spawnBrowsing(
	speciesId: string,
	mutation: string?,
	at: Vector3,
	wish: string,
	onDecide: (Guest) -> ()
): Guest
	local g = newGuest(speciesId, mutation, "Bus")
	g.state = "Browsing"
	g.speed = Constants.Bus.BrowseSpeed
	g.wish = wish
	g.onDecide = onDecide
	g.config:SetAttribute("Wish", wish)
	g.path = { at }
	walk(g, { at, StreetLayout.LaneEnd + Vector3.new(0, 0, (rng:NextNumber() - 0.5) * 6) })
	g.config.Parent = folder
	publish(g)
	return g
end

function GuestService.leaveStreet(g: Guest)
	sendHome(g, nil)
end

-- Checks the first waiting guest in, from the desk (the player's tap, or Front Desk staff).
function GuestService.checkIn(player: Player, byStaff: boolean?): Guest?
	local hotel = HotelService.get(player)
	local plot = PlotService.of(player)
	local data = PlayerData.get(player)
	if not hotel or not plot or not data then
		return nil
	end
	local g: Guest? = nil
	for _, id in hotel.queue do
		local candidate = guests[id]
		if candidate and candidate.state == "Queued" then
			g = candidate
			break
		end
	end
	if not g or not g.room then
		return nil
	end
	local rec = data.layout[g.room]
	local path = roomPath(plot, data, here(g), g.room)
	if not rec or not path then
		-- The room went missing or cannot be reached: the guest goes home.
		leaveQueue(player, g)
		HotelService.setRoom(player, g.room, "Vacant")
		sendHome(g, plot)
		return nil
	end
	g.waited = os.clock() - (g.deskSince or os.clock())
	HotelService.recordCheckIn(player, g.waited)
	local sp = assert(Species.get(g.species))
	g.tier = rec.tier
	g.prefsMatched = Stay.matched(sp.prefs, HotelService.roomTags(data, g.room))
	g.amenities = HotelService.amenitiesOn(data, rec.floor)
	local typeCount = 0
	for _, other in data.layout do
		if other.item == rec.item then
			typeCount += 1
		end
	end
	g.payRate =
		Economy.guestPay(g.species, rec.tier, g.mutation, typeCount, Income.multiplier(player))
	leaveQueue(player, g)
	HotelService.setRoom(player, g.room, "Occupied", g.id)
	g.state = "ToRoom"
	walk(g, path)
	publish(g)
	PlayerData.stat(player, "checkIns")
	Net.fire(
		player,
		"Moment",
		"CheckIn",
		{ species = g.species, mutation = g.mutation, byStaff = byStaff == true }
	)
	for _, h in checkInHandlers do
		task.spawn(h, player, g)
	end
	return g
end

local function checkout(g: Guest)
	local player = g.owner
	if not player or not g.room then
		destroy(g)
		return
	end
	local plot = PlotService.of(player)
	local satisfaction = Stay.satisfaction({
		prefsMatched = g.prefsMatched,
		tier = g.tier,
		amenities = g.amenities,
		requestsPlayer = g.requestsPlayer,
		requestsStaff = g.requestsStaff,
		requestsMissed = g.requestsMissed,
		deskWait = g.waited,
	})
	if g.happyFloor then
		satisfaction = math.max(satisfaction, g.happyFloor)
	end
	local sp = assert(Species.get(g.species))
	local stay = Constants.Rarity[sp.rarity].stay
	local tip = Stay.tip(g.payRate, stay, satisfaction)
	PlayerData.addTill(player, tip)
	local stars = Stay.review(satisfaction)
	HotelService.addReview(player, stars)
	HotelService.recordStay(player, g.prefsMatched / math.max(1, #sp.prefs))
	PlayerData.stat(player, "stays")
	if Stay.isHappy(satisfaction) then
		PlayerData.stat(player, "happyStays")
	end
	local room = g.room
	HotelService.setRoom(player, room, "Dirty")
	g.config:SetAttribute("Happy", Stay.isHappy(satisfaction))
	local bed = PlotService.piecePoint(plot :: any, room, "Bed")
	Net.fire(player, "Pop", tip, if bed then bed.Position else nil, "Tip")
	for _, h in checkoutHandlers do
		task.spawn(h, player, g, satisfaction)
	end
	-- Walk back out the way it came in: the desk-to-bed path, reversed.
	local data = PlayerData.get(player)
	local desk = plot and queueSpot(plot, 1)
	local inPath = if plot and data and desk then roomPath(plot, data, desk, room) else nil
	g.state = "Leaving"
	g.room = nil
	g.requestUntil = nil
	if plot and inPath then
		walk(g, exitPath(plot, reversed(inPath)))
	else
		sendHome(g, plot)
	end
	publish(g)
end

-- A request fulfilled, by the player (at the door) or by Room Service staff.
function GuestService.fulfil(player: Player, pieceId: string, byStaff: boolean): boolean
	local hotel = HotelService.get(player)
	local room = hotel and hotel.rooms[pieceId]
	local g = room and room.guest and guests[room.guest]
	if not g or not g.requestUntil then
		return false
	end
	g.requestUntil = nil
	if byStaff then
		g.requestsStaff += 1
	else
		g.requestsPlayer += 1
		local bonus = math.floor(g.payRate * S.RequestTipSeconds)
		PlayerData.addTill(player, bonus)
		Net.fire(player, "Pop", bonus, here(g), "Tip")
	end
	HotelService.setRequest(player, pieceId, nil)
	HotelService.recordRequest(player, true)
	PlayerData.stat(player, "requests")
	publish(g)
	return true
end

-- A dirty room cleaned, by the player (holding the door's prompt) or Housekeeping.
function GuestService.clean(player: Player, pieceId: string): boolean
	local hotel = HotelService.get(player)
	local room = hotel and hotel.rooms[pieceId]
	if not room or room.state ~= "Dirty" then
		return false
	end
	HotelService.setRoom(player, pieceId, "Vacant")
	PlayerData.stat(player, "cleaned")
	return true
end

function GuestService.collectTill(player: Player)
	local data = PlayerData.get(player)
	if not data or data.till <= 0 then
		return
	end
	local amount = math.floor(data.till)
	data.till = 0
	player:SetAttribute("Till", 0)
	PlayerData.earn(player, amount)
	local plot = PlotService.of(player)
	local at = plot and PlotService.lobbyPoint(plot, "Till")
	Net.fire(player, "Pop", amount, if at then at.Position else nil, "Collect")
	PlayerData.stat(player, "collects")
end

function GuestService.onCheckout(handler: (Player, Guest, number) -> ())
	table.insert(checkoutHandlers, handler)
end

function GuestService.onCheckIn(handler: (Player, Guest) -> ())
	table.insert(checkInHandlers, handler)
end

function GuestService.all(): { [number]: Guest }
	return guests
end

function GuestService.get(id: number): Guest?
	return guests[id]
end

-- The guests staying in or heading to a player's hotel.
function GuestService.of(player: Player): { Guest }
	local out = {}
	for _, g in guests do
		if g.owner == player and g.state ~= "Leaving" then
			table.insert(out, g)
		end
	end
	return out
end

-- Pauses walk-ins for a player (the tutorial times its first one itself).
function GuestService.setWalkIns(player: Player, on: boolean)
	walkInsOff[player] = if on then nil else true
end

-- Bellhop staff (§4.6): guests walk faster in this hotel.
function GuestService.setSpeedBonus(player: Player, bonus: number)
	speedBonus[player] = bonus
end

-- Takes a guest away (a hunter's net, §8.1): frees its room and sends it off unhappy.
function GuestService.remove(g: Guest)
	local player = g.owner
	if player and g.room then
		HotelService.setRoom(player, g.room, if g.state == "InRoom" then "Dirty" else "Vacant")
		if g.state == "Queued" or g.state == "ToHotel" then
			leaveQueue(player, g)
		end
	end
	destroy(g)
end

local function walkInInterval(player: Player): number
	local data = PlayerData.get(player)
	local rooms = 0
	if data then
		for _, rec in data.layout do
			local p = Pieces.get(rec.item)
			if p and p.kind == "Room" then
				rooms += 1
			end
		end
	end
	local W = Constants.WalkIn
	local rating = math.max(1, HotelService.rating(player))
	local t = W.BaseInterval / (1 + W.PerRoom * rooms) * (W.RatingPivot / rating)
	return math.clamp(t, W.MinInterval, W.MaxInterval)
end

local function tick()
	local now = os.clock()
	for _, g in guests do
		if g.state == "Browsing" then
			if now >= g.arriveAt then
				local decide = g.onDecide
				g.onDecide = nil
				if decide then
					decide(g)
				else
					sendHome(g, nil)
				end
			end
		elseif g.state == "ToHotel" then
			if now >= g.arriveAt then
				g.state = "Queued"
				g.deskSince = now
				publish(g)
			end
		elseif g.state == "Queued" then
			if g.owner and now - (g.deskSince or now) > S.DeskPatience then
				-- Gave up waiting: a 1-star review, and the room is free again.
				local player = g.owner
				leaveQueue(player, g)
				if g.room then
					HotelService.setRoom(player, g.room, "Vacant")
				end
				HotelService.addReview(player, 1)
				sendHome(g, PlotService.of(player))
			end
		elseif g.state == "ToRoom" then
			if now >= g.arriveAt then
				g.state = "InRoom"
				local sp = assert(Species.get(g.species))
				local stay = Constants.Rarity[sp.rarity].stay
				g.stayEnd = now + stay
				g.requestAt = now + stay * (0.25 + 0.5 * rng:NextNumber())
				publish(g)
			end
		elseif g.state == "InRoom" then
			local player = g.owner
			if g.requestAt and now >= g.requestAt then
				g.requestAt = nil
				g.requestUntil = now + S.RequestWindow
				if player and g.room then
					HotelService.setRequest(player, g.room, (Species.get(g.species) :: any).request)
				end
				publish(g)
			elseif g.requestUntil and now >= g.requestUntil then
				g.requestUntil = nil
				g.requestsMissed += 1
				if player and g.room then
					HotelService.setRequest(player, g.room, nil)
					HotelService.recordRequest(player, false)
				end
				publish(g)
			end
			if g.stayEnd and now >= g.stayEnd then
				checkout(g)
			end
		elseif g.state == "Leaving" then
			if now >= g.arriveAt then
				destroy(g)
			end
		end
	end
	-- Walk-ins.
	for player, data in PlayerData.loaded() do
		if not walkInsOff[player] and PlotService.of(player) then
			local at = nextWalkIn[player]
			if not at then
				nextWalkIn[player] = now + walkInInterval(player)
			elseif now >= at then
				nextWalkIn[player] = now + walkInInterval(player)
				GuestService.spawnWalkIn(player)
			end
		end
		local _ = data
	end
end

-- Pay per second into the till (§4.4), batched once a second per hotel.
local function payTick()
	local owed: { [Player]: number } = {}
	for _, g in guests do
		if g.state == "InRoom" and g.owner then
			owed[g.owner] = (owed[g.owner] or 0) + g.payRate
		end
	end
	for player, amount in owed do
		local data = PlayerData.get(player)
		if data and data.passes.AutoCollect then
			PlayerData.earn(player, amount)
		else
			PlayerData.addTill(player, amount)
		end
	end
end

function GuestService.Init()
	local old = ReplicatedStorage:FindFirstChild("Guests")
	if old then
		old:Destroy()
	end
	folder = Instance.new("Folder")
	folder.Name = "Guests"
	folder.Parent = ReplicatedStorage
end

function GuestService.Start()
	DevGrant.register("walkin", function(player, args)
		local g = GuestService.spawnWalkIn(player, args[1])
		return if g then `guest {g.id} {g.species} -> room {g.room}` else "no vacant room for it"
	end)
	DevGrant.register("checkin", function(player)
		local g = GuestService.checkIn(player, false)
		return if g then `checked in {g.id}` else "nobody waiting"
	end)
	DevGrant.register("guests", function()
		local lines = {}
		for id, g in guests do
			table.insert(lines, `{id} {g.species} {g.state} room={g.room} pay={g.payRate}`)
		end
		return table.concat(lines, " | ")
	end)
	DevGrant.register("request", function()
		-- Opens a request in every occupied room now.
		local n = 0
		for _, g in guests do
			if g.state == "InRoom" and not g.requestUntil then
				g.requestAt = os.clock()
				n += 1
			end
		end
		return `{n} requests`
	end)
	DevGrant.register("finish", function()
		-- Ends every stay and walk now (to see a check-out without waiting).
		local now = os.clock()
		for _, g in guests do
			if g.state == "InRoom" then
				g.stayEnd = now
			elseif g.state ~= "Queued" then
				g.arriveAt = math.min(g.arriveAt, now)
			end
		end
		return "ok"
	end)
	PlotService.onPrompt(function(player, plot, kind, pieceId)
		if kind == "Desk" then
			GuestService.checkIn(player, false)
		elseif kind == "Till" then
			GuestService.collectTill(player)
		elseif kind == "Clean" and pieceId then
			GuestService.clean(player, pieceId)
		elseif kind == "Request" and pieceId then
			GuestService.fulfil(player, pieceId, false)
		end
		local _ = plot
	end)
	Net.on("Collect", function(player)
		-- From the HUD: only within reach of the till, as the prompt would be.
		local plot = PlotService.of(player)
		local at = plot and PlotService.lobbyPoint(plot, "Till")
		local character = player.Character
		if at and character and (character:GetPivot().Position - at.Position).Magnitude <= 14 then
			GuestService.collectTill(player)
		end
	end)
	PlayerData.onDeparted(function(player)
		nextWalkIn[player] = nil
		walkInsOff[player] = nil
		speedBonus[player] = nil
		for _, g in guests do
			if g.owner == player then
				destroy(g)
			end
		end
	end)
	task.spawn(function()
		while true do
			task.wait(0.2)
			local ok, err = pcall(tick)
			if not ok then
				warn(`[guests] tick failed: {err}`)
			end
		end
	end)
	task.spawn(function()
		while true do
			task.wait(1)
			local ok, err = pcall(payTick)
			if not ok then
				warn(`[guests] pay failed: {err}`)
			end
		end
	end)
	local _ = Players
end

return GuestService
