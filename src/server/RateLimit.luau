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

Players.PlayerRemoving:Connect(function(player)
	last[player] = nil
end)

return RateLimit
