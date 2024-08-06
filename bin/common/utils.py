from pathlib import Path

import ome_utils

output_path = Path("pipeline_output")


def find_expr_image(input_data_dir: Path) -> Path:
    files = list(ome_utils.find_ome_tiffs(input_data_dir))
    if (count := len(files)) != 1:
        raise ValueError(f"Need 1 OME-TIFF in input directory, found {count}")
    return files[0]
