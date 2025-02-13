import os
import cv2
from utils import *


# Load the images
base_image_path = r"synthetic_samples\set6\Original.jpeg"
test_image_path = r"synthetic_samples\set6\Removed.jpg"

details  =get_file_meta(base_image_path)
# print(details)

details  =get_file_meta(test_image_path)
print(details)

base_image = read_pil_image(base_image_path)
test_image = read_pil_image(test_image_path)

additions = find_additions(base_image, test_image)
removals = find_removals(base_image, test_image)

addition_img, addition_cords = get_cordinates(test_image, additions)
removal_img, removal_cords = get_cordinates(base_image, removals)

cv2.imwrite("addition.png", addition_img)
print(addition_cords)
cv2.imwrite("removal.png", removal_img)
print(removal_cords)