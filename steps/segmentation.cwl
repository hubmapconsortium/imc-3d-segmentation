cwlVersion: v1.1
class: CommandLineTool
label: 3D segmentation for IMC
requirements:
  DockerRequirement:
      dockerPull: hubmap/imc_3d_segmentation:2.1
  DockerGpuRequirement: {}
  NetworkAccess:
    networkAccess: true
baseCommand: ["python", "/opt/run_3DCellComposer.py"]

inputs:
  input_dir:
    type: Directory
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
  results_dir:
    type: Directory
    outputBinding:
      glob: "results"
