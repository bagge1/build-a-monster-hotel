--!strict
--[[
	Guests (GDD §4.3, §4.4, §13.2). THE SERVER SIMULATES, THE CLIENT PAINTS:
	a guest here is a state machine and a path, never a model. Each one is
	published as a `Configuration` in `ReplicatedStorage.Guests` whose
	attributes say what it is and where it walks; every client draws it
	locally (`GuestRenderer`), so six hotels of guests cost a phone nothing in
	physics.

	States (§13.2): Browsing (a bus guest walking the pavements, pausing at
	each entrance) → ToHotel → Queued (at the desk) → ToRoom → InRoom (paying
	per second into the till, with one request) → Leaving (walking back to a
	bus stop) → Waiting (at the stop) → Boarding (onto the next bus). A guest
	that waits too long at the desk leaves unhappy; a guest no hotel takes
	walks back to a stop too. **Every guest comes and goes by the Night Bus**
	(his ruling, 2026-10-19: no walk-ins, nobody walks off the map's edge),
	but the tutorial's first, who walks in before the first bus.

	Published per guest: `Species`, `Mutation`, `State`, `Plot`, `Path`
	(`Walk.encode`: points, and seconds standing at some), `T0` (server time
	the path starts), `Speed`, `Wish` (a bus guest's wish list), `Request`,
	`Happy`.

	What other systems hook: `onCheckout(player, guest, satisfaction)` for
	friendship (§4.6); `checkIn`, `clean`, `fulfil` and `pathToDoor` for staff;
	`spawnTutorial` for the tutorial's first guest; `spawnBrowsing`, `assign`,
	`leaveStreet` and `board` for the bus.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Grid = require(ReplicatedStorage.Shared.Grid)
local Layout = require(ReplicatedStorage.Shared.Layout)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Species = require(ReplicatedStorage.Shared.Species)
local Stay = require(ReplicatedStorage.Shared.Stay)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)
local Walk = require(ReplicatedStorage.Shared.Walk)
local Events = require(ReplicatedStorage.Shared.Events)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local Income = require(ServerScriptService.Server.Income)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local S = Constants.Stay

local GuestService = {}

export type State =
	"Browsing"
	| "ToHotel"
	| "Queued"
	| "ToRoom"
	| "InRoom"
	| "Leaving"
	| "Waiting"
	| "Boarding"
export type Guest = {
	id: number,
	species: string,
	mutation: string?,
	source: string, -- "Bus" | "Tutorial" | "Dev"
	owner: Player?,
	room: string?,
	state: State,
	arriveAt: number, -- os.clock() when the current path ends
	startedAt: number, -- os.clock() when the current path began
	path: { Vector3 },
	waits: Walk.Waits, -- seconds standing at a point of the path
	walkSpeed: number, -- the current path's speed (with any Bellhop bonus)
	stop: string?, -- the bus stop a leaving guest walks to and waits at
	speed: number,
	desk: string?, -- the desk (a piece id) it queues at: the shortest line when it came (§5.4, A.1)
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
	tutorialFriend: boolean?, -- the tutorial Slime: moves in after 1 happy stay (§6.3)
	pitches: { [number]: number }, -- user id -> plot index (§4.3)
	wish: string?,
	config: Configuration,
	onDecide: ((Guest) -> ())?, -- a bus guest at the end of its browse
}

local guests: { [number]: Guest } = {}
local nextId = 1
local folder: Folder
local rng = Random.new()
local checkoutHandlers: { (Player, Guest, number) -> () } = {}
local checkInHandlers: { (Player, Guest) -> () } = {}
local speedBonus: { [Player]: number } = {}

local function publish(g: Guest)
	local c = g.config
	c:SetAttribute("State", g.state)
	c:SetAttribute("Plot", if g.owner then (g.owner:GetAttribute("Plot") or 0) else 0)
	c:SetAttribute(
		"Request",
		if g.requestUntil then (Species.get(g.species) :: any).request else nil
	)
end

-- Sends the guest along `path` at its speed, from now, standing `waits` seconds at some points.
local function walk(g: Guest, path: { Vector3 }, waits: Walk.Waits?)
	g.path = path
	g.waits = waits or {}
	local speed = g.speed
	if g.owner and speedBonus[g.owner] and g.state ~= "Browsing" then
		speed *= 1 + speedBonus[g.owner]
	end
	g.walkSpeed = speed
	g.startedAt = os.clock()
	g.arriveAt = g.startedAt + Walk.duration(path, g.waits, speed)
	g.config:SetAttribute("Speed", speed)
	g.config:SetAttribute("T0", workspace:GetServerTimeNow())
	g.config:SetAttribute("Path", Walk.encode(path, g.waits))
end

local function here(g: Guest): Vector3
	-- Where the guest is now along its path (the same arithmetic the client draws with).
	local p = Walk.sample(g.path, g.waits, g.walkSpeed, os.clock() - g.startedAt)
	return p
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
		startedAt = os.clock(),
		path = {},
		waits = {},
		walkSpeed = Constants.Stay.WalkSpeed,
		stop = nil,
		speed = Constants.Stay.WalkSpeed,
		desk = nil,
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

-- The hotel's desks (piece ids), lowest first: the first is the one staff work at (HotelPoints).
local function desks(data: PlayerData.Data): { string }
	local out = {}
	for id, rec in data.layout do
		local piece = Pieces.get(rec.item)
		if piece and piece.kind == "Desk" then
			table.insert(out, id)
		end
	end
	table.sort(out, function(a, b)
		return (tonumber(a) or 0) < (tonumber(b) or 0)
	end)
	return out
end

--[[ The walk from a desk's queue (`deskId`, else the first desk) to a room's
	bed (§5.4): to the cell in front of the desk, along the hallways and up or
	down the placed stairs (Grid.route), to the door, in, to the bed (only to
	the door with `toDoor`: staff on an errand, §4.6). ]]
local function roomPath(
	plot: PlotService.Plot,
	data: PlayerData.Data,
	from: Vector3,
	pieceId: string,
	toDoor: boolean?,
	deskId: string?
): { Vector3 }?
	local world = PlotService.world(data)
	local room = Layout.find(world, pieceId)
	local desk = (deskId and Layout.find(world, deskId)) or Layout.find(world, desks(data)[1] or "")
	if not room or not desk then
		return nil
	end
	local door = Grid.doorCell(room)
	local legs =
		Grid.route(world, Grid.doors(desk)[1], { floor = room.floor, x = door.x, z = door.z })
	if not legs then
		return nil
	end
	local out: { Vector3 } = { from }
	for _, leg in legs do
		if leg.stair then
			local glide = PlotService.stairPath(plot, (leg.stair :: Grid.Placed).id :: string)
			if #glide == 0 then
				return nil
			end
			for i = 1, #glide do
				table.insert(out, if leg.up then glide[i] else glide[#glide + 1 - i])
			end
		else
			for _, c in leg.cells :: { Grid.Cell } do
				table.insert(out, toWorld(plot, leg.floor :: number, c))
			end
		end
	end
	local doorPoint = PlotService.piecePoint(plot, pieceId, "Door")
	local bed = PlotService.piecePoint(plot, pieceId, "Bed")
	if doorPoint then
		table.insert(out, doorPoint.Position)
	end
	if bed and not toDoor then
		table.insert(out, bed.Position)
	end
	return out
end

--[[ The walk from `from` (on floor 1) to a room's door by the guests' own
	hallways and stairs, or nil if there is none: staff on an errand
	(ResidentService, §4.6 "Staff are seen working"). ]]
function GuestService.pathToDoor(player: Player, from: Vector3, pieceId: string): { Vector3 }?
	local plot = PlotService.of(player)
	local data = PlayerData.get(player)
	return if plot and data then roomPath(plot, data, from, pieceId, true) else nil
end

local function reversed(path: { Vector3 }): { Vector3 }
	local out = table.create(#path)
	for i = #path, 1, -1 do
		table.insert(out, path[i])
	end
	return out
end

-- ===== The street (§4.3, §5.4) =====

-- From the street to a hotel's entrance: onto its pavement, along to its path, up the path to the arch.
local function toHotel(plot: PlotService.Plot, from: Vector3): { Vector3 }
	local out = StreetLayout.ontoPavement(from, StreetLayout.side(plot.index))
	table.insert(out, StreetLayout.pavementFront(plot.index))
	local foot = PlotService.forecourtPoint(plot, "PathFoot")
	if foot then
		table.insert(out, foot.Position)
	end
	local entrance = PlotService.point(plot, "Entrance")
	if entrance then
		table.insert(out, entrance.Position)
	end
	return out
end

-- Where the next guest to wait at `stop` stands: a little crowd on the pavement by the shelter.
local function waitSpot(stop: StreetLayout.Stop): Vector3
	local k = 0
	for _, g in guests do
		if g.stop == stop.name then
			k += 1
		end
	end
	local col, row = k % 5, (k // 5) % 3
	return stop.wait + Vector3.new((col - 2) * 2.4, 0, (row - 1) * 1.8)
end

--[[ On from the end of `out` to the nearest bus stop, to wait there for the
	next bus (his ruling, 2026-10-19: a guest never walks off the map's edge). ]]
local function toStop(g: Guest, out: { Vector3 }): { Vector3 }
	local last = out[#out]
	local stop = StreetLayout.nearestStop(last)
	for _, p in StreetLayout.ontoPavement(last, 1) do
		table.insert(out, p)
	end
	table.insert(out, waitSpot(stop))
	g.stop = stop.name
	return out
end

-- Out of the hotel: through the arch, down the path to the pavement, and on to a bus stop.
local function exitPath(g: Guest, plot: PlotService.Plot, from: { Vector3 }): { Vector3 }
	local out = from
	local entrance = PlotService.point(plot, "Entrance")
	if entrance then
		table.insert(out, entrance.Position)
	end
	local foot = PlotService.forecourtPoint(plot, "PathFoot")
	if foot then
		table.insert(out, foot.Position)
	end
	table.insert(out, StreetLayout.pavementFront(plot.index))
	return toStop(g, out)
end

-- ===== The desk queues (§5.4, A.1: one or more desks) =====

-- Where the k-th guest in a desk's line stands.
local function queueSpot(plot: PlotService.Plot, deskId: string?, k: number): Vector3?
	local at = deskId and PlotService.piecePoint(plot, deskId, `Queue_{math.min(k, 4)}`)
	if not at then
		return nil
	end
	if k > 4 then
		-- On down the line, away from the desk (Queue_n look at it, MODELS.md "Front desk").
		return (at * CFrame.new(0, 0, (k - 4) * 3)).Position
	end
	return at.Position
end

-- How many guests in the hotel's queue are bound for each desk.
local function deskLines(hotel: HotelService.Hotel): { [string]: number }
	local out = {}
	for _, id in hotel.queue do
		local g = guests[id]
		if g and g.desk then
			out[g.desk] = (out[g.desk] or 0) + 1
		end
	end
	return out
end

-- The desk with the shortest line (the first of equals), or nil without a desk.
local function shortestDesk(data: PlayerData.Data, hotel: HotelService.Hotel): string?
	local counts = deskLines(hotel)
	local best, bestCount = nil, math.huge
	for _, id in desks(data) do
		local n = counts[id] or 0
		if n < bestCount then
			best, bestCount = id, n
		end
	end
	return best
end

--[[ Stands every waiting guest in its desk's line again: a guest whose desk
	is gone (sold) goes to the shortest line, and each walks to its place
	when it is not there (a desk moved, someone ahead checked in). ]]
local function requeue(player: Player)
	local hotel = HotelService.get(player)
	local plot = PlotService.of(player)
	local data = PlayerData.get(player)
	if not hotel or not plot or not data then
		return
	end
	for _, id in hotel.queue do
		local g = guests[id]
		if g and not (g.desk and data.layout[g.desk]) then
			g.desk = nil
			g.desk = shortestDesk(data, hotel)
		end
	end
	local k: { [string]: number } = {}
	for _, id in hotel.queue do
		local g = guests[id]
		if g and g.desk then
			k[g.desk] = (k[g.desk] or 0) + 1
			local spot = queueSpot(plot, g.desk, k[g.desk])
			if spot and g.state == "Queued" then
				local now = here(g)
				if (now - spot).Magnitude > 0.5 then
					walk(g, { now, spot })
				end
			end
			g.config:SetAttribute("Queue", k[g.desk])
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
	g.speed = S.WalkSpeed
	if plot then
		walk(g, exitPath(g, plot, { here(g) }))
	else
		walk(g, toStop(g, { here(g) }))
	end
	publish(g)
end

--[[ Points a guest at a hotel: reserves the room and walks it from where it
	stands on the street to the desk queue, by the pavement and the path. ]]
function GuestService.assign(g: Guest, player: Player, pieceId: string)
	local plot = PlotService.of(player)
	local hotel = HotelService.get(player)
	if not plot or not hotel then
		sendHome(g, nil)
		return
	end
	g.owner = player
	g.room = pieceId
	g.speed = S.WalkSpeed
	HotelService.setRoom(player, pieceId, "Reserved", g.id)
	local data = PlayerData.get(player)
	g.desk = if data then shortestDesk(data, hotel) else nil
	table.insert(hotel.queue, g.id)
	local k = deskLines(hotel)[g.desk or ""] or 1
	local from = here(g)
	local path: { Vector3 } = { from }
	for _, p in toHotel(plot, from) do
		table.insert(path, p)
	end
	local spot = queueSpot(plot, g.desk, k)
	if spot then
		table.insert(path, spot)
	end
	g.state = "ToHotel"
	g.config:SetAttribute("Queue", k)
	walk(g, path)
	publish(g)
end

--[[ The tutorial's first guest (§11), the only guest that does not come on the
	bus (his ruling, 2026-10-19): it appears on the pavement a little along
	from the hotel and walks in, before the first bus. Also the Studio-only
	`guest` command. Nil if the hotel has no vacant room for it. ]]
function GuestService.spawnTutorial(
	player: Player,
	speciesId: string,
	opts: {
		happyFloor: number?,
		source: string?,
		tutorialFriend: boolean?,
	}?
): Guest?
	local plot = PlotService.of(player)
	local offer = HotelService.vacantFor(player, speciesId)
	if not plot or not offer then
		return nil
	end
	local mutation = Events.rollMutation(rng:NextNumber(), os.time())
	local g =
		newGuest(speciesId, mutation, if opts and opts.source then opts.source else "Tutorial")
	g.happyFloor = opts and opts.happyFloor
	g.tutorialFriend = opts ~= nil and opts.tutorialFriend == true
	local front = StreetLayout.pavementFront(plot.index)
	local side = if rng:NextNumber() < 0.5 then -1 else 1
	g.path = { front + Vector3.new(side * 40, 0, 0) }
	g.config.Parent = folder
	GuestService.assign(g, player, offer.pieceId)
	return g
end

--[[ A bus guest (§4.3) stepping off at `stop`: onto a pavement, then
	browsing round the ring for `BrowseTime`, pausing at the entrance of every
	hotel on the street it passes; `onDecide` is called when the browse ends.
	`variant` 0–3 picks the pavement it starts on (the north, or straight
	across the lane to the south) and the way it walks, so a bus's guests
	between them pass every hotel. ]]
function GuestService.spawnBrowsing(
	speciesId: string,
	mutation: string?,
	stop: StreetLayout.Stop,
	variant: number,
	wish: string,
	onDecide: (Guest) -> ()
): Guest
	local B = Constants.Bus
	local g = newGuest(speciesId, mutation, "Bus")
	g.state = "Browsing"
	g.speed = B.BrowseSpeed
	g.wish = wish
	g.onDecide = onDecide
	g.config:SetAttribute("Wish", wish)
	local looks: { StreetLayout.Look } = {}
	for _, plot in PlotService.all() do
		if plot.owner then
			table.insert(looks, {
				s = StreetLayout.ringParam(StreetLayout.pavementFront(plot.index)),
				toward = Vector3.new(0, 0, StreetLayout.side(plot.index)),
			})
		end
	end
	local side = if variant % 4 < 2 then 1 else -1
	local dir = if variant % 2 == 0 then 1 else -1
	local kerb = stop.kerb + Vector3.new((rng:NextNumber() - 0.5) * 2, 0, 0)
	local cross = StreetLayout.ontoPavement(kerb, side)
	local start = cross[#cross] or kerb
	local ring, ringWaits = StreetLayout.browse(
		StreetLayout.ringParam(start),
		dir,
		looks,
		B.BrowseTime,
		g.speed,
		B.EntrancePause * (0.8 + 0.4 * rng:NextNumber())
	)
	local path: { Vector3 } = { kerb }
	local waits: Walk.Waits = {}
	for i, p in ring do
		table.insert(path, p)
		waits[#path] = ringWaits[i]
	end
	walk(g, path, waits)
	g.config.Parent = folder
	publish(g)
	return g
end

-- A guest no hotel took (or one the bus has no stop for) walks back to a stop and waits for the next bus.
function GuestService.leaveStreet(g: Guest)
	g.owner = nil
	sendHome(g, nil)
end

-- The bus is at `stopName`: everyone waiting there walks to its door and is gone with it.
function GuestService.board(stopName: string)
	local stop: StreetLayout.Stop? = nil
	for _, s in StreetLayout.Stops do
		if s.name == stopName then
			stop = s
		end
	end
	if not stop then
		return
	end
	for _, g in guests do
		if g.state == "Waiting" and g.stop == stopName then
			g.state = "Boarding"
			walk(g, { here(g), stop.kerb })
			publish(g)
		end
	end
end

--[[ Checks the first waiting guest in: at desk `deskId` (the player's tap
	there), or at any desk (Front Desk staff, the Studio command). ]]
function GuestService.checkIn(player: Player, byStaff: boolean?, deskId: string?): Guest?
	local hotel = HotelService.get(player)
	local plot = PlotService.of(player)
	local data = PlayerData.get(player)
	if not hotel or not plot or not data then
		return nil
	end
	local g: Guest? = nil
	for _, id in hotel.queue do
		local candidate = guests[id]
		if
			candidate
			and candidate.state == "Queued"
			and (deskId == nil or candidate.desk == deskId)
		then
			g = candidate
			break
		end
	end
	if not g or not g.room then
		return nil
	end
	local rec = data.layout[g.room]
	local path = roomPath(plot, data, here(g), g.room, false, g.desk)
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
	g.tier = HotelService.tier(data, g.room)
	g.prefsMatched = Stay.matched(sp.prefs, HotelService.roomTags(data, g.room))
	g.amenities = HotelService.amenitiesOn(data, rec.floor)
	local typeCount = 0
	for _, other in data.layout do
		if other.item == rec.item then
			typeCount += 1
		end
	end
	g.payRate =
		Economy.guestPay(g.species, g.tier, g.mutation, typeCount, Income.multiplier(player))
	leaveQueue(player, g)
	HotelService.setRoom(player, g.room, "Occupied", g.id)
	g.state = "ToRoom"
	walk(g, path)
	publish(g)
	PlayerData.stat(player, "checkIns")
	local at = here(g)
	Net.fire(
		player,
		"Moment",
		"CheckIn",
		{ species = g.species, mutation = g.mutation, byStaff = byStaff == true, at = at }
	)
	-- A rare check-in is the street's moment (§11 "a flashy check-in, a street-wide announcement").
	if sp.rarity == "Legendary" or sp.rarity == "Mythic" then
		local mutationName = if g.mutation then g.mutation .. " " else ""
		Net.fireAll(
			"Announce",
			`{player.DisplayName} checked in a {sp.rarity} {mutationName}{sp.name}!`,
			"Rare"
		)
		Net.fireAll("Moment", "RareCheckIn", { species = g.species, at = at })
	end
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
	local tip = math.floor(
		Stay.tip(g.payRate, stay, satisfaction) * (1 + GuestService.tipBonus(player, "Tips"))
	)
	PlayerData.addTill(player, tip)
	local stars = Stay.review(satisfaction)
	HotelService.addReview(player, stars)
	HotelService.recordStay(player, g.prefsMatched / math.max(1, #sp.prefs))
	PlayerData.stat(player, "stays")
	PlayerData.stat(player, `served_{g.species}`)
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
	local deskId = if data
			and g.desk
			and data.layout[g.desk]
		then g.desk
		elseif data then desks(data)[1]
		else nil
	local desk = plot and queueSpot(plot, deskId, 1)
	local inPath = if plot
			and data
			and desk
		then roomPath(plot, data, desk, room, false, deskId)
		else nil
	g.state = "Leaving"
	g.room = nil
	g.requestUntil = nil
	g.speed = S.WalkSpeed
	if plot and inPath then
		walk(g, exitPath(g, plot, reversed(inPath)))
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
		local bonus = math.floor(
			g.payRate * S.RequestTipSeconds * (1 + GuestService.tipBonus(player, "RequestTips"))
		)
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
	local at = plot and PlotService.point(plot, "Till")
	Net.fire(player, "Pop", amount, if at then at.Position else nil, "Collect")
	PlayerData.stat(player, "collects")
end

-- A tip's bonus fraction for `kind` ("Tips", "RequestTips"); residents' perks set it (ResidentService).
function GuestService.tipBonus(_player: Player, _kind: string): number
	return 0
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
		if
			g.owner == player
			and g.state ~= "Leaving"
			and g.state ~= "Waiting"
			and g.state ~= "Boarding"
		then
			table.insert(out, g)
		end
	end
	return out
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
				if g.owner then
					-- Its line may have moved on while it walked (a desk moved or sold).
					requeue(g.owner)
				end
			end
		elseif g.state == "Queued" then
			-- The tutorial's guest waits as long as the new player needs (§11: the
			-- tutorial never traps anyone, and its stay counts as happy).
			if g.owner and not g.tutorialFriend and now - (g.deskSince or now) > S.DeskPatience then
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
				-- At the stop: nobody's guest any more, waiting for the next bus.
				g.state = "Waiting"
				g.owner = nil
				publish(g)
			end
		elseif g.state == "Boarding" then
			if now >= g.arriveAt then
				destroy(g)
			end
		end
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
	DevGrant.register("guest", function(player, args)
		-- Studio only: a guest of `args[1]` (a Slime by default) walks in from the pavement, as the tutorial's does.
		local g = GuestService.spawnTutorial(player, args[1] or "Slime", { source = "Dev" })
		return if g then `guest {g.id} {g.species} -> room {g.room}` else "no vacant room for it"
	end)
	DevGrant.register("checkin", function(player, args)
		-- At any desk, or at desk `args[1]` (a piece id).
		local g = GuestService.checkIn(player, false, args[1])
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
			GuestService.checkIn(player, false, pieceId)
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
		-- From the HUD: only within reach of a desk's till, as the prompt would be.
		local plot = PlotService.of(player)
		local data = PlayerData.get(player)
		local character = player.Character
		if not plot or not data or not character then
			return
		end
		for _, id in desks(data) do
			local at = PlotService.piecePoint(plot, id, "Till")
			if at and (character:GetPivot().Position - at.Position).Magnitude <= 14 then
				GuestService.collectTill(player)
				return
			end
		end
	end)
	-- A desk moved or sold rebuilds the hotel: its line walks to its new place or another desk.
	PlotService.onBuilt(function(plot)
		if plot.owner then
			requeue(plot.owner)
		end
	end)
	PlayerData.onDeparted(function(player)
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
