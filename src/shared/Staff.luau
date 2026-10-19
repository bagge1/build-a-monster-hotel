--!strict
--[[
	Staff at work (GDD §4.6 "Staff are seen working", §5.4, Appendix A.5):
	where each role's post is, and the arithmetic of an errand. Pure: the
	server times the errand with it, the client draws the walk with the same
	numbers, and the `staff` spec holds it to its rules.

	A POST is found by the lobby's attachments (MODELS.md, "Lobby"), through
	`point`, which the server answers from `PlotService.lobbyPoint` and the
	client from the lobby model it sees. `slot` is the resident's place among
	its role's staff (1, 2, ...), which the server publishes so every client
	stands them in the same order.

	AN ERRAND is a walk along a path of world points at a constant speed,
	from a server time `T0`: the same encoding and the same arithmetic as a
	guest's walk (`GuestService`, `GuestRenderer`).
]]

local Staff = {}

-- The roles that walk to a room; the rest keep to their posts.
Staff.Errands = { RoomService = true, Housekeeping = true } :: { [string]: boolean }

-- What rises at the door when the job is done (Appendix A.5).
Staff.DoneText = {
	RoomService = "✓ Room Service",
	Housekeeping = "✓ Housekeeping",
} :: { [string]: string }

-- Where a resident in `role` stands, or nil (the Wing, or a lobby without the attachment).
function Staff.post(role: string, slot: number, point: (name: string) -> CFrame?): Vector3?
	local function near(name: string, offset: Vector3): Vector3?
		local cf = point(name)
		return if cf then (cf * CFrame.new(offset)).Position else nil
	end
	local spread = (slot - 1) * 3
	if role == "FrontDesk" then
		-- Behind the counter, side by side along it (MODELS.md, "Lobby": `Clerk`).
		return near("Clerk", Vector3.new(spread, 0, 0))
	elseif role == "Bellhop" then
		return near("Entrance", Vector3.new(4 + spread, 0, -1.5))
	elseif role == "Security" then
		return near("SignBoard", Vector3.new(6 + spread, 0, -2))
	elseif role == "Entertainment" then
		return near("Spawn", Vector3.new(-4 - spread, 0, -1))
	elseif role == "RoomService" then
		return near("Till", Vector3.new(4 + spread, -3.8, 2))
	elseif role == "Housekeeping" then
		return near("Queue_4", Vector3.new(-4 - spread, 0, 0))
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

return Staff
