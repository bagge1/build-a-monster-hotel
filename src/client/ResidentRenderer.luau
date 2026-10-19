--!strict
--[[
	Every hotel's residents, as every client sees them (GDD §4.6, §7 "Visit
	and like: see its residents"): the Wing's residents wander its garden;
	staff stand at their posts, found by the lobby's attachments (MODELS.md,
	"Lobby"). The server publishes them in `ReplicatedStorage.Residents`;
	this draws and moves them locally. Read by nothing.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local MonsterKit = require(script.Parent.MonsterKit)

local ResidentRenderer = {}

local G = Constants.Grid
local P = G.Cells * G.CellSize

type Drawn = {
	config: Configuration,
	plot: number,
	model: Model?,
	pos: Vector3,
	target: Vector3,
	waitUntil: number,
	key: string,
}

local drawn: { [Configuration]: Drawn } = {}
local rng = Random.new()

local function plotModel(index: number): Model?
	local plots = workspace:FindFirstChild("Plots")
	local m = plots and plots:FindFirstChild(`Plot_{index}`)
	return if m and m:IsA("Model") then m else nil
end

local function lobbyPoint(plot: Model, name: string): CFrame?
	local lobby = plot:FindFirstChild("Lobby")
	local root = lobby and lobby:FindFirstChild("Root")
	local a = root and root:FindFirstChild(name)
	return if a and a:IsA("Attachment") then a.WorldCFrame else nil
end

-- Where a resident in `role` belongs, or nil for the Wing (it wanders).
local function post(plot: Model, role: string, n: number): Vector3?
	local function near(name: string, offset: Vector3): Vector3?
		local cf = lobbyPoint(plot, name)
		return if cf then (cf * CFrame.new(offset)).Position else nil
	end
	local spread = (n - 1) * 3
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

local function add(c: Instance, plotIndex: number)
	if not c:IsA("Configuration") or drawn[c] then
		return
	end
	drawn[c] = {
		config = c,
		plot = plotIndex,
		model = nil,
		pos = Vector3.zero,
		target = Vector3.zero,
		waitUntil = 0,
		key = "",
	}
end

local function remove(c: Instance)
	local d = drawn[c :: Configuration]
	if d then
		if d.model then
			d.model:Destroy()
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

local function frame(dt: number)
	local now = os.clock()
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
			local goal = if role ~= "" then post(plot, role, counts[ck]) else nil
			if goal then
				d.target = goal
			elseif (d.pos - d.target).Magnitude < 0.5 and now >= d.waitUntil then
				d.target = wingPoint(plot) or d.pos
				d.waitUntil = now + rng:NextNumber(2, 6)
			end
			local delta = d.target - d.pos
			local step = math.min(delta.Magnitude, (if role ~= "" then 12 else 3) * dt)
			local dir = if delta.Magnitude > 0.01 then delta.Unit else Vector3.new(0, 0, -1)
			if delta.Magnitude > 20 then
				d.pos = d.target -- a new post far away: appear there
			else
				d.pos += dir * step
			end
			if d.model then
				local flat = Vector3.new(dir.X, 0, dir.Z)
				local look = if flat.Magnitude > 0.01 then flat.Unit else Vector3.new(0, 0, -1)
				local bob = if role == "Entertainment" then math.abs(math.sin(now * 6)) * 0.6 else 0
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
