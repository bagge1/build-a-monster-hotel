--!strict
--[[
	How a guest picks a hotel (GDD §4.3):

		eligible = hotel has a vacant room of the guest's required type
		score    = ratingStars^1.5 × 1.0
		         + preferencesMatched × 0.6
		         + amenityBonus × 0.3
		         + pitchBonus
		         + newcomerBoost (Common/Uncommon guests only, low-rated hotels)
		score   *= random(0.9, 1.1)
		→ the highest-scoring eligible hotel; ties go to the nearest

	Pitching is "+15 % score toward their hotel": `pitchBonus` is 15 % of the
	score before it. "The tutorial weights Commons toward your hotel" (§11
	1:45): a Common the tutorial brought for a hotel (`tutorial`) adds
	`TutorialBoost` there, before the pitch, so the new player's pitch still
	counts. The Moon Tree's "+5 % bus score" (§6.5) multiplies the
	hotel's score. Pure; the random draws are passed in.
]]

local Constants = require(script.Parent.Constants)

local C = Constants.Scoring

export type Candidate = {
	id: any,
	eligible: boolean,
	rating: number,
	prefsMatched: number, -- in the best vacant room of the type
	amenityBonus: number, -- amenities on that room's floor
	pitched: boolean,
	busBonus: number?, -- the Moon Tree's, as a fraction
	distance: number,
	tutorial: boolean?, -- a Common the tutorial brought for this hotel (§11 1:45)
}

local Scoring = {}

function Scoring.score(c: Candidate, rarity: string, jitter: number): number
	local s = C.RatingWeight * c.rating ^ C.RatingPower
		+ C.PreferenceWeight * c.prefsMatched
		+ C.AmenityWeight * c.amenityBonus
	if (rarity == "Common" or rarity == "Uncommon") and c.rating <= C.NewcomerMaxRating then
		s += C.NewcomerBoost
	end
	if c.tutorial and rarity == "Common" then
		s += C.TutorialBoost
	end
	if c.pitched then
		s += s * C.PitchBonus
	end
	s *= 1 + (c.busBonus or 0)
	return s * jitter
end

--[[ The chosen candidate, or nil if none is eligible. `jitters[i]` is the
	draw in [0.9, 1.1] for `candidates[i]`. ]]
function Scoring.pick(candidates: { Candidate }, rarity: string, jitters: { number }): Candidate?
	local best: Candidate? = nil
	local bestScore = -math.huge
	for i, c in candidates do
		if c.eligible then
			local s = Scoring.score(c, rarity, jitters[i] or 1)
			if s > bestScore or (s == bestScore and best and c.distance < best.distance) then
				best, bestScore = c, s
			end
		end
	end
	return best
end

function Scoring.jitter(r: number): number
	return C.JitterLow + (C.JitterHigh - C.JitterLow) * r
end

return Scoring
