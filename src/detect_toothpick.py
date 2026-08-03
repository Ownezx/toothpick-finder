import argparse
import json
import logging
import math
from pathlib import Path

import cv2
import numpy as np
from cv2.typing import MatLike
from numpy.typing import NDArray

from config import load_calibration, DetectConfig
from utils import add_common_arguments, validate_arguments

logger = logging.getLogger(__name__)


OUTPUT_FOLDER = ""
"""Output folder"""
DEBUG = False
"""When active, exports extra images for debugging purposes"""


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
        config = load_calibration(Path(launch_arguments.input).parent, True)
        handle_image(
            launch_arguments.input,
            launch_arguments.export_image,
            launch_arguments.show_images,
            config,
        )
        return

    config = load_calibration(Path(launch_arguments.input), True)
    for image in list(Path(launch_arguments.input).glob("*.jpg")):
        logger.info(f"Handling image {image}.")
        handle_image(
            str(image),
            launch_arguments.export_image,
            launch_arguments.show_images,
            config,
        )


def handle_image(image_path: str, export: bool, show: bool, config: DetectConfig):
    lines = detect_lines(image_path, config)

    image_name = Path(image_path).name
    export_lines_to_json(f"{OUTPUT_FOLDER}/{image_name}.json", lines)

    if not export and not show:
        return

    out_image = generate_result_image(
        image_path,
        lines,
        config,
    )

    if export:
        logger.debug(f"Exporting image to {OUTPUT_FOLDER}/{image_name}")
        assert cv2.imwrite(f"{OUTPUT_FOLDER}/{image_name}", out_image)

    if show:
        show_result(out_image)


def detect_lines(image_path: str, config: DetectConfig):

    # Load the image
    loaded_image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Remove selected hues
    hsv = cv2.cvtColor(loaded_image, cv2.COLOR_BGR2HSV)

    blacklist_mask = cv2.inRange(
        hsv,
        np.array(config.low_HSV_blacklist),
        np.array(config.high_HSV_blacklist),
    )
    blacklist_mask = cv2.bitwise_not(blacklist_mask)
    blacklist_image = cv2.bitwise_and(
        loaded_image, loaded_image, mask=blacklist_mask)

    # Conserve only selected hues
    whitelist_mask = cv2.inRange(
        hsv,
        np.array(config.low_HSV_whitelist),
        np.array(config.high_HSV_whitelist),
    )
    whitelist_image = cv2.bitwise_and(
        loaded_image, loaded_image, mask=whitelist_mask)

    masked_image = cv2.bitwise_and(whitelist_image, blacklist_image)

    # Create a binary image: 0 if below ceil, 1 if >= ceil
    binary_image = np.any(masked_image != 0, axis=2).astype(np.uint8)

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (config.line_width, config.line_width)
    )
    binary_image_erroded = cv2.morphologyEx(
        binary_image, cv2.MORPH_OPEN, kernel)

    if DEBUG:
        image_name = Path(image_path).stem
        logger.debug(f"Exporting image to {OUTPUT_FOLDER}/{image_name}")
        assert cv2.imwrite(
            f"{OUTPUT_FOLDER}/{image_name}_mask1.png", blacklist_image)
        assert cv2.imwrite(
            f"{OUTPUT_FOLDER}/{image_name}_mask2.png", whitelist_image)
        assert cv2.imwrite(
            f"{OUTPUT_FOLDER}/{image_name}_mask3.png", masked_image)
        assert cv2.imwrite(
            f"{OUTPUT_FOLDER}/{image_name}_ceil_errode.png", binary_image_erroded * 255
        )
        assert cv2.imwrite(
            f"{OUTPUT_FOLDER}/{image_name}_original.jpg", loaded_image)

    # Detect lines using Probabilistic Hough Transform
    lines = cv2.HoughLinesP(
        binary_image_erroded,
        rho=config.rho,
        theta=config.theta,
        threshold=config.threshold,
        minLineLength=config.minLineLength,
        maxLineGap=config.maxLineGap,
    )

    if lines is None:
        return []

    def line_angle(line) -> float:
        x1, y1, x2, y2 = line
        return math.atan2(y2 - y1, x2 - x1)

    def point_to_line_distance(point, line):
        px, py = point
        x1, y1, x2, y2 = line

        return abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1) / math.sqrt(
            (y2 - y1) ** 2 + (x2 - x1) ** 2
        )

    def line_length(line):
        return math.sqrt((line[2] - line[0]) ** 2 + (line[3] - line[1]) ** 2)

    # This can be improved both for speed and accuracy. Taking the longest line is a bit silly.
    # Filter lines to get the longest one
    filtered_lines = []
    for i in range(len(lines)):
        line = lines[i][0]

        angle = line_angle(line)

        duplicate = False
        for k in range(len(filtered_lines)):
            other_line = filtered_lines[k]
            other_angle = line_angle(other_line)

            if math.fabs(angle - other_angle) > config.duplicate_line_max_angle:
                continue

            # Check distance between extremities
            distances = [
                point_to_line_distance((line[0], line[1]), other_line),
                point_to_line_distance((line[2], line[3]), other_line),
                point_to_line_distance((other_line[0], other_line[1]), line),
                point_to_line_distance((other_line[2], other_line[3]), line),
            ]

            if max(distances) < config.duplicate_line_max_distance:
                duplicate = True
                if line_length(line) > line_length(other_line):
                    filtered_lines[k] = line
                break

        if not duplicate:
            filtered_lines.append(line)

    return [line.tolist() for line in filtered_lines]


def generate_result_image(input: str | np.ndarray, lines: MatLike, config):
    if type(input) is str:
        loaded_image = cv2.imread(input, cv2.IMREAD_COLOR)
    elif type(input) is NDArray:
        loaded_image = input
    else:
        raise TypeError("Invalid image, needs path or ndarray")

    overlay = loaded_image.copy()
    # Draw detected lines
    if lines is not None:
        for x1, y1, x2, y2 in lines[:]:
            cv2.line(overlay, (x1, y1), (x2, y2), config.overlay_color, 10)
    return cv2.addWeighted(
        overlay,
        config.overlay_alpha,
        loaded_image,
        1 - config.overlay_alpha,
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


def export_lines_to_json(output_path: str, lines):
    out = dict()
    out["lines"] = lines
    with open(output_path, "w") as f:
        json.dump(out, f, indent=2)
