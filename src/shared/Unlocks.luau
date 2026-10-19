--!strict
--[[
	When a piece can be built (GDD §5.2, §6.4), as a pure function, so the
	build panel shows the same answer the server enforces.

	A piece of the hotel's own location is buildable once its `unlock` is met:
	rooms owned, a floor reached, a rating, a Legendary resident. Once met it
	stays unlocked (`unlocked`), and an unlocked piece stays buildable after a
	rebirth at its normal price (§6.4: "every room type already unlocked").
	The tutorial can unlock a piece early (§11, Appendix A.7).
]]

local Pieces = require(script.Parent.Pieces)

export type Context = {
	location: number,
	unlocked: { [string]: boolean },
	rating: number,
	rooms: number, -- rooms owned (not amenities)
	floors: number,
	legendaryResident: boolean,
	tutorial: { [string]: boolean }?,
}

local Unlocks = {}

-- Whether its condition is met now, ignoring what was unlocked before; and if not, why.
function Unlocks.met(id: string, c: Context): (boolean, string?)
	local piece = Pieces.get(id)
	if not piece then
		return false, "Unknown"
	end
	if piece.location ~= 0 and piece.location ~= c.location then
		return false, "Location"
	end
	local u = piece.unlock
	if not u then
		return true, nil
	end
	if u.rooms and c.rooms < u.rooms then
		return false, `Own {u.rooms} rooms`
	end
	if u.floor and c.floors < u.floor then
		return false, `Build floor {u.floor}`
	end
	if u.rating and c.rating < u.rating then
		return false, `Reach {u.rating}★`
	end
	if u.legendaryResident and not c.legendaryResident then
		return false, "A Legendary resident"
	end
	return true, nil
end

-- Whether it can be built now: unlocked before, met now, or unlocked by the tutorial.
function Unlocks.buildable(id: string, c: Context): (boolean, string?)
	if c.unlocked[id] or (c.tutorial and c.tutorial[id]) then
		return true, nil
	end
	return Unlocks.met(id, c)
end

return Unlocks
