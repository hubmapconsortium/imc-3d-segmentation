import json
from os import fspath
from pathlib import Path
from typing import Dict

from aicsimageio import AICSImage
from skimage.io import imread

channel_preset_path = Path("/data/channel-presets")


def get_imc_3d_channel_selection() -> Dict[str, str]:
    # The return type of this should be
    #   Dict[typing.Literal["nucleus", "cytoplasm", "membrane"], str]
    # but the segmentations image currently uses Python 3.7 and
    # typing.Literal was added in 3.8

    # temporarily hardcoded         ↓↓↓↓↓↓↓↓↓↓↓↓↓
    with open(channel_preset_path / "imc-3d.json") as f:
        channel_data = json.load(f)
    # drop comments
    return {channel_type: data["name"] for channel_type, data in channel_data.items()}


def IMC_3D_input_channels(img_dir):
    # find nuclear, cytoplasmic, cell membrane as input for 3D segmentation
    channels = get_imc_3d_channel_selection()

    # fspath is (currently) necessary to work around a bug in scikit-image
    #              ↓↓↓↓↓↓
    image = imread(fspath(img_dir))
    channel_names = AICSImage(img_dir).channel_names
    nucleus_channel_idx = channel_names.index(channels["nucleus"])
    cytoplasm_channel_idx = channel_names.index(channels["cytoplasm"])
    membrane_channel_idx = channel_names.index(channels["membrane"])
    nucleus_channel = image[:, nucleus_channel_idx, :, :]
    cytoplasm_channel = image[:, cytoplasm_channel_idx, :, :]
    membrane_channel = image[:, membrane_channel_idx, :, :]
    return nucleus_channel, cytoplasm_channel, membrane_channel
