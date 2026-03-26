cwlVersion: v1.1
class: CommandLineTool
label: Convert OBJ formats to GLB after geometry cleanups
requirements:
  DockerRequirement:
      dockerPull: hubmap/3d_mask_convert:latest
baseCommand: "/opt/obj_to_glb.py"

inputs:
  input_dir:
    type: Directory
    inputBinding:
      position: 0
outputs:
  glb_mesh_dir:
    type: Directory
    outputBinding:
      glob: "pipeline_output"
