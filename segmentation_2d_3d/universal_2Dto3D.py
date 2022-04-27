import argparse
import os
from os.path import join

import numpy as np

from input_channels_3D import IMC_3D_input_channels
from match_2D_stacks import match_stacks
from match_3D_cells import match_3D_cells
from segmentation_2D_slices import segmentation


def universal_2Dto3D(input_dir, output_dir):
    # get input channels from IMC
    print("Generating segmentation input channels..")
    nucleus, cytoplasm, membrane = IMC_3D_input_channels(input_dir)

    # segmentation for each slice on XY, YZ, XZ axes
    print("Segmenting all slices on XY, YZ, and XY axes..")
    segmentation(nucleus, cytoplasm, membrane, os.path.dirname(input_dir))

    # 3D reconstruction for each axis
    print("Matching 2D segmentation of all slices on each of axes..")
    mask_matched_XY, mask_matched_XZ, mask_matched_YZ = match_stacks(os.path.dirname(input_dir))

    # 3D reconstruction between all axes
    print("Reconstructing 3D segmentation..")
    mask_3D = match_3D_cells(
        mask_matched_XY, mask_matched_XZ, mask_matched_YZ, os.path.dirname(input_dir), output_dir
    )

    return mask_3D


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal 2D to 3D segmentation")
    parser.add_argument("img_dir")
    parser.add_argument("mask_dir")
    args = parser.parse_args()
    four_channel_3D_mask = universal_2Dto3D(args.img_dir, args.mask_dir)
