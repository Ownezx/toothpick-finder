#!/usr/bin/env zsh

set -e

# ---- Local variables ----
PROJECT_DIR="colmap_project"
DATABASE_PATH="$PROJECT_DIR/database.db"
IMAGES_PATH="images"
PROJECT_FILE="$PROJECT_DIR/sparse/project.ini"

# ---- Clean database ----
rm -f "$DATABASE_PATH"
rm -rf "$PROJECT_DIR/sparse"

# ---- Run COLMAP pipeline ----
colmap feature_extractor \
    --database_path "$DATABASE_PATH" \
    --image_path "$IMAGES_PATH"

colmap exhaustive_matcher \
    --database_path "$DATABASE_PATH"

colmap automatic_reconstructor \
    --image_path "$IMAGES_PATH" \
    --workspace_path "$PROJECT_DIR"

colmap gui \
    --database_path "$DATABASE_PATH" \
    --image_path "$IMAGES_PATH" \
    --import_path "$PROJECT_DIR/sparse/0"

