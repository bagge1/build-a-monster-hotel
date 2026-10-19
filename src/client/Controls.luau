--!strict
--[[
	The game's own controls (GDD §11: "Gamepad navigation for everything.
	Input Action System for all inputs."; UI.md, "Gamepad").

	KEYS AND BUTTONS ARE INPUT ACTIONS. Every key the game reads and every
	gamepad button it binds is an `InputAction` in an `InputContext`, made here
	at runtime in a folder under PlayerScripts (Roblox's own avatar controls
	are its `CharacterContext`, DEVNOTES). A context that sinks takes its keys
	from every context of lower priority: build mode (2000) takes B and R from
	the HUD's keys (1000) and the left stick and A from the avatar. Pointer
	input (a click or a tap on the plot, a drag, a pinch, a twist) stays on
	UserInputService: it carries a position.

	PANELS. A window registered by `Controls.panel` (every `Ui.window` is)
	gets the gamepad's selection on its first button when it opens while the
	gamepad is the input, keeps it while it redraws, and lets it go when it
	closes. ButtonB closes the panel on top; with none open it steps back once
	in what is open (`Controls.onBack`: build mode's chain). ButtonY is the
	menu: the selection goes onto the HUD's buttons (or build mode's cards)
	and off them again, so the left stick walks again.

	Nothing here requires another client module, so anything may require it.
]]

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TextChatService = game:GetService("TextChatService")
local UserInputService = game:GetService("UserInputService")

local Controls = {}

local me = Players.LocalPlayer

-- A press that lands this soon after a context turned on or off is the press
-- that turned it (the HUD's B opening build mode, and build mode's B closing
-- it, would otherwise both see one press), seconds.
local SETTLE = 0.25
-- How long a selection just let go of still counts as there: Roblox's own
-- navigation may drop it on the same press that our handler reads, seconds.
local RECENT = 0.15
-- A panel's buttons are drawn by its opener after it is shown, and laid out a
-- frame later: the first selection waits this long, seconds.
local DRAWN = 0.05

local folder: Folder? = nil
local toggledAt = 0
local clearedAt = 0
local releasedAt = 0

local function root(): Folder
	if not folder then
		local f = Instance.new("Folder")
		f.Name = "GameInputContexts"
		f.Parent = me:WaitForChild("PlayerScripts")
		folder = f
	end
	return folder :: Folder
end

-- ===== The device and its words =====

-- Whether the gamepad was the last thing used.
function Controls.gamepad(): boolean
	return string.find(UserInputService:GetLastInputType().Name, "^Gamepad") ~= nil
end

-- A hint's words for the device in use (only where a keyboard hint is shown already, UI.md).
function Controls.hint(keyboard: string, gamepad: string): string
	return if Controls.gamepad() then gamepad else keyboard
end

-- Whether the player is typing (a TextBox, or the chat's bar): no key acts then.
function Controls.typing(): boolean
	if UserInputService:GetFocusedTextBox() then
		return true
	end
	local bar = TextChatService:FindFirstChildOfClass("ChatInputBarConfiguration")
	return bar ~= nil and bar.IsFocused
end

-- ===== Input actions =====

-- A context of actions. `sink`: its keys reach no context of lower priority.
function Controls.context(
	name: string,
	priority: number,
	sink: boolean,
	enabled: boolean?
): InputContext
	local c = Instance.new("InputContext")
	c.Name = name
	c.Priority = priority
	c.Sink = sink
	c.Enabled = enabled ~= false
	c:GetPropertyChangedSignal("Enabled"):Connect(function()
		toggledAt = os.clock()
	end)
	c.Parent = root()
	return c
end

local function bind(action: InputAction, name: string, props: { [string]: any })
	local b = Instance.new("InputBinding")
	b.Name = name
	for k, v in props do
		(b :: any)[k] = v
	end
	b.Parent = action
end

-- A button: `keys` are its keyboard keys and gamepad buttons, `fn` runs on a
-- press, never while typing nor in the moment a context turned on or off.
function Controls.press(
	context: InputContext,
	name: string,
	keys: { Enum.KeyCode },
	fn: () -> ()
): InputAction
	local a = Instance.new("InputAction")
	a.Name = name
	a.Type = Enum.InputActionType.Bool
	for _, key in keys do
		bind(a, key.Name, { KeyCode = key })
	end
	a.Pressed:Connect(function()
		if Controls.typing() or os.clock() - toggledAt < SETTLE then
			return
		end
		fn()
	end)
	a.Parent = context
	return a
end

-- A direction (a Vector2, read with `Controls.read`): a thumbstick, and keys
-- as its composite directions.
function Controls.direction(
	context: InputContext,
	name: string,
	stick: Enum.KeyCode?,
	keys: {
		Left: Enum.KeyCode?,
		Right: Enum.KeyCode?,
		Up: Enum.KeyCode?,
		Down: Enum.KeyCode?,
	}?
): InputAction
	local a = Instance.new("InputAction")
	a.Name = name
	a.Type = Enum.InputActionType.Direction2D
	if stick then
		bind(a, stick.Name, { KeyCode = stick })
	end
	if keys then
		bind(a, "Keys", keys :: any)
	end
	a.Parent = context
	return a
end

-- A direction's state, zero inside `deadzone` (a resting stick drifts) and while typing.
function Controls.read(action: InputAction, deadzone: number?): Vector2
	local v = action:GetState()
	if typeof(v) ~= "Vector2" or Controls.typing() then
		return Vector2.zero
	end
	return if v.Magnitude < (deadzone or 0.2) then Vector2.zero else v
end

-- ===== Selection =====

-- Whether a GUI object, every ancestor and its ScreenGui are shown.
local function shown(g: GuiObject): boolean
	local node: Instance? = g
	while node do
		if node:IsA("GuiObject") and not node.Visible then
			return false
		elseif node:IsA("LayerCollector") then
			return node.Enabled
		end
		node = node.Parent
	end
	return false
end
Controls.shown = shown

-- Selects `g` when the gamepad is the input; nil lets the selection go.
function Controls.select(g: GuiObject?)
	if g == nil then
		releasedAt = os.clock()
		GuiService.SelectedObject = nil
	elseif Controls.gamepad() then
		GuiService.SelectedObject = g
	end
end

-- Whether something is selected, or was a moment ago (`RECENT`).
function Controls.selectedRecently(): boolean
	return GuiService.SelectedObject ~= nil or os.clock() - clearedAt < RECENT
end

-- The first button to select inside `within`: the top-left one shown, `skip` (the cross) never.
function Controls.first(within: Instance, skip: Instance?): GuiObject?
	local best: GuiObject? = nil
	for _, d in within:GetDescendants() do
		if d:IsA("GuiButton") and d ~= skip and d.Selectable and shown(d) then
			local p = d.AbsolutePosition
			local b = best and best.AbsolutePosition
			if not b or p.Y < b.Y - 2 or (math.abs(p.Y - b.Y) <= 2 and p.X < b.X) then
				best = d
			end
		end
	end
	return best
end

-- ===== Panels =====

type Panel = { window: GuiObject, close: () -> (), cross: GuiObject? }
local open: { Panel } = {} -- the open panels, the last opened on top

local function selectIn(p: Panel)
	Controls.select(Controls.first(p.window, p.cross) or p.cross)
end

-- A panel: `close` is what its cross does (ButtonB does the same).
function Controls.panel(window: GuiObject, close: () -> (), cross: GuiObject?)
	-- The selection stays inside an open window: never onto the HUD behind it.
	window.SelectionGroup = true
	window.SelectionBehaviorUp = Enum.SelectionBehavior.Stop
	window.SelectionBehaviorDown = Enum.SelectionBehavior.Stop
	window.SelectionBehaviorLeft = Enum.SelectionBehavior.Stop
	window.SelectionBehaviorRight = Enum.SelectionBehavior.Stop
	local p: Panel = { window = window, close = close, cross = cross }
	window:GetPropertyChangedSignal("Visible"):Connect(function()
		local i = table.find(open, p)
		if i then
			table.remove(open, i)
		end
		if window.Visible then
			table.insert(open, p)
			if Controls.gamepad() then
				task.delay(DRAWN, function()
					if window.Visible and open[#open] == p then
						selectIn(p)
					end
				end)
			end
			return
		end
		local sel = GuiService.SelectedObject
		if sel == nil or sel:IsDescendantOf(window) then
			local top = open[#open]
			if top and Controls.gamepad() then
				selectIn(top)
			else
				Controls.select(nil)
			end
		end
	end)
end

-- ===== Back and menu =====

local backHandlers: { () -> boolean } = {}
local menuHandlers: { () -> boolean } = {}

-- A step back for ButtonB when no panel is open: `fn` returns true when it took the press.
-- The last registered is asked first.
function Controls.onBack(fn: () -> boolean)
	table.insert(backHandlers, 1, fn)
end

-- Where ButtonY puts the selection when nothing is selected and no panel is open:
-- `fn` returns true when it did. The last registered is asked first.
function Controls.onMenu(fn: () -> boolean)
	table.insert(menuHandlers, 1, fn)
end

local function back()
	local top = open[#open]
	if top then
		top.close()
		return
	end
	for _, fn in backHandlers do
		if fn() then
			return
		end
	end
	if GuiService.SelectedObject then
		Controls.select(nil)
	end
end

local function menu()
	if GuiService.SelectedObject then
		Controls.select(nil)
		return
	end
	local top = open[#open]
	if top then
		selectIn(top)
		return
	end
	for _, fn in menuHandlers do
		if fn() then
			return
		end
	end
end

-- ===== Keeping the selection through a redraw =====

-- A panel redraws by destroying its buttons and making them again: the
-- selection, lost with its button, goes to the button of the same name in
-- the same place, or to the panel's first.
local last: GuiObject? = nil
local lastPath: { string } = {}
local lastGui: Instance? = nil
local lastPanel: Panel? = nil

local function remember(sel: GuiObject)
	last = sel
	table.clear(lastPath)
	lastGui = nil
	lastPanel = nil
	local node: Instance? = sel
	while node and not node:IsA("LayerCollector") do
		table.insert(lastPath, 1, node.Name)
		node = node.Parent
	end
	lastGui = node
	for _, p in open do
		if sel:IsDescendantOf(p.window) then
			lastPanel = p
		end
	end
end

local function lost()
	local path, gui, panel = table.clone(lastPath), lastGui, lastPanel
	last = nil
	if not Controls.gamepad() or not gui then
		return
	end
	task.delay(DRAWN, function()
		-- Let go of on purpose since (a card chosen), or something else selected.
		if GuiService.SelectedObject ~= nil or os.clock() - releasedAt < DRAWN * 4 then
			return
		end
		local node: Instance? = gui
		for _, name in path do
			node = node and node:FindFirstChild(name)
		end
		if node and node:IsA("GuiObject") and node.Selectable and shown(node) then
			Controls.select(node)
		elseif panel and table.find(open, panel) then
			selectIn(panel)
		end
	end)
end

function Controls.Init()
	local ui = Controls.context("UiKeys", 3000, true)
	Controls.press(ui, "Back", { Enum.KeyCode.ButtonB }, back)
	Controls.press(ui, "Menu", { Enum.KeyCode.ButtonY }, menu)
end

function Controls.Start()
	GuiService:GetPropertyChangedSignal("SelectedObject"):Connect(function()
		local sel = GuiService.SelectedObject
		if sel then
			remember(sel)
			return
		end
		clearedAt = os.clock()
		if last and last.Parent == nil then
			lost()
		end
		last = nil
	end)
	-- A selected button destroyed may stay the SelectedObject: let it go here.
	RunService.Heartbeat:Connect(function()
		local sel = GuiService.SelectedObject
		if sel and sel.Parent == nil then
			GuiService.SelectedObject = nil
		end
	end)
end

return Controls
