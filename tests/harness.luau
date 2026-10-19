--[[
	The test harness (D-17). Not a module: `tools/test_bundle.py` pastes this,
	then every `tests/*.spec.luau` each in its own `do ... end`, then
	`return summary()`, into one chunk that runs in a playtest's Server
	datamodel through the MCP's `execute_luau`. The specs require the real modules from
	`ReplicatedStorage.Shared`, as synced by Rojo, so what is tested is what
	the game runs.

	A spec states RULES, NEVER VALUES. Every number in the game is a
	placeholder (PLAN.md), so a test that pins one fails the first time
	balancing touches it and tests nothing. "Buying never costs less than
	selling pays", "damage never raises a layer", "every hull's weapons are
	rows in the roster" survive any tuning.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Shared = ReplicatedStorage:WaitForChild("Shared")

local passed, failed = 0, {}
local current = "?"

local function describe(name: string, body: () -> ())
	current = name
	body()
end

local function it(name: string, body: () -> ())
	local ok, err = pcall(body)
	if ok then
		passed += 1
	else
		table.insert(failed, `{current} — {name}: {err}`)
	end
end

local function fmt(v: any): string
	return if typeof(v) == "string" then `"{v}"` else tostring(v)
end

local expect = {}
function expect.eq(actual: any, wanted: any, what: string?)
	if actual ~= wanted then
		error(`{what or "value"}: got {fmt(actual)}, wanted {fmt(wanted)}`, 2)
	end
end
function expect.near(actual: number, wanted: number, tolerance: number?, what: string?)
	if math.abs(actual - wanted) > (tolerance or 1e-6) then
		error(`{what or "value"}: got {actual}, wanted {wanted} ± {tolerance or 1e-6}`, 2)
	end
end
function expect.truthy(value: any, what: string?)
	if not value then
		error(`{what or "condition"} was {fmt(value)}`, 2)
	end
end
function expect.atMost(actual: number, limit: number, what: string?)
	if actual > limit + 1e-9 then
		error(`{what or "value"}: {actual} > {limit}`, 2)
	end
end
function expect.atLeast(actual: number, limit: number, what: string?)
	if actual < limit - 1e-9 then
		error(`{what or "value"}: {actual} < {limit}`, 2)
	end
end

local function summary(): string
	local lines = { `{passed} passed, {#failed} failed` }
	for _, line in failed do
		table.insert(lines, "FAIL " .. line)
	end
	return table.concat(lines, "\n")
end
