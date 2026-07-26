import argparse
import logging
import shutil
from pathlib import Path


def add_common_arguments(
    parser: argparse.ArgumentParser,
    *,
    default_output: str,
    object_name: str,
):
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to the input folder or image.",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=default_output,
        help="Output file (default: %(default)s)",
    )

    parser.add_argument(
        "-e",
        "--export-image",
        action="store_true",
        help=f"Exports images with the detected {object_name}.",
    )

    parser.add_argument(
        "-s",
        "--show-images",
        action="store_true",
        help="Shows the images as they are generated.",
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing output without prompting.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show additional log information.",
    )


def validate_arguments(launch_arguments: argparse.Namespace):
    if launch_arguments.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if not Path(launch_arguments.output).exists():
        Path(launch_arguments.output).mkdir()
        return

    if launch_arguments.force:
        shutil.rmtree(launch_arguments.output)
        Path(launch_arguments.output).mkdir()
    else:
        try:
            Path(launch_arguments.output).mkdir()
        except FileExistsError:
            raise FileExistsError(
                "Output folder already exists, if you want to delete folder on launch use -f"
            )
