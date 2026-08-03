"""Configuration loading for the toothpick detector."""

from __future__ import annotations

import copy
import json
import logging
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

CALIBRATION_FILENAME = "calibration.json"


@dataclass(slots=True)
class DetectConfig:
    """Configuration parameters for toothpick detection."""

    # Hough transform
    line_width: int = 7
    rho: int = 6
    theta: float = np.pi / 180
    threshold: int = 200
    minLineLength: int = 100
    maxLineGap: int = 10

    # Visualisation
    overlay_color: tuple[int, int, int] = (255, 0, 255)
    overlay_alpha: float = 1.0

    # HSV masks
    low_HSV_blacklist: tuple[int, int, int] = (35, 40, 40)
    high_HSV_blacklist: tuple[int, int, int] = (90, 255, 255)

    low_HSV_whitelist: tuple[int, int, int] = (100, 140, 60)
    high_HSV_whitelist: tuple[int, int, int] = (150, 255, 255)

    # Duplicate line suppression
    duplicate_line_max_angle: int = 3
    duplicate_line_max_distance: int = 5


DEFAULT_CONFIG = DetectConfig()


def _validate_and_merge(data: dict[str, Any]) -> DetectConfig:
    """
    Merge a JSON dictionary with defaults and validate keys and types.
    """

    defaults = asdict(DEFAULT_CONFIG)

    unknown = set(data) - set(defaults)
    if unknown:
        raise ValueError(f"Unknown configuration keys: {sorted(unknown)}")

    merged = defaults | data

    validated: dict[str, Any] = {}

    for field in fields(DetectConfig):
        value = merged[field.name]
        expected = field.type

        # Handle tuple fields stored as JSON lists.
        if expected == tuple[int, int, int]:
            if not isinstance(value, (list, tuple)) or len(value) != 3:
                raise TypeError(f"{field.name!r} must contain exactly three integers.")
            value = tuple(int(v) for v in value)

        elif expected == int:
            if not isinstance(value, int):
                raise TypeError(f"{field.name!r} must be an integer.")

        elif expected == float:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{field.name!r} must be a float.")
            value = float(value)

        validated[field.name] = value

    return DetectConfig(**validated)


def load_calibration(
    workspace_path: Path,
    create_if_missing: bool = True,
) -> DetectConfig:
    """
    Load the calibration configuration.

    If the calibration file does not exist and `create_if_missing`
    is True, a new one is written using the default configuration.
    """

    config_path = workspace_path / CALIBRATION_FILENAME

    try:
        with config_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

    except FileNotFoundError:
        if not create_if_missing:
            raise FileNotFoundError(
                f"Calibration file not found: {config_path}"
            ) from None

        config = copy.deepcopy(DEFAULT_CONFIG)

        with config_path.open("w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=4)

        logger.info(
            "Created default calibration file at %s",
            config_path,
        )

        return config

    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in calibration file: {config_path}") from exc

    return _validate_and_merge(raw)
