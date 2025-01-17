#!/usr/bin/env -S blender -b -P
import json
import logging
import sys
from math import radians
from os import fspath
from pathlib import Path
from typing import Dict

import bmesh
import bpy
import manhole

# Can't import from common/utils.py due to differences running under Blender
output_path = Path("pipeline_output/mesh")


def convert(obj_file: Path, glb_file: Path, mapping: Dict[str, int]):
    logging.info("Converting %s to %s", obj_file, glb_file)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    bpy.ops.import_scene.obj(
        filepath=fspath(obj_file),
        use_split_groups=True,
    )
    meshes = {o.data for o in bpy.context.selected_objects if o.type == "MESH"}

    bm = bmesh.new()

    logging.info("Performing limited dissolve cleanup on %d meshes", len(meshes))
    for m in meshes:
        bm.from_mesh(m)
        bmesh.ops.dissolve_limit(
            bm,
            angle_limit=radians(5),
            verts=bm.verts,
            edges=bm.edges,
        )
        bm.to_mesh(m)
        m.update()
        bm.clear()

    bm.free()

    objs_to_assign = list(bpy.data.objects)
    logging.info("Assigning %d objects to parent", len(objs_to_assign))
    mask_parent = bpy.data.objects.new("Segmentation_Mask", None)
    for obj in objs_to_assign:
        obj.name = f"Cell_{mapping[obj.name]}"
        obj.parent = mask_parent

    logging.info("Linking parent object to scene")
    bpy.context.scene.collection.objects.link(mask_parent)
    logging.info("Saving GLB")
    bpy.ops.export_scene.gltf(filepath=fspath(glb_file))


def main(directory: Path, object_id_mapping_file: Path, base_dir: Path = output_path):
    with open(object_id_mapping_file) as f:
        mapping = json.load(f)
    for obj_file in directory.glob("**/*.obj"):
        glb_file = base_dir / obj_file.relative_to(directory).with_suffix(".glb")
        glb_file.parent.mkdir(exist_ok=True, parents=True)
        convert(obj_file, glb_file, mapping)
    # apparently necessary due to Blender's runtime:
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(
        format="{asctime:<15} {levelname:<7} | {message}",
        style="{",
        level=logging.INFO,
    )
    manhole.install(activate_on="USR1")

    # TODO: maybe try to use argparse again; Blender's runtime
    #   complicates that quite a bit
    # here, sys.argv[:4] = ['blender', '-b', '-P', __file__]
    if len(sys.argv) != 6:
        raise ValueError(
            "Need exactly two arguments: directory containing OBJ files, and JSON file"
        )
    main(Path(sys.argv[4]), Path(sys.argv[5]))
