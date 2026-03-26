#!/usr/bin/env python3
import json
from argparse import ArgumentParser
from pathlib import Path
from shutil import copy
from typing import Iterable

import bioio
import numpy as np
import ome_utils
import tifffile
from bioio.writers import OmeTiffWriter

from utils import find_expr_image, output_path

masks_input = ["cell_mask", "nuclear_mask", "cell_boundaries", "nuclear_boundaries"]
channels_output = ["cells", "nuclei", "cell_boundaries", "nucleus_boundaries"]


def read_normalize_masks(paths: Iterable[Path]) -> np.ndarray:
    masks = [tifffile.imread(path) for path in paths]
    mask_data = np.stack(masks)

    return mask_data


def main(input_data_dir: Path, results_dir: Path, output_path: Path):
    expr_image = find_expr_image(input_data_dir)
    with tifffile.TiffFile(expr_image) as tf:
        physical_pixel_sizes = ome_utils.get_converted_physical_size(tf)
    pps = bioio.PhysicalPixelSizes(
        **{dim: size.magnitude for dim, size in physical_pixel_sizes.items()}
    )

    masks = [results_dir / f"3D_{mask}.tif" for mask in masks_input]
    mask_data = read_normalize_masks(masks)

    multichannel_mask = np.stack(mask_data)
    (mask_dir := output_path / "mask").mkdir(exist_ok=True, parents=True)
    OmeTiffWriter.save(
        multichannel_mask,
        dim_order="CZYX",
        channel_names=channels_output,
        physical_pixel_sizes=pps,
        uri=mask_dir / "3D_mask.ome.tiff",
    )

    copy(results_dir / "metrics.json", output_path)
    copy(results_dir / "quality_score.txt", output_path)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("input_data_dir", type=Path)
    p.add_argument("results_dir", type=Path)
    p.add_argument("output_path", type=Path, default=output_path, nargs="?")
    args = p.parse_args()

    main(args.input_data_dir, args.results_dir, args.output_path)
