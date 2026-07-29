import argparse
import logging
from pathlib import Path

import apriltag
import cv2
import numpy as np
from cv2.typing import MatLike
from numpy.typing import NDArray

from utils import add_common_arguments, validate_arguments

OUTPUT_FOLDER = ""
"""Output folder"""

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
    launch_arguments = parser.parse_args()
    validate_arguments(launch_arguments)

    global OUTPUT_FOLDER
    OUTPUT_FOLDER = launch_arguments.output

    logger.info(f"Staring program with input {launch_arguments.input}")

    input_is_dir = Path(launch_arguments.input).is_dir()
    if not input_is_dir:
        detection = handle_image(
            launch_arguments.input,
            launch_arguments.export_image,
        )
        logger.debug(f"Detections : {detection}")
        return

    for image in list(Path(launch_arguments.input).glob("*.jpg")):
        logger.info(f"Handling image {image}.")
        handle_image(
            str(image),
            launch_arguments.export_image,
        )


def handle_image(image_path: str, export: bool):
    loaded_image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    # todo pre process the image to have the most contrast for the april tag
    detections = detector.detect(loaded_image)  # type: ignore

    if export:
        out_image = generate_result_image(image_path, detections)
        image_name = Path(image_path).name
        logger.debug(f"Exporting image to {OUTPUT_FOLDER}/{image_name}")
        assert cv2.imwrite(f"{OUTPUT_FOLDER}/{image_name}", out_image)

    return detections


def generate_result_image(input: str | np.ndarray, detections):
    if type(input) is str:
        loaded_image = cv2.imread(input, cv2.IMREAD_COLOR)
    elif type(input) is np.ndarray:
        loaded_image = input
    else:
        raise TypeError(f"Invalid image, needs path or ndarray, got {type(input)}")

    overlay = loaded_image.copy()

    for detection in detections:
        corners = np.squeeze(detection["lb-rb-rt-lt"])
        for point in corners:
            x, y = int(point[0]), int(point[1])
            cv2.circle(overlay, (x, y), radius=10, color=(0, 0, 255), thickness=-1)

    return overlay
