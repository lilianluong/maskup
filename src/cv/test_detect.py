import numpy as np
import cv2
from mask_detection import detect
import sys

image = cv2.imread(sys.argv[1])
print(detect(image))
