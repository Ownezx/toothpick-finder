# type: ignore
import argparse
import json
import logging
from pathlib import Path

import cv2
import numpy as np
from cv2.typing import MatLike
from numpy._typing import NDArray

from utils import add_common_arguments, validate_arguments

logger = logging.getLogger(__name__)


OUTPUT_FOLDER = ""
"""Output folder"""
DEBUG = False
"""When active, exports extra images for debugging purposes"""

DETECT_CONFIG = {
    "line_width": 7,
    "rho": 6,
    "theta": np.pi / 180,
    "threshold": 200,
    "minLineLength": 100,
    "maxLineGap": 10,
    "overlay_color": (255, 0, 255),
    "overlay_alpha": 1,
    "low_HSV_blacklist": [35, 40, 40],
    "high_HSV_blacklist": [90, 255, 255],
    "low_HSV_whitelist": [100, 140, 60],
    "high_HSV_whitelist": [150, 255, 255],
}
"""Default configuration file for toothpick detector"""


def toothpick_cli():
    parser = argparse.ArgumentParser(
        description="This command line tool allows to detect lines in pictures. It is recommended to use a dataset folder with all the images within the same folder as a file to finetune will be created inside of it."
    )
    add_common_arguments(
        parser,
        default_output="tfd_toothpick_output",
        object_name="toothpick",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Export additional intermediate images.",
    )
    launch_arguments = parser.parse_args()
    validate_arguments(launch_arguments)

    global OUTPUT_FOLDER
    OUTPUT_FOLDER = launch_arguments.output

    global DEBUG
    DEBUG = launch_arguments.debug

    logger.info(f"Staring program with input {launch_arguments.input}")

    input_is_dir = Path(launch_arguments.input).is_dir()
    if not input_is_dir:
        load_calibration(launch_arguments.input, True)
        handle_image(
            launch_arguments.input,
            launch_arguments.export_image,
            launch_arguments.show_images,
        )
        return

    load_calibration(launch_arguments.input, True)
    for image in list(Path(launch_arguments.input).glob("*.jpg")):
        logger.info(f"Handling image {image}.")
        handle_image(
            str(image),
            launch_arguments.export_image,
            launch_arguments.show_images,
        )


def handle_image(image_path: str, export: bool, show: bool):
    lines = detect_lines(image_path)

    out_image = generate_result_image(image_path, lines)

    if export:
        image_name = Path(image_path).name
        logger.debug(f"Exporting image to {OUTPUT_FOLDER}/{image_name}")
        assert cv2.imwrite(f"{OUTPUT_FOLDER}/{image_name}", out_image)

    if show:
        show_result(out_image)


def detect_lines(image_path: str):

    # Load the image
    loaded_image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Remove selected hues
    hsv = cv2.cvtColor(loaded_image, cv2.COLOR_BGR2HSV)

    blacklist_mask = cv2.inRange(
        hsv,
        np.array(DETECT_CONFIG["low_HSV_blacklist"]),
        np.array(DETECT_CONFIG["high_HSV_blacklist"]),
    )
    blacklist_mask = cv2.bitwise_not(blacklist_mask)
    blacklist_image = cv2.bitwise_and(loaded_image, loaded_image, mask=blacklist_mask)

    # Conserve only selected hues
    whitelist_mask = cv2.inRange(
        hsv,
        np.array(DETECT_CONFIG["low_HSV_whitelist"]),
        np.array(DETECT_CONFIG["high_HSV_whitelist"]),
    )
    whitelist_image = cv2.bitwise_and(loaded_image, loaded_image, mask=whitelist_mask)

    masked_image = cv2.bitwise_and(whitelist_image, blacklist_image)

    # Create a binary image: 0 if below ceil, 1 if >= ceil
    binary_image = np.any(masked_image != 0, axis=2).astype(np.uint8)

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (DETECT_CONFIG["line_width"], DETECT_CONFIG["line_width"])
    )
    binary_image_erroded = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)

    if DEBUG:
        image_name = Path(image_path).stem
        logger.debug(f"Exporting image to {OUTPUT_FOLDER}/{image_name}")
        assert cv2.imwrite(f"{OUTPUT_FOLDER}/{image_name}_mask1.png", blacklist_image)
        assert cv2.imwrite(f"{OUTPUT_FOLDER}/{image_name}_mask2.png", whitelist_image)
        assert cv2.imwrite(f"{OUTPUT_FOLDER}/{image_name}_mask3.png", masked_image)
        assert cv2.imwrite(
            f"{OUTPUT_FOLDER}/{image_name}_ceil_errode.png", binary_image_erroded * 255
        )
        assert cv2.imwrite(f"{OUTPUT_FOLDER}/{image_name}_original.jpg", loaded_image)

    # Detect lines using Probabilistic Hough Transform
    return cv2.HoughLinesP(
        binary_image_erroded,
        rho=DETECT_CONFIG["rho"],
        theta=DETECT_CONFIG["theta"],
        threshold=DETECT_CONFIG["threshold"],
        minLineLength=DETECT_CONFIG["minLineLength"],
        maxLineGap=DETECT_CONFIG["maxLineGap"],
    )


def generate_result_image(input: str | np.ndarray, lines: MatLike):
    if type(input) is str:
        loaded_image = cv2.imread(input, cv2.IMREAD_COLOR)
    elif type(input) is NDArray:
        loaded_image = input
    else:
        raise TypeError("Invalid image, needs path or ndarray")

    overlay = loaded_image.copy()
    # Draw detected lines
    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            cv2.line(overlay, (x1, y1), (x2, y2), DETECT_CONFIG["overlay_color"], 10)
    return cv2.addWeighted(
        overlay,
        DETECT_CONFIG["overlay_alpha"],
        loaded_image,
        1 - DETECT_CONFIG["overlay_alpha"],
        0,
    )


def show_result(input: str | np.ndarray):
    if type(input) is str:
        loaded_image = cv2.imread(input, cv2.IMREAD_COLOR)
    elif type(input) is np.ndarray:
        loaded_image = input
    else:
        raise TypeError("Invalid image, needs path or ndarray")

    cv2.imshow("Detected Toothpicks", loaded_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def load_calibration(workspace_path: str, write_default_if_empty: bool):

    try:
        # Open and load the JSON file
        with open(f"{workspace_path}/calibration.json", "r", encoding="utf-8") as file:
            read_config = json.load(file)
            global DETECT_CONFIG
            is_valid = read_config.keys() == DETECT_CONFIG.keys()
            if is_valid:
                DETECT_CONFIG = read_config
            else:
                raise ValueError(
                    "Invalid configuration file, please review or delete configuration file."
                )
    except FileNotFoundError:
        if not write_default_if_empty:
            raise FileNotFoundError("Calibration Json not found in dataset.")
        with open(f"{workspace_path}/calibration.json", "w", encoding="utf-8") as file:
            json.dump(DETECT_CONFIG, file, indent=4)
            logger.info(
                f"Writing new calibration file in dataset folder {workspace_path}."
            )
