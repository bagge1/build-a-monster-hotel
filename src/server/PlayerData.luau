--!strict
--[[
	Player persistence on ProfileStore (GDD §13.3; the pattern is Sector
	Omega's, D:\Roblox\playbook\PATTERNS.md, "Persistence and money").

	A session lock is what makes duplicating a profile across servers
	impossible, which is why the only dependency is ProfileStore
	(`lm-loleris/profilestore`, the author's own package, `wally.toml`).

	WHAT IT HOLDS (§13.3): currencies; the layout (piece ids, plot-relative
	cells, rotations, what each cost, floor finishes), the decor on its
	squares, the tiles owned, of the hotel being played, and the chain's
	other hotels in `chain` (§6.4); residents (species, mutation, role, the
	hotel they staff);
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
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Rooms = require(ReplicatedStorage.Shared.Rooms)

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
local SCHEMA_VERSION = 6

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
		out[tostring(Grid.tileKey(1, c.x, c.z))] = true
	end
	return out
end

export type PieceRecord = {
	item: string,
	floor: number,
	x: number,
	z: number,
	r: number,
	paid: number, -- what it cost, for the refund
	finish: string?,
}
-- An inner wall on a half edge (GDD §5.4, A.12), keyed by Rooms.edgeKey; `door` when it has a door in it.
export type WallRecord = { door: boolean?, paid: number }
--[[ A built room (A.12): its type (a Room or Amenity row of Pieces), its floor,
	and its seed, a half cell of it (a room is the area holding its seed);
	`finish` its floor finish ("" none). ]]
export type RoomRecord = { type: string, floor: number, hx: number, hz: number, finish: string? }
-- A window on a facade wall (A.1): its type (Constants.Windows.Types) and what it cost, for the refund.
export type WindowRecord = { type: string, paid: number }
-- Decor and furniture (§5.4, A.12): squares of 3 studs on the plot. `room` is kept "" (a room is
-- found from the walls, Rooms.contents).
export type DecorRecord = {
	item: string,
	floor: number,
	x: number,
	z: number,
	r: number,
	room: string,
	paid: number,
}
-- `hotel` is the location of the hotel a resident staffs (§6.4: each hotel its own staff); nil in the Wing.
export type ResidentRecord = {
	species: string,
	mutation: string, -- the look ("" none); a size is `size` (A.11.5: two fields, so `== "Golden"` keeps meaning the look)
	size: string?, -- Tiny or Giant, stacked with the look (A.11.5)
	role: string,
	campUntil: number,
	hotel: number?,
	level: number?, -- A.11.6: its level (nil reads as 1), kept through a rebirth with the resident
	xp: number?, -- toward the next level (ResidentLevels)
}
--[[ A hotel of the chain that is not being played (§6.4): its own fields as
	the played hotel keeps them in `Data`, its rating when it was left, and
	the rate it earned while played, for its background earnings. ]]
export type HotelRecord = {
	layout: { [string]: PieceRecord },
	decor: { [string]: DecorRecord },
	walls: { [string]: WallRecord },
	rooms: { [string]: RoomRecord },
	tiles: { [string]: boolean },
	tilesBought: { [string]: number },
	windows: { [string]: WindowRecord },
	finishes: { [string]: string },
	floors: number,
	freeStairs: number,
	reviews: { number }?,
	rating: number,
	rate: number,
}
export type Data = {
	version: number,
	cash: number,
	till: number,
	runCash: number, -- earned this run, for rebirth (§6.4)
	lifetimeCash: number,
	location: number, -- the hotel being played (§6.4); its fields are `layout`, `tiles` … below
	chain: { [string]: HotelRecord }, -- the chain's other hotels, by location id (§6.4)
	rate: number, -- the played hotel's earning rate, $/s (Chain.updateRate)
	rebirths: number,
	prestige: number, -- Prestige Stars (§6.4)
	shards: number,
	candy: number, -- the season's event currency (§6.1), kept for the event's duration
	candySeason: string,
	moonTree: { [string]: number },
	floors: number,
	layout: { [string]: PieceRecord }, -- the desks and the stairs (rooms are built from walls, `rooms`)
	decor: { [string]: DecorRecord },
	walls: { [string]: WallRecord }, -- inner walls and doors by Rooms.edgeKey (§5.4, A.12)
	rooms: { [string]: RoomRecord }, -- built rooms by id (ids shared with `layout` and `decor`)
	tiles: { [string]: boolean }, -- owned cells per floor, by Grid.tileKey(floor, x, z) (§5.4, A.1)
	tilesBought: { [string]: number }, -- per floor, tiles bought with cash, for the next one's price (the start's and gifts are free)
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
	likesWeek: { week: number, count: number, by: { [string]: boolean } }, -- the showcase's weekly count, each liker once (A.11.4)
	played: { day: number, seconds: number }, -- play time this UTC day (a like counts after Constants.Showcase.LikeAfterPlay)
	visited: { day: number, owners: { [string]: boolean } }, -- other players' lobbies walked into today ("Visit 3 hotels", A.11.4)
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
	chain = {},
	rate = 0,
	rebirths = 0,
	prestige = 0,
	shards = 0,
	candy = 0,
	candySeason = "",
	moonTree = {},
	floors = 1,
	layout = {},
	decor = {},
	walls = {},
	rooms = {},
	tiles = startTiles(),
	tilesBought = {},
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
	likesWeek = { week = 0, count = 0, by = {} },
	played = { day = 0, seconds = 0 },
	visited = { day = 0, owners = {} },
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

--[[ A new hotel's one room (his ruling 2026-10-20; built, 2026-10-21, A.12):
	walls, a door and a Bed, `Constants.Rooms.Start`, free. ]]
local function startRoom(data: Data)
	local S = Constants.Rooms.Start
	for _, w in S.walls do
		for _, e in Rooms.cellEdges(1, w[1], w[2], w[3]) do
			data.walls[e] = { paid = 0 }
		end
	end
	data.walls[Rooms.edgeKey(1, S.door.hx, S.door.hz, S.door.o)] = { door = true, paid = 0 }
	-- At a later location (§6.4) its first room type, with that type's key piece.
	local typeId = S.type
	local start = Pieces.get(typeId)
	if start and start.location ~= data.location then
		for _, p in Pieces.List do
			if p.kind == "Room" and p.location == data.location and p.unlock == nil then
				typeId = p.id
				break
			end
		end
	end
	local req = Rooms.requirement(typeId)
	data.rooms[tostring(data.nextId)] =
		{ type = typeId, floor = 1, hx = S.seed.hx, hz = S.seed.hz, finish = "" }
	data.nextId += 1
	for _, f in S.furniture do
		local item = f.item
		local d = Pieces.decor(item)
		if
			req
			and d
			and d.keyFor
			and table.find(d.keyFor, S.type)
			and not table.find(req.keys, item)
		then
			item = req.keys[1] or item -- the same footprint at every location (Pieces)
		end
		data.decor[tostring(data.nextId)] =
			{ item = item, floor = 1, x = f.x, z = f.z, r = f.r, room = "", paid = 0 }
		data.nextId += 1
	end
end

--[[ A new hotel (§5.4, A.1, A.12): the start square's tiles, one floor, the
	desk across from the arch and one built Standard Room beside it. A
	rebirth (§6.4), a new hotel of the chain and the schema steps start from
	here. ]]
function PlayerData.resetHotel(data: Data)
	data.layout = {}
	data.decor = {}
	data.walls = {}
	data.rooms = {}
	data.tiles = startTiles()
	data.tilesBought = {}
	data.windows = startWindows()
	data.finishes = { Hallway = "" }
	data.floors = 1
	data.freeStairs = 0
	ensureDesk(data)
	startRoom(data)
end

local function migrate(data: Data)
	if typeof(data.version) ~= "number" then
		data.version = SCHEMA_VERSION
	end
	if data.version < 4 then
		-- Tiles, not areas, and bought per floor (§5.4, A.1, his rulings
		-- 2026-10-20): the hotel is built again from the start square; the rest
		-- of the save stays. The game is not live (CLAUDE.md): no migration.
		PlayerData.resetHotel(data)
		local old = data :: any
		old.areas = nil
	end
	if data.version < 5 then
		-- The hotel chain (§6.4, his rulings 2026-10-20): one hotel, at
		-- Haunted Manor, from the start square; residents back in the Wing.
		-- Not live (CLAUDE.md): rebuilt, not migrated.
		PlayerData.resetHotel(data)
		data.location = 1
		data.chain = {}
		data.rate = 0
		data.prestige = 0
		for _, r in data.residents do
			r.role = ""
			r.hotel = nil
		end
	end
	if data.nextId == 1 then
		-- A brand-new profile (the template): a new hotel with its start room.
		PlayerData.resetHotel(data)
	end
	if data.version < 6 then
		-- Built rooms (§5.4, A.12, his rulings 2026-10-21): rooms are walls, a
		-- door and furniture, no longer pieces. Every hotel of the chain starts
		-- again from the start square with its one built room; not live
		-- (CLAUDE.md): rebuilt, not migrated.
		PlayerData.resetHotel(data)
		for _, rec in data.chain do
			local fresh = table.clone(data)
			PlayerData.resetHotel(fresh)
			rec.layout, rec.decor, rec.walls, rec.rooms =
				fresh.layout, fresh.decor, fresh.walls, fresh.rooms
			rec.tiles, rec.tilesBought, rec.windows = fresh.tiles, fresh.tilesBought, fresh.windows
			rec.finishes, rec.floors, rec.freeStairs =
				fresh.finishes, fresh.floors, fresh.freeStairs
			data.nextId = fresh.nextId
		end
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
