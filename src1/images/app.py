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

addition_img, addition_cords = get_cordinates(test_image, additions, "blue")
removal_img, removal_cords = get_cordinates(addition_img, removals,"red")
removal_img = cv2.cvtColor(removal_img, cv2.COLOR_BGR2RGB)

cv2.imwrite("modifications.png", removal_img)
print(removal_cords)
print(addition_cords)
