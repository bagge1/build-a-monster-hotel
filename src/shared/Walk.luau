--!strict
--[[
	A walk: a path of points walked at one speed, with a wait at any point
	(GDD §4.3: a browsing guest pauses a couple of seconds at each entrance).
	Shared, because the server and every client must put a walker in the same
	place from the same published path (§13.2): the server to know where a
	guest is when it is pitched or decides, the client to draw it.

	Published as one string, "x,y,z;x,y,z,w;...": a fourth number is the
	seconds spent standing at that point once it is reached.
]]

local Walk = {}

export type Path = { Vector3 }
export type Waits = { [number]: number } -- point index -> seconds standing there

function Walk.encode(path: Path, waits: Waits?): string
	local parts = table.create(#path)
	for i, p in path do
		local w = waits and waits[i]
		parts[i] = if w and w > 0
			then string.format("%.1f,%.1f,%.1f,%.2f", p.X, p.Y, p.Z, w)
			else string.format("%.1f,%.1f,%.1f", p.X, p.Y, p.Z)
	end
	return table.concat(parts, ";")
end

function Walk.decode(s: string?): (Path, Waits)
	local path, waits = {}, {}
	if not s or s == "" then
		return path, waits
	end
	for i, chunk in string.split(s, ";") do
		local n = string.split(chunk, ",")
		path[i] = Vector3.new(tonumber(n[1]) or 0, tonumber(n[2]) or 0, tonumber(n[3]) or 0)
		local w = tonumber(n[4])
		if w and w > 0 then
			waits[i] = w
		end
	end
	return path, waits
end

-- Seconds from the first point to standing at the last, waits included.
function Walk.duration(path: Path, waits: Waits?, speed: number): number
	local t = if waits and waits[1] then waits[1] else 0
	for i = 2, #path do
		t += (path[i] - path[i - 1]).Magnitude / speed
		if waits and waits[i] then
			t += waits[i]
		end
	end
	return t
end

--[[ Where a walker is `elapsed` seconds into its walk, which way it faces
	(the way it last walked) and whether it is walking. Past the end it stands
	at the last point. ]]
function Walk.sample(
	path: Path,
	waits: Waits?,
	speed: number,
	elapsed: number
): (Vector3, Vector3, boolean)
	local forward = Vector3.new(0, 0, -1)
	if #path == 0 then
		return Vector3.zero, forward, false
	end
	local t = math.max(0, elapsed)
	local w1 = if waits and waits[1] then waits[1] else 0
	if t < w1 then
		return path[1], forward, false
	end
	t -= w1
	for i = 2, #path do
		local a, b = path[i - 1], path[i]
		local d = b - a
		local seg = d.Magnitude / speed
		if d.Magnitude > 0.01 then
			forward = d.Unit
		end
		if t < seg then
			return a:Lerp(b, t / seg), forward, true
		end
		t -= seg
		local w = if waits and waits[i] then waits[i] else 0
		if t < w then
			return b, forward, false
		end
		t -= w
	end
	return path[#path], forward, false
end

return Walk
