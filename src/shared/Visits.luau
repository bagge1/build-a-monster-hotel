--!strict
--[[
	Visits (GDD A.13.1, night draft 2026-10-26): while it stays, a guest
	leaves its room now and then for an activity room whose tags meet one of
	its preferences, takes a free spot there, does the action for a while and
	walks back. Pure rules, no engine calls, so the server's GuestService and
	the specs read the same answers:

	- who may visit where: an activity room (kind "Amenity": today's amenities
	  and A.13.2's types) that is ready, reachable from the guest's room (the
	  caller's flag: `Rooms.route` found a way, not merely the same floor, as
	  `amenitiesOn` did) and has a free spot, whose tags meet a preference;
	- spots: a room's capacity is its usable spots (`Use_<n>` on its activity
	  furniture, MODELS.md, with a square in the room a visitor steps onto it
	  from, `Rooms.spotApproach`; listed by the caller). A spot is named by its
	  piece's decor id and its number (`Visits.spotKey`, "12:2"), never by its
	  place in a list, so selling or moving another piece never moves it. One
	  guest a spot, one spot a guest; a spot is taken when the guest sets out
	  (`Visits.begin`), so two never walk to the same one, and freed when it
	  leaves; a visitor whose piece is sold or moved is sent back
	  (`Visits.stranded`, `Visits.onPiece`);
	- when: every 90–150 s of a stay, at most one decision a guest per 10 s,
	  at most 12 visitors walking at once per hotel, so a full hotel does not
	  route every frame, and only while the stay has time left for the walk
	  and the shortest action (`Visits.fits`);
	- what a visit gives: the preferences it meets count as met for the stay,
	  and +5 satisfaction once a stay;
	- busy: a room with a visitor in it or on the way is busy (`Rooms.keepsBusy`).

	The server keeps, per hotel, `Taken` (the spots) and `Visitors` (guest id ->
	its visit), and per guest the time its next visit is due and its last
	decision. A guest's own room stays Occupied while it is out.
]]

local Constants = require(script.Parent.Constants)
local Pieces = require(script.Parent.Pieces)

local Visits = {}

-- Every number of A.13.1, PLACEHOLDER each: `Constants.Visits`, where the tuning lives.
local C = Constants.Visits

-- A spot's name: its piece's decor id and its `Use_<n>`'s number, "decorId:n" (`Visits.spotKey`).
export type SpotKey = string
-- An activity room as the caller sees it now. `spots` lists its usable spots, in a fixed order.
export type RoomInfo = {
	id: string,
	type: string,
	ready: boolean,
	reachable: boolean, -- a route from the guest's room to it (Rooms.route)
	spots: { SpotKey },
}
-- The spots taken in a hotel: room id -> spot key -> guest id.
export type Taken = { [string]: { [SpotKey]: string } }
-- A visit under way: `Going` to the room, `There` doing the action, `Back` to its own room.
export type Phase = "Going" | "There" | "Back"
export type Visitor = { room: string, spot: SpotKey, phase: Phase }
-- A visit chosen: the room, the spot taken there and the preference that drew the guest.
export type Choice = { room: string, spot: SpotKey, pref: string }
export type Decide = {
	now: number,
	dueAt: number, -- when this guest's next visit is due (`Visits.nextAt`)
	lastDecision: number?, -- when it last decided, nil if never
	prefs: { string },
	met: { [string]: boolean }?, -- its preferences met already this stay
	rooms: { RoomInfo },
	taken: Taken,
	visitors: { [string]: Visitor }, -- the hotel's, for the walking cap
	roll: number, -- 0 <= roll < 1, the server's random draw
}

local function lerp(a: number, b: number, t: number): number
	return a + (b - a) * math.clamp(t, 0, 1)
end

-- ===== Who and where =====

-- Whether a room type is one guests visit (A.13: the amenities and the new types).
function Visits.isActivity(typeId: string): boolean
	local p = Pieces.get(typeId)
	return p ~= nil and p.kind == "Amenity"
end

-- The preferences in `prefs` that a visit to a room of `typeId` meets, in `prefs`' order; none for a bedroom.
function Visits.meets(prefs: { string }, typeId: string): { string }
	local out = {}
	local p = Pieces.get(typeId)
	if not p or p.kind ~= "Amenity" then
		return out
	end
	for _, pref in prefs do
		if table.find(p.tags or {}, pref) then
			table.insert(out, pref)
		end
	end
	return out
end

--[[ The rooms guests can visit now (A.13.1): activity rooms, ready, reachable
	and with at least one usable spot. What the bus counts and offers
	(`HotelService.visitTags`, its amenity bonus); a room with no usable spot
	draws nobody. ]]
function Visits.open(rooms: { RoomInfo }): { RoomInfo }
	local out = {}
	for _, r in rooms do
		if r.ready and r.reachable and #r.spots > 0 and Visits.isActivity(r.type) then
			table.insert(out, r)
		end
	end
	return out
end

-- ===== Spots =====

-- A spot's key: the piece's decor id and its `Use_<n>`'s number.
function Visits.spotKey(decor: string, n: number): SpotKey
	return `{decor}:{n}`
end

-- The decor id of the piece a spot is on, nil for a key that is not a spot's.
function Visits.pieceOf(spot: SpotKey): string?
	return string.match(spot, "^(.+):%d+$")
end

--[[ How many of a room's spots are taken ("2/4 spots in use", A.13.1): of
	`spots` when given (its spots now, so a spot gone never counts), else
	every one held. ]]
function Visits.inUse(taken: Taken, roomId: string, spots: { SpotKey }?): number
	local t = taken[roomId] or {}
	local n = 0
	if spots then
		for _, k in spots do
			if t[k] ~= nil then
				n += 1
			end
		end
		return n
	end
	for _ in t do
		n += 1
	end
	return n
end

-- The first free spot of a room's `spots`, in their order, or nil when every one is taken.
function Visits.freeSpot(taken: Taken, roomId: string, spots: { SpotKey }): SpotKey?
	local t = taken[roomId] or {}
	for _, k in spots do
		if t[k] == nil then
			return k
		end
	end
	return nil
end

-- The spot a guest holds, if any.
function Visits.spotOf(taken: Taken, guest: string): (string?, SpotKey?)
	for roomId, t in taken do
		for k, g in t do
			if g == guest then
				return roomId, k
			end
		end
	end
	return nil, nil
end

--[[ Takes spot `spot` of a room for `guest`: refused when the spot is not
	one of the room's `spots`, is taken, or the guest holds a spot already. ]]
function Visits.take(
	taken: Taken,
	roomId: string,
	spot: SpotKey,
	spots: { SpotKey },
	guest: string
): boolean
	if not table.find(spots, spot) then
		return false
	end
	if Visits.spotOf(taken, guest) ~= nil then
		return false
	end
	local t = taken[roomId]
	if t and t[spot] ~= nil then
		return false
	end
	if not t then
		t = {}
		taken[roomId] = t
	end
	t[spot] = guest
	return true
end

-- Frees the spot a guest holds (it left, was sent home or checked out); whether it held one.
function Visits.free(taken: Taken, guest: string): boolean
	local roomId, k = Visits.spotOf(taken, guest)
	if not roomId or not k then
		return false
	end
	local t = taken[roomId]
	t[k] = nil
	if next(t) == nil then
		taken[roomId] = nil
	end
	return true
end

--[[ A visit begun, in one step (A.13.1): the choice's spot taken for `guest`
	and the guest recorded `Going` there, or neither (refused as `take` is,
	or when the guest is a visitor already), so a spot is never held by
	nobody's visit. ]]
function Visits.begin(
	taken: Taken,
	visitors: { [string]: Visitor },
	guest: string,
	choice: Choice,
	spots: { SpotKey }
): boolean
	if visitors[guest] ~= nil then
		return false
	end
	if not Visits.take(taken, choice.room, choice.spot, spots, guest) then
		return false
	end
	visitors[guest] = { room = choice.room, spot = choice.spot, phase = "Going" }
	return true
end

-- ===== Choosing =====

--[[ The visits a guest may make now, one per room (its first free spot), in
	room-id order: an activity room, ready, reachable, with a free spot, whose
	tags meet one of the guest's preferences. When some room meets a
	preference not yet met this stay (`met`), only those: a guest goes first
	for what it lacks (a choice A.13.1 leaves open). `pref` is the first such
	preference. A guest with no match has none, and never visits. ]]
function Visits.candidates(
	prefs: { string },
	rooms: { RoomInfo },
	taken: Taken,
	met: { [string]: boolean }?
): { Choice }
	local fresh, any = {}, {}
	for _, r in rooms do
		if r.ready and r.reachable and Visits.isActivity(r.type) then
			local spot = Visits.freeSpot(taken, r.id, r.spots)
			local hits = Visits.meets(prefs, r.type)
			if spot and #hits > 0 then
				local unmet: string? = nil
				for _, h in hits do
					if not (met and met[h]) then
						unmet = h
						break
					end
				end
				table.insert(any, { room = r.id, spot = spot, pref = hits[1] })
				if unmet then
					table.insert(fresh, { room = r.id, spot = spot, pref = unmet })
				end
			end
		end
	end
	local list = if #fresh > 0 then fresh else any
	table.sort(list, function(a, b)
		return a.room < b.room
	end)
	return list
end

-- One of `candidates`, drawn by `roll` (0 <= roll < 1), or nil when there is none.
function Visits.choose(
	prefs: { string },
	rooms: { RoomInfo },
	taken: Taken,
	roll: number,
	met: { [string]: boolean }?
): Choice?
	local list = Visits.candidates(prefs, rooms, taken, met)
	if #list == 0 then
		return nil
	end
	return list[math.clamp(math.floor(roll * #list) + 1, 1, #list)]
end

-- ===== When =====

-- When the next visit is due, `from` a check-in or a return: 90–150 s later by `roll`.
function Visits.nextAt(from: number, roll: number): number
	return from + lerp(C.EveryMin, C.EveryMax, roll)
end

-- Whether a guest may decide now: its visit is due and its last decision is at least the gap ago.
function Visits.mayDecide(now: number, dueAt: number, lastDecision: number?): boolean
	return now >= dueAt and (lastDecision == nil or now - lastDecision >= C.DecisionGap)
end

--[[ Whether a visit fits in what is left of the stay (`remaining` seconds,
	nil for no end set): the walk there and back (`walk`, the caller's
	estimate) and the shortest action. A visit that would not is not begun,
	so a check-out never waits long on a guest out at a spot. ]]
function Visits.fits(remaining: number?, walk: number): boolean
	return remaining == nil or remaining >= walk + C.DoMin
end

-- How many visitors are walking (to a room or back), for the cap.
function Visits.walking(visitors: { [string]: Visitor }): number
	local n = 0
	for _, v in visitors do
		if v.phase == "Going" or v.phase == "Back" then
			n += 1
		end
	end
	return n
end

-- Whether one more visitor may set out (the hotel's cap on visitors walking).
function Visits.canSetOut(visitors: { [string]: Visitor }): boolean
	return Visits.walking(visitors) < C.MaxWalking
end

-- How long a visit's action lasts, by `roll`: 20–40 s.
function Visits.duration(roll: number): number
	return lerp(C.DoMin, C.DoMax, roll)
end

--[[ The server's one call per guest in its room: nil and false when it may
	not decide yet; otherwise it decided now (the caller stores `now` as its
	last decision), and the visit chosen, nil when there is none or the
	hotel's walkers are at the cap (it tries again after the gap). The caller
	begins the visit (`Visits.begin`: the spot taken, the guest `Going`). ]]
function Visits.decide(i: Decide): (Choice?, boolean)
	if not Visits.mayDecide(i.now, i.dueAt, i.lastDecision) then
		return nil, false
	end
	if not Visits.canSetOut(i.visitors) then
		return nil, true
	end
	return Visits.choose(i.prefs, i.rooms, i.taken, i.roll, i.met), true
end

-- ===== What it gives =====

--[[ What a visit to a room of `typeId` gives (A.13.1): the preferences it
	meets, counted met for the stay, and the satisfaction it adds: +5 when it
	meets one and the stay has not had the bonus (`rewarded`), else 0. ]]
function Visits.gives(prefs: { string }, typeId: string, rewarded: boolean): ({ string }, number)
	local hits = Visits.meets(prefs, typeId)
	return hits, if #hits > 0 and not rewarded then C.Satisfaction else 0
end

-- ===== Busy and sent home =====

--[[ The activity rooms visitors keep busy (A.13.1 "Rules kept"): a visitor
	on its way or in the room; one walking back no longer. Added to `into`
	when given (the booked rooms' set the server passes `Rooms.keepsBusy`). ]]
function Visits.busyRooms(
	visitors: { [string]: Visitor },
	into: { [string]: boolean }?
): { [string]: boolean }
	local out = into or {}
	for _, v in visitors do
		if v.phase == "Going" or v.phase == "There" then
			out[v.room] = true
		end
	end
	return out
end

--[[ The visitors to send home (A.13.1): on the way to or in a room no
	longer ready (`ready` by room id), or, when `spots` (each room's spots
	now) is given, whose spot is no longer one of its room's (its piece sold,
	or moved where no square reaches it). ]]
function Visits.stranded(
	visitors: { [string]: Visitor },
	ready: { [string]: boolean },
	spots: { [string]: { SpotKey } }?
): { string }
	local out = {}
	for g, v in visitors do
		if v.phase == "Going" or v.phase == "There" then
			local gone = spots ~= nil and not table.find(spots[v.room] or {}, v.spot)
			if not ready[v.room] or gone then
				table.insert(out, g)
			end
		end
	end
	table.sort(out)
	return out
end

-- The visitors on the way to or at a spot on piece `decor` (sold or moved: each is sent back), sorted.
function Visits.onPiece(visitors: { [string]: Visitor }, decor: string): { string }
	local out = {}
	for g, v in visitors do
		if (v.phase == "Going" or v.phase == "There") and Visits.pieceOf(v.spot) == decor then
			table.insert(out, g)
		end
	end
	table.sort(out)
	return out
end

return Visits
