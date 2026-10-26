--!strict
--[[
	Robux (GDD §10, §13.3 "Purchases"). One `ProcessReceipt` handler: grant,
	save, THEN acknowledge, deduplicated by PurchaseId (`PlayerData.grantOnce`)
	so a retry never grants twice. `NotProcessedYet` means "later", never "no".

	Passes are read at join (`UserOwnsGamePassAsync`) and when bought, and
	cached in the profile's `passes` for the systems that read them
	(AutoCollect: GuestService; NightManager, ResidentWingPlus:
	ResidentService; ExtraFloor: BuildService; VIPLobby: dailies).

	Timed boosts (§10.2) count down in PLAY time (the profile's `boosts`,
	seconds left), so a boost bought before bed is not wasted.

	Rewarded ads (§10.2): optional, 13+ only (`PolicyService`), and the reward
	is a non-random developer product granted through ProcessReceipt.

	Gift passes (§10.1 point 4; GDD Appendix A.9, WAITING §2.6's recommended
	option): the giver picks a player on the street, the target is saved in
	the giver's `giftTo`, and the gift product's receipt sends the pass to the
	recipient's PROFILE as a message (`PlayerData.message`), so it arrives even
	if they left before the purchase finished. The recipient keeps it in
	`gifted`, which the join's ownership check never clears.

	Every id is a placeholder (`Store.luau`) until August creates them
	(WAITING.md §3).
]]

local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local PolicyService = game:GetService("PolicyService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local Store = require(ReplicatedStorage.Shared.Store)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local GuestService = require(ServerScriptService.Server.GuestService)
local ResidentService = require(ServerScriptService.Server.ResidentService)
local BusService = require(ServerScriptService.Server.BusService)
local StateService = require(ServerScriptService.Server.StateService)
local Income = require(ServerScriptService.Server.Income)
local Analytics = require(ServerScriptService.Server.Analytics)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local StoreService = {}

-- What the player earns per second now: guests in rooms and the Wing (for cash packs, §10.2).
function StoreService.incomeRate(player: Player): number
	local data = PlayerData.get(player)
	local rate = 0
	for _, g in GuestService.of(player) do
		if g.state == "InRoom" then
			rate += g.payRate
		end
	end
	if data then
		rate += ResidentService.rate(player, data)
	end
	return math.max(rate, Constants.Economy.BasePay * Constants.Economy.RewardFloor)
end

local function addBoost(data: PlayerData.Data, name: string, seconds: number)
	data.boosts[name] = (data.boosts[name] or 0) + seconds
end

-- The grant behind each product: changes `data`, returns true. Runs inside grantOnce.
local function grantFor(player: Player, key: string): ((PlayerData.Data) -> boolean)?
	local boost = Store.Boosts[key]
	if boost then
		return function(data)
			addBoost(data, boost.boost, boost.seconds)
			return true
		end
	end
	local minutes = Store.CashMinutes[key]
	if minutes then
		local amount = math.floor(StoreService.incomeRate(player) * minutes * 60)
		return function(data)
			data.cash += amount
			player:SetAttribute("Cash", data.cash)
			return true
		end
	end
	if key == "StarterPack" then
		local s = Store.StarterPack
		local amount =
			math.max(s.minCash, math.floor(StoreService.incomeRate(player) * s.cashMinutes * 60))
		return function(data)
			data.cash += amount
			data.cosmetics.Cosmetic_SlimeFacade = true
			data.cosmetics.StarterPack = true
			addBoost(data, s.boost, s.seconds)
			player:SetAttribute("Cash", data.cash)
			return true
		end
	end
	local entry = Store.ByKey[key]
	local pass = entry and entry.gift
	if pass then
		return function(data)
			-- A target lost (a retry on another server after a crash) gives the pass to the giver,
			-- never nothing: a paid purchase is always granted (Appendix A.9).
			local to = data.giftTo[pass] or player.UserId
			local sent = PlayerData.message(to, {
				kind = "GiftPass",
				pass = pass,
				from = player.DisplayName,
			})
			if not sent then
				return false
			end
			data.giftTo[pass] = nil
			return true
		end
	end
	if key == "CallBus" then
		return function()
			BusService.callNow(player.DisplayName)
			return true
		end
	end
	return nil
end

local function processReceipt(receipt: any): Enum.ProductPurchaseDecision
	local player = Players:GetPlayerByUserId(receipt.PlayerId)
	if not player then
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	local entry = Store.byId("Product", receipt.ProductId)
	if not entry then
		warn(`[store] unknown product {receipt.ProductId}`)
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	local grant = grantFor(player, entry.key)
	if not grant then
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	local saved = PlayerData.grantOnce(player, tostring(receipt.PurchaseId), grant)
	if not saved then
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	Net.fire(player, "Toast", `Thank you! {entry.name}`, "Unlock")
	Analytics.event(player, `Bought_{entry.key}`, receipt.CurrencySpent or 0)
	StateService.mark(player)
	return Enum.ProductPurchaseDecision.PurchaseGranted
end

local function refreshPasses(player: Player)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	for _, e in Store.Entries do
		if e.kind == "Pass" and e.id ~= 0 then
			local ok, owns = pcall(
				MarketplaceService.UserOwnsGamePassAsync,
				MarketplaceService,
				player.UserId,
				e.id
			)
			if ok then
				data.passes[e.key] = owns or data.gifted[e.key] or nil
			end
		end
	end
	StateService.mark(player)
end

local function buy(player: Player, key: string)
	local e = Store.ByKey[key]
	local data = PlayerData.get(player)
	-- Not the ad's product, nor a gift (only through `Gift`, its player picked): Store.buyable.
	if not e or not data or not Store.buyable(key) then
		return
	end
	if e.id == 0 then
		Net.fire(player, "Toast", `{e.name} is coming soon!`, "Bad")
		return
	end
	if e.kind == "Pass" then
		if data.passes[e.key] then
			Net.fire(player, "Toast", "You already own it.", "Bad")
			return
		end
		MarketplaceService:PromptGamePassPurchase(player, e.id)
	else
		if e.key == "StarterPack" and data.cosmetics.StarterPack then
			Net.fire(player, "Toast", "You already have the Starter Pack.", "Bad")
			return
		end
		MarketplaceService:PromptProductPurchase(player, e.id)
	end
end

-- A gift (§10.1 point 4): a pass for another player on the street, bought as its gift product.
local function gift(player: Player, pass: string, userId: number)
	local e = Store.ByKey[`Gift_{pass}`]
	local data = PlayerData.get(player)
	local target = Players:GetPlayerByUserId(userId)
	if not e or not data then
		return
	end
	if not target or target == player then
		Net.fire(player, "Toast", "Pick another player on your street.", "Bad")
		return
	end
	local theirs = PlayerData.get(target)
	if not theirs then
		return
	end
	if theirs.passes[pass] then
		Net.fire(
			player,
			"Toast",
			`{target.DisplayName} already has {Store.ByKey[pass].name}.`,
			"Bad"
		)
		return
	end
	if e.id == 0 then
		Net.fire(player, "Toast", "Gifts are coming soon!", "Bad")
		return
	end
	data.giftTo[pass] = userId
	MarketplaceService:PromptProductPurchase(player, e.id)
end

-- A pass given to this player (a gift product's message, from any server).
local function receiveGift(player: Player, data: PlayerData.Data, message: any): boolean
	if typeof(message) ~= "table" or message.kind ~= "GiftPass" then
		return false
	end
	local e = Store.ByKey[message.pass]
	if e and e.kind == "Pass" then
		data.gifted[e.key] = true
		data.passes[e.key] = true
		Net.fire(player, "Toast", `{message.from or "A friend"} gave you {e.name}!`, "Unlock")
		Analytics.event(player, `Gifted_{e.key}`)
		StateService.mark(player)
	end
	return true -- taken: a message for a pass that no longer exists is dropped, not kept forever
end

-- A rewarded video ad (§10.2): optional, 13+, its reward a product granted by ProcessReceipt.
local function ad(player: Player)
	local entry = Store.ByKey.AdCash2x15
	if entry.id == 0 then
		Net.fire(player, "Toast", "Ads are coming soon!", "Bad")
		return
	end
	local ok, policy = pcall(PolicyService.GetPolicyInfoForPlayerAsync, PolicyService, player)
	if not ok or not policy or policy.AreAdsAllowed == false then
		Net.fire(player, "Toast", "Ads aren't available for you.", "Bad")
		return
	end
	local shown, err = pcall(function()
		local AdService = game:GetService("AdService") :: any
		local reward = AdService:CreateAdRewardFromDevProductId(entry.id)
		AdService:ShowRewardedVideoAdAsync(player, reward)
	end)
	if not shown then
		warn(`[store] rewarded ad failed: {err}`)
		Net.fire(player, "Toast", "No ad right now. Try again later!", "Bad")
	end
end

-- Boosts count down in play time.
local function boostTick(dt: number)
	for player, data in PlayerData.loaded() do
		local changed = false
		for name, left in data.boosts do
			local now = left - dt
			if now <= 0 then
				data.boosts[name] = nil
				Net.fire(
					player,
					"Toast",
					`Your {name == "Cash2x" and "2x Cash" or "2x Friendship"} boost ran out.`,
					nil
				)
				changed = true
			else
				data.boosts[name] = now
			end
		end
		player:SetAttribute("BoostCash", data.boosts.Cash2x)
		player:SetAttribute("BoostFriendship", data.boosts.Friendship2x)
		if changed then
			StateService.mark(player)
		end
	end
end

function StoreService.Init()
	MarketplaceService.ProcessReceipt = processReceipt
	Net.on("Buy", buy)
	Net.on("Gift", gift)
	PlayerData.onMessage(receiveGift)
	Net.on("Ad", ad)
end

function StoreService.Start()
	Income.addBoost(function(player)
		local data = PlayerData.get(player)
		return if data and (data.boosts.Cash2x or 0) > 0 then 2 else 1
	end)
	ResidentService.addFriendship(function(player)
		local data = PlayerData.get(player)
		return if data and (data.boosts.Friendship2x or 0) > 0 then 2 else 1
	end)
	PlayerData.onLoaded(function(player)
		task.spawn(refreshPasses, player)
	end)
	MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player, passId, bought)
		if bought then
			local e = Store.byId("Pass", passId)
			local data = PlayerData.get(player)
			if e and data then
				data.passes[e.key] = true
				Net.fire(player, "Toast", `Thank you! {e.name} is yours.`, "Unlock")
				StateService.mark(player)
			end
		end
	end)
	StateService.provide("store", function(player, data)
		local entries = {}
		for _, e in Store.Entries do
			if e.gift then
				continue -- drawn as the Gift button on its pass's row
			end
			local giftEntry = Store.ByKey[`Gift_{e.key}`]
			table.insert(entries, {
				key = e.key,
				name = e.name,
				kind = e.kind,
				price = e.price,
				text = e.text,
				image = e.image,
				onSale = e.id ~= 0,
				owned = (e.kind == "Pass" and data.passes[e.key] == true)
					or (e.key == "StarterPack" and data.cosmetics.StarterPack == true),
				giftable = giftEntry ~= nil,
				giftOnSale = giftEntry ~= nil and giftEntry.id ~= 0,
			})
		end
		local cash = {}
		for key, minutes in Store.CashMinutes do
			cash[key] = Format.cash(math.floor(StoreService.incomeRate(player) * minutes * 60))
		end
		return { entries = entries, cash = cash, boosts = data.boosts }
	end)
	DevGrant.register("receipt", function(player, args)
		-- Runs a product's grant through grantOnce with a fake purchase id: what ProcessReceipt does.
		local key = args[1] or "Cash2x15"
		local grant = grantFor(player, key)
		if not grant then
			return `no grant for {key}`
		end
		local id = args[2] or `dev-{os.clock()}`
		local ok = PlayerData.grantOnce(player, id, grant)
		return `{key} purchase {id}: saved={ok}`
	end)
	DevGrant.register("gift", function(player, args)
		-- A gift product's receipt for `args[1]` (a pass key) to UserId `args[2]` (default: yourself).
		local pass = args[1] or "NightManager"
		local data = PlayerData.get(player)
		if not data or not Store.ByKey[`Gift_{pass}`] then
			return `no gift for {pass}`
		end
		data.giftTo[pass] = tonumber(args[2]) or player.UserId
		local ok = PlayerData.grantOnce(
			player,
			`dev-gift-{os.clock()}`,
			grantFor(player, `Gift_{pass}`) :: any
		)
		return `gift {pass} to {data.giftTo[pass] or "sent"}: saved={ok}`
	end)
	DevGrant.register("pass", function(player, args)
		local data = PlayerData.get(player)
		if data then
			data.passes[args[1] or "AutoCollect"] = true
			StateService.mark(player)
		end
		return "ok"
	end)
	task.spawn(function()
		while true do
			local dt = task.wait(1)
			pcall(boostTick, dt)
		end
	end)
end

return StoreService
