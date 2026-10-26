--!strict
--[[
	The hotel rating (GDD §5.3, Appendix A.4): 1–5 stars in half steps, from
	five categories of 0–100 and a rolling average of the last 30 reviews.
	Pure: the server publishes it, the sign and the panel show its breakdown,
	the specs hold it to its rules.
]]

local Constants = require(script.Parent.Constants)
local Rooms = require(script.Parent.Rooms)

local R = Constants.Rating

export type Inputs = {
	roomBars: { Rooms.Bars }, -- each READY room's three bars (GDD A.12)
	prefsShare: number, -- 0..1: preferences matched in recent stays
	meanWait: number, -- seconds at the desk, recent check-ins
	checkIns: number, -- how many recent check-ins meanWait is over (none: no Service yet)
	requestShare: number, -- 0..1: requests fulfilled of those asked, recent
	rooms: number,
	dirtyRooms: number,
	amenities: number,
	entertainers: number,
	decor: number,
	roomTypes: number,
	perks: { [string]: number }?, -- residents' rating perks: Service, Fun, Cleanliness points (Perks)
	-- Staff coverage (§5.3): each role's summed efficiency on duty (Appendix A.5).
	frontDesk: number?,
	roomService: number?,
	housekeeping: number?,
	onTimeShare: number?, -- 0..1: recent cleanings within CleanOnTime, rooms overdue now counting late
}

export type Categories = {
	Comfort: number,
	Service: number,
	Cleanliness: number,
	Fun: number,
	Style: number,
}

local Rating = {}

Rating.Order = { "Comfort", "Service", "Cleanliness", "Fun", "Style" }

-- A role's coverage (§5.3 "staff coverage"), 0..1: its staff's summed
-- efficiency over what the hotel needs, full at or above the need.
function Rating.coverage(efficiency: number, need: number): number
	return if need > 0 then math.clamp(efficiency / need, 0, 1) else 0
end

function Rating.categories(i: Inputs): Categories
	-- Comfort's room part (A.12, his "no room deducts points"): what each ready
	-- room's bars add, summed to its cap, so a new room never lowers it; its
	-- preferences part is as before.
	local comfort = Rooms.comfortPoints(i.roomBars) + 40 * i.prefsShare
	-- A hotel nobody has stayed in has earned no Service and no Cleanliness yet.
	local service = if i.checkIns > 0
		then math.clamp(100 - i.meanWait * R.ServiceWaitPerPoint, 0, 100) * 0.6 + 40 * i.requestShare
		else 0
	local cleanliness = if i.rooms > 0 then 100 * (1 - i.dirtyRooms / i.rooms) else 0
	-- Staff coverage and cleaning on time (§5.3, Appendix A.4): points on top,
	-- never taken away, so more staff or quicker cleaning never lowers a category.
	local roomsNeed = math.max(1, i.rooms / R.RoomsPerStaff)
	if i.checkIns > 0 then
		service += R.ServicePerDeskCoverage * Rating.coverage(i.frontDesk or 0, R.DesksCovered) + R.ServicePerRoomServiceCoverage * Rating.coverage(
			i.roomService or 0,
			roomsNeed
		)
	end
	if i.rooms > 0 then
		cleanliness += R.CleanPerHousekeepingCoverage * Rating.coverage(
			i.housekeeping or 0,
			roomsNeed
		) + R.CleanPerOnTime * math.clamp(i.onTimeShare or 0, 0, 1)
	end
	local fun = math.min(100, i.amenities * R.FunPerAmenity + i.entertainers * R.FunPerEntertainer)
	local style = math.min(100, i.decor * R.StylePerDecor + i.roomTypes * R.StylePerRoomType)
	-- Residents' perks under the same gates as the staff (A.4: no Service before a
	-- stay, no Cleanliness without rooms; 2026-10-26 review: they were added ungated).
	local perks = i.perks or {}
	if i.checkIns > 0 then
		service += perks.Service or 0
	end
	if i.rooms > 0 then
		cleanliness += perks.Cleanliness or 0
	end
	return {
		Comfort = math.clamp(comfort, 0, 100),
		Service = math.clamp(service, 0, 100),
		Cleanliness = math.clamp(cleanliness, 0, 100),
		Fun = math.clamp(fun + (perks.Fun or 0), 0, 100),
		Style = style,
	}
end

function Rating.roundHalf(x: number): number
	return math.floor(x * 2 + 0.5) / 2
end

-- The stars, from the categories and the reviews kept (1–5 each).
function Rating.stars(c: Categories, reviews: { number }): number
	local mean = (c.Comfort + c.Service + c.Cleanliness + c.Fun + c.Style) / 5
	local fromCategories = R.Min + (R.Max - R.Min) * (mean / 100) ^ R.CategoryCurve
	local stars = fromCategories
	if #reviews > 0 then
		local sum = 0
		for _, r in reviews do
			sum += r
		end
		stars = (fromCategories + sum / #reviews) / 2
	end
	return math.clamp(Rating.roundHalf(stars), R.Min, R.Max)
end

--[[ The daily request "Reach {n}★" (A.9: "reach the next whole star"): the
	next whole star above `rating`, or nil at the top, where there is none to
	reach (so the request is never drawn there, met as it is drawn). ]]
function Rating.nextStar(rating: number): number?
	local n = math.floor(rating) + 1
	return if n <= R.Max then n else nil
end

--[[ How far that request has come: `target` once the hotel played
	(`playedAt`) reaches it, else its whole stars, and nothing at another
	hotel of the chain than the one it was drawn for (`drawnAt`; nil for a
	request drawn before it was kept, counted anywhere), since its target is
	that hotel's next star. ]]
function Rating.towardStar(
	target: number,
	rating: number,
	drawnAt: number?,
	playedAt: number
): number
	if drawnAt ~= nil and drawnAt ~= playedAt then
		return 0
	end
	return if rating >= target then target else math.floor(rating)
end

-- Keeps the last `Constants.Stay.ReviewsKept` reviews, the newest last.
function Rating.addReview(reviews: { number }, stars: number)
	table.insert(reviews, stars)
	while #reviews > Constants.Stay.ReviewsKept do
		table.remove(reviews, 1)
	end
end

return Rating
