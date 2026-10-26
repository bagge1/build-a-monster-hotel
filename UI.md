# What the code needs from a UI

`UI.md` is to the interface what `MODELS.md` is to the models: **the names a
designed panel must carry so the code can drive it**. Claude designs and
builds the interface; August decides what it is and approves the look.

## How a panel is found

- A panel is a **ScreenGui named for the panel**. Its controller asks for it by
  name; a designed one (if any) is cloned, otherwise a builder makes it in code,
  carrying exactly the names below, so every panel works before it is designed.
- **The controller touches only the named elements**, found by name anywhere in
  the panel, so a design can nest them as it likes. A name it cannot find is
  warned about once and that part of the panel does nothing.
- Everything else in a designed panel is the design's, and the code never
  looks at it.
- A ScreenGui built in code that clips with a `CanvasGroup` needs
  `ZIndexBehavior = Sibling` (`DEVNOTES.md`).

The pattern, ready to lift: `D:\Roblox\sector-omega\src\client\UiView.luau`
(`D:\Roblox\playbook\PATTERNS.md`).

### Lists

A list is any container holding **one hidden child named `Row`**, the template
for one item: the controller clones it per item, names the clone after the
item, shows it, sets its `LayoutOrder` and fills its named children. A
choosable row may carry a hidden `Selected`.

### Pop-ups close with a cross

Every menu or dialog over a window carries a cross in its top-right corner as
well as closing on a click beside it (his ruling in Sector Omega,
2026-10-04; confirm it carries over).

### One panel at a time

A HUD window is named `<X>Panel` (`ResidentsPanel`, `StorePanel`, ...) and
stands at the screen's centre; opening one closes any other `<X>Panel`
(`Ui.window`; found 2026-10-26 night, eight open one on another). Pop-ups
(`FoundPopup`, `VipDone`, `ShowcaseMilestone`) and build mode's windows are
named otherwise and may stand over a panel. Entering build mode closes every
panel (`Ui.closePanels`): one left open lay over the hotel and took its taps.

### Gamepad

GDD §11: gamepad navigation for everything, the Input Action System for all
inputs. The code is `src/client/Controls.luau`.

- **Every button is `Selectable`** (`Ui.button`), and a designed panel's
  buttons must be too.
- **Every window is a panel** (`Ui.window` calls `Controls.panel`; a menu
  built otherwise, like `PingMenu`, calls it itself). Opened while the
  gamepad is the input, its top-left button is selected (the cross last);
  the selection stays inside it (`SelectionGroup`, `Stop` on every side);
  a redraw keeps the selection on the button of the same name; closed, the
  selection goes, so the left stick walks again.
- **ButtonB** closes the panel on top, with no panel open it steps back
  (build mode: stop placing, leave the cards, leave build mode).
  **ButtonY** puts the selection on the HUD's menu buttons (in build mode
  the cards) and takes it off again.
- **`NextSelection*` only where the automatic order is wrong**: build mode's
  cards go up to their tab, the tools' last row down to the cards.
- **Keys and gamepad buttons are input actions** (`InputContext`,
  `InputAction`, `InputBinding`, made in code under PlayerScripts): the
  HUD's B and R at priority 1000, build mode's at 2000 (sinking, so it takes
  B, R, the left stick and A while building), back and menu at 3000.
  Pointer input (clicks and taps on the plot, drags, pinches, twists) stays
  on UserInputService, since it carries a position.
- **Build mode with a gamepad**: a cursor on the plot (the door marker's
  gold square) stands in for the pointer. Left stick moves it, A places or
  taps, RB rotates (beside R), D-pad up/down changes floor and left/right
  turns the view a quarter, the right stick turns and zooms.
- **A hint names the gamepad's button only where it names a key already**
  (`Controls.hint`): the build strip's lines.

### Every window and menu, on a phone

- A window (`Ui.window`), the room view and the Ping menu are `Active`: a tap
  on their empty space never reaches a HUD button or the plot behind them.
- A scrolling list keeps its bar in its own room (`ScrollBarInset`), never
  over a row's right-hand button.
- On a computer (a tall screen, no touch) the HUD's right column keeps its
  buttons at its foot, and the Ping menu opens beside them: Roblox's player
  list, the street's leaderboard (§7), stands open at the top right there and
  grows a row per player (2026-10-26: it lay over Moon and Travel and took
  their clicks). A phone or tablet keeps the list shut and has its jump button
  under the column's foot, so there the column starts at the top.
- On a short screen (under 500 px high) the HUD's two menu columns are each
  two buttons wide, the toasts, the banner and the Hunter Night timer keep to
  the lane between them and grow downward rather than clip, and the Ping menu
  opens left of the right column, so the Ping button that shuts it stays
  free (2026-10-24, measured on an iPhone 14 and an iPad 10 in Studio's
  simulator).
- **Gloom on a short screen** sits along the bottom edge, from 120 px in
  (past the thumbstick's resting place) to the HUD's right column, so it
  covers no menu button (2026-10-25: at the top it covered five on an
  iPhone 7); on a tall screen it stays top centre. The bus countdown keeps
  to the lane between the columns too (at most 260 px).
- **Landscape only** (2026-10-25): the client sets
  `PlayerGui.ScreenOrientation = LandscapeSensor` and sets it again when
  Roblox puts StarterGui's `Sensor` back; upright, the top row ran off both
  edges. A window refits when the screen's size changes.

## Images

Every image is drawn by a script in `tools/` (Python, PIL) into `ui/`,
versioned; nothing is downloaded. **Claude uploads** them through the Studio
MCP's `upload_image` (URLs, not paths: serve `ui/` on 127.0.0.1; five per
call). Ids live in one file (`src/client/UiImages.luau`) and nowhere else; an
empty id means not uploaded yet, and whatever reads it must still work.

Drawn **white on transparent, glow baked into alpha**, wherever the code tints
it: colour is then `ImageColor3` or a `UIGradient`, free to change without an
upload. Roblox UI has no bloom. 1024 × 1024 is the largest Roblox keeps.
Developer product and pass icons are the exception: shown as they are, so
drawn in colour, with what matters inside the circle a pass icon is cropped to.

## The panels' look

<!-- His ruling, once he has picked from style rounds: Sector Omega showed four
directions on one panel as an HTML mock-up, and he picked one with another's
type. -->

## Panels

<!-- One section per panel: what it does, the names it carries, in a table
of Name | What | The code. -->

### Build mode (`Build`, `src/client/BuildController.luau`)

Built in code; free building (GDD §5.4, 2026-10-19) and built rooms (A.12,
his rulings 2026-10-21). A designed one carries these names. Mobile first:
every button at least 44 × 44 (`Ui.MinTap`), the strip between a phone's
thumbstick and jump button, the room view on the right clear of both. On a
short screen (under 500 px high) `Tools` shows the whole rows that fit
above the strip (8 px clear) and scrolls, and the HUD's right column is hidden while building, as its left
one always is (2026-10-24: both covered the strip on a phone). On any screen the right column steps aside
while the room view is open. The room view is never scaled: on a short screen it is as tall as the screen
allows and its middle (`Details`: tooltip, status, bars) scrolls between `Top` and `Actions`.

| Name | What | The code |
|---|---|---|
| `Strip` | The bottom strip: `Info` (what to do, a run's price, or why the ghost is red) over `Cards` (a horizontal list of cards) | Fills the cards for the open tab |
| `Tools` | Top-left, in rows: the tabs `Walls`, `Rooms`, `Furniture`, `Decor`; `Stairs` (shows "n free" when a new floor's stair is owed), `Floor`, `Window`; `Down`, `FloorLabel`, `Up`, `BuyFloor`; `Rotate`, `Turn`, `TopView`, `Place`; `Traps`, `Style`, `Done` | Each button's action |
| `PieceMenu` | A window: a stair's or a desk's Move and Sell; a piece of decor's or furniture's Move and Sell (and whether it counts toward a room's Furniture or Decor bar); a window's Move, Sell and swap | Opened by a tap on what it is for |
| `RoomTypes` | A window, its `Body` a scrolling list: one row per room type and amenity of the location, named by its id, each with `Name`, `Tooltip` (who stays in it or what it gives; its key furniture; its minimum and full size) and `Choose` (or 🔒 and its unlock; "too small" when the space is under its minimum). Its `Title` says the space's size | Opened by a tap on a walled space with a door, or the room view's Change type; `Choose` sends `MakeRoom` |
| `RoomView` | A panel on the right: `Top` (`Title`, the type's name; `Close`), `Tooltip`, `Status` (ready, its size and its guest, or what it lacks; for an activity room its visitors' spots, "2/4 spots in use", GDD A.13.1), three bars `SizeBar`, `FurnitureBar`, `DecorBar` (each `Name`, `Value` in %, `Track` with `Fill` sized by the bar, `Bonus`: what the bar gives now), `Actions` (`Retype`, `Furnish`, `Hallway`) | Opened by a tap on a room or its card; the camera flies to the room and the walls toward it fade; Close flies back |

Cards per tab:

- **Walls**: `Tool_Wall` (a tap puts up the cell edge under the pointer, a
  drag a straight run along the grid; a ghost shows each half edge green or
  red and the strip its price), `Tool_Door` (pointing at a standing wall
  outlines its doorway on the half edge the camera's ray meets first, green
  or red; a tap puts a door in it or takes one out; a door never goes where
  no wall stands, GDD A.12), `Tool_Remove` (as Walls, taking them
  down), `HalfCells` (the toggle: half edges of 6 studs instead of cell
  edges).
- **Rooms**: `Room_<id>`, one per room built on the floor in view: its type
  and "ready" or what it lacks; a tap opens its room view.
- **Furniture** and **Decor**: one card per piece (`<DecorId>`): name, size
  in squares, price ("free" while a tutorial voucher pays for it).
  **Decor** starts with what is **Found** (GDD A.11.3): each rare set piece
  and souvenir found, `<DecorId>` "★ name", gold, its copy's price; then
  this location's set pieces and its species' souvenirs not found yet,
  `Unfound_<DecorId>`, dark, "? name" and where it comes from (a tap says
  more in `Info`, with the pity's count); then the shop.
- The room view's `DecorBar` `Bonus` adds a rare set's line: "★ <set> +25%"
  in the room that has the set's bonus, "<set>: bonus in another room", or
  "<set> n/5".
- **Stairs, desks**: a piece's name, size and price ("free" for an owed stair).
- **Floors**: a finish's name and "Its own floor"; tap a room or a hallway.
- **Windows**: one per window type; tap an outer wall.

### Found (`Finds`, `src/client/FindsPanel.luau`)

GDD A.11.3. The `Moment` "Found" (`FindService`: a set piece, a souvenir or
a duplicate) opens one pop-up; mobile first, buttons 48 tall.

| Name | What | The code |
|---|---|---|
| `FoundPopup` | A window: `Title` ("★ Found!", "A souvenir!", "Found again"), `Text` (the piece, its set's count, where it came from; a duplicate's cash), `Where` (size, layer, "Build → Decor, under Found", a copy's price), `Buttons` with `Place` ("Place it") and `Ok` ("Later"; "Lovely" for a duplicate) | `Place` opens build mode on the Decor tab with the piece chosen (`BuildController.placeDecor`) |

The Book page's `Seasons` line ends with "souvenir ★" once the species'
souvenir is found, else "souvenir n/3" (its move-ins toward it).

### Showcase (`Showcase`, `src/client/ShowcasePanel.luau`)

Built in code; GDD A.11.4, street only (his call, WAITING §2.38). Opened by
the HUD's `ShowcaseButton` (left column). The list is the server's
`showcase` state section; nothing the client sends but `Visit` (a plot
index) and `Equip`.

| Name | What | The code |
|---|---|---|
| `ShowcasePanel` | A window, its `Body` a scrolling list: `Head` (your lifetime and weekly likes, the next milestone), `Hint` (how long until you may like today, or how liking works), one row `Hotel_<plot index>` per hotel played on the server, most liked this week first | Redrawn on every state send while open |
| `Hotel_<i>` | `Name` (rank, the owner's hotel, "★ Street Favourite" for its street's weekly favourite), `Likes` (its street, likes this week, in all, "you liked it today"), `Visit` ("Yours" on your own) | `Visit` sends `Visit`; the server stands you at that hotel's forecourt and the window closes |
| `ShowcaseMilestone` | A pop-up: `Text` (the likes reached and the sign cosmetic earned), `Wear` | Opened by the `Moment` "LikeMilestone"; `Wear` sends `Equip` "Sign" |

### Residents: levels (`Panels`, `ResidentsPanel`, `src/client/CollectionPanels.luau`)

GDD A.11.6. Each resident's row `R_<id>` carries, under its `Name` and over
its `Roles`, a `Level` row; the resident's model carries a `LevelBadge`.

| Name | What | The code |
|---|---|---|
| `Level` | `Value` ("Lv n", "(top)" at the cap), `Track` with `Fill` (the XP bar, gold when full), `Xp` ("x/y XP"), `LevelUp` ("Level up $price" when the bar is full, else "Working…" or "Top level") | `LevelUp` sends `LevelUp` with the resident's id; the server checks the bar, the cap and the cash |
| `LevelBadge` | A BillboardGui over each resident in the Wing and at work: "Lv n", gold at the cap | `ResidentRenderer`, from the Configuration's `Level` |

### Monster Book: stacks and Seasons (`Panels`, `BookPanel`, `src/client/CollectionPanels.luau`)

GDD A.11.5. Each species page carries, under its `Mutations` line (the
sizes and looks of the set, found or "·"), a `Seasons` line: the season's
and the month's looks found (`Mutations.Seasonal`) and "stack ✓" once a
stacked one (a size and a look) has been found. The Events panel names the
month's mutation in a line of its own.

### VIP ledger (`Vip`, `src/client/VipPanel.luau`)

Built in code; GDD A.11.1 (the scrutinized recommendations, his calls in
WAITING §2.38). Opened by the HUD's `VipButton` (left column) and the front
desk's **VIP ledger** prompt (F, LB on a gamepad; the server answers with the
`Moment` "VipLedger"). Everything drawn is the server's `vip` state section;
the client sends only `Vip` with an action and an id (or a species).

| Name | What | The code |
|---|---|---|
| `VipPanel` | A window, its `Body` a scrolling list: `Head` (VIPs hosted today of the cap, swaps left, how many at a time; below the unlock, the stars it opens at), `Note` (why none can be accepted now, "new contracts tomorrow"), the running contracts `Contract_<id>`, `OffersHead` and the offers `Offer_<id>`, `Hint` | Redrawn on every state send while open; the `Status` lines each second |
| `Contract_<id>` | `Name` (👑, the VIP's look and species, its rarity), `Spec` (room type and bars asked), `Likes` (its preferences: a happy stay needs them), `Reward`, `Status` (play time left and the best room of the type now, or what Ready lacks; "Room held" and the next bus; on its way; staying), `Ready` (green when a ready, free room meets it) or `Cancel` ("Let the room go", while held) | `Ready` sends `Vip` "Ready"; the server holds the room and the clock stops |
| `Offer_<id>` | `Name`, `Spec`, `Likes`, `Reward` (and the deadline), `Accept`, `Swap` | `Vip` "Accept" / "Swap" |
| `VipDone` | A pop-up: `Text` (the VIP hosted, the cash, today's count), `Ok` | Opened by the `Moment` "VipDone" |

Elsewhere: a Book page of a species the ledger can draw carries `RequestVip`
(👑, top right; `Vip` "Request" with its id, one of the day's swaps). The room
view's `Status` adds "👑 held for your VIP" or "👑 meets your VIP's ask". A
VIP guest's label reads "👑 VIP for <owner>" in gold, with a gold glow.

### Expedition board (`Expedition`, `ExpeditionPanel`, `src/client/ExpeditionPanel.luau`)

Built in code; GDD A.11.2 (its scrutinized recommendations; the pay his
ruling, §18 2026-10-26). Opened by the `ExpeditionBoard`'s **Expeditions**
prompt in the Resident Wing (E; the server answers with the `Moment`
"ExpeditionBoard"). Everything drawn is the server's `expedition` state
section and, for the residents, `collection`; the client sends only
`ExpeditionSend` (a destination, a length, the party's ids) and
`ExpeditionCollect`. Mobile first: every button at least 44 tall, the party
filled by one tap on **Best for this trip**.

| Name | What | The code |
|---|---|---|
| `ExpeditionPanel` | A window, its `Body` a scrolling list: `Head` (how a trip pays: three quarters of what the party would earn in the Wing meanwhile, the offline cap included, and a free roll for a find), then either the planner below or `Trip` | Redrawn on every state send while open; `Left` each second |
| `Destinations` | A row of picture cards `Dest_<id>`, one per destination: `Name`, `Likes` (the tags a resident matches by), its picture `Image` (`UiImages` `Expedition_<id>`; the location's facade colour while that is empty); a closed one is dark with "Open <hotel> first"; the chosen one has a gold outline | A tap chooses it |
| `Lengths` | `Len_<seconds>`: "30 min · 5% find", the chosen one pumpkin | A tap chooses it |
| `Party` | `Slot_1`… (`Constants.Expeditions.Party`): the resident in it or "Empty" | A tap empties the slot |
| `Best` | **Best for this trip** | Fills the slots (`Expeditions.best`: matching the destination first, then level, then rarity); any slot can then be changed |
| `Send` | "Send n" (green when a party is picked) and `Chance` beside it (the find's chance with this party's matches) | Sends `ExpeditionSend`; the server checks everything again |
| `Residents` | A list `Pick_<id>`, one per resident who may go (in the Wing, home): its look and species, "Lv n", its Wing pay, "♥ likes it" when it matches; teal when picked | A tap puts it in the first empty slot or takes it out |
| `Trip` | While a trip is out: `Where` (destination and length), `Who` (the party), `Left` (time left, or "Back!"), `SoFar` (the pay counted so far), `Chance` (the find's chance; "a find is sure" on the guaranteed one), and `Collect` once it is back | `Collect` sends `ExpeditionCollect` |

### Collect pop-up (`Expedition`, `ExpeditionCollect`)

Opened once per trip, the first time the state shows it back (as it comes
home while the player plays, or on joining with one back). Named not
`<X>Panel`, so it stands over a panel.

| Name | What | The code |
|---|---|---|
| `ExpeditionCollect` | A pop-up: `Text` ("Your residents are back from the <destination>!", the pay, the find's chance), `Buttons` with `Collect` and `Later` | `Collect` sends `ExpeditionCollect`; the `Moment` "ExpeditionCollected" closes it (a find opens `FoundPopup` as any find does) |

### Residents button: the trip's timer (`Hud`, `ResidentsButton`)

While a trip is out, the HUD's `ResidentsButton` carries `ExpeditionTimer`, a
small badge on its top-right corner: the time left ("1:23:45"), "Back!" in
gold once the party is home and the trip waits for Collect. Hidden with no
trip. Counted down on the client from the state's `left`. In the Residents
panel a resident on a trip reads "· on an expedition" in its `Name`, and its
buttons are refused by the server until it is home.
