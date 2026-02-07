#!/usr/bin/env zsh

set -e

# ---- Local variables ----
PROJECT_DIR="colmap_project"
DATABASE_PATH="$PROJECT_DIR/database.db"
IMAGES_PATH="images"
PROJECT_FILE="$PROJECT_DIR/sparse/project.ini"

colmap gui \
    --database_path "$DATABASE_PATH" \
    --image_path "$IMAGES_PATH" \