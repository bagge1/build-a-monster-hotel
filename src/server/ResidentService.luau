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

	Published: `ReplicatedStorage.Residents.Plot_<i>` holds a Configuration per
	resident (`Species`, `Mutation`, `Role`) so every client draws the Wing
	and the staff at work; the panels get the `collection` state section.
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
	for id, r in data.residents do
		local c = Instance.new("Configuration")
		c.Name = id
		c:SetAttribute("Species", r.species)
		c:SetAttribute("Mutation", if r.mutation ~= "" then r.mutation else nil)
		c:SetAttribute("Role", r.role)
		c:SetAttribute("Away", r.campUntil > os.time())
		c.Parent = f
	end
	f.Parent = folder
	-- Effects that live in other systems.
	local hotel = HotelService.get(player)
	if hotel then
		hotel.staffBonus.Entertainment = sum(ResidentService.staff(data, "Entertainment"))
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

-- Offline earnings (§4.6), into the till on joining.
local function welcomeBack(player: Player, data: PlayerData.Data)
	if data.lastSeen <= 0 then
		return
	end
	local away = os.time() - data.lastSeen
	local cap = if data.passes.NightManager
		then Constants.Residents.NightManagerCap
		else Constants.Residents.OfflineCap
	-- The Moon Tree's offline nodes (§6.5) publish their seconds on the player.
	cap += (player:GetAttribute("OfflineBonus") :: number? or 0)
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
					local due = (first.deskSince or now) + Constants.Staff.FrontDeskDelay / desk
					if now >= due then
						GuestService.checkIn(player, true)
					end
				end
			end
			-- Housekeeping: a dirty room after a delay.
			local keep = sum(ResidentService.staff(data, "Housekeeping"))
			local cleanBonus = player:GetAttribute("CleaningBonus") :: number? or 0
			if keep > 0 then
				for id, room in hotel.rooms do
					if
						room.state == "Dirty"
						and room.dirtySince
						and now - room.dirtySince
							>= Constants.Staff.HousekeepingDelay * (1 - cleanBonus) / keep
					then
						GuestService.clean(player, id)
						break
					end
				end
			end
			-- Room Service: an open request after a delay.
			local service = sum(ResidentService.staff(data, "RoomService"))
			if service > 0 then
				for id, room in hotel.rooms do
					if room.request then
						local key = `req_{id}`
						timers[key] = timers[key] or now
						if now - timers[key] >= Constants.Staff.RoomServiceDelay / service then
							timers[key] = nil
							GuestService.fulfil(player, id, true)
							break
						end
					else
						timers[`req_{id}`] = nil
					end
				end
			end
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
