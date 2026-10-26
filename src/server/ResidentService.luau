--!strict
--[[
	The collection (GDD §4.6): friendship, move-ins, residents, staff, and
	offline earnings.

	FRIENDSHIP IS DETERMINISTIC. Every happy stay (satisfaction ≥ 80) adds +1
	with that species. At the rarity's threshold (§4.2) the happy stay ends
	with "<species> wants to move in!", and every happy stay also has a small
	free chance of an early move-in. The guest moves in as it was, mutation
	and all, and the meter starts again.

	RESIDENTS live in the Resident Wing (capacity 6, more by Moon Tree and pass,
	Appendix A.5). In the Wing a resident earns 25 % of its species' pay into
	the till, and offline 50 % of that, capped (§4.6). Assigned to a staff role
	instead, it earns nothing and automates: Front Desk checks guests in,
	Housekeeping cleans, Room Service answers requests, Bellhop speeds guests
	up, Entertainment adds Fun, Security guards on Hunter Night (§8.1). A
	resident in its species' best role works at 100 %, any other at 60 %.

	Releasing a resident ("a holiday") gives Moon Shards by rarity.

	AWAY (`present`): a resident in the Hunter Camp (`campUntil`, §8.1) or on
	an expedition (`expedition`, A.11.2: "away, as a resident in the Hunter
	Camp is") earns nothing in the Wing or offline, gives no perk, works no
	post and cannot be moved or sent on holiday; it is home by itself when
	its time is up. The trip itself is `ExpeditionService`'s.

	LEVELS (A.11.6, `ResidentLevels`): each resident gains XP a minute at
	work while the player plays (the Wing or a post at any hotel of the chain), a
	full bar is taken by **Level up** (`LevelUp`) for a price in its own Wing
	rate, and a level raises its Wing earnings and its staff efficiency.

	STAFF ARE SEEN WORKING (§4.6, §5.4, Appendix A.5): Room Service and
	Housekeeping walk from their post to the room by the guests' hallways and
	stairs (`GuestService.pathToDoor`), work at the door, and walk back; one
	errand a resident at a time. The server times it all (`Staff.due`); the
	client only draws the walk.

	Published: `ReplicatedStorage.Residents.Plot_<i>` holds a Configuration per
	resident (`Species`, `Mutation`, `Role`, `Away`, `Slot`: its place among
	its role's staff) so every client draws the Wing and the staff at work;
	on an errand also `Errand` (the room's piece id), `Phase` ("Out", "Work",
	"Done" walking back from a finished job, "Back" from one that closed),
	`Path` and `T0`, `Speed` (the leg, as a guest's walk), and `Door` (where
	the "✓" rises). A publish updates the folder in place: a resident still
	there keeps its Configuration, so a client keeps its model and its spot
	(2026-10-26: each publish replaced the folder whole, and every resident
	of the hotel was rebuilt and jumped across the garden). The panels get
	the `collection` state section.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Expeditions = require(ReplicatedStorage.Shared.Expeditions)
local Format = require(ReplicatedStorage.Shared.Format)
local Locations = require(ReplicatedStorage.Shared.Locations)
local Net = require(ReplicatedStorage.Shared.Net)
local Species = require(ReplicatedStorage.Shared.Species)
local Stay = require(ReplicatedStorage.Shared.Stay)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local GuestService = require(ServerScriptService.Server.GuestService)
local StateService = require(ServerScriptService.Server.StateService)
local Income = require(ServerScriptService.Server.Income)
local BusService = require(ServerScriptService.Server.BusService)
local Mutations = require(ReplicatedStorage.Shared.Mutations)
local Perks = require(ReplicatedStorage.Shared.Perks)
local ResidentLevels = require(ReplicatedStorage.Shared.ResidentLevels)
local Staff = require(ReplicatedStorage.Shared.Staff)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local ResidentService = {}

ResidentService.Roles =
	{ "FrontDesk", "Housekeeping", "RoomService", "Bellhop", "Entertainment", "Security" }
ResidentService.RoleNames = {
	FrontDesk = "Front Desk",
	Housekeeping = "Housekeeping",
	RoomService = "Room Service",
	Bellhop = "Bellhop",
	Entertainment = "Entertainment",
	Security = "Security",
}

local rng = Random.new()
local folder: Folder
local capacityProviders: { (Player) -> number } = {}
local friendshipProviders: { (Player, string) -> number } = {}
local moveInHandlers: { (Player, string, PlayerData.ResidentRecord) -> () } = {}
local staffTimers: { [Player]: { [string]: number } } = {} -- what each automation is waiting on

-- A resident's errand to a room (Appendix A.5): the leg it walks now, and when the job is done.
type Errand = {
	role: string,
	room: string, -- the piece id
	phase: string, -- "Out" | "Work" | "Done" | "Back"
	path: { Vector3 }, -- the current leg
	t0: number, -- os.clock() the leg started
	serverT0: number, -- the same moment in server time, for the clients
	arriveAt: number, -- os.clock() the leg ends
	due: number, -- os.clock() the job is done, on the way out
	door: Vector3?,
}
local errands: { [Player]: { [string]: Errand } } = {}

-- A provider of extra Wing slots (the Moon Tree, §6.5).
function ResidentService.addCapacity(provider: (Player) -> number)
	table.insert(capacityProviders, provider)
end

-- A provider of a friendship multiplier for a species (the featured monster, a boost).
function ResidentService.addFriendship(provider: (Player, string) -> number)
	table.insert(friendshipProviders, provider)
end

function ResidentService.onMoveIn(handler: (Player, string, PlayerData.ResidentRecord) -> ())
	table.insert(moveInHandlers, handler)
end

function ResidentService.capacity(player: Player, data: PlayerData.Data): number
	local n = Constants.Residents.WingCapacity
		+ (if data.passes.ResidentWingPlus then Constants.Residents.WingPassSlots else 0)
	for _, f in capacityProviders do
		local ok, v = pcall(f, player)
		if ok and typeof(v) == "number" then
			n += v
		end
	end
	return n
end

function ResidentService.count(data: PlayerData.Data): number
	local n = 0
	for _ in data.residents do
		n += 1
	end
	return n
end

function ResidentService.threshold(speciesId: string): number
	local sp = Species.get(speciesId)
	return if sp then Constants.Rarity[sp.rarity].friendship else math.huge
end

-- Whether a resident is home at `now`: not in the Hunter Camp (§8.1), not on an expedition (A.11.2).
local function present(r: PlayerData.ResidentRecord, now: number): boolean
	return r.campUntil <= now and not Expeditions.away(r, now)
end
ResidentService.present = present

-- Whether a resident on staff works at the hotel being played (§6.4: each hotel its own staff).
local function here(data: PlayerData.Data, r: PlayerData.ResidentRecord): boolean
	return (r.hotel or data.location) == data.location
end
ResidentService.here = here

-- The staff on duty in a role at the hotel being played, with each one's efficiency.
function ResidentService.staff(data: PlayerData.Data, role: string): { number }
	local out = {}
	for _, r in data.residents do
		if r.role == role and present(r, os.time()) and here(data, r) then
			local sp = Species.get(r.species)
			table.insert(
				out,
				(
					if sp and sp.staff == role
						then Constants.Staff.BestEfficiency
						else Constants.Staff.OtherEfficiency
				) * ResidentLevels.efficiency(ResidentLevels.level(r))
			)
		end
	end
	return out
end

-- A resident's efficiency in its role: best or other, times its level's (A.11.6).
local function efficiencyOf(rec: PlayerData.ResidentRecord): number
	local sp = Species.get(rec.species)
	return (
		if sp and sp.staff == rec.role
			then Constants.Staff.BestEfficiency
			else Constants.Staff.OtherEfficiency
	) * ResidentLevels.efficiency(ResidentLevels.level(rec))
end

-- A resident's own Wing rate at level 1 and no income multiplier (A.11.6's price is in it).
local function wingRate(rec: PlayerData.ResidentRecord): number
	return Economy.residentPay(
		rec.species,
		if rec.mutation ~= "" then rec.mutation else nil,
		1,
		rec.size
	)
end

-- An errand's attributes on its resident's Configuration, or none.
local function applyErrand(c: Instance, e: Errand?)
	c:SetAttribute("Errand", if e then e.room else nil)
	c:SetAttribute("Phase", if e then e.phase else nil)
	c:SetAttribute("Path", if e then Staff.encode(e.path) else nil)
	c:SetAttribute("T0", if e then e.serverT0 else nil)
	c:SetAttribute("Speed", if e then Constants.Staff.WalkSpeed else nil)
	c:SetAttribute("Door", if e then e.door else nil)
end

local function configOf(player: Player, id: string): Instance?
	local mine = folder:FindFirstChild(`Plot_{player:GetAttribute("Plot") or 0}`)
	return mine and mine:FindFirstChild(id)
end

local function sum(list: { number }): number
	local s = 0
	for _, v in list do
		s += v
	end
	return s
end

local function publish(player: Player)
	local data = PlayerData.get(player)
	local plot = PlotService.of(player)
	local name = `Plot_{player:GetAttribute("Plot") or 0}`
	local mine = folder:FindFirstChild(name)
	if not data or not plot then
		if mine then
			mine:Destroy()
		end
		return
	end
	local f = mine or Instance.new("Folder")
	f.Name = name
	f:SetAttribute("OwnerId", player.UserId)
	for _, c in f:GetChildren() do
		if not data.residents[c.Name] then
			c:Destroy() -- sold, or gone some other way
		end
	end
	-- Each role's staff in id order, so every client stands them alike.
	local ids = {}
	for id in data.residents do
		table.insert(ids, id)
	end
	table.sort(ids, function(a, b)
		return (tonumber(a) or 0) < (tonumber(b) or 0)
	end)
	local slots: { [string]: number } = {}
	local ongoing = errands[player] or {}
	for _, id in ids do
		local r = data.residents[id]
		local tripping = Expeditions.away(r, os.time())
		local away = not present(r, os.time())
		local c = f:FindFirstChild(id) or Instance.new("Configuration")
		c.Name = id
		c:SetAttribute("Species", r.species)
		c:SetAttribute("Mutation", if r.mutation ~= "" then r.mutation else nil)
		c:SetAttribute("Size", r.size)
		c:SetAttribute("Role", r.role)
		c:SetAttribute("Level", ResidentLevels.level(r))
		c:SetAttribute("Away", away)
		c:SetAttribute("Trip", if tripping then true else nil) -- away on an expedition (A.11.2), not in the camp
		c:SetAttribute("Hotel", if r.role ~= "" then r.hotel or data.location else nil)
		local slot: number? = nil
		if r.role ~= "" and not away and here(data, r) then
			slots[r.role] = (slots[r.role] or 0) + 1
			slot = slots[r.role]
		end
		c:SetAttribute("Slot", slot) -- set either way: a reused Configuration may carry an old one
		applyErrand(c, ongoing[id])
		c.Parent = f
	end
	f.Parent = folder
	-- Effects that live in other systems.
	local hotel = HotelService.get(player)
	if hotel then
		hotel.staffBonus.Entertainment = sum(ResidentService.staff(data, "Entertainment"))
		-- The rating's staff coverage (§5.3, Appendix A.4).
		hotel.staffBonus.FrontDesk = sum(ResidentService.staff(data, "FrontDesk"))
		hotel.staffBonus.RoomService = sum(ResidentService.staff(data, "RoomService"))
		hotel.staffBonus.Housekeeping = sum(ResidentService.staff(data, "Housekeeping"))
		hotel.staffBonus.PerkService = Perks.total(data.residents, "Service", os.time())
		hotel.staffBonus.PerkFun = Perks.total(data.residents, "Fun", os.time())
		hotel.staffBonus.PerkCleanliness = Perks.total(data.residents, "Cleanliness", os.time())
	end
	local bell = ResidentService.staff(data, "Bellhop")
	local best = 0
	for _, e in bell do
		best = math.max(best, e)
	end
	GuestService.setSpeedBonus(
		player,
		best * Constants.Staff.BellhopSpeedBonus + Perks.total(data.residents, "Speed", os.time())
	)
	StateService.mark(player)
end
ResidentService.publish = publish

-- Adds a resident, if the Wing has room. Returns its id.
function ResidentService.add(
	player: Player,
	speciesId: string,
	mutation: string?,
	size: string?
): string?
	local data = PlayerData.get(player)
	if not data or ResidentService.count(data) >= ResidentService.capacity(player, data) then
		return nil
	end
	local id = tostring(data.nextResident)
	data.nextResident += 1
	local rec: PlayerData.ResidentRecord =
		{ species = speciesId, mutation = mutation or "", size = size, role = "", campUntil = 0 }
	data.residents[id] = rec
	publish(player)
	for _, h in moveInHandlers do
		task.spawn(h, player, id, rec)
	end
	return id
end

local function onCheckout(player: Player, g: GuestService.Guest, satisfaction: number)
	local data = PlayerData.get(player)
	local sp = Species.get(g.species)
	if not data or not sp or not Stay.isHappy(satisfaction) then
		return
	end
	-- The room's Decor bar: more friendship per happy stay (GDD A.12).
	local gain = g.friendshipMult or 1
	for _, f in friendshipProviders do
		local ok, v = pcall(f, player, g.species)
		if ok and typeof(v) == "number" then
			gain *= v
		end
	end
	local before = data.friendship[g.species] or 0
	local now = before + gain
	data.friendship[g.species] = now
	-- Only the tutorial's own Slime needs just 1 friendship (§6.3, Appendix A.7);
	-- every other guest, the tutorial's Vampire Count too, needs its rarity's.
	local threshold = if g.tutorialFriend
		then Constants.Residents.TutorialFriendship
		else ResidentService.threshold(g.species)
	local early = rng:NextNumber() < Constants.Rarity[sp.rarity].moveInChance
	if now >= threshold or early then
		local mutationName = Mutations.prefix(g.size, g.mutation)
		if ResidentService.count(data) >= ResidentService.capacity(player, data) then
			Net.fire(
				player,
				"Toast",
				`{mutationName}{sp.name} wants to move in, but the Resident Wing is full!`,
				"Bad"
			)
		else
			ResidentService.add(player, g.species, g.mutation, g.size)
			data.friendship[g.species] = 0
			Net.fire(player, "Moment", "MoveIn", {
				species = g.species,
				mutation = g.mutation,
				size = g.size,
				early = early and now < threshold,
			})
			Net.fire(player, "Announce", `Your {mutationName}{sp.name} wants to move in!`, "Rare")
			PlayerData.stat(player, "moveIns")
		end
	end
	StateService.mark(player)
end

--[[ Refuses moving a resident on staff at another hotel of the chain (`Staff.movable`,
	WAITING §2.48): that hotel's background rate counts it, so it moves only once the
	player is there. Returns whether it was refused. ]]
local function heldElsewhere(
	player: Player,
	data: PlayerData.Data,
	rec: PlayerData.ResidentRecord,
	remote: string
): boolean
	if Staff.movable(rec, data.location) then
		return false
	end
	local name = Locations.get(rec.hotel or data.location).name
	Net.fire(player, "Refused", remote, `It works at your {name}: travel there to move it`)
	return true
end

-- Refuses moving a resident away on an expedition (A.11.2): it is not here. Returns whether it was refused.
local function onTrip(player: Player, rec: PlayerData.ResidentRecord, remote: string): boolean
	if not Expeditions.away(rec, os.time()) then
		return false
	end
	Net.fire(player, "Refused", remote, "It's away on an expedition")
	return true
end

-- In the Hunter Camp it is away too (the header's AWAY): not moved, not sent on holiday
-- (2026-10-26 review: Assign and Release took one the hunters had netted).
local function inCamp(player: Player, rec: PlayerData.ResidentRecord, remote: string): boolean
	if rec.campUntil <= os.time() then
		return false
	end
	Net.fire(player, "Refused", remote, "It's in the Hunter Camp: rescue it first")
	return true
end

local function assign(player: Player, idNumber: number, role: string)
	local data = PlayerData.get(player)
	local rec = data and data.residents[tostring(idNumber)]
	if not data or not rec then
		return
	end
	if role ~= "" and not table.find(ResidentService.Roles, role) then
		return
	end
	if
		heldElsewhere(player, data, rec, "Assign")
		or onTrip(player, rec, "Assign")
		or inCamp(player, rec, "Assign")
	then
		return
	end
	rec.role = role
	rec.hotel = if role ~= "" then data.location else nil -- staffs the hotel being played (§6.4)
	publish(player)
end

local function release(player: Player, idNumber: number)
	local data = PlayerData.get(player)
	local id = tostring(idNumber)
	local rec = data and data.residents[id]
	local sp = rec and Species.get(rec.species)
	if not data or not rec or not sp then
		return
	end
	if
		heldElsewhere(player, data, rec, "Release")
		or onTrip(player, rec, "Release")
		or inCamp(player, rec, "Release")
	then
		return
	end
	data.residents[id] = nil
	local shards = Constants.Rarity[sp.rarity].releaseShards
	PlayerData.addShards(player, shards)
	Net.fire(player, "Toast", `{sp.name} went on holiday: +{shards} Moon Shards`, "Good")
	publish(player)
end

-- What multiplies the Wing's pay now: the income bonuses (offline's for the time away) and the residents' perks.
local function wingMultiplier(player: Player, data: PlayerData.Data, offline: boolean?): number
	return Income.multiplier(player, offline)
		* (1 + Perks.total(data.residents, "ResidentIncome", os.time()))
end

-- One resident's Wing rate at its level, times `m`, wherever it is now.
local function wingPay(r: PlayerData.ResidentRecord, m: number): number
	return Economy.residentPay(r.species, if r.mutation ~= "" then r.mutation else nil, m, r.size)
		* ResidentLevels.wing(ResidentLevels.level(r))
end

--[[ The Wing's residents' combined rate, before offline's 50 %; `offline` for
	the time away (no friend bonus, no timed boost). With `since` (a logout),
	only those who were not on an expedition then: welcome-back pays one home
	since for the part after its trip (§18, 2026-10-26). ]]
function ResidentService.rate(
	player: Player,
	data: PlayerData.Data,
	offline: boolean?,
	since: number?
): number
	local m = wingMultiplier(player, data, offline)
	local total = 0
	for _, r in data.residents do
		if
			r.role == ""
			and present(r, os.time())
			and (r.expedition or 0) <= (since or math.huge)
		then
			total += wingPay(r, m)
		end
	end
	return total
end

--[[ What an expedition's party would earn by staying, $/s (A.11.2, his
	ruling 2026-10-26: the pay is counted as staying counts): each one's Wing
	rate at its level with the bonuses now (`offline`: offline's), though it
	is away. Its own perks are lost while away (A.11.2 "no perk"), so the
	Wing's ResidentIncome is the one the hotel has now. ]]
function ResidentService.partyRate(
	player: Player,
	data: PlayerData.Data,
	ids: { string },
	offline: boolean?
): number
	local m = wingMultiplier(player, data, offline)
	local total = 0
	for _, id in ids do
		local r = data.residents[id]
		if r then
			total += wingPay(r, m)
		end
	end
	return total
end

-- How long residents earn offline (§4.6): 2 h, 8 h with Night Manager, plus the Moon Tree's.
function ResidentService.offlineCap(player: Player, data: PlayerData.Data): number
	local cap = if data.passes.NightManager
		then Constants.Residents.NightManagerCap
		else Constants.Residents.OfflineCap
	-- The Moon Tree's offline nodes (§6.5) publish their seconds on the player.
	return cap + (player:GetAttribute("OfflineBonus") :: number? or 0)
end

-- Offline earnings (§4.6), into the till on joining.
local function welcomeBack(player: Player, data: PlayerData.Data)
	-- From when it was last seen before this session: `data.lastSeen` is kept
	-- up to date from the load on (PlayerData.awaySince).
	local since = PlayerData.awaySince(player)
	if since <= 0 then
		return
	end
	local away = os.time() - since
	local cap = ResidentService.offlineCap(player, data)
	-- No friend bonus for the hours away, whoever is online now (WAITING §2.48, his yes 2026-10-26).
	-- Those on an expedition at the logout are left out: the trip pays for its time (A.11.2) …
	local earned = Economy.offline(ResidentService.rate(player, data, true, since), away, cap)
	-- … and one home since earns only for the part after its trip (§18, 2026-10-26: a trip back
	-- before the login does not also fill the offline till).
	local m = wingMultiplier(player, data, true)
	for _, r in data.residents do
		local ends = r.expedition or 0
		if r.role == "" and present(r, os.time()) and ends > since then
			earned += Economy.offline(
				wingPay(r, m),
				Expeditions.homeSeconds(since, away, cap, ends),
				cap
			)
		end
	end
	if earned > 0 then
		PlayerData.addTill(player, earned)
		Net.fire(
			player,
			"Announce",
			`Welcome back! Your residents earned {Format.cash(earned)} while you were away.`,
			"Good"
		)
	end
end

-- Whether the job an errand went for is still there to do.
local function jobOpen(hotel: HotelService.Hotel, role: string, pieceId: string): boolean
	local room = hotel.rooms[pieceId]
	if not room then
		return false
	end
	return if role == "RoomService" then room.request ~= nil else room.state == "Dirty"
end

-- Turns an errand round, from where the resident stands, back to its post.
local function turnBack(player: Player, id: string, e: Errand, phase: string, now: number)
	local travelled = if e.phase == "Out"
		then (now - e.t0) * Constants.Staff.WalkSpeed
		else Staff.length(e.path)
	e.path = if #e.path > 0 then Staff.backFrom(e.path, travelled) else {}
	e.phase = phase
	e.t0 = now
	e.serverT0 = workspace:GetServerTimeNow()
	e.arriveAt = now + Staff.length(e.path) / Constants.Staff.WalkSpeed
	local c = configOf(player, id)
	if c then
		applyErrand(c, e)
	end
end

-- Sends a resident from its post to a room's door (Appendix A.5).
local function setOff(
	player: Player,
	plot: PlotService.Plot,
	id: string,
	role: string,
	pieceId: string,
	delay: number,
	openedAt: number,
	efficiency: number,
	now: number
)
	local c = configOf(player, id)
	local slot = if c then c:GetAttribute("Slot") :: number? or 1 else 1
	local post = Staff.post(role, slot, function(name)
		return PlotService.point(plot, name)
	end)
	local door = PlotService.piecePoint(plot, pieceId, "Door")
	local path = if post then GuestService.pathToDoor(player, post, pieceId) else nil
	if path and door then
		-- The last point is the threshold: stand just outside it, out of the way.
		path[#path] = door.Position + door.LookVector * 2.5
	end
	local walk = path or {}
	local arriveAt = now + Staff.length(walk) / Constants.Staff.WalkSpeed
	local e: Errand = {
		role = role,
		room = pieceId,
		phase = "Out",
		path = walk,
		t0 = now,
		serverT0 = workspace:GetServerTimeNow(),
		arriveAt = arriveAt,
		due = Staff.due(
			openedAt,
			delay,
			efficiency,
			arriveAt,
			if path then Constants.Staff.AtDoor else 0
		),
		door = if door then door.Position else nil,
	}
	local mine = errands[player] or {}
	errands[player] = mine
	mine[id] = e
	if c then
		applyErrand(c, e)
	end
end

local function clearErrand(player: Player, id: string)
	local mine = errands[player]
	if mine then
		mine[id] = nil
	end
	local c = configOf(player, id)
	if c then
		applyErrand(c, nil)
	end
end

-- Moves every errand on, then gives the open jobs to the free staff, oldest first.
local function runErrands(
	player: Player,
	data: PlayerData.Data,
	hotel: HotelService.Hotel,
	timers: { [string]: number },
	now: number
)
	local plot = PlotService.of(player)
	local mine = errands[player] or {}
	errands[player] = mine
	local taken: { [string]: boolean } = {}
	for id, e in mine do
		local rec = data.residents[id]
		-- Reassigned, released or away: it stands at its new post at once.
		local stale = not rec
			or rec.role ~= e.role
			or not present(rec, os.time())
			or not plot
			or not here(data, rec)
		if not stale and (e.phase == "Out" or e.phase == "Work") then
			if not jobOpen(hotel, e.role, e.room) then
				turnBack(player, id, e, "Back", now)
			elseif now >= e.due then
				local done = if e.role == "RoomService"
					then GuestService.fulfil(player, e.room, true)
					else GuestService.clean(player, e.room)
				turnBack(player, id, e, if done then "Done" else "Back", now)
			else
				taken[`{e.role}|{e.room}`] = true
				if e.phase == "Out" and now >= e.arriveAt then
					e.phase = "Work"
					local c = configOf(player, id)
					if c then
						c:SetAttribute("Phase", "Work")
					end
				end
			end
		elseif stale or now >= e.arriveAt then
			clearErrand(player, id)
		end
	end
	if not plot then
		return
	end
	local cleanBonus = player:GetAttribute("CleaningBonus") :: number? or 0
	for role in Staff.Errands do
		local free = {}
		for id, rec in data.residents do
			if
				rec.role == role
				and present(rec, os.time())
				and not mine[id]
				and here(data, rec)
			then
				table.insert(free, id)
			end
		end
		if #free == 0 then
			continue
		end
		table.sort(free, function(a, b)
			return (tonumber(a) or 0) < (tonumber(b) or 0)
		end)
		local jobs = {}
		for pieceId, room in hotel.rooms do
			local openedAt = if role == "RoomService"
				then (if room.request then timers[`req_{pieceId}`] else nil)
				else (if room.state == "Dirty" then room.dirtySince else nil)
			if openedAt and not taken[`{role}|{pieceId}`] then
				table.insert(jobs, { room = pieceId, openedAt = openedAt })
			end
		end
		table.sort(jobs, function(a, b)
			return a.openedAt < b.openedAt
		end)
		local delay = if role == "RoomService"
			then Constants.Staff.RoomServiceDelay
			else Constants.Staff.HousekeepingDelay * (1 - cleanBonus)
		for i, job in jobs do
			local id = free[i]
			if not id then
				break
			end
			setOff(
				player,
				plot,
				id,
				role,
				job.room,
				delay,
				job.openedAt,
				efficiencyOf(data.residents[id]),
				now
			)
		end
	end
end

--[[ XP for every resident at work while the player plays (A.11.6): in the
	Wing, or on staff at any hotel of the chain, the one played or another
	(`ResidentLevels.learning`, WAITING §2.48); not in the Hunter Camp. A bar
	that fills sends the panel again (its Level up button). ]]
local function giveXp(player: Player, data: PlayerData.Data, seconds: number)
	local filled = false
	for _, r in data.residents do
		if ResidentLevels.learning(r, os.time()) then
			local level = ResidentLevels.level(r)
			local before = ResidentLevels.xp(r)
			r.xp = ResidentLevels.gain(level, before, seconds)
			if
				not ResidentLevels.ready(level, before)
				and ResidentLevels.ready(level, r.xp :: number)
			then
				filled = true
			end
		end
	end
	if filled then
		StateService.mark(player)
	end
end

-- Takes a resident's next level when its bar is full, for its price (A.11.6 decision 3b).
local function levelUp(player: Player, idNumber: number)
	local data = PlayerData.get(player)
	local rec = data and data.residents[tostring(idNumber)]
	local sp = rec and Species.get(rec.species)
	if not data or not rec or not sp then
		return
	end
	local level = ResidentLevels.level(rec)
	if level >= Constants.Residents.LevelCap then
		Net.fire(player, "Refused", "LevelUp", "Already at the top level")
		return
	end
	if not ResidentLevels.ready(level, ResidentLevels.xp(rec)) then
		Net.fire(player, "Refused", "LevelUp", "Its bar isn't full yet: it learns by working")
		return
	end
	local price = ResidentLevels.price(level, wingRate(rec))
	if not PlayerData.spend(player, price) then
		Net.fire(player, "Refused", "LevelUp", "Cash")
		return
	end
	rec.level = level + 1
	rec.xp = 0
	Net.fire(
		player,
		"Moment",
		"LevelUp",
		{ id = idNumber, species = rec.species, level = rec.level }
	)
	Net.fire(player, "Toast", `{sp.name} is now level {rec.level}!`, "Unlock")
	PlayerData.stat(player, "levelUps")
	publish(player)
end

-- Staff at work, once a second.
local lastTick = os.clock()
local function staffTick()
	local now = os.clock()
	local step = math.min(now - lastTick, 5)
	lastTick = now
	for player, data in PlayerData.loaded() do
		local hotel = HotelService.get(player)
		if hotel then
			local timers = staffTimers[player] or {}
			staffTimers[player] = timers
			-- A resident home from the Hunter Camp by itself is on staff again:
			-- its Away, its Slot, the staff bonuses and the Bellhop's speed are
			-- worked out in `publish`, which nothing else calls when the time runs out.
			local clock = os.time()
			if Staff.backFromCamp(data.residents, timers.campChecked or clock, clock) then
				publish(player)
			end
			timers.campChecked = clock
			-- Front Desk: the first guest waiting at the desk, after a delay from
			-- when it got there. The head of the queue may still be walking in
			-- (ToHotel); the ones behind it at the desk are served (Staff.nextAtDesk).
			local desk = sum(ResidentService.staff(data, "FrontDesk"))
			if desk > 0 and #hotel.queue > 0 then
				local firstId = Staff.nextAtDesk(hotel.queue, function(id)
					local g = GuestService.get(id)
					return g ~= nil and g.state == "Queued"
				end)
				local first = firstId and GuestService.get(firstId)
				if first then
					-- The best Bellhop shortens it too (§4.6 "check-in time").
					local bell = 0
					for _, e in ResidentService.staff(data, "Bellhop") do
						bell = math.max(bell, e)
					end
					local due = (first.deskSince or now)
						+ Staff.deskDelay(
							Constants.Staff.FrontDeskDelay,
							desk,
							bell,
							Constants.Staff.BellhopCheckInBonus
						)
					if now >= due then
						GuestService.checkIn(player, true)
					end
				end
			end
			-- Housekeeping and Room Service: errands to the rooms.
			for id, room in hotel.rooms do
				local key = `req_{id}`
				timers[key] = if room.request then timers[key] or now else nil
			end
			runErrands(player, data, hotel, timers, now)
			giveXp(player, data, step)
			-- The Wing's income into the till.
			local rate = ResidentService.rate(player, data)
			if rate > 0 then
				if data.passes.AutoCollect then
					PlayerData.earn(player, rate)
				else
					PlayerData.addTill(player, rate)
				end
			end
		end
	end
end

function ResidentService.Init()
	local old = ReplicatedStorage:FindFirstChild("Residents")
	if old then
		old:Destroy()
	end
	folder = Instance.new("Folder")
	folder.Name = "Residents"
	folder.Parent = ReplicatedStorage
	Net.on("Assign", assign)
	Net.on("Release", release)
	Net.on("LevelUp", levelUp)
end

function ResidentService.Start()
	GuestService.onCheckout(onCheckout)
	-- Perks (§4.6, Appendix A.5) through each system's own hook.
	local function perk(player: Player, kind: string): number
		local data = PlayerData.get(player)
		return if data then Perks.total(data.residents, kind, os.time()) else 0
	end
	Income.addPermanent(function(player)
		local hunting = workspace:GetAttribute("HunterNightUntil") ~= nil
		return perk(player, "Income") + (if hunting then perk(player, "HunterIncome") else 0)
	end)
	BusService.addScoreBonus(function(player)
		return perk(player, "Bus")
	end)
	GuestService.tipBonus = function(player, kind)
		return perk(player, kind)
	end
	PlayerData.onLoaded(function(player, data)
		task.defer(function()
			publish(player)
			welcomeBack(player, data)
		end)
	end)
	PlayerData.onDeparted(function(player)
		staffTimers[player] = nil
		errands[player] = nil
		local mine = folder:FindFirstChild(`Plot_{player:GetAttribute("Plot") or 0}`)
		if mine then
			mine:Destroy()
		end
	end)
	PlotService.onBuilt(function(plot)
		if plot.owner then
			publish(plot.owner)
		end
	end)
	StateService.provide("collection", function(player, data)
		local residents = {}
		for id, r in data.residents do
			local sp = Species.get(r.species)
			table.insert(residents, {
				id = tonumber(id),
				species = r.species,
				mutation = r.mutation,
				size = r.size, -- Tiny or Giant, stacked with the look (A.11.5)
				role = r.role,
				hotel = if r.role ~= "" then r.hotel or data.location else nil,
				away = r.campUntil > os.time(), -- in the Hunter Camp
				trip = Expeditions.away(r, os.time()), -- away on an expedition (A.11.2)
				pay = if sp then wingRate(r) * ResidentLevels.wing(ResidentLevels.level(r)) else 0,
				-- A.11.6: its level, the bar, and the next level's price.
				level = ResidentLevels.level(r),
				xp = math.floor(ResidentLevels.xp(r)),
				need = ResidentLevels.need(ResidentLevels.level(r)),
				ready = ResidentLevels.ready(ResidentLevels.level(r), ResidentLevels.xp(r)),
				price = if sp
					then ResidentLevels.price(ResidentLevels.level(r), wingRate(r))
					else 0,
			})
		end
		local friendship = {}
		for _, sp in Species.List do
			friendship[sp.id] =
				{ have = data.friendship[sp.id] or 0, need = ResidentService.threshold(sp.id) }
		end
		return {
			residents = residents,
			capacity = ResidentService.capacity(player, data),
			friendship = friendship,
			roles = ResidentService.Roles,
		}
	end)
	DevGrant.register("resident", function(player, args)
		-- `resident <species> [look] [size]`; a size alone also works as the second word.
		local look, size = args[2], args[3]
		if Mutations.isSize(look) then
			look, size = size, look
		end
		local id = ResidentService.add(player, args[1] or "Slime", look, size)
		return if id then `resident {id}` else "Wing full or no data"
	end)
	-- `xp <id> <amount>`: XP for a resident (A.11.6), to see its bar fill without hours of play; `xp <id>` reads it.
	DevGrant.register("xp", function(player, args)
		local data = PlayerData.get(player)
		local rec = data and data.residents[args[1] or "1"]
		if not data or not rec then
			return "no such resident"
		end
		local level = ResidentLevels.level(rec)
		if args[2] then
			rec.xp = math.min(
				ResidentLevels.need(level),
				ResidentLevels.xp(rec) + (tonumber(args[2]) or 0)
			)
			StateService.mark(player)
		end
		return `level {level} xp {ResidentLevels.xp(rec)}/{ResidentLevels.need(level)} price {ResidentLevels.price(
			level,
			wingRate(rec)
		)} wing {wingRate(rec) * ResidentLevels.wing(level)} eff {efficiencyOf(rec)}`
	end)
	DevGrant.register("friend", function(player, args)
		local data = PlayerData.get(player)
		if data then
			data.friendship[args[1] or "Slime"] = tonumber(args[2]) or 1
			StateService.mark(player)
		end
		return "ok"
	end)
	task.spawn(function()
		while true do
			task.wait(1)
			local ok, err = pcall(staffTick)
			if not ok then
				warn(`[residents] tick failed: {err}`)
			end
		end
	end)
end

return ResidentService
