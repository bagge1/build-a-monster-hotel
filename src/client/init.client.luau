--!strict
--[[
	Client entry point: the same Init()/Start() pattern as the server, each
	phase in a pcall, so one failing controller never stops the rest.
]]

-- local Client = script

local systems: { { Init: () -> (), Start: () -> () } } = {}

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
