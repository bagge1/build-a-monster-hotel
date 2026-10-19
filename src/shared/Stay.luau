--!strict
--[[
	A guest's stay (GDD §4.4, Appendix A.3), as pure functions: how happy it
	is, what it tips, the review it leaves, and which preferences a room
	matches. The server's GuestService runs a stay on these; the specs hold
	them to their rules.
]]

local Constants = require(script.Parent.Constants)

local S = Constants.Stay

local Stay = {}

export type Inputs = {
	prefsMatched: number,
	tier: number,
	amenities: number, -- amenities on the room's floor
	requestsPlayer: number,
	requestsStaff: number,
	requestsMissed: number,
	deskWait: number, -- seconds waited at the desk
}

function Stay.waitPenalty(seconds: number): number
	local over = math.max(0, seconds - S.WaitFree)
	return math.min(S.WaitMaxPenalty, math.floor(over / S.WaitPerPoint))
end

-- Satisfaction, 0–100 (§4.4: preferences, room tier, requests, amenities; Appendix A.3).
function Stay.satisfaction(i: Inputs): number
	local s = S.SatisfactionBase
		+ S.SatisfactionPerPreference * i.prefsMatched
		+ S.SatisfactionPerTier * (i.tier - 1)
		+ math.min(S.SatisfactionAmenityMax, S.SatisfactionPerAmenity * i.amenities)
		+ S.SatisfactionRequestPlayer * i.requestsPlayer
		+ S.SatisfactionRequestStaff * i.requestsStaff
		+ S.SatisfactionRequestMissed * i.requestsMissed
		- Stay.waitPenalty(i.deskWait)
	return math.clamp(s, 0, 100)
end

function Stay.isHappy(satisfaction: number): boolean
	return satisfaction >= S.Happy
end

-- The check-out tip: pay × stay × satisfaction/100 × TipFraction.
function Stay.tip(payRate: number, stay: number, satisfaction: number): number
	return math.floor(payRate * stay * (satisfaction / 100) * S.TipFraction)
end

-- The review, 1–5 stars.
function Stay.review(satisfaction: number): number
	return math.clamp(1 + math.floor(satisfaction / 25), 1, 5)
end

-- How many of `prefs` the set of `tags` holds.
function Stay.matched(prefs: { string }, tags: { [string]: boolean }): number
	local n = 0
	for _, p in prefs do
		if tags[p] then
			n += 1
		end
	end
	return n
end

return Stay
