--!strict
--[[
	Rare decor sets and souvenirs (GDD A.11.3), on the draft's scrutinized
	recommendations (his calls, WAITING §2.38; every number
	`Constants.Finds`, PLACEHOLDER). The rules are `Shared/Finds` (pure,
	specced); this runs them for each player.

	FINDS. A happy stay of a Rare-or-better guest rolls for a set piece of the
	played hotel's location (`StayChance`), and so does every player on a
	defended Hunter Night (`HunterChance`; decision 5: per street, one roll
	for each player on it). The pity gives the next unfound piece after a run
	of misses. An expedition's collected trip that found (A.11.2, its roll
	and guarantee `Expeditions`') draws a piece of its destination's location
	(`draw`). Once a location's sets are all found, a find is a duplicate,
	paid in cash (`DuplicateMinutes` of income, at least the piece's price).

	SOUVENIRS. A species' souvenir on its first VIP contract
	(`ContractService.onSouvenir`) or its `SouvenirMoveIns`-th move-in,
	whichever first.

	A find is kept in the profile's `finds` (found once; `BuildService`
	then places copies for cash) and through a rebirth while
	`KeepThroughRebirth` (decision 4a, his call). It pops up on the client
	(`Moment` "Found") with the piece and where it goes.

	State section `finds`.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Finds = require(ReplicatedStorage.Shared.Finds)
local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Species = require(ReplicatedStorage.Shared.Species)
local Stay = require(ReplicatedStorage.Shared.Stay)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local GuestService = require(ServerScriptService.Server.GuestService)
local ResidentService = require(ServerScriptService.Server.ResidentService)
local HunterService = require(ServerScriptService.Server.HunterService)
local ContractService = require(ServerScriptService.Server.ContractService)
local ProgressionService = require(ServerScriptService.Server.ProgressionService)
local StoreService = require(ServerScriptService.Server.StoreService)
local StateService = require(ServerScriptService.Server.StateService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local F = Constants.Finds

local FindService = {}

local rng = Random.new()
local function rand(): number
	return rng:NextNumber()
end

local function record(data: PlayerData.Data): Finds.Record
	if not data.finds then
		data.finds = Finds.newRecord()
	end
	return data.finds
end

-- What the pop-up shows for a decor id: its name, its set and how many of it are found.
local function describe(data: PlayerData.Data, id: string): { [string]: any }
	local d = Pieces.decor(id)
	local out: { [string]: any } = {
		id = id,
		name = if d then d.name else id,
		layer = if d then d.layer else "Floor",
		w = if d then d.w else 1,
		d = if d then d.d else 1,
		price = if d then d.cost else 0,
	}
	local set = d and d.set and Pieces.SetById[d.set]
	if set then
		local have = 0
		for _, p in set.pieces do
			if data.finds.found[p] then
				have += 1
			end
		end
		out.set = set.name
		out.have = have
		out.total = #set.pieces
	end
	return out
end

-- What a roll or a draw gave: the pop-up, the announcement, a duplicate's cash, the state.
local function give(
	player: Player,
	data: PlayerData.Data,
	out: Finds.Outcome,
	id: string?,
	why: string
)
	if out == "Piece" and id then
		local info = describe(data, id)
		info.kind = "Piece"
		info.why = why
		Net.fire(player, "Moment", "Found", info)
		Net.fire(player, "Announce", `You found {info.name}!`, "Rare")
		PlayerData.stat(player, "rareFinds")
		StateService.mark(player)
	elseif out == "Duplicate" and id then
		local d = Pieces.decor(id)
		local cash = math.max(
			if d then d.cost else 0,
			math.floor(StoreService.incomeRate(player) * F.DuplicateMinutes * 60)
		)
		PlayerData.earn(player, cash)
		local info = describe(data, id)
		info.kind = "Duplicate"
		info.why = why
		info.cash = cash
		Net.fire(player, "Moment", "Found", info)
		PlayerData.stat(player, "rareDuplicates")
		StateService.mark(player)
	elseif out == "Miss" then
		StateService.mark(player)
	end
end

--[[ One roll for the played hotel's set pieces (`why` says where it came
	from, for the pop-up). Returns the outcome, for the dev commands. ]]
function FindService.roll(player: Player, chance: number, why: string): Finds.Outcome
	local data = PlayerData.get(player)
	if not data then
		return "None"
	end
	local out, id = Finds.roll(record(data), data.location, chance, rand, os.time())
	give(player, data, out, id, why)
	return out
end

--[[ An expedition's find (A.11.2): its roll already found, so a piece of the
	destination's `location` (not the hotel played) among the unfound, or a
	duplicate. The trip's own guarantee is `Expeditions`'; the stays' pity is
	left alone. ]]
function FindService.draw(player: Player, location: number, why: string): Finds.Outcome
	local data = PlayerData.get(player)
	if not data then
		return "None"
	end
	local out, id = Finds.draw(record(data), location, rand, os.time())
	give(player, data, out, id, why)
	return out
end

-- A species' souvenir, if it is new: the pop-up and the state. `why` for the pop-up.
function FindService.souvenir(
	player: Player,
	species: string,
	why: string,
	viaMoveIn: boolean?
): boolean
	local data = PlayerData.get(player)
	if not data then
		return false
	end
	local rec = record(data)
	local now = os.time()
	local new = if viaMoveIn
		then Finds.moveIn(rec, species, now)
		else Finds.giveSouvenir(rec, species, now)
	if not new then
		if viaMoveIn then
			StateService.mark(player)
		end
		return false
	end
	local info = describe(data, Finds.souvenirId(species))
	info.kind = "Souvenir"
	info.species = species
	info.why = why
	Net.fire(player, "Moment", "Found", info)
	PlayerData.stat(player, "souvenirs")
	StateService.mark(player)
	return true
end

function FindService.Init() end

function FindService.Start()
	GuestService.onCheckout(function(player, g, satisfaction)
		local sp = Species.get(g.species)
		if sp and Stay.isHappy(satisfaction) and Finds.rolls(sp.rarity) then
			FindService.roll(player, F.StayChance, `a happy {sp.rarity} guest's stay`)
		end
	end)
	HunterService.onDefended(function()
		for player in PlayerData.loaded() do
			FindService.roll(player, F.HunterChance, "a defended Hunter Night")
		end
	end)
	ResidentService.onMoveIn(function(player, _, rec)
		local sp = Species.get(rec.species)
		FindService.souvenir(
			player,
			rec.species,
			`{if sp then sp.name else rec.species}'s move-in no. {F.SouvenirMoveIns}`,
			true
		)
	end)
	ContractService.onSouvenir(function(player, species)
		local sp = Species.get(species)
		FindService.souvenir(
			player,
			species,
			`{if sp then sp.name else species}'s first VIP contract`
		)
	end)
	ProgressionService.onRebirth(function(player)
		local data = PlayerData.get(player)
		if data and not F.KeepThroughRebirth then
			data.finds = Finds.newRecord()
			StateService.mark(player)
		end
	end)
	StateService.provide("finds", function(_, data)
		local rec = record(data)
		local found = {}
		for id in rec.found do
			table.insert(found, id)
		end
		table.sort(found)
		return {
			found = found,
			misses = rec.misses[tostring(data.location)] or 0,
			pity = F.Pity,
			moveIns = rec.moveIns,
			souvenirMoveIns = F.SouvenirMoveIns,
		}
	end)

	-- Studio only: `rare roll [n] [chance]`, `rare misses <n>`, `rare give <decor id>`,
	-- `rare souvenir <species>` (as a first VIP contract), `rare reset`, `rare show`.
	DevGrant.register("rare", function(player, args)
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		local rec = record(data)
		local what = args[1] or "show"
		if what == "roll" then
			local counts: { [string]: number } = {}
			for _ = 1, tonumber(args[2]) or 1 do
				local out =
					FindService.roll(player, tonumber(args[3]) or F.StayChance, "a dev roll")
				counts[out] = (counts[out] or 0) + 1
			end
			local parts = {}
			for k, v in counts do
				table.insert(parts, `{k}={v}`)
			end
			table.sort(parts)
			return table.concat(parts, " ") .. ` misses {rec.misses[tostring(data.location)] or 0}`
		elseif what == "misses" then
			rec.misses[tostring(data.location)] = tonumber(args[2]) or 0
			StateService.mark(player)
			return `misses {rec.misses[tostring(data.location)]}`
		elseif what == "give" then
			local id = args[2] or ""
			if not Pieces.decor(id) then
				return "no such decor"
			end
			rec.found[id] = os.time()
			StateService.mark(player)
			return `found {id}`
		elseif what == "souvenir" then
			return tostring(FindService.souvenir(player, args[2] or "Slime", "a dev grant"))
		elseif what == "reset" then
			data.finds = Finds.newRecord()
			StateService.mark(player)
			return "reset"
		end
		local found = {}
		for id in rec.found do
			table.insert(found, id)
		end
		table.sort(found)
		return `found [{table.concat(found, ", ")}] misses {rec.misses[tostring(data.location)] or 0}/{F.Pity} `
			.. `cash {Format.cash(data.cash)}`
	end)
end

return FindService
