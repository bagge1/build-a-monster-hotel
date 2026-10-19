"""Set up a machine to work on this game: the memory junction, the tools, the packages.

    python tools/setup_machine.py          # do it
    python tools/setup_machine.py --check  # only report

Claude Code keeps this project's memory in ~/.claude/projects/<encoded repo
path>/memory, outside the repository. The repository carries it in memory/
(skill machine-setup), so this script makes that harness folder a
directory junction to the repo's memory/. A junction needs no admin rights and
every file API sees through it, so memory reads and writes land in the repo and
travel with git. An existing real folder is merged into memory/ first and kept
beside the junction as memory.before-junction-<date>.

Then it checks the tools a session needs (rokit's rojo, wally, stylua, selene;
Blender; Python with numpy and Pillow), runs `rokit install` and `wally
install` where they are missing, and lists what does not travel with git.
"""
from __future__ import annotations

import datetime as _dt
import filecmp
import importlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MEMORY = REPO / "memory"
CHECK = "--check" in sys.argv[1:]

_BLENDER_ROOT = Path(r"C:\Program Files\Blender Foundation")
BLENDER_CANDIDATES = [
    _BLENDER_ROOT / "Blender 5.2" / "blender.exe",
    *(sorted(_BLENDER_ROOT.glob("Blender */blender.exe")) if _BLENDER_ROOT.exists() else []),
]


def say(msg: str) -> None:
    print(msg, flush=True)


def encoded_project_dir(path: Path) -> str:
    """How Claude Code names a project's folder under ~/.claude/projects:
    every character that is not a letter or a digit becomes '-'
    (D:\\Roblox\\sector-omega -> D--Roblox-sector-omega). Windows folders are
    case-insensitive, so a lower-case drive letter lands in the same folder."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def is_junction(p: Path) -> bool:
    if hasattr(os.path, "isjunction"):
        return os.path.isjunction(p)
    try:
        return bool(os.lstat(p).st_file_attributes & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT
    except (OSError, AttributeError):
        return False


def make_junction(link: Path, target: Path) -> None:
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                       check=True, capture_output=True, text=True)
    else:
        os.symlink(target, link, target_is_directory=True)


def setup_memory() -> None:
    harness = Path.home() / ".claude" / "projects" / encoded_project_dir(REPO)
    link = harness / "memory"
    say(f"Memory: repo folder {MEMORY}")
    say(f"        harness folder {link}")
    if not MEMORY.is_dir():
        say("  ERROR: the repo has no memory/ folder; pull first.")
        return
    if is_junction(link):
        same = os.path.realpath(link).lower() == os.path.realpath(MEMORY).lower()
        if same:
            say("  OK: already a junction into the repo.")
            return
        say(f"  a junction to somewhere else ({os.path.realpath(link)}); re-pointing it")
        if not CHECK:
            os.rmdir(link)  # removes the junction only, never its target
    elif link.is_dir():
        files = [f for f in link.iterdir() if f.is_file()]
        say(f"  a real folder with {len(files)} file(s): merging into memory/, then replacing it")
        stamp = _dt.date.today().isoformat()
        for f in files:
            dest = MEMORY / f.name
            if not dest.exists():
                say(f"    + {f.name} (only here; copied into memory/)")
                if not CHECK:
                    shutil.copy2(f, dest)
            elif filecmp.cmp(f, dest, shallow=False):
                pass
            else:
                side = MEMORY / f"{f.stem}.local-{stamp}{f.suffix}"
                say(f"    ! {f.name} differs from the repo copy; kept as {side.name} to merge by hand")
                if not CHECK:
                    shutil.copy2(f, side)
        if not CHECK:
            kept = harness / f"memory.before-junction-{stamp}"
            n = 1
            while kept.exists():
                n += 1
                kept = harness / f"memory.before-junction-{stamp}-{n}"
            link.rename(kept)
            say(f"    the old folder is kept as {kept.name}")
    elif link.exists():
        say(f"  ERROR: {link} exists and is neither a folder nor a junction; remove it by hand.")
        return
    else:
        say("  nothing there yet; creating the junction")
        if not CHECK:
            harness.mkdir(parents=True, exist_ok=True)
    if CHECK:
        say("  (--check: not changed)")
        return
    make_junction(link, MEMORY)
    say("  OK: junction made." if is_junction(link) else "  ERROR: the junction was not made.")


def setup_tools() -> None:
    say("Tools:")
    missing = []
    for tool in ("rojo", "wally", "stylua", "selene"):
        where = shutil.which(tool)
        say(f"  {tool:7} {'OK  ' + where if where else 'MISSING'}")
        if not where:
            missing.append(tool)
    rokit = shutil.which("rokit")
    if missing:
        if rokit and not CHECK:
            say("  running `rokit install` (rokit.toml names the versions)")
            subprocess.run([rokit, "install"], cwd=REPO, check=False)
        elif not rokit:
            say("  rokit is not installed: https://github.com/rojo-rbx/rokit (then `rokit install` here)")
    blender = next((p for p in BLENDER_CANDIDATES if p.exists()), None)
    say(f"  blender {'OK  ' + str(blender) if blender else 'MISSING: install Blender 5.2 to C:/Program Files/Blender Foundation/Blender 5.2/'}")
    for mod, pip in (("numpy", "numpy"), ("PIL", "pillow")):
        try:
            importlib.import_module(mod)
            say(f"  python {mod:6} OK")
        except ImportError:
            say(f"  python {mod:6} MISSING: pip install {pip}")
    if not (REPO / "ServerPackages").is_dir():
        wally = shutil.which("wally")
        if wally and not CHECK:
            say("  ServerPackages/ missing: running `wally install`")
            subprocess.run([wally, "install"], cwd=REPO, check=False)
        else:
            say("  ServerPackages/ missing: run `wally install` (PlayerData cannot load without it)")
    else:
        say("  ServerPackages OK")


def main() -> None:
    say(f"{REPO.name} at {REPO}{'  (--check)' if CHECK else ''}")
    setup_memory()
    setup_tools()
    say("Not in git (skill machine-setup): Roblox Studio with the Rojo plugin; the Claude")
    say("desktop app, whose Studio MCP is what Claude drives Studio with; the effort level and")
    say("model, set in the app; and blender/'s scenes, FBX, renders and 4K source textures:")
    say("rebuild a set from its tools/build_*.py, or copy blender/ from the other machine.")


if __name__ == "__main__":
    main()
