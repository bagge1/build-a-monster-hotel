--!strict
--[[
	Rare decor sets and souvenirs (GDD A.11.3), the rules only: what a roll
	finds, the pity, a souvenir's milestones and the set bonus. Pure, specced
	(`tests/finds.spec.luau`); `FindService` runs them for each player.

	THE ROLLS. A happy stay of a Rare-or-better guest, and a defended Hunter
	Night, roll for a set piece of the played hotel's location. **A roll draws
	only among the location's unfound pieces**; after `Pity` rolls in a row
	without a find, the next gives the **next unfound piece** (the set's order,
	`Pieces.Sets`). Once every piece of the location is found, a hit (or the
	pity) is a duplicate, paid in cash. A location with no set rolls nothing.

	SOUVENIRS. One per species, by milestone: its first VIP contract or its
	`SouvenirMoveIns`-th move-in, whichever comes first. Found once.

	COPIES. Found once, then placed any number of times at its price
	(`Pieces` `cost`).

	THE SET BONUS. A room holding every piece of a set adds `SetBonus` to its
	Decor bar; it counts **once per set per hotel**: in the room with the
	lowest id holding the whole set (the oldest), copies elsewhere are looks
	and points only.

	All numbers are `Constants.Finds`, PLACEHOLDER (WAITING §2.38).
]]

local Constants = require(script.Parent.Constants)
local Pieces = require(script.Parent.Pieces)

local F = Constants.Finds

local Finds = {}

-- The profile's record: found decor ids (when, os.time), rolls missed in a row per location, move-ins per species.
export type Record = {
	found: { [string]: number },
	misses: { [string]: number },
	moveIns: { [string]: number },
}
export type Outcome = "Piece" | "Duplicate" | "Miss" | "None"

function Finds.newRecord(): Record
	return { found = {}, misses = {}, moveIns = {} }
end

-- Every set piece of a location, the sets in order, each set's pieces in the pity's order.
function Finds.pool(location: number): { string }
	local out = {}
	for _, s in Pieces.Sets do
		if s.location == location then
			for _, id in s.pieces do
				table.insert(out, id)
			end
		end
	end
	return out
end

-- The location's pieces not found yet, in the pity's order.
function Finds.unfound(rec: Record, location: number): { string }
	local out = {}
	for _, id in Finds.pool(location) do
		if rec.found[id] == nil then
			table.insert(out, id)
		end
	end
	return out
end

-- Whether a guest of this rarity rolls on a happy stay.
function Finds.rolls(rarity: string): boolean
	local at = table.find(Constants.RarityOrder, rarity :: any)
	local min = table.find(Constants.RarityOrder, F.MinRarity :: any)
	return at ~= nil and min ~= nil and at >= min
end

local function pick(list: { string }, rand: () -> number): string
	return list[math.clamp(math.floor(rand() * #list) + 1, 1, #list)]
end

--[[ One roll at `chance` for the location's pieces: what it found (a piece id
	for Piece and Duplicate) and the record's misses updated. A Piece is marked
	found at `now`. `rand` returns 0..1. ]]
function Finds.roll(
	rec: Record,
	location: number,
	chance: number,
	rand: () -> number,
	now: number
): (Outcome, string?)
	local pool = Finds.pool(location)
	if #pool == 0 then
		return "None", nil
	end
	local key = tostring(location)
	local before = rec.misses[key] or 0
	local hit = rand() < chance
	if not hit and before < F.Pity then
		rec.misses[key] = before + 1
		return "Miss", nil
	end
	rec.misses[key] = 0
	local unfound = Finds.unfound(rec, location)
	if #unfound == 0 then
		return "Duplicate", pick(pool, rand)
	end
	-- A hit draws among the unfound; the pity gives the next unfound.
	local id = if hit then pick(unfound, rand) else unfound[1]
	rec.found[id] = now
	return "Piece", id
end

--[[ A find already decided (an expedition's roll, A.11.2, with its own
	guarantee): a piece drawn among the location's unfound ones, or a
	duplicate once all are found. It leaves the rolls' pity alone, which
	counts the stays' and Hunter Nights' rolls only. ]]
function Finds.draw(
	rec: Record,
	location: number,
	rand: () -> number,
	now: number
): (Outcome, string?)
	local pool = Finds.pool(location)
	if #pool == 0 then
		return "None", nil
	end
	local unfound = Finds.unfound(rec, location)
	if #unfound == 0 then
		return "Duplicate", pick(pool, rand)
	end
	local id = pick(unfound, rand)
	rec.found[id] = now
	return "Piece", id
end

-- The decor id of a species' souvenir.
function Finds.souvenirId(species: string): string
	return `Souvenir_{species}`
end

-- Marks a species' souvenir found; true when it is new.
function Finds.giveSouvenir(rec: Record, species: string, now: number): boolean
	local id = Finds.souvenirId(species)
	if rec.found[id] ~= nil or not Pieces.decor(id) then
		return false
	end
	rec.found[id] = now
	return true
end

-- Counts a species' move-in; true when it is the one its souvenir is due on (and the souvenir is new).
function Finds.moveIn(rec: Record, species: string, now: number): boolean
	rec.moveIns[species] = (rec.moveIns[species] or 0) + 1
	if rec.moveIns[species] < F.SouvenirMoveIns then
		return false
	end
	return Finds.giveSouvenir(rec, species, now)
end

-- How many of each set's pieces stand among `items` (decor ids); only sets with one or more.
function Finds.progress(items: { string }): { [string]: number }
	local have: { [string]: boolean } = {}
	for _, id in items do
		have[id] = true
	end
	local out = {}
	for _, s in Pieces.Sets do
		local n = 0
		for _, id in s.pieces do
			if have[id] then
				n += 1
			end
		end
		if n > 0 then
			out[s.id] = n
		end
	end
	return out
end

-- The sets wholly present among `items`.
function Finds.complete(items: { string }): { string }
	local out = {}
	for setId, n in Finds.progress(items) do
		if n >= #Pieces.SetById[setId].pieces then
			table.insert(out, setId)
		end
	end
	table.sort(out)
	return out
end

local function older(a: string, b: string): boolean
	local na, nb = tonumber(a), tonumber(b)
	if na and nb and na ~= nb then
		return na < nb
	end
	return a < b
end

--[[ The one room per set that has its bonus: of the rooms (id -> the decor
	ids standing in it) holding the whole set, the oldest (lowest id). ]]
function Finds.bonusRooms(rooms: { [string]: { string } }): { [string]: string }
	local out: { [string]: string } = {}
	for roomId, items in rooms do
		for _, setId in Finds.complete(items) do
			local held = out[setId]
			if not held or older(roomId, held) then
				out[setId] = roomId
			end
		end
	end
	return out
end

-- The Decor bar with the set bonus of `sets` (the sets this room holds the bonus of), 0..1.
function Finds.withBonus(decor: number, sets: number): number
	return math.clamp(decor + F.SetBonus * sets, 0, 1)
end

return Finds
