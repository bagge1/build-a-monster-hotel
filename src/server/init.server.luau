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

-- local ServerScriptService = game:GetService("ServerScriptService")

local systems: { { Init: () -> (), Start: () -> () } } = {
	-- require(ServerScriptService.Server.PlayerData), -- early: nearly every system reads a profile
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
