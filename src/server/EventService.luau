--!strict
--[[
	The events (GDD §8.2), from the calendar in `Events`: the Full Moon weekend
	(bus weights, `BusService`), the Monster Parade (a bus a minute,
	`BusService`; announced 15 minutes ahead here), the Saturday Full Moon Hunt
	(a Hunter Night with twice the hunters), and the season's event with its
	Candy (§6.1 "event currency, kept for the event's duration") and Candy shop.

	Candy: +1 per happy stay (+2 Epic, +3 Legendary and up) and +10 for a
	defended Hunter Night, during a season that has a currency. A new season
	starts every profile's Candy from zero. Night drafts (Appendix A.10).
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Events = require(ReplicatedStorage.Shared.Events)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Species = require(ReplicatedStorage.Shared.Species)
local Stay = require(ReplicatedStorage.Shared.Stay)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local GuestService = require(ServerScriptService.Server.GuestService)
local HunterService = require(ServerScriptService.Server.HunterService)
local StateService = require(ServerScriptService.Server.StateService)
local DevGrant = require(ServerScriptService.Server.DevGrant)
local Safe = require(ServerScriptService.Server.Safe)

local EventService = {}

local CANDY_BY_RARITY = { Common = 1, Uncommon = 1, Rare = 1, Epic = 2, Legendary = 3, Mythic = 3 }
local CANDY_DEFENDED = 10

local clockOffset = 0 -- STUDIO: dev `eventclock` shifts the calendar to test an event

function EventService.now(): number
	return os.time() + clockOffset
end

local function seasonFor(data: PlayerData.Data): Events.Season?
	local s = Events.season(EventService.now())
	if s and s.currency and data.candySeason ~= s.id then
		data.candy = 0
		data.candySeason = s.id
	end
	return s
end

local function addCandy(player: Player, n: number)
	local data = PlayerData.get(player)
	local s = data and seasonFor(data)
	if not data or not s or not s.currency then
		return
	end
	data.candy += n
	player:SetAttribute("Candy", data.candy)
	StateService.mark(player)
end

local function buy(player: Player, key: string)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local s = seasonFor(data)
	local item
	for _, i in Events.shop(s and s.id) do
		if i.key == key then
			item = i
		end
	end
	if not item or not s or not s.currency then
		return
	end
	-- Event decor is one copy per purchase (WAITING §2.48): bought again for another copy. A cosmetic once.
	local decor = string.sub(key, 1, 6) == "Decor_"
	if not decor and (data.unlocked[key] or data.cosmetics[key]) then
		Net.fire(player, "Refused", "EventShop", "You already have it")
		return
	end
	if data.candy < item.cost then
		Net.fire(player, "Refused", "EventShop", `Not enough {s.currencyName}`)
		return
	end
	data.candy -= item.cost
	player:SetAttribute("Candy", data.candy)
	if decor then
		local copies = Pieces.copiesKey(string.sub(key, 7))
		data.stats[copies] = Pieces.copiesBought(data.stats[copies], data.unlocked[key] == true) + 1
		data.unlocked[key] = true
	else
		data.cosmetics[key] = true
	end
	Net.fire(player, "Toast", `{item.name} is yours!`, "Unlock")
	StateService.mark(player)
end

local announcedParade = 0
local startedHunt = 0
local announcedSeason = ""
local announcedMonthly = "" -- the mutation of the month announced (A.11.5)

local function tick()
	local t = EventService.now()
	-- The Parade: a notice 15 minutes ahead, then the start (§8.2 "announced in advance").
	local p = Events.paradeStart(t)
	if p and announcedParade ~= p then
		if t >= p - Events.ParadeNotice and t < p then
			announcedParade = p
			Net.fireAll(
				"Announce",
				"A Monster Parade starts in 15 minutes: a bus every minute, full of rare guests!",
				"Rare"
			)
		end
	end
	if p and Events.parade(t) and workspace:GetAttribute("Parade") ~= true then
		workspace:SetAttribute("Parade", true)
		Net.fireAll("Announce", "The Monster Parade has begun!", "Rare")
	elseif not (p and Events.parade(t)) and workspace:GetAttribute("Parade") == true then
		workspace:SetAttribute("Parade", false)
	end
	-- The Saturday Full Moon Hunt.
	local h = Events.huntStart(t)
	-- A Hunter Night already on holds it off: it starts once that night is over,
	-- inside the window (a night is 3 minutes, the window 5).
	if h and startedHunt ~= h and t >= h and t < h + 300 and HunterService.start(2) then
		startedHunt = h
		Net.fireAll("Announce", "The Full Moon Hunt! Twice the hunters tonight!", "Hunter")
	end
	workspace:SetAttribute("FullMoon", Events.fullMoonWeekend(t))
	local season = Events.season(t)
	workspace:SetAttribute("Season", if season then season.name else nil)
	if season and announcedSeason ~= season.id then
		announcedSeason = season.id
		Net.fireAll(
			"Announce",
			`{season.name} is here! Look out for {season.mutation} guests.`,
			"Rare"
		)
	end
	-- The mutation of the month (A.11.5), announced once per server as its month begins.
	local monthly = Events.monthly(t)
	workspace:SetAttribute("MonthlyMutation", monthly)
	if monthly and announcedMonthly ~= monthly then
		announcedMonthly = monthly
		Net.fireAll("Announce", `This month's mutation: look out for {monthly} guests!`, "Rare")
	end
end

function EventService.Init()
	Net.on("EventShop", buy)
end

function EventService.Start()
	GuestService.onCheckout(function(player, g, satisfaction)
		if Stay.isHappy(satisfaction) then
			local sp = Species.get(g.species)
			addCandy(player, if sp then CANDY_BY_RARITY[sp.rarity] or 1 else 1)
		end
	end)
	HunterService.onDefended(function()
		for player in PlayerData.loaded() do
			addCandy(player, CANDY_DEFENDED)
		end
	end)
	PlayerData.onLoaded(function(player, data)
		seasonFor(data)
		player:SetAttribute("Candy", data.candy)
	end)
	StateService.provide("event", function(_, data)
		local t = EventService.now()
		local s = seasonFor(data)
		local shop = {}
		for _, i in Events.shop(s and s.id) do
			table.insert(shop, {
				key = i.key,
				name = i.name,
				cost = i.cost,
				text = i.text,
				-- Decor is never "owned" here: each purchase is one more copy (WAITING §2.48).
				owned = string.sub(i.key, 1, 6) ~= "Decor_" and data.cosmetics[i.key] == true,
			})
		end
		local p = Events.paradeStart(t)
		return {
			season = if s then s.name else nil,
			mutation = if s then s.mutation else nil,
			monthly = Events.monthly(t), -- the mutation of the month (A.11.5)
			currency = s ~= nil and s.currency,
			currencyName = if s then s.currencyName else nil,
			icon = if s then s.icon else nil,
			candy = data.candy,
			shop = shop,
			fullMoon = Events.fullMoonWeekend(t),
			parade = Events.parade(t),
			paradeIn = if p and t < p then p - t else nil,
		}
	end)
	DevGrant.register("candy", function(player, args)
		addCandy(player, tonumber(args[1]) or 50)
		return "ok"
	end)
	DevGrant.register("eventclock", function(_, args)
		-- Shift the event calendar by N hours (STUDIO only) to see an event now.
		clockOffset = (tonumber(args[1]) or 0) * 3600
		return `calendar at {os.date("!%A %Y-%m-%d %H:%M", EventService.now())} UTC`
	end)
	task.spawn(function()
		while true do
			task.wait(5)
			Safe.call("[event] tick", tick) -- said once a minute when it fails (2026-10-26: it failed silently)
		end
	end)
end

return EventService
