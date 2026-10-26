--!strict
--[[
	The long game (GDD §6.4, §6.5, his rulings 2026-10-20): rebirth and the
	Moon Tree. Opening the next location is the chain's (`ChainService`).

	REBIRTH asks for 5★ on every hotel of the chain (`Chain.rebirthReady`).
	It takes the chain apart: cash, every hotel and the locations opened go,
	and the player starts again at Haunted Manor from the start square. Its
	VIP contracts and offers end with it, without penalty (`ContractService`,
	WAITING §2.48). It keeps residents (staff of a lost hotel back in the Wing), the Book,
	cosmetics, Moon Shards, the Moon Tree, friendship and every room type
	already unlocked. It gives Moon Shards = floor(10 × √(run cash / $1M)),
	and either the right to buy one more floor (odd rebirths, to the cap) or
	a Prestige Star (`Chain.givesPrestige`), whose income bonus is paid here.

	THE MOON TREE turns shards into permanent bonuses, each read by the system
	it changes through that system's provider hook (`Income`, `ResidentService`,
	`BusService`) or a published player attribute (`OfflineBonus`,
	`CleaningBonus`, `Rerolls`).
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Chain = require(ReplicatedStorage.Shared.Chain)
local Constants = require(ReplicatedStorage.Shared.Constants)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Format = require(ReplicatedStorage.Shared.Format)
local Locations = require(ReplicatedStorage.Shared.Locations)
local MoonTree = require(ReplicatedStorage.Shared.MoonTree)
local Net = require(ReplicatedStorage.Shared.Net)
local Rating = require(ReplicatedStorage.Shared.Rating)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local HotelService = require(ServerScriptService.Server.HotelService)
local BusService = require(ServerScriptService.Server.BusService)
local ResidentService = require(ServerScriptService.Server.ResidentService)
local StateService = require(ServerScriptService.Server.StateService)
local Income = require(ServerScriptService.Server.Income)
local ChainService = require(ServerScriptService.Server.ChainService)
local DevGrant = require(ServerScriptService.Server.DevGrant)
local Safe = require(ServerScriptService.Server.Safe)

local ProgressionService = {}

local rebirthHandlers: { (Player, number) -> () } = {}
local startHandlers: { (Player) -> () } = {}

function ProgressionService.onRebirth(handler: (Player, number) -> ())
	table.insert(rebirthHandlers, handler)
end

--[[ Called at once when a rebirth is taken, before the chain is taken apart:
	what has to be let go while the hotels are still there (a VIP contract's
	held room, WAITING §2.48). It must not yield. ]]
function ProgressionService.onRebirthStart(handler: (Player) -> ())
	table.insert(startHandlers, handler)
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
	ratings: { { name: string, rating: number?, ok: boolean } },
	ready: boolean,
	shards: number,
	floor: boolean, -- this rebirth unlocks one more floor to buy
	prestige: boolean, -- this rebirth gives a Prestige Star
	floorCap: number, -- the floors a hotel may have after it (before the pass)
}

function ProgressionService.requirements(player: Player, data: PlayerData.Data): Requirements
	local ratings = ChainService.ratings(player, data)
	local list = {}
	for id = 1, Constants.Chain.Locations do
		local r = ratings[id]
		table.insert(list, {
			name = Locations.get(id).name,
			rating = r,
			ok = r ~= nil and r >= Constants.Chain.RebirthRating,
		})
	end
	local n = data.rebirths + 1
	return {
		ratings = list,
		ready = Chain.rebirthReady(ratings),
		shards = Economy.rebirthShards(data.runCash),
		floor = Chain.floorCap(n) > Chain.floorCap(n - 1),
		prestige = Chain.givesPrestige(n),
		floorCap = Chain.floorCap(n),
	}
end

local function rebirth(player: Player, force: boolean?)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local req = ProgressionService.requirements(player, data)
	if not req.ready and not force then
		Net.fire(player, "Refused", "Rebirth", "Every hotel needs 5★ first")
		return
	end
	local from = data.location
	for _, h in startHandlers do
		local ok, err = pcall(h, player)
		if not ok then
			warn(`[rebirth] {player.Name}: {err}`)
		end
	end
	--[[ The shards and the count together, before anything that can throw
		(2026-10-26 review: a throw after the shards were given skipped the
		count, the save and the handlers). Every step after them is protected
		on its own, so a rebirth that began always ends counted and saved. ]]
	PlayerData.addShards(player, req.shards)
	data.rebirths += 1
	if req.prestige then
		data.prestige += 1
	end
	data.cash = Constants.Economy.StartCash
	data.till = 0
	data.runCash = 0
	-- The chain is taken apart: Haunted Manor again, from the start square.
	data.chain = {}
	data.location = 1
	Safe.call(`[rebirth] new hotel for {player.Name}`, PlayerData.resetHotel, data)
	data.reviews = {}
	-- The new Haunted Manor rates from nothing (2026-10-26: samples are saved);
	-- the other hotels' went with `chain`.
	data.samples = Rating.newSamples()
	data.rate = 0
	Safe.call(`[rebirth] resample for {player.Name}`, ChainService.resample, player)
	-- Staff of the hotels that are gone go back to the Wing.
	for _, r in data.residents do
		if r.role ~= "" and (r.hotel or 1) ~= 1 then
			r.role = ""
			r.hotel = nil
		end
	end
	Safe.call(`[rebirth] redraw for {player.Name}`, ChainService.redraw, player)
	Net.fireAll("Announce", `{player.DisplayName} was reborn! Rebirth {data.rebirths}`, "Rare")
	Net.fire(
		player,
		"Toast",
		`+{req.shards} Moon Shards. `
			.. (if req.prestige then "+1 Prestige Star. " else "")
			.. (if req.floor then `Hotels may now have {req.floorCap} floors.` else ""),
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
	Income.addPermanent(function(player)
		local data = PlayerData.get(player)
		return if data then Chain.prestigeIncome(data.prestige) else 0
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
		return {
			location = data.location,
			locationName = Locations.get(data.location).name,
			rebirths = data.rebirths,
			prestige = data.prestige,
			shards = data.shards,
			nodes = nodes,
			req = {
				ratings = req.ratings,
				need = Constants.Chain.RebirthRating,
				ready = req.ready,
				shards = req.shards,
				floor = req.floor,
				prestige = req.prestige,
				floorCap = req.floorCap,
				cashText = `{Format.cash(data.runCash)} earned this run`,
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
