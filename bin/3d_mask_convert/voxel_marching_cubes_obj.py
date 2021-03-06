#!/usr/bin/env python3
import logging
from argparse import ArgumentParser
from itertools import repeat
from multiprocessing import Pool
from pathlib import Path
from typing import Tuple

import aicsimageio
import manhole
import numpy as np
from skimage.measure import marching_cubes

from utils import find_ome_tiffs

dims_to_drop = frozenset("ST")


def cubes(data: Tuple[np.ndarray, int]):
    mask_data, cell = data
    coords, faces, *_ = marching_cubes(mask_data == cell)
    return coords, faces, cell


def convert(mask_file: Path, output_dir: Path, processes: int):
    image = aicsimageio.AICSImage(mask_file)
    logging.info("Mask dimensions: %s", image.shape)
    channel_names = image.channel_names
    logging.info("Mask channels: %s", channel_names)
    squeeze_sel = tuple(i for i, dim in enumerate(image.dims.order) if dim in dims_to_drop)
    mask_data = np.squeeze(image.data, squeeze_sel).astype(int)

    for channel, mask in zip(channel_names, mask_data):
        logging.info("Converting channel '%s', mask shape %s", channel, mask.shape)
        cells = set(mask.flat) - {0}
        logging.info("Cell count: %d", len(cells))
        output_file = output_dir / f"{channel}.obj"
        with open(output_file, "w") as f:
            print("o Segmentation_Mask", file=f)
            # The next vertex written to the output file will have index
            # `vertex_count`, so add this to every vertex index in `faces`.
            # Start at 1 because the OBJ format is 1-indexed
            vertex_count = 1
            mask_id = 0
            with Pool(processes=processes) as pool:
                for coords, faces, mask_id in pool.imap(
                    cubes,
                    zip(repeat(mask), cells),
                    chunksize=256,
                ):
                    print(f"g {channel}_{mask_id}", file=f)
                    for vertex in coords:
                        print("v " + " ".join(str(x) for x in vertex), file=f)
                    for face in faces:
                        print("f " + " ".join(str(x + vertex_count) for x in face), file=f)
                    vertex_count += coords.shape[0]
            logging.info("Wrote cubes for %d shape(s)", mask_id)


def main(input_dir: Path, output_dir_base: Path, processes: int):
    for mask_ome_tiff in find_ome_tiffs(input_dir):
        relative_ome_tiff = mask_ome_tiff.relative_to(input_dir)
        output_dir = output_dir_base / relative_ome_tiff
        output_dir.mkdir(exist_ok=True, parents=True)

        convert(mask_ome_tiff, output_dir, processes)


if __name__ == "__main__":
    manhole.install(activate_on="USR1")

    p = ArgumentParser()
    p.add_argument("input_directory", type=Path)
    p.add_argument("output_dir", type=Path, nargs="?", default=Path("mesh"))
    p.add_argument("-p", "--processes", type=int, default=1)
    args = p.parse_args()

    logging.basicConfig(
        format="{asctime:<15} {levelname:<7} | {message}",
        style="{",
        level=logging.INFO,
    )

    main(args.input_directory, args.output_dir, args.processes)
