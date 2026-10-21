--!strict
--[[
	The events calendar (GDD §8.2), as pure functions of the server clock
	(UTC), so every server agrees on what is on without asking anyone:

	  - FULL MOON WEEKEND (Saturday and Sunday): more Legendaries and Epics on
	    the bus (the Werewolf is the full moon's Epic).
	  - FULL MOON HUNT (Saturday 20:00 UTC): a Hunter Night with twice the hunters.
	  - MONSTER PARADE (Friday 18:00–18:10 UTC, announced from 17:45): a bus
	    every minute, weighted to the rare.
	  - THE SEASON: Halloween (1 October – 3 November), our biggest event (§8.2):
	    Candy from every happy stay, the Pumpkin mutation, the Candy shop.
	    Winter (10 December – 5 January), the Frostfang crossover: Snowflakes,
	    the Frosted mutation, the Winter shop.
	  Each season with a currency has its own shop (`Events.Shops`); the
	  currency is one profile field for whichever season is on.

	Every time and weight here is a night draft (GDD Appendix A.10).
]]

local Constants = require(script.Parent.Constants)
local Mutations = require(script.Parent.Mutations)

local Events = {}

local function parts(t: number): any
	return os.date("!*t", t)
end

function Events.fullMoonWeekend(t: number): boolean
	local d = parts(t)
	return d.wday == 7 or d.wday == 1 -- Saturday, Sunday
end

-- The Saturday Full Moon Hunt's start, for the week of `t` (nil on other days).
function Events.huntStart(t: number): number?
	local d = parts(t)
	if d.wday ~= 7 then
		return nil
	end
	return t - (d.hour * 3600 + d.min * 60 + d.sec) + 20 * 3600
end

Events.ParadeLength = 10 * 60
Events.ParadeNotice = 15 * 60
Events.ParadeInterval = 60

-- The Friday Monster Parade's start, for the week of `t` (nil on other days).
function Events.paradeStart(t: number): number?
	local d = parts(t)
	if d.wday ~= 6 then
		return nil
	end
	return t - (d.hour * 3600 + d.min * 60 + d.sec) + 18 * 3600
end

function Events.parade(t: number): boolean
	local s = Events.paradeStart(t)
	return s ~= nil and t >= s and t < s + Events.ParadeLength
end

export type Season = {
	id: string,
	name: string,
	mutation: string,
	chance: number,
	currency: boolean,
	currencyName: string, -- what the season's currency is called
	icon: string, -- the currency's and the Events button's glyph
}

local SEASONS: { { from: { number }, to: { number }, season: Season } } = {
	{
		from = { 10, 1 },
		to = { 11, 3 },
		season = {
			id = "Halloween",
			name = "Halloween",
			mutation = "Pumpkin",
			chance = 0.03,
			currency = true,
			currencyName = "Candy",
			icon = "🍬",
		},
	},
	{
		from = { 12, 10 },
		to = { 1, 5 },
		season = {
			id = "Winter",
			name = "Winter",
			mutation = "Frosted",
			chance = 0.03,
			currency = true, -- night draft (Appendix A.10)
			currencyName = "Snowflakes",
			icon = "❄",
		},
	},
}

local function within(month: number, day: number, from: { number }, to: { number }): boolean
	local v, a, b = month * 100 + day, from[1] * 100 + from[2], to[1] * 100 + to[2]
	if a <= b then
		return v >= a and v <= b
	end
	return v >= a or v <= b -- across New Year
end

function Events.season(t: number): Season?
	local d = parts(t)
	for _, s in SEASONS do
		if within(d.month, d.day, s.from, s.to) then
			return s.season
		end
	end
	return nil
end

-- The bus's rarity weights at `t`: the GDD's (§4.2), raised on a Full Moon weekend or a Parade.
function Events.weights(t: number): { [string]: number }
	local w = {}
	for id, r in Constants.Rarity do
		w[id] = r.weight
	end
	if Events.fullMoonWeekend(t) then
		w.Legendary *= 3
		w.Epic *= 2
	end
	if Events.parade(t) then
		w.Common *= 0.5
		w.Rare *= 2
		w.Epic *= 3
		w.Legendary *= 4
	end
	return w
end

-- The mutation of the month at `t` (A.11.5; Constants.Mutations.Monthly), or nil.
function Events.monthly(t: number): string?
	return Constants.Mutations.Monthly[parts(t).month]
end

--[[ The look rolled at `t`: the season's own or the month's mutation is a
	row of the look table, taken first and the rest scaled (§4.5 "Seasonal:
	event only", A.11.5), so Shadow, Golden and Glitched come in every month. ]]
function Events.rollMutation(r: number, t: number): string?
	local s = Events.season(t)
	local monthly = Events.monthly(t)
	local extra = if s
		then { id = s.mutation, chance = s.chance }
		elseif monthly then { id = monthly, chance = Constants.Mutations.MonthlyChance }
		else nil
	return Mutations.rollLook(r, extra)
end

-- A guest's size and look at `t` (A.11.5 decision 1a): two independent rolls.
function Events.rollMutations(rSize: number, rLook: number, t: number): (string?, string?)
	return Mutations.rollSize(rSize), Events.rollMutation(rLook, t)
end

export type ShopItem = { key: string, name: string, cost: number, text: string }

-- Each season's shop (§8.2): event cosmetics and decor, bought with its currency.
Events.Shops = {} :: { [string]: { ShopItem } }

Events.Shops.Halloween = {
	{
		key = "Decor_JackOLantern",
		name = "Jack-o'-Lantern decor",
		cost = 30,
		text = "A decor piece for any room: candles, garden.",
	},
	{
		key = "Cosmetic_PumpkinSign",
		name = "Pumpkin sign",
		cost = 60,
		text = "Your hotel sign, carved from a pumpkin.",
	},
	{
		key = "Cosmetic_BatBunting",
		name = "Bat bunting",
		cost = 90,
		text = "Paper bats strung across your lobby.",
	},
}

-- Winter, the Frostfang crossover (night draft, Appendix A.10).
Events.Shops.Winter = {
	{
		key = "Decor_Snowman",
		name = "Snowman decor",
		cost = 30,
		text = "A decor piece for any room: cold, snow.",
	},
	{
		key = "Cosmetic_IcicleSign",
		name = "Icicle sign",
		cost = 60,
		text = "Your hotel sign, hung with icicles.",
	},
	{
		key = "Cosmetic_FairyLights",
		name = "Fairy lights",
		cost = 90,
		text = "Warm little lights strung across your lobby.",
	},
}

-- The shop of the season `id` (empty when it has none).
function Events.shop(id: string?): { ShopItem }
	return if id then Events.Shops[id] or {} else {}
end

return Events
