#!/usr/bin/env -S blender -b -P
from argparse import ArgumentParser
from os import fspath
from pathlib import Path
from typing import Iterable

import bmesh
import bpy


def convert(obj_file: Path, glb_file: Path):
    print("Converting", obj_file, "to", glb_file)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    bpy.ops.import_scene.obj(
        filepath=fspath(obj_file),
        use_split_groups=True,
    )

    meshes = {o.data for o in bpy.context.selected_objects if o.type == "MESH"}

    bm = bmesh.new()

    for m in meshes:
        bm.from_mesh(m)
        bmesh.ops.dissolve_limit(bm, verts=bm.verts, edges=bm.edges)
        bm.to_mesh(m)
        m.update()
        bm.clear()

    bm.free()

    bpy.ops.export_scene.glb(filepath=fspath(glb_file))


def main(directory: Path):
    for obj_file in directory.glob("**/*.obj"):
        glb_file = obj_file.relative_to(directory).with_suffix(".glb")
        glb_file.parent.mkdir(exist_ok=True, parents=True)
        convert(obj_file, glb_file)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("directory", type=Path)
    args = p.parse_args()

    main(args.directory)
