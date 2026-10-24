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
local pending: { [Player]: boolean } = {}
-- What each player was last sent, per section (as JSON): a section that has not changed is not sent again
-- (2026-10-24 evening: a full hotel's state was 58 KB, sent whole every 15 s; the client keeps what it has).
local lastSent: { [Player]: { [string]: string } } = {}

function StateService.provide(section: string, fn: (Player, PlayerData.Data) -> any)
	providers[section] = fn
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
	local any = false
	for section, fn in providers do
		local ok, value = pcall(fn, player, data)
		if ok then
			local encoded, json = pcall(HttpService.JSONEncode, HttpService, value)
			if not encoded or sent[section] ~= json then
				out[section] = value
				sent[section] = if encoded then json else nil
				any = true
			end
		else
			warn(`[state] section {section} failed: {value}`)
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
	end)
end

return StateService
