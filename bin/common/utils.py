import re
from pathlib import Path
from typing import Iterable

# no path glob or fnmatch because we need the last 'f' to be optional
OME_TIFF_PATTERN = re.compile(r".*\.ome\.tiff?")


def find_ome_tiffs(directory: Path) -> Iterable[Path]:
    for path in directory.glob("**/*"):
        if path.is_file() and OME_TIFF_PATTERN.match(path.name):
            yield path
