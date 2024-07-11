#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path

import aicsimageio.types
from aicsimageio.writers.ome_tiff_writer import OmeTiffWriter
import ome_utils
import tifffile
import numpy as np

masks_input = ['cell', 'nuclear']
channels_output = ['cell', 'nucleus']

def read_normalize_mask(path: Path) -> np.ndarray:
    mask_data = tifffile.imread(path)

    unique_values = np.unique(mask_data)
    # Is it likely that an entire image will be composed of cells,
    # with no background pixels? No. Should we handle it properly? Yes.
    if 0 not in unique_values:
        np.insert(unique_values, 0, 0)

    print(f'Mask {path}: shape {mask_data.shape}, {len(unique_values)} objects')

    new_mask = np.zeros_like(mask_data, dtype=np.uint32)
    for i, value in enumerate(unique_values):
        new_mask[mask_data == value] = i

    return new_mask

def find_expr_image(input_data_dir: Path) -> Path:
    files = list(ome_utils.find_ome_tiffs(input_data_dir))
    if (count := len(files)) != 1:
        raise ValueError(f'Need 1 OME-TIFF in input directory, found {count}')
    return files[0]

def main(input_data_dir: Path, results_dir: Path):
    expr_image = find_expr_image(input_data_dir)
    with tifffile.TiffFile(expr_image) as tf:
        physical_pixel_sizes = ome_utils.get_converted_physical_size(tf)
    pps = aicsimageio.types.PhysicalPixelSizes(
        **{dim: size.magnitude for dim, size in physical_pixel_sizes.items()})

    mask_data = [
        read_normalize_mask(results_dir / f'3D_{mask}_mask.tif')
        for mask in masks_input
    ]

    multichannel_mask = np.stack(mask_data)
    OmeTiffWriter.save(
        multichannel_mask,
        dim_order='CZYX',
        channel_names=channels_output,
        physical_pixel_sizes=pps,
        uri='3D_mask.ome.tiff',
    )

if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('input_data_dir', type=Path, help='')
    p.add_argument('results_dir', type=Path)
    args = p.parse_args()

    main(args.input_data_dir, args.results_dir)
