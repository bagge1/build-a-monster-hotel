--!strict
--[[
	Every hotel's residents, as every client sees them (GDD §4.6, §7 "Visit
	and like: see its residents"): the Wing's residents wander its garden;
	staff stand at their posts (`Staff.post`, found by the hotel's shared
	points, `HotelPoints`), in the order the server's `Slot` gives.

	STAFF ARE SEEN WORKING (§4.6, §5.4, Appendix A.5): a resident on an
	errand carries `Path`, `T0` and `Speed`, and this walks it along them by
	the same arithmetic the server times it with; at the door (`Phase`
	"Work") it faces in and knocks, and when the job is done (`Phase` turns
	"Done") a "✓" rises at the `Door`. The server publishes them in
	`ReplicatedStorage.Residents`; this draws and moves them locally. Read by
	nothing.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local HotelPoints = require(ReplicatedStorage.Shared.HotelPoints)
local Staff = require(ReplicatedStorage.Shared.Staff)
local MonsterKit = require(script.Parent.MonsterKit)
local Hud = require(script.Parent.Hud)
local Ui = require(script.Parent.Ui)

local ResidentRenderer = {}

local G = Constants.Grid
local P = G.Cells * G.CellSize
local POP_RADIUS = 150 -- a "✓" further from the camera than this is not drawn

type Drawn = {
	config: Configuration,
	plot: number,
	model: Model?,
	pos: Vector3,
	target: Vector3,
	waitUntil: number,
	key: string,
	errand: { Vector3 }, -- the leg being walked, decoded from `Path`
	errandCode: string?,
	connections: { RBXScriptConnection },
}

local drawn: { [Configuration]: Drawn } = {}
local rng = Random.new()

local function plotModel(index: number): Model?
	local plots = workspace:FindFirstChild("Plots")
	local m = plots and plots:FindFirstChild(`Plot_{index}`)
	return if m and m:IsA("Model") then m else nil
end

local function wingPoint(plot: Model): Vector3?
	local origin = plot:GetAttribute("Origin")
	if typeof(origin) ~= "CFrame" then
		return nil
	end
	local l = Vector3.new(
		rng:NextNumber(6, P - 6),
		G.SlabThickness,
		rng:NextNumber(P + 4, P + G.WingDepth - 4)
	)
	return origin:PointToWorldSpace(l)
end

-- The "✓" at the door when a job is done (Appendix A.5).
local function popDone(c: Configuration)
	local door = c:GetAttribute("Door")
	local text = Staff.DoneText[c:GetAttribute("Role") :: string? or ""]
	local camera = workspace.CurrentCamera
	if typeof(door) ~= "Vector3" or not text then
		return
	end
	if camera and (camera.CFrame.Position - door).Magnitude > POP_RADIUS then
		return
	end
	Hud.float(text, door + Vector3.new(0, 3, 0), Ui.Colour.Good)
end

local function add(c: Instance, plotIndex: number)
	if not c:IsA("Configuration") or drawn[c] then
		return
	end
	local d: Drawn = {
		config = c,
		plot = plotIndex,
		model = nil,
		pos = Vector3.zero,
		target = Vector3.zero,
		waitUntil = 0,
		key = "",
		errand = {},
		errandCode = nil,
		connections = {},
	}
	drawn[c] = d
	table.insert(
		d.connections,
		c:GetAttributeChangedSignal("Phase"):Connect(function()
			if c:GetAttribute("Phase") == "Done" then
				popDone(c)
			end
		end)
	)
end

local function remove(c: Instance)
	local d = drawn[c :: Configuration]
	if d then
		if d.model then
			d.model:Destroy()
		end
		for _, conn in d.connections do
			conn:Disconnect()
		end
		drawn[c :: Configuration] = nil
	end
end

local function watchPlot(f: Instance)
	local index = tonumber(string.match(f.Name, "%d+")) or 0
	for _, c in f:GetChildren() do
		add(c, index)
	end
	f.ChildAdded:Connect(function(c)
		add(c, index)
	end)
	f.ChildRemoved:Connect(remove)
end

-- Where a resident on an errand is now, the way it faces, and whether it is still walking.
local function onErrand(d: Drawn, serverNow: number): (Vector3?, Vector3, boolean)
	local c = d.config
	local code = c:GetAttribute("Path") :: string?
	if code ~= d.errandCode then
		d.errandCode = code
		d.errand = Staff.decode(code)
	end
	if not code or #d.errand == 0 then
		return nil, Vector3.new(0, 0, -1), false
	end
	local speed = c:GetAttribute("Speed") :: number? or Constants.Staff.WalkSpeed
	local travelled = (serverNow - (c:GetAttribute("T0") :: number? or serverNow)) * speed
	local pos, dir = Staff.along(d.errand, travelled)
	local walking = travelled < Staff.length(d.errand)
	if not walking and c:GetAttribute("Phase") == "Work" then
		-- At the door: face it.
		local door = c:GetAttribute("Door")
		if typeof(door) == "Vector3" then
			local toward = Vector3.new(door.X - pos.X, 0, door.Z - pos.Z)
			if toward.Magnitude > 0.1 then
				dir = toward.Unit
			end
		end
	end
	return pos, dir, walking
end

local function frame(dt: number)
	local now = os.clock()
	local serverNow = workspace:GetServerTimeNow()
	local counts: { [string]: number } = {}
	for c, d in drawn do
		-- A republished Wing replaces its folder whole: drop what it took with it.
		if not c:IsDescendantOf(game) then
			remove(c)
			continue
		end
		local plot = plotModel(d.plot)
		local away = c:GetAttribute("Away") == true
		local key = `{c:GetAttribute("Species")}|{c:GetAttribute("Mutation")}`
		if d.model and (d.key ~= key or away or not plot) then
			d.model:Destroy()
			d.model = nil
		end
		if plot and not away then
			if not d.model then
				local m = MonsterKit.build(
					c:GetAttribute("Species") :: string,
					c:GetAttribute("Mutation") :: string?
				)
				if m then
					m.Parent = workspace:FindFirstChild("ClientGuests") or workspace
					d.model = m
					d.key = key
					d.pos = wingPoint(plot) or Vector3.zero
					d.target = d.pos
				end
			end
			local role = c:GetAttribute("Role") :: string? or ""
			local ck = `{d.plot}|{role}`
			counts[ck] = (counts[ck] or 0) + 1
			local slot = c:GetAttribute("Slot") :: number? or counts[ck]
			local errandPos, errandDir, walking = onErrand(d, serverNow)
			local dir: Vector3
			if errandPos then
				d.pos = errandPos
				d.target = errandPos
				dir = errandDir
			else
				local goal = if role ~= ""
					then Staff.post(role, slot, function(name)
						return HotelPoints.find(plot, name)
					end)
					else nil
				if goal then
					d.target = goal
				elseif (d.pos - d.target).Magnitude < 0.5 and now >= d.waitUntil then
					d.target = wingPoint(plot) or d.pos
					d.waitUntil = now + rng:NextNumber(2, 6)
				end
				local delta = d.target - d.pos
				local step = math.min(delta.Magnitude, (if role ~= "" then 12 else 3) * dt)
				dir = if delta.Magnitude > 0.01 then delta.Unit else Vector3.new(0, 0, -1)
				walking = delta.Magnitude > 0.05
				if delta.Magnitude > 20 then
					d.pos = d.target -- a new post far away: appear there
				else
					d.pos += dir * step
				end
			end
			if d.model then
				local flat = Vector3.new(dir.X, 0, dir.Z)
				local look = if flat.Magnitude > 0.01 then flat.Unit else Vector3.new(0, 0, -1)
				local phase = c:GetAttribute("Phase")
				local bob = if walking and errandPos
					then math.abs(math.sin(now * 8)) * 0.25 -- a guest's stride (GuestRenderer)
					elseif phase == "Work" then math.abs(math.sin(now * 5)) * 0.4 -- knocking
					elseif role == "Entertainment" then math.abs(math.sin(now * 6)) * 0.6
					else 0
				d.model:PivotTo(
					CFrame.lookAt(
						d.pos + Vector3.new(0, bob, 0),
						d.pos + Vector3.new(0, bob, 0) + look
					)
				)
			end
		end
	end
end

function ResidentRenderer.Init() end

function ResidentRenderer.Start()
	local folder = ReplicatedStorage:WaitForChild("Residents")
	for _, f in folder:GetChildren() do
		watchPlot(f)
	end
	folder.ChildAdded:Connect(watchPlot)
	folder.ChildRemoved:Connect(function(f)
		for _, c in f:GetChildren() do
			remove(c)
		end
	end)
	RunService.Heartbeat:Connect(frame)
end

return ResidentRenderer
