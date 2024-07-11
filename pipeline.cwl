#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.1
label: 3D segmentation for IMC datasets

requirements:
  StepInputExpressionRequirement: {}

inputs:
  input_dir:
    label: "Directory containing 3D OME-TIFF images"
    type: Directory
  processes:
    label: "Number of subprocesses"
    type: int
    default: 1

outputs:
  expr_image_dir:
    outputSource: normalize_expr_images/output_dir
    type: Directory[]
    label: "Expression OME-TIFF images"
  mask_image_dir:
    outputSource: segmentation/mask_image_dir
    type: Directory
    label: "3D segmentation masks, same structure as input dir"
  glb_mesh_dir:
    outputSource: obj_to_glb/glb_mesh_dir
    type: Directory
    label: "GLB directory"

steps:
  normalize_expr_images:
    in:
      data_dir:
        source: input_dir
      output_path_prefix:
        valueFrom: "expr"
    out: [output_dir]
    run: ome-tiff-normalize/ome_tiff_normalize.cwl
    label: "Write normalized OME-TIFF expression images"
  segmentation:
    in:
      input_dir:
        source: input_dir
    out: [results_dir]
    run: steps/segmentation.cwl
    label: "3D IMC segmentation"
  convert_to_ometiff:
    in:
      input_dir:
        source: segmentation/input_dir
      segmentation_results_dir:
        source: segmentation/results_dir
    out: [mask]
    run: steps/convert_to_ometiff.cwl
    label: "Segmentation mask consolidation to OME-TIFF"
  obj_to_glb:
    in:
      input_dir:
        source:
          3d_mask_convert/obj_mesh_dir
    out: [glb_mesh_dir]
    run: steps/obj_to_glb.cwl
    label: "OBJ -> GLB conversion"
