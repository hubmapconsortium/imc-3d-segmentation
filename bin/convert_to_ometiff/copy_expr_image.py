#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
from shutil import copy

from utils import find_expr_image, output_path


def main(input_data_dir: Path):
    dest = output_path / "expr"
    dest.mkdir(exist_ok=True, parents=True)
    expr_image = find_expr_image(input_data_dir)
    print("Copying", expr_image, "to", dest)
    copy(expr_image, dest)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("input_data_dir", type=Path)
    args = p.parse_args()

    main(args.input_data_dir)
