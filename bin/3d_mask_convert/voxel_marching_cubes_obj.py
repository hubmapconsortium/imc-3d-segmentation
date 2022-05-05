#!/usr/bin/env python3
import re
from argparse import ArgumentParser
from itertools import repeat
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable, Tuple

import aicsimageio
import numpy as np
from skimage.measure import marching_cubes

# TODO: deduplicate

# no path glob or fnmatch because we need the last 'f' to be optional
OME_TIFF_PATTERN = re.compile(r".*\.ome\.tiff?")


def find_ome_tiffs(directory: Path) -> Iterable[Path]:
    for path in directory.glob("**/*"):
        if path.is_file() and OME_TIFF_PATTERN.match(path.name):
            yield path


def cubes(data: Tuple[np.ndarray, int]):
    mask_data, cell = data
    coords, faces, *_ = marching_cubes(mask_data == cell)
    return coords, faces, cell


def convert(mask_file: Path, output_file: Path, processes: int):
    image = aicsimageio.AICSImage(mask_file)
    # TODO: handle multiple channels
    mask_data = np.squeeze(image.data, (0, 1, 2)).astype(int)
    cells = set(mask_data.flat) - {0}

    with open(output_file, "w") as f:
        print("o Segmentation_Mask", file=f)
        # The next vertex written to the output file will have index
        # `vertex_count`, so add this to every vertex index in `faces`.
        # Start at 1 because the OBJ format is 1-indexed
        vertex_count = 1
        cell = 0
        with Pool(processes=processes) as pool:
            for coords, faces, cell in pool.imap(
                cubes,
                zip(repeat(mask_data), cells),
                chunksize=256,
            ):
                print(f"g cell_{cell}", file=f)
                coords, faces, *_ = marching_cubes(mask_data == cell)
                for vertex in coords:
                    print("v " + " ".join(str(x) for x in vertex), file=f)
                for face in faces:
                    print("f " + " ".join(str(x + vertex_count) for x in face), file=f)
                vertex_count += coords.shape[0]
        print(f"Wrote cubes for {cell} cell(s)")


def main(input_dir: Path, output_dir: Path, processes: int):
    for mask_ome_tiff in find_ome_tiffs(input_dir):
        relative_ome_tiff = mask_ome_tiff.relative_to(input_dir)
        relative_mesh = relative_ome_tiff.with_suffix(".obj")
        mesh = output_dir / relative_mesh
        mesh.parent.mkdir(exist_ok=True, parents=True)

        convert(mask_ome_tiff, mesh, processes)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("input_directory", type=Path)
    p.add_argument("output_dir", type=Path, nargs="?", default=Path("mask"))
    p.add_argument("-p", "--processes", type=int, default=1)
    args = p.parse_args()

    main(args.input_directory, args.output_dir, args.processes)
