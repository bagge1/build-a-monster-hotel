--!strict
--[[
	The hotel rating (GDD §5.3, Appendix A.4): 1–5 stars in half steps, from
	five categories of 0–100 and a rolling average of the last 30 reviews.
	Pure: the server publishes it, the sign and the panel show its breakdown,
	the specs hold it to its rules.
]]

local Constants = require(script.Parent.Constants)

local R = Constants.Rating

export type Inputs = {
	roomTiers: { number }, -- each room's tier
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

function Rating.categories(i: Inputs): Categories
	local tierMean = 0
	for _, t in i.roomTiers do
		tierMean += t
	end
	tierMean = if #i.roomTiers > 0 then tierMean / #i.roomTiers else 0
	local comfort = math.min(100, tierMean * R.ComfortPerTier) * 0.6 + 40 * i.prefsShare
	-- A hotel nobody has stayed in has earned no Service and no Cleanliness yet.
	local service = if i.checkIns > 0
		then math.clamp(100 - i.meanWait * R.ServiceWaitPerPoint, 0, 100) * 0.6 + 40 * i.requestShare
		else 0
	local cleanliness = if i.rooms > 0 then 100 * (1 - i.dirtyRooms / i.rooms) else 0
	local fun = math.min(100, i.amenities * R.FunPerAmenity + i.entertainers * R.FunPerEntertainer)
	local style = math.min(100, i.decor * R.StylePerDecor + i.roomTypes * R.StylePerRoomType)
	return {
		Comfort = math.clamp(comfort, 0, 100),
		Service = math.clamp(service, 0, 100),
		Cleanliness = math.clamp(cleanliness, 0, 100),
		Fun = fun,
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

-- Keeps the last `Constants.Stay.ReviewsKept` reviews, the newest last.
function Rating.addReview(reviews: { number }, stars: number)
	table.insert(reviews, stars)
	while #reviews > Constants.Stay.ReviewsKept do
		table.remove(reviews, 1)
	end
end

return Rating
