--!strict
--[[
	Building the hotel (GDD §5, §5.4, §13.2 "Placement"). The client sends only
	an intent; this file rechecks everything: the piece or type exists and is
	unlocked (`Unlocks`), the place is legal (`Rooms`, on `Grid`), the wallet
	holds the price (`Economy`, `Constants.Rooms`), and a room a guest is in
	or due at stays ready (`HotelService`).

	FREE BUILDING (§5.4, A.1, his rulings of 2026-10-19 and 2026-10-20): the
	plot is bought one tile (cell) at a time on each floor apart (`BuyTile`),
	dearer a floor up, a tile upstairs over an owned one below; stairs and
	front desks are placed, moved and sold anywhere on owned tiles (the first
	desk is free, the last cannot be sold); a window is placed, moved, swapped
	or sold on any outer wall section (A.1) and moves out along its line when a
	tile bought makes its wall an inside one. A new floor's first stair is free.

	BUILT ROOMS (§5.4, A.12, his rulings of 2026-10-21): rooms are no longer
	pieces. The player draws inner walls on half-cell edges (`WallRun`: a
	straight run of half edges, put up or taken down, $5 each), puts a door in
	one (`Door`, $10), taps an enclosed area with a door and chooses its type
	(`MakeRoom`; `ClearRoom` makes it hallway again), and places furniture
	like decor (`PlaceDecor`, `MoveDecor`, `SellDecor`: furniture and decor
	stand on 3-stud squares anywhere in the hotel, `Rooms.canPlaceDecor`). A
	tile bought beside a room is walled off from it (`Rooms.autoWalls`, free).
	Every other change (a desk, a stair, decor, a tile) is held to
	`Rooms.check`: no room merged into another or opened onto the hallway,
	nothing guests reached cut off. A room's floor finish is chosen per room
	(`Finish`). No ready-made rooms; no Flip.

	Remotes: Place, Move, Sell, BuyFloor, BuyTile, WallRun, Door, MakeRoom,
	ClearRoom, PlaceWindow, MoveWindow, SellWindow, PlaceDecor, MoveDecor,
	SellDecor, Finish, Equip. A refusal says why (`Refused`), so the client can
	show it.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Chain = require(ReplicatedStorage.Shared.Chain)
local Constants = require(ReplicatedStorage.Shared.Constants)
local Cosmetics = require(ReplicatedStorage.Shared.Cosmetics)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Finds = require(ReplicatedStorage.Shared.Finds)
local Grid = require(ReplicatedStorage.Shared.Grid)
local Layout = require(ReplicatedStorage.Shared.Layout)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Rooms = require(ReplicatedStorage.Shared.Rooms)
local Species = require(ReplicatedStorage.Shared.Species)
local Unlocks = require(ReplicatedStorage.Shared.Unlocks)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local StateService = require(ServerScriptService.Server.StateService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local R = Constants.Rooms

local BuildService = {}

local changedHandlers: { (Player, string) -> () } = {}

--[[ Called after the layout changes (what changed: "Place", "Sell", "Move",
	"Floor", "Tile", "Decor", "Finish", "Wall", "Door", "Room"). ]]
function BuildService.onChanged(handler: (Player, string) -> ())
	table.insert(changedHandlers, handler)
end

local function changed(player: Player, what: string)
	HotelService.sync(player)
	HotelService.recompute(player)
	StateService.mark(player)
	for _, h in changedHandlers do
		task.spawn(h, player, what)
	end
end

local function refuse(player: Player, remote: string, reason: string)
	Net.fire(player, "Refused", remote, reason)
end

local function newId(data: PlayerData.Data): string
	local id = tostring(data.nextId)
	data.nextId += 1
	return id
end

function BuildService.owned(data: PlayerData.Data, item: string): number
	local n = 0
	for _, rec in data.layout do
		if rec.item == item then
			n += 1
		end
	end
	return n
end

-- Rooms built of a room type (not amenities), for Unlocks' "rooms owned" (§5.2).
function BuildService.rooms(data: PlayerData.Data): number
	local n = 0
	for _, rec in data.rooms do
		local p = Pieces.get(rec.type)
		if p and p.kind == "Room" then
			n += 1
		end
	end
	return n
end

local tutorialUnlocks: { [Player]: { [string]: boolean } } = {}
local windowsOut: (Player, PlayerData.Data) -> ()
local keepsGuests: (Player, PlayerData.Data, Rooms.World) -> boolean

-- The tutorial unlocks a room type early (Appendix A.7).
function BuildService.tutorialUnlock(player: Player, item: string)
	tutorialUnlocks[player] = tutorialUnlocks[player] or {}
	tutorialUnlocks[player][item] = true
end

--[[ The goal card's free tiles (§11, A.7, his go 2026-10-20; PLACEHOLDER
	block): a `TutorialTiles` block (3 × 4) beside the start square, so a
	Coffin Suite (3×3) can be built on it: on the right of the start square
	when it lies on the plot, else on the left; tiles owned already stay
	owned, and the start room is walled off from the new ones (as any tile
	bought, `Rooms.autoWalls`). Free: the next tile's price is not raised. ]]
function BuildService.tutorialTiles(player: Player)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local G = Constants.Grid
	local S, T = G.StartTiles, G.TutorialTiles
	local function block(x0: number): { { number } }?
		local out = {}
		for z = S.z, S.z + T.d - 1 do
			for x = x0, x0 + T.w - 1 do
				if not Grid.inBounds(x, z) then
					return nil
				end
				table.insert(out, { x, z })
			end
		end
		return out
	end
	-- The side with fewer of its cells taken by rooms already (the second room may stand there).
	local world = PlotService.world(data)
	local function taken(b: { { number } }?): number
		if not b then
			return math.huge
		end
		local n = 0
		for _, c in b do
			local HC = Rooms.HalfCells
			local a = Rooms.areaAt(world, 1, c[1] * HC, c[2] * HC)
			if a and a.room and not a.hallway then
				n += 1
			end
		end
		return n
	end
	local right, left = block(S.x + S.w), block(S.x - T.w)
	local chosen = (if taken(left) < taken(right) then left else right) or left or {}
	for _, c in chosen do
		local key = tostring(Grid.tileKey(1, c[1], c[2]))
		if not data.tiles[key] then
			-- As a tile bought (buyTile): its auto walls, and never one that breaks a room or a guest's stay.
			local now = PlotService.world(data)
			local auto = Rooms.autoWalls(now, 1, c[1], c[2])
			local after = table.clone(now)
			after.tiles = table.clone(now.tiles)
			after.tiles[Grid.tileKey(1, c[1], c[2])] = true
			after.walls = table.clone(now.walls)
			for _, e in auto do
				after.walls[e] = { paid = 0 }
			end
			if Rooms.check(now, after) and keepsGuests(player, data, after) then
				for _, e in auto do
					data.walls[e] = { paid = 0 }
				end
				data.tiles[key] = true
			end
		end
	end
	windowsOut(player, data)
	PlotService.rebuild(player)
	changed(player, "Tile")
end

function BuildService.context(player: Player, data: PlayerData.Data): Unlocks.Context
	local legendary = false
	for _, r in data.residents do
		local sp = Species.get(r.species)
		if sp and sp.rarity == "Legendary" then
			legendary = true
		end
	end
	return {
		location = data.location,
		unlocked = data.unlocked,
		rating = HotelService.rating(player),
		rooms = BuildService.rooms(data),
		floors = data.floors,
		legendaryResident = legendary,
		tutorial = tutorialUnlocks[player],
	}
end

-- Marks every piece whose condition is met now as unlocked for good (§6.4), returning the new ones.
function BuildService.refreshUnlocks(player: Player): { string }
	local data = PlayerData.get(player)
	if not data then
		return {}
	end
	local ctx = BuildService.context(player, data)
	local new = {}
	for _, p in Pieces.List do
		if p.location ~= 0 and not data.unlocked[p.id] and Unlocks.met(p.id, ctx) then
			data.unlocked[p.id] = true
			table.insert(new, p.id)
		end
	end
	return new
end

-- 2 floors, one more the right to buy per odd rebirth to a cap, +1 with the pass (§6.4).
function BuildService.maxFloors(data: PlayerData.Data): number
	return Chain.floorCap(data.rebirths) + (if data.passes.ExtraFloor then 1 else 0)
end

-- What placing `item` (a stair or a desk) costs now: a stair owed for a new floor is free.
function BuildService.price(data: PlayerData.Data, item: string): number
	local piece = Pieces.get(item)
	if not piece then
		return math.huge
	end
	if piece.kind == "Stairs" and data.freeStairs > 0 then
		return 0
	end
	if piece.kind == "Desk" then
		-- The first desk is free, every other one costs the same (§5.4, A.1, PLACEHOLDER).
		return if BuildService.owned(data, item) == 0 then 0 else Constants.Economy.DeskCost
	end
	return Economy.pieceCost(item, BuildService.owned(data, item))
end

--[[ Whether a change keeps every room a guest is in or due at as it was for
	them (§4.4): still ready, the same size. `after` is the world after it. ]]
function keepsGuests(player: Player, data: PlayerData.Data, after: Rooms.World): boolean
	local busy = {}
	for id in data.rooms do
		if HotelService.busy(player, id) then
			busy[id] = true
		end
	end
	return Rooms.keepsBusy(PlotService.world(data), after, busy)
end

-- ===== Pieces: the stairs and the desks =====

-- The world with piece `id` left out and `extra` (if any) in its place.
local function withPiece(world: Rooms.World, id: string, extra: Grid.Placed?): Rooms.World
	local after = table.clone(world)
	after.pieces = {}
	for _, p in world.pieces do
		if p.id ~= id then
			table.insert(after.pieces, p)
		end
	end
	if extra then
		table.insert(after.pieces, extra)
	end
	return after
end

local function place(player: Player, item: string, floor: number, x: number, z: number, r: number)
	local data = PlayerData.get(player)
	local piece = Pieces.get(item)
	if not data or not piece then
		return
	end
	if piece.kind == "Room" or piece.kind == "Amenity" then
		-- Rooms are built from walls now (A.12): a type is chosen for an area.
		refuse(player, "Place", "Built")
		return
	end
	local ok, why = Unlocks.buildable(item, BuildService.context(player, data))
	if not ok then
		refuse(player, "Place", why or "Locked")
		return
	end
	local candidate =
		Layout.piece("", { item = item, floor = floor, x = x, z = z, r = r }) :: Grid.Placed
	candidate.id = nil
	local world = PlotService.world(data)
	local legal, reason = Rooms.canPlacePiece(world, candidate)
	if not legal then
		refuse(player, "Place", reason or "Blocked")
		return
	end
	local placedWorld = table.clone(world)
	placedWorld.pieces = table.clone(world.pieces)
	table.insert(placedWorld.pieces, candidate)
	if not keepsGuests(player, data, placedWorld) then
		refuse(player, "Place", "Busy")
		return
	end
	local cost = BuildService.price(data, item)
	if not PlayerData.spend(player, cost) then
		refuse(player, "Place", "Cash")
		return
	end
	if piece.kind == "Stairs" and data.freeStairs > 0 then
		data.freeStairs -= 1
	end
	local id = newId(data)
	data.layout[id] = { item = item, floor = floor, x = x, z = z, r = r, paid = cost, finish = "" }
	PlotService.rebuild(player)
	changed(player, "Place")
end

local function move(
	player: Player,
	idNumber: number,
	floor: number,
	x: number,
	z: number,
	r: number
)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	local rec = data and data.layout[id]
	if not data or not rec then
		return
	end
	local world = PlotService.world(data)
	local skip = Layout.find(world, id)
	local candidate =
		Layout.piece(id, { item = rec.item, floor = floor, x = x, z = z, r = r }) :: Grid.Placed
	local legal, reason = Rooms.canPlacePiece(world, candidate, skip)
	if not legal then
		refuse(player, "Move", reason or "Blocked")
		return
	end
	if not keepsGuests(player, data, withPiece(world, id, candidate)) then
		refuse(player, "Move", "Busy")
		return
	end
	rec.floor, rec.x, rec.z, rec.r = floor, x, z, r
	PlotService.rebuild(player)
	changed(player, "Move")
end

local function sell(player: Player, idNumber: number)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	local rec = data and data.layout[id]
	if not data or not rec then
		return
	end
	local world = PlotService.world(data)
	local ok, why = Rooms.canRemovePiece(world, Layout.find(world, id) :: Grid.Placed)
	if not ok then
		refuse(player, "Sell", why or "Blocked")
		return
	end
	if not keepsGuests(player, data, withPiece(world, id, nil)) then
		refuse(player, "Sell", "Busy")
		return
	end
	data.layout[id] = nil
	PlotService.rebuild(player)
	PlayerData.refund(player, Economy.refund(rec.paid or 0))
	changed(player, "Sell")
end

local function buyFloor(player: Player)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local next = data.floors + 1
	if next > BuildService.maxFloors(data) then
		refuse(player, "BuyFloor", "FloorCap")
		return
	end
	local cost = Economy.floorCost(next)
	if not cost or not PlayerData.spend(player, cost) then
		refuse(player, "BuyFloor", "Cash")
		return
	end
	data.floors = next
	data.freeStairs += 1 -- its first stair is free to place (§5.4)
	player:SetAttribute("Floors", next)
	PlotService.rebuild(player)
	Net.fire(
		player,
		"Toast",
		`Floor {next}! Buy its tiles over the floor below, then place its stairs: the first is free.`,
		"Unlock"
	)
	changed(player, "Floor")
end

--[[ After tiles are bought: each window whose wall became an inside one
	moves out along its line (Grid.moveWindows); one with nowhere to go is
	refunded. ]]
function windowsOut(player: Player, data: PlayerData.Data)
	local moved, refunded =
		Grid.moveWindows(PlotService.world(data).tiles, data.floors, data.windows)
	data.windows = moved
	local back = 0
	for _, r in refunded do
		back += r.window.paid
	end
	if #refunded > 0 then
		PlayerData.refund(player, back)
		Net.fire(player, "Toast", `A window had nowhere to go: refunded ${back}`, "Info")
	end
end

-- What the next tile on `floor` costs (§5.4, A.1, PLACEHOLDER).
function BuildService.tileCost(data: PlayerData.Data, floor: number): number
	return Economy.tileCost(floor, data.tilesBought[tostring(floor)] or 0)
end

local function buyTile(player: Player, floor: number, x: number, z: number)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local world = PlotService.world(data)
	local ok, why = Grid.canBuyTile(world.tiles, data.floors, floor, x, z)
	if not ok then
		refuse(player, "BuyTile", why or "Blocked")
		return
	end
	-- A room beside it is walled off from it (A.12, "the facade counts as a wall").
	local auto = Rooms.autoWalls(world, floor, x, z)
	local after = table.clone(world)
	after.tiles = table.clone(world.tiles)
	after.tiles[Grid.tileKey(floor, x, z)] = true
	after.walls = table.clone(world.walls)
	for _, e in auto do
		after.walls[e] = { paid = 0 }
	end
	local fine, refusal = Rooms.check(world, after)
	if not fine then
		refuse(player, "BuyTile", refusal or "Blocked")
		return
	end
	if not keepsGuests(player, data, after) then
		refuse(player, "BuyTile", "Busy")
		return
	end
	if not PlayerData.spend(player, BuildService.tileCost(data, floor)) then
		refuse(player, "BuyTile", "Cash")
		return
	end
	data.tiles[tostring(Grid.tileKey(floor, x, z))] = true
	data.tilesBought[tostring(floor)] = (data.tilesBought[tostring(floor)] or 0) + 1
	for _, e in auto do
		data.walls[e] = { paid = 0 }
	end
	windowsOut(player, data)
	PlotService.refreshTiles(player)
	if #auto > 0 then
		PlotService.refreshRooms(player)
	end
	changed(player, "Tile")
end

-- ===== Built rooms (§5.4, A.12) =====

--[[ A straight run of `count` half edges from (hx, hz) on `floor`, along x
	(`o` 0) or z (`o` 1): walls put up (`on`, $WallCost each, a door's half
	edge left as it is) or taken down (a door with them; half the price back).
	Each half edge is checked on the hotel as the run leaves it; one refused is
	skipped and the first refusal said. ]]
local function wallRun(
	player: Player,
	floor: number,
	hx: number,
	hz: number,
	o: number,
	count: number,
	on: boolean
)
	local data = PlayerData.get(player)
	if not data or count < 1 or count > Rooms.Size or (o ~= 0 and o ~= 1) then
		return
	end
	local first: string? = nil
	local done = 0
	local refund = 0
	for i = 0, count - 1 do
		local e =
			Rooms.edgeKey(floor, hx + (if o == 0 then i else 0), hz + (if o == 1 then i else 0), o)
		local world = PlotService.world(data)
		local ok, why
		if on then
			if data.walls[e] then
				ok, why = false, nil -- already standing: nothing to do
			else
				ok, why = Rooms.canWall(world, e, false)
			end
		else
			ok, why = Rooms.canRemoveWall(world, e)
		end
		if ok then
			local after = table.clone(world)
			after.walls = table.clone(world.walls)
			after.walls[e] = if on then { paid = 0 } else nil
			if not keepsGuests(player, data, after) then
				ok, why = false, "Busy"
			end
		end
		if ok and on then
			if not PlayerData.spend(player, R.WallCost) then
				first = first or "Cash"
				break
			end
			data.walls[e] = { paid = R.WallCost }
			done += 1
		elseif ok then
			refund += Economy.refund(data.walls[e].paid or 0)
			data.walls[e] = nil
			done += 1
		elseif why then
			first = first or why
		end
	end
	if refund > 0 then
		PlayerData.refund(player, refund)
	end
	if first then
		refuse(player, "WallRun", first)
	end
	if done > 0 then
		PlotService.refreshRooms(player)
		changed(player, "Wall")
	end
end

--[[ A door put in the wall on `edge` (`on`: $DoorCost; only in a wall that
	stands, his ruling 2026-10-23) or walled up again (half its price back). ]]
local function door(player: Player, edge: string, on: boolean)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local world = PlotService.world(data)
	local f, hx, hz, o = Rooms.edgeOf(edge)
	local e = Rooms.edgeKey(f, hx, hz, o)
	local rec = data.walls[e]
	if not rec then
		-- A door goes only in a wall that stands (his ruling 2026-10-23, A.12).
		refuse(player, "Door", "DoorNeedsWall")
		return
	end
	local ok, why = Rooms.canDoor(world, e, on)
	if not ok then
		refuse(player, "Door", why or "Blocked")
		return
	end
	local after = table.clone(world)
	after.walls = table.clone(world.walls)
	after.walls[e] = { door = if on then true else nil, paid = 0 }
	if not keepsGuests(player, data, after) then
		refuse(player, "Door", "Busy")
		return
	end
	if on then
		local cost = R.DoorCost
		if not PlayerData.spend(player, cost) then
			refuse(player, "Door", "Cash")
			return
		end
		data.walls[e] = { door = true, paid = (rec.paid or 0) + cost }
	else
		local back = math.min(rec.paid or 0, R.DoorCost)
		PlayerData.refund(player, Economy.refund(back))
		data.walls[e] = { paid = (rec.paid or 0) - back }
	end
	PlotService.refreshRooms(player)
	changed(player, "Door")
end

--[[ The area holding half cell (hx, hz) of `floor` made a room of `typeId`
	(A.12: an enclosed area with a door, the type unlocked), or its type
	changed when it is a room already (not while a guest is in it or due). ]]
local function makeRoom(player: Player, floor: number, hx: number, hz: number, typeId: string)
	local data = PlayerData.get(player)
	local p = Pieces.get(typeId)
	if not data or not p or (p.kind ~= "Room" and p.kind ~= "Amenity") then
		return
	end
	if p.location ~= data.location then
		refuse(player, "MakeRoom", "Location")
		return
	end
	local can, locked = Unlocks.buildable(typeId, BuildService.context(player, data))
	if not can then
		refuse(player, "MakeRoom", locked or "Locked")
		return
	end
	local world = PlotService.world(data)
	local a = Rooms.areaAt(world, floor, hx, hz)
	local existing = a and a.room
	if existing and HotelService.busy(player, existing) then
		refuse(player, "MakeRoom", "Busy")
		return
	end
	if existing and HotelService.dirty(player, existing) then
		refuse(player, "MakeRoom", "Dirty")
		return
	end
	local ok, why = Rooms.canMakeRoom(world, floor, hx, hz, typeId, existing)
	if not ok then
		refuse(player, "MakeRoom", why or "Blocked")
		return
	end
	if existing then
		data.rooms[existing].type = typeId
		-- A retyped room starts empty for guests: its old state goes.
		local hotel = HotelService.get(player)
		if hotel then
			hotel.rooms[existing] = nil
		end
	else
		data.rooms[newId(data)] = { type = typeId, floor = floor, hx = hx, hz = hz, finish = "" }
	end
	PlotService.refreshRooms(player)
	changed(player, "Room")
end

-- A room made hallway again (its walls and furniture stay).
local function clearRoom(player: Player, idNumber: number)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	if not data or not data.rooms[id] then
		return
	end
	if HotelService.busy(player, id) then
		refuse(player, "ClearRoom", "Busy")
		return
	end
	if HotelService.dirty(player, id) then
		refuse(player, "ClearRoom", "Dirty")
		return
	end
	data.rooms[id] = nil
	PlotService.refreshRooms(player)
	changed(player, "Room")
end

-- ===== Windows (A.1, his rulings 2026-10-20) =====

-- Whether `edge` (Grid.edgeKey) is one of the hotel's outer wall sections now.
local function wallAt(data: PlayerData.Data, edge: string): boolean
	local floor, x, z, side = Grid.edgeOf(edge)
	return Grid.isWall(PlotService.world(data).tiles, data.floors, floor, x, z, side)
end

local function windowsChanged(player: Player)
	PlotService.refreshCosmetics(player)
	StateService.mark(player)
end

-- A window of `kind` on wall section `edge`: bought, or swapped for the one there (that one refunded).
local function placeWindow(player: Player, kind: string, sent: string)
	local data = PlayerData.get(player)
	local edge = Grid.canonicalEdge(sent)
	if not data or not edge then
		return
	end
	if not table.find(Constants.Windows.Types, kind) then
		refuse(player, "PlaceWindow", "Unknown")
		return
	end
	if not wallAt(data, edge) then
		refuse(player, "PlaceWindow", "NotWall")
		return
	end
	local old = data.windows[edge]
	if old and old.type == kind then
		return
	end
	local cost = Constants.Economy.WindowCost
	if not PlayerData.spend(player, cost) then
		refuse(player, "PlaceWindow", "Cash")
		return
	end
	if old then
		PlayerData.refund(player, old.paid)
	end
	data.windows[edge] = { type = kind, paid = cost }
	windowsChanged(player)
end

local function moveWindow(player: Player, sentFrom: string, sentTo: string)
	local data = PlayerData.get(player)
	local from, to = Grid.canonicalEdge(sentFrom), Grid.canonicalEdge(sentTo)
	local w = data and from and data.windows[from]
	if not data or not w or not from or not to or from == to then
		return
	end
	if not wallAt(data, to) then
		refuse(player, "MoveWindow", "NotWall")
		return
	end
	if data.windows[to] then
		refuse(player, "MoveWindow", "Overlap")
		return
	end
	data.windows[from] = nil
	data.windows[to] = w
	windowsChanged(player)
end

-- Sold: what it cost comes back whole (A.1).
local function sellWindow(player: Player, sent: string)
	local data = PlayerData.get(player)
	local edge = Grid.canonicalEdge(sent)
	local w = data and edge and data.windows[edge]
	if not data or not edge or not w then
		return
	end
	data.windows[edge] = nil
	PlayerData.refund(player, w.paid)
	windowsChanged(player)
end

-- ===== Decor and furniture (§5.4, A.12) =====

-- The world with decor record `id` (if any) left out and `extra` added.
local function withDecor(world: Rooms.World, id: string?, extra: Grid.DecorPlaced?): Rooms.World
	local after = table.clone(world)
	after.decor = {}
	for _, d in world.decor do
		if not (id and d.id == id) then
			table.insert(after.decor, d)
		end
	end
	if extra then
		table.insert(after.decor, extra)
	end
	return after
end

local function decorWhere(
	player: Player,
	remote: string,
	data: PlayerData.Data,
	item: string,
	floor: number,
	x: number,
	z: number,
	r: number,
	skip: string?
): boolean
	local candidate = Layout.decor("", { item = item, floor = floor, x = x, z = z, r = r })
	if not candidate then
		return false
	end
	candidate.id = skip
	local world = PlotService.world(data)
	local ok, why = Rooms.canPlaceDecor(world, candidate, skip)
	if not ok then
		refuse(player, remote, why or "Blocked")
		return false
	end
	if not keepsGuests(player, data, withDecor(world, skip, candidate)) then
		refuse(player, remote, "Busy")
		return false
	end
	return true
end

-- The tutorial's free key piece (A.7: the goal card's first Coffin Suite): a voucher for a type it is a key of.
local function voucherFor(data: PlayerData.Data, d: Pieces.Decor): string?
	for _, t in d.keyFor or {} do
		if (data.stats[`voucher_{t}`] or 0) > 0 then
			return `voucher_{t}`
		end
	end
	return nil
end

--[[ The copies of event decor `d` the player may still place (`Pieces.copiesLeft`, WAITING
	§2.48): its purchases less the copies standing in every hotel of the chain, the one
	played and the others. Nil for other decor. ]]
local function copiesLeft(data: PlayerData.Data, d: Pieces.Decor): number?
	local placed = 0
	local function count(decor: { [string]: PlayerData.DecorRecord })
		for _, rec in decor do
			if rec.item == d.id then
				placed += 1
			end
		end
	end
	count(data.decor)
	for _, hotel in data.chain do
		count(hotel.decor or {})
	end
	return Pieces.copiesLeft(
		d,
		data.stats[Pieces.copiesKey(d.id)],
		data.unlocked[`Decor_{d.id}`] == true,
		placed
	)
end

local function decorChanged(player: Player, id: string)
	PlotService.drawDecor(player, id)
	PlotService.refreshRooms(player)
	changed(player, "Decor")
end

local function placeDecor(
	player: Player,
	item: string,
	floor: number,
	x: number,
	z: number,
	r: number
)
	local data = PlayerData.get(player)
	local d = Pieces.decor(item)
	if not data or not d then
		return
	end
	if d.found and not (data.finds and data.finds.found[d.id]) then
		-- Rare decor (A.11.3): found, never bought.
		refuse(player, "PlaceDecor", "NotFound")
		return
	end
	if
		not Pieces.decorHere(
			d,
			data.location,
			data.unlocked,
			data.finds and data.finds.found,
			data.passes
		)
	then
		refuse(player, "PlaceDecor", "Location")
		return
	end
	-- Event decor is one copy per purchase in its shop (WAITING §2.48): another needs another purchase.
	local left = copiesLeft(data, d)
	if left and left <= 0 then
		refuse(
			player,
			"PlaceDecor",
			"Each copy is one purchase in the event shop: yours are all placed"
		)
		return
	end
	if not decorWhere(player, "PlaceDecor", data, item, floor, x, z, r) then
		return
	end
	-- Event decor is paid for in its shop, a copy a purchase: placing a copy bought is free.
	-- A pass's decor is bought with cash (A.2): its cost is its decor points.
	local cost = if Pieces.isEventDecor(d) then 0 else d.cost
	local voucher = voucherFor(data, d)
	if voucher then
		cost = 0
	end
	if not PlayerData.spend(player, cost) then
		refuse(player, "PlaceDecor", "Cash")
		return
	end
	if voucher then
		data.stats[voucher] -= 1
	end
	local id = newId(data)
	data.decor[id] = { item = item, floor = floor, x = x, z = z, r = r, room = "", paid = cost }
	decorChanged(player, id)
end

local function moveDecor(
	player: Player,
	idNumber: number,
	floor: number,
	x: number,
	z: number,
	r: number
)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	local rec = data and data.decor[id]
	if not data or not rec then
		return
	end
	if not decorWhere(player, "MoveDecor", data, rec.item, floor, x, z, r, id) then
		return
	end
	rec.floor, rec.x, rec.z, rec.r, rec.room = floor, x, z, r, ""
	decorChanged(player, id)
end

local function sellDecor(player: Player, idNumber: number)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	local rec = data and data.decor[id]
	if not data or not rec then
		return
	end
	if not keepsGuests(player, data, withDecor(PlotService.world(data), id, nil)) then
		refuse(player, "SellDecor", "Busy")
		return
	end
	data.decor[id] = nil
	PlayerData.refund(player, Economy.refund(rec.paid or 0))
	decorChanged(player, id)
end

-- A floor finish: `target` a built room's id or "Hallway"; "" is the slab's own.
local function finish(player: Player, target: string, finishId: string)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	-- The room first, so a finish is never paid for a room that is not there.
	local rec = if target == "Hallway" then nil else data.rooms[target]
	if target ~= "Hallway" and not rec then
		return
	end
	-- The finish it has already: nothing to lay, nothing to pay (Pieces.finishChanges).
	local current = if rec then rec.finish else data.finishes[target]
	if not Pieces.finishChanges(current, finishId) then
		return
	end
	if finishId ~= "" then
		local f = Pieces.finish(finishId)
		if not f or f.location ~= data.location then
			refuse(player, "Finish", "Location")
			return
		end
		if not PlayerData.spend(player, f.cost) then
			refuse(player, "Finish", "Cash")
			return
		end
	end
	if target == "Hallway" then
		data.finishes[target] = finishId
		PlotService.rebuild(player)
	elseif rec then
		rec.finish = finishId
		PlotService.refreshRooms(player)
	end
	changed(player, "Finish")
end

-- Wears an owned cosmetic in its slot, or takes the slot's off ("") (Cosmetics.luau).
local function equip(player: Player, slot: string, id: string)
	local data = PlayerData.get(player)
	if not data or not table.find(Cosmetics.Slots, slot :: any) then
		return
	end
	if id ~= "" then
		local c = Cosmetics.get(id)
		if not c or c.slot ~= slot or not Cosmetics.owns(data, id) then
			Net.fire(player, "Refused", "Equip", "You don't have that yet")
			return
		end
	end
	data.equipped[slot] = id
	PlotService.refreshCosmetics(player)
	StateService.mark(player)
end

function BuildService.Init()
	Net.on("Equip", equip)
	Net.on("Place", place)
	Net.on("Move", move)
	Net.on("Sell", sell)
	Net.on("BuyFloor", buyFloor)
	Net.on("BuyTile", buyTile)
	Net.on("WallRun", wallRun)
	Net.on("Door", door)
	Net.on("MakeRoom", makeRoom)
	Net.on("ClearRoom", clearRoom)
	Net.on("PlaceWindow", placeWindow)
	Net.on("MoveWindow", moveWindow)
	Net.on("SellWindow", sellWindow)
	Net.on("PlaceDecor", placeDecor)
	Net.on("MoveDecor", moveDecor)
	Net.on("SellDecor", sellDecor)
	Net.on("Finish", finish)
end

local function announceUnlocks(player: Player)
	for _, id in BuildService.refreshUnlocks(player) do
		local piece = Pieces.get(id)
		if piece then
			Net.fire(player, "Toast", `Unlocked: {piece.name}!`, "Unlock")
		end
	end
	StateService.mark(player)
end

--[[ DEV: a room of `typeId` built free in the w × d cells at (x, z) on
	`floor`: walls round it (those standing kept), a door in its front's first
	half edge (or the first that takes one), and one of its key furniture.
	Returns the room's id or why not. ]]
local function buildBox(
	data: PlayerData.Data,
	typeId: string,
	floor: number,
	x: number,
	z: number,
	w: number,
	d: number
): (string?, string?)
	local function wall(e: string, withDoor: boolean): boolean
		local world = PlotService.world(data)
		if data.walls[e] then
			if withDoor and not data.walls[e].door and Rooms.canDoor(world, e, true) then
				data.walls[e] = { door = true, paid = 0 }
			end
			return true
		end
		if Rooms.canWall(world, e, withDoor) then
			data.walls[e] = { door = if withDoor then true else nil, paid = 0 }
			return true
		end
		return false
	end
	local edges: { string } = {}
	for cx = x, x + w - 1 do
		for _, e in Rooms.cellEdges(floor, cx, z, 0) do
			table.insert(edges, e)
		end
	end
	local front = #edges
	for cx = x, x + w - 1 do
		for _, e in Rooms.cellEdges(floor, cx, z + d - 1, 2) do
			table.insert(edges, e)
		end
	end
	for cz = z, z + d - 1 do
		for _, e in Rooms.cellEdges(floor, x, cz, 1) do
			table.insert(edges, e)
		end
		for _, e in Rooms.cellEdges(floor, x + w - 1, cz, 3) do
			table.insert(edges, e)
		end
	end
	-- The door first, on the front, before the box closes.
	local doored = false
	for i = 1, front do
		if not doored and wall(edges[i], true) and data.walls[edges[i]].door then
			doored = true
		end
	end
	if not doored then
		return nil, "NoDoor"
	end
	for _, e in edges do
		-- A half edge on the facade or refused stays open: the box is then not closed.
		wall(e, false)
	end
	local HC = Rooms.HalfCells
	local world = PlotService.world(data)
	local ok, why = Rooms.canMakeRoom(world, floor, x * HC, z * HC, typeId)
	if not ok then
		return nil, why
	end
	local id = newId(data)
	data.rooms[id] = { type = typeId, floor = floor, hx = x * HC, hz = z * HC, finish = "" }
	local req = Rooms.requirement(typeId)
	local key = req and req.keys[1]
	local item = key and Pieces.decor(key)
	local area = Rooms.roomArea(PlotService.world(data), id)
	if item and area then
		local cells = {}
		for _, k in area.cells do
			cells[k] = true
		end
		local Q = Constants.Grid.Squares
		local SQ = Q // HC
		-- From the back of the box forward, so the door's side stays clear.
		for sz = (z + d) * Q - 1, z * Q, -1 do
			for sx = x * Q, (x + w) * Q - 1 do
				for r = 0, 3 do
					local c =
						Layout.decor("", { item = item.id, floor = floor, x = sx, z = sz, r = r })
					if c then
						c.id = nil
						local inside = true
						for _, s in Grid.squares(c) do
							if not cells[Rooms.halfKey(s.x // SQ, s.z // SQ)] then
								inside = false
							end
						end
						if inside and Rooms.canPlaceDecor(PlotService.world(data), c) then
							data.decor[newId(data)] = {
								item = item.id,
								floor = floor,
								x = sx,
								z = sz,
								r = r,
								room = "",
								paid = 0,
							}
							return id, nil
						end
					end
				end
			end
		end
	end
	return id, "NoKeyFurniture"
end

--[[ DEV: a full hotel for the performance budget (§13.4): every tile and
	floor, a stair to each floor, and every floor packed with 2 × 2 rooms of
	`item` (default StandardRoom) in rows off hallways, each with its key
	furniture. ]]
local function fill(player: Player, args: { string }): string
	local data = PlayerData.get(player)
	if not data then
		return "no data"
	end
	local item = args[1] or "StandardRoom"
	if not Rooms.requirement(item) then
		return `no room type {item}`
	end
	local N = Constants.Grid.Cells
	data.floors = BuildService.maxFloors(data)
	for f = 1, data.floors do
		for z = 0, N - 1 do
			for x = 0, N - 1 do
				data.tiles[tostring(Grid.tileKey(f, x, z))] = true
			end
		end
	end
	-- It yields a frame per row: a whole hotel at once ran past Roblox's script
	-- timeout (2026-10-24 evening, and took a ProfileStore thread with it).
	for floor = 1, data.floors - 1 do
		local done = false
		for z = N - 2, 0, -1 do
			task.wait()
			for x = 0, N - 2 do
				if not done then
					local p = Layout.piece(
						"",
						{ item = "Stairs", floor = floor, x = x, z = z, r = 0 }
					) :: Grid.Placed
					p.id = nil
					if Rooms.canPlacePiece(PlotService.world(data), p) then
						data.layout[newId(data)] = {
							item = "Stairs",
							floor = floor,
							x = x,
							z = z,
							r = 0,
							paid = 0,
							finish = "",
						}
						done = true
					end
				end
			end
		end
	end
	local n = 0
	for floor = 1, data.floors do
		for _, z in { 2, 5, 8 } do
			for x = 0, N - 2, 2 do
				task.wait()
				if buildBox(data, item, floor, x, z, 2, 2) then
					n += 1
				end
			end
		end
	end
	player:SetAttribute("Floors", data.floors)
	PlotService.rebuild(player)
	changed(player, "Floor")
	return `{n} rooms on {data.floors} floors`
end

function BuildService.Start()
	PlayerData.onDeparted(function(player)
		tutorialUnlocks[player] = nil
	end)
	PlayerData.onLoaded(function(player)
		BuildService.refreshUnlocks(player)
	end)
	DevGrant.register("cosmetic", function(player, args)
		-- Owns a cosmetic (`args[1]`, or every one), to see it worn without earning it.
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		for _, c in Cosmetics.List do
			if args[1] == nil or args[1] == c.id then
				data.cosmetics[c.id] = true
			end
		end
		StateService.mark(player)
		return "ok"
	end)
	DevGrant.register("unlock", function(player, args)
		local data = PlayerData.get(player)
		if data and args[1] then
			data.unlocked[args[1]] = true
			StateService.mark(player)
		end
		return "ok"
	end)
	DevGrant.register("fill", fill)
	DevGrant.register("room", function(player, args)
		-- `room <x> <z> <w> <d> [type] [floor]`: a built room, free (tiles bought for it first).
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		local x, z = tonumber(args[1]) or 0, tonumber(args[2]) or 0
		local w, d = tonumber(args[3]) or 2, tonumber(args[4]) or 2
		local floor = tonumber(args[6]) or 1
		for cz = z, z + d - 1 do
			for cx = x, x + w - 1 do
				data.tiles[tostring(Grid.tileKey(floor, cx, cz))] = true
			end
		end
		local id, why = buildBox(data, args[5] or "StandardRoom", floor, x, z, w, d)
		PlotService.rebuild(player)
		changed(player, "Room")
		return `room {id} {why or "ready"}`
	end)
	BuildService.onChanged(function(player)
		announceUnlocks(player)
	end)
	HotelService.onRating(function(player)
		announceUnlocks(player)
	end)
	-- What the build mode draws: the layout, the walls and rooms, the decor, the tiles, the prices and what can be built.
	StateService.provide("build", function(player, data)
		local ctx = BuildService.context(player, data)
		local world = PlotService.world(data)
		local layout = {}
		for id, rec in data.layout do
			table.insert(layout, {
				id = tonumber(id),
				item = rec.item,
				floor = rec.floor,
				x = rec.x,
				z = rec.z,
				r = rec.r,
				paid = rec.paid or 0,
			})
		end
		local decor = {}
		for id, rec in data.decor do
			table.insert(decor, {
				id = tonumber(id),
				item = rec.item,
				floor = rec.floor,
				x = rec.x,
				z = rec.z,
				r = rec.r,
				room = "",
				paid = rec.paid or 0,
			})
		end
		local walls = {}
		for edge, rec in data.walls do
			table.insert(walls, { edge = edge, door = rec.door == true, paid = rec.paid or 0 })
		end
		-- Each built room with what the room view shows (A.12): ready or what it lacks, its bars and bonuses.
		local rooms = {}
		local all = HotelService.readiness(player) or Rooms.readiness(world)
		for id, rec in data.rooms do
			local r = all[id] or { ok = false, missing = nil }
			local ok, missing = r.ok, r.missing
			local info = assert(HotelService.roomInfo(data, id))
			local bars = info.bars
			-- A.11.3: the rare sets standing in it (pieces of each), and whether it has the set's bonus.
			local sets = {}
			for setId, n in Finds.progress(info.decor) do
				table.insert(sets, {
					id = setId,
					have = n,
					total = #Pieces.SetById[setId].pieces,
					bonus = bars.sets ~= nil and table.find(bars.sets, setId) ~= nil,
				})
			end
			table.insert(rooms, {
				sets = sets,
				id = tonumber(id),
				type = rec.type,
				floor = rec.floor,
				hx = rec.hx,
				hz = rec.hz,
				finish = rec.finish or "",
				ready = ok,
				missing = missing or {},
				missingText = if ok then "" else HotelService.missingText(rec.type, missing or {}),
				size = info.size,
				bars = bars,
				bonuses = Rooms.bonuses(bars),
				state = (function()
					local hotel = HotelService.get(player)
					local room = hotel and hotel.rooms[id]
					return if room then room.state else ""
				end)(),
			})
		end
		local buildable, costs = {}, {}
		for _, p in Pieces.List do
			local ok, why = Unlocks.buildable(p.id, ctx)
			buildable[p.id] = if ok then true else (why or "Locked")
			if p.kind == "Stairs" or p.kind == "Desk" then
				costs[p.id] = BuildService.price(data, p.id)
			end
		end
		local unlockedDecor = {}
		for _, d in Pieces.DecorList do
			if
				Pieces.decorHere(
					d,
					data.location,
					data.unlocked,
					data.finds and data.finds.found,
					data.passes
				)
			then
				unlockedDecor[d.id] = true
			end
		end
		-- Event decor's copies left to place (WAITING §2.48): the Decor tab's card says how many.
		local copies = {}
		for _, d in Pieces.DecorList do
			local left = unlockedDecor[d.id] and copiesLeft(data, d)
			if left then
				copies[d.id] = left
			end
		end
		local vouchers = {}
		for k, v in data.stats do
			if string.sub(k, 1, 8) == "voucher_" and v > 0 then
				vouchers[string.sub(k, 9)] = v
			end
		end
		local tiles = {}
		for k, v in data.tiles do
			if v then
				table.insert(tiles, tonumber(k))
			end
		end
		local tileCosts = {}
		for f = 1, data.floors do
			tileCosts[f] = BuildService.tileCost(data, f)
		end
		local windows = {}
		for edge, w in data.windows do
			table.insert(windows, { edge = edge, type = w.type, paid = w.paid })
		end
		local cosmetics = {}
		for _, c in Cosmetics.List do
			table.insert(cosmetics, {
				id = c.id,
				name = c.name,
				slot = c.slot,
				from = c.from,
				owned = Cosmetics.owns(data, c.id),
			})
		end
		return {
			cosmetics = cosmetics,
			equipped = data.equipped,
			traps = data.traps,
			unlockedDecor = unlockedDecor,
			copies = copies,
			vouchers = vouchers,
			layout = layout,
			decor = decor,
			walls = walls,
			rooms = rooms,
			types = Rooms.typesFor(ctx),
			wallCost = R.WallCost,
			doorCost = R.DoorCost,
			tiles = tiles,
			tileCosts = tileCosts,
			windows = windows,
			windowCost = Constants.Economy.WindowCost,
			finishes = data.finishes,
			freeStairs = data.freeStairs,
			floors = data.floors,
			maxFloors = BuildService.maxFloors(data),
			floorCost = Economy.floorCost(data.floors + 1),
			buildable = buildable,
			costs = costs,
			location = data.location,
		}
	end)
end

return BuildService
