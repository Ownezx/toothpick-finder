# %%
import stag
import cv2
import numpy as np
import os

workdir: str = "images/"
output_dir: str = "output/"


file_list = os.listdir(workdir)

for file in file_list:

    print(file)
    # load image
    image = cv2.imread(workdir + file)

    # detect markers
    (corners, ids, rejected_corners) = stag.detectMarkers(image, 19)

    # draw detected markers with ids
    stag.drawDetectedMarkers(image, corners, ids)

    # draw rejected quads without ids with different color
    stag.drawDetectedMarkers(image, rejected_corners, border_color=(255, 0, 0))

    # save resulting image
    cv2.imwrite(output_dir + file, image)

# %%
