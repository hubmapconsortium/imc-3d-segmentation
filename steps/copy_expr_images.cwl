cwlVersion: v1.1
class: CommandLineTool
label: Copies expression OME-TIFFs to output directory
requirements:
  DockerRequirement:
      dockerPull: hubmap/3d_mask_convert:latest
baseCommand: "/opt/copy_expr_images.py"

inputs:
  input_dir:
    type: Directory
    inputBinding:
      position: 0
outputs:
  expr_image_dir:
    type: Directory
    outputBinding:
      glob: "expr"
