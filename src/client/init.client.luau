--!strict
--[[
	Client entry point: the same Init()/Start() pattern as the server, each
	phase in a pcall, so one failing controller never stops the rest.
]]

local Client = script

local systems: { { Init: () -> (), Start: () -> () } } = {
	require(Client.State) :: any, -- first: panels read what it receives
	require(Client.Hud) :: any, -- before every panel that adds a button to it
	require(Client.PromptFilter) :: any,
	require(Client.GuestRenderer) :: any,
	require(Client.BuildController) :: any,
	require(Client.BusRenderer) :: any,
	require(Client.RatingPanel) :: any,
	require(Client.ResidentRenderer) :: any,
	require(Client.CollectionPanels) :: any,
	require(Client.ProgressionPanel) :: any,
	require(Client.LivePanels) :: any,
	require(Client.HunterRenderer) :: any,
	require(Client.Sound) :: any,
	require(Client.Pings) :: any,
	require(Client.EventPanel) :: any,
	require(Client.Effects) :: any,
	require(Client.Lod) :: any,
	require(Client.TutorialController) :: any, -- last: it points at every other panel's buttons
}

local function run(phase: string)
	for i, system in systems do
		local ok, err = pcall((system :: any)[phase])
		if not ok then
			warn(`[client] system {i} {phase} failed: {err}`)
		end
	end
end

run("Init")
run("Start")
