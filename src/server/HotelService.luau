--!strict
--[[
	Each hotel's live state, which is not saved (GDD §4.4, §5.3): which rooms
	are vacant, reserved, occupied or dirty, the desk queue, what recent stays
	were like, and the rating computed from all of it.

	The saved layout is `PlayerData`'s; this is what the layout is doing now.
	`GuestService` moves guests through it, `BuildService` asks whether a room
	is busy before selling or moving it, the bus asks which hotels can take a
	guest and how they score.

	Published (copies for drawing): the player's `Rating` attribute, and on the
	plot model `Rating`, `Categories` (JSON), `Featured` (the room types it
	has) and `Likes`. The sign's text is set here.
]]

local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Rating = require(ReplicatedStorage.Shared.Rating)
local Species = require(ReplicatedStorage.Shared.Species)
local Stay = require(ReplicatedStorage.Shared.Stay)
local Format = require(ReplicatedStorage.Shared.Format)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local PlotService = require(ServerScriptService.Server.PlotService)

local HotelService = {}

export type RoomState = "Vacant" | "Reserved" | "Occupied" | "Dirty"
export type Room = {
	state: RoomState,
	guest: number?,
	dirtySince: number?,
	request: string?, -- the open request's text
}
export type Hotel = {
	player: Player,
	rooms: { [string]: Room },
	queue: { number }, -- guest ids at the desk, first first
	rating: number,
	categories: Rating.Categories?,
	waits: { number },
	prefsShares: { number },
	requestsAsked: number,
	requestsDone: number,
	staffBonus: { [string]: number }, -- set by the staff system: Entertainment count etc.
}

local hotels: { [Player]: Hotel } = {}
local ratingHandlers: { (Player, number, number) -> () } = {}

-- Called when a hotel's rating changes (new, old).
function HotelService.onRating(handler: (Player, number, number) -> ())
	table.insert(ratingHandlers, handler)
end

local function push(list: { number }, v: number, keep: number)
	table.insert(list, v)
	while #list > keep do
		table.remove(list, 1)
	end
end

function HotelService.get(player: Player): Hotel?
	return hotels[player]
end

function HotelService.all(): { [Player]: Hotel }
	return hotels
end

-- Brings the room table in line with the layout: new rooms vacant, removed ones gone.
function HotelService.sync(player: Player)
	local hotel = hotels[player]
	local data = PlayerData.get(player)
	if not hotel or not data then
		return
	end
	for id, rec in data.layout do
		local piece = Pieces.get(rec.item)
		if piece and piece.kind == "Room" and not hotel.rooms[id] then
			hotel.rooms[id] = { state = "Vacant" }
		end
	end
	for id in hotel.rooms do
		if not data.layout[id] then
			hotel.rooms[id] = nil
		end
	end
	HotelService.refreshPrompts(player)
end

-- The tags a room has: its own decor and every amenity on its floor (Appendix A.2).
function HotelService.roomTags(data: PlayerData.Data, pieceId: string): { [string]: boolean }
	local tags: { [string]: boolean } = {}
	local rec = data.layout[pieceId]
	if not rec then
		return tags
	end
	for _, decorId in rec.decor do
		local d = Pieces.decor(decorId)
		if d then
			for _, t in d.tags do
				tags[t] = true
			end
		end
	end
	for _, other in data.layout do
		local p = Pieces.get(other.item)
		if p and p.kind == "Amenity" and other.floor == rec.floor and p.tags then
			for _, t in p.tags do
				tags[t] = true
			end
		end
	end
	return tags
end

function HotelService.amenitiesOn(data: PlayerData.Data, floor: number): number
	local n = 0
	for _, rec in data.layout do
		local p = Pieces.get(rec.item)
		if p and p.kind == "Amenity" and rec.floor == floor then
			n += 1
		end
	end
	return n
end

export type Offer = { pieceId: string, prefsMatched: number, amenities: number }

-- The best vacant room for a species: the one matching most of its preferences, or nil.
function HotelService.vacantFor(player: Player, speciesId: string): Offer?
	local hotel = hotels[player]
	local data = PlayerData.get(player)
	local sp = Species.get(speciesId)
	if not hotel or not data or not sp then
		return nil
	end
	local best: Offer? = nil
	for id, room in hotel.rooms do
		local rec = data.layout[id]
		if room.state == "Vacant" and rec and rec.item == sp.room then
			local matched = Stay.matched(sp.prefs, HotelService.roomTags(data, id))
			local amen = HotelService.amenitiesOn(data, rec.floor)
			if
				not best
				or matched > best.prefsMatched
				or (matched == best.prefsMatched and rec.tier > data.layout[best.pieceId].tier)
			then
				best = { pieceId = id, prefsMatched = matched, amenities = amen }
			end
		end
	end
	return best
end

function HotelService.setRoom(player: Player, pieceId: string, state: RoomState, guest: number?)
	local hotel = hotels[player]
	local room = hotel and hotel.rooms[pieceId]
	if not room then
		return
	end
	room.state = state
	room.guest = guest
	room.dirtySince = if state == "Dirty" then os.clock() else nil
	if state ~= "Occupied" then
		room.request = nil
	end
	HotelService.refreshPrompts(player, pieceId)
end

function HotelService.setRequest(player: Player, pieceId: string, text: string?)
	local hotel = hotels[player]
	local room = hotel and hotel.rooms[pieceId]
	if room then
		room.request = text
		HotelService.refreshPrompts(player, pieceId)
	end
end

function HotelService.busy(player: Player, pieceId: string): boolean
	local hotel = hotels[player]
	local room = hotel and hotel.rooms[pieceId]
	return room ~= nil and (room.state == "Reserved" or room.state == "Occupied")
end

-- Sets each room door's prompts and label from its state.
function HotelService.refreshPrompts(player: Player, only: string?)
	local hotel = hotels[player]
	local plot = PlotService.of(player)
	local data = PlayerData.get(player)
	if not hotel or not plot or not data then
		return
	end
	for id, room in hotel.rooms do
		if only == nil or only == id then
			local clean = PlotService.roomPrompt(plot, id, "Clean")
			if clean then
				clean.Enabled = room.state == "Dirty"
			end
			local help = PlotService.roomPrompt(plot, id, "Request")
			if help then
				help.Enabled = room.request ~= nil
				help.ObjectText = room.request or ""
				help.ActionText = "Help"
			end
			local model = plot.pieces[id]
			if model then
				model:SetAttribute("State", room.state)
				model:SetAttribute("Request", room.request)
				local rec = data.layout[id]
				local piece = rec and Pieces.get(rec.item)
				local label = model:FindFirstChild("Label", true)
				local text = label and label:FindFirstChild("Text")
				if text and text:IsA("TextLabel") and piece and rec then
					local suffix = if room.state == "Dirty"
						then " · needs cleaning"
						elseif room.request then " · !"
						elseif room.state == "Vacant" then " · vacant"
						else ""
					text.Text = `{piece.name} T{rec.tier}{suffix}`
				end
			end
		end
	end
end

-- Recent stays, for the rating's Comfort and Service (Appendix A.4).
function HotelService.recordCheckIn(player: Player, waited: number)
	local hotel = hotels[player]
	if hotel then
		push(hotel.waits, waited, Constants.Rating.ServiceSampleSize)
	end
end

function HotelService.recordStay(player: Player, prefsShare: number)
	local hotel = hotels[player]
	if hotel then
		push(hotel.prefsShares, prefsShare, Constants.Rating.ServiceSampleSize)
	end
end

function HotelService.recordRequest(player: Player, done: boolean)
	local hotel = hotels[player]
	if hotel then
		hotel.requestsAsked += 1
		if done then
			hotel.requestsDone += 1
		end
	end
end

local function mean(list: { number }): number
	if #list == 0 then
		return 0
	end
	local s = 0
	for _, v in list do
		s += v
	end
	return s / #list
end

function HotelService.inputs(player: Player): Rating.Inputs?
	local hotel = hotels[player]
	local data = PlayerData.get(player)
	if not hotel or not data then
		return nil
	end
	local tiers, types, decor, amenities, rooms, dirty = {}, {}, 0, 0, 0, 0
	for id, rec in data.layout do
		local p = Pieces.get(rec.item)
		if p then
			if p.kind == "Room" then
				rooms += 1
				table.insert(tiers, rec.tier)
				types[rec.item] = true
				local room = hotel.rooms[id]
				if room and room.state == "Dirty" then
					dirty += 1
				end
			else
				amenities += 1
			end
			for _, d in rec.decor do
				if d ~= "" then
					decor += 1
				end
			end
		end
	end
	local nTypes = 0
	for _ in types do
		nTypes += 1
	end
	return {
		roomTiers = tiers,
		prefsShare = mean(hotel.prefsShares),
		meanWait = mean(hotel.waits),
		checkIns = #hotel.waits,
		requestShare = if hotel.requestsAsked > 0
			then hotel.requestsDone / hotel.requestsAsked
			else 0,
		rooms = rooms,
		dirtyRooms = dirty,
		amenities = amenities,
		entertainers = hotel.staffBonus.Entertainment or 0,
		perks = {
			Service = hotel.staffBonus.PerkService or 0,
			Fun = hotel.staffBonus.PerkFun or 0,
			Cleanliness = hotel.staffBonus.PerkCleanliness or 0,
		},
		decor = decor,
		roomTypes = nTypes,
	}
end

function HotelService.rating(player: Player): number
	local hotel = hotels[player]
	return if hotel then hotel.rating else 1
end

local function updateSign(player: Player, hotel: Hotel)
	local plot = PlotService.of(player)
	local data = PlayerData.get(player)
	if not plot or not plot.sign or not data then
		return
	end
	local board = plot.sign:FindFirstChild("Board")
	if not board or not board:IsA("BasePart") then
		return
	end
	local gui = board:FindFirstChild("SignGui") :: SurfaceGui?
	if not gui then
		local g = Instance.new("SurfaceGui")
		g.Name = "SignGui"
		g.Face = Enum.NormalId.Front
		g.CanvasSize = Vector2.new(480, 180)
		g.LightInfluence = 0
		local label = Instance.new("TextLabel")
		label.Name = "Text"
		label.Size = UDim2.fromScale(1, 1)
		label.BackgroundTransparency = 1
		label.Font = Enum.Font.FredokaOne
		label.TextScaled = true
		label.TextColor3 = Color3.fromRGB(255, 230, 180)
		label.Parent = g
		g.Parent = board
		gui = g
	end
	local featured = {}
	local seen = {}
	for _, rec in data.layout do
		local p = Pieces.get(rec.item)
		if p and p.kind == "Room" and not seen[p.id] then
			seen[p.id] = true
			table.insert(featured, p.name)
		end
	end
	table.sort(featured)
	while #featured > 3 do
		table.remove(featured)
	end
	local label = (gui :: SurfaceGui):FindFirstChild("Text") :: TextLabel
	local badge = if plot.model:GetAttribute("StreetFavourite")
		then "  ★ Street Favourite"
		else ""
	label.Text =
		`{player.DisplayName}'s Hotel{badge}\n{Format.stars(hotel.rating)} · ♥ {data.likes}\n{table.concat(
			featured,
			" · "
		)}`
	plot.model:SetAttribute("Featured", table.concat(featured, ","))
	plot.model:SetAttribute("Likes", data.likes)
end

function HotelService.recompute(player: Player)
	local hotel = hotels[player]
	local data = PlayerData.get(player)
	local inputs = HotelService.inputs(player)
	if not hotel or not data or not inputs then
		return
	end
	local categories = Rating.categories(inputs)
	hotel.categories = categories
	local before = hotel.rating
	hotel.rating = Rating.stars(categories, data.reviews)
	if hotel.rating ~= before then
		for _, h in ratingHandlers do
			task.spawn(h, player, hotel.rating, before)
		end
	end
	player:SetAttribute("Rating", hotel.rating)
	local plot = PlotService.of(player)
	if plot then
		plot.model:SetAttribute("Rating", hotel.rating)
		plot.model:SetAttribute("Categories", HttpService:JSONEncode(categories))
	end
	updateSign(player, hotel)
end

function HotelService.addReview(player: Player, stars: number)
	local data = PlayerData.get(player)
	if data then
		Rating.addReview(data.reviews, stars)
	end
end

function HotelService.Init() end

function HotelService.Start()
	PlayerData.onLoaded(function(player)
		hotels[player] = {
			player = player,
			rooms = {},
			queue = {},
			rating = 1,
			categories = nil,
			waits = {},
			prefsShares = {},
			requestsAsked = 0,
			requestsDone = 0,
			staffBonus = {},
		}
		HotelService.sync(player)
		HotelService.recompute(player)
	end)
	PlayerData.onDeparted(function(player)
		hotels[player] = nil
	end)
	-- A full rebuild makes new prompts: put the room states back on them.
	PlotService.onBuilt(function(plot)
		if plot.owner then
			HotelService.refreshPrompts(plot.owner)
			HotelService.recompute(plot.owner)
		end
	end)
	task.spawn(function()
		while true do
			task.wait(5)
			for player in hotels do
				HotelService.recompute(player)
			end
		end
	end)
end

return HotelService
