---
name: night-sprint
description: Runs an unattended night session while August sleeps - the brief and the go he gives before he leaves, starting as /loop with no interval, the usage gates (90 % weekly, the 5-hour window), sleeping to a reset with ScheduleWakeup, the night's log in archive/NATTLOGG-<date>.md, never waiting for an answer, forks into WAITING.md, commits per step, keeping Studio alive, and the morning hand-over. Use it whenever August says "natt", "i natt", "nattsession", "nattsprint", "kör i natt", "medan jag sover", "jag går och lägger mig", "god natt", "overnight", "night sprint", "while I sleep", "tonight", or starts a /loop with a brief and leaves, and whenever a session is running unattended.
---

# A night sprint

August sleeps; the session works through his brief alone and he reads the
log in the morning. Sector Omega ran five of these: one built four phases in a
night, one built nine systems in an hour, one ran a 28-hull import and a
playtest end to end. What made them work is below. Every rule is his or was
learned the hard way.

## Before he leaves (with him, in this chat)

1. **The brief, in order.** Write it back to him as a numbered list: what
   each step is, what "done" is, and what to do if a step is blocked (skip to
   the next, never wait). Work that needs a new model from him, his look, or a
   value changed is not night work.
2. **His go, here.** A go given to another session does not carry to this one,
   and an earlier "pause" he said in this chat still stands until he lifts it.
   Anything that writes a DataStore, merges a branch or pushes needs a
   permission rule from him first: the session's own safety check refuses it
   at night otherwise, and nobody is there to approve.
3. **Studio, if the brief needs it:** the published place open (never a local
   file), Studio maximized, the Rojo plugin **Connected** (Studio, **Plugins**
   tab; his click), nothing importing.
4. **Usage**: read it (`mcp__ccd_session_mgmt__get_usage`) and tell him the
   two figures, so he knows how much night there is.
5. **He starts it as `/loop` with no interval**, followed by the brief.
   That is what makes the session self-paced and able to sleep:
   `ScheduleWakeup` exists only in that mode.

## The log

Write the night's plan and log as `archive/NATTLOGG-<date>.md` before the
first step, in Swedish or English as he wrote the brief:

```markdown
# Nattlogg — <date>

Unattended night session (`/loop`, self-paced) while August sleeps. His brief, in order:

1. **<step>.** <what, and what done is>
2. ...

## Rules for the night

- Usage before every step: weekly ≥ 90 % → finish, commit, wrap up, end.
  5-hour ≥ 90 % → finish, commit, sleep past the reset.
- <the brief's own rules: never restart Rojo, no value changes, ...>
- Never wait for an answer: take the reversible option, write the assumption here.

## Log

- **03:35** Start. Usage: 5-hour 53 %, weekly 44 %. <state found>
- **03:59** <what happened, with numbers> ...

## In the morning
<what was done, what was not and why, what waits on him (by WAITING.md §)>
```

- **Read the time from `date`**, never from memory or a guess.
- One line per event, with the numbers that prove it ("all 14 OK: 7
  Precise/55 Box"), not "looks fine".
- What waits on him goes in `WAITING.md`, not only in the log.

## Each step

1. **Usage** (`get_usage`). Weekly at or over **90 %**: finish nothing new;
   commit, write the morning section, wrap up, end the loop. The 5-hour window
   at or over **~90 %**: finish the step in hand, commit, then sleep until it
   resets. Extra usage is off: a full window stops the session hard,
   mid-edit.
2. **Do the step.** Prove it the way a day session would: run it in Studio if
   it can be run there, specs for rules, a read-back in a separate call for
   anything set through the MCP. What could not be run is written as "not run
   in Studio" in the log and in memory `phase-status`. A night that builds
   phases nobody plays leaves weeks of "verified by script" behind it.
3. **Commit** the step (only this session's files, by path; push if the repo
   has a remote and he allowed it). A crash at 4 a.m. then loses one step.
4. **Log line**, then the next step.

## Never wait

- **No answer will come.** Take the reversible option, write the assumption in
  the log, keep going. A fork that is his (a design choice, a look, a value)
  goes into `WAITING.md` with the options and a recommendation, and the step
  moves on without it, or is skipped.
- **Values are his.** Never change one at night, even to make a test pass. A
  measurement that disagrees with what was balanced is logged with its numbers
  and goes to `WAITING.md`.
- **Blocked on Studio** (the plugin disconnected, the MCP gone, Studio hung):
  log it, put a **Connect** or a restart in `WAITING.md` §0, and carry on with
  the steps that need no Studio. Never restart `rojo serve`: it is his.

## Sleeping

- `ScheduleWakeup` takes at most 3600 s a call: chain calls to the reset time
  the usage reading gives, and say in `reason` what is awaited ("5-hour
  window resets 06:10").
- Waiting on something outside (his import finishing, a long build): check at
  a pace matched to how fast it changes (an import: every 5 minutes; call it
  stalled after 45 minutes with no change), and log each check in one line.
- A step that finishes needs no sleep: go on to the next one in the same turn.

## Keep Studio alive

- **One playtest per step**, stopped at its end. The MCP cannot start a
  playtest right after stopping one (`DEVNOTES.md`): leave a pause, and if it
  answers "Start play hasn't finished yet", the step goes without one.
- **No heavy renders while Studio runs** (no EEVEE/Cycles sheets): a GPU hang
  lost Studio for the rest of the first night.
- A big batch set through the MCP (collision on many models) times the call
  out and drops the MCP for ~5 minutes, but the values land: wait for
  `list_roblox_studios` to show Studio again, then read back.

## Keep the context small

Nobody can start a fresh session at night, so the one session carries the
whole night. Hand independent heavy pieces (a rebuild, a long investigation)
to background agents, one per piece, with a shared brief, unique scratch file
names, and never two writers on one file. Their reports stay out of this
context, which is what makes a long night affordable.

## In the morning

Write the log's last section: what was done (with commits), what was not and
why, and what now waits on him by its `WAITING.md` §. Update memory
`phase-status`. Commit. When he is back, tell him in a few lines, in his
language, and that it is a good place to start a new session (skill
`wrap-up`).
