cwlVersion: v1.1
class: CommandLineTool
label: Copy expression image to output directory
requirements:
  DockerRequirement:
      dockerPull: hubmap/3d_convert_to_ometiff:latest
baseCommand: "/opt/copy_expr_image.py"

inputs:
  input_dir:
    type: Directory
    inputBinding:
      position: 0
outputs:
  image_dir:
    type: Directory
    outputBinding:
      glob: "pipeline_output"
