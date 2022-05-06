import re
from pathlib import Path
from typing import Iterable, List

import aicsimageio
import aicsimageio.vendor.omexml
import lxml

# no path glob or fnmatch because we need the last 'f' to be optional
OME_TIFF_PATTERN = re.compile(r".*\.ome\.tiff?")


def find_ome_tiffs(directory: Path) -> Iterable[Path]:
    for path in directory.glob("**/*"):
        if path.is_file() and OME_TIFF_PATTERN.match(path.name):
            yield path


# for aicsimageio<4
def get_channel_names(image: aicsimageio.AICSImage) -> List[str]:
    if isinstance(image.metadata, aicsimageio.vendor.omexml.OMEXML):
        # aicsimageio<4 doesn't allow overriding whether to include
        # an encoding declaration or to skip decoding to text from bytes,
        # so re-encode to UTF-8 bytes ourselves
        metadata = image.metadata.to_xml().encode("utf-8")
    elif isinstance(image.metadata, str):
        # shouldn't have an encoding declaration if aicsimageio didn't
        # recognize it as OME-XML
        metadata = image.metadata
    tree = lxml.etree.fromstring(metadata)
    namespaces = tree.nsmap.copy()
    namespaces["OME"] = namespaces[None]
    del namespaces[None]
    channels = tree.xpath("//OME:Pixels/OME:Channel/@Name", namespaces=namespaces)
    return channels
