--!strict
--[[
	Co-play without chat (GDD §7): since age checks cut on-platform chat,
	everything here works with no typing.

	  - VISIT AND LIKE: walk up to any other hotel's sign and give it one like
	    a day; likes show on the sign, and the most-liked hotel on the street
	    wears "Street Favourite".
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
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Species = require(ReplicatedStorage.Shared.Species)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)
local HotelService = require(ServerScriptService.Server.HotelService)
local Income = require(ServerScriptService.Server.Income)
local BusService = require(ServerScriptService.Server.BusService)
local DevGrant = require(ServerScriptService.Server.DevGrant)

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

-- The most-liked hotel on the street wears the badge.
local function refreshFavourite()
	local best, bestLikes = nil, 0
	for _, plot in PlotService.all() do
		local data = plot.owner and PlayerData.get(plot.owner)
		if data and data.likes > bestLikes then
			best, bestLikes = plot, data.likes
		end
	end
	for _, plot in PlotService.all() do
		plot.model:SetAttribute("StreetFavourite", plot == best)
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
	local ownerData = PlayerData.get(owner)
	if not ownerData then
		return
	end
	data.likesGiven.plots[key] = true
	ownerData.likes += 1
	SocialService.likesChanged()
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

function SocialService.Init()
	Net.on("Like", like)
	Net.on("Ping", ping)
end

function SocialService.Start()
	Income.setFriends(function()
		return friendsOnline
	end)
	PlayerData.onLoaded(function(player)
		leaderstats(player)
		recomputeFriends()
		refreshFavourite()
	end)
	Players.PlayerRemoving:Connect(function()
		task.defer(recomputeFriends)
		task.defer(refreshFavourite)
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
