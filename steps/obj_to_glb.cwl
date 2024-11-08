cwlVersion: v1.1
class: CommandLineTool
label: Convert OBJ formats to GLB after geometry cleanups
requirements:
  DockerRequirement:
      dockerPull: hubmap/3d_mask_convert:2.0
baseCommand: "/opt/obj_to_glb.py"

inputs:
  input_dir:
    type: Directory
    inputBinding:
      position: 0
  object_id_mapping:
    type: File
    inputBinding:
      position: 1
outputs:
  glb_mesh_dir:
    type: Directory
    outputBinding:
      glob: "pipeline_output"
