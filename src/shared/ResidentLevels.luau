--!strict
--[[
	Residents level up, to a cap (GDD A.11.6, on its scrutinized
	recommendation; every number Constants.Residents.Level*, PLACEHOLDER).

	Each resident (the individual, not its species) fills an XP bar by
	working: `LevelXpPerMinute` a minute while the player plays, in the Wing
	or at a staff post alike, at any hotel of the chain (`learning`; one
	time-based scale, not per cash, so a loved Common levels as fast as a
	Mythic). A full bar waits for **Level up**,
	which costs `LevelPriceMinutes` × level minutes of that resident's own
	Wing rate (what it earns, or would earn, in the Wing at its level). A
	level gives Wing earnings and staff efficiency (decision 1a); perks stay
	flat. One cap for all (decision 2a). Levels go through a rebirth with the
	resident (decision 4a, his call WAITING §2.38: kept, reversible).

	A record keeps `level` and `xp`; nil reads as level 1 and no XP.
]]

local Constants = require(script.Parent.Constants)

local ResidentLevels = {}

local R = Constants.Residents

function ResidentLevels.level(rec: { level: number? }): number
	return math.clamp(rec.level or 1, 1, R.LevelCap)
end

function ResidentLevels.xp(rec: { xp: number? }): number
	return rec.xp or 0
end

-- The XP that fills the bar from `level` to the next (0 at the cap).
function ResidentLevels.need(level: number): number
	return if level >= R.LevelCap then 0 else R.LevelXpBar * level
end

-- What a level multiplies the resident's Wing earnings by.
function ResidentLevels.wing(level: number): number
	return 1 + R.LevelWing * (level - 1)
end

-- What a level multiplies the resident's staff efficiency by.
function ResidentLevels.efficiency(level: number): number
	return 1 + R.LevelEfficiency * (level - 1)
end

--[[ The XP after `seconds` at work: it fills the bar and stops there (the
	rest waits for Level up); nothing at the cap. ]]
function ResidentLevels.gain(level: number, xp: number, seconds: number): number
	local need = ResidentLevels.need(level)
	return math.min(need, xp + R.LevelXpPerMinute * seconds / 60)
end

-- Whether the bar is full and a level is left to take.
function ResidentLevels.ready(level: number, xp: number): boolean
	return level < R.LevelCap and xp >= ResidentLevels.need(level)
end

--[[ The price of the next level: `LevelPriceMinutes` × level minutes of the
	resident's Wing rate at its level (`wingRate`, $/s at level 1, before the
	level's multiplier). ]]
function ResidentLevels.price(level: number, wingRate: number): number
	return math.ceil(R.LevelPriceMinutes * level * 60 * wingRate * ResidentLevels.wing(level))
end

--[[ Whether a resident gains XP while the player plays (at `now`, os.time):
	in the Wing, or on staff at any hotel of the chain, the one played or
	another ("at the same rate in the Wing and at a staff post", WAITING
	§2.48, his yes 2026-10-26: a hotel not played still works); not in the
	Hunter Camp (`campUntil`). ]]
function ResidentLevels.learning(rec: { campUntil: number }, now: number): boolean
	return rec.campUntil <= now
end

return ResidentLevels
