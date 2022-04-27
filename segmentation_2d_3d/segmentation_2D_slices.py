from os import fspath
from pathlib import Path

from skimage.io import imsave

from .deepcell_wrapper_membrane_new_3D import main as deepcell_main

directions = ["XY", "YZ", "XZ"]


def segmentation(nucleus, cytoplasm, membrane, save_dir: Path):
    imsave(fspath(save_dir / "nucleus.tif"), nucleus)
    imsave(fspath(save_dir / "cytoplasm.tif"), cytoplasm)
    imsave(fspath(save_dir / "membrane.tif"), membrane)

    for direction in directions:
        deepcell_main(save_dir, direction)
