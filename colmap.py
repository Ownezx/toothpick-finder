# type: ignore
#%%
import pycolmap
from pycolmap import Camera
from pycolmap import Image
from pycolmap import CameraModelId
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict
from itertools import combinations
import numpy as np
import apriltag
import cv2

# Define paths
project_dir = Path("colmap_project")
database_path = project_dir / "database.db"
images_dir = Path("images")
sparse_path = project_dir / "sparse"

# Ensure project directories exist
project_dir.mkdir(parents=True, exist_ok=True)
sparse_path.mkdir(exist_ok=True)

# Create an empty COLMAP database
db = pycolmap.Database.open(str(database_path))
db.clear_images()
db.clear_cameras()
db.clear_keypoints()
db.clear_matches()

# Setup april tag detector
detector = apriltag.apriltag('tagStandard41h12', threads=4)

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

# This remembers the image/keypoint ids for each AprilTag so matching is possible
# Structure: point_dictionary[tag_id][image_id] = (kp1, kp2, kp3, kp4)
point_dictionary: Dict[int, Dict[int, Tuple[int, int, int, int]]] = defaultdict(dict)

for index, image_path in enumerate(image_files):
    image:Image = Image(image_path.name,camera_id=camera_id)
    image_id = db.write_image(image)
    loaded_image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    detections = detector.detect(loaded_image) # type: ignore

    # Collect all corners into one array for this image
    all_keypoints = []
    
    for index, detection in enumerate(detections):
        corners = np.squeeze(detection['lb-rb-rt-lt'])
        scale = np.ones((corners.shape[0], 1), dtype=np.float32)
        orientation = np.zeros((corners.shape[0], 1), dtype=np.float32)
        keypoints = np.hstack((corners.astype(np.float32), scale, orientation))
        point_dictionary[detection["id"]][image_id] = [4 * index + i for i in range(0,4)]
        all_keypoints.append(keypoints)

    if all_keypoints:
        keypoints_arr = np.vstack(all_keypoints)
        db.write_keypoints(image_id, keypoints_arr)
        print(f"Wrote {len(keypoints_arr)} keypoints for {image_path.name}")
        if False: 
            print(keypoints_arr)
            debug_image = cv2.cvtColor(loaded_image, cv2.COLOR_GRAY2BGR)
            for kp in keypoints_arr:
                x, y = int(kp[0]), int(kp[1])
                cv2.circle(debug_image, (x, y), radius=10, color=(0, 0, 255), thickness=-1)
            cv2.imshow(f"Keypoints - {image_path.name}", debug_image)
            cv2.waitKey(0)  # Press any key to continue
            cv2.destroyAllWindows()
    else:
        print(f"No markers found in {image_path.name}")


pair_matches = defaultdict(list)
for tag_id, image_map in point_dictionary.items():
    image_ids = list(image_map.keys())

    # Match tag across all image pairs that see it
    for img1, img2 in combinations(image_ids, 2):

        kp_indices1 = image_map[img1]
        kp_indices2 = image_map[img2]

        # Match corresponding corners
        for kp1, kp2 in zip(kp_indices1, kp_indices2):

            # Ensure deterministic ordering
            if img1 < img2:
                pair_matches[(img1, img2)].append([kp1, kp2])
            else:
                pair_matches[(img2, img1)].append([kp2, kp1])

for (img1, img2), matches_list in pair_matches.items():

    matches_arr = np.array(matches_list, dtype=np.uint32)

    if len(matches_arr) > 0:
        db.write_matches(img1, img2, matches_arr)

        print(
            f"Wrote {len(matches_arr)} matches between "
            f"{img1} and {img2}"
        )


db.close()

# %%
