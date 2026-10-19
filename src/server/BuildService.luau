--!strict
--[[
	Building the hotel (GDD §5, §5.4, §13.2 "Placement"). The client sends only
	an intent; this file rechecks everything: the piece exists and is unlocked
	(`Unlocks`), the place is legal (`Grid`, `Furnish` through `Layout`), the
	wallet holds the price (`Economy`), and a room being sold or moved has no
	guest in it (`HotelService`).

	FREE BUILDING (§5.4, his rulings and his yes of 2026-10-19): the plot is
	bought in areas (`BuyArea`); rooms, amenities and stairs are placed, moved
	and sold; the one front desk is moved, never bought or sold; decor stands
	on 3-stud squares in rooms and on hallway floor (`PlaceDecor`,
	`MoveDecor`, `SellDecor`) and moves and goes with its room; a floor finish
	is chosen per room, for the lobby and for the hallways (`Finish`). A new
	floor's first stair is free. A room's tier is its decor's (`Layout`), not
	bought.

	Remotes: Place, Move, Sell, BuyFloor, BuyArea, PlaceDecor, MoveDecor,
	SellDecor, Finish, Equip. A refusal says why (`Refused`), so the client
	can show it.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

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
local HotelService = require(ServerScriptService.Server.HotelService)
local StateService = require(ServerScriptService.Server.StateService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local BuildService = {}

local changedHandlers: { (Player, string) -> () } = {}

--[[ Called after the layout changes (what changed: "Place", "Sell", "Move",
	"Floor", "Area", "Decor", "Finish"). ]]
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

function BuildService.areasOwned(data: PlayerData.Data): number
	local n = 0
	for _, v in data.areas do
		if v then
			n += 1
		end
	end
	return n
end

local tutorialUnlocks: { [Player]: { [string]: boolean } } = {}

-- The tutorial unlocks a piece early (Appendix A.7).
function BuildService.tutorialUnlock(player: Player, item: string)
	tutorialUnlocks[player] = tutorialUnlocks[player] or {}
	tutorialUnlocks[player][item] = true
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

function BuildService.maxFloors(data: PlayerData.Data): number
	return Constants.Economy.FloorCap + (if data.passes.ExtraFloor then 1 else 0)
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

-- Stairs change the slabs over them and the model of the stair below: the hotel is built again.
local function redraw(player: Player, item: string, id: string)
	local piece = Pieces.get(item)
	if piece and piece.kind == "Stairs" then
		PlotService.rebuild(player)
	else
		PlotService.addPiece(player, id)
	end
end

-- ===== Pieces =====

local function place(player: Player, item: string, floor: number, x: number, z: number, r: number)
	local data = PlayerData.get(player)
	local piece = Pieces.get(item)
	if not data or not piece then
		return
	end
	if piece.kind == "Desk" then
		refuse(player, "Place", "OneDesk")
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
	data.layout[id] = { item = item, floor = floor, x = x, z = z, r = r, paid = cost, finish = "" }
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
	r: number
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
	local world = PlotService.world(data)
	local skip = Layout.find(world, id)
	local candidate =
		Layout.piece(id, { item = rec.item, floor = floor, x = x, z = z, r = r }) :: Grid.Placed
	local legal, reason = Grid.canPlace(world, candidate, skip)
	if not legal then
		refuse(player, "Move", reason or "Blocked")
		return
	end
	-- Its decor goes with it, in the same place in the room (Furnish's frame).
	local old = Layout.find(world, id) :: Grid.Placed
	for did, d in decorIn(data, id) do
		local item = assert(Pieces.decor(d.item))
		local l = Furnish.toRoom(old, { x = d.x, z = d.z, r = d.r, w = item.w, d = item.d })
		local now = Furnish.fromRoom(candidate, l, item.w, item.d)
		d.floor, d.x, d.z, d.r = floor, now.x, now.z, now.r
		data.decor[did] = d
	end
	rec.floor, rec.x, rec.z, rec.r = floor, x, z, r
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
	if rec.item == "Stairs" then
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
	Net.fire(player, "Toast", `Floor {next}! Place its stairs: the first is free.`, "Unlock")
	changed(player, "Floor")
end

local function buyArea(player: Player, index: number)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local owned = {}
	for k, v in data.areas do
		owned[tonumber(k) :: number] = v
	end
	local ok, why = Grid.canBuyArea(owned, index)
	if not ok then
		refuse(player, "BuyArea", why or "Blocked")
		return
	end
	local cost = Economy.areaCost(BuildService.areasOwned(data))
	if not cost or not PlayerData.spend(player, cost) then
		refuse(player, "BuyArea", "Cash")
		return
	end
	data.areas[tostring(index)] = true
	PlotService.rebuild(player)
	changed(player, "Area")
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

-- A floor finish: `target` a room's id, "Lobby" or "Hallway"; "" is the model's own floor.
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
	if target == "Lobby" or target == "Hallway" then
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
	Net.on("BuyArea", buyArea)
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

--[[ DEV: a full hotel for the performance budget (§13.4): every area and
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
	for i = 1, Grid.areaCount() do
		data.areas[tostring(i)] = true
	end
	data.floors = BuildService.maxFloors(data)
	local N = Constants.Grid.Cells
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
	-- What the build mode draws: the layout, the decor, the areas, each piece's price and whether it can be built.
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
		local buildable, costs = {}, {}
		for _, p in Pieces.List do
			local ok, why = Unlocks.buildable(p.id, ctx)
			buildable[p.id] = if ok then true else (why or "Locked")
			costs[p.id] = BuildService.price(data, p.id)
		end
		local unlockedDecor = {}
		for _, d in Pieces.DecorList do
			if Pieces.decorHere(d, data.location, data.unlocked) then
				unlockedDecor[d.id] = true
			end
		end
		local areas = {}
		for k, v in data.areas do
			if v then
				table.insert(areas, tonumber(k))
			end
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
			areas = areas,
			areaCost = Economy.areaCost(BuildService.areasOwned(data)),
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
