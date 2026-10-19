# Tests

Rules the pure shared modules must keep, run against the real modules in
Studio.

**A spec states rules, never values.** "Buying never costs less than selling
pays", "a rebirth never lowers income", "one large sale pays what ten small ones
do" survive any tuning; a test that pins a number fails the first time
balancing touches it.

## Running them

There is no Luau runtime outside Studio, so the tests run inside it through the
Studio MCP. Claude does this; August does not need to.

1. `python tools/test_bundle.py [spec ...]` joins `harness.luau` and every
   `<name>.spec.luau` (or the named ones) into `src/server/TestBundle.luau`, a
   gitignored ModuleScript that Rojo syncs and nothing in the game requires.
2. Start a playtest, then with the MCP, against the **Server** datamodel:
   `return require(game.ServerScriptService.Server.TestBundle:Clone())`. The
   answer is `<n> passed, <m> failed`, then one `FAIL` line per failure. **Not
   the Edit datamodel**: its module cache outlives a Rojo sync, so it tests
   yesterday's modules (`DEVNOTES.md`).
3. `python tools/test_bundle.py --clean`.

## Writing one

A spec is a chunk, not a module: it runs inside `do ... end` after the harness,
so it sees `Shared` (the `ReplicatedStorage.Shared` folder), `describe`, `it`
and `expect` (`eq`, `near`, `truthy`, `atMost`, `atLeast`). Require what it
tests from `Shared`.

| Spec | What it holds the module to |
|---|---|
| <!-- name --> | <!-- the rules --> |
