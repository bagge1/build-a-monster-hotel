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

Built in code; free building (GDD §5.4, 2026-10-19). A designed one carries
these names.

| Name | What | The code |
|---|---|---|
| `Strip` | The bottom strip: `Info` (what to do, or why the ghost is red) over `Cards` (a horizontal list of cards) | Fills the cards for the open tab |
| `Tools` | Top-left, in rows: the tabs `Rooms`, `Amenity`, `Stairs` (shows "n free" when a new floor's stair is owed), `Decor`, `Floor`; `Down`, `FloorLabel`, `Up`, `BuyFloor`; `Rotate`, `Turn`, `Place`; `Traps`, `Style`, `Done` | Each button's action |
| `PieceMenu` | A window: a room's tier, its decor points and what the next tier needs, Move, Sell, and its floor finish; a stair's or the desk's Move (the desk is never sold); a piece of decor's Move and Sell; a closed area's Buy | Opened by a tap on what it is for |
| `AreaLabel` | A billboard over each closed area of the floor in view: its price, or "buy one next to it" | Drawn on the plot's `Areas` plates |

Cards per tab: a piece's name, size and price ("free" for an owed stair);
decor's name, size in squares and price; a floor finish's name and "Its own
floor". With the Floors tab a chosen finish is laid by tapping a room, the
lobby or a hallway.
