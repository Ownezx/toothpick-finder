import argparse
import logging

from utils import add_common_arguments, validate_arguments

logger = logging.getLogger(__name__)


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
