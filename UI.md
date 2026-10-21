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
thumbstick and jump button, the room view on the right clear of both.

| Name | What | The code |
|---|---|---|
| `Strip` | The bottom strip: `Info` (what to do, a run's price, or why the ghost is red) over `Cards` (a horizontal list of cards) | Fills the cards for the open tab |
| `Tools` | Top-left, in rows: the tabs `Walls`, `Rooms`, `Furniture`, `Decor`; `Stairs` (shows "n free" when a new floor's stair is owed), `Floor`, `Window`; `Down`, `FloorLabel`, `Up`, `BuyFloor`; `Rotate`, `Turn`, `TopView`, `Place`; `Traps`, `Style`, `Done` | Each button's action |
| `PieceMenu` | A window: a stair's or a desk's Move and Sell; a piece of decor's or furniture's Move and Sell (and whether it counts toward a room's Furniture or Decor bar); a window's Move, Sell and swap | Opened by a tap on what it is for |
| `RoomTypes` | A window, its `Body` a scrolling list: one row per room type and amenity of the location, named by its id, each with `Name`, `Tooltip` (who stays in it or what it gives; its key furniture; its minimum and full size) and `Choose` (or 🔒 and its unlock; "too small" when the space is under its minimum). Its `Title` says the space's size | Opened by a tap on a walled space with a door, or the room view's Change type; `Choose` sends `MakeRoom` |
| `RoomView` | A panel on the right: `Top` (`Title`, the type's name; `Close`), `Tooltip`, `Status` (ready, its size and its guest, or what it lacks), three bars `SizeBar`, `FurnitureBar`, `DecorBar` (each `Name`, `Value` in %, `Track` with `Fill` sized by the bar, `Bonus`: what the bar gives now), `Actions` (`Retype`, `Furnish`, `Hallway`) | Opened by a tap on a room or its card; the camera flies to the room and the walls toward it fade; Close flies back |

Cards per tab:

- **Walls**: `Tool_Wall` (a tap puts up the cell edge under the pointer, a
  drag a straight run along the grid; a ghost shows each half edge green or
  red and the strip its price), `Tool_Door` (a tap puts a door in the half
  edge under it or takes one out), `Tool_Remove` (as Walls, taking them
  down), `HalfCells` (the toggle: half edges of 6 studs instead of cell
  edges).
- **Rooms**: `Room_<id>`, one per room built on the floor in view: its type
  and "ready" or what it lacks; a tap opens its room view.
- **Furniture** and **Decor**: one card per piece (`<DecorId>`): name, size
  in squares, price ("free" while a tutorial voucher pays for it).
- **Stairs, desks**: a piece's name, size and price ("free" for an owed stair).
- **Floors**: a finish's name and "Its own floor"; tap a room or a hallway.
- **Windows**: one per window type; tap an outer wall.
