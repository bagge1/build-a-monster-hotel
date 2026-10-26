--!strict
--[[
	A per-player cooldown for remotes a client could send every frame (GDD
	§13.2: every remote rate-limited). `Net.on` asks it for every remote that
	declares a `rate`; a system may also ask it directly.

	`RateLimit.allow(player, key, seconds)` is true at most once per `seconds`
	for each player and key, and stamps the time when it is. A refused call is
	not stamped, so a client hammering a remote is refused until the cooldown
	from its last accepted call has passed. Forgotten when the player leaves.

	Lifted from Sector Omega's (D:\Roblox\playbook\PATTERNS.md, "Safety").
]]

local Players = game:GetService("Players")

local RateLimit = {}

local last: { [Player]: { [string]: number } } = {}

function RateLimit.allow(player: Player, key: string, seconds: number): boolean
	local now = os.clock()
	local mine = last[player]
	if not mine then
		mine = {}
		last[player] = mine
	end
	local at = mine[key]
	if at and now - at < seconds then
		return false
	end
	mine[key] = now
	return true
end

--[[ A budget shared by several remotes (2026-10-26 review: each build remote
	had its own cooldown, so a client firing all of them at once loaded the
	server for everyone). `capacity` calls at once, refilled at `perSecond`: a
	burst a person makes (a click that sends two) passes, a stream does not. ]]
local buckets: { [Player]: { [string]: { tokens: number, at: number } } } = {}

function RateLimit.bucket(player: Player, key: string, capacity: number, perSecond: number): boolean
	local now = os.clock()
	local mine = buckets[player]
	if not mine then
		mine = {}
		buckets[player] = mine
	end
	local b = mine[key]
	if not b then
		b = { tokens = capacity, at = now }
		mine[key] = b
	end
	b.tokens = math.min(capacity, b.tokens + (now - b.at) * perSecond)
	b.at = now
	if b.tokens < 1 then
		return false
	end
	b.tokens -= 1
	return true
end

Players.PlayerRemoving:Connect(function(player)
	last[player] = nil
	buckets[player] = nil
end)

return RateLimit
