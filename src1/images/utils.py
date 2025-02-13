import os
import cv2
import time

import pathlib
import platform
import numpy as np
from PIL import Image, ImageChops


def get_file_meta(image_path):
    details = {}

    # File System Information
    file = pathlib.Path(image_path)
    file_stats = file.stat()

    details["name"] = file.name
    details["extension"] = file.suffix
    details["size_bytes"] = file_stats.st_size
    details["created"] = time.ctime(file_stats.st_ctime)
    details["modified"] = time.ctime(file_stats.st_mtime)
    details["accessed"] = time.ctime(file_stats.st_atime)

    # File Permissions
    details["readable"] = os.access(image_path, os.R_OK)
    details["writable"] = os.access(image_path, os.W_OK)
    details["executable"] = os.access(image_path, os.X_OK)

    # Image Information (if image)
    try:
        image = Image.open(image_path)
        details["format"] = image.format
        details["mode"] = image.mode
        details["image_size"] = image.size
        details["dpi"] = image.info.get("dpi")
        image.close()
    except Exception:
        details["image_info"] = "Not an image or could not read image properties."

    # Extended File Metadata (Linux-specific: Inode, Blocks, Device)
    details["device"] = file_stats.st_dev
    details["inode"] = file_stats.st_ino
    details["number_of_links"] = file_stats.st_nlink
    details["user_id"] = file_stats.st_uid
    details["group_id"] = file_stats.st_gid

    # System Information
    details["os"] = f"{platform.system()} {platform.release()}"
    details["python_version"] = platform.python_version()
    details["platform_architecture"] = platform.architecture()[0]

    return details


def read_pil_image(image_path):
    base_image = Image.open(image_path).convert('RGB')
    return base_image

def find_additions(base_image, test_image):
    added_pil = ImageChops.subtract(base_image, test_image)

    # converting pil to numpy
    diff_np = np.array(added_pil)

    # Converting images to grayscale
    base_gray = cv2.cvtColor(diff_np, cv2.COLOR_RGB2GRAY)
    base_gray = cv2.normalize(base_gray, None, 0, 255, cv2.NORM_MINMAX)
    t0, base_binary = cv2.threshold(base_gray, 0, 255, cv2.THRESH_BINARY+ cv2.THRESH_OTSU)

    return base_binary

def find_removals(base_image, test_image):
    removed_pil = ImageChops.subtract(test_image, base_image)
    
    # converting pil to numpy
    diff_np = np.array(removed_pil)

    # Converting images to grayscale
    base_gray = cv2.cvtColor(diff_np, cv2.COLOR_RGB2GRAY)
    base_gray = cv2.normalize(base_gray, None, 0, 255, cv2.NORM_MINMAX)
    t0, base_binary = cv2.threshold(base_gray, 0, 255, cv2.THRESH_BINARY+ cv2.THRESH_OTSU)

    return base_binary


def get_cordinates(base_image, base_binary):
    contours, _ = cv2.findContours(base_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # Calculate bounding boxes for each contour
    bounding_boxes = [cv2.boundingRect(contour) for contour in contours]

    # Calculate area for each bounding box
    areas = [(w * h) for (x, y, w, h) in bounding_boxes]
    print(len(bounding_boxes))

    image_with_boxes = np.array(base_image.copy())
    filtered_bboxes = []
    for (x, y, w, h),area in zip(bounding_boxes, areas):
        print("area", area)
        if area>=50:
            cv2.rectangle(image_with_boxes, (x, y), (x + w, y + h), 255, 10)  # Green box with thickness 2
            filtered_bboxes.append([x,y,w,h])
    
    return image_with_boxes, filtered_bboxes




# Example usage:
# meta = get_file_meta("example.jpg")
# print(meta)
