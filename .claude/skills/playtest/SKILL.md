---
name: playtest
description: How Claude plays the game in Studio itself through the Studio MCP - starting and stopping a playtest, keys, clicks, walking, screenshots, server and client state, two players, phones and tablets - and runs TESTRUN.md item by item. Use it whenever August says "testkör", "provkör", "kör testkörningen", "spela igenom", "testa i Studio", "kolla i spelet", "playtest", "test run", or asks whether something works in the game; whenever a change has to be seen working in a Studio playtest; and whenever the Studio MCP (execute_luau, user_keyboard_input, user_mouse_input, character_navigation, screen_capture, start_stop_play) is used to find out what is actually happening.
---

# Playtesting through the Studio MCP

**Claude runs the playtests** (August, 2026-10-09: "is there nothing you could
do so I don't have as much to do?"). Claude plays every item it can, fixes
what is broken, and hands August only what a person must judge: how it feels,
how it looks. Start from the first phase: a phase that closes on "verified by
script" leaves faults that only playing finds for the end.

`TESTRUN.md` is the list: start at its first unmarked item. The platform
underneath (the MCP's module copies, stale caches) is `DEVNOTES.md`, "The
Studio MCP".

## Before a run

- **The published place**, never a local file, or every persistence test
  runs against a mock (`DEVNOTES.md`, "Data").
- **The sync landed**: dump every script's name and `#Source` length under the
  synced folders and compare with `git show HEAD:<file>` sizes, all of them,
  not only the ones you touched. Stale copies are a **Connect** for August
  (Studio, **Plugins** tab). Until then, a fix of your own can be applied to
  the Edit copy by plain `string.find(s, old, 1, true)` replacement, checked
  by byte count; never other sessions' files.
- **Never while August is importing.**
- **A `Test_` profile, set before Play**: the attribute
  `ServerStorage:SetAttribute("StudioProfile", "Test_...")` in Edit (an
  attribute, not a child). Without it the playtest loads his own Studio
  save (2026-10-24 evening: one did). Read `[playerdata] STUDIO TEST
  PROFILE` in the console before anything else.
- **T0, proof first:** a synthetic key, a click and a walk are seen to act in
  the game before anything else counts.

## How each item is run

- **Per item:** the console read before and after (a script error or a warn of
  the game's own is a failure of its own), a screen capture where the item is
  visual, server state read with `execute_luau` where it is a number.
- **A failure** is fixed in the code, the sync checked, and the item run again.
  A fix is never "verified" from the call that made it.
- **Mark** each item `[x]` pass, `[!]` failed and fixed (commit), `[?]` cannot
  be run this way (why), `[A]` handed to August (why). One log line per item
  at the bottom of `TESTRUN.md`.
- **Commit and update `TESTRUN.md` after every section**, so a new session
  picks it up at the first unmarked item.
- **Money and items come from Studio-only grants** (workspace attributes the
  server reads only in Studio), never by playing around a missing one.

## The MCP in general

- `execute_luau` runs against the **Edit**, **Server** or **Client**
  datamodel; `get_console_output`, `screen_capture`, `start_stop_play`.
  `user_keyboard_input`, `user_mouse_input` and `character_navigation` act on
  the Client.
- **MCP calls run one at a time**: two sent together queue and the second
  times out.
- **A `require` from the MCP is its own copy of a module**: read what the game
  publishes (attributes, instances), or parent a `Script` in the running
  server (it shares the game's modules) that writes its answer to a
  `workspace` attribute, read in a second call. `_G` survives between calls in
  one datamodel, not across a restart, and is not shared with a Script in the
  game.
- **A server-side change needs a new playtest**: a running one keeps the
  scripts it started with. The MCP cannot start one straight after stopping
  one; if it refuses, ask August to press **Play**.
- **A helper Script in the game is destroyed only after what it started is
  done**: destroying it kills every thread it spawned.

## Input

- **Never take the focus from August** (his ask, 2026-10-20: "can you stop
  forcing me to alt-tab"). He works on the same computer while sessions run,
  and bringing Studio forward pulls him out of what he is doing. So while he
  is at the computer: **no `SetForegroundWindow`, no simulated keys or mouse,
  no `character_navigation`**. Test through `execute_luau` instead: the
  game's remotes from a Client, the function a key or button calls, the
  `Controls` action's handler, `prompt:InputHoldBegin()`, a camera set from
  the Client, `screen_capture` for pictures. Only an item that is *about* the
  input itself (does a right-drag turn the camera?) needs real input: put it
  in `WAITING.md` for a night run, or ask him in chat first ("Studio comes to
  the front for about 30 s, ok?") and do every such item in one batch on his
  yes. In a night sprint he is away, and the rules below apply as they are.
- **Look before taking the focus, even on a night his brief allows it**: list
  the windows (`Get-Process | ? MainWindowTitle`). A game running (2026-10-24
  night: Europa Universalis V, the focus taken back 36 times in 30 s) means
  he is at the computer: no focus, no keys, no clicks, and no frame timing
  (Studio renders in the background at 15 fps).
- **Studio must have the focus**, or every key returns *Success* and nothing
  reaches the game. Bring it forward from PowerShell with
  `SetForegroundWindow` on `RobloxStudioBeta`'s `MainWindowHandle` (a tap of
  Alt first lets it through). **Every shell call takes the focus back**: focus
  again before the next key. Keep Studio maximized (`ShowWindow(h, 3)`;
  `ShowWindow(h, 9)` un-maximizes and shrinks every coordinate).
- **Keys are US KeyCodes** (August's keyboard is Nordic, user-level
  `CLAUDE.md`). **Number keys and Escape cannot be sent** (bound to CoreGui):
  design a test path that does not need them, or fire the remote the key
  would.
- **Prefer the game's own remotes** from a Client `execute_luau` where an item
  allows: they need no focus and no aim.
- **Coordinates**: `user_mouse_input` x/y are viewport pixels. A ScreenGui's
  origin sits below Roblox's top bar (`ScreenGui.AbsolutePosition`, 58 px on
  his screen), and a capture is the viewport scaled to 1920 wide *with* the
  bar. Click by `instance_path` wherever there is one; scroll a row into its
  list first. Nothing in Roblox's own top bar can be clicked.
- **Text boxes**: click, then `textInput`.
- **A held key is released early** (2026-10-24: `keyDown` E, wait 3 s,
  `keyUp`, and `InputEnded` came after 0.72 s): a prompt with a
  `HoldDuration` over ~0.5 s is held by `InputHoldBegin`/`InputHoldEnd`.
- **A click on a GUI button can arrive and not press it** (2026-10-24 night,
  on foot: `InputBegan` MouseButton1 with `gameProcessed` true over the
  button, no `Activated`, HUD and windows alike; the build cards clicked
  fine minutes before). Check `Activated` with a connection, and fall back
  to the remote the button sends.
- **A ProximityPrompt only shows on screen**: turn the camera to it before E,
  hold for its `HoldDuration` (`keyDown`, wait, `keyUp`), or trigger it without
  the focus by `prompt:InputHoldBegin()`, wait, `InputHoldEnd()` from a Client
  `execute_luau`.
- **A click while the mouse is locked lands mid-screen**: free the cursor (a
  panel open, on foot) before clicking a UI element.
- **Roblox's purchase prompt is CoreGui**: not in a capture, not clickable. A
  real purchase is August's click.

## Walking

- **`character_navigation` plans for a 5-stud agent.** For anything smaller,
  walk with `Humanoid:MoveTo` waypoints from a Client `execute_luau`: a real
  physical walk, so it tests clearance. A call that walks over ~30 s times
  out: `task.spawn` the walk, keep its log in `_G`, poll in ~28 s calls, and
  give it a stop flag (a loose walker fights every later `MoveTo`).
- **`PathfindingService` with the game's agent size** plans a small person's
  walk. Where the client's `ComputeAsync` hangs, plan on the Server and hand
  the waypoints over as a JSON `workspace` attribute.
- **A walker that will not move** with `MoveDirection` set is held by a
  collider: test each collidable part's box against the point on the Server.
  Parts with `CanQuery` off are invisible to rays and overlap queries.
- **Conveyors and moving walkways** carry a walker off a waypoint (and drift it
  in X, `DEVNOTES.md`): keep waypoints off belts, cross a lane square.
- **A railing is tested by pressing into it** at many bearings and watching
  `Humanoid.StateChanged` for Climbing and Freefall.

## Pictures and time

- **Pictures of new models or a changed assembly go to a blind review**
  (skill `blind-review`) before August sees them: rays and walkers prove a
  path is open, not that a sign belongs in front of an entrance.

- **On foot the camera is Roblox's**: set `workspace.CurrentCamera.CFrame` and
  it stays. A game camera that writes every frame needs a Studio-only override
  (an attribute on the local player the camera honours, as Sector Omega's
  `StudioCamera` / `StudioHud`).
- **A capture leaves every BillboardGui out**: check those by their
  properties.
- **A background Studio window renders at ~15 fps and stops `RenderStepped`**:
  timings and frame rates need Studio in front (ask him to leave it 40 s).
- **Time by the server clock** (`workspace:GetServerTimeNow()`), speeds by
  velocities, and know `GetRealPhysicsFPS()`: physics runs slower than wall time
  at low frame rates.
- After a restart, wait for `ContentProvider.RequestQueueSize` to reach 0
  before a picture, or meshes are not drawn.
- **A target far from the player is not on the client** (streaming): read its
  position on the Server and hand it over by attribute.

## Two players

- **He starts it**: `start_stop_play` cannot. **Test → Start Test Session →
  Server and Clients**, then **Test → Add Clients** in the window titled
  *Server* (greyed out in the main window). Add Clients is also how a player
  rejoins.
- **Each window is its own Studio** in `list_roblox_studios`: tell them apart by
  `Players.LocalPlayer` in each `Client` datamodel (UserId −1, −2, changing
  every session).
- **Their profiles are new** (keyed −1, −2) on the real DataStores; grant on
  those players. **`DevCommand` acts on the first player only**: grant the
  second by a Script parented in the running server that calls the services
  on that player.
- **Nothing may end the session by accident**: while it runs, never
  `start_stop_play`, and never load a playing player's profile from another
  datamodel (ProfileStore's session lock kicks that player). The unattended
  order is `TESTRUN.md`, "Launch run".
- **Keys go to the focused window**; remotes from each client's `execute_luau`
  need no focus. A logger on each client recording every `OnClientEvent` in `_G`
  with the server time, and a server Script hooked to the game's damage or
  economy events, tell who did what to whom.
- **Leaving is `Player:Kick` from the server**, a real disconnect, and only
  August brings that player back: do every leave half last.
- **Closing**: stopping play leaves the windows open. Close the `Server` and
  client windows by their processes' titles, keeping the edit window, or he
  presses **Test → Cleanup**.

## Phones and tablets

`StudioDeviceSimulatorService` from an Edit `execute_luau`
(`SetDeviceAsync("iphone_14")` or `"ipad_10th_generation"`, then
`SetOrientationAsync` landscape) before Play, `StopSimulationAsync()` after.
A click then arrives as a `Touch`. On a notched phone an `instance_path` click
misses by the safe inset (47 px on the iPhone 14): click at the element's
`AbsolutePosition` centre plus the inset in x. Pinch cannot be sent. A real
device's memory and frame rate are only known on the real device: that run is
August's, early.

**Pressing a button in the simulator**: a click arrives as two touches, one
of them shifted (2026-10-24: a click on Rating pressed Store). Select the
button instead (`GuiService.SelectedObject` from a Client `execute_luau`)
and press Return with Studio in front: that is the button's own
`Activated`. Measure each panel open with AbsolutePosition (off the
screen, `TextFits`, under 44 px, buttons over each other in one ScreenGui,
over `TouchGui`'s `JumpButton` and `ThumbstickStart`).

## Data in a playtest

- `DataStoreService` works from a playtest's Server and from Edit on the
  published place, and **what it touches is the live store**.
- Persistence is proven by **rejoining**, never by reloading.
- Stopping the playtest is a logout: anything that settles at logout runs, and
  what it prints is lost (`DEVNOTES.md`). Grant again after a restart.
- A DataStore entry is deleted with `RemoveAsync`; an `UpdateAsync` returning
  nil leaves it.
