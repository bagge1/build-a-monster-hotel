--!strict
--[[
	The drawable state a client's panels need that attributes cannot carry
	well (tables): the layout, what is buildable and why not, residents, the
	Book, the Moon Tree, the daily requests. One `State` remote, a table of
	sections; each system `provide`s its section and `mark`s a player when it
	changes, and the send is batched (at most one per `DEBOUNCE` seconds).

	A copy for drawing (§13.2): nothing the client sends back is trusted.
]]

local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Net = require(ReplicatedStorage.Shared.Net)
local PlayerData = require(ServerScriptService.Server.PlayerData)

local StateService = {}

local DEBOUNCE = 0.25

local providers: { [string]: (Player, PlayerData.Data) -> any } = {}
--[[ A section's version (2026-10-26): a string its owner changes whenever
	anything the section is made of changes. While it stands, the section
	is neither made nor encoded again: `build` (~58 KB) was rebuilt and
	encoded on every send (every 15 s per player and every stay) to find
	that nothing had changed. A section without one is made every send. ]]
type Version = (Player, PlayerData.Data) -> string
local versions: { [string]: Version } = {}
-- A versioned section as last made, per player: its data table (a profile loaded again is new), version, value and JSON.
type Kept = { data: PlayerData.Data, version: string, value: any, json: string }
local kept: { [Player]: { [string]: Kept } } = {}
local pending: { [Player]: boolean } = {}
-- What each player was last sent, per section (as JSON): a section that has not changed is not sent again
-- (2026-10-24 evening: a full hotel's state was 58 KB, sent whole every 15 s; the client keeps what it has).
local lastSent: { [Player]: { [string]: string } } = {}

function StateService.provide(
	section: string,
	fn: (Player, PlayerData.Data) -> any,
	version: Version?
)
	providers[section] = fn
	versions[section] = version
end

local function send(player: Player)
	pending[player] = nil
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local out = {}
	local sent = lastSent[player] or {}
	lastSent[player] = sent
	local keep = kept[player] or {}
	kept[player] = keep
	local any = false
	for section, fn in providers do
		local version: string? = nil
		local versionOf = versions[section]
		if versionOf then
			local vok, v = pcall(versionOf, player, data)
			if vok then
				version = v
			else
				warn(`[state] section {section}'s version failed: {v}`)
			end
		end
		local k = keep[section]
		local value, json
		if version ~= nil and k and k.data == data and k.version == version then
			value, json = k.value, k.json
		else
			local ok, made = pcall(fn, player, data)
			if not ok then
				keep[section] = nil
				warn(`[state] section {section} failed: {made}`)
				continue
			end
			value = made
			local encoded, encoding = pcall(HttpService.JSONEncode, HttpService, value)
			json = if encoded then encoding else nil
			keep[section] = if version ~= nil and json ~= nil
				then { data = data, version = version, value = value, json = json }
				else nil
		end
		if json == nil or sent[section] ~= json then
			out[section] = value
			sent[section] = json
			any = true
		end
	end
	if any then
		Net.fire(player, "State", out)
	end
end

function StateService.mark(player: Player)
	if pending[player] then
		return
	end
	pending[player] = true
	task.delay(DEBOUNCE, send, player)
end

function StateService.markAll()
	for player in PlayerData.loaded() do
		StateService.mark(player)
	end
end

function StateService.Init()
	Net.on("Ready", function(player)
		lastSent[player] = nil -- a client starting has nothing yet
		StateService.mark(player)
	end)
end

function StateService.Start()
	PlayerData.onLoaded(function(player)
		StateService.mark(player)
	end)
	PlayerData.onDeparted(function(player)
		pending[player] = nil
		lastSent[player] = nil
		kept[player] = nil
	end)
end

return StateService
