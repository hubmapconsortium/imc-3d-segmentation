#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
from shutil import copy

from utils import find_ome_tiffs

base_path = Path("expr")


def copy_images(input_dir: Path):
    for ome_tiff in find_ome_tiffs(input_dir):
        dest_path = base_path / ome_tiff.relative_to(input_dir)
        dest_path.parent.mkdir(exist_ok=True, parents=True)
        print("Copying", ome_tiff, "to", dest_path)
        copy(ome_tiff, dest_path)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("input_dir", type=Path)
    args = p.parse_args()

    copy_images(args.input_dir)
