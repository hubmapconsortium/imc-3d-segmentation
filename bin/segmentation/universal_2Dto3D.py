#!/usr/bin/env python3
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from input_channels_3D import IMC_3D_input_channels
from match_2D_stacks import match_stacks
from match_3D_cells import match_3D_cells
from segmentation_2D_slices import segmentation
from utils import find_ome_tiffs


def universal_2Dto3D(img_file: Path, output_file: Path):
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # get input channels from IMC
        print("Generating segmentation input channels..")
        nucleus, cytoplasm, membrane = IMC_3D_input_channels(img_file)

        # segmentation for each slice on XY, YZ, XZ axes
        print("Segmenting all slices on XY, YZ, and XY axes..")
        segmentation(nucleus, cytoplasm, membrane, tmp_path)

        # 3D reconstruction for each axis
        print("Matching 2D segmentation of all slices on each of axes..")
        mask_matched_XY, mask_matched_XZ, mask_matched_YZ = match_stacks(tmp_path)

        # 3D reconstruction between all axes
        print("Reconstructing 3D segmentation..")
        mask_3D = match_3D_cells(
            mask_matched_XY,
            mask_matched_XZ,
            mask_matched_YZ,
            tmp_path,
            output_file,
        )

    return mask_3D


def main(input_dir: Path, output_dir: Path):
    for ome_tiff in find_ome_tiffs(input_dir):
        relative_ome_tiff = ome_tiff.relative_to(input_dir)
        mask = output_dir / relative_ome_tiff
        mask.parent.mkdir(exist_ok=True, parents=True)

        universal_2Dto3D(ome_tiff, mask)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal 2D to 3D segmentation")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path, nargs="?", default=Path("mask"))
    args = parser.parse_args()

    main(args.input_dir, args.output_dir)
