import argparse
import json
import logging
from pathlib import Path
from tomllib import load

import apriltag
import cv2
import numpy as np

from config import DetectConfig, load_calibration
from utils import CommonNamespace, add_common_arguments, validate_arguments

logger = logging.getLogger(__name__)

# Setup april tag detector
detector = apriltag.apriltag("tagStandard41h12", threads=4)


def apriltag_cli():
    parser = argparse.ArgumentParser(
        description="This command line tool allows to detect lines in pictures. It is recommended to use a dataset folder with all the images within the same folder as a file to finetune will be created inside of it."
    )
    add_common_arguments(
        parser,
        default_output="tfd_apriltag_output",
        object_name="AprilTag",
    )
    launch_arguments = parser.parse_args(namespace=CommonNamespace)
    validate_arguments(launch_arguments())

    logger.info(f"Staring program with input {launch_arguments.input}")

    input_is_dir = Path(launch_arguments.input).is_dir()
    if not input_is_dir:
        config = load_calibration(Path(launch_arguments.input).parent, True)
        detection = handle_image(
            launch_arguments.input,
            launch_arguments.output,
            launch_arguments.export_image,
            config,
        )
        logger.debug(f"Detections : {detection}")
        return

    config = load_calibration(Path(launch_arguments.input), True)
    for image in list(Path(launch_arguments.input).glob("*.jpg")) + list(
        Path(launch_arguments.input).glob("*.jpeg")
    ):
        logger.info(f"Handling image {image}.")
        _ = handle_image(
            str(image),
            launch_arguments.output,
            launch_arguments.export_image,
            config,
        )


def handle_image(
    image_path: str, output_folder: str, export: bool, config: DetectConfig
):
    loaded_image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    assert loaded_image is not None

    # todo pre process the image to have the most contrast for the april tag
    detections = detector.detect(loaded_image)  # type: ignore
    image_name = Path(image_path).name
    export_april_tag_to_json(Path(f"{output_folder}/{image_name}.json"), detections)

    if export:
        out_image = generate_result_image(image_path, detections, config)
        logger.debug(f"Exporting image to {output_folder}/{image_name}")
        assert cv2.imwrite(f"{output_folder}/{image_name}", out_image)

    return detections


def generate_result_image(input: str | np.ndarray, detections, config: DetectConfig):
    if type(input) is str:
        loaded_image = cv2.imread(input, cv2.IMREAD_COLOR)
        assert loaded_image is not None
    elif type(input) is np.ndarray:
        loaded_image = input
    else:
        raise TypeError(f"Invalid image, needs path or ndarray, got {type(input)}")

    overlay = loaded_image.copy()

    for detection in detections:
        corners = np.squeeze(detection["lb-rb-rt-lt"])
        for point in corners:
            x, y = int(point[0]), int(point[1])
            cv2.circle(
                overlay, (x, y), radius=10, color=config.overlay_color, thickness=-1
            )

    return overlay


def export_april_tag_to_json(output_path: Path, detections):
    detection_list = []
    for detection in detections:
        detection_list.append(
            [detection["id"], np.squeeze(detection["lb-rb-rt-lt"]).tolist()]
        )
    out_dict = {}
    out_dict["april_tags"] = detection_list

    with open(output_path, "w") as f:
        json.dump(out_dict, f, indent=2)
