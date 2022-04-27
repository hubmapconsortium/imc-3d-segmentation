#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import tensorflow as tf
from deepcell.applications import MultiplexSegmentation
from skimage.io import imread, imsave
from tensorflow.compat.v1 import ConfigProto, InteractiveSession


def main(input_dir: Path, axis: str, output_dir: Path):
    im1 = imread(input_dir / "nucleus.tif")
    im2 = imread(input_dir / "membrane.tif")
    z_slice_num = im1.shape[0]

    if axis == "XY":
        pass
    elif axis == "XZ":
        im1 = np.rot90(im1, k=1, axes=(2, 0))
        im2 = np.rot90(im2, k=1, axes=(2, 0))
    elif axis == "YZ":
        im1 = np.rot90(im1, k=1, axes=(1, 0))
        im2 = np.rot90(im2, k=1, axes=(1, 0))

    im = np.stack((im1, im2), axis=-1)
    if axis == "XY":
        pass
    elif axis == "XZ":
        im_zeros = np.zeros((im.shape[0], im.shape[1], im.shape[0] - im.shape[2], im.shape[3]))
        im = np.dstack((im, im_zeros))
    elif axis == "YZ":
        im_zeros = np.zeros((im.shape[0], im.shape[2] - im.shape[1], im.shape[2], im.shape[3]))
        im = np.hstack((im, im_zeros))

    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)
    config.gpu_options.per_process_gpu_memory_fraction = 0.9
    tf.compat.v1.keras.backend.set_session(tf.compat.v1.Session(config=config))
    app = MultiplexSegmentation()

    predictions = [
        app.predict(np.expand_dims(im[i], 0), compartment="both") for i in range(len(im))
    ]
    labeled_image = np.vstack(predictions)

    print(z_slice_num)
    if axis == "XY":
        cell_mask = labeled_image[:, :, :, 0]
        nuc_mask = labeled_image[:, :, :, 1]
    elif axis == "XZ":
        cell_mask = labeled_image[:, :, :z_slice_num, 0]
        nuc_mask = labeled_image[:, :, :z_slice_num, 1]
    elif axis == "YZ":
        cell_mask = labeled_image[:, :z_slice_num, :, 0]
        nuc_mask = labeled_image[:, :z_slice_num, :, 1]

    imsave(output_dir / f"mask_{axis}.tif", cell_mask)
    imsave(output_dir / f"nuclear_mask_{axis}.tif", nuc_mask)

    print(cell_mask.shape)
    np.save(output_dir / f"mask_{axis}.npy", cell_mask)
    np.save(output_dir / f"nuclear_mask_{axis}.npy", nuc_mask)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("image_dir", type=Path)
    p.add_argument("axis")
    p.add_argument("output_dir", type=Path, default=Path())
    args = p.parse_args()

    main(args.image_dir, args.axis, args.output_dir)
