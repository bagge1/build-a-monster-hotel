"""The rig's prototype (LAUNCH.md #6): ONE species built with its armature into its
own set, blender/monsters/rig_proto/, so the Haunted Manor set's manifest and FBX
stay as they are until the rig is proved in Studio (every colour part deforms,
Tiny/Giant scale the bones, the phone's cost).

    blender -b --python-exit-code 1 -t 4 -P tools/build_rig_proto.py -- pose
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monster_kit as k  # noqa: E402
import build_monsters_l1 as l1  # noqa: E402

SET = 'monsters/rig_proto'
SPECIES = ['Skeleton']

if __name__ == '__main__':
    l1.SET = SET
    k.start_set(SET)
    for n in SPECIES:
        l1.BUILDERS[n]()
    k.finish_set(SET)
    k.validate(SET, SPECIES)
