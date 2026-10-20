--!strict
--[[
	The launch catalog (GDD §10.2): game passes and developer products, with
	the GDD's default prices in Robux. Principles (§10.1): sell convenience,
	capacity, cosmetics and gifts, never winning; no paid random items; no
	countdown offers; never monetize loss.

	The ids are the experience's own, created in Creator Hub on 2026-10-20 at
	the GDD's default prices (WAITING §3.2); a price changed there must be
	changed here too, since the Store shows this one. An entry with id 0 (the
	facade packs, not created until the facades exist) is shown as "coming
	soon" and cannot be bought; the grant behind it is still tested (DevGrant
	`receipt`). `image` names its icon in `UiImages`.

	Facade packs (§10.2, 99–249 each) are passes; what each one wears is a
	Facade-slot cosmetic in `Cosmetics.luau` naming the pass. Their prices
	within the GDD's range are PLACEHOLDERS.

	GIFTS (§10.1 point 4, GDD Appendix A.9): every pass has a developer
	product "Gift: <pass>" at the pass's price (a PLACEHOLDER: the GDD gives no
	gift price), made below from the pass list so the two never drift apart.
	A pass cannot be bought for someone else, which is why a gift is a product.
]]

export type Entry = {
	key: string,
	name: string,
	kind: "Pass" | "Product",
	id: number,
	price: number,
	text: string,
	image: string?, -- its icon's name in UiImages (a ui/ file name)
	gift: string?, -- a gift product: the key of the pass it gives
}

local Store = {}

Store.Entries = {
	-- Game passes (§10.2)
	{
		key = "AutoCollect",
		name = "Auto-Collect Till",
		kind = "Pass",
		id = 2040496945,
		image = "Pass_AutoCollectTill",
		price = 149,
		text = "Till cash goes straight to your wallet.",
	},
	{
		key = "NightManager",
		name = "Night Manager",
		kind = "Pass",
		id = 2040125090,
		image = "Pass_NightManager",
		price = 249,
		text = "Residents earn offline for 8 hours instead of 2.",
	},
	{
		key = "ResidentWingPlus",
		name = "Resident Wing+",
		kind = "Pass",
		id = 2039699307,
		image = "Pass_ResidentWingPlus",
		price = 249,
		text = "+6 Resident Wing slots.",
	},
	{
		key = "ExtraFloor",
		name = "Extra Floor",
		kind = "Pass",
		id = 2037929410,
		image = "Pass_ExtraFloor",
		price = 299,
		text = "+1 floor beyond the cap.",
	},
	{
		key = "VIPLobby",
		name = "VIP Lobby",
		kind = "Pass",
		id = 2042360787,
		image = "Pass_VipLobby",
		price = 399,
		text = "VIP badge, gold name tag, a VIP lounge decor set, +1 daily reroll.",
	},
	-- Facade packs (§10.2): cosmetic only, worn with the build mode's Style tool.
	{
		key = "FacadeGothic",
		name = "Gothic facade pack",
		kind = "Pass",
		id = 0,
		price = 99, -- PLACEHOLDER within §10.2's 99–249
		text = "A Gothic exterior for your hotel. Cosmetic only.",
	},
	{
		key = "FacadeNeon",
		name = "Neon facade pack",
		kind = "Pass",
		id = 0,
		price = 149, -- PLACEHOLDER
		text = "A Neon exterior for your hotel. Cosmetic only.",
	},
	{
		key = "FacadeCandy",
		name = "Candy facade pack",
		kind = "Pass",
		id = 0,
		price = 199, -- PLACEHOLDER
		text = "A Candy exterior for your hotel. Cosmetic only.",
	},
	{
		key = "FacadePirate",
		name = "Pirate facade pack",
		kind = "Pass",
		id = 0,
		price = 249, -- PLACEHOLDER
		text = "A Pirate exterior for your hotel. Cosmetic only.",
	},
	-- Developer products (§10.2)
	{
		key = "StarterPack",
		name = "Starter Pack",
		kind = "Product",
		id = 3720401936,
		image = "Product_StarterPack",
		price = 99,
		text = "Cash, an exclusive Slime facade and a 30-minute 2x Cash boost. Once per player.",
	},
	{
		key = "CallBus",
		name = "Call the Bus",
		kind = "Product",
		id = 3720401997,
		image = "Product_CallTheBus",
		price = 39,
		text = "Brings the next Night Bus now, for the whole street.",
	},
	{
		key = "Cash2x15",
		name = "2x Cash (15 min)",
		kind = "Product",
		id = 3720402003,
		image = "Product_2xCash15m",
		price = 49,
		text = "Double cash for 15 minutes of play.",
	},
	{
		key = "Cash2x60",
		name = "2x Cash (1 hour)",
		kind = "Product",
		id = 3720402012,
		image = "Product_2xCash1h",
		price = 149,
		text = "Double cash for an hour of play.",
	},
	{
		key = "Friendship2x",
		name = "2x Friendship (30 min)",
		kind = "Product",
		id = 3720402025,
		image = "Product_2xFriendship",
		price = 79,
		text = "Happy stays count double for 30 minutes. Never changes odds.",
	},
	{
		key = "CashSmall",
		name = "Cash Pouch",
		kind = "Product",
		id = 3720402037,
		image = "Product_CashSmall",
		price = 49,
		text = "10 minutes of your income.",
	},
	{
		key = "CashMedium",
		name = "Cash Sack",
		kind = "Product",
		id = 3720402053,
		image = "Product_CashMedium",
		price = 149,
		text = "35 minutes of your income.",
	},
	{
		key = "CashLarge",
		name = "Cash Vault",
		kind = "Product",
		id = 3720402063,
		image = "Product_CashLarge",
		price = 449,
		text = "120 minutes of your income.",
	},
	-- The rewarded ad's reward (§10.2): a non-random product granted through ProcessReceipt.
	{
		key = "AdCash2x15",
		name = "2x Cash (ad)",
		kind = "Product",
		id = 3720402161,
		image = "Product_AdCash2x15",
		price = 1, -- Roblox's lowest product price; the ad grants it, nobody pays it
		text = "Watch an ad: double cash for 15 minutes.",
	},
} :: { Entry }

-- A gift product per pass (§10.1 point 4), by the pass's key: its product id and icon.
local GiftIds = {
	AutoCollect = { 3720402071, "Product_Gift_AutoCollectTill" },
	NightManager = { 3720402085, "Product_Gift_NightManager" },
	ResidentWingPlus = { 3720402090, "Product_Gift_ResidentWingPlus" },
	ExtraFloor = { 3720402097, "Product_Gift_ExtraFloor" },
	VIPLobby = { 3720402114, "Product_Gift_VipLobby" },
}
for _, e in table.clone(Store.Entries) do
	if e.kind == "Pass" then
		table.insert(Store.Entries, {
			key = `Gift_{e.key}`,
			name = `Gift: {e.name}`,
			kind = "Product",
			id = if GiftIds[e.key] then GiftIds[e.key][1] else 0,
			image = if GiftIds[e.key] then GiftIds[e.key][2] else nil,
			price = e.price, -- PLACEHOLDER: the pass's own price
			text = `Give {e.name} to a player on your street.`,
			gift = e.key,
		})
	end
end

Store.ByKey = {} :: { [string]: Entry }
for _, e in Store.Entries do
	Store.ByKey[e.key] = e
end

-- What each product grants, in the units its system reads (§10.2).
Store.Boosts = {
	Cash2x15 = { boost = "Cash2x", seconds = 15 * 60 },
	Cash2x60 = { boost = "Cash2x", seconds = 60 * 60 },
	AdCash2x15 = { boost = "Cash2x", seconds = 15 * 60 },
	Friendship2x = { boost = "Friendship2x", seconds = 30 * 60 },
}
Store.CashMinutes = { CashSmall = 10, CashMedium = 35, CashLarge = 120 }
Store.StarterPack = { cashMinutes = 10, minCash = 500, boost = "Cash2x", seconds = 30 * 60 } -- PLACEHOLDER amounts

function Store.byId(kind: string, id: number): Entry?
	if id == 0 then
		return nil
	end
	for _, e in Store.Entries do
		if e.kind == kind and e.id == id then
			return e
		end
	end
	return nil
end

return Store
