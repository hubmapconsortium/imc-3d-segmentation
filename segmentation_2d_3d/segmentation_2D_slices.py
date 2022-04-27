from pathlib import Path
from tempfile import TemporaryDirectory

from skimage.io import imsave

from .deepcell_wrapper_membrane_new_3D import main as deepcell_main

directions = ["XY", "YZ", "XZ"]


def segmentation(nucleus, cytoplasm, membrane, save_dir: Path):
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        imsave(tmp_path / "nucleus.tif", nucleus)
        imsave(tmp_path / "cytoplasm.tif", cytoplasm)
        imsave(tmp_path / "membrane.tif", membrane)

        for direction in directions:
            deepcell_main(tmp_path, direction, save_dir)
