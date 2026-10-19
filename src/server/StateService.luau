--!strict
--[[
	The drawable state a client's panels need that attributes cannot carry
	well (tables): the layout, what is buildable and why not, residents, the
	Book, the Moon Tree, the daily requests. One `State` remote, a table of
	sections; each system `provide`s its section and `mark`s a player when it
	changes, and the send is batched (at most one per `DEBOUNCE` seconds).

	A copy for drawing (§13.2): nothing the client sends back is trusted.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Net = require(ReplicatedStorage.Shared.Net)
local PlayerData = require(ServerScriptService.Server.PlayerData)

local StateService = {}

local DEBOUNCE = 0.25

local providers: { [string]: (Player, PlayerData.Data) -> any } = {}
local pending: { [Player]: boolean } = {}

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
	for section, fn in providers do
		local ok, value = pcall(fn, player, data)
		if ok then
			out[section] = value
		else
			warn(`[state] section {section} failed: {value}`)
		end
	end
	Net.fire(player, "State", out)
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
		StateService.mark(player)
	end)
end

function StateService.Start()
	PlayerData.onLoaded(function(player)
		StateService.mark(player)
	end)
	PlayerData.onDeparted(function(player)
		pending[player] = nil
	end)
end

return StateService
