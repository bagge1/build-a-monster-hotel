--!strict
--[[
	A hotel's prompts (the desk, the till, a room's door) are its owner's: the
	server ignores anyone else who triggers one (`PlotService`), and this hides
	them from everyone else, so a visitor's screen is not full of buttons that
	do nothing. Prompts carry their owner as an `OwnerId` attribute.

	The server turns prompts on and off as rooms change state; a hidden one is
	hidden again whenever it does.

	A DOOR'S PROMPTS (`Doorway`: Clean, Help) show only to a player who sees
	the doorway: from the room or from the hallway it opens onto, never through
	a wall (2026-10-26: they showed and fired from the next room and through the
	facade from the forecourt, so E in one room cleaned another). A ray from the
	player to a point just inside and one just outside the threshold, against
	what collides on the plot (the walls, the facade); hidden by a range of 0 on
	this client, so the server's `Enabled` is never overwritten here.
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local PromptFilter = {}

local me = Players.LocalPlayer

-- How often a door prompt's sight is checked, in seconds; a walk covers about 3 studs in it.
local CHECK = 0.2
-- Checked this far past its range, so one walked into is decided before it can show.
local AHEAD = 4
-- The points looked at: a person's chest height over the threshold (an opening is
-- at least 7 tall, MODELS.md "Walls"), the middle of the squares either side of it.
local CHEST = 2.5
local SIDE = 1.5

-- A door prompt -> its range as the server made it.
local doors: { [ProximityPrompt]: number } = {}

local function watch(prompt: ProximityPrompt)
	local function apply()
		local owner = prompt:GetAttribute("OwnerId")
		if owner ~= nil and owner ~= me.UserId and prompt.Enabled then
			prompt.Enabled = false
		end
		-- A visitor's prompt (a hotel's Like) is hidden from the hotel's own owner.
		if prompt:GetAttribute("VisitorOnly") == me.UserId and prompt.Enabled then
			prompt.Enabled = false
		end
	end
	apply()
	prompt:GetPropertyChangedSignal("Enabled"):Connect(apply)
	prompt:GetAttributeChangedSignal("OwnerId"):Connect(apply)
	local function doorway()
		if prompt:GetAttribute("Doorway") and not doors[prompt] then
			doors[prompt] = prompt.MaxActivationDistance
			prompt.MaxActivationDistance = 0
		end
	end
	doorway()
	prompt:GetAttributeChangedSignal("Doorway"):Connect(doorway)
	prompt.Destroying:Connect(function()
		doors[prompt] = nil
	end)
end

-- The plot model a prompt is on (`Plots.Plot_<i>`), or nil.
local function plotOf(prompt: Instance): Instance?
	local plots = workspace:FindFirstChild("Plots")
	local at: Instance? = prompt
	while at and at.Parent ~= plots do
		at = at.Parent
	end
	return at
end

-- Whether the doorway is in sight from `from`: either side of its threshold.
local function seesDoorway(door: Attachment, from: Vector3, params: RaycastParams): boolean
	local cf = door.WorldCFrame
	for _, side in { SIDE, -SIDE } do
		local target = cf.Position + Vector3.new(0, CHEST, 0) + cf.LookVector * side
		if not workspace:Raycast(from, target - from, params) then
			return true
		end
	end
	return false
end

local function checkDoors()
	local character = me.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	local from = if root and root:IsA("BasePart") then root.Position else nil
	for prompt, range in doors do
		local door = prompt.Parent
		if not door or not prompt:IsDescendantOf(workspace) then
			if not prompt.Parent then
				doors[prompt] = nil
			end
			continue
		end
		local show = false
		if from and prompt.Enabled and door:IsA("Attachment") then
			local plot = plotOf(prompt)
			if plot and (door.WorldPosition - from).Magnitude <= range + AHEAD then
				local params = RaycastParams.new()
				params.FilterType = Enum.RaycastFilterType.Include
				params.FilterDescendantsInstances = { plot }
				params.RespectCanCollide = true
				show = seesDoorway(door, from, params)
			end
		end
		local want = if show then range else 0
		if prompt.MaxActivationDistance ~= want then
			prompt.MaxActivationDistance = want
		end
	end
end

function PromptFilter.Init() end

function PromptFilter.Start()
	for _, d in workspace:GetDescendants() do
		if d:IsA("ProximityPrompt") then
			watch(d)
		end
	end
	workspace.DescendantAdded:Connect(function(d)
		if d:IsA("ProximityPrompt") then
			watch(d)
		end
	end)
	local since = 0
	RunService.Heartbeat:Connect(function(dt)
		since += dt
		if since >= CHECK then
			since = 0
			checkDoors()
		end
	end)
end

return PromptFilter
