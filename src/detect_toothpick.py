# type: ignore
import cv2
import numpy as np

def main_cli():
    print("lel")
    #test()


def test():
    image_path = "images/IMG_2352.jpg"

    # Load the image
    loaded_image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Extract the red channel (OpenCV uses BGR order)
    red_channel = loaded_image[:, :, 2]

    # Define a threshold (ceil) value
    ceil_value = 230  # you can change this

    # Create a binary image: 0 if below ceil, 1 if >= ceil
    binary_red = (red_channel >= ceil_value).astype(np.uint8)


    # Detect lines using Probabilistic Hough Transform
    lines = cv2.HoughLinesP(
        binary_red,
        rho=6,
        theta=np.pi / 180,
        threshold=50,       # minimum number of intersections to detect a line
        minLineLength=180,   # minimum line length to accept
        maxLineGap=15        # maximum gap between line segments
    )

    # Draw detected lines
    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            cv2.line(loaded_image, (x1, y1), (x2, y2), (0, 0, 255), 10)


    cv2.imshow("Detected Toothpicks", loaded_image)
    cv2.imwrite("outImage.jpg",loaded_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
