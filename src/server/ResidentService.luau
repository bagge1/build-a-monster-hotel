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
	the "✓" rises). The panels get the `collection` state section.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Format = require(ReplicatedStorage.Shared.Format)
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
local Perks = require(ReplicatedStorage.Shared.Perks)
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

-- The staff on duty in a role, with each one's efficiency.
function ResidentService.staff(data: PlayerData.Data, role: string): { number }
	local out = {}
	for _, r in data.residents do
		if r.role == role and r.campUntil <= os.time() then
			local sp = Species.get(r.species)
			table.insert(
				out,
				if sp and sp.staff == role
					then Constants.Staff.BestEfficiency
					else Constants.Staff.OtherEfficiency
			)
		end
	end
	return out
end

local function efficiencyOf(rec: PlayerData.ResidentRecord): number
	local sp = Species.get(rec.species)
	return if sp and sp.staff == rec.role
		then Constants.Staff.BestEfficiency
		else Constants.Staff.OtherEfficiency
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
	if mine then
		mine:Destroy()
	end
	if not data or not plot then
		return
	end
	local f = Instance.new("Folder")
	f.Name = name
	f:SetAttribute("OwnerId", player.UserId)
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
		local away = r.campUntil > os.time()
		local c = Instance.new("Configuration")
		c.Name = id
		c:SetAttribute("Species", r.species)
		c:SetAttribute("Mutation", if r.mutation ~= "" then r.mutation else nil)
		c:SetAttribute("Role", r.role)
		c:SetAttribute("Away", away)
		if r.role ~= "" and not away then
			slots[r.role] = (slots[r.role] or 0) + 1
			c:SetAttribute("Slot", slots[r.role])
		end
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
function ResidentService.add(player: Player, speciesId: string, mutation: string?): string?
	local data = PlayerData.get(player)
	if not data or ResidentService.count(data) >= ResidentService.capacity(player, data) then
		return nil
	end
	local id = tostring(data.nextResident)
	data.nextResident += 1
	local rec: PlayerData.ResidentRecord =
		{ species = speciesId, mutation = mutation or "", role = "", campUntil = 0 }
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
	local gain = 1
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
		local mutationName = if g.mutation then g.mutation .. " " else ""
		if ResidentService.count(data) >= ResidentService.capacity(player, data) then
			Net.fire(
				player,
				"Toast",
				`{mutationName}{sp.name} wants to move in, but the Resident Wing is full!`,
				"Bad"
			)
		else
			ResidentService.add(player, g.species, g.mutation)
			data.friendship[g.species] = 0
			Net.fire(
				player,
				"Moment",
				"MoveIn",
				{ species = g.species, mutation = g.mutation, early = early and now < threshold }
			)
			Net.fire(player, "Announce", `Your {mutationName}{sp.name} wants to move in!`, "Rare")
			PlayerData.stat(player, "moveIns")
		end
	end
	StateService.mark(player)
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
	rec.role = role
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
	data.residents[id] = nil
	local shards = Constants.Rarity[sp.rarity].releaseShards
	PlayerData.addShards(player, shards)
	Net.fire(player, "Toast", `{sp.name} went on holiday: +{shards} Moon Shards`, "Good")
	publish(player)
end

-- The Wing's residents' combined rate, before offline's 50 %.
function ResidentService.rate(player: Player, data: PlayerData.Data): number
	local m = Income.multiplier(player)
		* (1 + Perks.total(data.residents, "ResidentIncome", os.time()))
	local total = 0
	for _, r in data.residents do
		if r.role == "" and r.campUntil <= os.time() then
			total += Economy.residentPay(r.species, if r.mutation ~= "" then r.mutation else nil, m)
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
	if data.lastSeen <= 0 then
		return
	end
	local away = os.time() - data.lastSeen
	local cap = ResidentService.offlineCap(player, data)
	local earned = Economy.offline(ResidentService.rate(player, data), away, cap)
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
		return PlotService.lobbyPoint(plot, name)
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
		local stale = not rec or rec.role ~= e.role or rec.campUntil > os.time() or not plot
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
			if rec.role == role and rec.campUntil <= os.time() and not mine[id] then
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

-- Staff at work, once a second.
local function staffTick()
	local now = os.clock()
	for player, data in PlayerData.loaded() do
		local hotel = HotelService.get(player)
		if hotel then
			local timers = staffTimers[player] or {}
			staffTimers[player] = timers
			-- Front Desk: the first waiting guest after a delay.
			local desk = sum(ResidentService.staff(data, "FrontDesk"))
			if desk > 0 and #hotel.queue > 0 then
				local first = GuestService.get(hotel.queue[1])
				if first and first.state == "Queued" then
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
				role = r.role,
				away = r.campUntil > os.time(),
				pay = if sp
					then Economy.residentPay(
						r.species,
						if r.mutation ~= "" then r.mutation else nil,
						1
					)
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
		local id = ResidentService.add(player, args[1] or "Slime", args[2])
		return if id then `resident {id}` else "Wing full or no data"
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
