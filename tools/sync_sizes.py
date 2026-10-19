"""Prints a Luau table of every synced script's expected byte size, for the
sync check in skill `playtest` ("The sync landed"): paste it into an Edit
execute_luau that compares it with each script's #Source in Studio.

    python tools/sync_sizes.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = {
    "src/server": "ServerScriptService.Server",
    "src/shared": "ReplicatedStorage.Shared",
    "src/client": "StarterPlayer.StarterPlayerScripts.Client",
}
rows = []
for folder, path in MAP.items():
    for f in sorted((ROOT / folder).glob("*.luau")):
        name = f.name.split(".")[0]
        inst = path if name == "init" else f"{path}.{name}"
        size = len(f.read_bytes().replace(b"\r\n", b"\n"))  # Studio keeps LF
        rows.append(f'["{inst}"]={size}')
print("{" + ",".join(rows) + "}")
