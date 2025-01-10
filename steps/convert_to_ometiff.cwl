cwlVersion: v1.1
class: CommandLineTool
label: Consolidate individual masks to multichannel OME-TIFF
requirements:
  DockerRequirement:
      dockerPull: hubmap/3d_convert_to_ometiff:2.1
baseCommand: "/opt/convert_to_ometiff.py"

inputs:
  input_dir:
    type: Directory
    inputBinding:
      position: 0
  segmentation_results_dir:
    type: Directory
    inputBinding:
      position: 1
outputs:
  mask:
    type: Directory
    outputBinding:
      glob: "pipeline_output"
  object_id_mapping:
    type: File
    outputBinding:
      glob: "object_id_mapping.json"
