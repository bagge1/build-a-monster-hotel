--!strict
--[[
	Expeditions (GDD A.11.2, on its scrutinized recommendations; his ruling on
	the pay, §18 2026-10-26; every number `Constants.Expeditions`, PLACEHOLDER
	but `Pay`). The rules are `Shared/Expeditions` (pure, specced); this runs
	them for each player.

	SENDING (`ExpeditionSend`): a destination open in the run, a length, up to
	three residents from the Wing. They are away as in the Hunter Camp
	(`ResidentService.present`): no Wing earnings, no offline earnings, no
	perk, not movable; they keep learning as in the Wing.

	COUNTING THE PAY as staying counts: each second the player plays, the
	party's Wing rate (`ResidentService.partyRate`) goes into the trip; on
	joining, the trip's part of the time away at the offline rate and cap
	(`Expeditions.countOffline`). Online counting waits until the time away
	is counted (`settled`), so a join never counts the hours away as play.

	COMING HOME: at its end the party is home in the Wing by itself (this
	republishes it), and the board glows until **Collect**
	(`ExpeditionCollect`): the pay into the wallet, the free roll, and a find
	of the destination's location through `FindService.draw`.

	A REBIRTH calls the party home before the chain is taken apart: a trip
	still out pays what was counted so far and rolls nothing (A.11.2
	"Mid-trip"); one already back is collected as Collect would. Travel
	changes nothing.

	State section `expedition`; remotes `ExpeditionSend`, `ExpeditionCollect`.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Expeditions = require(ReplicatedStorage.Shared.Expeditions)
local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local ResidentService = require(ServerScriptService.Server.ResidentService)
local ChainService = require(ServerScriptService.Server.ChainService)
local ProgressionService = require(ServerScriptService.Server.ProgressionService)
local FindService = require(ServerScriptService.Server.FindService)
local StateService = require(ServerScriptService.Server.StateService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local X = Constants.Expeditions

local ExpeditionService = {}

local rng = Random.new()
local function rand(): number
	return rng:NextNumber()
end

local settled: { [Player]: boolean } = {} -- the time away is counted into the trip
local announced: { [Player]: number } = {} -- the trip (its `start`) whose return was announced

local function record(data: PlayerData.Data): Expeditions.Record
	if not data.expedition then
		data.expedition = Expeditions.newRecord()
	end
	return data.expedition
end

local function destinationName(id: number): string
	local d = Expeditions.destination(id)
	return if d then d.name else "the woods"
end

local function lengthText(seconds: number): string
	return if seconds >= 3600 then `{seconds // 3600} h` else `{seconds // 60} min`
end

-- Counts the trip's play seconds up to now (once its time away is counted).
local function countPlay(player: Player, data: PlayerData.Data, trip: Expeditions.Trip)
	if settled[player] and trip.counted < trip.ends then
		Expeditions.countOnline(
			trip,
			ResidentService.partyRate(player, data, trip.party),
			os.time()
		)
	end
end

--[[ On joining: the trip's part of the time away, at the offline rate and
	cap from the logout, as welcome-back counts the Wing's. ]]
local function settle(player: Player, data: PlayerData.Data)
	local trip = record(data).trip
	local since = PlayerData.awaySince(player)
	if trip and since > 0 then
		local now = os.time()
		Expeditions.countOffline(
			trip,
			ResidentService.partyRate(player, data, trip.party, true),
			since,
			now - since,
			ResidentService.offlineCap(player, data),
			now
		)
	elseif trip then
		trip.counted = math.max(trip.counted, os.time())
	end
	settled[player] = true
	StateService.mark(player)
end

local function send(player: Player, destination: number, length: number, party: string)
	local data = PlayerData.get(player)
	if not data or not settled[player] then
		return
	end
	local ids = {}
	for token in string.gmatch(party, "%d+") do
		table.insert(ids, tostring(tonumber(token)))
	end
	local rec = record(data)
	local now = os.time()
	local why = Expeditions.check(
		rec,
		data.residents,
		ids,
		destination,
		length,
		ChainService.opened(data),
		now
	)
	if why then
		Net.fire(player, "Refused", "ExpeditionSend", why)
		return
	end
	Expeditions.start(rec, data.residents, ids, destination, length, now)
	ResidentService.publish(player)
	Net.fire(
		player,
		"Toast",
		`Your residents set off for the {destinationName(destination)}: back in {lengthText(length)}`,
		"Good"
	)
	PlayerData.stat(player, "expeditions")
	StateService.mark(player)
end

--[[ A trip that is back: its pay into the wallet, its roll, a find drawn at
	its destination. Returns the pay, or nil when none is back. ]]
local function collectTrip(player: Player, data: PlayerData.Data): number?
	local rec = record(data)
	local trip = rec.trip
	if not trip then
		return nil
	end
	countPlay(player, data, trip)
	local cash, found, done = Expeditions.collect(rec, data.residents, rand, os.time())
	if not done then
		return nil
	end
	local d = Expeditions.destination(done.destination)
	PlayerData.earn(player, cash)
	Net.fire(player, "Moment", "ExpeditionCollected", {
		cash = cash,
		destination = done.destination,
		name = destinationName(done.destination),
		found = found,
	})
	Net.fire(
		player,
		"Toast",
		`Back from the {destinationName(done.destination)}: +{Format.cash(cash)}`,
		"Good"
	)
	if found and d then
		FindService.draw(player, d.location, `an expedition to the {d.name}`)
	end
	announced[player] = nil
	ResidentService.publish(player)
	PlayerData.stat(player, "expeditionsCollected")
	StateService.mark(player)
	return cash
end

local function collect(player: Player)
	local data = PlayerData.get(player)
	if not data or not settled[player] then
		return
	end
	if not collectTrip(player, data) then
		Net.fire(player, "Refused", "ExpeditionCollect", "Nobody is back yet")
	end
end

-- A rebirth (A.11.2 "Mid-trip"): a trip back is collected; one still out pays what was counted and rolls nothing.
local function onRebirthStart(player: Player)
	local data = PlayerData.get(player)
	local trip = data and record(data).trip
	if not data or not trip then
		return
	end
	if Expeditions.back(trip, os.time()) then
		collectTrip(player, data)
		return
	end
	countPlay(player, data, trip)
	local cash = Expeditions.recall(record(data), data.residents)
	PlayerData.earn(player, cash)
	Net.fire(
		player,
		"Toast",
		`Your residents came home from the {destinationName(trip.destination)} for the rebirth: +{Format.cash(
			cash
		)}`,
		"Good"
	)
	announced[player] = nil
	ResidentService.publish(player)
	StateService.mark(player)
end

-- Once a second: the play seconds into each trip, and a party home at its end.
local function tick()
	local now = os.time()
	for player, data in PlayerData.loaded() do
		local trip = record(data).trip
		if trip and settled[player] then
			countPlay(player, data, trip)
			if Expeditions.back(trip, now) and announced[player] ~= trip.start then
				announced[player] = trip.start
				-- Home in the Wing by itself (its Away attribute, the Wing's rate).
				ResidentService.publish(player)
				Net.fire(
					player,
					"Toast",
					`Your residents are back from the {destinationName(trip.destination)}! Collect at the Expedition board`,
					"Unlock"
				)
				StateService.mark(player)
			end
		end
	end
end

function ExpeditionService.Init()
	Net.on("ExpeditionSend", send)
	Net.on("ExpeditionCollect", collect)
end

function ExpeditionService.Start()
	PlayerData.onLoaded(function(player, data)
		-- Deferred as welcome-back is, so the Moon Tree's OfflineBonus is on the player.
		task.defer(settle, player, data)
	end)
	PlayerData.onDeparted(function(player)
		settled[player] = nil
		announced[player] = nil
	end)
	ProgressionService.onRebirthStart(onRebirthStart)
	StateService.provide("expedition", function(player, data)
		local rec = record(data)
		local opened = ChainService.opened(data)
		local destinations = {}
		for _, d in Expeditions.Destinations do
			table.insert(destinations, {
				id = d.id,
				name = d.name,
				location = d.location,
				likes = d.likes,
				open = Expeditions.offered(d.id, opened),
			})
		end
		local lengths = {}
		for _, seconds in Expeditions.lengths() do
			table.insert(lengths, { seconds = seconds, chance = X.Lengths[seconds] })
		end
		local trip = rec.trip
		local out = nil
		if trip then
			local now = os.time()
			local party = {}
			for _, id in trip.party do
				local r = data.residents[id]
				if r then
					table.insert(party, {
						id = tonumber(id),
						species = r.species,
						mutation = r.mutation,
						size = r.size,
					})
				end
			end
			out = {
				destination = trip.destination,
				name = destinationName(trip.destination),
				length = trip.length,
				left = Expeditions.left(trip, now),
				back = Expeditions.back(trip, now),
				party = party,
				pay = Expeditions.pay(trip), -- so far, by what was counted
				chance = Expeditions.findChance(trip.length, trip.matches),
				guaranteed = Expeditions.guaranteed(rec, trip.length),
				start = trip.start,
			}
		end
		return {
			destinations = destinations,
			lengths = lengths,
			party = X.Party,
			pay = X.Pay,
			match = X.Match,
			pityTrips = X.PityTrips,
			pityMin = X.PityMin,
			longMisses = rec.longMisses,
			trips = rec.trips,
			trip = out,
			ready = settled[player] == true,
		}
	end)
	-- Studio only: `trip show`, `trip end` (the trip out comes home now).
	DevGrant.register("trip", function(player, args)
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		local rec = record(data)
		local trip = rec.trip
		if (args[1] or "show") == "end" and trip then
			countPlay(player, data, trip)
			local now = os.time()
			for _, id in trip.party do
				local r = data.residents[id]
				if r and r.expedition == trip.ends then
					r.expedition = now
				end
			end
			trip.ends = now
			return `ends now; pay {Expeditions.pay(trip)}`
		end
		if not trip then
			return `no trip; trips {rec.trips} long misses {rec.longMisses}`
		end
		return `{destinationName(trip.destination)} {trip.length}s left {Expeditions.left(
			trip,
			os.time()
		)}s earned {math.floor(trip.earned)} pay {Expeditions.pay(trip)} party {table.concat(
			trip.party,
			","
		)} chance {Expeditions.findChance(trip.length, trip.matches)}`
	end)
	task.spawn(function()
		while true do
			task.wait(1)
			local ok, err = pcall(tick)
			if not ok then
				warn(`[expeditions] tick failed: {err}`)
			end
		end
	end)
end

return ExpeditionService
