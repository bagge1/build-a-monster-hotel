--!strict
--[[
	A hotel's income multiplier (GDD §6.2, "bonus stacking"): bonuses add
	within a category and multiply across categories (`Economy.incomeMultiplier`).

	Systems that give a bonus register a provider here rather than being
	required by whoever pays: the Moon Tree's cash nodes and the Book's
	families add to `permanent`; the friend bonus (§7) and timed boosts
	(§10.2) are their own categories. Every payer (guests, tips, residents)
	asks `Income.multiplier(player)`.
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

function Income.multiplier(player: Player): number
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
	local m = Economy.incomeMultiplier({ permanent = p, friends = withFriends, boost = boost })
	player:SetAttribute("IncomeMultiplier", m)
	return m
end

function Income.Init() end
function Income.Start() end

return Income
