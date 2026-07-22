# type: ignore
import argparse
import logging
import shutil
from pathlib import Path

import cv2
import numpy as np
from cv2.typing import MatLike
from numpy._typing import NDArray

OUTPUT_FOLDER = ""
"""Output folder"""
DEBUG = False
"""When active, exports extra images for debugging purposes"""

DETECT_CONFIG = {
    "line_width": 7,
    "ceil_thresold": 240,
    "rho": 6,
    "theta": np.pi / 180,
    "threshold": 200,
    "minLineLength": 100,
    "maxLineGap": 10,
    "overlay_color": (255, 0, 0),
    "overlay_alpha": 0.7,
    "low_HSV_grass_removal": [35, 40, 40],
    "high_HSV_grass_removal": [90, 255, 255],
    "low_HSV_toothpick": [5, 20, 60],
    "high_HSV_toothpick": [35, 255, 255],
}
"""Default configuration file for toothpick detector"""


def get_arguments():
    parser = argparse.ArgumentParser(
        description="This command line tool allows to detect lines in pictures. It is recommended to use a dataset folder with all the images within the same folder as a file to finetune will be created inside of it."
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
        "-f",
        "--force",
        action="store_true",
        help="If the output folder already exists, deletes it without warning before starting.",
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

    logging.info(f"Staring program with input {launch_arguments.input}")

    global OUTPUT_FOLDER
    OUTPUT_FOLDER = launch_arguments.output

    global DEBUG
    DEBUG = launch_arguments.debug

    input_is_dir = Path(launch_arguments.input).is_dir()

    if launch_arguments.force:
        shutil.rmtree(OUTPUT_FOLDER)
        Path(OUTPUT_FOLDER).mkdir()
    else:
        try:
            Path(OUTPUT_FOLDER).mkdir()
        except FileExistsError:
            raise FileExistsError(
                "Output folder already exists, if you want to delete folder on launch use -f"
            )

    if not input_is_dir:
        handle_image(
            launch_arguments.input,
            launch_arguments.export_image,
            launch_arguments.show_images,
        )
        return

    for image in list(Path(launch_arguments.input).glob("*.jpg")):
        logging.info(f"Handling image {image}.")
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
        logging.debug(f"Exporting image to {OUTPUT_FOLDER}/{image_name}")
        assert cv2.imwrite(f"{OUTPUT_FOLDER}/{image_name}", out_image)

    if show:
        show_result(out_image)


def detect_lines(image_path: str):

    # Load the image
    loaded_image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Remove the green grass that is definitely not a toothpick
    hsv = cv2.cvtColor(loaded_image, cv2.COLOR_BGR2HSV)

    grass_mask = cv2.inRange(
        hsv,
        np.array(DETECT_CONFIG["low_HSV_grass_removal"]),
        np.array(DETECT_CONFIG["high_HSV_grass_removal"]),
    )
    grass_mask = cv2.bitwise_not(grass_mask)
    grass_removed_image = cv2.bitwise_and(loaded_image, loaded_image, mask=grass_mask)

    # toothpick hue selector
    toothpick_mask = cv2.inRange(
        hsv,
        np.array(DETECT_CONFIG["low_HSV_toothpick"]),
        np.array(DETECT_CONFIG["high_HSV_toothpick"]),
    )
    toothpick_image = cv2.bitwise_and(loaded_image, loaded_image, mask=toothpick_mask)

    masked_image = cv2.bitwise_and(toothpick_image, grass_removed_image)

    # Extract the red channel (OpenCV uses BGR order)
    red_channel = masked_image[:, :, 2]

    # Create a binary image: 0 if below ceil, 1 if >= ceil
    binary_red = (red_channel >= DETECT_CONFIG["ceil_thresold"]).astype(np.uint8)

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (DETECT_CONFIG["line_width"], DETECT_CONFIG["line_width"])
    )
    binary_red_erroded = cv2.morphologyEx(binary_red, cv2.MORPH_OPEN, kernel)

    if DEBUG:
        image_name = Path(image_path).stem
        logging.debug(f"Exporting image to {OUTPUT_FOLDER}/{image_name}")
        assert cv2.imwrite(f"{OUTPUT_FOLDER}/{image_name}_ceil.png", binary_red * 255)
        assert cv2.imwrite(
            f"{OUTPUT_FOLDER}/{image_name}_no_grass.png", grass_removed_image
        )
        assert cv2.imwrite(
            f"{OUTPUT_FOLDER}/{image_name}_toothpick.png", toothpick_image
        )
        assert cv2.imwrite(
            f"{OUTPUT_FOLDER}/{image_name}_double_mask.png", masked_image
        )
        assert cv2.imwrite(
            f"{OUTPUT_FOLDER}/{image_name}_ceil_erroded.png", binary_red_erroded * 255
        )
        assert cv2.imwrite(f"{OUTPUT_FOLDER}/{image_name}_original.jpg", loaded_image)

    # Detect lines using Probabilistic Hough Transform
    return cv2.HoughLinesP(
        binary_red_erroded,
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
