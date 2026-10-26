--[[
	Runs the pure specs (tests/*.spec.luau) against src/shared under Lune,
	outside Studio (tests/README.md):

		lune run tools/run_specs.luau <repo root> [spec ...]

	The specs require the real modules; `script.Parent.X` and `Shared.X` are
	resolved to src/shared/X.luau, Roblox's datatypes come from @lune/roblox,
	and `Random` is a small seeded stand-in; `game` is a stub enough for Net
	to load as a client. A spec that needs more of the engine runs only in
	Studio (`data`). Lune is installed globally by
	rokit (`rokit add --global lune-org/lune`), not by the project.
]]
local fs = require("@lune/fs")
local luau = require("@lune/luau")
local process = require("@lune/process")
local roblox = require("@lune/roblox")

local root = process.args[1]
local only = {}
for i = 2, #process.args do
	only[process.args[i]] = true
end

local env = {}
for k, v in roblox do
	env[k] = v
end
env.Vector3 = roblox.Vector3
env.CFrame = roblox.CFrame
env.Color3 = roblox.Color3
env.Enum = roblox.Enum
env.Vector2 = roblox.Vector2
env.UDim2 = roblox.UDim2
env.Random = {
	new = function(seed)
		local s = (seed or os.time()) % 2147483647
		if s <= 0 then
			s += 2147483646
		end
		local function nxt()
			s = (s * 16807) % 2147483647
			return s / 2147483647
		end
		return {
			NextInteger = function(_, a, b)
				return a + math.floor(nxt() * (b - a + 1))
			end,
			NextNumber = function(_, a, b)
				a = a or 0
				b = b or 1
				return a + nxt() * (b - a)
			end,
		}
	end,
}

local cache = {}
local Shared = setmetatable({}, {
	__index = function(_, name)
		return { __module = name }
	end,
})
function Shared:WaitForChild(name)
	return { __module = name }
end

--[[ The engine as far as a module needs it to load: Net asks RunService
	whether it is the server (here a client, so it makes no remotes) and
	waits for its Remotes folder, which it touches only when a message is
	sent. So Net's validation (`Net._valid`) runs here too. ]]
local game = {
	GetService = function(_, _name)
		return {
			WaitForChild = function(_, n)
				return Shared
			end,
			IsServer = function()
				return false
			end,
		}
	end,
}

local function load(name: string)
	if cache[name] then
		return cache[name]
	end
	local path = `{root}/src/shared/{name}.luau`
	local source = fs.readFile(path)
	local scriptObj = { Parent = Shared, Name = name }
	local fenv = table.clone(env)
	fenv.script = scriptObj
	fenv.game = game
	fenv.require = function(ref)
		return load(ref.__module)
	end
	local fn = luau.load(source, { debugName = name, environment = fenv })
	local result = fn()
	cache[name] = result
	return result
end

local harness = fs.readFile(`{root}/tests/harness.luau`)
local chunks = { harness }
for _, entry in fs.readDir(`{root}/tests`) do
	local name = string.match(entry, "^(.+)%.spec%.luau$")
	if name and (next(only) == nil or only[name]) then
		table.insert(chunks, `-- {entry}\ndo\n{fs.readFile(`{root}/tests/{entry}`)}\nend\n`)
	end
end
table.insert(chunks, "return summary()\n")
local fenv = table.clone(env)
fenv.game = game
fenv.require = function(ref)
	return load(ref.__module)
end
local fn = luau.load(table.concat(chunks, "\n"), { debugName = "specs", environment = fenv })
print(fn())
