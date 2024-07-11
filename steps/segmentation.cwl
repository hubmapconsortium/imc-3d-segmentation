cwlVersion: v1.1
class: CommandLineTool
label: 3D segmentation for IMC
requirements:
  DockerRequirement:
      dockerPull: hubmap/imc_3d_segmentation:latest
  DockerGpuRequirement: {}
  NetworkAccess:
    networkAccess: true
baseCommand: ["python", "/opt/run_3DCellComposer.py"]

inputs:
  image:
    type: File
    inputBinding:
      position: 0
  nucleus_markers:
    type: string
    inputBinding:
      position: 1
  cytoplasm_markers:
    type: string
    inputBinding:
      position: 2
  membrane_markers:
    type: string
    inputBinding:
      position: 3
outputs:
  mask_image_dir:
    type: Directory
    outputBinding:
      glob: "results"
