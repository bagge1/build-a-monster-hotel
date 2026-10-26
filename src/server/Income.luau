--!strict
--[[
	A hotel's income multiplier (GDD §6.2, "bonus stacking"): bonuses add
	within a category and multiply across categories (`Economy.incomeMultiplier`).

	Systems that give a bonus register a provider here rather than being
	required by whoever pays: the Moon Tree's cash nodes and the Book's
	families add to `permanent`; the friend bonus (§7) and timed boosts
	(§10.2) are their own categories. Every payer (guests, tips, residents)
	asks `Income.multiplier(player)`; the residents' offline earnings ask it
	with `offline`, which leaves the friend bonus (WAITING §2.48) and the
	timed boost (it counts down in play time, A.9) out.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Economy = require(ReplicatedStorage.Shared.Economy)

local Income = {}

local permanent: { (Player) -> number } = {}
local boosts: { (Player) -> number } = {}
local friends: ((Player) -> boolean)? = nil

-- A provider of a permanent bonus, as a fraction (0.1 is +10 %).
function Income.addPermanent(provider: (Player) -> number)
	table.insert(permanent, provider)
end

-- A provider of a timed boost's multiplier (1 when none).
function Income.addBoost(provider: (Player) -> number)
	table.insert(boosts, provider)
end

function Income.setFriends(provider: (Player) -> boolean)
	friends = provider
end

--[[ The player's income multiplier now; `offline` for what pays the time it was away
	(§4.6): without the friend bonus or a timed boost (`Economy.offlineBonuses`). ]]
function Income.multiplier(player: Player, offline: boolean?): number
	local p = 0
	for _, f in permanent do
		local ok, v = pcall(f, player)
		if ok and typeof(v) == "number" then
			p += v
		end
	end
	local boost = 1
	for _, f in boosts do
		local ok, v = pcall(f, player)
		if ok and typeof(v) == "number" then
			boost = math.max(boost, v)
		end
	end
	local withFriends = false
	if friends then
		local ok, v = pcall(friends, player)
		withFriends = ok and v == true
	end
	local bonuses: Economy.Bonuses = { permanent = p, friends = withFriends, boost = boost }
	if offline then
		-- Not published: the HUD's multiplier is the one paying now.
		return Economy.incomeMultiplier(Economy.offlineBonuses(bonuses))
	end
	local m = Economy.incomeMultiplier(bonuses)
	player:SetAttribute("IncomeMultiplier", m)
	return m
end

function Income.Init() end
function Income.Start() end

return Income
