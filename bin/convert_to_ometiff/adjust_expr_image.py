#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
from shutil import copy

import tifffile

from utils import find_expr_image, output_path


def add_sa_segmentation_channels_info(omexml: ET.Element, channel_metadata: dict[str, list[str]]):
    """
    Will add this, to the root, after Image node
    <StructuredAnnotations>
    <XMLAnnotation ID="Annotation:0">
        <Value>
            <OriginalMetadata>
                <Key>SegmentationChannels</Key>
                <Value>
                    <Nucleus>DAPI-02</Nucleus>
                    <Cell>CD45</Cell>
                </Value>
            </OriginalMetadata>
        </Value>
    </XMLAnnotation>
    </StructuredAnnotations>
    """
    structured_annotation = ET.Element("StructuredAnnotations")
    # TODO: make sure "Annotation:0" is a good key to use
    annotation = ET.SubElement(structured_annotation, "XMLAnnotation", {"ID": "Annotation:0"})
    annotation_value = ET.SubElement(annotation, "Value")
    original_metadata = ET.SubElement(annotation_value, "OriginalMetadata")
    ET.SubElement(original_metadata, "Key").text = "SegmentationChannels"
    segmentation_channels_value = ET.SubElement(original_metadata, "Value")
    for key, channel_list in channel_metadata.items():
        for channel in channel_list:
            ET.SubElement(segmentation_channels_value, key).text = channel
    omexml.append(structured_annotation)


def strip_namespace(xmlstr: str):
    it = ET.iterparse(BytesIO(xmlstr.encode("utf-8")))
    for _, el in it:
        _, _, el.tag = el.tag.rpartition("}")
    root = it.root
    return root


def main(
    input_data_dir: Path,
    nucleus: list[str],
    cytoplasm: list[str],
    membrane: list[str],
):
    dest = output_path / "expr"
    dest.mkdir(exist_ok=True, parents=True)
    expr_image = find_expr_image(input_data_dir)
    channel_metadata = {"Nucleus": nucleus, "Cytoplasm": cytoplasm, "Cell": membrane}
    with tifffile.TiffFile(expr_image) as TF:
        xml_str = TF.ome_metadata
        ome_xml = strip_namespace(xml_str)
        img_stack = TF.series[0].asarray()
    add_sa_segmentation_channels_info(ome_xml, channel_metadata)
    ome_str = ET.tostring(ome_xml, xml_declaration=True, encoding="utf-8")
    print("Writing expression image to", dest)
    with tifffile.TiffWriter(dest / expr_image.name, bigtiff=True, shaped=False) as TW:
        TW.write(
            img_stack,
            contiguous=True,
            photometric="minisblack",
            description=ome_str,
        )
    copy(expr_image, dest)


def parse_marker_list(arg):
    return arg.split(",")


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("input_data_dir", type=Path)
    p.add_argument("--nucleus", required=True, type=parse_marker_list)
    p.add_argument("--cytoplasm", required=True, type=parse_marker_list)
    p.add_argument("--membrane", required=True, type=parse_marker_list)
    args = p.parse_args()

    main(
        input_data_dir=args.input_data_dir,
        nucleus=args.nucleus,
        cytoplasm=args.cytoplasm,
        membrane=args.membrane,
    )
