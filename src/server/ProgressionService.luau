--!strict
--[[
	The long game (GDD §6.4, §6.5): rebirth ("Move to a new location") and
	the Moon Tree.

	REBIRTH asks for a rating of 4★, the run's earnings ($1M at Location 1,
	×20 per location after, Appendix A.6) and a resident of the location's
	named monster (a Vampire Count at the Haunted Manor). It resets cash,
	rooms, amenities, decor and floors; it keeps residents, the Book,
	cosmetics, Moon Shards, the Moon Tree, friendship and every room type
	already unlocked; and it gives Moon Shards = floor(10 × √(run cash / $1M))
	and the next location, with its family on the bus and its rooms to build.

	THE MOON TREE turns shards into permanent bonuses, each read by the system
	it changes through that system's provider hook (`Income`, `ResidentService`,
	`BusService`) or a published player attribute (`OfflineBonus`,
	`CleaningBonus`, `Rerolls`).
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Format = require(ReplicatedStorage.Shared.Format)
local Locations = require(ReplicatedStorage.Shared.Locations)
local MoonTree = require(ReplicatedStorage.Shared.MoonTree)
local Net = require(ReplicatedStorage.Shared.Net)
local Species = require(ReplicatedStorage.Shared.Species)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local BuildService = require(ServerScriptService.Server.BuildService)
local GuestService = require(ServerScriptService.Server.GuestService)
local BusService = require(ServerScriptService.Server.BusService)
local ResidentService = require(ServerScriptService.Server.ResidentService)
local StateService = require(ServerScriptService.Server.StateService)
local Income = require(ServerScriptService.Server.Income)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local ProgressionService = {}

local rebirthHandlers: { (Player, number) -> () } = {}

function ProgressionService.onRebirth(handler: (Player, number) -> ())
	table.insert(rebirthHandlers, handler)
end

function ProgressionService.level(data: PlayerData.Data, id: string): number
	return data.moonTree[id] or 0
end

local function publishTree(player: Player, data: PlayerData.Data)
	player:SetAttribute(
		"OfflineBonus",
		MoonTree.effect("Offline", ProgressionService.level(data, "Offline"))
	)
	player:SetAttribute(
		"CleaningBonus",
		MoonTree.effect("Cleaning", ProgressionService.level(data, "Cleaning"))
	)
	player:SetAttribute(
		"Rerolls",
		MoonTree.effect("Reroll", ProgressionService.level(data, "Reroll"))
	)
end

export type Requirements = {
	rating: boolean,
	cash: boolean,
	resident: boolean,
	cashNeed: number,
	cashHave: number,
	residentId: string?,
	ready: boolean,
	shards: number,
	next: string,
}

function ProgressionService.requirements(player: Player, data: PlayerData.Data): Requirements
	local loc = Locations.get(data.location)
	local need = Economy.rebirthCash(data.location)
	local hasResident = false
	for _, r in data.residents do
		if r.species == loc.rebirthResident then
			hasResident = true
		end
	end
	local rating = HotelService.rating(player) >= Constants.Rebirth.MinRating
	local cash = data.runCash >= need
	local nextLoc = Locations.get(math.min(data.location + 1, Locations.last()))
	return {
		rating = rating,
		cash = cash,
		resident = hasResident,
		cashNeed = need,
		cashHave = data.runCash,
		residentId = loc.rebirthResident,
		ready = rating and cash and hasResident,
		shards = Economy.rebirthShards(data.runCash),
		next = nextLoc.name,
	}
end

local function rebirth(player: Player, force: boolean?)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local req = ProgressionService.requirements(player, data)
	if not req.ready and not force then
		Net.fire(player, "Refused", "Rebirth", "Not ready to move yet")
		return
	end
	-- The guests of this hotel go home; the hotel is taken down.
	for _, g in GuestService.of(player) do
		GuestService.remove(g)
	end
	local hotel = HotelService.get(player)
	if hotel then
		table.clear(hotel.queue)
	end
	PlayerData.addShards(player, req.shards)
	data.cash = Constants.Economy.StartCash
	data.till = 0
	data.runCash = 0
	data.layout = {}
	data.floors = 1
	data.reviews = {}
	data.rebirths += 1
	local from = data.location
	data.location = math.min(data.location + 1, Locations.last())
	PlayerData.publish(player)
	PlotService.rebuild(player)
	HotelService.sync(player)
	HotelService.recompute(player)
	BuildService.refreshUnlocks(player)
	ResidentService.publish(player)
	StateService.mark(player)
	Net.fireAll(
		"Announce",
		`{player.DisplayName} moved to {Locations.get(data.location).name}!`,
		"Rare"
	)
	Net.fire(
		player,
		"Toast",
		`+{req.shards} Moon Shards. Welcome to {Locations.get(data.location).name}!`,
		"Unlock"
	)
	PlayerData.stat(player, "rebirths")
	PlayerData.save(player)
	for _, h in rebirthHandlers do
		task.spawn(h, player, from)
	end
end

local function buyNode(player: Player, id: string)
	local data = PlayerData.get(player)
	if not data or not MoonTree.ById[id] then
		return
	end
	local level = ProgressionService.level(data, id)
	local cost = MoonTree.cost(id, level)
	if not cost then
		Net.fire(player, "Refused", "MoonTree", "MaxTier")
		return
	end
	if data.shards < cost then
		Net.fire(player, "Refused", "MoonTree", "Not enough Moon Shards")
		return
	end
	PlayerData.addShards(player, -cost)
	data.moonTree[id] = level + 1
	publishTree(player, data)
	ResidentService.publish(player)
	StateService.mark(player)
	Net.fire(player, "Toast", `{MoonTree.ById[id].name} grew to level {level + 1}`, "Unlock")
end

function ProgressionService.Init()
	Net.on("Rebirth", function(player)
		rebirth(player, false)
	end)
	Net.on("MoonTree", buyNode)
end

function ProgressionService.Start()
	Income.addPermanent(function(player)
		local data = PlayerData.get(player)
		return if data then MoonTree.effect("Cash", ProgressionService.level(data, "Cash")) else 0
	end)
	ResidentService.addCapacity(function(player)
		local data = PlayerData.get(player)
		return if data then MoonTree.effect("Wing", ProgressionService.level(data, "Wing")) else 0
	end)
	BusService.addScoreBonus(function(player)
		local data = PlayerData.get(player)
		return if data then MoonTree.effect("Bus", ProgressionService.level(data, "Bus")) else 0
	end)
	PlayerData.onLoaded(function(player, data)
		publishTree(player, data)
	end)
	HotelService.onRating(function(player)
		StateService.mark(player)
	end)
	StateService.provide("progression", function(player, data)
		local req = ProgressionService.requirements(player, data)
		local nodes = {}
		for _, n in MoonTree.Nodes do
			local level = ProgressionService.level(data, n.id)
			table.insert(nodes, { id = n.id, level = level, cost = MoonTree.cost(n.id, level) })
		end
		local sp = req.residentId and Species.get(req.residentId)
		return {
			location = data.location,
			locationName = Locations.get(data.location).name,
			rebirths = data.rebirths,
			shards = data.shards,
			nodes = nodes,
			req = {
				rating = req.rating,
				cash = req.cash,
				resident = req.resident,
				cashText = `{Format.cash(req.cashHave)} / {Format.cash(req.cashNeed)} earned this run`,
				residentName = sp and sp.name or "",
				ready = req.ready,
				shards = req.shards,
				next = req.next,
			},
		}
	end)
	DevGrant.register("rebirth", function(player)
		rebirth(player, true)
		local data = PlayerData.get(player)
		return `location {data and data.location}`
	end)
	DevGrant.register("runcash", function(player, args)
		local data = PlayerData.get(player)
		if data then
			data.runCash = tonumber(args[1]) or 1e6
			StateService.mark(player)
		end
		return "ok"
	end)
end

return ProgressionService
