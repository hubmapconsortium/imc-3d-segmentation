cwlVersion: v1.1
class: CommandLineTool
label: Copy expression image to output directory
requirements:
  DockerRequirement:
      dockerPull: hubmap/3d_convert_to_ometiff:latest
baseCommand: "/opt/adjust_expr_image.py"

inputs:
  input_dir:
    type: Directory
    inputBinding:
      position: 0
  nucleus_markers:
    type: string
    inputBinding:
      position: 1
      prefix: "--nucleus"
  cytoplasm_markers:
    type: string
    inputBinding:
      position: 2
      prefix: "--cytoplasm"
  membrane_markers:
    type: string
    inputBinding:
      position: 3
      prefix: "--membrane"
outputs:
  image_dir:
    type: Directory
    outputBinding:
      glob: "pipeline_output"
