--!strict
--[[
	Staff at work (GDD §4.6 "Staff are seen working", §5.4, Appendix A.5):
	where each role's post is, and the arithmetic of an errand. Pure: the
	server times the errand with it, the client draws the walk with the same
	numbers, and the `staff` spec holds it to its rules.

	A POST is found by the hotel's shared points (`HotelPoints`: the facade's
	`Entrance`, the first desk's pivot `FrontDesk` and its `Clerk`, `Till`,
	`Queue_n`), through `point`, which the server answers from
	`PlotService.point` and the client from the plot it sees. `slot` is the
	resident's place among its role's staff (1, 2, ...), which the server
	publishes so every client stands them in the same order.

	AN ERRAND is a walk along a path of world points at a constant speed,
	from a server time `T0`: the same encoding and the same arithmetic as a
	guest's walk (`GuestService`, `GuestRenderer`).
]]

local Constants = require(script.Parent.Constants)
local Grid = require(script.Parent.Grid)
local Pieces = require(script.Parent.Pieces)

local CELL = Constants.Grid.CellSize

local Staff = {}

-- The roles that walk to a room; the rest keep to their posts.
Staff.Errands = { RoomService = true, Housekeeping = true } :: { [string]: boolean }

-- What rises at the door when the job is done (Appendix A.5).
Staff.DoneText = {
	RoomService = "✓ Room Service",
	Housekeeping = "✓ Housekeeping",
} :: { [string]: string }

-- Staff of a role stand this far apart, a row's places and its rows alike.
local STEP = 3
-- A post keeps this far inside its area's edge: about half the 5-stud person's width.
local MARGIN = 1

--[[ Slot `slot`'s place in an area of `frame` (x within ±`halfW`, z within
	`z0..z1`, at y 0 of the frame: its walking surface): the first place at
	`first`'s x and z (pulled inside the area), the next ones STEP along
	`along` (+1 or −1 in x) while they stay inside, then a row `rowStep`
	further in z; past the last row it starts again at the first place. A
	post never leaves its area, whatever the role's count (2026-10-26: Room
	Service's third stood 1.4 past the desk's end, in the next cell's wall or
	room, and its errands started there). ]]
local function placeIn(
	frame: CFrame,
	first: Vector3,
	slot: number,
	along: number,
	rowStep: number,
	halfW: number,
	z0: number,
	z1: number
): Vector3
	local lo, hi = -halfW + MARGIN, halfW - MARGIN
	local zlo, zhi = math.min(z0, z1) + MARGIN, math.max(z0, z1) - MARGIN
	local x = math.clamp(first.X, lo, hi)
	local z = math.clamp(first.Z, zlo, zhi)
	local cols = 1 + math.floor((if along > 0 then hi - x else x - lo) / STEP)
	local rows = 1 + math.floor((if rowStep > 0 then zhi - z else z - zlo) / math.abs(rowStep))
	local i = (slot - 1) % (cols * rows)
	return frame:PointToWorldSpace(
		Vector3.new(x + along * (i % cols) * STEP, 0, z + (i // cols) * rowStep)
	)
end

--[[ Where a resident in `role` stands, or nil (the Wing, or a hotel without
	the point). Every post is on a walking surface, inside an area nothing is
	built on: the first desk's footprint (`FrontDesk`, the desk's pivot: its
	footprint's centre on the floor, MODELS.md "Hotel kit"), the desk's two
	front cells where the queue stands, or the entrance's mouth
	(`Grid.entrance`: the cells inside the arch, +Z of `Entrance`, which
	looks to the street). ]]
function Staff.post(role: string, slot: number, point: (name: string) -> CFrame?): Vector3?
	if role == "Bellhop" or role == "Security" or role == "Entertainment" then
		local entrance = point("Entrance")
		if not entrance then
			return nil
		end
		local half = #Grid.entrance() * CELL / 2
		if role == "Bellhop" then
			-- Just inside the arch, to its side (2026-10-26: it stood 0.9 outside the facade, on the forecourt).
			return placeIn(entrance, Vector3.new(4, 0, 1.5), slot, 1, STEP, half, 0, CELL)
		elseif role == "Security" then
			-- Inside the entrance, across from the Bellhop (the sign left the lobby for the forecourt);
			-- its rows two steps apart, between Entertainment's.
			return placeIn(entrance, Vector3.new(-4, 0, 1.5), slot, -1, 2 * STEP, half, 0, CELL)
		end
		-- Just inside the arch, off to the side of the queue (the lobby's spawn went with the lobby).
		return placeIn(entrance, Vector3.new(-8, 0, 4), slot, -1, 2 * STEP, half, 0, CELL)
	end
	local desk = point("FrontDesk")
	local piece = Pieces.get("FrontDesk")
	if not desk or not piece then
		return nil
	end
	local halfW, halfD = piece.w * CELL / 2, piece.d * CELL / 2
	-- A desk point moved by `offset` in its own frame, in the desk's frame.
	local function near(name: string, offset: Vector3): Vector3?
		local cf = point(name)
		return if cf then desk:PointToObjectSpace((cf * CFrame.new(offset)).Position) else nil
	end
	if role == "FrontDesk" then
		-- Behind the first desk's counter, side by side along it (MODELS.md, "Front desk": `Clerk`).
		local at = near("Clerk", Vector3.zero)
		return if at then placeIn(desk, at, slot, 1, STEP, halfW, -halfD, halfD) else nil
	elseif role == "RoomService" then
		--[[ Beside the till, on the desk's floor: the desk's pivot is on the
			walking surface (2026-10-26: the post took the counter's height,
			3.8, off the till's, a blockout's measurement in gameplay code). ]]
		local at = near("Till", Vector3.new(4, 0, 2))
		return if at then placeIn(desk, at, slot, 1, STEP, halfW, -halfD, halfD) else nil
	elseif role == "Housekeeping" then
		-- Beside the queue, in the desk's two front cells (`Grid` keeps them walkable).
		local at = near("Queue_4", Vector3.new(-4, 0, 0))
		return if at then placeIn(desk, at, slot, -1, STEP, halfW, -halfD - CELL, -halfD) else nil
	end
	return nil
end

function Staff.encode(path: { Vector3 }): string
	local parts = table.create(#path)
	for i, p in path do
		parts[i] = string.format("%.1f,%.1f,%.1f", p.X, p.Y, p.Z)
	end
	return table.concat(parts, ";")
end

function Staff.decode(s: string?): { Vector3 }
	local out = {}
	if not s or s == "" then
		return out
	end
	for _, chunk in string.split(s, ";") do
		local xyz = string.split(chunk, ",")
		table.insert(
			out,
			Vector3.new(tonumber(xyz[1]) or 0, tonumber(xyz[2]) or 0, tonumber(xyz[3]) or 0)
		)
	end
	return out
end

function Staff.length(path: { Vector3 }): number
	local total = 0
	for i = 2, #path do
		total += (path[i] - path[i - 1]).Magnitude
	end
	return total
end

--[[ Where a walker is `travelled` studs along `path`: its position, the way
	it faces, and the index of the point it walks toward (#path + 1 once it
	has arrived). ]]
function Staff.along(path: { Vector3 }, travelled: number): (Vector3, Vector3, number)
	local forward = Vector3.new(0, 0, -1)
	if #path == 0 then
		return Vector3.zero, forward, 1
	end
	local left = math.max(0, travelled)
	for i = 2, #path do
		local seg = path[i] - path[i - 1]
		local l = seg.Magnitude
		if left < l then
			return path[i - 1]:Lerp(path[i], left / l), seg.Unit, i
		end
		left -= l
	end
	local last = path[#path]
	local prev = if #path > 1 then path[#path - 1] else last
	local dir = last - prev
	return last, if dir.Magnitude > 0.01 then dir.Unit else forward, #path + 1
end

-- The way back to the start from `travelled` studs along `path`: from where it stands, the points it passed.
function Staff.backFrom(path: { Vector3 }, travelled: number): { Vector3 }
	local here, _, nextIndex = Staff.along(path, travelled)
	local out = { here }
	for i = nextIndex - 1, 1, -1 do
		if (path[i] - out[#out]).Magnitude > 0.05 then
			table.insert(out, path[i])
		end
	end
	return out
end

--[[ When an errand's job is done (Appendix A.5): the role's delay after the
	job opened, divided by the resident's efficiency, but never sooner than
	`atDoor` seconds after it reaches the door. ]]
function Staff.due(
	openedAt: number,
	delay: number,
	efficiency: number,
	arriveAt: number,
	atDoor: number
): number
	return math.max(openedAt + delay / math.max(efficiency, 0.01), arriveAt + atDoor)
end

--[[ How long Front Desk takes to check the first waiting guest in (§4.6,
	Appendix A.5): the role's delay divided by the desk's summed efficiency,
	and shortened by the best Bellhop on staff ("check-in time"). ]]
function Staff.deskDelay(delay: number, desk: number, bellhop: number, bonus: number): number
	return delay / math.max(desk, 0.01) / (1 + math.max(bellhop, 0) * math.max(bonus, 0))
end

--[[ Which guest Front Desk serves next (§4.6, Appendix A.5): the first in
	`queue` that is waiting at the desk (`isQueued`), as `GuestService.checkIn`
	picks, or nil. A guest at the head of the queue still walking in
	(assigned, `ToHotel`) does not hold up the ones behind it at the desk. ]]
function Staff.nextAtDesk<T>(queue: { T }, isQueued: (T) -> boolean): T?
	for _, id in queue do
		if isQueued(id) then
			return id
		end
	end
	return nil
end

--[[ Whether a resident came home from the Hunter Camp by itself (§8.1, A.8: its
	`campUntil` passed) after `since` and by `now` (server seconds): the
	server's staff and their bonuses are worked out again then, as when it is
	rescued. A resident rescued (`campUntil` 0) or never taken did not. ]]
function Staff.backFromCamp(
	residents: { [string]: { campUntil: number } },
	since: number,
	now: number
): boolean
	for _, r in residents do
		if r.campUntil > since and r.campUntil <= now then
			return true
		end
	end
	return false
end

--[[ Whether a resident may be moved now (to another role or hotel, or
	released to the Wing or on holiday), with `location` the hotel played:
	not while it is on staff at another hotel of the chain (WAITING §2.48,
	his yes 2026-10-26). That hotel earns in the background at the rate it
	earned while played (`Chain.background`, frozen as it was left, its
	staff in it), so a resident taken from it would be counted twice: at
	the hotel it left and where it went. At that hotel it moves freely. ]]
function Staff.movable(rec: { role: string, hotel: number? }, location: number): boolean
	return rec.role == "" or (rec.hotel or location) == location
end

return Staff
