--!strict
--[[
	A hotel's prompts (the desk, the till, a room's door) are its owner's: the
	server ignores anyone else who triggers one (`PlotService`), and this hides
	them from everyone else, so a visitor's screen is not full of buttons that
	do nothing. Prompts carry their owner as an `OwnerId` attribute.

	The server turns prompts on and off as rooms change state; a hidden one is
	hidden again whenever it does.
]]

local Players = game:GetService("Players")

local PromptFilter = {}

local me = Players.LocalPlayer

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
end

return PromptFilter
