--!strict
--[[
	Experience notifications (GDD §9 "Return prompts", Appendix A.9; his picks,
	2026-10-20), sent by the game's own servers through Open Cloud's
	CreateUserNotification (HttpService, the API key in the experience's
	Secrets as `OpenCloudKey`; no outside server):

	  - TILL FULL: "Your residents' till is full", when the offline cap has run
	    out since the player left, if their residents earn offline at all.
	    Cancelled when they come back first.
	  - FULL MOON: "Full Moon tonight", Saturday 16:00 UTC, to every player seen
	    in the last 7 days, four hours before the Full Moon Hunt.
	  - EXPEDITION BACK (GDD A.11.2 decision 6b): when a trip of
	    `Constants.Expeditions.NotifyMin` or longer comes home while the player
	    is away. Its string is August's to write in Creator Hub (WAITING
	    §2.38); the one below is a PLACEHOLDER. Cancelled when they come back
	    first. It shares Roblox's one a day with the two above.

	Both wait in a MemoryStore sorted map, the due time its sort key, and every
	running server sends what is due once a minute. A server claims an entry
	by pushing its due time on by a lease before it sends, so two servers
	never send the same one; a failed send comes due again when the lease
	runs out, up to `TRIES` times. A notification due while no server runs
	goes out when the next one starts.

	Roblox delivers at most one a day per player, and only to opted-in players
	of 13 and over (the opt-in: `LivePanels`). Nothing here can tell who opted
	in; a send to someone who did not is simply not delivered.

	Not set up yet (WAITING §3.3): until a message's id is filled in below, the
	key is in Secrets and HTTP requests are allowed, a send is only logged.
	Studio uses its own maps, so a playtest never touches the live queue.
]]

local HttpService = game:GetService("HttpService")
local MemoryStoreService = game:GetService("MemoryStoreService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Events = require(ReplicatedStorage.Shared.Events)
local Expeditions = require(ReplicatedStorage.Shared.Expeditions)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local ResidentService = require(ServerScriptService.Server.ResidentService)
local EventService = require(ServerScriptService.Server.EventService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local NotifyService = {}

export type Kind = "TillFull" | "FullMoon" | "ExpeditionBack"

-- Each notification string's asset id, from Creator Hub (Engagement → Notifications); 0 until made.
NotifyService.Messages = {
	TillFull = 0, -- "Your residents' till is full"
	FullMoon = 0, -- "Full Moon tonight"
	-- PLACEHOLDER text, his to write (A.11.2, WAITING §2.38): "[PLACEHOLDER] Your residents are back from their expedition!"
	ExpeditionBack = 0,
} :: { [Kind]: number }

local SECRET = "OpenCloudKey"
local TICK = 60 -- seconds between looks at the queue
local LEASE = 10 * 60 -- a claimed entry's due time is pushed on by this
local TRIES = 3
local PAGE = 50 -- entries sent per tick at most
local RECENT_FOR = 7 * 86400 -- "seen in the last 7 days"
local FULL_MOON_HOUR = 16 -- UTC, Saturday (a night draft)
local MAX_EXPIRY = 45 * 86400 -- MemoryStore's longest

local suffix = if RunService:IsStudio() then "_Studio" else ""
local queue = MemoryStoreService:GetSortedMap("Notify" .. suffix)
local recent = MemoryStoreService:GetSortedMap("NotifyRecent" .. suffix)
local broadcasts = MemoryStoreService:GetSortedMap("NotifyBroadcast" .. suffix)

local warned: { [string]: boolean } = {}
local function warnOnce(key: string, message: string)
	if not warned[key] then
		warned[key] = true
		warn(`[notify] {message}`)
	end
end

local function key(kind: Kind, userId: number): string
	return `{kind}_{userId}`
end

local function expiry(due: number): number
	return math.clamp(math.ceil(due - os.time()) + 2 * 86400, 60, MAX_EXPIRY)
end

-- Puts a notification for `userId` in the queue, due at `due` (replacing one of the same kind).
function NotifyService.queue(kind: Kind, userId: number, due: number)
	pcall(function()
		queue:SetAsync(key(kind, userId), { u = userId, k = kind, n = 0 }, expiry(due), due)
	end)
end

function NotifyService.cancel(kind: Kind, userId: number)
	pcall(function()
		queue:RemoveAsync(key(kind, userId))
	end)
end

-- The key, or nil while sending is not set up (the reason warned once).
local function apiKey(): any
	if not HttpService.HttpEnabled then
		warnOnce("http", "HTTP requests are off (Experience Settings → Security); only logging")
		return nil
	end
	local ok, secret = pcall(function()
		return HttpService:GetSecret(SECRET)
	end)
	if not ok then
		warnOnce("secret", `no secret {SECRET} in the experience's Secrets; only logging`)
		return nil
	end
	return secret
end

--[[ One send. Returns "sent", "retry" (worth trying again later) or "drop".
	Logged instead while its message id or the key is missing. ]]
local function send(kind: Kind, userId: number): string
	local messageId = NotifyService.Messages[kind]
	local secret = if messageId ~= 0 then apiKey() else nil
	if not secret then
		print(`[notify] would send {kind} to {userId} (not set up)`)
		return "drop"
	end
	local ok, response = pcall(function()
		return HttpService:RequestAsync({
			Url = `https://apis.roblox.com/cloud/v2/users/{userId}/notifications`,
			Method = "POST",
			Headers = { ["x-api-key"] = secret, ["Content-Type"] = "application/json" },
			Body = HttpService:JSONEncode({
				source = { universe = `universes/{game.GameId}` },
				payload = { message_id = tostring(messageId), type = "MOMENT" },
				analytics_data = { category = kind },
			}),
		})
	end)
	if not ok then
		warn(`[notify] {kind} to {userId}: {response}`)
		return "retry"
	end
	local r = response :: any
	if r.Success then
		return "sent"
	end
	if r.StatusCode == 429 or r.StatusCode >= 500 then
		return "retry"
	end
	-- Not opted in, under 13, today's one already sent: nothing to try again.
	warn(`[notify] {kind} to {userId}: {r.StatusCode} {string.sub(r.Body or "", 1, 200)}`)
	return "drop"
end

-- Claims entry `k` (nil if another server has it or it is gone), its lease taken.
local function claim(k: string, now: number): any
	local claimed = nil
	pcall(function()
		queue:UpdateAsync(k, function(value: any, sortKey: any)
			if value == nil or (tonumber(sortKey) or 0) > now then
				return nil -- gone, or another server's lease
			end
			value.n = (value.n or 0) + 1
			claimed = value
			return value, now + LEASE
		end, expiry(now + LEASE))
	end)
	return claimed
end

-- Sends what is due. Returns how many were looked at.
function NotifyService.tick(): number
	local now = os.time()
	local ok, items = pcall(function()
		return queue:GetRangeAsync(Enum.SortDirection.Ascending, PAGE, nil, { sortKey = now })
	end)
	if not ok then
		return 0
	end
	for _, item in items :: any do
		local value = claim(item.key, now)
		if value then
			local result = if Players:GetPlayerByUserId(value.u)
				then "drop"
				else send(value.k, value.u)
			if result ~= "retry" or value.n >= TRIES then
				pcall(function()
					queue:RemoveAsync(item.key)
				end)
			end
		end
	end
	return #(items :: any)
end

--[[ The Saturday broadcast: the first server past 16:00 UTC (before the
	Hunt) claims the day's broadcast and queues a Full Moon for everyone in
	`recent`, page by page, keeping its place in the claim so another server
	carries on if it goes down. `force` (Studio) ignores the clock. ]]
function NotifyService.broadcastFullMoon(force: boolean?): number
	local now = EventService.now()
	local hunt = Events.huntStart(now)
	if not force and not (hunt and now >= hunt - (20 - FULL_MOON_HOUR) * 3600 and now < hunt) then
		return 0
	end
	local day = os.date("!%Y-%m-%d", now)
	local queued = 0
	while true do
		-- Take (or keep) the day's claim; its value is where the last page ended.
		local cursor = nil
		local mine = false
		pcall(function()
			broadcasts:UpdateAsync(`FullMoon_{day}`, function(value: any, sortKey: any)
				local t = os.time()
				if
					value
					and (value.done or ((tonumber(sortKey) or 0) > t and value.by ~= game.JobId))
				then
					return nil -- finished, or another server is on it
				end
				value = value or { by = game.JobId }
				value.by = game.JobId
				cursor = value.after
				mine = true
				return value, t + LEASE
			end, 2 * 86400)
		end)
		if not mine then
			return queued
		end
		local ok, page = pcall(function()
			return recent:GetRangeAsync(
				Enum.SortDirection.Ascending,
				200,
				if cursor then { key = cursor.key, sortKey = cursor.sortKey } else nil,
				nil
			)
		end)
		if not ok then
			return queued
		end
		local seen = os.time() - RECENT_FOR
		for _, item in page :: any do
			if (tonumber(item.sortKey) or 0) >= seen then
				NotifyService.queue("FullMoon", item.value, os.time())
				queued += 1
			end
		end
		local last = (page :: any)[#(page :: any)]
		local done = #(page :: any) < 200
		pcall(function()
			broadcasts:UpdateAsync(`FullMoon_{day}`, function(value: any)
				value = value or { by = game.JobId }
				if last then
					value.after = { key = last.key, sortKey = last.sortKey }
				end
				value.done = done
				return value, os.time() + LEASE
			end, 2 * 86400)
		end)
		if done then
			return queued
		end
	end
end

-- Marks `userId` as seen now, for the broadcasts.
local function seen(userId: number)
	pcall(function()
		recent:SetAsync(tostring(userId), userId, RECENT_FOR, os.time())
	end)
end

function NotifyService.Init() end

function NotifyService.Start()
	PlayerData.onLoaded(function(player)
		task.spawn(function()
			NotifyService.cancel("TillFull", player.UserId)
			NotifyService.cancel("FullMoon", player.UserId)
			NotifyService.cancel("ExpeditionBack", player.UserId)
			seen(player.UserId)
		end)
	end)
	PlayerData.onRelease(function(player, data)
		-- Worked out now, while the profile and the player's attributes are here.
		local earns = ResidentService.rate(player, data) > 0
		local due = os.time() + ResidentService.offlineCap(player, data)
		local userId = player.UserId
		-- A trip still out (A.11.2 decision 6b: of NotifyMin or longer): "back" at its end.
		local trip = data.expedition and data.expedition.trip
		local tripDue = if trip
				and trip.length >= Constants.Expeditions.NotifyMin
				and not Expeditions.back(trip, os.time())
			then trip.ends
			else nil
		task.spawn(function()
			seen(userId)
			if earns then
				NotifyService.queue("TillFull", userId, due)
			end
			if tripDue then
				NotifyService.queue("ExpeditionBack", userId, tripDue)
			end
		end)
	end)
	task.spawn(function()
		task.wait(math.random() * TICK) -- servers out of step with each other
		while true do
			pcall(NotifyService.broadcastFullMoon)
			pcall(NotifyService.tick)
			task.wait(TICK)
		end
	end)

	-- `notify tick` | `notify queue <TillFull|FullMoon|ExpeditionBack> [seconds] [userId]` |
	-- `notify fullmoon` (the broadcast now) | `notify list` (the queue)
	DevGrant.register("notify", function(player, args)
		local what = args[1] or "list"
		if what == "tick" then
			return `looked at {NotifyService.tick()}`
		elseif what == "queue" then
			local kind = (args[2] or "TillFull") :: Kind
			local userId = tonumber(args[4]) or player.UserId
			NotifyService.queue(kind, userId, os.time() + (tonumber(args[3]) or 0))
			return `queued {kind} for {userId}`
		elseif what == "fullmoon" then
			return `queued {NotifyService.broadcastFullMoon(true)}`
		end
		local items = queue:GetRangeAsync(Enum.SortDirection.Ascending, 20)
		local lines = {}
		for _, item in items do
			table.insert(lines, `{item.key} due {(tonumber(item.sortKey) or 0) - os.time()}s`)
		end
		return if #lines > 0 then table.concat(lines, "; ") else "empty"
	end)
end

return NotifyService
