# Decor and customization ideas (2026-10-20, for August's picks)

His ask, 2026-10-20: "a list of all possible decor items that could add nice
content to the game, maybe how you could customize rooms, wallpaper, carpets,
or other customizations that could fit neatly into the game". **Nothing here
is decided.** What he picks goes into `docs/GDD.md` (§5.4, A.2) before it is
built; names, prices and tags are his.

How it fits the game as built: decor stands on the 3-stud grid in one of three
layers (`Floor`, `Rug`, `Wall`; `MODELS.md`, "Decor"), gives a room its
**preference tags** (what guests want) and its **decor points** (its tier),
and is bought with cash, or in an event's shop. So each idea below names the
tag it serves; an item with no tag is only for looks, which is fine but earns
a guest nothing.

## 1. What the game has today, and where it is thin

Haunted Manor has 25 decor pieces of its own, Frostfang Lodge 6, and 7 are
shared (the bench, the urn planter, three rugs, and the two event pieces once
bought). Counted by the tag a guest asks for (`Pieces.luau`, 2026-10-20):

| Tag | Who wants it | Decor today | Amenity |
|---|---|---|---|
| garden | Pumpkin Head | 6 | Graveyard Garden |
| antique furniture | Ghost | 5 | Quiet Library |
| quiet | Skeleton, Ghost, Yeti | 4, **all Haunted Manor** | Quiet Library (Manor) |
| music; candles; darkness | Skeleton; Pumpkin Head; Vampire Count | 3 each | Music Room, Organ Hall; none; Graveyard Garden |
| damp; slow music | Slime; Zombie | 2 each | none; Music Room |
| snacks | Slime, Zombie | 1 | Snack Bar |
| **dry, dark** | **Mummy** | **1 each** | none |
| **cats, cauldron** | **Witch** | **1 each** | none |
| **moonlight, steak** | **Werewolf** | **1 each** | none |
| **organ music** | **Vampire Count** | **1** | Organ Hall |
| **silence, chandelier** | **Grand Banshee** (Legendary) | **1 each**, Manor only | none |
| cold; snow | Frostfang's Sprite, Imp, Troll, Wyrm; Yeti | 2 each | Aurora Deck (cold) |
| **cocoa, mischief, stone, northern lights** | Frostfang's guests | **1 each** | Cocoa Lounge; none; none; Aurora Deck |

Two findings:

- **The rarer the guest, the fewer the choices.** A player chasing a Werewolf
  or the Banshee has one item per wish and nothing to arrange. That is where
  new decor earns the most: two or three more items for each thin tag.
- **In Frostfang, two wishes cannot be met by furnishing at all**: no decor and
  no amenity a Frostfang hotel may place carries *quiet* (the Yeti's) or
  *silence* (the Aurora Spirit's, its Legendary); the only items with them
  are Haunted Manor's, which a Frostfang hotel cannot place
  (`Pieces.decorHere`). Not checked in a playtest; whether the code meets a
  wish some other way is not checked either.

## 2. More Haunted Manor decor, by the tag it serves

Footprints in 3-stud squares; `W` = Wall layer, `R` = Rug, else Floor.

| Tag (guest) | Idea | Size | What it is |
|---|---|---|---|
| dry, dark (Mummy) | **Canopic Jars** | 1x1 | four lidded jars with animal-head lids on a small stone plinth |
| | **Sarcophagus Lid** | 1x2 W | a painted gold lid leaned against the wall |
| | **Hieroglyph Tapestry** | 2x1 W | a sand-coloured hanging with a painted eye and birds |
| | **Bandage Basket** | 1x1 | a wicker basket of linen rolls (also *snacks*-free fun) |
| | **Desert Rug** | 3x2 R | a woven sand and terracotta rug with a zigzag border |
| cats, cauldron (Witch) | **Cat Tree** | 1x1 | a crooked scratching post with two perches and a sleeping black cat |
| | **Broom Rack** | 1x1 W | three brooms in a wall rack, one with a bow |
| | **Potion Shelf** | 2x1 W | a shelf of glowing bottles (Glow_Magic) |
| | **Spell Book Stand** | 1x1 | an open grimoire on a lectern, a candle beside it |
| | **Cat Bowl Set** | 1x1 R | two bowls on a fish-patterned mat |
| moonlight, steak (Werewolf) | **Moon Lamp** | 1x1 | a glowing full moon on a twisted iron stand (Glow_Cold) |
| | **Skylight Rug** | 2x2 R | a round rug of a starry sky with a crescent |
| | **Butcher's Block** | 1x1 | a wooden block with a cleaver and a ham |
| | **Bone Chew Pile** | 1x1 R | a heap of big chew bones on a tartan dog bed |
| | **Howling Portrait** | 1x1 W | a framed wolf howling at the moon |
| organ music, darkness (Vampire Count) | **Harpsichord** | 2x1 | a black-and-red baroque keyboard |
| | **Bat Roost** | 1x1 W | a beam with three hanging bats |
| | **Candelabra** | 1x1 | a tall seven-branched candelabra (Glow_Warm) |
| | **Velvet Drapes** | 2x1 W | crimson swags with gold tassels (a darker sister of the curtains) |
| | **Wine Rack** | 1x1 W | a diamond rack of dusty red bottles |
| silence, chandelier (Grand Banshee) | **Crystal Chandelier** | 2x2 | a hanging tiered chandelier (needs the ceiling layer, §4.3) |
| | **Hush Bell Jar** | 1x1 | a glass dome over a single white rose, on a pedestal |
| | **Mourning Veil Screen** | 2x1 | a tall folding screen of grey lace |
| | **Silent Harp** | 1x1 | a gilded harp with no strings |
| | **Opera Box Chairs** | 2x1 | two gilt balcony chairs and a little railing |
| snacks (Slime, Zombie) | **Candy Cart** | 2x1 | a striped cart of jars and lollipops |
| | **Brain Jelly Mould** | 1x1 | a wobbling green jelly on a cake stand |
| damp (Slime) | **Drip Bucket** | 1x1 | a bucket under a dripping pipe, a puddle beside it |
| | **Frog Fountain** | 1x1 | a little stone fountain with a frog spout |
| music, slow music (Skeleton, Zombie) | **Bone Xylophone** | 2x1 | a xylophone of rib bones with two mallets |
| | **Music Box** | 1x1 | a tiny dancer turning on a jewelled box (it turns) |
| candles, garden (Pumpkin Head) | **Pumpkin Patch** | 2x2 R | a mat of soil with three pumpkins and vines |
| | **Lantern Tree** | 1x1 | a crooked potted tree hung with paper lanterns (Glow_Warm) |
| quiet, antique furniture (Ghost, Skeleton) | **Writing Desk** | 2x1 | a roll-top desk with an inkwell and a quill |
| | **Rocking Chair** | 1x1 | it rocks slowly by itself |
| | **Gilded Mirror** | 1x1 W | a tall mirror (a ghost shows in it, §4.6) |

## 3. More Frostfang Lodge decor

Its tags: cold, cocoa, mischief, stone, snow, quiet, northern lights, silence.

| Tag | Idea | Size | What it is |
|---|---|---|---|
| cold | **Ice Sculpture** | 1x1 | a carved ice swan on a plinth |
| | **Icicle Chandelier** | 1x1 | a ring of icicles with blue light (Glow_Cold) |
| cocoa | **Cocoa Bar** | 2x1 | a counter with a pot, mugs and a marshmallow jar |
| | **Hot Water Bottle Rug** | 2x2 R | a knitted rug with a cocoa-cup motif |
| mischief | **Snowball Pile** | 1x1 R | a heap of snowballs, one with a face |
| | **Whoopee Cushion Chair** | 1x1 | a squashy armchair that toots (§4.6) |
| stone | **Rune Stone** | 1x1 | a standing stone with glowing runes |
| | **Stone Hearth** | 2x1 W | a fireplace of rough stones with a fire (Glow_Warm) |
| snow, quiet | **Snow Globe Lamp** | 1x1 | a big globe with a cabin inside |
| | **Fur Rug** | 2x2 R | a white fur rug with a bear's head |
| northern lights | **Aurora Window** | 2x1 W | a window of shifting green and violet (Glow_Magic) |
| | **Star Chart** | 1x1 W | a framed chart of the northern sky |
| silence | **Snowdrift Screen** | 2x1 | a curved wall of packed snow |
| quiet | **Reading Nook** | 2x1 | a window seat with cushions, a quilt and a stack of books |
| | **Earmuff Stand** | 1x1 | a coat stand hung with big fluffy earmuffs and scarves |
| silence | **Frozen Bell** | 1x1 | a bronze bell sealed in a block of ice, on a plinth |

## 4. Customizing a room, beyond decor

Each is a system, not a single item; each would need its rule in `MODELS.md`
and a little code. Ordered by what Claude would recommend first.

### 4.1 Wallpaper (wall finishes)

The twin of the floor finishes, which the game already has. Today a room's
walls are built in bands (a wainscot below, a coloured paper, a gold crown).
A **wall finish** would recolour or retexture the paper band, chosen per room,
for the lobby and the hallways, from the kit's set:

- Haunted Manor: Plum Damask, Teal Stripes, Pumpkin Diamonds, Moonlit Stars,
  Bone Lattice, Crimson Velvet, Faded Floral, Bare Plaster.
- Frostfang: Pine Logs, Snow Blocks, Aurora Stripes, Woollen Check.

A second, smaller choice: the **wainscot** colour (dark wood, light wood,
painted black, stone). The model contract would split each wall into its
`Paper` and `Wainscot` parts, as a room's `Floor` is split now.
**Tags:** a finish could carry one (Moonlit Stars: *moonlight*; Bare Plaster:
*dry*), which makes it a cheap way to serve a wish, so it may want a price.

### 4.2 Carpets and rugs

The floor already takes a finish (Plum Carpet is one), and the lobby's runner,
corner and square rugs join edge to edge. More of the same kind:

- **Rug patterns** in each rug shape: Crimson and Gold (today), Teal Medallion,
  Black Cat, Moon Phases, Spider Web, Checkerboard, Persian Plum.
- **Round and oval rugs** (2x2, 3x3) and a **hallway runner with ends**.
- **Floor finishes**: Moss Tiles, Bone Mosaic, Coffin Boards, Cobweb Carpet.

### 4.3 A ceiling layer

Today decor stands on the floor or hangs on a wall, so a chandelier stands on
a post. A **`Ceiling` layer** hangs from the slab above (17 up), over the same
3-stud grid, and never collides: chandeliers, hanging lamps, cobwebs, bats,
banners, a hanging cage, paper lanterns, drapery. Hanging things are what
make a room look full, and they leave the floor free for the guests' path.

### 4.4 Lighting and mood

- A **light colour** per room (warm candle, cold moonlight, green potion,
  violet): the room's own lamp and every glow in it take it.
- **Placeable lights** as decor: wall sconces, floor lamps, candle clusters,
  a fireplace. A *dark* room is then one with few lights, which the Mummy
  and the Vampire Count would like.

### 4.5 The room's own parts

- **Doorway style**: pointed arch (today), round, coffin-shaped, keyhole,
  with or without a curtain.
- **The bed**: two or three styles per room type (a Standard Room's iron bed,
  four-poster or bunk); colour the blanket.
- **The room plaque**: wood (today), brass, bone, a hanging chalkboard.

### 4.6 Decor that does something (ambient life)

Small animations or sounds that make a room feel alive, client-side, no
gameplay: the piano plays a phrase when clicked, the grandfather clock chimes
on the hour and its pendulum swings, the cauldron bubbles, the flytrap snaps
at a passing player, the rocking chair rocks, the music box turns, a ghost
appears in the gilded mirror, curtains sway, candle flames flicker. The
moving part becomes its own part (`MODELS.md` rule 2).

### 4.7 Sets

Matching pieces in one room give a small bonus or a name: the **Gothic
Library** (bookshelf, armchair, side table, writing desk), the **Witch's
Kitchen** (cauldron, potion shelf, broom rack, cat tree), the **Opera Box**.
A set shown in the Book gives players a collecting goal for decor too.

### 4.8 The forecourt and the lobby

The forecourt is the street's shop window, what other players see first:
lamp posts, gravestones, an iron fence, hedges cut into bats, a fountain, a
mailbox, pumpkins, a bench, a "Vacancy" sign. The lobby: a luggage cart, a
bell stand, a guest book, a notice board, statues, a coat stand.

### 4.9 Decor from the collection

A **framed portrait of each resident** for the wall (earned when a guest moves
in), a **statue** of a family when its Book page is complete, a trophy for
Street Favourite: decor that cannot be bought, only earned.

### 4.10 Colour variants

Each piece in two or three colourways (the Velvet Sofa in violet, crimson and
teal). Cheap content for the kit (the same mesh, other palette cells), but
every variant is a model to import, so a handful of pieces at most.

## 5. Seeds for the later locations

- **Bayou Spa**: a cypress planter, a lily-pad rug, a mud bath tub, a lantern
  of fireflies, a rocking chair on a porch plank, a gator-skull lamp.
- **Volcano Resort**: a lava lamp, an obsidian throne, a magma fountain, a
  hot-stone sauna bench, a dragon-egg nest, a basalt column.
- **Sky Castle**: a cloud sofa, a weather vane, a telescope, a wind chime, a
  storm jar (lightning in a bottle), a feathered banner.

## 6. What Claude would do first

1. **Two or three items for each thin tag** (§2's first five groups), and
   first of all **Frostfang's *quiet* and *silence*** (§3): it gives the
   players chasing the rarest guests something to arrange, and it is decor
   only (the kit and the contract exist).
2. **Wallpaper** (§4.1): the biggest change in how a room feels, and it works
   like the floor finishes already built.
3. **The ceiling layer** (§4.3): rooms look full without crowding the floor.
4. **Decor that does something** (§4.6) for a handful of pieces: cheap, and
   it is what players clip and share.

Open for him: whether premium (Robux) decor exists at all (decor points set
a room's tier, so paid decor that raises a tier would be pay-to-win; GDD §10.1
rules out pay-to-win), and whether a wall finish or a light colour may carry a
tag.
