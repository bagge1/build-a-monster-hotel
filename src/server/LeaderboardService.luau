--!strict
--[[
	The global leaderboards (GDD §7 "Global: Book completion, lifetime guests,
	weekly event score"), on a board at the lane's west end.

	Each is an OrderedDataStore keyed by user id. A player's own score is
	written when they leave and every few minutes while they play (never more
	often: a key takes one write per 6 s, DEVNOTES.md "Data"), and the top ten
	are read for the board every two minutes. The weekly board's store is named
	by the UTC week, so it starts empty every Monday.

	NEEDS DATASTORE ACCESS (WAITING.md §3.1): without it every call fails, and
	the board says so instead of showing a stale or empty list as if it were real.
]]

local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Format = require(ReplicatedStorage.Shared.Format)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)
local PlayerData = require(ServerScriptService.Server.PlayerData)

local LeaderboardService = {}

local WRITE_EVERY = 300
local READ_EVERY = 120

type Board = {
	key: string,
	title: string,
	store: () -> OrderedDataStore,
	score: (PlayerData.Data) -> number,
}

local function week(): number
	-- Weeks counted from a Monday (1970-01-05).
	return (os.time() - 4 * 86400) // (7 * 86400)
end

local BOARDS: { Board } = {
	{
		key = "Book",
		title = "Monster Book",
		store = function()
			return DataStoreService:GetOrderedDataStore("MonsterHotel_Book_v1")
		end,
		score = function(d)
			local n = 0
			for _ in d.book do
				n += 1
			end
			return n
		end,
	},
	{
		key = "Guests",
		title = "Lifetime guests",
		store = function()
			return DataStoreService:GetOrderedDataStore("MonsterHotel_Guests_v1")
		end,
		score = function(d)
			return d.stats.stays or 0
		end,
	},
	{
		key = "Week",
		title = "Happy stays this week",
		store = function()
			return DataStoreService:GetOrderedDataStore(`MonsterHotel_Week_{week()}`)
		end,
		score = function(d)
			if (d.stats.weekId or -1) ~= week() then
				d.stats.weekId = week()
				d.stats.weekHappy = 0
			end
			return d.stats.weekHappy or 0
		end,
	},
}

local labels: { [string]: TextLabel } = {}
local lastWrite: { [Player]: number } = {}

local function write(player: Player, data: PlayerData.Data)
	for _, b in BOARDS do
		local score = math.floor(b.score(data))
		if score > 0 then
			pcall(function()
				b.store():SetAsync(tostring(player.UserId), score)
			end)
		end
	end
end

local function nameOf(userId: number): string
	local ok, name = pcall(Players.GetNameFromUserIdAsync, Players, userId)
	return if ok then name else `#{userId}`
end

local function refresh()
	local access = workspace:GetAttribute("DataStoreState") == "Access"
	for _, b in BOARDS do
		local label = labels[b.key]
		if label then
			if not access then
				label.Text = `{b.title}\n\n(needs DataStore access)`
			else
				local ok, page = pcall(function()
					return b.store():GetSortedAsync(false, 10):GetCurrentPage()
				end)
				if ok and page then
					local lines = { b.title, "" }
					for i, entry in page do
						table.insert(
							lines,
							`{i}. {nameOf(tonumber(entry.key) or 0)}  {Format.number(entry.value)}`
						)
					end
					label.Text = table.concat(lines, "\n")
				else
					label.Text = `{b.title}\n\n(could not load)`
				end
			end
		end
	end
end

local function buildBoard()
	local board = Instance.new("Part")
	board.Name = "Leaderboards"
	board.Anchored = true
	board.Size = Vector3.new(30, 12, 1)
	board.Color = Color3.fromRGB(46, 32, 70)
	board.Material = Enum.Material.SmoothPlastic
	-- At the lane's west end on its south half, clear of the bus (which drives the north half), its front toward the lane.
	board.CFrame = CFrame.lookAt(
		StreetLayout.WestEnd + Vector3.new(-14, 8, -14),
		StreetLayout.WestEnd + Vector3.new(-14, 8, 0)
	)
	local gui = Instance.new("SurfaceGui")
	gui.Face = Enum.NormalId.Front
	gui.CanvasSize = Vector2.new(900, 360)
	gui.LightInfluence = 0
	local holder = Instance.new("Frame")
	holder.Size = UDim2.fromScale(1, 1)
	holder.BackgroundTransparency = 1
	holder.Parent = gui
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.Parent = holder
	for _, b in BOARDS do
		local l = Instance.new("TextLabel")
		l.Name = b.key
		l.Size = UDim2.fromScale(1 / #BOARDS, 1)
		l.BackgroundTransparency = 1
		l.Font = Enum.Font.FredokaOne
		l.TextColor3 = Color3.fromRGB(255, 230, 180)
		l.TextSize = 22
		l.TextYAlignment = Enum.TextYAlignment.Top
		l.Text = b.title
		l.Parent = holder
		labels[b.key] = l
	end
	gui.Parent = board
	board.Parent = workspace
end

function LeaderboardService.Init() end

function LeaderboardService.Start()
	buildBoard()
	PlayerData.onRelease(function(player, data)
		write(player, data)
		lastWrite[player] = nil
	end)
	-- The week's happy stays, counted from check-outs (GuestService stats "happyStays").
	local GuestService = require(ServerScriptService.Server.GuestService) :: any
	local Stay = require(ReplicatedStorage.Shared.Stay)
	GuestService.onCheckout(function(player, _, satisfaction)
		local data = PlayerData.get(player)
		if data and Stay.isHappy(satisfaction) then
			BOARDS[3].score(data) -- rolls the week over if it changed
			data.stats.weekHappy = (data.stats.weekHappy or 0) + 1
		end
	end)
	task.spawn(function()
		while true do
			for player, data in PlayerData.loaded() do
				if os.clock() - (lastWrite[player] or 0) >= WRITE_EVERY then
					lastWrite[player] = os.clock()
					task.spawn(write, player, data)
				end
			end
			refresh()
			task.wait(READ_EVERY)
		end
	end)
end

return LeaderboardService
