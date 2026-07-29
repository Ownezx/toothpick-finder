from pathlib import Path


def initialize_colmap_project(
    project_dir: Path = Path("colmap"),
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
    sparse_dir = project_dir / "sparse"
    database_path = project_dir / "database.db"

    # Create directory structure
    project_dir.mkdir(parents=True, exist_ok=True)
    sparse_dir.mkdir(exist_ok=True)

    return project_dir, database_path
