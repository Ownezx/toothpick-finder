# type: ignore
import argparse
import logging
from pathlib import Path

import cv2
import numpy as np
from cv2.typing import MatLike
from numpy._typing import NDArray

WORK_FOLDER = ""


def get_arguments():
    parser = argparse.ArgumentParser(
        description="This command line tool allows to detect toothpics in pictures."
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to the input folder or image. It will only take .jpg",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="tf_detect_output",
        help="Output file (default: %(default)s)",
    )

    parser.add_argument(
        "-e",
        "--export-image",
        action="store_true",
        help="Exports images with the detected toothpick in the ouput (otherwise just saves the segment data)",
    )

    parser.add_argument(
        "-s",
        "--show-images",
        action="store_true",
        help="Shows the images as they are generated",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Debug exports additional intermediate images",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Shows additional log information",
    )

    return parser.parse_args()


def main_cli():
    launch_arguments = get_arguments()
    if launch_arguments.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    global WORK_FOLDER
    logging.info(f"Staring program with input {launch_arguments.input}")
    WORK_FOLDER = launch_arguments.output

    if Path(launch_arguments.input).is_dir():
        raise argparse.ArgumentError("Folder are not currently supported.")

    Path(WORK_FOLDER).mkdir(exist_ok=True)

    lines = detect_lines(launch_arguments.input)

    out_image = generate_result_image(launch_arguments.input, lines)

    if launch_arguments.export_image:
        image_name = Path(launch_arguments.input).name
        logging.debug(f"Exporting image to {WORK_FOLDER}/{image_name}")
        assert cv2.imwrite(f"{WORK_FOLDER}/{image_name}", out_image)

    if launch_arguments.show_images:
        show_result(out_image)


def detect_lines(image_path: str):

    # Load the image
    loaded_image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Extract the red channel (OpenCV uses BGR order)
    red_channel = loaded_image[:, :, 2]

    # Define a threshold (ceil) value
    ceil_value = 230  # you can change this

    # Create a binary image: 0 if below ceil, 1 if >= ceil
    binary_red = (red_channel >= ceil_value).astype(np.uint8)

    # Detect lines using Probabilistic Hough Transform
    return cv2.HoughLinesP(
        binary_red,
        rho=6,
        theta=np.pi / 180,
        threshold=50,  # minimum number of intersections to detect a line
        minLineLength=180,  # minimum line length to accept
        maxLineGap=15,  # maximum gap between line segments
    )


def generate_result_image(input: str | np.ndarray, lines: MatLike):
    if type(input) is str:
        loaded_image = cv2.imread(input, cv2.IMREAD_COLOR)
    elif type(input) is NDArray:
        loaded_image = input
    else:
        raise TypeError("Invalid image, needs path or ndarray")

    # Draw detected lines
    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            cv2.line(loaded_image, (x1, y1), (x2, y2), (0, 0, 255), 10)
    return loaded_image


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
