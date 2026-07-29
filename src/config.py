import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


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


def load_calibration(
    workspace_path: Path, write_default_if_empty: bool
) -> dict[str, Any]:

    try:
        # Open and load the JSON file
        with open(f"{workspace_path}/calibration.json", "r", encoding="utf-8") as file:
            read_config = json.load(file)
            is_valid = read_config.keys() == DETECT_CONFIG.keys()
            if is_valid:
                return read_config
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
            return DETECT_CONFIG
