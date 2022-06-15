#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.1
label: 3D segmentation for IMC datasets

inputs:
  input_dir:
    label: "Directory containing 3D OME-TIFF images"
    type: Directory
  processes:
    label: "Number of subprocesses"
    type: int
    default: 1

outputs:
  mask_image_dir:
    outputSource: segmentation/mask_image_dir
    type: Directory
    label: "3D segmentation masks, same structure as input dir"
  glb_mesh_dir:
    outputSource: obj_to_glb/glb_mesh_dir
    type: Directory
    label: "GLB directory"

steps:
  copy_expr_images:
    in:
      input_dir:
        source: input_dir
    out: [expr_image_dir]
    run: steps/copy_expr_images.cwl
    label: "Copy expression images to output directory"
  segmentation:
    in:
      input_dir:
        source: input_dir
    out: [mask_image_dir]
    run: steps/segmentation.cwl
    label: "3D IMC segmentation"
  3d_mask_convert:
    in:
      input_dir:
        source:
          segmentation/mask_image_dir
      processes:
        source:
          processes
    out: [obj_mesh_dir]
    run: steps/3d_mask_convert.cwl
    label: "OME-TIFF -> OBJ conversion"
  obj_to_glb:
    in:
      input_dir:
        source:
          3d_mask_convert/obj_mesh_dir
    out: [glb_mesh_dir]
    run: steps/obj_to_glb.cwl
    label: "OBJ -> GLB conversion"
