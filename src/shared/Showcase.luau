--!strict
--[[
	The showcase's rules (GDD A.11.4, §7, §8.3), pure so the specs can hold
	them. Built street only (A.11.4 decision 1, his call WAITING §2.38: the
	draft's recommendation, reversible): the hotels on this server, liked as
	before at their sign, listed in the Showcase panel with Visit.

	  - A like is for the PLAYER, once a day per visitor (as `SocialService`
	    always keyed it, by the owner's UserId), and counts only from a player
	    who has played `LikeAfterPlay` seconds that UTC day.
	  - Two counts: the LIFETIME count on the sign (never falls), and a WEEKLY
	    count that counts each liker once a week per liked player, so a ring
	    liking every day cannot multiply it. Each street's favourite is its
	    hotel with the most weekly likes.
	  - Milestones of lifetime likes give sign cosmetics (Cosmetics rows with
	    `likes`), never cash (decision 4).
	  - The daily request "Visit 3 hotels": walking into the lobby of another
	    player's hotel (a floor-1 tile it owns) counts once a day per owner.

	Every number is Constants.Showcase, PLACEHOLDER.
]]

local Constants = require(script.Parent.Constants)
local Cosmetics = require(script.Parent.Cosmetics)
local Grid = require(script.Parent.Grid)

local Showcase = {}

local DAY = 86400

-- The UTC day, as DailyService counts it.
function Showcase.day(t: number): number
	return t // DAY
end

-- The UTC week, counted from a Monday (1970-01-05), as LeaderboardService's weekly board.
function Showcase.week(t: number): number
	return (t - 4 * DAY) // (7 * DAY)
end

export type Week = { week: number, count: number, by: { [string]: boolean } }

-- A player's weekly count in `week` (0 once the week has turned).
function Showcase.weekly(rec: Week, week: number): number
	return if rec.week == week then rec.count else 0
end

--[[ Counts a like from `liker` into the liked player's weekly record: once
	per liker a week. Returns true when it counted. ]]
function Showcase.countWeekly(rec: Week, liker: string, week: number): boolean
	if rec.week ~= week then
		rec.week = week
		rec.count = 0
		rec.by = {}
	end
	if rec.by[liker] then
		return false
	end
	rec.by[liker] = true
	rec.count += 1
	return true
end

-- Whether a player who has played `seconds` today may like (Constants.Showcase.LikeAfterPlay).
function Showcase.canLike(seconds: number): boolean
	return seconds >= Constants.Showcase.LikeAfterPlay
end

-- The milestone cosmetics reached at `likes` lifetime likes, lowest first.
function Showcase.milestones(likes: number): { Cosmetics.Cosmetic }
	local out = {}
	for _, c in Cosmetics.List do
		if c.likes and likes >= c.likes then
			table.insert(out, c)
		end
	end
	table.sort(out, function(a, b)
		return (a.likes :: number) < (b.likes :: number)
	end)
	return out
end

-- The next milestone above `likes`, or nil past the last.
function Showcase.nextMilestone(likes: number): Cosmetics.Cosmetic?
	local best: Cosmetics.Cosmetic? = nil
	for _, c in Cosmetics.List do
		if c.likes and likes < c.likes and (best == nil or c.likes < (best.likes :: number)) then
			best = c
		end
	end
	return best
end

export type Entry = { key: string, street: number, week: number, likes: number }

--[[ Each street's favourite: the hotel with the most weekly likes (more than
	none); a tie goes to the larger lifetime count, then the lower key, so
	every server and every call agree. ]]
-- Whether `a` ranks above `b`: the favourite's order, so a sorted list starts with it (the Showcase panel).
function Showcase.before(a: Entry, b: Entry): boolean
	if a.week ~= b.week then
		return a.week > b.week
	end
	if a.likes ~= b.likes then
		return a.likes > b.likes
	end
	return a.key < b.key
end

function Showcase.favourites(entries: { Entry }): { [number]: string }
	local best: { [number]: Entry } = {}
	for _, e in entries do
		local b = best[e.street]
		if e.week > 0 and (b == nil or Showcase.before(e, b)) then
			best[e.street] = e
		end
	end
	local out = {}
	for street, e in best do
		out[street] = e.key
	end
	return out
end

--[[ Whether a plot-local point stands in the hotel's lobby: on floor 1, over a
	tile the hotel owns (`tiles` as the profile keeps them, Grid.tileKey as a
	string). ]]
function Showcase.inside(tiles: { [string]: boolean }, at: Vector3): boolean
	local G = Constants.Grid
	if at.Y < -2 or at.Y > G.FloorHeight then
		return false
	end
	local x, z = math.floor(at.X / G.CellSize), math.floor(at.Z / G.CellSize)
	return Grid.inBounds(x, z) and tiles[tostring(Grid.tileKey(1, x, z))] == true
end

return Showcase
