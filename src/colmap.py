import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pycolmap

from config import load_calibration
from detect_apriltag import detect_apriltag

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

RECONSTRUCTION_DIR = "sparse"
IMAGE_DIR = "images"
DATABASE = "database.db"
APRIL_TAG_FOLDER = "april_tags"


@dataclass
class ColmapNamespace:
    project_dir: str
    action: str
    init: bool


def colmap_cli() -> None:
    """
    Colmap project utility for the toothpicker finder project
    """
    parser = argparse.ArgumentParser(
        description="Colmap project utility for the toothpicker finder project."
    )

    _ = parser.add_argument(
        "-p",
        "--project-dir",
        type=str,
        default="colmap_project",
        help="Directory where the COLMAP project will be created.",
    )
    _ = parser.add_argument(
        "--init",
        action="store_true",
        help="Initializes a new colmap project",
    )

    # Configure the multi-choice argument
    _ = parser.add_argument(
        "-a",
        "--action",
        choices=["MapImages", "InsertApril"],
        help="Action to do on the colmap project",
    )

    args = parser.parse_args()
    args = cast(ColmapNamespace, cast(object, args))

    if args.init:
        _ = initialize_colmap_project(Path(args.project_dir))
        print(
            f"Finished initializing, you can now place your images in {args.project_dir}/images"
        )
        return

    if not Path(args.project_dir).exists():
        raise ValueError("Please initialize a project with 'tf-colmap --init'")

    project_dir = Path(args.project_dir)

    if args.action == "MapImages":
        run_incremental_mapping(Path(args.project_dir))
        return
    elif args.action == "InsertApril":
        insert_april_tag_in_db(project_dir)
        return

    parser.print_help()


def initialize_colmap_project(
    project_dir: Path,
) -> tuple[Path, Path]:
    """
    Initialize a COLMAP project directory.

    Returns
    -------
    project_dir : Path
        Path to the project directory.
    database_path : Path
        Path where the COLMAP database should be created.
    """
    sparse_dir = project_dir / RECONSTRUCTION_DIR
    image_path = project_dir / IMAGE_DIR
    database_path = project_dir / DATABASE

    # Create directory structure
    project_dir.mkdir(parents=True)
    sparse_dir.mkdir()
    image_path.mkdir()

    project_file = Path(project_dir) / "project.ini"
    _ = project_file.write_text(
        f"""
database_path={database_path.resolve()}
image_path={Path(image_path).resolve()}
""",
        encoding="utf-8",
    )

    return project_dir, database_path


def run_incremental_mapping(project_dir: Path):
    sparse_dir = project_dir / RECONSTRUCTION_DIR
    image_path = project_dir / IMAGE_DIR
    database_path = project_dir / DATABASE

    if image_path.is_dir() and not any(image_path.iterdir()):
        raise FileNotFoundError("No images were found in the image directory")

    pycolmap.extract_features(
        database_path=str(database_path),
        image_path=str(image_path),
    )

    pycolmap.match_exhaustive(
        database_path=str(database_path),
    )

    _ = pycolmap.incremental_mapping(
        database_path=str(database_path),
        image_path=str(image_path),
        output_path=str(sparse_dir),
    )


def insert_april_tag_in_db(project_folder: Path):

    if not (project_folder / APRIL_TAG_FOLDER).exists():
        logger.info("Extracted data not fond, extracting apriltags from images.")
        (project_folder / APRIL_TAG_FOLDER).mkdir()
        for image in list((project_folder / IMAGE_DIR).glob("*.jpg")) + list(
            (project_folder / IMAGE_DIR).glob("*.jpeg")
        ):
            _ = detect_apriltag(
                image,
                project_folder / APRIL_TAG_FOLDER,
                False,
                load_calibration(project_folder / IMAGE_DIR, True),
            )

    logger.info("Loading april tag.")
    data = {}
    for json_file in (project_folder / "april_tags").glob("*.json"):
        with json_file.open("r", encoding="utf-8") as f:
            data[json_file.stem] = json.load(f)["april_tags"]
