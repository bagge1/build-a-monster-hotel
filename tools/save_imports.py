"""Save an import's models to their .rbxm files without August's Save to File.

The Studio MCP cannot write a file, but it can serialize a model
(`SerializationService`), and everything Studio prints lands in its log on
disk, which this script can read (DEVNOTES.md, "Saving an import without Save
to File"). Three steps, after the import settings are set and read back:

1. `python tools/save_imports.py luau` prints two Luau snippets. Run the first
   in the Edit datamodel: it serializes every Model in Workspace, or only
   those named in its `names` table. It returns at once; the work goes on in
   the background.
2. Run the second in a separate call: it prints every model as base64 lines
   tagged `@@RBXM`, and reports how many it printed. Run it again if it says
   the first is not finished.
3. `python tools/save_imports.py write assets/<folder>/<Name>.rbxm ...` reads
   the newest Studio log, decodes each file's model by its name (the file name
   is the instance name), checks the byte count and the file's start and end,
   and writes the files. It writes nothing if any one is missing or broken.

Then read the synced copies under ReplicatedStorage (ServerStorage for
the server-only templates) back once (collision,
mesh ids, sizes against the Workspace import), and delete the Workspace copies
and `ServerStorage._ClaudeSerialize`.
"""
import base64
import glob
import os
import re
import sys
from collections import defaultdict

SERIALIZE = r'''-- 1: serialize (Edit datamodel); returns at once
local names = {...}  -- the model names, or leave empty for every Model in Workspace
local SS, ES = game:GetService("SerializationService"), game:GetService("EncodingService")
local f = game:GetService("ServerStorage"):FindFirstChild("_ClaudeSerialize") or Instance.new("Folder")
f.Name = "_ClaudeSerialize"
f:ClearAllChildren()
f.Parent = game:GetService("ServerStorage")
if #names == 0 then
	for _, c in workspace:GetChildren() do if c:IsA("Model") then table.insert(names, c.Name) end end
end
f:SetAttribute("total", #names)
f:SetAttribute("done", 0)
f:SetAttribute("err", "")
-- Waiting on SerializeInstancesAsync inside the MCP call hangs it; spawned, it finishes.
task.spawn(function()
	for _, n in names do
		local ok, e = pcall(function()
			local b = SS:SerializeInstancesAsync({ workspace[n] })
			local s = buffer.tostring(ES:Base64Encode(b))
			-- a StringValue holds under 200,000 characters: a large model is kept in pieces
			local v = Instance.new("Folder")
			v.Name = n
			v:SetAttribute("bytes", buffer.len(b))
			for i = 1, math.ceil(#s / 180000) do
				local piece = Instance.new("StringValue")
				piece.Name = tostring(i)
				piece.Value = s:sub((i - 1) * 180000 + 1, i * 180000)
				piece.Parent = v
			end
			v.Parent = f
		end)
		if not ok then f:SetAttribute("err", f:GetAttribute("err") .. n .. ": " .. tostring(e) .. "\n") end
		f:SetAttribute("done", f:GetAttribute("done") + 1)
	end
end)
return #names .. " queued"'''

PRINT = r'''-- 2: print to the log (a separate call)
local f = game:GetService("ServerStorage")._ClaudeSerialize
if f:GetAttribute("done") < f:GetAttribute("total") then
	return ("not finished: %d/%d"):format(f:GetAttribute("done"), f:GetAttribute("total"))
end
local CH, lines = 800, 0  -- the log cuts a line at 1022 characters, its own prefix and a long name included
for _, v in f:GetChildren() do
	local pieces = {}
	for i = 1, #v:GetChildren() do pieces[i] = v[tostring(i)].Value end
	local s = table.concat(pieces)
	local n = math.ceil(#s / CH)
	for i = 1, n do
		print(("@@RBXM %s %d %d/%d %s"):format(v.Name, v:GetAttribute("bytes"), i, n, s:sub((i - 1) * CH + 1, i * CH)))
		lines += 1
	end
end
return ("%d models, %d lines, errors: %s"):format(#f:GetChildren(), lines, f:GetAttribute("err"))'''

LINE = re.compile(r'@@RBXM (\S+) (\d+) (\d+)/(\d+) ([A-Za-z0-9+/=]+)')


def newest_log():
    logs = glob.glob(os.path.expandvars(r'%LOCALAPPDATA%\Roblox\logs\*Studio*_last.log'))
    if not logs:
        sys.exit('no Studio log under %LOCALAPPDATA%\\Roblox\\logs')
    return max(logs, key=os.path.getmtime)


def read_models(log):
    """Each model's bytes from its last complete print in the log."""
    chunks, size = defaultdict(dict), {}
    for m in LINE.finditer(open(log, encoding='utf-8', errors='replace').read()):
        name, nbytes, i, n, data = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5)
        if i == 1:
            chunks[name] = {}   # a later print of the same model replaces an earlier one
        chunks[name][i] = data
        size[name] = (nbytes, n)
    models, faults = {}, {}
    for name, (nbytes, n) in size.items():
        if sorted(chunks[name]) != list(range(1, n + 1)):
            faults[name] = f'{len(chunks[name])} of {n} lines'
            continue
        raw = base64.b64decode(''.join(chunks[name][i] for i in range(1, n + 1)))
        if len(raw) != nbytes or not raw.startswith(b'<roblox!') or not raw.endswith(b'</roblox>'):
            faults[name] = f'{len(raw)} bytes decoded, {nbytes} printed'
            continue
        models[name] = raw
    return models, faults


def write(paths):
    log = newest_log()
    models, faults = read_models(log)
    missing = [p for p in paths if os.path.splitext(os.path.basename(p))[0] not in models]
    for p in missing:
        name = os.path.splitext(os.path.basename(p))[0]
        print(f'{name}: {faults.get(name, "not in the log")}')
    if missing:
        sys.exit(f'nothing written ({len(missing)} of {len(paths)} not found whole in {os.path.basename(log)})')
    for p in paths:
        os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
        with open(p, 'wb') as fh:
            fh.write(models[os.path.splitext(os.path.basename(p))[0]])
        print('wrote', p)


if __name__ == '__main__':
    if sys.argv[1:2] == ['luau']:
        print(SERIALIZE, PRINT, sep='\n\n')
    elif sys.argv[1:2] == ['write'] and len(sys.argv) > 2:
        write(sys.argv[2:])
    else:
        sys.exit(__doc__)
