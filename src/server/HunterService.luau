--!strict
--[[
	Hunter Night (GDD §8.1, Appendix A.8): the street's co-op defence.

	Every 90 minutes, for 3, goofy monster hunters walk in from the east end
	of Creepy Lane, two for each hotel, each toward its hotel's entrance. A
	player's **Boo!** scares a hunter within reach, and Security staff scare
	one near their hotel now and then; a scared hunter runs away screaming.
	A hunter who reaches a door nets one guest (or, with none, a resident)
	and leaves.

	NEVER PERMANENT LOSS, NEVER A PAID RESCUE (§8.1, §10.1.7): a netted resident
	goes to the Hunter Camp at the east end, where its owner rescues it with a
	prompt, or it walks home after 24 hours. No damage, no death: hunters only
	run away (the Minimal rating).

	A defended night (fewer than half the hunters reached a door) pays every
	player 5 minutes of income and sends a thank-you bus of Rare-or-better
	guests. Hunters are published like guests (`ReplicatedStorage.Hunters`),
	and drawn by each client.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local Species = require(ReplicatedStorage.Shared.Species)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local GuestService = require(ServerScriptService.Server.GuestService)
local ResidentService = require(ServerScriptService.Server.ResidentService)
local BusService = require(ServerScriptService.Server.BusService)
local StoreService = require(ServerScriptService.Server.StoreService)
local StateService = require(ServerScriptService.Server.StateService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local H = Constants.HunterNight

local HunterService = {}

type Hunter = {
	id: number,
	plot: PlotService.Plot,
	state: "Approach" | "Fleeing" | "Leaving",
	path: { Vector3 },
	speed: number,
	arriveAt: number,
	config: Configuration,
}

local hunters: { [number]: Hunter } = {}
local nextId = 1
local folder: Folder
local active = false
local nightEnd = 0
local nextNight = 0
local total, reached = 0, 0
local securityAt: { [Player]: number } = {}
local camp: Part
local trapsUsed: { [Player]: { [number]: boolean } } = {} -- this night's sprung traps

local function length(path: { Vector3 }): number
	local t = 0
	for i = 2, #path do
		t += (path[i] - path[i - 1]).Magnitude
	end
	return t
end

local function walk(h: Hunter, path: { Vector3 }, speed: number)
	h.path = path
	h.speed = speed
	h.arriveAt = os.clock() + length(path) / speed
	h.config:SetAttribute(
		"Path",
		(function()
			local parts = {}
			for _, p in path do
				table.insert(parts, string.format("%.1f,%.1f,%.1f", p.X, p.Y, p.Z))
			end
			return table.concat(parts, ";")
		end)()
	)
	h.config:SetAttribute("Speed", speed)
	h.config:SetAttribute("T0", workspace:GetServerTimeNow())
	h.config:SetAttribute("State", h.state)
end

local function here(h: Hunter): Vector3
	local travelled = length(h.path) - math.max(0, h.arriveAt - os.clock()) * h.speed
	for i = 2, #h.path do
		local seg = (h.path[i] - h.path[i - 1]).Magnitude
		if travelled <= seg then
			return h.path[i - 1]:Lerp(
				h.path[i],
				if seg > 0 then math.max(0, travelled) / seg else 1
			)
		end
		travelled -= seg
	end
	return h.path[#h.path]
end

local function spawnHunter(plot: PlotService.Plot, delay: number)
	task.delay(delay, function()
		if not active or not plot.owner then
			return
		end
		local id = nextId
		nextId += 1
		local config = Instance.new("Configuration")
		config.Name = tostring(id)
		config:SetAttribute("Plot", plot.index)
		local h: Hunter = {
			id = id,
			plot = plot,
			state = "Approach",
			path = {},
			speed = 1,
			arriveAt = 0,
			config = config,
		}
		local start = StreetLayout.HunterCamp + Vector3.new(30, 0, (math.random() - 0.5) * 10)
		local front = StreetLayout.laneFront(plot.index)
		local entrance = PlotService.point(plot, "Entrance")
		local path = { start, front }
		if entrance then
			table.insert(path, entrance.Position)
		end
		walk(h, path, length(path) / H.ApproachTime)
		config.Parent = folder
		hunters[id] = h
		total += 1
	end)
end

local function flee(h: Hunter)
	h.state = "Fleeing"
	local p = here(h)
	walk(h, { p, Vector3.new(p.X, p.Y, 0), StreetLayout.HunterCamp + Vector3.new(60, 0, 0) }, 26)
end

local function net(h: Hunter)
	reached += 1
	local owner = h.plot.owner
	h.state = "Leaving"
	local p = here(h)
	walk(h, { p, Vector3.new(p.X, p.Y, 0), StreetLayout.HunterCamp + Vector3.new(60, 0, 0) }, 14)
	if not owner then
		return
	end
	-- A guest first; a resident only if the hotel has no guest.
	local candidates = {}
	for _, g in GuestService.of(owner) do
		if g.state ~= "Leaving" then
			table.insert(candidates, g)
		end
	end
	if #candidates > 0 then
		local g = candidates[math.random(1, #candidates)]
		local sp = Species.get(g.species)
		GuestService.remove(g)
		Net.fire(owner, "Announce", `A hunter netted your {sp and sp.name or "guest"}!`, "Hunter")
		return
	end
	local data = PlayerData.get(owner)
	if data then
		for _, r in data.residents do
			if r.campUntil <= os.time() then
				r.campUntil = os.time() + H.CampReturn
				local sp = Species.get(r.species)
				Net.fire(
					owner,
					"Announce",
					`A hunter took your {sp and sp.name or "resident"} to the Hunter Camp! Rescue it at the east end.`,
					"Hunter"
				)
				ResidentService.publish(owner)
				return
			end
		end
	end
end

local defendedHandlers: { () -> () } = {}

-- Called when a night is defended (the season's Candy, Appendix A.10).
function HunterService.onDefended(handler: () -> ())
	table.insert(defendedHandlers, handler)
end

-- Starts a Hunter Night; `scale` multiplies the hunters (the Full Moon Hunt, §8.2).
function HunterService.start(scale: number?)
	if active then
		return
	end
	table.clear(trapsUsed)
	active = true
	total, reached = 0, 0
	nightEnd = os.clock() + H.Duration
	workspace:SetAttribute("HunterNightUntil", workspace:GetServerTimeNow() + H.Duration)
	Net.fireAll(
		"Announce",
		"Hunter Night! Goofy hunters are coming down the lane. Boo! them away!",
		"Hunter"
	)
	for _, plot in PlotService.all() do
		if plot.owner then
			for i = 1, H.HuntersPerHotel * (scale or 1) do
				spawnHunter(plot, (i - 1) * 25 + math.random() * 10)
			end
		end
	end
end

local function finish()
	active = false
	workspace:SetAttribute("HunterNightUntil", nil)
	nextNight = os.clock() + H.Interval
	workspace:SetAttribute("NextHunterNight", workspace:GetServerTimeNow() + H.Interval)
	local defended = total == 0 or reached / total < H.DefendedShare
	if defended and total > 0 then
		for player in PlayerData.loaded() do
			local amount = math.floor(StoreService.incomeRate(player) * H.RewardIncomeSeconds)
			PlayerData.earn(player, amount)
			Net.fire(player, "Toast", `The street is safe! +{Format.cash(amount)}`, "Unlock")
		end
		-- The thank-you bus: Rare or better, now.
		local present = {}
		for _, data in PlayerData.loaded() do
			present[data.location] = true
		end
		local pool = {}
		for _, sp in Species.List do
			if
				present[sp.location]
				and (sp.rarity == "Rare" or sp.rarity == "Epic" or sp.rarity == "Legendary")
			then
				table.insert(pool, sp.id)
			end
		end
		for _ = 1, H.BonusBusSize do
			if #pool > 0 then
				BusService.addToNext(pool[math.random(1, #pool)], nil)
			end
		end
		Net.fireAll(
			"Announce",
			"Hunter Night defended! A thank-you bus of rare guests is coming!",
			"Rare"
		)
		BusService.callNow(nil)
		for _, h in defendedHandlers do
			task.spawn(h)
		end
	else
		Net.fireAll(
			"Announce",
			"Hunter Night is over. The hunters got away with some guests...",
			"Hunter"
		)
	end
end

local function boo(player: Player, id: number)
	local h = hunters[id]
	local character = player.Character
	if not h or h.state ~= "Approach" or not character then
		return
	end
	if (character:GetPivot().Position - here(h)).Magnitude > H.BooRange then
		Net.fire(player, "Refused", "Boo", "Too far away")
		return
	end
	flee(h)
	PlayerData.stat(player, "boos")
	Net.fire(player, "Toast", "Boo! The hunter ran off screaming.", "Good")
end

local function setTrap(player: Player, slot: number, id: string)
	local data = PlayerData.get(player)
	if not data or slot % 1 ~= 0 or slot < 1 or slot > #data.traps then
		return
	end
	if id == "" then
		data.traps[slot] = ""
	else
		local trap = nil
		for _, t in Constants.Traps do
			if t.id == id then
				trap = t
			end
		end
		if not trap or data.traps[slot] == id then
			return
		end
		if not PlayerData.spend(player, trap.cost) then
			Net.fire(player, "Refused", "Trap", "Cash")
			return
		end
		data.traps[slot] = id
		Net.fire(
			player,
			"Toast",
			`{trap.name} set in the forecourt. It scares one hunter a night.`,
			"Good"
		)
	end
	PlotService.refreshTraps(player)
	StateService.mark(player)
end

-- A set trap scares the first hunter that comes within reach of it, once a night (§8.1).
local function springTraps()
	for _, h in hunters do
		local owner = h.plot.owner
		local data = owner and PlayerData.get(owner)
		if h.state == "Approach" and owner and data then
			local used = trapsUsed[owner] or {}
			trapsUsed[owner] = used
			for slot, id in data.traps do
				if id ~= "" and not used[slot] then
					local at = PlotService.forecourtPoint(h.plot, `Trap_{slot}`)
					if at and (here(h) - at.Position).Magnitude < Constants.TrapReach + 6 then
						used[slot] = true
						flee(h)
						Net.fire(owner, "Toast", "Your trap scared a hunter away!", "Good")
						break
					end
				end
			end
		end
	end
end

local function tick()
	local now = os.clock()
	if not active and now >= nextNight then
		HunterService.start()
	end
	for id, h in hunters do
		if now >= h.arriveAt then
			if h.state == "Approach" then
				net(h)
			else
				h.config:Destroy()
				hunters[id] = nil
			end
		end
	end
	-- Security staff (§4.6): scare a hunter near their hotel every few seconds.
	if active then
		springTraps()
		for player, data in PlayerData.loaded() do
			local staff = ResidentService.staff(data, "Security")
			local power = 0
			for _, e in staff do
				power += e
			end
			local plot = PlotService.of(player)
			if power > 0 and plot and now >= (securityAt[player] or 0) then
				local entrance = PlotService.point(plot, "Entrance")
				for _, h in hunters do
					if
						h.state == "Approach"
						and h.plot == plot
						and entrance
						and (here(h) - entrance.Position).Magnitude < H.BooRange
					then
						flee(h)
						securityAt[player] = now + Constants.Staff.SecurityInterval / power
						break
					end
				end
			end
		end
		-- The night ends when its time is up and every hunter is gone, or a minute after at most.
		if (now >= nightEnd and next(hunters) == nil) or now >= nightEnd + 60 then
			finish()
		end
	end
end

-- The Hunter Camp: a netted resident's owner rescues it here (§8.1).
local function buildCamp()
	camp = Instance.new("Part")
	camp.Name = "HunterCamp"
	camp.Anchored = true
	camp.Size = Vector3.new(10, 6, 10)
	camp.Color = Color3.fromRGB(110, 80, 60)
	camp.Material = Enum.Material.WoodPlanks
	camp.CFrame = CFrame.new(StreetLayout.HunterCamp + Vector3.new(14, 3, -14))
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Rescue"
	prompt.ObjectText = "Hunter Camp"
	prompt.HoldDuration = 1.5
	prompt.RequiresLineOfSight = false
	prompt.MaxActivationDistance = 12
	prompt.Parent = camp
	prompt.Triggered:Connect(function(player)
		local data = PlayerData.get(player)
		if not data then
			return
		end
		local n = 0
		for _, r in data.residents do
			if r.campUntil > os.time() then
				r.campUntil = 0
				n += 1
			end
		end
		if n > 0 then
			ResidentService.publish(player)
			Net.fire(
				player,
				"Toast",
				`You rescued {n} resident{if n > 1 then "s" else ""}!`,
				"Unlock"
			)
			StateService.mark(player)
		else
			Net.fire(player, "Toast", "None of your residents are here.", nil)
		end
	end)
	camp.Parent = workspace
end

function HunterService.Init()
	local old = ReplicatedStorage:FindFirstChild("Hunters")
	if old then
		old:Destroy()
	end
	folder = Instance.new("Folder")
	folder.Name = "Hunters"
	folder.Parent = ReplicatedStorage
	Net.on("Boo", boo)
	Net.on("Trap", setTrap)
end

function HunterService.Start()
	buildCamp()
	nextNight = os.clock() + H.FirstDelay
	workspace:SetAttribute("NextHunterNight", workspace:GetServerTimeNow() + H.FirstDelay)
	DevGrant.register("hunters", function()
		nextNight = os.clock()
		return "Hunter Night now"
	end)
	DevGrant.register("camp", function(player)
		-- Sends the player's first resident to the Hunter Camp (as a hunter's net would).
		local data = PlayerData.get(player)
		for _, r in (if data then data.residents else {}) do
			r.campUntil = os.time() + H.CampReturn
			ResidentService.publish(player)
			return `{r.species} is in the camp`
		end
		return "no resident"
	end)
	DevGrant.register("defend", function()
		-- Ends tonight's hunt as a defended one: every hunter scared off.
		for _, h in hunters do
			if h.state == "Approach" then
				flee(h)
			end
		end
		nightEnd = os.clock()
		return "all hunters fleeing"
	end)
	DevGrant.register("hunterstate", function()
		local lines = { `active={active} total={total} reached={reached}` }
		for id, h in hunters do
			table.insert(
				lines,
				`{id} plot{h.plot.index} {h.state} in {math.floor(h.arriveAt - os.clock())}s`
			)
		end
		return table.concat(lines, " | ")
	end)
	PlayerData.onDeparted(function(player)
		securityAt[player] = nil
	end)
	task.spawn(function()
		while true do
			task.wait(0.25)
			local ok, err = pcall(tick)
			if not ok then
				warn(`[hunters] tick failed: {err}`)
			end
		end
	end)
end

return HunterService
