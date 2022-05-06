import re
from pathlib import Path
from typing import Iterable, List

import lxml

# no path glob or fnmatch because we need the last 'f' to be optional
OME_TIFF_PATTERN = re.compile(r".*\.ome\.tiff?")


def find_ome_tiffs(directory: Path) -> Iterable[Path]:
    for path in directory.glob("**/*"):
        if path.is_file() and OME_TIFF_PATTERN.match(path.name):
            yield path


# for aicsimageio<4
def get_channel_names(metadata_xml: str) -> List[str]:
    tree = lxml.etree.fromstring(metadata_xml)
    namespaces = tree.nsmap.copy()
    namespaces["OME"] = namespaces[None]
    del namespaces[None]
    channels = tree.xpath("//OME:Pixels/OME:Channel/@Name", namespaces=namespaces)
    return channels
