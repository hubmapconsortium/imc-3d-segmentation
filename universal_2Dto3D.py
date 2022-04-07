import os
from .input_channels_3D import IMC_3D_input_channels
from .segmentation_2D_slices import segmentation
from .match_2D_stacks import match_stacks
from .match_3D_cells import match_3D_cells

def universal_2Dto3D(input_dir, output_dir):
	# get input channels
	nucleus, cytoplasm, membrane = IMC_3D_input_channels(input_dir)
	
	# segmentation for each slice on XY, YZ, XZ axes
	segmentation(nucleus, cytoplasm, membrane, os.path.dirname(input_dir))
	
	# 2D-3D reconstruction
	mask_matched_XY, mask_matched_XZ, mask_matched_YZ = match_stacks(os.path.dirname(input_dir))
	mask_3D = match_3D_cells(mask_matched_XY, mask_matched_XZ, mask_matched_YZ, os.path.dirname(input_dir), output_dir)
	
	return mask_3D
