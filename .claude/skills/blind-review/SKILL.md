---
name: blind-review
description: A second pair of eyes with no context - pictures of a finished model, a set or the assembled hotel in the game sent to a fresh subagent on another model, which is told only what the thing is for and asked to find what is wrong; then Claude triages every finding (confirmed and fixed, false with the reason, or August's call in WAITING.md). Use it before a model or set is handed to August, after an import once the models are seen in the game, after any change to how a hotel is assembled (lobby, sign, stairs, facade), and whenever he says "granska", "titta på det med nya ögon", "blind review", "review it without context", "another model should look at it", or points out a fault that was obvious in a picture.
---

# Blind review

**His ask, 2026-10-19:** "some other model should scrutinize your work without
context to find errors". He found, in Claude's own playtest pictures, a sign
standing in the hotel's entrance, a check-in desk nobody could stand at, and a
lobby that read as an outdoor patio. Every check Claude had run (rays, walkers,
part counts) passed, because none of them asked *does this make sense as a
hotel?* A reviewer who has not built the thing, and does not know what Claude
believes about it, sees it as a player will.

The first run found the sign as its first finding and the desk among its
first six, unprompted (`blender/hotel/haunted_manor/README.md`, "Blind review").

## When

1. **A model or a set, before it is handed to August**: after the final
   Cycles sheet, before staging (skill `modelling`, its checklist). Renders
   with the 5-stud person beside the model, from the front, the back, the
   game's camera angle and close up where a person uses it.
2. **In the game, after an import or an assembly change**: once the models
   are synced, pictures from a playtest (skill `playtest`): from the street at
   eye height, the game's raised camera, inside each space a person walks in.
   Composition faults (a sign in an entrance, a desk against a wall) exist only
   here: a set's own renders show each piece alone.
3. When August finds a fault a picture would have shown: run it on that
   picture's subject, and add what it missed to the prompt's list below.

## The pictures

- **Three to five**, each named for its view (`1_street.jpg`). A person for
  scale in each (in Studio the player's avatar; in Blender the kit's 5-stud
  figure).
- **No HUD, no labels Claude added**: hide every `ScreenGui` and the CoreGui on
  the client first. Billboards the game itself shows may stay; the prompt
  says to ignore them.
- Wait for `ContentProvider.RequestQueueSize` to reach 0 after a restart, or
  meshes are missing and the reviewer reports them.
- Kept where the work lives: a set's `review/blind/` (not in git), a game run's
  in the scratchpad. The ones that show a finding go to `archive/screens/`.

## The reviewer

- **The Agent tool, `subagent_type: general-purpose`, `model: "fable"`** (a
  model other than the session's own, so it does not share Claude's blind
  spots), in the foreground. About 80k tokens and three minutes a run.
- **The prompt is `prompt.md` in this folder**, filled in. It gives only:
  the paths, what each view is, what the thing is *for* (who uses it, how,
  their size, the game's camera and platform), and what to ignore (labels,
  the HUD). **Never** what Claude thinks is right or wrong with it, what was
  already checked, or a fault Claude or August already knows: that is the
  context the review exists to be without.
- One reviewer per subject. A second run on new pictures after a fix is a new
  agent, not a `SendMessage` to the first: it has seen the old ones.

## Triage: every finding gets one of three answers

Write them in the set's `README.md` under "Blind review <date>" (a game run's
in `TESTRUN.md`), one line each:

- **Confirmed**: proven by geometry where it can be (a ray, a box, a distance
  to the 5-stud person), then fixed: in the build script and rebuilt for a
  model, in the code for an assembly. A fix gets a new blind run on new
  pictures.
- **False**: what the reviewer could not see (a bed out of view, a label it
  misread), with the reason. Never drop one silently.
- **His call**: a look, a placement, a theme. Into `WAITING.md` §2 with the
  reviewer's words and Claude's recommendation. **A fault August has already
  ruled on** (`modelling/taste.md`) is not his call again: it is confirmed.

A finding the reviewer was "unsure" of is still triaged. **August sees the
work only after the triage**: what he is shown has had its obvious faults
fixed or put to him.
