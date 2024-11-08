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
  nucleus_markers:
    type: string
  cytoplasm_markers:
    type: string
  membrane_markers:
    type: string

outputs:
  segmentation_mask:
    outputSource: convert_to_ometiff/mask
    type: Directory
    label: "3D segmentation masks, same structure as input dir"
  glb_mesh_dir:
    outputSource: obj_to_glb/glb_mesh_dir
    type: Directory
    label: "GLB directory"
  expr_image:
    outputSource: copy_expr_image/image_dir
    type: Directory
    label: "Expression image used as input"

steps:
  segmentation:
    in:
      input_dir:
        source: input_dir
      nucleus_markers:
        source: nucleus_markers
      cytoplasm_markers:
        source: cytoplasm_markers
      membrane_markers:
        source: membrane_markers
    out: [results_dir]
    run: steps/segmentation.cwl
    label: "3D IMC segmentation"
  convert_to_ometiff:
    in:
      input_dir:
        source: input_dir
      segmentation_results_dir:
        source: segmentation/results_dir
    out: [mask, object_id_mapping]
    run: steps/convert_to_ometiff.cwl
    label: "Segmentation mask consolidation to OME-TIFF"
  copy_expr_image:
    in:
      input_dir:
        source: input_dir
    out: [image_dir]
    run: steps/copy_expr_image.cwl
    label: "Copy expression image to output dir"
  obj_to_glb:
    in:
      input_dir:
        source:
          segmentation/results_dir
      object_id_mapping:
        source:
          convert_to_ometiff/object_id_mapping
    out: [glb_mesh_dir]
    run: steps/obj_to_glb.cwl
    label: "OBJ -> GLB conversion"
