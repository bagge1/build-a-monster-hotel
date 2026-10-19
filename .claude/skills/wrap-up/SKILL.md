---
name: wrap-up
description: Ends a session cleanly at a review point - the set's README, the memory for the work, WAITING.md, git status, a commit of only this session's own files, and telling August it is a good place to start a new session. Use it when a session is past roughly 250k tokens and reaches a boundary (a model handed to him, a phase committed, a question waiting on him), before an unattended stop, and whenever he says "avsluta", "vi stannar här", "runda av", "spara läget", "skriv överlämningen", "dags för ny session", "byt session", "committa", "wrap up", "hand off", "end the session" or "commit this", and whenever a commit is about to be made, since how often to commit is here too.
---

# Wrap-up at a review point

Cost is the number of calls times the size of the context, so a long session
that reaches a boundary hands over and stops: the next session starts small.
The point is the boundary, not the limit.

Batch the reads below: the files and `git status` go out in one message.

1. **The set's `README.md`**, for every model set the session built or
   changed: what was done, what was validated and what was not, and "Studio
   runtime is not tested" until something has been seen running. A model's
   state and his rulings for it live there, never in a memory of its own.
2. **The memory for the work** (`memory/<name>.md`), when the work is not a
   model. State, not a log: what stands, what is next, his rulings for that
   work. Rewrite the state rather than append a round. If its line in
   `MEMORY.md` no longer says where the work stands, rewrite that line (one
   line, ~120 characters, only the hook). A lesson or a decision of his that
   changes *how* a job is done goes into that job's skill in
   `.claude/skills/`, not into memory.
3. **`WAITING.md`**: add what the session leaves him (an import with its
   staging folder named, a look, a flight, a ruling), and strike what he has
   answered: `~~the item~~` and where the answer went (`GDD §4.2`, a set's
   README, a commit). Written in Swedish, keeping the game's English names.
   Nothing goes in if nothing actually waits on him.
4. **`git status`**. Several sessions may share this tree: a modified file you
   did not touch is another session's. Stage only your own files, by path,
   never `git add -A` or `git add .`; the memory files the session changed are
   among them.
5. **Commit** once per finished piece of work (below). The message says what
   changed and why, with his rulings dated. Push if the repo has a remote,
   unless he has said otherwise.
6. **Tell him**, in the language he wrote in: what was done, what now waits on
   him (by its `WAITING.md` §), and that this is a good place to start a new
   session. If something only he can do comes next in Studio (the **Connect**
   button under the **Plugins** tab, an import, a flight), say where it is.

## How often to commit

While iterating on a look with him round by round (colour, outline, size), do
not commit and push after every round: keep the work in the tree and commit
once, when he accepts it or the session reaches a boundary. Rounds of the same
picture are one piece of work ("maybe not commit and push a million commits
btw lol", 2026-10-04). Still commit before ending a session, and still stage
only your own files.
