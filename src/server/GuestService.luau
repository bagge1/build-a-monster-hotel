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
	bus stop) → Waiting (at the stop) → Boarding (onto the next bus). While it
	stays, an InRoom guest goes Visiting now and then (GDD A.13.1, `Visits`):
	to an activity room's free spot, doing the action there, and back, still
	paying; its room stays Occupied, and a request or a check-out waits until
	it is back. A guest
	that waits too long at the desk leaves unhappy; a guest no hotel takes
	walks back to a stop too. **Every guest comes and goes by the Night Bus**
	(his ruling, 2026-10-19: no walk-ins, nobody walks off the map's edge),
	but the tutorial's first, who walks in before the first bus.

	Published per guest: `Species`, `Mutation` (the look), `Size` (A.11.5), `State`, `Plot`, `Path`
	(`Walk.encode`: points, and seconds standing at some), `T0` (server time
	the path starts), `Speed`, `Wish` (a bus guest's wish list), `Request`,
	`Happy`; a visitor's `Pose` (its spot's, MODELS.md) and `Face` (the spot's
	LookVector) while it goes to or is at its spot (A.13.1).

	What other systems hook: `onCheckout(player, guest, satisfaction)` for
	friendship (§4.6); `checkIn`, `clean`, `fulfil` and `pathToDoor` for staff;
	`spawnTutorial` for the tutorial's first guest; `spawnBrowsing`, `assign`,
	`leaveStreet` and `board` for the bus.

	ONE WORLD (§3, §6.4): a guest belongs to one street (`street`), the one
	its bus stopped on: it browses that street's hotels, walks that street's
	pavements and waits at its stops. A played hotel's guests are on its
	street because the plot stands there.
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
local Rooms = require(ReplicatedStorage.Shared.Rooms)
local Species = require(ReplicatedStorage.Shared.Species)
local Stay = require(ReplicatedStorage.Shared.Stay)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)
local Walk = require(ReplicatedStorage.Shared.Walk)
local Events = require(ReplicatedStorage.Shared.Events)
local Mutations = require(ReplicatedStorage.Shared.Mutations)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local ActivityKit = require(ServerScriptService.Server.ActivityKit)
local Income = require(ServerScriptService.Server.Income)
local DevGrant = require(ServerScriptService.Server.DevGrant)
local StateService = require(ServerScriptService.Server.StateService)
local Visits = require(ReplicatedStorage.Shared.Visits)

local S = Constants.Stay

local GuestService = {}

export type State =
	"Browsing"
	| "ToHotel"
	| "Queued"
	| "ToRoom"
	| "InRoom"
	| "Visiting"
	| "Leaving"
	| "Waiting"
	| "Boarding"
export type Guest = {
	id: number,
	species: string,
	mutation: string?, -- the look (A.11.5)
	size: string?, -- Tiny or Giant, stacked with the look (A.11.5)
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
	street: number, -- the street it came to (StreetLayout), whose hotels it browses
	speed: number,
	desk: string?, -- the desk (a piece id) it queues at: the shortest line when it came (§5.4, A.1)
	deskSince: number?,
	waited: number,
	payRate: number,
	tier: number,
	-- What the room's three bars give (GDD A.12, Rooms.bonuses), set at check-in.
	stayMult: number,
	satBonus: number,
	friendshipMult: number,
	prefsMatched: number,
	stayEnd: number?,
	requestAt: number?,
	requestUntil: number?,
	requestsPlayer: number,
	requestsStaff: number,
	requestsMissed: number,
	happyFloor: number?, -- the tutorial's: a stay at least this happy (Appendix A.7)
	tutorialFriend: boolean?, -- the tutorial Slime: moves in after 1 happy stay (§6.3)
	vip: boolean?, -- a VIP booked by a contract (A.11.1): waits at the desk, its pay × Contracts.VipPay
	pitches: { [number]: number }, -- user id -> plot index (§4.3)
	wish: string?,
	config: Configuration,
	onDecide: ((Guest) -> ())?, -- a bus guest at the end of its browse
	-- Visits (GDD A.13.1): when the next is due, the last decision, the preferences met this
	-- stay (its room's tags and its visits'), whether a visit's satisfaction was given, and,
	-- on a visit, when its action ends and the square it walked to (its way back starts there).
	visitDue: number?,
	visitDecided: number?,
	met: { [string]: boolean },
	visitRewarded: boolean,
	visitUntil: number?,
	visitSquare: Rooms.Spot?,
}

local guests: { [number]: Guest } = {}
local nextId = 1
local folder: Folder
local rng = Random.new()
local checkoutHandlers: { (Player, Guest, number) -> () } = {}
local checkInHandlers: { (Player, Guest) -> () } = {}

-- What each player's guests have paid this session (pay, tips, request tips):
-- the hotel's own income, which the chain measures (`ChainService`, §6.4).
local income: { [Player]: number } = {}
local function countIncome(player: Player, amount: number)
	income[player] = (income[player] or 0) + amount
end

function GuestService.income(player: Player): number
	return income[player] or 0
end
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

local function newGuest(speciesId: string, mutation: string?, source: string, size: string?): Guest
	local id = nextId
	nextId += 1
	local config = Instance.new("Configuration")
	config.Name = tostring(id)
	config:SetAttribute("Species", speciesId)
	config:SetAttribute("Mutation", mutation)
	config:SetAttribute("Size", size)
	local g: Guest = {
		id = id,
		species = speciesId,
		mutation = mutation,
		size = size,
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
		street = 1,
		speed = Constants.Stay.WalkSpeed,
		desk = nil,
		deskSince = nil,
		waited = 0,
		payRate = 0,
		tier = 1,
		stayMult = 1,
		satBonus = 0,
		friendshipMult = 1,
		prefsMatched = 0,
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
		visitDue = nil,
		visitDecided = nil,
		met = {},
		visitRewarded = false,
		visitUntil = nil,
		visitSquare = nil,
	}
	guests[id] = g
	return g
end

--[[ Ends a guest's visit, wherever it is (GDD A.13.1): its spot freed and its
	visit forgotten, so a guest sent home, taken or gone never holds a spot. ]]
local function endVisit(g: Guest)
	local hotel = g.owner and HotelService.get(g.owner)
	if not hotel then
		return
	end
	local key = tostring(g.id)
	local had = hotel.visitors[key] ~= nil
	hotel.visitors[key] = nil
	if Visits.free(hotel.taken, key) or had then
		StateService.mark(hotel.player) -- the room view's "n/m spots in use"
	end
	g.visitUntil = nil
	g.visitSquare = nil
	g.config:SetAttribute("Pose", nil)
	g.config:SetAttribute("Face", nil)
end

local function destroy(g: Guest)
	endVisit(g)
	guests[g.id] = nil
	g.config:Destroy()
end

-- ===== Paths through a hotel =====

-- A 3-stud square's centre (Rooms' walking grid, A.12 "Guests"), in the world.
local SQUARE = Constants.Grid.CellSize / Constants.Grid.Squares
local function squareWorld(plot: PlotService.Plot, floor: number, c: Grid.Cell): Vector3
	return plot.frame:PointToWorldSpace(
		Vector3.new((c.x + 0.5) * SQUARE, Grid.floorY(floor), (c.z + 0.5) * SQUARE)
	)
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

--[[ The walk from a desk's queue (`deskId`, else the first desk) to a built
	room's key furniture (A.12 "Guests"): from the square in front of the
	desk along the 3-stud squares between the walls, up or down the placed
	stairs, through the room's door (Rooms.route) to the square beside its
	key furniture (Rooms.keySpot), and onto it (the room's `Bed`: the
	furniture's `Use`). With `toDoor` only to the square outside the door:
	staff on an errand (§4.6). ]]
local function roomPath(
	plot: PlotService.Plot,
	data: PlayerData.Data,
	from: Vector3,
	pieceId: string,
	toDoor: boolean?,
	deskId: string?
): { Vector3 }?
	local world = PlotService.world(data)
	local desk = (deskId and Layout.find(world, deskId)) or Layout.find(world, desks(data)[1] or "")
	if not data.rooms[pieceId] or not desk then
		return nil
	end
	local start = Rooms.spotSquare(world, Grid.doors(desk)[1])
	local target = if toDoor
		then (Rooms.doorSquares(world, pieceId))
		else Rooms.keySpot(world, pieceId)
	if not start or not target then
		return nil
	end
	local legs = Rooms.route(world, start, target)
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
				table.insert(out, squareWorld(plot, leg.floor :: number, c))
			end
		end
	end
	local bed = PlotService.piecePoint(plot, pieceId, "Bed")
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
	table.insert(out, StreetLayout.pavementFront(plot.index, plot.street))
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
	table.insert(out, StreetLayout.pavementFront(plot.index, plot.street))
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
	endVisit(g)
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
	stands on the street to the desk queue, by the pavement and the path.
	Never into a room it cannot walk to from the desk (A.12 "Guests"):
	`Rooms.ready` promises a way to the key furniture, and this keeps the
	promise if a room slips through; the guest goes home instead. Answers
	whether it booked the guest (false: it went home). ]]
function GuestService.assign(g: Guest, player: Player, pieceId: string): boolean
	local plot = PlotService.of(player)
	local hotel = HotelService.get(player)
	local data = PlayerData.get(player)
	if not plot or not hotel or not data then
		sendHome(g, nil)
		return false
	end
	local desk = shortestDesk(data, hotel)
	if not roomPath(plot, data, here(g), pieceId, false, desk) then
		warn(
			`[guests] no way from the desk to room {pieceId}'s key furniture: {g.species} not booked`
		)
		sendHome(g, nil)
		return false
	end
	g.owner = player
	g.room = pieceId
	g.speed = S.WalkSpeed
	HotelService.setRoom(player, pieceId, "Reserved", g.id)
	g.desk = desk
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
	return true
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
	local size, mutation = Events.rollMutations(rng:NextNumber(), rng:NextNumber(), os.time())
	local g = newGuest(
		speciesId,
		mutation,
		if opts and opts.source then opts.source else "Tutorial",
		size
	)
	g.happyFloor = opts and opts.happyFloor
	g.tutorialFriend = opts ~= nil and opts.tutorialFriend == true
	g.street = plot.street
	local front = StreetLayout.pavementFront(plot.index, plot.street)
	local side = if rng:NextNumber() < 0.5 then -1 else 1
	g.path = { front + Vector3.new(side * 40, 0, 0) }
	g.config.Parent = folder
	GuestService.assign(g, player, offer.pieceId)
	return g
end

--[[ A bus guest (§4.3) stepping off at `stop`: onto a pavement, then
	browsing round the ring for `BrowseTime`, pausing at the entrance of every
	hotel played on the stop's street it passes; `onDecide` is called when the browse ends.
	`variant` 0–3 picks the pavement it starts on (the north, or straight
	across the lane to the south) and the way it walks, so a bus's guests
	between them pass every hotel. ]]
function GuestService.spawnBrowsing(
	speciesId: string,
	mutation: string?,
	stop: StreetLayout.Stop,
	variant: number,
	wish: string,
	onDecide: (Guest) -> (),
	size: string?
): Guest
	local B = Constants.Bus
	local g = newGuest(speciesId, mutation, "Bus", size)
	g.state = "Browsing"
	g.speed = B.BrowseSpeed
	g.wish = wish
	g.onDecide = onDecide
	g.street = stop.street
	g.config:SetAttribute("Wish", wish)
	local looks: { StreetLayout.Look } = {}
	for _, plot in PlotService.all() do
		if plot.owner and plot.street == stop.street then
			table.insert(looks, {
				s = StreetLayout.ringParam(StreetLayout.pavementFront(plot.index, plot.street)),
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
		B.EntrancePause * (0.8 + 0.4 * rng:NextNumber()),
		stop.street
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

--[[ A VIP of a contract (A.11.1): booked to `owner`'s hotel by the bus, it
	waits at the desk as long as it takes and pays `VipPay` × for its stay;
	every client draws "VIP for <name>" over it and a glow (`VipFor`). ]]
function GuestService.markVip(g: Guest, owner: Player)
	g.vip = true
	g.config:SetAttribute("VipFor", owner.DisplayName)
	g.config:SetAttribute("VipOwner", owner.UserId)
end

-- A guest no hotel took (or one the bus has no stop for) walks back to a stop and waits for the next bus.
function GuestService.leaveStreet(g: Guest)
	g.owner = nil
	sendHome(g, nil)
end

-- The bus is at `stopName` (a stop's name is unique in the world): everyone waiting there walks to its door and is gone with it.
function GuestService.board(stopName: string)
	local stop = StreetLayout.stopNamed(stopName)
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
	local rec = data.rooms[g.room]
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
	g.tier = 1
	-- Its room's own tags (A.12); the rest of its preferences are met by visits (A.13.1).
	local tags = HotelService.roomTags(data, g.room)
	g.prefsMatched = Stay.matched(sp.prefs, tags)
	g.met = {}
	for _, pref in sp.prefs do
		if tags[pref] then
			g.met[pref] = true
		end
	end
	g.visitRewarded = false
	-- The room's three bars' bonuses (A.12) replace the tiers' pay.
	local _, bonus = HotelService.roomBars(data, g.room)
	g.stayMult = if bonus then bonus.stay else 1
	g.satBonus = if bonus then bonus.satisfaction else 0
	g.friendshipMult = if bonus then bonus.friendship else 1
	local typeCount = HotelService.readyOfType(player, data, rec.type)
	g.payRate = Economy.guestPay(
		g.species,
		1,
		g.mutation,
		typeCount,
		Income.multiplier(player),
		g.size
	) * (if bonus then bonus.pay else 1)
	if g.vip then
		g.payRate *= Constants.Contracts.VipPay -- A.11.1: the VIP's pay for its stay
	end
	leaveQueue(player, g)
	HotelService.setRoom(player, g.room, "Occupied", g.id)
	g.state = "ToRoom"
	walk(g, path)
	publish(g)
	PlayerData.stat(player, "checkIns")
	local at = here(g)
	Net.fire(player, "Moment", "CheckIn", {
		species = g.species,
		mutation = g.mutation,
		size = g.size,
		byStaff = byStaff == true,
		at = at,
	})
	-- A rare check-in is the street's moment (§11 "a flashy check-in, a street-wide announcement").
	if sp.rarity == "Legendary" or sp.rarity == "Mythic" then
		local mutationName = Mutations.prefix(g.size, g.mutation)
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
	endVisit(g)
	local player = g.owner
	if not player or not g.room then
		destroy(g)
		return
	end
	local plot = PlotService.of(player)
	if not plot then
		-- The owner is leaving: the hotel is freed before their guests are (PlayerData
		-- settles first). No tip, review or stat, each tick again (2026-10-26 review).
		destroy(g)
		return
	end
	local satisfaction = math.clamp(
		Stay.satisfaction({
			prefsMatched = g.prefsMatched,
			tier = g.tier,
			-- The floor rule goes (A.13.1): activity rooms add to a stay only by visits (their +5, `satBonus`).
			amenities = 0,
			requestsPlayer = g.requestsPlayer,
			requestsStaff = g.requestsStaff,
			requestsMissed = g.requestsMissed,
			deskWait = g.waited,
		}) + g.satBonus, -- the Furniture and Decor bars (A.12)
		0,
		100
	)
	if g.happyFloor then
		satisfaction = math.max(satisfaction, g.happyFloor)
	end
	local sp = assert(Species.get(g.species))
	local stay = Constants.Rarity[sp.rarity].stay * g.stayMult
	local tip = math.floor(
		Stay.tip(g.payRate, stay, satisfaction) * (1 + GuestService.tipBonus(player, "Tips"))
	)
	PlayerData.addTill(player, tip)
	countIncome(player, tip)
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
		countIncome(player, bonus)
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
		HotelService.setRoom(
			player,
			g.room,
			if g.state == "InRoom" or g.state == "Visiting" then "Dirty" else "Vacant"
		)
		if g.state == "Queued" or g.state == "ToHotel" then
			leaveQueue(player, g)
		end
	end
	destroy(g)
end

-- ===== Visits (GDD A.13.1) =====

-- The floor and square (sx, sz) of a point on a plot (Rooms' walking grid, as `squareWorld` the other way).
local function squareOf(plot: PlotService.Plot, at: Vector3): (number, number, number)
	local p = plot.frame:PointToObjectSpace(at)
	local G = Constants.Grid
	local floor = math.max(1, math.floor((p.Y - G.SlabThickness) / G.FloorHeight + 0.5) + 1)
	return floor, math.floor(p.X / SQUARE), math.floor(p.Z / SQUARE)
end

--[[ The guests' tick's one world per hotel (GDD A.13.1, the server's cost):
	built on first ask and remembered (`Rooms.remember`: its walking grid,
	flood from the entrance and areas once), so a tick's visit decisions and
	a Hunter Night's recall of every visitor share them instead of each
	rebuilding the hotel. Nothing changes the layout during a tick. Outside a
	tick, a fresh world. ]]
local tickWorlds: { [PlayerData.Data]: Rooms.World }? = nil
local function worldFor(data: PlayerData.Data): Rooms.World
	local cache = tickWorlds
	if not cache then
		return PlotService.world(data)
	end
	local w = cache[data]
	if not w then
		w = PlotService.world(data)
		Rooms.remember(w)
		cache[data] = w
	end
	return w
end

-- The points of `Rooms.route`'s legs on a plot: each run's squares, each stair's glide; nil when a stair is missing.
local function legPoints(plot: PlotService.Plot, legs: { Grid.Leg }, out: { Vector3 }): boolean
	for _, leg in legs do
		if leg.stair then
			local glide = PlotService.stairPath(plot, (leg.stair :: Grid.Placed).id :: string)
			if #glide == 0 then
				return false
			end
			for i = 1, #glide do
				table.insert(out, if leg.up then glide[i] else glide[#glide + 1 - i])
			end
		else
			for _, c in leg.cells :: { Grid.Cell } do
				table.insert(out, squareWorld(plot, leg.floor :: number, c))
			end
		end
	end
	return true
end

-- Whether a Hunter Night is on (HunterService publishes its end on workspace): visitors are called back (A.13.1).
local function hunterNight(): boolean
	local untilAt = workspace:GetAttribute("HunterNightUntil")
	return type(untilAt) == "number" and workspace:GetServerTimeNow() < untilAt
end

--[[ A visitor turns back to its room (A.13.1): its action done, its target no
	longer ready, or a Hunter Night calling it back. Its spot is freed now (a
	visitor walking back no longer keeps the room busy), and it walks from where
	it is by `Rooms.route` to its room's key spot and onto its `Bed`; with no
	way (the hotel changed under it), straight to the `Bed`. ]]
local function visitBack(g: Guest)
	local player = g.owner
	local hotel = player and HotelService.get(player)
	local key = tostring(g.id)
	local v = hotel and hotel.visitors[key]
	if not player or not hotel or not v or not g.room then
		return
	end
	local phase = v.phase
	if Visits.free(hotel.taken, key) then
		StateService.mark(player)
	end
	v.phase = "Back"
	g.visitUntil = nil
	g.config:SetAttribute("Pose", nil)
	g.config:SetAttribute("Face", nil)
	local plot = PlotService.of(player)
	local data = PlayerData.get(player)
	local now = here(g)
	local path: { Vector3 } = { now }
	if plot and data then
		local world = worldFor(data)
		local home = Rooms.keySpot(world, g.room)
		--[[ From where it is now: at its spot, the square it stepped on from;
			on its way, the square under it (or the nearest on its side of any
			wall), never its destination's, or a guest called back mid-walk
			would cut straight through the walls. ]]
		local from: Rooms.Spot? = nil
		if phase == "There" then
			from = g.visitSquare
		else
			local floor, sx, sz = squareOf(plot, now)
			from = Rooms.standNear(world, floor, sx, sz) or g.visitSquare
		end
		local legs = if home and from then Rooms.route(world, from, home) else nil
		local ok = legs ~= nil and legPoints(plot, legs :: { Grid.Leg }, path)
		if not ok then
			path = { here(g) }
		end
		local bed = PlotService.piecePoint(plot, g.room, "Bed")
		if bed then
			table.insert(path, bed.Position)
		end
	end
	walk(g, path)
	publish(g)
end

--[[ An InRoom guest's visit decision (A.13.1), from the guests' one tick (no
	loop of its own): when its visit is due and the last decision is the gap
	ago (`Visits.mayDecide`), with no open request and no Hunter Night, it
	chooses a ready activity room meeting one of its preferences with a free
	spot (`Visits.decide`, which keeps the hotel's walkers under the cap), takes
	the spot and walks there by `Rooms.route`. Not when what is left of its
	stay is less than the walk there and back and the shortest action
	(`Visits.fits`). The spot is taken and the visitor recorded in one step
	(`Visits.begin`), once the way is found, so a spot never leaks. ]]
local function tryVisit(g: Guest, now: number)
	local player = g.owner
	if not player or not g.room or g.requestUntil or not g.visitDue then
		return
	end
	if not Visits.mayDecide(now, g.visitDue, g.visitDecided) or hunterNight() then
		return
	end
	local hotel = HotelService.get(player)
	local plot = PlotService.of(player)
	local data = PlayerData.get(player)
	local sp = Species.get(g.species)
	if not hotel or not plot or not data or not sp then
		return
	end
	local choice, decided = Visits.decide({
		now = now,
		dueAt = g.visitDue,
		lastDecision = g.visitDecided,
		prefs = sp.prefs,
		met = g.met,
		rooms = HotelService.activityRooms(player),
		taken = hotel.taken,
		visitors = hotel.visitors,
		roll = rng:NextNumber(),
	})
	if decided then
		g.visitDecided = now
	end
	if not choice then
		return
	end
	local key = tostring(g.id)
	local ref = HotelService.spotRef(player, choice.room, choice.spot)
	local point = ref and HotelService.spotPoint(player, ref)
	local rec = data.rooms[choice.room]
	if not point or not rec or hotel.visitors[key] then
		return
	end
	local world = worldFor(data)
	local from = Rooms.keySpot(world, g.room)
	-- The square in the room it steps onto the spot from (`Rooms.spotApproach`, found with the spots).
	local target = (ref :: HotelService.SpotRef).square
	local legs = if from and target then Rooms.route(world, from, target) else nil
	local path: { Vector3 } = { here(g) }
	if not legs or not legPoints(plot, legs, path) then
		return
	end
	table.insert(path, point.WorldPosition)
	-- The walk there and back (at its own pace, a Bellhop's bonus aside) and the shortest action must fit the stay.
	local walkTime = 2 * Walk.duration(path, {}, g.speed)
	if not Visits.fits(if g.stayEnd then g.stayEnd - now else nil, walkTime) then
		return
	end
	local keys = HotelService.spotKeys(player)[choice.room] or {}
	if not Visits.begin(hotel.taken, hotel.visitors, key, choice, keys) then
		return
	end
	g.visitSquare = target
	g.state = "Visiting"
	g.config:SetAttribute("Pose", ActivityKit.pose(point))
	g.config:SetAttribute("Face", point.WorldCFrame.LookVector)
	walk(g, path)
	publish(g)
	StateService.mark(player)
end

--[[ A visitor's tick (A.13.1): at its spot it does the action for its
	duration (`Visits.duration`) and is given what the visit gives (the
	preferences it meets counted met for the stay, +satisfaction once a stay,
	`Visits.gives`); then it walks back; back in its room it is InRoom again
	and its next visit is due (`Visits.nextAt`). A Hunter Night calls it back. ]]
local function visitTick(g: Guest, now: number)
	local player = g.owner
	local hotel = player and HotelService.get(player)
	local v = hotel and hotel.visitors[tostring(g.id)]
	if not player or not hotel or not v then
		-- Its visit was lost (the hotel was put away): it is in its room again.
		g.state = "InRoom"
		g.visitDue = Visits.nextAt(now, rng:NextNumber())
		publish(g)
		return
	end
	local calledBack = v.phase ~= "Back" and hunterNight()
	local done = v.phase == "There" and now >= (g.visitUntil or now)
	if calledBack or done then
		visitBack(g)
	elseif v.phase == "Going" and now >= g.arriveAt then
		v.phase = "There"
		g.visitUntil = now + Visits.duration(rng:NextNumber())
		local data = PlayerData.get(player)
		local rec = data and data.rooms[v.room]
		local sp = Species.get(g.species)
		if rec and sp then
			local hits, bonus = Visits.gives(sp.prefs, rec.type, g.visitRewarded)
			for _, h in hits do
				if not g.met[h] then
					g.met[h] = true
					g.prefsMatched += 1
				end
			end
			if bonus > 0 then
				g.satBonus += bonus
				g.visitRewarded = true
			end
		end
	elseif v.phase == "Back" and now >= g.arriveAt then
		hotel.visitors[tostring(g.id)] = nil
		g.visitSquare = nil
		g.state = "InRoom"
		g.visitDue = Visits.nextAt(now, rng:NextNumber())
		publish(g)
	end
end

-- A visitor sent back to its room (by its guest id's key): its spot freed; a visit with no guest behind it forgotten.
local function sendBack(hotel: HotelService.Hotel, key: string)
	local g = guests[tonumber(key) or 0]
	if g and g.state == "Visiting" then
		visitBack(g)
	else
		hotel.visitors[key] = nil
		Visits.free(hotel.taken, key)
	end
end

--[[ Visitors whose target stopped being ready, or whose spot is no longer
	one of its room's (its piece sold), walk back to their rooms (A.13.1,
	`Visits.stranded`). ]]
local function strandedTick()
	for player, hotel in HotelService.all() do
		if next(hotel.visitors) ~= nil then
			local ready = {}
			for _, v in hotel.visitors do
				ready[v.room] = HotelService.ready(player, v.room)
			end
			for _, key in Visits.stranded(hotel.visitors, ready, HotelService.spotKeys(player)) do
				sendBack(hotel, key)
			end
		end
	end
end

local function tickGuests()
	local now = os.clock()
	strandedTick()
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
			-- A VIP (A.11.1) waits too: its room was held for it.
			if
				g.owner
				and not g.tutorialFriend
				and not g.vip
				and now - (g.deskSince or now) > S.DeskPatience
			then
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
				-- The Size bar's longer stay (A.12).
				local stay = Constants.Rarity[sp.rarity].stay * g.stayMult
				g.stayEnd = now + stay
				g.requestAt = now + stay * (0.25 + 0.5 * rng:NextNumber())
				g.visitDue = Visits.nextAt(now, rng:NextNumber()) -- A.13.1: its first visit
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
			elseif g.state == "InRoom" then
				tryVisit(g, now)
			end
		elseif g.state == "Visiting" then
			visitTick(g, now)
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

-- The guests' tick, with one remembered world per hotel for the tick (`worldFor`), forgotten after.
local function tick()
	tickWorlds = {}
	local ok, err = pcall(tickGuests)
	for _, w in tickWorlds :: { [PlayerData.Data]: Rooms.World } do
		Rooms.forget(w)
	end
	tickWorlds = nil
	if not ok then
		error(err, 0)
	end
end

-- Pay per second into the till (§4.4), batched once a second per hotel.
local function payTick()
	local owed: { [Player]: number } = {}
	for _, g in guests do
		-- A visitor still pays: its room stays Occupied while it is out (A.13.1).
		if (g.state == "InRoom" or g.state == "Visiting") and g.owner then
			owed[g.owner] = (owed[g.owner] or 0) + g.payRate
		end
	end
	for player, amount in owed do
		countIncome(player, amount)
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
	Players.PlayerRemoving:Connect(function(player)
		income[player] = nil
	end)
	-- A guest whose room stopped being ready never stays in it (§5.4, A.12): it is sent back, the room freed.
	HotelService.onUnready(function(player, roomId)
		local sent = 0
		for _, g in guests do
			if g.owner == player and g.room == roomId then
				if g.state == "Queued" or g.state == "ToHotel" then
					leaveQueue(player, g)
				end
				sendHome(g, PlotService.of(player))
				sent += 1
			end
		end
		HotelService.setRoom(player, roomId, "Vacant")
		if sent > 0 then
			Net.fire(player, "Toast", "A guest left: its room isn't ready any more", "Info")
		end
	end)
	-- A piece moved or sold under a visitor (A.13.1): it walks back, never left on nothing.
	HotelService.onPieceChanged(function(player, decorId)
		local hotel = HotelService.get(player)
		if hotel then
			for _, key in Visits.onPiece(hotel.visitors, decorId) do
				sendBack(hotel, key)
			end
		end
	end)
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
	DevGrant.register("visitnow", function()
		-- Studio only: every guest in its room may decide on a visit now (A.13.1). Not
		-- `visit`: the showcase's command (SocialService) has that name and won.
		local now, n = os.clock(), 0
		for _, g in guests do
			if g.state == "InRoom" then
				g.visitDue = now
				g.visitDecided = nil
				n += 1
			end
		end
		return `{n} guests may visit`
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
			if g.state == "InRoom" or g.state == "Visiting" then
				g.stayEnd = now -- a visitor checks out once it is back (A.13.1)
				g.arriveAt = math.min(g.arriveAt, now)
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
