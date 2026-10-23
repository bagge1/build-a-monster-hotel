# The rig's prototype (LAUNCH.md #6)

ONE species, the Skeleton, built with its Biped armature by
`tools/build_rig_proto.py` (the Haunted Manor builder, its own set folder so
`blender/monsters/haunted_manor/` is untouched until the rig is proved).

    blender -b --python-exit-code 1 -t 4 -P tools/build_rig_proto.py -- pose

**Validated (Blender, 2026-10-23):** the model's contract as before (names,
3,692 triangles + proxy 273, height, Root, markers, eyes), and the rig
round-trip from the FBX: one armature, the ten bones of MODELS.md "The rig"
by name, `RigRoot` at the origin, every visible part (`Body`, `Dark`, `Trim`,
both eyes) skinned with 1-4 influences a vertex summing to 1 and none on
`RigRoot`; `Root`, `LOD_Proxy` and the markers not skinned
(`validation.json`). `review/pose.png` (not in git): a test pose, every
colour part following its bone (legs in stride, arms out, head turned, the
eyes, sockets and bow tie with the head and chest).

**Not validated:** anything in Studio: the import with Rig Type Custom,
where the importer puts the bones and the armature's node (`import_settings.luau`
reports both), every colour MeshPart deforming from the one armature,
`Model:ScaleTo` (Tiny 0.5, Giant 1.5) moving the bones, the clips' look and
the cost of many animated guests on a phone.
