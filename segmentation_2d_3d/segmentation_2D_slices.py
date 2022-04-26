import os
from skimage.io import imsave
from os.path import join
def segmentation(nucleus, cytoplasm, membrane, save_dir):
	imsave(join(save_dir, 'nucleus.tif'), nucleus)
	imsave(join(save_dir, 'cytoplasm.tif'), cytoplasm)
	imsave(join(save_dir, 'membrane.tif'), membrane)
	os.system('bash run_deepcell_membrane_new_3D.sh ' + save_dir)
	os.system('rm ' + join(save_dir, 'nucleus.tif'))
	os.system('rm ' + join(save_dir, 'cytoplasm.tif'))
	os.system('rm ' + join(save_dir, 'membrane.tif'))
