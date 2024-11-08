#!/usr/bin/env python3
import json
from argparse import ArgumentParser
from pathlib import Path
from shutil import copy
from typing import Iterable

import aicsimageio.types
import numpy as np
import ome_utils
import tifffile
from aicsimageio.writers.ome_tiff_writer import OmeTiffWriter

from utils import find_expr_image, output_path

masks_input = ["cell", "nuclear"]
channels_output = ["cell", "nucleus"]


def read_normalize_masks(paths: Iterable[Path]) -> tuple[np.ndarray, dict[str, int]]:
    masks = [tifffile.imread(path) for path in paths]
    mask_data = np.stack(masks)

    unique_values = np.unique(mask_data)
    # Is it likely that an entire image will be composed of cells,
    # with no background pixels? No. Should we handle it properly? Yes.
    if 0 not in unique_values:
        np.insert(unique_values, 0, 0)

    print(f"Consolidated mask shape: {mask_data.shape}, {len(unique_values)} objects")

    object_id_mapping = {}
    new_mask = np.zeros_like(mask_data, dtype=np.uint32)
    for i, value in enumerate(unique_values):
        new_mask[mask_data == value] = i
        object_id_mapping[f"Cell_{value}"] = i

    return new_mask, object_id_mapping


def main(input_data_dir: Path, results_dir: Path, output_path: Path):
    expr_image = find_expr_image(input_data_dir)
    with tifffile.TiffFile(expr_image) as tf:
        physical_pixel_sizes = ome_utils.get_converted_physical_size(tf)
    pps = aicsimageio.types.PhysicalPixelSizes(
        **{dim: size.magnitude for dim, size in physical_pixel_sizes.items()}
    )

    masks = [results_dir / f"3D_{mask}_mask.tif" for mask in masks_input]
    mask_data, object_id_mapping = read_normalize_masks(masks)

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
    with open("object_id_mapping.json", "w") as f:
        json.dump(object_id_mapping, f)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("input_data_dir", type=Path)
    p.add_argument("results_dir", type=Path)
    p.add_argument("output_path", type=Path, default=output_path, nargs="?")
    args = p.parse_args()

    main(args.input_data_dir, args.results_dir, args.output_path)
