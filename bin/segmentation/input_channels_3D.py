from os import fspath
from pathlib import Path

from aicsimageio import AICSImage
from skimage.io import imread

channel_preset_path = Path("/data/channel-presets")


def IMC_3D_input_channels(img_dir):
    # find nuclear, cytoplasmic, cell membrane as input for 3D segmentation

    # fspath is (currently) necessary to work around a bug in scikit-image
    #              ↓↓↓↓↓↓
    image = imread(fspath(img_dir))
    channel_names = AICSImage(img_dir).channel_names
    nucleus_channel_idx = channel_names.index("Ir191")  # Iridium
    cytoplasm_channel_idx = channel_names.index("In115")  # SMA
    membrane_channel_idx = channel_names.index("La139")  # E-Cad/P-Cad
    nucleus_channel = image[:, nucleus_channel_idx, :, :]
    cytoplasm_channel = image[:, cytoplasm_channel_idx, :, :]
    membrane_channel = image[:, membrane_channel_idx, :, :]
    return nucleus_channel, cytoplasm_channel, membrane_channel
