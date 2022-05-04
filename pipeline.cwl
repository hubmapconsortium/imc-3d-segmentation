#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.1
label: 3D segmentation for IMC datasets

inputs:
  input_dir:
    label: "Directory containing 3D OME-TIFF images"
    type: Directory

outputs:
  mask_image_dir:
    outputSource: segmentation/mask_image_dir
    type: File[]
    label: "3D segmentation masks, same structure as input dir"

steps:
  segmentation:
    in:
      input_dir:
        source: input_dir
    out: [mask_image_dir]
    run: steps/segmentation.cwl
    label: "3D IMC segmentation"
