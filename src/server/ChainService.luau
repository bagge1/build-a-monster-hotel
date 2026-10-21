--!strict
--[[
	The hotel chain (GDD §6.4, his rulings 2026-10-20). A player owns one
	hotel per location opened and plays one at a time: its fields stay where
	every system already reads them (`data.layout`, `data.tiles` …), and the
	chain's other hotels wait in `data.chain`, by location id, as
	`PlayerData.HotelRecord`s.

	TRAVEL swaps them: the played hotel is put away with its rating and its
	measured earning rate, the chosen one is taken out, and the plot, the
	rooms and the build state are drawn again. Opening the next location is
	the same, with a new hotel from the start square, for its price
	(`Chain.openCost`, PLACEHOLDER).

	BACKGROUND EARNINGS: a hotel not played earns `Chain.background` of the
	rate it earned while played: a moving average of what its guests paid
	(pay, tips, request tips: `GuestService.income`), so a lump of cash (a
	daily reward, a cash pack, the till collected) never inflates it. Online
	only; the residents' offline till is unchanged (§4.6).
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Chain = require(ReplicatedStorage.Shared.Chain)
local Constants = require(ReplicatedStorage.Shared.Constants)
local Format = require(ReplicatedStorage.Shared.Format)
local Locations = require(ReplicatedStorage.Shared.Locations)
local Net = require(ReplicatedStorage.Shared.Net)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local BuildService = require(ServerScriptService.Server.BuildService)
local GuestService = require(ServerScriptService.Server.GuestService)
local ResidentService = require(ServerScriptService.Server.ResidentService)
local StateService = require(ServerScriptService.Server.StateService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local ChainService = {}

local TICK = 30 -- seconds between background payments and rate samples

-- Per player: when the played hotel was last measured and its guests' income then.
local samples: { [Player]: { at: number, income: number } } = {}
local travelHandlers: { (Player, number) -> () } = {}

-- Called after a player travels or opens a hotel, with the location left.
function ChainService.onTravel(handler: (Player, number) -> ())
	table.insert(travelHandlers, handler)
end

-- The locations opened: the one played and the chain's others.
function ChainService.opened(data: PlayerData.Data): { [number]: boolean }
	local out = { [data.location] = true }
	for key in data.chain do
		local id = tonumber(key)
		if id then
			out[id] = true
		end
	end
	return out
end

-- Each opened hotel's rating, by location: the played one live, the others as left.
function ChainService.ratings(player: Player, data: PlayerData.Data): { [number]: number }
	local out = { [data.location] = HotelService.rating(player) }
	for key, rec in data.chain do
		local id = tonumber(key)
		if id then
			out[id] = rec.rating
		end
	end
	return out
end

local function putAway(player: Player, data: PlayerData.Data)
	data.chain[tostring(data.location)] = {
		layout = data.layout,
		decor = data.decor,
		walls = data.walls,
		rooms = data.rooms,
		tiles = data.tiles,
		tilesBought = data.tilesBought,
		windows = data.windows,
		finishes = data.finishes,
		floors = data.floors,
		freeStairs = data.freeStairs,
		reviews = data.reviews,
		rating = HotelService.rating(player),
		rate = data.rate,
	}
end

local function takeOut(data: PlayerData.Data, location: number)
	local key = tostring(location)
	local rec = data.chain[key]
	data.chain[key] = nil
	data.location = location
	if rec then
		data.layout = rec.layout
		data.decor = rec.decor
		data.walls = rec.walls or {}
		data.rooms = rec.rooms or {}
		data.tiles = rec.tiles
		data.tilesBought = rec.tilesBought
		data.windows = rec.windows
		data.finishes = rec.finishes
		data.floors = rec.floors
		data.freeStairs = rec.freeStairs
		data.reviews = rec.reviews or {}
		data.rate = rec.rate
	else
		PlayerData.resetHotel(data) -- a new hotel: the start square and the desk (§5.4)
		data.reviews = {}
		data.rate = 0
	end
end

-- Draws the played hotel again after a swap: guests of the old one go home.
function ChainService.redraw(player: Player)
	for _, g in GuestService.of(player) do
		GuestService.remove(g)
	end
	local hotel = HotelService.get(player)
	if hotel then
		table.clear(hotel.queue)
	end
	PlayerData.publish(player)
	PlotService.rebuild(player)
	HotelService.sync(player)
	HotelService.recompute(player)
	BuildService.refreshUnlocks(player)
	ResidentService.publish(player)
	StateService.mark(player)
end

local function sample(player: Player)
	samples[player] = { at = os.clock(), income = GuestService.income(player) }
end

local function travel(player: Player, location: number)
	local data = PlayerData.get(player)
	if not data or location == data.location then
		return
	end
	local loc = Locations.List[location]
	if not loc or not loc.playable or location > Constants.Chain.Locations then
		Net.fire(player, "Refused", "Travel", "Unknown")
		return
	end
	local opened = ChainService.opened(data)
	local from = data.location
	if not opened[location] then
		if Chain.nextToOpen(opened) ~= location then
			Net.fire(player, "Refused", "Travel", "OpenInOrder")
			return
		end
		local cost = Chain.openCost(location) or 0
		if data.cash < cost then
			Net.fire(player, "Refused", "Travel", "NotEnoughCash")
			return
		end
		data.cash -= cost
	end
	putAway(player, data)
	takeOut(data, location)
	HotelService.switchSamples(player, from, location)
	sample(player)
	ChainService.redraw(player)
	if opened[location] then
		Net.fire(player, "Toast", `Welcome back to your {loc.name}`, "Good")
	else
		Net.fireAll("Announce", `{player.DisplayName} opened a hotel at {loc.name}!`, "Rare")
		Net.fire(player, "Toast", `Your {loc.name} is open. The others keep earning.`, "Unlock")
		PlayerData.stat(player, "hotelsOpened")
	end
	PlayerData.save(player)
	for _, h in travelHandlers do
		task.spawn(h, player, from)
	end
end

-- One tick for a player: pay the chain's other hotels and measure the played one.
local function tick(player: Player)
	local data = PlayerData.get(player)
	local s = samples[player]
	if not data or not s then
		return
	end
	local now = os.clock()
	local dt = now - s.at
	if dt <= 0 then
		return
	end
	data.rate = Chain.updateRate(data.rate, GuestService.income(player) - s.income, dt)
	local pay = 0
	for _, rec in data.chain do
		pay += Chain.background(rec.rate, dt)
	end
	pay = math.floor(pay)
	sample(player)
	if pay > 0 then
		PlayerData.earn(player, pay)
	end
end

function ChainService.Init()
	Net.on("Travel", travel)
end

function ChainService.Start()
	PlayerData.onLoaded(function(player)
		sample(player)
	end)
	Players.PlayerRemoving:Connect(function(player)
		samples[player] = nil
	end)
	task.spawn(function()
		while true do
			task.wait(TICK)
			for _, player in Players:GetPlayers() do
				local ok, err = pcall(tick, player)
				if not ok then
					warn(`[chain] tick for {player.Name}: {err}`)
				end
			end
		end
	end)
	StateService.provide("chain", function(player, data)
		local opened = ChainService.opened(data)
		local ratings = ChainService.ratings(player, data)
		local nextOpen = Chain.nextToOpen(opened)
		local hotels = {}
		for id = 1, Constants.Chain.Locations do
			local rec = data.chain[tostring(id)]
			table.insert(hotels, {
				id = id,
				name = Locations.get(id).name,
				here = id == data.location,
				opened = opened[id] == true,
				canOpen = id == nextOpen,
				cost = Chain.openCost(id),
				rating = ratings[id],
				-- what it earns a minute while not played (PLACEHOLDER share)
				perMinute = if rec then math.floor(Chain.background(rec.rate, 60)) else nil,
			})
		end
		return {
			location = data.location,
			hotels = hotels,
			share = Constants.Chain.BackgroundShare,
			floorCap = BuildService.maxFloors(data),
			prestige = data.prestige,
		}
	end)
	DevGrant.register("chainopen", function(player, args)
		-- Opens (or travels to) a location free: `chainopen 2`.
		local data = PlayerData.get(player)
		local id = tonumber(args[1] or "")
		if not data or not id then
			return "chainopen <location>"
		end
		local cost = Chain.openCost(id) or 0
		data.cash += cost
		travel(player, id)
		local others = {}
		for k in data.chain do
			table.insert(others, k)
		end
		return `location {data.location}; chain {table.concat(others, ",")}`
	end)
	DevGrant.register("chainrating", function(player, args)
		-- Sets a hotel not played's rating as left: `chainrating 2 5`.
		local data = PlayerData.get(player)
		local rec = data and data.chain[args[1] or ""]
		if not rec then
			return "no such hotel in the chain"
		end
		rec.rating = tonumber(args[2] or "") or rec.rating
		StateService.mark(player)
		return `rating {rec.rating}`
	end)
	DevGrant.register("chainrate", function(player, args)
		-- Sets a hotel's measured rate ($/s): `chainrate 2 10`, or the played one's with no location.
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		local rec = data.chain[args[1] or ""]
		local v = tonumber(args[2] or args[1] or "") or 0
		if rec then
			rec.rate = v
		else
			data.rate = v
		end
		StateService.mark(player)
		return `ok {Format.cash(v)}/s`
	end)
	DevGrant.register("chaintick", function(player)
		tick(player)
		local data = PlayerData.get(player)
		return if data then `cash {data.cash}, rate {data.rate}` else "no data"
	end)
end

return ChainService
