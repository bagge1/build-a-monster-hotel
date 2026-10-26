--[[
	The night's guard (night brief 2026-10-26, "Hur buggar jagas"): a Script
	pasted into a RUNNING server (never in src/), which checks the game's rules
	every 0.5 s and records each breach with the server time.

	Paste its source into `Instance.new("Script")` from a Server execute_luau
	and parent it to ServerScriptService. It shares the game's modules (a
	Script's require cache, not the plugin's). Read the record from
	`ServerStorage._Guard`: `Log` (StringValue, newest last), attributes
	`Breaches`, `Ticks`, `Parts` (the last count).

	What it checks:
	- a guest walking to or staying in a room that is not ready, for over 1 s
	  (a change's `sync` sends it back at once; a breach outlasting that is a bug);
	- NaN, infinity or a negative value in cash, till, shards, a stat;
	- a resident counted twice (two Residents folders for one owner, or a
	  resident both away and on a staff slot);
	- profile keys that do not parse (walls, tiles, windows, rooms' cells);
	- instances growing while nothing is built (Workspace and ReplicatedStorage,
	  counted every 30 s);
	- every error or warning in the server's output.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local ServerScriptService = game:GetService("ServerScriptService")
local LogService = game:GetService("LogService")

local Server = ServerScriptService.Server
local PlayerData = require(Server.PlayerData)
local GuestService = require(Server.GuestService)
local PlotService = require(Server.PlotService)
local Rooms = require(ReplicatedStorage.Shared.Rooms)

local old = ServerStorage:FindFirstChild("_Guard")
if old then
	old:Destroy()
end
local box = Instance.new("Folder")
box.Name = "_Guard"
local logValue = Instance.new("StringValue")
logValue.Name = "Log"
logValue.Parent = box
box:SetAttribute("Breaches", 0)
box:SetAttribute("Ticks", 0)
box.Parent = ServerStorage

local lines = {}
local seen: { [string]: number } = {} -- a breach's key -> times logged
local function breach(key: string, text: string)
	local n = (seen[key] or 0) + 1
	seen[key] = n
	if n > 3 then
		return -- the same breach logged three times is enough
	end
	box:SetAttribute("Breaches", (box:GetAttribute("Breaches") or 0) + 1)
	table.insert(lines, string.format("%.1f %s", workspace:GetServerTimeNow() % 100000, text))
	while #lines > 200 do
		table.remove(lines, 1)
	end
	logValue.Value = table.concat(lines, "\n")
end

LogService.MessageOut:Connect(function(message, kind)
	if kind == Enum.MessageType.MessageError or kind == Enum.MessageType.MessageWarning then
		if string.find(message, "_Guard", 1, true) then
			return
		end
		breach("log:" .. string.sub(message, 1, 80), (if kind == Enum.MessageType.MessageError then "ERROR " else "WARN ") .. string.sub(message, 1, 300))
	end
end)

local function bad(n: any): boolean
	return typeof(n) ~= "number" or n ~= n or n == math.huge or n == -math.huge
end

local unreadySince: { [number]: number } = {}

local function checkGuests()
	local ready: { [Player]: Rooms.Readiness } = {}
	local now = os.clock()
	local still: { [number]: boolean } = {}
	for id, g in GuestService.all() do
		local owner = g.owner
		if owner and g.room and (g.state == "ToRoom" or g.state == "InRoom") then
			local data = PlayerData.get(owner)
			if data and data.rooms and data.rooms[g.room] then
				local r = ready[owner]
				if not r then
					local ok, res = pcall(Rooms.readiness, PlotService.world(data))
					r = if ok then res else {}
					ready[owner] = r
				end
				local entry = r[g.room]
				if entry and not entry.ok then
					still[id] = true
					unreadySince[id] = unreadySince[id] or now
					if now - unreadySince[id] > 1 then
						breach(
							`unready:{id}:{g.room}`,
							`guest {id} ({g.species}, {g.state}) in room {g.room} of {owner.Name}, not ready: {table.concat(entry.missing or {}, ",")}`
						)
					end
				end
			elseif data and g.room and string.sub(g.room, 1, 1) == "R" then
				breach(`gone:{id}:{g.room}`, `guest {id} ({g.state}) booked into room {g.room} that {owner.Name}'s profile lacks`)
			end
		end
	end
	for id in unreadySince do
		if not still[id] then
			unreadySince[id] = nil
		end
	end
end

local function checkData(player: Player, data: any)
	for _, field in { "cash", "till", "shards" } do
		local v = data[field]
		if bad(v) or v < 0 then
			breach(`num:{player.UserId}:{field}`, `{player.Name} {field} = {tostring(v)}`)
		end
	end
	for k, v in data.stats or {} do
		if bad(v) or v < 0 then
			breach(`stat:{player.UserId}:{k}`, `{player.Name} stat {k} = {tostring(v)}`)
		end
	end
	for k in data.walls or {} do
		-- Rooms.edgeKey: "floor:hx:hz:o", never "-0" (one half edge under two keys)
		if
			typeof(k) ~= "string"
			or not string.match(k, "^%d+:%-?[%d%.]+:%-?[%d%.]+:%d+$")
			or string.find(":" .. k .. ":", ":%-0:")
		then
			breach(`wallkey:{player.UserId}:{tostring(k)}`, `{player.Name} wall key {tostring(k)}`)
		end
	end
	for k in data.tiles or {} do
		if typeof(k) ~= "string" then
			breach(`tilekey:{player.UserId}:{tostring(k)}`, `{player.Name} tile key {tostring(k)} ({typeof(k)})`)
		end
	end
	for id, room in data.rooms or {} do
		if typeof(room) ~= "table" or bad(room.floor) or bad(room.hx) or bad(room.hz) then
			breach(`room:{player.UserId}:{id}`, `{player.Name} room {id} broken`)
		end
	end
	for id, r in data.residents or {} do
		if typeof(r) ~= "table" or typeof(r.species) ~= "string" or bad(r.campUntil) then
			breach(`res:{player.UserId}:{id}`, `{player.Name} resident {id} broken`)
		end
	end
end

local function checkResidents()
	local folder = ReplicatedStorage:FindFirstChild("Residents")
	if not folder then
		return
	end
	local owners: { [number]: number } = {}
	for _, f in folder:GetChildren() do
		local o = f:GetAttribute("OwnerId")
		if o then
			owners[o] = (owners[o] or 0) + 1
			if owners[o] > 1 then
				breach(`resdup:{o}`, `two Residents folders for owner {o}`)
			end
		end
		for _, c in f:GetChildren() do
			if c:GetAttribute("Away") and c:GetAttribute("Slot") then
				breach(`awayslot:{o}:{c.Name}`, `resident {c.Name} of {o} away and on slot {c:GetAttribute("Slot")}`)
			end
		end
	end
end

local lastCount: { [string]: number } = {}
local function checkGrowth()
	for _, root in { workspace, ReplicatedStorage } do
		local n = #root:GetDescendants()
		local was = lastCount[root.Name]
		box:SetAttribute(root.Name, n)
		if was and n > was * 1.2 + 200 then
			breach(`grow:{root.Name}:{n // 500}`, `{root.Name} grew {was} -> {n} in 30 s`)
		end
		lastCount[root.Name] = n
	end
end

local ticks = 0
while box.Parent do
	ticks += 1
	box:SetAttribute("Ticks", ticks)
	local ok, err = pcall(function()
		checkGuests()
		if ticks % 4 == 0 then
			for _, p in Players:GetPlayers() do
				local data = PlayerData.get(p)
				if data then
					checkData(p, data)
				end
			end
			checkResidents()
		end
		if ticks % 60 == 1 then
			checkGrowth()
		end
	end)
	if not ok then
		breach("guard:" .. tostring(err), "_Guard itself failed: " .. tostring(err))
	end
	task.wait(0.5)
end
