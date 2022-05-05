cwlVersion: v1.1
class: CommandLineTool
label: Convert 3D segmentation mask from OME-TIFF to OBJ
requirements:
  DockerRequirement:
      dockerPull: hubmap/3d_mask_convert:latest
  DockerGpuRequirement: {}
baseCommand: "/opt/voxel_marching_cubes_obj.py"

inputs:
  input_dir:
    type: Directory
    inputBinding:
      position: 0
outputs:
  obj_dir:
    type: Directory
    outputBinding:
      glob: "mask"
