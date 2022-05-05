cwlVersion: v1.1
class: CommandLineTool
label: 3D segmentation for IMC
requirements:
  DockerRequirement:
      dockerPull: hubmap/imc_3d_segmentation:latest
  DockerGpuRequirement: {}
baseCommand: "/opt/universal_2Dto3D.py"

inputs:
  input_dir:
    type: Directory
    inputBinding:
      position: 0
outputs:
  mask_image_dir:
    type: Directory
    outputBinding:
      glob: "mask"
