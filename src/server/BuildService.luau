--!strict
--[[
	Building the hotel (GDD §5, §13.2 "Placement"). The client sends only an
	intent, `{item, floor, cell, rotation}`; this file rechecks everything:
	the piece exists and is unlocked (`Unlocks`), the cell is legal (`Grid`),
	the wallet holds the price (`Economy`), and a room being sold or moved has
	no guest in it (`HotelService`).

	Remotes: Place, Move, Sell, Upgrade, Decorate, BuyFloor. A refusal says why
	(`Refused`), so the client can show it.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Grid = require(ReplicatedStorage.Shared.Grid)
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

-- Called after the layout changes (what changed: "Place", "Sell", "Upgrade", "Decorate", "Floor", "Move").
function BuildService.onChanged(handler: (Player, string) -> ())
	table.insert(changedHandlers, handler)
end

local function changed(player: Player, what: string)
	HotelService.sync(player)
	HotelService.recompute(player)
	for _, h in changedHandlers do
		task.spawn(h, player, what)
	end
end

local function refuse(player: Player, remote: string, reason: string)
	Net.fire(player, "Refused", remote, reason)
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
		if not data.unlocked[p.id] and Unlocks.met(p.id, ctx) then
			data.unlocked[p.id] = true
			table.insert(new, p.id)
		end
	end
	return new
end

function BuildService.maxFloors(data: PlayerData.Data): number
	return Constants.Economy.FloorCap + (if data.passes.ExtraFloor then 1 else 0)
end

local function place(player: Player, item: string, floor: number, x: number, z: number, r: number)
	local data = PlayerData.get(player)
	local piece = Pieces.get(item)
	if not data or not piece then
		return
	end
	local ok, why = Unlocks.buildable(item, BuildService.context(player, data))
	if not ok then
		refuse(player, "Place", why or "Locked")
		return
	end
	local candidate: Grid.Placed =
		{ item = item, floor = floor, x = x, z = z, r = r, w = piece.w, d = piece.d }
	local legal, reason = Grid.canPlace(PlotService.placed(data), data.floors, candidate)
	if not legal then
		refuse(player, "Place", reason or "Blocked")
		return
	end
	local cost = Economy.pieceCost(item, BuildService.owned(data, item))
	-- A free build the tutorial gave (Appendix A.7: the goal card's Coffin Suite).
	local voucher = `voucher_{item}`
	if (data.stats[voucher] or 0) > 0 then
		cost = 0
		data.stats[voucher] -= 1
	end
	if not PlayerData.spend(player, cost) then
		refuse(player, "Place", "Cash")
		return
	end
	local id = tostring(data.nextId)
	data.nextId += 1
	local decor = {}
	for i = 1, Pieces.DecorSlots do
		decor[i] = ""
	end
	data.layout[id] = { item = item, floor = floor, x = x, z = z, r = r, tier = 1, decor = decor }
	PlotService.addPiece(player, id)
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
	if HotelService.busy(player, id) then
		refuse(player, "Move", "Busy")
		return
	end
	local piece = assert(Pieces.get(rec.item))
	local placed = PlotService.placed(data)
	local skip: Grid.Placed? = nil
	for _, p in placed do
		if (p :: any).id == id then
			skip = p
		end
	end
	local candidate: Grid.Placed =
		{ item = rec.item, floor = floor, x = x, z = z, r = r, w = piece.w, d = piece.d }
	local legal, reason = Grid.canPlace(placed, data.floors, candidate, skip)
	if not legal then
		refuse(player, "Move", reason or "Blocked")
		return
	end
	rec.floor, rec.x, rec.z, rec.r = floor, x, z, r
	PlotService.addPiece(player, id)
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
	local refund =
		Economy.sellValue(rec.item, math.max(0, BuildService.owned(data, rec.item) - 1), rec.tier)
	data.layout[id] = nil
	PlotService.removePiece(player, id)
	PlayerData.refund(player, refund)
	changed(player, "Sell")
end

local function upgrade(player: Player, idNumber: number)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	local rec = data and data.layout[id]
	if not data or not rec then
		return
	end
	local cost = Economy.tierCost(rec.item, rec.tier)
	if not cost then
		refuse(player, "Upgrade", "MaxTier")
		return
	end
	if not PlayerData.spend(player, cost) then
		refuse(player, "Upgrade", "Cash")
		return
	end
	rec.tier += 1
	PlotService.addPiece(player, id)
	changed(player, "Upgrade")
end

local function decorate(player: Player, idNumber: number, slot: number, decorId: string)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	local rec = data and data.layout[id]
	if not data or not rec or slot % 1 ~= 0 or slot < 1 or slot > Pieces.DecorSlots then
		return
	end
	local piece = Pieces.get(rec.item)
	if not piece or piece.kind ~= "Room" then
		return
	end
	if decorId == "" then
		rec.decor[slot] = ""
	else
		local d = Pieces.decor(decorId)
		if not d or (d.location ~= data.location and not data.unlocked[`Decor_{decorId}`]) then
			refuse(player, "Decorate", "Location")
			return
		end
		if rec.decor[slot] == decorId then
			return
		end
		if not PlayerData.spend(player, d.cost) then
			refuse(player, "Decorate", "Cash")
			return
		end
		rec.decor[slot] = decorId
		data.unlocked[`Decor_{decorId}`] = true
	end
	PlotService.addPiece(player, id)
	changed(player, "Decorate")
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
	player:SetAttribute("Floors", next)
	PlotService.rebuild(player)
	changed(player, "Floor")
end

function BuildService.Init()
	Net.on("Place", place)
	Net.on("Move", move)
	Net.on("Sell", sell)
	Net.on("Upgrade", upgrade)
	Net.on("Decorate", decorate)
	Net.on("BuyFloor", buyFloor)
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

function BuildService.Start()
	PlayerData.onDeparted(function(player)
		tutorialUnlocks[player] = nil
	end)
	PlayerData.onLoaded(function(player)
		BuildService.refreshUnlocks(player)
	end)
	DevGrant.register("fill", function(player, args)
		-- A full hotel for the performance budget (§13.4): every floor packed
		-- with `item` (default StandardRoom), each with three decor pieces.
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		local item = args[1] or "StandardRoom"
		local piece = assert(Pieces.get(item))
		data.floors = BuildService.maxFloors(data)
		local n = 0
		for floor = 1, data.floors do
			for z = 0, Constants.Grid.Cells - 1 do
				for x = 0, Constants.Grid.Cells - 1 do
					for r = 0, 3 do
						local c: Grid.Placed = {
							item = item,
							floor = floor,
							x = x,
							z = z,
							r = r,
							w = piece.w,
							d = piece.d,
						}
						if Grid.canPlace(PlotService.placed(data), data.floors, c) then
							local id = tostring(data.nextId)
							data.nextId += 1
							data.layout[id] = {
								item = item,
								floor = floor,
								x = x,
								z = z,
								r = r,
								tier = 1,
								decor = { "Candles", "Planter", "PuddleRug" },
							}
							n += 1
							break
						end
					end
				end
			end
		end
		player:SetAttribute("Floors", data.floors)
		PlotService.rebuild(player)
		changed(player, "Floor")
		return `{n} pieces on {data.floors} floors`
	end)
	BuildService.onChanged(function(player)
		announceUnlocks(player)
	end)
	HotelService.onRating(function(player)
		announceUnlocks(player)
	end)
	-- What the build panel draws: the layout, and each piece's price and whether it can be built.
	StateService.provide("build", function(player, data)
		local ctx = BuildService.context(player, data)
		local layout = {}
		for id, rec in data.layout do
			table.insert(layout, {
				id = tonumber(id),
				item = rec.item,
				floor = rec.floor,
				x = rec.x,
				z = rec.z,
				r = rec.r,
				tier = rec.tier,
				decor = rec.decor,
			})
		end
		local buildable, costs = {}, {}
		for _, p in Pieces.List do
			local ok, why = Unlocks.buildable(p.id, ctx)
			buildable[p.id] = if ok then true else (why or "Locked")
			costs[p.id] = Economy.pieceCost(p.id, BuildService.owned(data, p.id))
		end
		local unlockedDecor = {}
		for _, d in Pieces.DecorList do
			if data.unlocked[`Decor_{d.id}`] then
				unlockedDecor[d.id] = true
			end
		end
		return {
			unlockedDecor = unlockedDecor,
			layout = layout,
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
