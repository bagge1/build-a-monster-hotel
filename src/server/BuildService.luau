--!strict
--[[
	Building the hotel (GDD §5, §5.4, §13.2 "Placement"). The client sends only
	an intent; this file rechecks everything: the piece exists and is unlocked
	(`Unlocks`), the place is legal (`Grid`, `Furnish` through `Layout`), the
	wallet holds the price (`Economy`), and a room being sold or moved has no
	guest in it (`HotelService`).

	FREE BUILDING (§5.4, A.1, his rulings of 2026-10-19 and 2026-10-20): the
	plot is bought one tile (cell) at a time on each floor apart (`BuyTile`),
	dearer a floor up, a tile upstairs over an owned one below; rooms, amenities, stairs and front desks are placed, moved and
	sold anywhere on owned tiles (the first desk is free, the last cannot be
	sold); decor stands on 3-stud squares in rooms and on hallway floor
	(`PlaceDecor`, `MoveDecor`, `SellDecor`) and moves and goes with its room;
	a floor finish is chosen per room and for the hallways (`Finish`); a room
	or amenity may be placed or moved mirrored (Flip, A.1: `m`, free) when its
	kit has `<PieceId>_Mirror` or it is still a blockout; a window is placed,
	moved, swapped or sold on any outer wall section (`PlaceWindow`,
	`MoveWindow`, `SellWindow`, A.1), and moves out along its line when a tile
	bought makes its wall an inside one. A new
	floor's first stair is free. A room's tier is its decor's (`Layout`), not
	bought.

	Remotes: Place, Move, Sell, BuyFloor, BuyTile, PlaceWindow, MoveWindow,
	SellWindow, PlaceDecor, MoveDecor, SellDecor, Finish, Equip. A refusal says why (`Refused`), so the client
	can show it.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Chain = require(ReplicatedStorage.Shared.Chain)
local Constants = require(ReplicatedStorage.Shared.Constants)
local Cosmetics = require(ReplicatedStorage.Shared.Cosmetics)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Furnish = require(ReplicatedStorage.Shared.Furnish)
local Grid = require(ReplicatedStorage.Shared.Grid)
local Layout = require(ReplicatedStorage.Shared.Layout)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Species = require(ReplicatedStorage.Shared.Species)
local Unlocks = require(ReplicatedStorage.Shared.Unlocks)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelKit = require(ServerScriptService.Server.HotelKit)
local HotelService = require(ServerScriptService.Server.HotelService)
local StateService = require(ServerScriptService.Server.StateService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local BuildService = {}

local changedHandlers: { (Player, string) -> () } = {}

--[[ Called after the layout changes (what changed: "Place", "Sell", "Move",
	"Floor", "Tile", "Decor", "Finish"). ]]
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

function BuildService.rooms(data: PlayerData.Data): number
	local n = 0
	for _, rec in data.layout do
		local p = Pieces.get(rec.item)
		if p and p.kind == "Room" then
			n += 1
		end
	end
	return n
end

local tutorialUnlocks: { [Player]: { [string]: boolean } } = {}
local windowsOut: (Player, PlayerData.Data) -> ()

-- The tutorial unlocks a piece early (Appendix A.7).
function BuildService.tutorialUnlock(player: Player, item: string)
	tutorialUnlocks[player] = tutorialUnlocks[player] or {}
	tutorialUnlocks[player][item] = true
end

--[[ The goal card's free tiles (§11, A.7, his go 2026-10-20; PLACEHOLDER
	block): a `TutorialTiles` block (3 × 4) beside the start square, so the
	free Coffin Suite (3×3) fits. The block on the right of the start square
	is given if a suite fits with it, else the one on the left, else the
	right; tiles owned already stay owned. Free: the next tile's price is not
	raised. ]]
function BuildService.tutorialTiles(player: Player)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local G = Constants.Grid
	local S, T = G.StartTiles, G.TutorialTiles
	local function block(x0: number): { string }
		local out = {}
		for z = S.z, S.z + T.d - 1 do
			for x = x0, x0 + T.w - 1 do
				if Grid.inBounds(x, z) then
					table.insert(out, tostring(Grid.tileKey(1, x, z)))
				end
			end
		end
		return out
	end
	local function suiteFits(keys: { string }): boolean
		local tiles = table.clone(data.tiles)
		for _, k in keys do
			tiles[k] = true
		end
		local world = Layout.world(data.floors, tiles, data.layout, data.decor)
		for z = 0, G.Cells - 1 do
			for x = 0, G.Cells - 1 do
				for r = 0, 3 do
					local p =
						Layout.piece("", { item = "CoffinSuite", floor = 1, x = x, z = z, r = r })
					if p then
						p.id = nil
						if Grid.canPlace(world, p) then
							return true
						end
					end
				end
			end
		end
		return false
	end
	local right, left = block(S.x + S.w), block(S.x - T.w)
	local chosen = if suiteFits(right) then right elseif suiteFits(left) then left else right
	for _, k in chosen do
		data.tiles[k] = true
	end
	windowsOut(player, data)
	PlotService.refreshTiles(player)
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

-- What placing `item` costs now: a stair owed for a new floor is free, a tutorial voucher too.
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
	if (data.stats[`voucher_{item}`] or 0) > 0 then
		return 0
	end
	return Economy.pieceCost(item, BuildService.owned(data, item))
end

-- The squares a room item's own furniture covers, for Layout.canPlaceDecor.
local function blockedFor(data: PlayerData.Data): (string) -> { [number]: boolean }
	return function(item: string)
		return PlotService.roomInfo(item, data.location).blocked
	end
end

--[[ Stairs change the slabs over them and the model of the stair below, and a
	desk the guests' queues (GuestService, on PlotService.onBuilt): the hotel
	is built again. ]]
local function redraw(player: Player, item: string, id: string)
	local piece = Pieces.get(item)
	if piece and (piece.kind == "Stairs" or piece.kind == "Desk") then
		PlotService.rebuild(player)
	else
		PlotService.addPiece(player, id)
	end
end

-- ===== Pieces =====

local function place(
	player: Player,
	item: string,
	floor: number,
	x: number,
	z: number,
	r: number,
	mirrored: boolean
)
	local data = PlayerData.get(player)
	local piece = Pieces.get(item)
	if not data or not piece then
		return
	end
	if mirrored and not HotelKit.mirrorable(item, data.location) then
		refuse(player, "Place", "NoMirror")
		return
	end
	local ok, why = Unlocks.buildable(item, BuildService.context(player, data))
	if not ok then
		refuse(player, "Place", why or "Locked")
		return
	end
	local candidate = Layout.piece(
		"",
		{ item = item, floor = floor, x = x, z = z, r = r, m = mirrored }
	) :: Grid.Placed
	candidate.id = nil
	local legal, reason = Grid.canPlace(PlotService.world(data), candidate)
	if not legal then
		refuse(player, "Place", reason or "Blocked")
		return
	end
	local cost = BuildService.price(data, item)
	if not PlayerData.spend(player, cost) then
		refuse(player, "Place", "Cash")
		return
	end
	if piece.kind == "Stairs" and data.freeStairs > 0 then
		data.freeStairs -= 1
	elseif cost == 0 and (data.stats[`voucher_{item}`] or 0) > 0 then
		-- A free build the tutorial gave (Appendix A.7: the goal card's Coffin Suite).
		data.stats[`voucher_{item}`] -= 1
	end
	local id = newId(data)
	data.layout[id] = {
		item = item,
		floor = floor,
		x = x,
		z = z,
		r = r,
		m = if candidate.m then true else nil,
		paid = cost,
		finish = "",
	}
	redraw(player, item, id)
	changed(player, "Place")
end

-- The decor standing in room `id`, by decor id.
local function decorIn(data: PlayerData.Data, id: string): { [string]: PlayerData.DecorRecord }
	local out = {}
	for did, d in data.decor do
		if d.room == id then
			out[did] = d
		end
	end
	return out
end

local function move(
	player: Player,
	idNumber: number,
	floor: number,
	x: number,
	z: number,
	r: number,
	mirrored: boolean
)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	local rec = data and data.layout[id]
	if not data or not rec then
		return
	end
	if HotelService.busy(player, id) then
		refuse(player, "Move", "Busy")
		return
	end
	if mirrored ~= (rec.m == true) and not HotelKit.mirrorable(rec.item, data.location) then
		refuse(player, "Move", "NoMirror")
		return
	end
	local world = PlotService.world(data)
	local skip = Layout.find(world, id)
	local candidate = Layout.piece(
		id,
		{ item = rec.item, floor = floor, x = x, z = z, r = r, m = mirrored }
	) :: Grid.Placed
	local legal, reason = Grid.canPlace(world, candidate, skip)
	if not legal then
		refuse(player, "Move", reason or "Blocked")
		return
	end
	-- Its decor goes with it, in the same place in the room (Furnish's frame),
	-- mirrored with it when it is flipped.
	local old = Layout.find(world, id) :: Grid.Placed
	local flipped = (old.m == true) ~= (candidate.m == true)
	for did, d in decorIn(data, id) do
		local item = assert(Pieces.decor(d.item))
		local l = Furnish.toRoom(old, { x = d.x, z = d.z, r = d.r, w = item.w, d = item.d })
		if flipped then
			l = Furnish.mirror(candidate, l, item.w, item.d)
		end
		local now = Furnish.fromRoom(candidate, l, item.w, item.d)
		d.floor, d.x, d.z, d.r = floor, now.x, now.z, now.r
		data.decor[did] = d
	end
	rec.floor, rec.x, rec.z, rec.r = floor, x, z, r
	rec.m = if candidate.m then true else nil
	local piece = assert(Pieces.get(rec.item))
	if piece.kind == "Stairs" or piece.kind == "Desk" then
		PlotService.rebuild(player)
	else
		PlotService.addPiece(player, id)
		for did in decorIn(data, id) do
			PlotService.drawDecor(player, did)
		end
	end
	changed(player, "Move")
end

local function sell(player: Player, idNumber: number)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	local rec = data and data.layout[id]
	if not data or not rec then
		return
	end
	if HotelService.busy(player, id) then
		refuse(player, "Sell", "Busy")
		return
	end
	local world = PlotService.world(data)
	local ok, why = Grid.canRemove(world, Layout.find(world, id) :: Grid.Placed)
	if not ok then
		refuse(player, "Sell", why or "Blocked")
		return
	end
	-- Its decor is sold with it.
	local refund = Economy.refund(rec.paid or 0)
	for did, d in decorIn(data, id) do
		refund += Economy.refund(d.paid or 0)
		data.decor[did] = nil
		PlotService.drawDecor(player, did)
	end
	data.layout[id] = nil
	local piece = Pieces.get(rec.item)
	if piece and (piece.kind == "Stairs" or piece.kind == "Desk") then
		PlotService.rebuild(player)
	else
		PlotService.removePiece(player, id)
	end
	PlayerData.refund(player, refund)
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
	local ok, why = Grid.canBuyTile(PlotService.world(data).tiles, data.floors, floor, x, z)
	if not ok then
		refuse(player, "BuyTile", why or "Blocked")
		return
	end
	if not PlayerData.spend(player, BuildService.tileCost(data, floor)) then
		refuse(player, "BuyTile", "Cash")
		return
	end
	data.tiles[tostring(Grid.tileKey(floor, x, z))] = true
	data.tilesBought[tostring(floor)] = (data.tilesBought[tostring(floor)] or 0) + 1
	windowsOut(player, data)
	PlotService.refreshTiles(player)
	changed(player, "Tile")
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
local function placeWindow(player: Player, kind: string, edge: string)
	local data = PlayerData.get(player)
	if not data then
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

local function moveWindow(player: Player, from: string, to: string)
	local data = PlayerData.get(player)
	local w = data and data.windows[from]
	if not data or not w or from == to then
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
local function sellWindow(player: Player, edge: string)
	local data = PlayerData.get(player)
	local w = data and data.windows[edge]
	if not data or not w then
		return
	end
	data.windows[edge] = nil
	PlayerData.refund(player, w.paid)
	windowsChanged(player)
end

-- ===== Decor (§5.4) =====

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
): string?
	local candidate = Layout.decor("", { item = item, floor = floor, x = x, z = z, r = r })
	if not candidate then
		return nil
	end
	candidate.id = nil
	local ok, why, room =
		Layout.canPlaceDecor(PlotService.world(data), candidate, skip, blockedFor(data))
	if not ok then
		refuse(player, remote, why or "Blocked")
		return nil
	end
	return room
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
	if not Pieces.decorHere(d, data.location, data.unlocked) then
		refuse(player, "PlaceDecor", "Location")
		return
	end
	local room = decorWhere(player, "PlaceDecor", data, item, floor, x, z, r)
	if room == nil then
		return
	end
	-- Event decor (location 0, not `always`) is owned once bought in its shop: placing it is free.
	local cost = if d.location == 0 and not d.always then 0 else d.cost
	if not PlayerData.spend(player, cost) then
		refuse(player, "PlaceDecor", "Cash")
		return
	end
	local id = newId(data)
	data.decor[id] = { item = item, floor = floor, x = x, z = z, r = r, room = room, paid = cost }
	PlotService.drawDecor(player, id)
	if room ~= "" then
		PlotService.addPiece(player, room) -- its plaque's tier
	end
	changed(player, "Decor")
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
	local room = decorWhere(player, "MoveDecor", data, rec.item, floor, x, z, r, id)
	if room == nil then
		return
	end
	local was = rec.room
	rec.floor, rec.x, rec.z, rec.r, rec.room = floor, x, z, r, room
	PlotService.drawDecor(player, id)
	for _, roomId in { was, room } do
		if roomId ~= "" and data.layout[roomId] then
			PlotService.addPiece(player, roomId)
		end
	end
	changed(player, "Decor")
end

local function sellDecor(player: Player, idNumber: number)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	local rec = data and data.decor[id]
	if not data or not rec then
		return
	end
	data.decor[id] = nil
	PlotService.drawDecor(player, id)
	if rec.room ~= "" and data.layout[rec.room] then
		PlotService.addPiece(player, rec.room)
	end
	PlayerData.refund(player, Economy.refund(rec.paid or 0))
	changed(player, "Decor")
end

-- A floor finish: `target` a room's id or "Hallway"; "" is the model's own floor.
local function finish(player: Player, target: string, finishId: string)
	local data = PlayerData.get(player)
	if not data then
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
	else
		local rec = data.layout[target]
		local piece = rec and Pieces.get(rec.item)
		if not rec or not piece or (piece.kind ~= "Room" and piece.kind ~= "Amenity") then
			return
		end
		rec.finish = finishId
		PlotService.addPiece(player, target)
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

--[[ DEV: a full hotel for the performance budget (§13.4): every tile and
	floor, a stair to each floor, every floor packed with `item` (default
	StandardRoom), each room with what decor fits of Candles, Planter and
	PuddleRug. ]]
local function fill(player: Player, args: { string }): string
	local data = PlayerData.get(player)
	if not data then
		return "no data"
	end
	local item = args[1] or "StandardRoom"
	if not Pieces.get(item) then
		return `no piece {item}`
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
	local function try(id: string, floor: number): boolean
		for z = 0, N - 1 do
			for x = 0, N - 1 do
				for r = 0, 3 do
					local p =
						Layout.piece("", { item = id, floor = floor, x = x, z = z, r = r }) :: Grid.Placed
					p.id = nil
					if Grid.canPlace(PlotService.world(data), p) then
						data.layout[newId(data)] =
							{ item = id, floor = floor, x = x, z = z, r = r, paid = 0, finish = "" }
						return true
					end
				end
			end
		end
		return false
	end
	for floor = 1, data.floors - 1 do
		try("Stairs", floor)
	end
	local n = 0
	for floor = 1, data.floors do
		while try(item, floor) do
			n += 1
		end
	end
	local Q = Constants.Grid.Squares
	for roomId, rec in data.layout do
		if rec.item == item then
			local placed = Layout.find(PlotService.world(data), roomId) :: Grid.Placed
			local ex, ez = Grid.extent(placed.w, placed.d, placed.r)
			for _, decorId in { "Candles", "Planter", "PuddleRug" } do
				local done = false
				for sz = rec.z * Q, (rec.z + ez) * Q - 1 do
					for sx = rec.x * Q, (rec.x + ex) * Q - 1 do
						if not done then
							local c = Layout.decor(
								"",
								{ item = decorId, floor = rec.floor, x = sx, z = sz, r = rec.r }
							) :: Grid.DecorPlaced
							c.id = nil
							local ok, _, room = Layout.canPlaceDecor(
								PlotService.world(data),
								c,
								nil,
								blockedFor(data)
							)
							if ok and room == roomId then
								data.decor[newId(data)] = {
									item = decorId,
									floor = rec.floor,
									x = sx,
									z = sz,
									r = rec.r,
									room = roomId,
									paid = 0,
								}
								done = true
							end
						end
					end
				end
			end
		end
	end
	player:SetAttribute("Floors", data.floors)
	PlotService.rebuild(player)
	changed(player, "Floor")
	return `{n} pieces on {data.floors} floors`
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
	BuildService.onChanged(function(player)
		announceUnlocks(player)
	end)
	HotelService.onRating(function(player)
		announceUnlocks(player)
	end)
	-- What the build mode draws: the layout, the decor, the tiles, each piece's price and whether it can be built.
	StateService.provide("build", function(player, data)
		local ctx = BuildService.context(player, data)
		local world = PlotService.world(data)
		local layout = {}
		local blocked = {}
		for id, rec in data.layout do
			local piece = Pieces.get(rec.item)
			local entry = {
				id = tonumber(id),
				item = rec.item,
				floor = rec.floor,
				x = rec.x,
				z = rec.z,
				r = rec.r,
				m = rec.m == true,
				paid = rec.paid or 0,
				finish = rec.finish or "",
			}
			if piece and piece.kind == "Room" then
				local tier, points, nextAt = Layout.roomTier(world, id)
				entry.tier, entry.points, entry.nextAt = tier, points, nextAt
				if not blocked[rec.item] then
					local keys = {}
					for k in PlotService.roomInfo(rec.item, data.location).blocked do
						table.insert(keys, k)
					end
					blocked[rec.item] = keys
				end
			end
			table.insert(layout, entry)
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
				room = rec.room,
				paid = rec.paid or 0,
			})
		end
		local buildable, costs, mirrorable = {}, {}, {}
		for _, p in Pieces.List do
			local ok, why = Unlocks.buildable(p.id, ctx)
			buildable[p.id] = if ok then true else (why or "Locked")
			costs[p.id] = BuildService.price(data, p.id)
			mirrorable[p.id] = HotelKit.mirrorable(p.id, data.location)
		end
		local unlockedDecor = {}
		for _, d in Pieces.DecorList do
			if Pieces.decorHere(d, data.location, data.unlocked) then
				unlockedDecor[d.id] = true
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
			layout = layout,
			decor = decor,
			blocked = blocked,
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
			mirrorable = mirrorable,
			location = data.location,
		}
	end)
end

return BuildService
