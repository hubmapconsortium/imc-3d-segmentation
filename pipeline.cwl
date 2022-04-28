#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.1
label: 3D segmentation for IMC datasets

inputs:
  image_file:
    label: "3D OME-TIFF"
    type: File

outputs:
  mask_image_file:
    outputSource: segmentation/mask_image_file
    type: File
    label: "3D segmentation mask"

steps:
  segmentation:
    in:
      image_file:
        source: image_file
    out: [mask_image_file]
    run: steps/segmentation.cwl
    label: "3D IMC segmentation"
