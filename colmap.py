#%%
import pycolmap
from pycolmap import Camera
from pycolmap import Image
from pycolmap import CameraModelId
from pycolmap import FeatureKeypoint
from pathlib import Path
import numpy as np
import stag
import cv2
import sqlite3

# Define paths
project_dir = Path("colmap_project")
database_path = project_dir / "database.db"
images_dir = Path("images")
sparse_path = project_dir / "sparse"

# Ensure project directories exist
project_dir.mkdir(parents=True, exist_ok=True)
sparse_path.mkdir(exist_ok=True)

# Create an empty COLMAP database
db = pycolmap.Database(str(database_path))
db.clear_images()
db.clear_cameras()
db.clear_keypoints()

#%%

# These are the values from my Iphone16e
camera:Camera = Camera.create(1,CameraModelId.PINHOLE,4.2,5712,4284)
camera_id = db.write_camera(camera)

image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
image_files = sorted(
    [f for f in images_dir.iterdir() if f.suffix.lower() in image_extensions]
)

if not image_files:
    raise RuntimeError(f"No images found in {images_dir}")


for index, image_path in enumerate(image_files):
    image:Image = Image(image_path.name,camera_id=camera_id)
    image_id = db.write_image(image)
    loaded_image = cv2.imread(str(image_path))
    (tag_corners, tag_ids, _) = stag.detectMarkers(loaded_image, 19)
    

    # Collect all corners into one array for this image
    all_keypoints = []
    for corners in tag_corners:
        corners = np.squeeze(corners)  # shape (4,2)
        scale = np.ones((corners.shape[0], 1), dtype=np.float32)
        orientation = np.zeros((corners.shape[0], 1), dtype=np.float32)
        keypoints = np.hstack((corners.astype(np.float32), scale, orientation))
        all_keypoints.append(keypoints)

    if all_keypoints:
        keypoints_arr = np.vstack(all_keypoints)
        db.write_keypoints(image_id, keypoints_arr)
        print(f"Wrote {len(keypoints_arr)} keypoints for {image_path.name}")
    else:
        print(f"No markers found in {image_path.name}")

db.close()

# %%
