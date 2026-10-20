--!strict
--[[
	Player persistence on ProfileStore (GDD §13.3; the pattern is Sector
	Omega's, D:\Roblox\playbook\PATTERNS.md, "Persistence and money").

	A session lock is what makes duplicating a profile across servers
	impossible, which is why the only dependency is ProfileStore
	(`lm-loleris/profilestore`, the author's own package, `wally.toml`).

	WHAT IT HOLDS (§13.3): currencies; the layout (piece ids, plot-relative
	cells, rotations, what each cost, floor finishes), the decor on its
	squares, the tiles owned; residents (species, mutation, role);
	friendship; the Monster Book; the Moon Tree; reviews; the tutorial; daily
	and login state; codes; passes; boosts; settings; and the processed
	PurchaseIds, so a receipt is never granted twice.

	ONE WRITER, MANY AUTHORS: systems change `Data` through what they get from
	`get`, and anything that must happen on the way out arrives through
	`onRelease`, so this file never requires a gameplay system.

	A MOCK SAVES NOTHING AND SAYS NOTHING (DEVNOTES.md, "Data"): without
	DataStore access ProfileStore falls back to a mock that succeeds at every
	write. The state is published as `workspace.DataStoreState` and warned
	about loudly unless it is `Access`.
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ServerScriptService = game:GetService("ServerScriptService")
local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Grid = require(ReplicatedStorage.Shared.Grid)

local packages = ServerScriptService:FindFirstChild("ServerPackages")
if not packages or not packages:FindFirstChild("ProfileStore") then
	error(
		"[playerdata] ServerScriptService.ServerPackages.ProfileStore is missing: "
			.. "run `wally install` and let Rojo sync it. Nothing can be saved without it."
	)
end
local ProfileStore =
	require((packages :: Instance):FindFirstChild("ProfileStore") :: ModuleScript) :: any

local PlayerData = {}

--[[ Bump only when the shape changes in a way old data cannot satisfy, and add
	the step to `migrate` in the same commit. The game is not live (CLAUDE.md),
	so until it is, a shape change may simply start everyone over. ]]
local SCHEMA_VERSION = 3

-- A new hotel's windows (A.1, his ruling): a Twin sash on each front wall beside the entrance, free.
local function startWindows(): { [string]: WindowRecord }
	local out = {}
	for _, w in Constants.Windows.Start do
		out[Grid.edgeKey(w.floor, w.x, w.z, w.side)] = { type = w.type, paid = 0 }
	end
	return out
end

-- A new hotel's tiles (§5.4, A.1): the start square, keyed as the profile keeps them.
local function startTiles(): { [string]: boolean }
	local out = {}
	for _, c in Grid.startTiles() do
		out[tostring(Grid.tileKey(c.x, c.z))] = true
	end
	return out
end

export type PieceRecord = {
	item: string,
	floor: number,
	x: number,
	z: number,
	r: number,
	m: boolean?, -- mirrored left to right (Flip, A.1), a room or amenity only
	paid: number, -- what it cost, for the refund
	finish: string?, -- a room's floor finish (Pieces.Finishes), "" or nil for the model's own
}
-- A window on a facade wall (A.1): its type (Constants.Windows.Types) and what it cost, for the refund.
export type WindowRecord = { type: string, paid: number }
-- Decor (§5.4): squares of 3 studs on the plot, and the room it stands in ("" on hallway floor).
export type DecorRecord = {
	item: string,
	floor: number,
	x: number,
	z: number,
	r: number,
	room: string,
	paid: number,
}
export type ResidentRecord = { species: string, mutation: string, role: string, campUntil: number }
export type Data = {
	version: number,
	cash: number,
	till: number,
	runCash: number, -- earned this run, for rebirth (§6.4)
	lifetimeCash: number,
	location: number,
	rebirths: number,
	shards: number,
	candy: number, -- the season's event currency (§6.1), kept for the event's duration
	candySeason: string,
	moonTree: { [string]: number },
	floors: number,
	layout: { [string]: PieceRecord },
	decor: { [string]: DecorRecord },
	tiles: { [string]: boolean }, -- owned cells of the plot, by Grid.tileKey (§5.4, A.1), on every floor
	tilesBought: number, -- tiles bought with cash, for the next one's price (the start's and gifts are free)
	windows: { [string]: WindowRecord }, -- by Grid.edgeKey: the windows placed on facade walls (A.1)
	finishes: { [string]: string }, -- "Hallway" -> a finish id ("" the model's own)
	freeStairs: number, -- stairs owed for floors bought (§5.4: a new floor's first stair is free)
	nextId: number, -- pieces and decor share it
	unlocked: { [string]: boolean }, -- room types unlocked, kept through rebirth (§6.4)
	residents: { [string]: ResidentRecord },
	nextResident: number,
	friendship: { [string]: number },
	book: { [string]: { [string]: boolean } }, -- species -> mutation ("Normal") -> found
	families: { [string]: boolean }, -- location id -> completed
	titles: { [string]: boolean },
	reviews: { number },
	stats: { [string]: number },
	tutorial: string,
	daily: { day: number, list: { any }, rerolls: number, done: { [string]: boolean } },
	login: { streak: number, lastDay: number, claimedDay: number },
	codes: { [string]: boolean },
	receipts: { string },
	passes: { [string]: boolean },
	gifted: { [string]: boolean }, -- passes given by another player (§10.1 point 4), kept as if bought
	giftTo: { [string]: number }, -- pass key -> the UserId this player is buying it for now
	boosts: { [string]: number }, -- name -> seconds of play time left
	settings: { [string]: boolean },
	lastSeen: number,
	likes: number,
	likesGiven: { day: number, plots: { [string]: boolean } },
	funnel: { [string]: boolean },
	cosmetics: { [string]: boolean },
	equipped: { [string]: string }, -- slot -> the cosmetic worn there ("" for none; Cosmetics.luau)
	traps: { string }, -- the lobby's trap slots (§8.1), "" when empty
}

local TEMPLATE: Data = {
	version = SCHEMA_VERSION,
	cash = Constants.Economy.StartCash,
	till = 0,
	runCash = 0,
	lifetimeCash = 0,
	location = 1,
	rebirths = 0,
	shards = 0,
	candy = 0,
	candySeason = "",
	moonTree = {},
	floors = 1,
	layout = {},
	decor = {},
	tiles = startTiles(),
	tilesBought = 0,
	windows = startWindows(),
	finishes = { Hallway = "" },
	freeStairs = 0,
	nextId = 1,
	unlocked = {},
	residents = {},
	nextResident = 1,
	friendship = {},
	book = {},
	families = {},
	titles = {},
	reviews = {},
	stats = {},
	tutorial = "Start",
	daily = { day = 0, list = {}, rerolls = 0, done = {} },
	login = { streak = 0, lastDay = 0, claimedDay = 0 },
	codes = {},
	receipts = {},
	passes = {},
	gifted = {},
	giftTo = {},
	boosts = {},
	settings = { music = true, sfx = true, lowGraphics = false },
	lastSeen = 0,
	likes = 0,
	likesGiven = { day = 0, plots = {} },
	funnel = {},
	cosmetics = {},
	equipped = { Sign = "", Lobby = "", Facade = "" },
	traps = { "", "", "" },
}

local store = ProfileStore.New("MonsterHotel_Players_v1", TEMPLATE)

local profiles: { [Player]: any } = {}
local loadedCallbacks: { (Player, Data) -> () } = {}
local releaseCallbacks: { (Player, Data) -> () } = {}
local departedCallbacks: { (Player) -> () } = {}
local messageCallbacks: { (Player, Data, any) -> boolean } = {}
local statCallbacks: { (Player, string) -> () } = {}
local keys: { [Player]: string } = {}
local settled: { [Player]: boolean } = {}

-- At least one front desk (§5.4): a hotel without one gets it across from the arch.
local function ensureDesk(data: Data)
	local hasDesk = false
	for _, rec in data.layout do
		if rec.item == "FrontDesk" then
			hasDesk = true
		end
	end
	if not hasDesk then
		local at = Constants.Grid.DeskStart
		data.layout[tostring(data.nextId)] =
			{ item = "FrontDesk", floor = 1, x = at.x, z = at.z, r = at.r, paid = 0 }
		data.nextId += 1
	end
end

--[[ A new hotel (§5.4, A.1): the start square's tiles, one floor, the desk
	across from the arch and nothing else. A rebirth (§6.4) and the tiles'
	schema step start from here. ]]
function PlayerData.resetHotel(data: Data)
	data.layout = {}
	data.decor = {}
	data.tiles = startTiles()
	data.tilesBought = 0
	data.windows = startWindows()
	data.finishes = { Hallway = "" }
	data.floors = 1
	data.freeStairs = 0
	ensureDesk(data)
end

local function migrate(data: Data)
	if typeof(data.version) ~= "number" then
		data.version = SCHEMA_VERSION
	end
	if data.version < 3 then
		-- Tiles, not areas (§5.4, A.1, his rulings 2026-10-20): the hotel is
		-- built again from the start square; the rest of the save stays. The
		-- game is not live (CLAUDE.md): no migration of the old layout.
		PlayerData.resetHotel(data)
		local old = data :: any
		old.areas = nil
	end
	ensureDesk(data)
	data.version = SCHEMA_VERSION
end

-- Watch the store's state and say so loudly unless it is Access (DEVNOTES.md, "Data").
task.spawn(function()
	local waited = 0
	while ProfileStore.DataStoreState == "NotReady" and waited < 30 do
		waited += task.wait(0.25)
	end
	local state = ProfileStore.DataStoreState
	workspace:SetAttribute("DataStoreState", state)
	if state ~= "Access" then
		warn(
			`[playerdata] DataStore state is {state}: PROFILES ARE A MOCK AND NOTHING WILL BE SAVED`
		)
	else
		print("[playerdata] DataStore Access")
	end
end)

--[[ STUDIO ONLY: a test profile in place of the player's own, so a playtest
	can start fresh without touching August's. Set ServerStorage's
	`StudioProfile` attribute to a name beginning `Test_` before Play. Off
	before release (memory phase-status). ]]
local function profileKey(player: Player): string
	if RunService:IsStudio() and player.UserId > 0 then
		local test = ServerStorage:GetAttribute("StudioProfile")
		if typeof(test) == "string" and string.sub(test, 1, 5) == "Test_" then
			warn(`[playerdata] STUDIO TEST PROFILE Player_{test} in place of {player.Name}'s own`)
			return `Player_{test}`
		end
	end
	return `Player_{player.UserId}`
end

-- The values a HUD reads at any moment, as attributes on the player (a copy for drawing).
function PlayerData.publish(player: Player)
	local profile = profiles[player]
	local d = if profile then profile.Data else nil
	player:SetAttribute("Cash", if d then d.cash else nil)
	player:SetAttribute("Till", if d then d.till else nil)
	player:SetAttribute("Shards", if d then d.shards else nil)
	player:SetAttribute("Location", if d then d.location else nil)
	player:SetAttribute("Floors", if d then d.floors else nil)
	player:SetAttribute("Tutorial", if d then d.tutorial else nil)
	player:SetAttribute("Loaded", d ~= nil)
end

local function settle(player: Player, profile: any)
	if settled[player] then
		return
	end
	settled[player] = true
	profile.Data.lastSeen = os.time()
	for _, callback in releaseCallbacks do
		local ok, err = pcall(callback, player, profile.Data)
		if not ok then
			warn(`[playerdata] release handler failed for {player.Name}: {err}`)
		end
	end
end

local function onPlayerAdded(player: Player)
	local key = profileKey(player)
	local profile = store:StartSessionAsync(key, {
		Cancel = function()
			return player.Parent ~= Players
		end,
	})
	if not profile then
		player:Kick("Could not load your save data. Please rejoin.")
		return
	end
	profile:AddUserId(player.UserId)
	profile:Reconcile()
	migrate(profile.Data)

	if player.Parent ~= Players then
		profile:EndSession()
		return
	end

	local lastSaveReason: string? = nil
	profile.OnLastSave:Connect(function(reason: string)
		lastSaveReason = reason
		settle(player, profile)
	end)
	profile.OnSessionEnd:Connect(function()
		profiles[player] = nil
		if lastSaveReason == "Shutdown" or lastSaveReason == "Manual" then
			return
		end
		player:Kick("Your save data was opened elsewhere. Please rejoin.")
	end)

	profiles[player] = profile
	keys[player] = key
	PlayerData.publish(player)
	for _, callback in loadedCallbacks do
		local ok, err = pcall(callback, player, profile.Data)
		if not ok then
			warn(`[playerdata] load handler failed for {player.Name}: {err}`)
		end
	end
	-- Messages sent to this profile (`PlayerData.message`), now and while the session lasts.
	profile:MessageHandler(function(message: any, processed: () -> ())
		for _, callback in messageCallbacks do
			local ok, taken = pcall(callback, player, profile.Data, message)
			if not ok then
				warn(`[playerdata] message handler failed for {player.Name}: {taken}`)
			elseif taken == true then
				processed()
				PlayerData.publish(player)
				return
			end
		end
	end)
end

local function onPlayerRemoving(player: Player)
	local profile = profiles[player]
	if profile then
		settle(player, profile)
		profiles[player] = nil
		profile:EndSession()
	end
	for _, callback in departedCallbacks do
		local ok, err = pcall(callback, player)
		if not ok then
			warn(`[playerdata] departure handler failed for {player.Name}: {err}`)
		end
	end
	settled[player] = nil
	keys[player] = nil
end

-- Called with each loaded profile; a player already loaded is called at once.
function PlayerData.onLoaded(callback: (Player, Data) -> ())
	table.insert(loadedCallbacks, callback)
	for player, profile in profiles do
		task.spawn(callback, player, profile.Data)
	end
end

-- Called once per session as it ends, while changes to `Data` are still saved.
function PlayerData.onRelease(callback: (Player, Data) -> ())
	table.insert(releaseCallbacks, callback)
end

-- Called after a player has gone, to drop what a system held for them.
function PlayerData.onDeparted(callback: (Player) -> ())
	table.insert(departedCallbacks, callback)
end

--[[ Handles a message sent to a profile (`PlayerData.message`): returns true
	when it took the message, which removes it from the profile for good. ]]
function PlayerData.onMessage(callback: (Player, Data, any) -> boolean)
	table.insert(messageCallbacks, callback)
end

--[[ Sends a message to a player's profile, online or not (ProfileStore's
	MessageAsync: it waits in the profile until a session takes it). A player
	on this server is saved at once so the message arrives in seconds, not at
	the next auto-save. False when the send failed. ]]
function PlayerData.message(userId: number, message: { [string]: any }): boolean
	local key = `Player_{userId}`
	local here: Player? = nil
	for player, k in keys do
		if player.UserId == userId then
			key, here = k, player
		end
	end
	local ok, sent = pcall(store.MessageAsync, store, key, message)
	if not ok or sent ~= true then
		warn(`[playerdata] message to {key} failed: {sent}`)
		return false
	end
	if here then
		PlayerData.save(here)
	end
	return true
end

function PlayerData.get(player: Player): Data?
	local profile = profiles[player]
	return if profile then profile.Data else nil
end

function PlayerData.waitFor(player: Player): Data?
	while player.Parent == Players do
		local data = PlayerData.get(player)
		if data then
			return data
		end
		task.wait()
	end
	return nil
end

function PlayerData.loaded(): { [Player]: Data }
	local out = {}
	for player, profile in profiles do
		out[player] = profile.Data
	end
	return out
end

-- Adds cash (positive) to the wallet; earned cash counts toward the run and lifetime.
function PlayerData.earn(player: Player, amount: number)
	local d = PlayerData.get(player)
	if not d or amount <= 0 or amount ~= amount then
		return
	end
	d.cash += amount
	d.runCash += amount
	d.lifetimeCash += amount
	player:SetAttribute("Cash", d.cash)
end

-- Gives cash back (a sale's refund): into the wallet, but not earned (§6.4's run cash).
function PlayerData.refund(player: Player, amount: number)
	local d = PlayerData.get(player)
	if not d or amount <= 0 or amount ~= amount then
		return
	end
	d.cash += amount
	player:SetAttribute("Cash", d.cash)
end

-- Adds to the till (§4.4), counting toward the run when it is collected.
function PlayerData.addTill(player: Player, amount: number)
	local d = PlayerData.get(player)
	if not d or amount <= 0 or amount ~= amount then
		return
	end
	d.till = math.min(Constants.Economy.TillCap, d.till + amount)
	player:SetAttribute("Till", d.till)
end

-- Spends `amount` if the wallet holds it; true when spent.
function PlayerData.spend(player: Player, amount: number): boolean
	local d = PlayerData.get(player)
	if not d or amount ~= amount or amount < 0 or d.cash < amount then
		return false
	end
	d.cash -= amount
	player:SetAttribute("Cash", d.cash)
	return true
end

function PlayerData.addShards(player: Player, amount: number)
	local d = PlayerData.get(player)
	if not d then
		return
	end
	d.shards = math.max(0, d.shards + amount)
	player:SetAttribute("Shards", d.shards)
end

function PlayerData.stat(player: Player, name: string, delta: number?)
	local d = PlayerData.get(player)
	if d then
		d.stats[name] = (d.stats[name] or 0) + (delta or 1)
		for _, callback in statCallbacks do
			task.spawn(callback, player, name)
		end
	end
end

-- Called after a profile stat changes (`PlayerData.stat`), with its name.
function PlayerData.onStat(callback: (Player, string) -> ())
	table.insert(statCallbacks, callback)
end

-- Saves now, in the background (ProfileStore's own merging is enough at this size).
function PlayerData.save(player: Player)
	local profile = profiles[player]
	if profile and profile:IsActive() and not settled[player] then
		profile:Save()
	end
end

function PlayerData.isClosing(): boolean
	return ProfileStore.IsClosing == true
end

--[[ A Robux grant (§13.3): `grant` changes the data and returns whether it
	granted; it runs only if `purchaseId` is not already among the receipts,
	and the id is remembered in the same change. Then this yields until a save
	holds the id, so ProcessReceipt acknowledges only goods on disk; false is
	"not yet", never "refused for good". ]]
function PlayerData.grantOnce(player: Player, purchaseId: string, grant: (Data) -> boolean): boolean
	local profile = profiles[player]
	if not profile or not profile:IsActive() then
		return false
	end
	local data: Data = profile.Data
	if not table.find(data.receipts, purchaseId) then
		local ok, granted = pcall(grant, data)
		if not ok or granted ~= true then
			warn(`[playerdata] purchase {purchaseId} for {player.Name} not granted: {granted}`)
			return false
		end
		table.insert(data.receipts, purchaseId)
		while #data.receipts > 200 do
			table.remove(data.receipts, 1)
		end
		PlayerData.publish(player)
	end
	-- Wait for a save that holds it.
	local saved = false
	local connection = profile.OnAfterSave:Connect(function(last: any)
		if
			typeof(last) == "table"
			and typeof(last.receipts) == "table"
			and table.find(last.receipts, purchaseId)
		then
			saved = true
		end
	end)
	profile:Save()
	local waited = 0
	while not saved and profile:IsActive() and waited < 30 do
		waited += task.wait(0.1)
	end
	connection:Disconnect()
	return saved
end

function PlayerData.Init()
	Players.PlayerRemoving:Connect(onPlayerRemoving)
end

function PlayerData.Start()
	Players.PlayerAdded:Connect(onPlayerAdded)
	for _, player in Players:GetPlayers() do
		task.spawn(onPlayerAdded, player)
	end
end

PlayerData.Template = TEMPLATE

return PlayerData
