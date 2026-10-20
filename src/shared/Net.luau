--!strict
--[[
	The typed remote layer (GDD §13.1, §13.2; decided in M0 as a thin wrapper
	over RemoteEvents, decision log 2026-10-19). Every remote the game has is
	declared once, here: its direction, the type of each argument, and for one
	a client sends, the shortest time between two of them.

	"Assume every piece of data sent from the client has been manipulated"
	(§13.2). So on the server a message is dropped before any handler sees it
	if an argument has the wrong type, a number is not finite, a string is
	longer than `MaxString`, or the player sent the same remote within its
	`rate` (`RateLimit`). What survives is still only an INTENT: an id, a cell,
	a rotation. The handler checks ownership, funds, bounds and unlocks again.

	Server:  Net.on(name, function(player, ...) end); Net.fire(player, name, ...);
	         Net.fireAll(name, ...)
	Client:  Net.send(name, ...); Net.listen(name, function(...) end)
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Net = {}

Net.MaxString = 64

type ArgType = "string" | "number" | "boolean" | "any"
type Def = { dir: "C2S" | "S2C", args: { ArgType }?, rate: number? }

local DEFS: { [string]: Def } = {
	-- Client to server: intents.
	Place = {
		dir = "C2S",
		args = { "string", "number", "number", "number", "number", "boolean" },
		rate = 0.2,
	}, -- item, floor, x, z, r, mirrored
	Move = {
		dir = "C2S",
		args = { "number", "number", "number", "number", "number", "boolean" },
		rate = 0.2,
	}, -- id, floor, x, z, r, mirrored
	Sell = { dir = "C2S", args = { "number" }, rate = 0.2 },
	BuyFloor = { dir = "C2S", rate = 0.5 },
	BuyTile = { dir = "C2S", args = { "number", "number" }, rate = 0.15 }, -- a cell x, z (§5.4, A.1)
	PlaceDecor = {
		dir = "C2S",
		args = { "string", "number", "number", "number", "number" },
		rate = 0.15,
	}, -- decor id, floor, square x, z, r
	MoveDecor = {
		dir = "C2S",
		args = { "number", "number", "number", "number", "number" },
		rate = 0.15,
	}, -- id, floor, square x, z, r
	SellDecor = { dir = "C2S", args = { "number" }, rate = 0.15 },
	Finish = { dir = "C2S", args = { "string", "string" }, rate = 0.2 }, -- a room id or "Hallway"; a finish id ("" is the model's own)
	Pitch = { dir = "C2S", args = { "number" }, rate = 0.25 }, -- guest id
	Assign = { dir = "C2S", args = { "number", "string" }, rate = 0.25 }, -- resident id, role ("" = the Wing)
	Release = { dir = "C2S", args = { "number" }, rate = 0.5 },
	Rebirth = { dir = "C2S", rate = 2 },
	MoonTree = { dir = "C2S", args = { "string" }, rate = 0.25 },
	Like = { dir = "C2S", args = { "number" }, rate = 1 }, -- plot index
	Tutorial = { dir = "C2S", args = { "string" }, rate = 0.25 }, -- "Skip" | "Next"
	Daily = { dir = "C2S", args = { "string", "number" }, rate = 0.25 }, -- "Claim" | "Reroll" | "Login", index
	Code = { dir = "C2S", args = { "string" }, rate = 2 },
	Boo = { dir = "C2S", args = { "number" }, rate = 0.3 }, -- hunter id
	Settings = { dir = "C2S", args = { "string", "boolean" }, rate = 0.25 },
	Ping = { dir = "C2S", args = { "string" }, rate = 3 }, -- a quick ping (§7)
	Buy = { dir = "C2S", args = { "string" }, rate = 1 }, -- a store entry id: the server prompts
	Gift = { dir = "C2S", args = { "string", "number" }, rate = 1 }, -- a pass key, the recipient's UserId (§10.1)
	Ad = { dir = "C2S", rate = 5 }, -- a rewarded ad (§10.2)
	Collect = { dir = "C2S", rate = 0.5 }, -- the till, from the HUD (a pass or nearby)
	Ready = { dir = "C2S", rate = 1 }, -- the client has started and wants its state
	EventShop = { dir = "C2S", args = { "string" }, rate = 0.5 }, -- the season's shop: an item key
	Trap = { dir = "C2S", args = { "number", "string" }, rate = 0.3 },
	Equip = { dir = "C2S", args = { "string", "string" }, rate = 0.3 }, -- a cosmetic slot, its id ("" takes it off) -- lobby trap slot, trap id ("" clears)

	-- Server to client: what to draw.
	State = { dir = "S2C" }, -- (table) the profile's drawable state
	Announce = { dir = "S2C" }, -- (text, kind)
	Pop = { dir = "S2C" }, -- (amount, position, kind): floating "+$"
	Toast = { dir = "S2C" }, -- (text, kind): a short message for one player
	Refused = { dir = "S2C" }, -- (remote, reason): why an intent was turned down
	Moment = { dir = "S2C" }, -- (kind, data): a check-in flourish, a move-in, a rare arrival
}

Net.Defs = DEFS

local folder: Folder
if RunService:IsServer() then
	--[[ Reused if it exists: a second copy of this module (a spec, the MCP's
		own require, DEVNOTES.md "The Studio MCP") must not replace the
		remotes the game's handlers are connected to. ]]
	local existing = ReplicatedStorage:FindFirstChild("Remotes")
	if existing and existing:IsA("Folder") then
		folder = existing
	else
		folder = Instance.new("Folder")
		folder.Name = "Remotes"
		folder.Parent = ReplicatedStorage
	end
	for name in DEFS do
		if not folder:FindFirstChild(name) then
			local remote = Instance.new("RemoteEvent")
			remote.Name = name
			remote.Parent = folder
		end
	end
else
	folder = ReplicatedStorage:WaitForChild("Remotes") :: Folder
end

local function remote(name: string): RemoteEvent
	assert(DEFS[name], `[net] no remote called {name}`)
	return folder:WaitForChild(name) :: RemoteEvent
end

local function valid(def: Def, args: { any }): boolean
	local want = def.args or {}
	if #args > #want then
		return false
	end
	for i, t in want do
		local v = args[i]
		if t ~= "any" and typeof(v) ~= t then
			return false
		end
		if t == "number" and (v ~= v or v == math.huge or v == -math.huge) then
			return false
		end
		if t == "string" and #v > Net.MaxString then
			return false
		end
	end
	return true
end

-- Server: handle a client's intent. Malformed or too-frequent messages never reach `handler`.
function Net.on(name: string, handler: (Player, ...any) -> ())
	local def = DEFS[name]
	assert(def and def.dir == "C2S", `[net] {name} is not a client-to-server remote`)
	local RateLimit = require(game:GetService("ServerScriptService").Server.RateLimit) :: any
	remote(name).OnServerEvent:Connect(function(player: Player, ...)
		local args = table.pack(...)
		args.n = nil
		if not valid(def, args) then
			return
		end
		if def.rate and not RateLimit.allow(player, name, def.rate) then
			return
		end
		local ok, err = pcall(handler, player, table.unpack(args))
		if not ok then
			warn(`[net] {name} from {player.Name} failed: {err}`)
		end
	end)
end

function Net.fire(player: Player, name: string, ...: any)
	assert(DEFS[name] and DEFS[name].dir == "S2C", `[net] {name} is not a server-to-client remote`)
	if player.Parent == Players then
		remote(name):FireClient(player, ...)
	end
end

function Net.fireAll(name: string, ...: any)
	assert(DEFS[name] and DEFS[name].dir == "S2C", `[net] {name} is not a server-to-client remote`)
	remote(name):FireAllClients(...)
end

-- Client: send an intent.
function Net.send(name: string, ...: any)
	assert(DEFS[name] and DEFS[name].dir == "C2S", `[net] {name} is not a client-to-server remote`)
	remote(name):FireServer(...)
end

-- Client: draw what the server says.
function Net.listen(name: string, handler: (...any) -> ()): RBXScriptConnection
	assert(DEFS[name] and DEFS[name].dir == "S2C", `[net] {name} is not a server-to-client remote`)
	return remote(name).OnClientEvent:Connect(handler)
end

-- For the specs: the validation alone.
Net._valid = valid

return Net
