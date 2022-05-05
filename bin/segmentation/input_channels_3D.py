from os import fspath

import tifffile
from skimage.io import imread


def get_channel_names(img_dir):

    with tifffile.TiffFile(img_dir) as tif:
        tif_tags = {}
        for tag in tif.pages[0].tags.values():
            name, value = tag.name, tag.value
            tif_tags[name] = value
    description = tif_tags["ImageDescription"]
    name_list = list()
    for i in range(50):
        channel_num = "Channel:0:" + str(i)
        channel_anchor = description.find(channel_num)
        channel_str = description[channel_anchor : channel_anchor + 80]
        name_anchor = channel_str.find("Name")
        name_str = channel_str[name_anchor + 6 : name_anchor + 20]
        channel_name = name_str[: name_str.find('"')]
        if len(channel_name) > 0:
            name_list.append(channel_name)
    return name_list


def IMC_3D_input_channels(img_dir):
    # find nuclear, cytoplasmic, cell membrane as input for 3D segmentation

    # fspath is (currently) necessary to work around a bug in scikit-image
    #              ↓↓↓↓↓↓
    image = imread(fspath(img_dir))
    channel_names = get_channel_names(img_dir)
    nucleus_channel_idx = channel_names.index("Ir191")  # Iridium
    cytoplasm_channel_idx = channel_names.index("In115")  # SMA
    membrane_channel_idx = channel_names.index("La139")  # E-Cad/P-Cad
    nucleus_channel = image[:, nucleus_channel_idx, :, :]
    cytoplasm_channel = image[:, cytoplasm_channel_idx, :, :]
    membrane_channel = image[:, membrane_channel_idx, :, :]
    return nucleus_channel, cytoplasm_channel, membrane_channel
