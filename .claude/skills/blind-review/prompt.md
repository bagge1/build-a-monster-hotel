# The blind reviewer's prompt

Fill the `<...>` parts and send the rest as it stands. Add nothing about what
Claude believes is right or wrong with the subject (skill `blind-review`).

---

You are reviewing a 3D game asset from pictures alone. You have no other
context, and you should not look at any other files. Your job is to find what
is wrong with it. Assume there are faults; the person who built it is too
close to it to see them.

Look at these pictures (open each with your Read tool):
- `<path>` (<the view: where the camera is, what it faces>)
- ...

What it is meant to be: <what the thing is, in the game's words, and what it
is for: who uses it, in what order, what they must be able to do there>.
Players walk around with ordinary Roblox avatars about 5 studs tall (<which
figure in the pictures is one>). The camera is usually raised behind the
player, and the game is played mostly on phones. <What to ignore: floating
labels, the small guest characters, a grey placeholder named as such.>

Scrutinize it as a demanding art director and a level designer would:
1. Function: can a person and a guest actually do what the place or thing is
   for? Anything blocking a path, an entrance, a doorway or a view; anything a
   person cannot stand at, reach or fit through; anything at the wrong scale
   for a 5-stud person.
2. Does each part read as what it is meant to be? Would a player recognise it?
   Name anything that reads as something else.
3. Placement and composition: things in front of other things, in the wrong
   place, overlapping, floating, clipping, sunk into floors, misaligned.
4. Look: anything that looks broken, unfinished, or ugly.

Answer with a numbered list, most serious first. For each fault: what you see,
in which picture and where in it, why it is a problem, and how certain you are
(certain / likely / unsure). Then, separately, anything you could not judge
from these pictures and which extra view would settle it. Do not praise; do
not soften. Keep it under 500 words.

---

## What a past review missed

When August finds a fault a blind review did not, add a line here naming the
kind of fault, and a sentence for it to the prompt's list above.

- (none yet)
