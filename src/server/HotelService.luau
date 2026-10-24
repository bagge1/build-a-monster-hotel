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
local Furnish = require(ReplicatedStorage.Shared.Furnish)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local Rating = require(ReplicatedStorage.Shared.Rating)
local Rooms = require(ReplicatedStorage.Shared.Rooms)
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
	cleanTimes: { number }, -- seconds each recent cleaning's room stood dirty (§5.3)
	staffBonus: { [string]: number }, -- set by the staff system: Entertainment count etc.
}

local hotels: { [Player]: Hotel } = {}

--[[ The rating's samples of the chain's hotels not being played (§6.4: the
	rating is each hotel's own), by location, this session. ]]
type Samples = {
	waits: { number },
	prefsShares: { number },
	requestsAsked: number,
	requestsDone: number,
	cleanTimes: { number },
}
local away: { [Player]: { [number]: Samples } } = {}

--[[ Travel (ChainService): the samples of the hotel left are put away under
	`from`, and `to`'s taken out, empty for a hotel never played this
	session. `to` nil forgets them all (a rebirth). ]]
function HotelService.switchSamples(player: Player, from: number, to: number?)
	local hotel = hotels[player]
	if not hotel then
		return
	end
	local bank = away[player] or {}
	away[player] = bank
	if to == nil then
		table.clear(bank)
	else
		bank[from] = {
			waits = hotel.waits,
			prefsShares = hotel.prefsShares,
			requestsAsked = hotel.requestsAsked,
			requestsDone = hotel.requestsDone,
			cleanTimes = hotel.cleanTimes,
		}
	end
	local s = if to then bank[to] else nil
	if to then
		bank[to] = nil
	end
	hotel.waits = if s then s.waits else {}
	hotel.prefsShares = if s then s.prefsShares else {}
	hotel.requestsAsked = if s then s.requestsAsked else 0
	hotel.requestsDone = if s then s.requestsDone else 0
	hotel.cleanTimes = if s then s.cleanTimes else {}
end
local ratingHandlers: { (Player, number, number) -> () } = {}

-- Called when a hotel's rating changes (new, old).
function HotelService.onRating(handler: (Player, number, number) -> ())
	table.insert(ratingHandlers, handler)
end

local unreadyHandlers: { (Player, string) -> () } = {}

--[[ Called (player, room id) when a room a guest is in or due at is no longer
	ready (§5.4, A.12): the guest must not stay. Whatever change let it
	through, the guest is sent back (GuestService). ]]
function HotelService.onUnready(handler: (Player, string) -> ())
	table.insert(unreadyHandlers, handler)
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

local function world(data: PlayerData.Data): Rooms.World
	return PlotService.world(data)
end

--[[ Each built room's readiness (A.12), by id: a room is booked only while
	ready. Asked often, so cached per change of the hotel (`sync`). ]]
local readyCache: { [Player]: { [string]: boolean } } = {}
local readinessCache: { [Player]: Rooms.Readiness } = {} -- with what each room lacks, for the build panel

--[[ Each built room's bars, area size and decor, by profile and room id,
	kept until the hotel next changes (`sync` drops them): the build and VIP
	panels ask for every room's every 15 s, and a full hotel's 44 took a
	third of a second each time (2026-10-24 evening, a server hitch). ]]
export type RoomInfo = { bars: Rooms.Bars, size: number, decor: { string } }
local infoCache: { [PlayerData.Data]: { [string]: RoomInfo } } = setmetatable({}, { __mode = "k" }) :: any

function HotelService.ready(player: Player, roomId: string): boolean
	local cache = readyCache[player]
	return cache ~= nil and cache[roomId] == true
end

--[[ Brings the room table in line with the built rooms (A.12): a ready room
	is a room guests can be booked into (Vacant when new); a room no longer
	ready leaves the table once nobody is in it or due, and a removed one goes. ]]
function HotelService.sync(player: Player)
	local hotel = hotels[player]
	local data = PlayerData.get(player)
	if not hotel or not data then
		return
	end
	infoCache[data] = nil
	local all = Rooms.readiness(world(data))
	readinessCache[player] = all
	local cache = {}
	for id, rec in data.rooms do
		local p = Pieces.get(rec.type)
		local ok = p ~= nil and all[id].ok
		cache[id] = ok
		-- Amenities are rooms too (their tags and Fun), but no guest is booked into one.
		if ok and p and p.kind == "Room" and not hotel.rooms[id] then
			hotel.rooms[id] = { state = "Vacant" }
		end
	end
	readyCache[player] = cache
	local unready = {}
	for id, room in hotel.rooms do
		if not cache[id] and (room.state == "Reserved" or room.state == "Occupied") then
			table.insert(unready, id) -- freed by the handlers, dropped on the next sync
		elseif not data.rooms[id] or (not cache[id] and room.state == "Vacant") then
			hotel.rooms[id] = nil
		end
	end
	for _, id in unready do
		for _, h in unreadyHandlers do
			h(player, id)
		end
	end
	HotelService.refreshPrompts(player)
end

-- A room's three bars and what they give (A.12); nil for a room that is not there.
function HotelService.roomBars(data: PlayerData.Data, roomId: string): (Rooms.Bars?, Rooms.Bonuses?)
	local info = HotelService.roomInfo(data, roomId)
	if not info then
		return nil, nil
	end
	return info.bars, Rooms.bonuses(info.bars)
end

-- Every built room's readiness and what it lacks, as of the last `sync` (nil before the first).
function HotelService.readiness(player: Player): Rooms.Readiness?
	return readinessCache[player]
end

-- A room's bars, its area's size and the decor in it (nil for a room that is not there), kept until `sync`.
function HotelService.roomInfo(data: PlayerData.Data, roomId: string): RoomInfo?
	if not data.rooms[roomId] then
		return nil
	end
	local cache = infoCache[data]
	if not cache then
		cache = {}
		infoCache[data] = cache
	end
	if not cache[roomId] then
		-- Every room's at once: the panels ask for them all, and the floor's areas are then worked out once.
		local w = world(data)
		Rooms.withAreas(w, function()
			for id in data.rooms do
				if not cache[id] then
					local a = Rooms.roomArea(w, id)
					local decor = {}
					for _, d in Rooms.contents(w, id).decor do
						table.insert(decor, d.item)
					end
					cache[id] =
						{ bars = Rooms.bars(w, id), size = if a then a.size else 0, decor = decor }
				end
			end
		end)
	end
	return cache[roomId]
end

--[[ The tags a room has (§5.4, A.12): its furniture's and decor's, and every
	ready amenity's on its floor (Appendix A.2). ]]
function HotelService.roomTags(data: PlayerData.Data, roomId: string): { [string]: boolean }
	local rec = data.rooms[roomId]
	if not rec then
		return {}
	end
	local w = world(data)
	local items = {}
	local c = Rooms.contents(w, roomId)
	for _, d in c.furniture do
		table.insert(items, d.item)
	end
	for _, d in c.decor do
		table.insert(items, d.item)
	end
	local tags = Furnish.tags(items)
	for id, other in data.rooms do
		local p = Pieces.get(other.type)
		if
			p
			and p.kind == "Amenity"
			and other.floor == rec.floor
			and p.tags
			and Rooms.ready(w, id)
		then
			for _, t in p.tags do
				tags[t] = true
			end
		end
	end
	return tags
end

-- The ready amenities on a floor (A.12: built like rooms).
function HotelService.amenitiesOn(data: PlayerData.Data, floor: number): number
	local n = 0
	local w = world(data)
	for id, rec in data.rooms do
		local p = Pieces.get(rec.type)
		if p and p.kind == "Amenity" and rec.floor == floor and Rooms.ready(w, id) then
			n += 1
		end
	end
	return n
end

-- The ready rooms of a type (for the milestones' count, §6.2).
function HotelService.readyOfType(player: Player, data: PlayerData.Data, typeId: string): number
	local n = 0
	for id, rec in data.rooms do
		if rec.type == typeId and HotelService.ready(player, id) then
			n += 1
		end
	end
	return n
end

export type Offer = { pieceId: string, prefsMatched: number, amenities: number }

-- The best vacant ready room of a species' type (A.12): the one matching most of its preferences, or nil.
function HotelService.vacantFor(player: Player, speciesId: string): Offer?
	local hotel = hotels[player]
	local data = PlayerData.get(player)
	local sp = Species.get(speciesId)
	if not hotel or not data or not sp then
		return nil
	end
	local best: Offer? = nil
	for id, room in hotel.rooms do
		local rec = data.rooms[id]
		if
			room.state == "Vacant"
			and rec
			and rec.type == sp.room
			and HotelService.ready(player, id)
		then
			local matched = Stay.matched(sp.prefs, HotelService.roomTags(data, id))
			local amen = HotelService.amenitiesOn(data, rec.floor)
			if not best or matched > best.prefsMatched then
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
	-- A room leaving Dirty was cleaned: how long it stood dirty feeds
	-- Cleanliness's "rooms cleaned on time" (§5.3, Appendix A.4).
	if room.state == "Dirty" and state ~= "Dirty" and room.dirtySince and hotel then
		push(hotel.cleanTimes, os.clock() - room.dirtySince, Constants.Rating.CleanSampleSize)
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

-- Whether a room is waiting to be cleaned: it may not be retyped or cleared, or it would come back clean.
function HotelService.dirty(player: Player, pieceId: string): boolean
	local hotel = hotels[player]
	local room = hotel and hotel.rooms[pieceId]
	return room ~= nil and room.state == "Dirty"
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
		end
	end
	-- Every built room's plaque: its name, and its state or what it lacks (A.12 "Ready").
	local w = world(data)
	-- The whole hotel's plaques: what `sync` worked out just before, or worked out now.
	local all = if only == nil then (readinessCache[player] or Rooms.readiness(w)) else nil
	for id, rec in data.rooms do
		if only == nil or only == id then
			local model = plot.pieces[id]
			local piece = Pieces.get(rec.type)
			if model and piece then
				local room = hotel.rooms[id]
				local ok, missing
				local r = all and all[id]
				if r then
					ok, missing = r.ok, r.missing
				else
					ok, missing = Rooms.ready(w, id)
				end
				model:SetAttribute("State", if room then room.state else nil)
				model:SetAttribute("Request", if room then room.request else nil)
				model:SetAttribute("Ready", ok)
				local label = model:FindFirstChild("Label", true)
				local text = label and label:FindFirstChild("Text")
				if text and text:IsA("TextLabel") then
					local state = if not ok
						then HotelService.missingText(rec.type, missing or {})
						elseif not room then ""
						elseif room.state == "Dirty" then "needs cleaning"
						elseif room.request then "!"
						elseif room.state == "Vacant" then "vacant"
						else ""
					-- The plaque has a line of its own for the state.
					local status = label and label:FindFirstChild("Status")
					if status and status:IsA("TextLabel") then
						text.Text = piece.name
						status.Text = state
					else
						text.Text = `{piece.name}{if state ~= "" then " · " .. state else ""}`
					end
				end
			end
		end
	end
end

-- What a room lacks to be ready (Rooms.ready's list), in words.
function HotelService.missingText(typeId: string, missing: { string }): string
	local req = Rooms.requirement(typeId)
	local first = missing[1]
	if first == "KeyFurniture" and req then
		local names = {}
		for _, k in req.keys do
			local d = Pieces.decor(k)
			table.insert(names, if d then d.name else k)
		end
		return `needs a {table.concat(names, " or ")}`
	elseif first == "MinSize" and req then
		return `needs {req.minCells} cells`
	elseif first == "Door" then
		return "needs a door"
	elseif first == "Unreached" then
		return "guests can't reach it"
	elseif first == "KeyUnreached" and req then
		-- Its key furniture is walled or furnished off from the door (A.12 "Ready").
		local names = {}
		for _, k in req.keys do
			local d = Pieces.decor(k)
			table.insert(names, if d then d.name else k)
		end
		return `guests can't get to the {table.concat(names, " or ")}`
	elseif first == "Hallway" then
		return "not closed off"
	end
	return "not ready"
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
	local bars, types, decor, amenities, rooms, dirty = {}, {}, 0, 0, 0, 0
	local overdue, now = 0, os.clock()
	local w = world(data)
	-- Ready rooms only (A.12: Comfort and Cleanliness count what each ready room adds).
	for id, rec in data.rooms do
		local p = Pieces.get(rec.type)
		local ok = HotelService.ready(player, id)
		if p and ok then
			table.insert(bars, Rooms.bars(w, id))
		end
		if p and ok and p.kind == "Room" then
			rooms += 1
			types[rec.type] = true
			local room = hotel.rooms[id]
			if room and room.state == "Dirty" then
				dirty += 1
				-- Dirty past the limit now: late already, before anyone cleans it.
				if room.dirtySince and now - room.dirtySince > Constants.Rating.CleanOnTime then
					overdue += 1
				end
			end
		elseif p and ok and p.kind == "Amenity" then
			amenities += 1
		end
	end
	-- Style counts every piece of decor, in rooms and on hallway floor (§5.4).
	for _ in data.decor do
		decor += 1
	end
	local nTypes = 0
	for _ in types do
		nTypes += 1
	end
	-- Rooms cleaned on time (§5.3): the share of recent cleanings within the
	-- limit, every room overdue now counted as a late one.
	local onTime = 0
	for _, t in hotel.cleanTimes do
		if t <= Constants.Rating.CleanOnTime then
			onTime += 1
		end
	end
	local judged = #hotel.cleanTimes + overdue
	return {
		roomBars = bars,
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
		-- Staff coverage (§5.3): each role's summed efficiency, set by ResidentService.
		frontDesk = hotel.staffBonus.FrontDesk or 0,
		roomService = hotel.staffBonus.RoomService or 0,
		housekeeping = hotel.staffBonus.Housekeeping or 0,
		onTimeShare = if judged > 0 then onTime / judged else 0,
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
	for id, rec in data.rooms do
		local p = Pieces.get(rec.type)
		if p and p.kind == "Room" and not seen[p.id] and HotelService.ready(player, id) then
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
			cleanTimes = {},
			staffBonus = {},
		}
		HotelService.sync(player)
		HotelService.recompute(player)
	end)
	PlayerData.onDeparted(function(player)
		hotels[player] = nil
		away[player] = nil
		readyCache[player] = nil
		readinessCache[player] = nil
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
