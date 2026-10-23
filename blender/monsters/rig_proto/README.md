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

**Proved in Studio (2026-10-23, imported with Rig Type Custom, saved as
`assets/Monsters/Skeleton.rbxm`):** the importer's structure (MODELS.md, "The
rig"); `HasSkinnedMesh` on all five colour parts and on nothing else; each
part's skin read back with an EditableMesh: every vertex weighted to bones
the model has, at most 3 influences, summing to 1 (`Body` across all nine,
`Dark` Head/Spine, `Trim` and the eyes rigid on Head); `ScaleTo` 0.5 and 1.5
move every bone exactly with the meshes. In a playtest, the game's
`MonsterKit` and `MonsterAnimator` on the rigged template: every clip turns
the bones as written (Walk: thighs ±25° in opposition, the shin bending back
on the swing, the arms against the legs, the hips dropping 0.15 as the legs
spread; Happy: arms up and out, hops of 0.3; Sad: face down 35°, a lean;
Staff: the right arm reaching forward; CheckIn: the arm sweeping out, a bow,
back at rest by 1.4 s). Cost: 6 µs of CPU a monster a frame (8 for a blended
walk), 0.1 ms for the 16 animated, on August's PC; 14 of 40 within the
70-stud radius moving.

**Not validated:** the mesh seen bending (a background Studio draws no new
frames; it needs Studio in front, or August's eyes in a playtest), the GPU's
cost of skinning, and any of it on a phone.
