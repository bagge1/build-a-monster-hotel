--!strict
--[[
	Co-play without chat (GDD §7): since age checks cut on-platform chat,
	everything here works with no typing.

	  - VISIT AND LIKE: walk up to any other hotel's sign and give it one like
	    a day; likes show on the sign, and the most-liked hotel on the street
	    wears "Street Favourite".
	  - THE SHOWCASE (A.11.4, street only; rules in `Showcase`): a like counts
	    only after `LikeAfterPlay` of play that day; the sign shows the
	    lifetime count, the weekly count (each liker once a week) picks each
	    street's favourite; milestones give sign cosmetics; the Showcase panel
	    lists this server's hotels with Visit (the `Visit` remote stands the
	    player at that hotel's forecourt); walking into another player's lobby
	    counts toward the daily "Visit 3 hotels" (stat `hotelsVisited`).
	  - FRIEND BONUS: +10 % income for everyone on the street while two or more
	    friends play together (an `Income` category of its own, §6.2).
	  - QUICK PINGS: a few set phrases over your head ("Need a Coffin Suite!",
	    "Pitching!", "Thanks!"). "Need a ...!" names the room the rarest guest
	    on the street wants, browsing or announced for the next bus; with
	    none, it is the generic phrase. The server words it, not the client.
	  - LEADERBOARD (street): rating and likes in the player list.

	  - VIP LOBBY (§10.2): the badge and the gold name tag (`vipTag`).

	Not built yet: co-managers (build rights for a friend, §7). The global
	leaderboards are `LeaderboardService`.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Bus = require(ReplicatedStorage.Shared.Bus)
local Constants = require(ReplicatedStorage.Shared.Constants)
local Locations = require(ReplicatedStorage.Shared.Locations)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Showcase = require(ReplicatedStorage.Shared.Showcase)
local Species = require(ReplicatedStorage.Shared.Species)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local Income = require(ServerScriptService.Server.Income)
local BusService = require(ServerScriptService.Server.BusService)
local DevGrant = require(ServerScriptService.Server.DevGrant)
local StateService = require(ServerScriptService.Server.StateService)

local SocialService = {}

SocialService.Pings = {
	NeedRoom = "Need a room for that guest!",
	Pitching = "Pitching!",
	Thanks = "Thanks!",
	Hunters = "Hunters coming!",
	Hello = "Hello, neighbour!",
	Visit = "Come visit my hotel!",
}

local friendsOnline = false
local friendCache: { [string]: boolean } = {}

local function pairKey(a: Player, b: Player): string
	local x, y = math.min(a.UserId, b.UserId), math.max(a.UserId, b.UserId)
	return `{x}:{y}`
end

local function recomputeFriends()
	local list = Players:GetPlayers()
	local found = false
	for i = 1, #list do
		for j = i + 1, #list do
			local key = pairKey(list[i], list[j])
			if friendCache[key] == nil then
				local ok, yes = pcall(list[i].IsFriendsWith, list[i], list[j].UserId)
				friendCache[key] = ok and yes == true
			end
			if friendCache[key] then
				found = true
			end
		end
	end
	if found ~= friendsOnline then
		friendsOnline = found
		Net.fireAll(
			"Toast",
			if found
				then "Friends are playing together: +10% income for the whole street!"
				else "The friend bonus has ended.",
			"Good"
		)
	end
	workspace:SetAttribute("FriendBonus", found)
end

local function today(): number
	return os.time() // 86400
end

local function thisWeek(): number
	return Showcase.week(os.time())
end

-- The hotels played on this server, as the showcase ranks them (A.11.4).
local function entries(): { Showcase.Entry }
	local out = {}
	for _, plot in PlotService.all() do
		local data = plot.owner and PlayerData.get(plot.owner)
		if plot.owner and data then
			table.insert(out, {
				key = tostring(plot.owner.UserId),
				street = plot.street,
				week = Showcase.weekly(data.likesWeek, thisWeek()),
				likes = data.likes,
			})
		end
	end
	return out
end

-- Each street's hotel with the most likes this week wears the badge (A.11.4: the weekly count).
local function refreshFavourite()
	local best = Showcase.favourites(entries())
	for _, plot in PlotService.all() do
		local owner = plot.owner
		plot.model:SetAttribute(
			"StreetFavourite",
			owner ~= nil and best[plot.street] == tostring(owner.UserId)
		)
	end
end

-- The milestone cosmetics (A.11.4) a lifetime count has reached; `announce` for a like just received.
local function milestones(owner: Player, data: PlayerData.Data, announce: boolean)
	for _, c in Showcase.milestones(data.likes) do
		if not data.cosmetics[c.id] then
			data.cosmetics[c.id] = true
			if announce then
				Net.fire(
					owner,
					"Moment",
					"LikeMilestone",
					{ id = c.id, name = c.name, likes = c.likes }
				)
			end
		end
	end
end

--[[ A like received by `owner` from the player keyed `liker` (a UserId):
	the lifetime count, the weekly count (each liker once a week) and the
	milestones. The giver's own checks are `like`'s. ]]
local function receive(owner: Player, ownerData: PlayerData.Data, liker: string)
	ownerData.likes += 1
	Showcase.countWeekly(ownerData.likesWeek, liker, thisWeek())
	milestones(owner, ownerData, true)
	SocialService.likesChanged()
end

-- Stands the player at another hotel's forecourt (the Showcase panel's Visit, A.11.4).
local function visit(player: Player, plotIndex: number)
	local plot = PlotService.all()[plotIndex]
	local character = player.Character
	local at = plot and plot.owner and PlotService.point(plot, "Spawn")
	if not at or not character or plot.owner == player then
		return
	end
	pcall(function()
		player:RequestStreamAroundAsync(at.Position, 5)
	end)
	if player.Character == character then
		character:PivotTo(at + Vector3.new(0, 3, 0))
	end
end

-- A lobby walked into (A.11.4's daily "Visit 3 hotels"): once a day per owner.
local function visited(player: Player, data: PlayerData.Data, owner: string, ownerName: string)
	if data.visited.day ~= today() then
		data.visited = { day = today(), owners = {} }
	end
	if data.visited.owners[owner] then
		return
	end
	data.visited.owners[owner] = true
	PlayerData.stat(player, "hotelsVisited")
	local n = 0
	for _ in data.visited.owners do
		n += 1
	end
	Net.fire(player, "Toast", `Visiting {ownerName}'s hotel ({n} today)`, "Good")
end

-- Who stands in whose lobby: every live hotel's floor-1 tiles, against every other player.
local function checkVisits()
	for _, plot in PlotService.all() do
		local owner = plot.owner
		local ownerData = owner and PlayerData.get(owner)
		if owner and ownerData then
			for player, data in PlayerData.loaded() do
				local character = player.Character
				local root = character and character:FindFirstChild("HumanoidRootPart")
				if
					player ~= owner
					and root
					and root:IsA("BasePart")
					and Showcase.inside(
						ownerData.tiles,
						plot.frame:PointToObjectSpace(root.Position)
					)
				then
					visited(player, data, tostring(owner.UserId), owner.DisplayName)
				end
			end
		end
	end
end

local function like(player: Player, plotIndex: number)
	local data = PlayerData.get(player)
	local plot = PlotService.all()[plotIndex]
	local owner = plot and plot.owner
	if not data or not owner or owner == player then
		return
	end
	if data.likesGiven.day ~= today() then
		data.likesGiven = { day = today(), plots = {} }
	end
	local key = tostring(owner.UserId)
	if data.likesGiven.plots[key] then
		Net.fire(player, "Refused", "Like", "You already liked this hotel today")
		return
	end
	-- A like counts only from a player who has played a while today (A.11.4).
	local played = if data.played.day == today() then data.played.seconds else 0
	if not Showcase.canLike(played) then
		local left = math.ceil((Constants.Showcase.LikeAfterPlay - played) / 60)
		Net.fire(
			player,
			"Refused",
			"Like",
			`Play {left} more minute{if left == 1 then "" else "s"} today to like a hotel`
		)
		return
	end
	local ownerData = PlayerData.get(owner)
	if not ownerData then
		return
	end
	data.likesGiven.plots[key] = true
	receive(owner, ownerData, tostring(player.UserId))
	Net.fire(player, "Toast", `You liked {owner.DisplayName}'s hotel!`, "Good")
	Net.fire(
		owner,
		"Toast",
		`{player.DisplayName} liked your hotel! ♥ {ownerData.likes}`,
		"Unlock"
	)
	PlayerData.stat(player, "likesGiven")
end

-- After any like: the badge first, then every sign and leaderboard row that shows likes.
function SocialService.likesChanged()
	refreshFavourite()
	StateService.markAll()
	for _, plot in PlotService.all() do
		local owner = plot.owner
		local data = owner and PlayerData.get(owner)
		if owner and data then
			HotelService.recompute(owner)
			local stats = owner:FindFirstChild("leaderstats")
			local likes = stats and stats:FindFirstChild("Likes")
			if likes and likes:IsA("IntValue") then
				likes.Value = data.likes
			end
		end
	end
end

-- A like prompt on every hotel's sign, for visitors only (`VisitorOnly`, PromptFilter).
local function likePrompt(plot: PlotService.Plot)
	local sign = plot.sign
	local board = sign and sign:FindFirstChild("Board")
	if not board or not plot.owner then
		return
	end
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "Prompt_Like"
	prompt.ActionText = "Like ♥"
	prompt.ObjectText = `{plot.owner.DisplayName}'s Hotel`
	prompt.MaxActivationDistance = 14
	prompt.RequiresLineOfSight = false
	prompt:SetAttribute("VisitorOnly", plot.owner.UserId)
	prompt.Parent = board
	prompt.Triggered:Connect(function(player)
		like(player, plot.index)
	end)
end

-- "Need a Coffin Suite!" (§7): the room the rarest guest on the pinger's street wants, or the generic phrase.
local function needRoom(player: Player): string
	local plot = PlotService.of(player)
	local id = Bus.rarest(BusService.wanted(if plot then plot.street else nil))
	local sp = id and Species.get(id)
	local room = sp and Pieces.get(sp.room)
	if not room then
		return SocialService.Pings.NeedRoom
	end
	local article = if string.find(room.name, "^[AEIOU]") then "an" else "a"
	return `Need {article} {room.name}!`
end

local function ping(player: Player, key: string)
	local text = if key == "NeedRoom" then needRoom(player) else SocialService.Pings[key]
	local character = player.Character
	local head = character and character:FindFirstChild("Head")
	if not text or not head then
		return
	end
	local old = head:FindFirstChild("Ping")
	if old then
		old:Destroy()
	end
	local bb = Instance.new("BillboardGui")
	bb.Name = "Ping"
	bb.Size = UDim2.fromOffset(240, 50)
	bb.StudsOffset = Vector3.new(0, 3, 0)
	bb.MaxDistance = 120
	bb.LightInfluence = 0
	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundColor3 = Color3.fromRGB(46, 32, 70)
	label.BackgroundTransparency = 0.15
	label.TextColor3 = Color3.fromRGB(255, 230, 180)
	label.Font = Enum.Font.FredokaOne
	label.TextScaled = true
	label.Text = text
	label.Parent = bb
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 12)
	corner.Parent = label
	bb.Parent = head
	task.delay(4, function()
		bb:Destroy()
	end)
end

--[[ VIP Lobby's badge and gold name tag (§10.2): a gold name over the
	head with "VIP" before it, in place of Roblox's own name, and the
	player's `VIP` attribute for anything else that shows the badge. Kept in
	step with the pass however it arrives (bought, gifted, restored), so it
	is checked every few seconds rather than on one event. The look is a
	draft (WAITING §2). ]]
local function vipTag(player: Player)
	local data = PlayerData.get(player)
	local vip = data ~= nil and data.passes.VIPLobby == true
	if player:GetAttribute("VIP") ~= vip then
		player:SetAttribute("VIP", vip)
	end
	local character = player.Character
	local head = character and character:FindFirstChild("Head")
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if not head or not humanoid then
		return
	end
	local tag = head:FindFirstChild("VipTag")
	if vip and not tag then
		local bb = Instance.new("BillboardGui")
		bb.Name = "VipTag"
		bb.Size = UDim2.fromScale(7, 1)
		bb.StudsOffset = Vector3.new(0, 1.8, 0)
		bb.MaxDistance = 100
		bb.LightInfluence = 0
		local label = Instance.new("TextLabel")
		label.Size = UDim2.fromScale(1, 1)
		label.BackgroundTransparency = 1
		label.TextColor3 = Color3.fromRGB(255, 205, 80)
		label.TextStrokeColor3 = Color3.fromRGB(46, 32, 70)
		label.TextStrokeTransparency = 0
		label.Font = Enum.Font.FredokaOne
		label.TextScaled = true
		label.Text = `VIP  {player.DisplayName}`
		label.Parent = bb
		bb.Parent = head
		humanoid.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	elseif not vip and tag then
		tag:Destroy()
		humanoid.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.Viewer
	end
end

-- The street leaderboard in the player list (§7).
local function leaderstats(player: Player)
	local stats = Instance.new("Folder")
	stats.Name = "leaderstats"
	local rating = Instance.new("NumberValue")
	rating.Name = "Rating"
	rating.Parent = stats
	local likes = Instance.new("IntValue")
	likes.Name = "Likes"
	likes.Parent = stats
	stats.Parent = player
	local function update()
		rating.Value = player:GetAttribute("Rating") :: number? or 1
		local data = PlayerData.get(player)
		likes.Value = if data then data.likes else 0
	end
	player:GetAttributeChangedSignal("Rating"):Connect(update)
	update()
end

-- The `Like` remote likes only from where the sign's prompt would (A.11.4: "likes it at the sign"), so no
-- client can like every hotel on the server from anywhere.
local function likeAtSign(player: Player, plotIndex: number)
	local plot = PlotService.all()[plotIndex]
	local board = plot and plot.sign and plot.sign:FindFirstChild("Board")
	local prompt = board and board:FindFirstChild("Prompt_Like")
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	if
		not (board and board:IsA("BasePart") and prompt and prompt:IsA("ProximityPrompt"))
		or not (root and root:IsA("BasePart"))
		or (root.Position - board.Position).Magnitude > prompt.MaxActivationDistance + 4
	then
		return
	end
	like(player, plotIndex)
end

function SocialService.Init()
	Net.on("Like", likeAtSign)
	Net.on("Ping", ping)
	Net.on("Visit", visit)
end

function SocialService.Start()
	Income.setFriends(function()
		return friendsOnline
	end)
	PlayerData.onLoaded(function(player, data)
		leaderstats(player)
		recomputeFriends()
		milestones(player, data, false) -- a milestone reached while away
		refreshFavourite()
		StateService.markAll()
	end)
	Players.PlayerRemoving:Connect(function()
		task.defer(recomputeFriends)
		task.defer(refreshFavourite)
		task.defer(StateService.markAll)
	end)
	-- Play time today (the like's rule) and the lobbies walked into (the daily visits), A.11.4.
	task.spawn(function()
		local last = os.clock()
		local week = thisWeek()
		while true do
			task.wait(1)
			local step = os.clock() - last
			last = os.clock()
			-- A new week starts every count at 0: last week's Street Favourite gives up its badge now, not at
			-- the next like, join or leave.
			if thisWeek() ~= week then
				week = thisWeek()
				refreshFavourite()
				StateService.markAll()
			end
			for _, data in PlayerData.loaded() do
				if data.played.day ~= today() then
					data.played = { day = today(), seconds = 0 }
				end
				data.played.seconds += step
			end
			local ok, err = pcall(checkVisits)
			if not ok then
				warn(`[social] visits: {err}`)
			end
		end
	end)
	-- The Showcase panel (A.11.4): this server's hotels by likes this week, each with Visit.
	StateService.provide("showcase", function(player, data)
		local best = Showcase.favourites(entries())
		local list = {}
		for _, plot in PlotService.all() do
			local owner = plot.owner
			local d = owner and PlayerData.get(owner)
			if owner and d then
				local key = tostring(owner.UserId)
				local loc = Locations.get(plot.street)
				table.insert(list, {
					index = plot.index,
					name = owner.DisplayName,
					street = if loc then loc.name else `Street {plot.street}`,
					week = Showcase.weekly(d.likesWeek, thisWeek()),
					likes = d.likes,
					favourite = best[plot.street] == key,
					mine = owner == player,
					liked = data.likesGiven.day == today() and data.likesGiven.plots[key] == true,
				})
			end
		end
		local upcoming = Showcase.nextMilestone(data.likes)
		local played = if data.played.day == today() then data.played.seconds else 0
		return {
			list = list,
			likes = data.likes,
			week = Showcase.weekly(data.likesWeek, thisWeek()),
			nextName = if upcoming then upcoming.name else "",
			nextAt = if upcoming then upcoming.likes else 0,
			likeIn = math.max(0, math.ceil((Constants.Showcase.LikeAfterPlay - played) / 60)),
		}
	end)
	-- A like received from a made-up liker (`likefrom <userId>`): the weekly count, milestones, the badge.
	DevGrant.register("likefrom", function(player, args)
		local data = PlayerData.get(player)
		local plot = PlotService.of(player)
		if not data or not plot then
			return "no data"
		end
		receive(player, data, args[1] or "1")
		return `likes {data.likes} week {Showcase.weekly(data.likesWeek, thisWeek())} favourite {plot.model:GetAttribute(
			"StreetFavourite"
		)}`
	end)
	-- Play time today (`played <seconds>`), for the like's rule.
	DevGrant.register("played", function(player, args)
		local data = PlayerData.get(player)
		if not data then
			return "no data"
		end
		data.played = { day = today(), seconds = tonumber(args[1]) or 0 }
		return `played {data.played.seconds}`
	end)
	--[[ `visit <ownerId>` counts a visit as if the player had walked into that
		owner's lobby; `visit here` says whether the player stands in their own. ]]
	DevGrant.register("visit", function(player, args)
		local data = PlayerData.get(player)
		local plot = PlotService.of(player)
		if not data or not plot then
			return "no data"
		end
		if args[1] == "here" then
			local character = player.Character
			local root = character and character:FindFirstChild("HumanoidRootPart")
			return if root and root:IsA("BasePart")
				then tostring(
					Showcase.inside(data.tiles, plot.frame:PointToObjectSpace(root.Position))
				)
				else "no character"
		end
		visited(player, data, args[1] or "1", `#{args[1] or "1"}`)
		return `visited {data.stats.hotelsVisited or 0}`
	end)
	PlotService.onBuilt(likePrompt)
	task.spawn(function()
		while true do
			task.wait(2)
			for _, player in Players:GetPlayers() do
				pcall(vipTag, player)
			end
		end
	end)
	DevGrant.register("likes", function(player, args)
		local data = PlayerData.get(player)
		if data then
			data.likes = tonumber(args[1]) or 5
			SocialService.likesChanged()
		end
		return "ok"
	end)
end

return SocialService
