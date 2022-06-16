# IMC 3D segmentation
This pipeline implements functionality for performing 3D segmentation of
IMC datasets, using DeepCell and conversion of 2D masks to 3D.

Results are saved as 3D indexed OME-TIFF images, then converted to 3D meshes
with the Marching Cubes algorithm, and exported as GLB files.
