--!strict
--[[
	Server entry point.

	Each system is a module exposing Init() and Start(), listed below in order.
	Init() wires up its own state and must not depend on other systems being
	ready; Start() may assume every Init() has already run. Keeping the two
	phases apart is what stops load-order bugs before they exist.

	EVERY PHASE OF EVERY SYSTEM RUNS IN A pcall. Some properties throw from a
	game script (DEVNOTES.md, "Some properties throw from a game script"), and
	one unguarded throw in an Init() otherwise takes down every system listed
	after it, silently.

	Each entry says why it sits where it does.
]]

local ServerScriptService = game:GetService("ServerScriptService")

local Server = ServerScriptService.Server

local systems: { { Init: () -> (), Start: () -> () } } = {
	require(Server.PlayerData) :: any, -- first: nearly every system reads a profile
	require(Server.Income) :: any, -- before anything pays: providers register in Start
	require(Server.DevGrant) :: any, -- Studio only; commands register in other systems' Start
	require(Server.StateService) :: any, -- before the systems that provide sections
	require(Server.PlotService) :: any, -- the street and plots, before anything is built on them
	require(Server.HotelService) :: any, -- each hotel's live state, after its plot
	require(Server.BuildService) :: any, -- placement, after the hotel it checks
	require(Server.GuestService) :: any, -- guests, after the hotels they stay in
}

local function run(phase: string)
	for i, system in systems do
		local ok, err = pcall((system :: any)[phase])
		if not ok then
			warn(`[server] system {i} {phase} failed: {err}`)
		end
	end
end

run("Init")
run("Start")
print("[server] started")
