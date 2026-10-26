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
	- spots: a room's capacity is its spots (`Use_<n>` on its activity
	  furniture, MODELS.md, counted by the caller); one guest a spot, one spot
	  a guest; a spot is taken when the guest sets out, so two never walk to
	  the same one, and freed when it leaves;
	- when: every 90–150 s of a stay, at most one decision a guest per 10 s,
	  and at most 12 visitors walking at once per hotel, so a full hotel does
	  not route every frame;
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

-- An activity room as the caller sees it now. `spots` counts the `Use_<n>` of its furniture.
export type RoomInfo = {
	id: string,
	type: string,
	ready: boolean,
	reachable: boolean, -- a route from the guest's room to it (Rooms.route)
	spots: number,
}
-- The spots taken in a hotel: room id -> spot index (1..spots) -> guest id.
export type Taken = { [string]: { [number]: string } }
-- A visit under way: `Going` to the room, `There` doing the action, `Back` to its own room.
export type Phase = "Going" | "There" | "Back"
export type Visitor = { room: string, spot: number, phase: Phase }
-- A visit chosen: the room, the spot taken there and the preference that drew the guest.
export type Choice = { room: string, spot: number, pref: string }
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

-- ===== Spots =====

-- How many of a room's spots are taken ("2/4 spots in use", A.13.1).
function Visits.inUse(taken: Taken, roomId: string): number
	local n = 0
	for _ in taken[roomId] or {} do
		n += 1
	end
	return n
end

-- The lowest free spot of a room with `spots` spots, or nil when every one is taken.
function Visits.freeSpot(taken: Taken, roomId: string, spots: number): number?
	local t = taken[roomId] or {}
	for i = 1, spots do
		if t[i] == nil then
			return i
		end
	end
	return nil
end

-- The spot a guest holds, if any.
function Visits.spotOf(taken: Taken, guest: string): (string?, number?)
	for roomId, t in taken do
		for i, g in t do
			if g == guest then
				return roomId, i
			end
		end
	end
	return nil, nil
end

--[[ Takes spot `spot` of a room for `guest`: refused when the spot is not
	one of the room's, is taken, or the guest holds a spot already. ]]
function Visits.take(
	taken: Taken,
	roomId: string,
	spot: number,
	spots: number,
	guest: string
): boolean
	if spot < 1 or spot > spots or spot % 1 ~= 0 then
		return false
	end
	if Visits.spotOf(taken, guest) ~= nil then
		return false
	end
	local t = taken[roomId]
	if not t then
		t = {}
		taken[roomId] = t
	end
	if t[spot] ~= nil then
		return false
	end
	t[spot] = guest
	return true
end

-- Frees the spot a guest holds (it left, was sent home or checked out); whether it held one.
function Visits.free(taken: Taken, guest: string): boolean
	local roomId, i = Visits.spotOf(taken, guest)
	if not roomId or not i then
		return false
	end
	local t = taken[roomId]
	t[i] = nil
	if next(t) == nil then
		taken[roomId] = nil
	end
	return true
end

-- ===== Choosing =====

--[[ The visits a guest may make now, one per room (its lowest free spot), in
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
	takes the choice's spot (`Visits.take`) and sets the guest `Going`. ]]
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

-- The visitors to send home (A.13.1): on the way to or in a room no longer ready (`ready` by room id).
function Visits.stranded(visitors: { [string]: Visitor }, ready: { [string]: boolean }): { string }
	local out = {}
	for g, v in visitors do
		if (v.phase == "Going" or v.phase == "There") and not ready[v.room] then
			table.insert(out, g)
		end
	end
	table.sort(out)
	return out
end

return Visits
