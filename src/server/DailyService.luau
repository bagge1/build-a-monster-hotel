--!strict
--[[
	The daily return hooks (GDD §8.2 "Daily", §9): the Featured Monster of the
	Day (double friendship), three daily requests with rewards and rerolls,
	the 7-day login calendar (a cosmetic on day 7; missing a day pauses the
	streak, it never resets it), and codes (§9 "a codes system").

	A day is the UTC day (`os.time() // 86400`), the same on every server.
	Request progress is a profile stat counted from where it stood when the
	request was drawn, so it survives a rejoin. Every reward amount is a
	PLACEHOLDER (GDD Appendix A.9).

	Codes live here, on the server only, so no client can read the list.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local Species = require(ReplicatedStorage.Shared.Species)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local HotelService = require(ServerScriptService.Server.HotelService)
local ResidentService = require(ServerScriptService.Server.ResidentService)
local StoreService = require(ServerScriptService.Server.StoreService)
local StateService = require(ServerScriptService.Server.StateService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local DailyService = {}

local DAY = 86400
local REQUESTS_PER_DAY = 3 -- §8.2
local BASE_REROLLS = 1 -- PLACEHOLDER
local REWARD_MINUTES = 8 -- PLACEHOLDER: each request pays 8 minutes of income
local LOGIN_MINUTES = { 3, 4, 5, 6, 8, 10, 15 } -- PLACEHOLDER: days 1–7
local LOGIN_COSMETIC = "Cosmetic_LanternSign" -- day 7's cosmetic (§8.2; Cosmetics.luau)

-- The kinds of daily request (§8.2: "Serve 5 Ghosts", "Reach 3★").
type Kind = { id: string, text: string, stat: string?, target: (number) -> number }
local KINDS: { Kind } = {
	{
		id = "Stays",
		text = "Host {n} happy stays",
		stat = "happyStays",
		target = function(_)
			return 5
		end,
	},
	{
		id = "CheckIns",
		text = "Check in {n} guests",
		stat = "checkIns",
		target = function(_)
			return 10
		end,
	},
	{
		id = "Clean",
		text = "Clean {n} rooms",
		stat = "cleaned",
		target = function(_)
			return 5
		end,
	},
	{
		id = "Pitch",
		text = "Pitch {n} bus guests",
		stat = "pitches",
		target = function(_)
			return 3
		end,
	},
	{
		id = "Requests",
		text = "Answer {n} guest requests",
		stat = "requests",
		target = function(_)
			return 4
		end,
	},
	{
		id = "Collect",
		text = "Collect the till {n} times",
		stat = "collects",
		target = function(_)
			return 6
		end,
	},
	{
		id = "Rating",
		text = "Reach {n}★",
		stat = nil,
		target = function(rating)
			return math.min(5, math.floor(rating) + 1)
		end,
	},
	{
		id = "Serve",
		text = "Serve {n} {species}",
		stat = "served_",
		target = function(_)
			return 3
		end,
	},
}

local CODES: { [string]: { cash: number?, shards: number? } } = {
	-- PLACEHOLDER codes for the social channels (§9); August names the real ones.
	WELCOME = { cash = 500 },
	SPOOKY = { shards = 3 },
}

function DailyService.today(): number
	return os.time() // DAY
end

-- The day's featured species (§8.2), the same on every server: one of the families present.
function DailyService.featured(location: number): string
	local list = Species.ofLocation(location)
	local day = DailyService.today()
	local i = (day * 7919) % #list + 1
	return list[i].id
end

local function draw(player: Player, data: PlayerData.Data, rng: Random): { [string]: any }
	local kind = KINDS[rng:NextInteger(1, #KINDS)]
	local species: string? = nil
	local stat = kind.stat
	if kind.id == "Serve" then
		local list = {}
		for _, sp in Species.ofLocation(data.location) do
			if sp.rarity == "Common" or sp.rarity == "Uncommon" then
				table.insert(list, sp.id)
			end
		end
		species = list[rng:NextInteger(1, #list)]
		stat = `served_{species}`
	end
	local target = kind.target(HotelService.rating(player))
	local sp = species and Species.get(species)
	local text = string.gsub(
		string.gsub(kind.text, "{n}", tostring(target)),
		"{species}",
		if sp
			then (if string.sub(sp.name, -1) == "y"
				then string.sub(sp.name, 1, -2) .. "ies"
				else sp.name .. "s")
			else ""
	)
	return {
		kind = kind.id,
		text = text,
		stat = stat,
		target = target,
		base = if stat then (data.stats[stat] or 0) else 0,
		claimed = false,
	}
end

local function ensureDay(player: Player, data: PlayerData.Data)
	local today = DailyService.today()
	if data.daily.day == today and #data.daily.list == REQUESTS_PER_DAY then
		return
	end
	local rng = Random.new(today * 1000 + (player.UserId % 1000))
	data.daily.day = today
	data.daily.list = {}
	data.daily.rerolls = 0
	for _ = 1, REQUESTS_PER_DAY do
		table.insert(data.daily.list, draw(player, data, rng))
	end
end

local function progress(player: Player, data: PlayerData.Data, r: any): number
	if r.kind == "Rating" then
		return if HotelService.rating(player) >= r.target
			then r.target
			else math.floor(HotelService.rating(player))
	end
	return math.max(0, (data.stats[r.stat] or 0) - r.base)
end

function DailyService.rerolls(player: Player, data: PlayerData.Data): number
	local extra = (player:GetAttribute("Rerolls") :: number? or 0)
		+ (if data.passes.VIPLobby then 1 else 0)
	return BASE_REROLLS + extra - data.daily.rerolls
end

local function claim(player: Player, index: number)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	ensureDay(player, data)
	local r = data.daily.list[index]
	if not r or r.claimed or progress(player, data, r) < r.target then
		return
	end
	r.claimed = true
	local amount = math.floor(StoreService.incomeRate(player) * REWARD_MINUTES * 60)
	PlayerData.earn(player, amount)
	Net.fire(player, "Toast", `Daily request done: +{Format.cash(amount)}`, "Unlock")
	local all = true
	for _, other in data.daily.list do
		all = all and other.claimed
	end
	if all then
		PlayerData.addShards(player, 1) -- PLACEHOLDER: a shard for all three
		Net.fire(player, "Toast", "All three done! +1 Moon Shard", "Unlock")
	end
	StateService.mark(player)
end

local function reroll(player: Player, index: number)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	ensureDay(player, data)
	local r = data.daily.list[index]
	if not r or r.claimed or DailyService.rerolls(player, data) <= 0 then
		return
	end
	data.daily.rerolls += 1
	data.daily.list[index] = draw(player, data, Random.new())
	StateService.mark(player)
end

local function login(player: Player)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local today = DailyService.today()
	if data.login.claimedDay == today then
		return
	end
	-- Missing a day pauses the streak; it never resets it (§8.2).
	data.login.streak = data.login.streak % 7 + 1
	data.login.claimedDay = today
	data.login.lastDay = today
	local day = data.login.streak
	local amount = math.floor(StoreService.incomeRate(player) * LOGIN_MINUTES[day] * 60)
	PlayerData.earn(player, amount)
	if day == 7 then
		data.cosmetics[LOGIN_COSMETIC] = true
		Net.fire(player, "Announce", "Day 7! You earned the Lantern sign cosmetic.", "Rare")
	end
	Net.fire(player, "Toast", `Login day {day}: +{Format.cash(amount)}`, "Unlock")
	StateService.mark(player)
end

local function redeem(player: Player, raw: string)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local code = string.upper(string.gsub(raw, "%s", ""))
	local reward = CODES[code]
	if not reward then
		Net.fire(player, "Refused", "Code", "That code doesn't work")
		return
	end
	if data.codes[code] then
		Net.fire(player, "Refused", "Code", "You already used that code")
		return
	end
	data.codes[code] = true
	if reward.cash then
		PlayerData.earn(player, reward.cash)
	end
	if reward.shards then
		PlayerData.addShards(player, reward.shards)
	end
	Net.fire(player, "Toast", `Code {code} redeemed!`, "Unlock")
	StateService.mark(player)
end

function DailyService.Init()
	Net.on("Daily", function(player, what, index)
		if what == "Claim" then
			claim(player, index)
		elseif what == "Reroll" then
			reroll(player, index)
		elseif what == "Login" then
			login(player)
		end
	end)
	Net.on("Code", redeem)
end

function DailyService.Start()
	-- Double friendship for the day's featured species (§8.2).
	ResidentService.addFriendship(function(player, speciesId)
		local data = PlayerData.get(player)
		return if data and DailyService.featured(data.location) == speciesId then 2 else 1
	end)
	PlayerData.onLoaded(function(player, data)
		ensureDay(player, data)
	end)
	StateService.provide("daily", function(player, data)
		ensureDay(player, data)
		local list = {}
		for i, r in data.daily.list do
			table.insert(list, {
				index = i,
				text = r.text,
				have = math.min(progress(player, data, r), r.target),
				target = r.target,
				claimed = r.claimed,
			})
		end
		local featured = Species.get(DailyService.featured(data.location))
		return {
			list = list,
			rerolls = DailyService.rerolls(player, data),
			featured = featured and featured.name or "",
			loginDay = data.login.streak,
			loginClaimed = data.login.claimedDay == DailyService.today(),
			nextLoginDay = data.login.streak % 7 + 1,
		}
	end)
	DevGrant.register("daily", function(player)
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		ensureDay(player, data)
		local out = {}
		for i, r in data.daily.list do
			table.insert(out, `{i}: {r.text} {progress(player, data, r)}/{r.target}`)
		end
		return table.concat(out, " | ")
	end)
	-- Progress changes as stats move: refresh the panel now and then.
	task.spawn(function()
		while true do
			task.wait(15)
			StateService.markAll()
		end
	end)
end

return DailyService
