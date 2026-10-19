--!strict
--[[
	The client's copy of its drawable state (`StateService`): a table of
	sections the server sends whenever one changes. Panels read
	`State.data.<section>` and redraw on `State.changed`.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Net = require(ReplicatedStorage.Shared.Net)

local State = {}

State.data = {} :: { [string]: any }
local changed = Instance.new("BindableEvent")
State.changed = changed.Event

function State.Init()
	Net.listen("State", function(sections: { [string]: any })
		for k, v in sections do
			State.data[k] = v
		end
		changed:Fire()
	end)
end

function State.Start()
	Net.send("Ready")
end

return State
