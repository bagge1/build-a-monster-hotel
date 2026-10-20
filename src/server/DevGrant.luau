--!strict
--[[
	STUDIO ONLY: test hooks driven by a workspace attribute
	(D:\Roblox\playbook\PATTERNS.md, "Safety"), so a playtest gets cash, a
	guest or a bus without playing around a missing one (skill `playtest`).

	Set `workspace.DevCommand` to a command line from the MCP's Server
	execute_luau; the answer appears in `workspace.DevResult`. A client cannot
	set a server attribute, and nothing here runs outside Studio: on a
	published server no command is even registered, and nothing listens.

	Commands are registered by the systems they test: `DevGrant.register`.
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ServerScriptService = game:GetService("ServerScriptService")

local PlayerData = require(ServerScriptService.Server.PlayerData)

local DevGrant = {}

type Command = (player: Player, args: { string }) -> string
local commands: { [string]: Command } = {}

function DevGrant.register(name: string, fn: Command)
	if not RunService:IsStudio() then
		return
	end
	commands[name] = fn
end

local function firstPlayer(): Player?
	return Players:GetPlayers()[1]
end

local function run(line: string): string
	local args = string.split(line, " ")
	local name = table.remove(args, 1) or ""
	local fn = commands[name]
	if not fn then
		local names = {}
		for n in commands do
			table.insert(names, n)
		end
		table.sort(names)
		return `unknown command {name}; have: {table.concat(names, ", ")}`
	end
	local player = firstPlayer()
	if not player then
		return "no player"
	end
	local ok, result = pcall(fn, player, args)
	return if ok then tostring(result) else `error: {result}`
end

function DevGrant.Init()
	if not RunService:IsStudio() then
		return
	end
	DevGrant.register("cash", function(player, args)
		local n = tonumber(args[1]) or 1000
		PlayerData.earn(player, n)
		return `cash +{n} -> {player:GetAttribute("Cash")}`
	end)
	DevGrant.register("shards", function(player, args)
		local n = tonumber(args[1]) or 10
		PlayerData.addShards(player, n)
		return `shards +{n}`
	end)
	DevGrant.register("data", function(player, args)
		local data = PlayerData.get(player) :: any
		local v = data
		for _, key in args do
			v = if typeof(v) == "table" then v[key] else nil
		end
		return game:GetService("HttpService"):JSONEncode(v)
	end)
end

function DevGrant.Start()
	if not RunService:IsStudio() then
		return
	end
	workspace:GetAttributeChangedSignal("DevCommand"):Connect(function()
		local line = workspace:GetAttribute("DevCommand")
		if typeof(line) == "string" and line ~= "" then
			workspace:SetAttribute("DevResult", run(line))
			workspace:SetAttribute("DevCommand", "")
		end
	end)
end

return DevGrant
