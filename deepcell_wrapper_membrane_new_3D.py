from skimage.io import imread
from skimage.io import imsave
from deepcell.applications import MultiplexSegmentation

from os.path import join
import numpy as np
import sys

file_dir = sys.argv[1]
axis = sys.argv[2]

im1 = imread(join(file_dir, 'nucleus.tif'))
im2 = imread(join(file_dir, 'membrane.tif'))
z_slice_num = im1.shape[0]

if axis == 'XY':
	pass
elif axis == 'XZ':
	im1 = np.rot90(im1, k=1, axes=(2, 0))
	im2 = np.rot90(im2, k=1, axes=(2, 0))
elif axis == 'YZ':
	im1 = np.rot90(im1, k=1, axes=(1, 0))
	im2 = np.rot90(im2, k=1, axes=(1, 0))


im = np.stack((im1, im2), axis=-1)
if axis == 'XY':
	pass
elif axis == 'XZ':
	im_zeros = np.zeros((im.shape[0], im.shape[1], im.shape[0]-im.shape[2], im.shape[3]))
	im = np.dstack((im, im_zeros))
elif axis == 'YZ':
	im_zeros = np.zeros((im.shape[0], im.shape[2]-im.shape[1], im.shape[2], im.shape[3]))
	im = np.hstack((im, im_zeros))


from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
import tensorflow as tf
#
config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
config.gpu_options.per_process_gpu_memory_fraction = 0.9
tf.compat.v1.keras.backend.set_session(tf.compat.v1.Session(config=config))
app = MultiplexSegmentation()


for i in range(len(im)):
	if i == 0:
		labeled_image = app.predict(np.expand_dims(im[i], 0), compartment='both')
	else:
		labeled_image = np.vstack((labeled_image, app.predict(np.expand_dims(im[i], 0), compartment='both')))
print(z_slice_num)
if axis == 'XY':
	cell_mask = labeled_image[:, :, :, 0]
	nuc_mask = labeled_image[:, :, :, 1]
elif axis == 'XZ':
	cell_mask = labeled_image[:, :, :z_slice_num, 0]
	nuc_mask = labeled_image[:, :, :z_slice_num, 1]
elif axis == 'YZ':
	cell_mask = labeled_image[:, :z_slice_num, :, 0]
	nuc_mask = labeled_image[:, :z_slice_num, :, 1]


imsave(join(file_dir, 'mask_' + axis + '.tif'), cell_mask)
imsave(join(file_dir, 'nuclear_mask_' + axis + '.tif'), nuc_mask)



print(cell_mask.shape)
np.save(join(file_dir, 'mask_' + axis + '.npy'), cell_mask)


np.save(join(file_dir, 'nuclear_mask_' + axis + '.npy'), nuc_mask)

