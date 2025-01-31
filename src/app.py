import os
import cv2
import base64
import numpy as np
from io import BytesIO

from openai import OpenAI
import matplotlib.pyplot as plt
from PIL import Image, ImageChops

from utils import ImageUtils, PdfUtils
from llm import LLmDescriptor


class ChangeDetection():
    def __init__(self):
        """
        Initializes the ChangeDetection class with pixel threshold values.

        :param low_pixel: Lower pixel intensity threshold for detecting changes.
        :param high_pixel: Upper pixel intensity threshold for detecting changes.
        """
        self.__low_pixel = 100
        self.__high_pixel= 255
        self.__crop_box_area = 100
        self.imgutils = ImageUtils()
        self.llmdescriptor = LLmDescriptor()

    
    def compute_difference(self, img1, img2):
        """
        Computes the difference between two images and applies thresholding.

        :param img1_path: Path to the first image.
        :param img2_path: Path to the second image.
        :return: Thresholded difference image.
        """
        base_image = self.imgutils._read_image(img1)
        test_image = self.imgutils._read_image(img2)

        # Convert to grayscale
        base_gray = cv2.cvtColor(np.array(base_image), cv2.COLOR_RGB2GRAY)
        test_gray = cv2.cvtColor(np.array(test_image), cv2.COLOR_RGB2GRAY)

        # Get absolute difference
        diff = cv2.absdiff(base_gray, test_gray)

        # Threshold the difference image to highlight changes
        _, thresh = cv2.threshold(diff, self.__low_pixel, self.__high_pixel, cv2.THRESH_BINARY)
        return thresh


    def find_changes(self, thresholded_img):
        """
        Finds contours of changes in a thresholded image and calculates bounding boxes and areas.

        :param thresholded_image: Binary image with highlighted changes.
        :return: List of bounding boxes and their corresponding areas.
        """
        # Find contours of the changes
        contours, _ = cv2.findContours(thresholded_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Calculate bounding boxes for each contour
        bounding_boxes = [cv2.boundingRect(contour) for contour in contours]

        # Calculate area for each bounding box
        areas = [(w * h) for (x, y, w, h) in bounding_boxes]
        
        return bounding_boxes, areas


    def visualize_changes(self, img1_path, bounding_boxes, areas):
        """
        Visualizes changes by drawing bounding boxes on the original image.

        :param img1_path: Path to the original image.
        :param thresholded_image: Binary image with highlighted changes.
        :param bounding_boxes: List of bounding boxes around changes.
        :return: Image with bounding boxes drawn.
        """
        # Read the original image
        base_image = self.imgutils._read_image(img1_path)
        color = (255,0,0)
        thickness = 2

        # Draw bounding boxes
        for (x, y, w, h),area in zip(bounding_boxes, areas):
            if area>self.__crop_box_area:
                cv2.rectangle(base_image, (x, y), (x + w, y + h), color, thickness)
        
        # Convert back to RGB Image
        base_image = cv2.cvtColor(base_image, cv2.COLOR_BGR2RGB)

        return base_image


    def crop_changes(self, img1_path, img2_path, bounding_boxes, areas):
        base_image = self.imgutils._read_image(img1_path)
        test_image = self.imgutils._read_image(img2_path)

        croped_diff_imgs = []
        croped_diff_areas = []
        for img in [base_image, test_image]:
            for (x, y, w, h),area in zip(bounding_boxes, areas):
                if area>self.__crop_box_area:
                    crop_img = img[y:y+h, x:x+w]
                    crop_img = Image.fromarray(crop_img)
                    crop_img = self.imgutils._pil2base64(crop_img)
                    croped_diff_imgs.append(crop_img)
                    croped_diff_areas.append(area)
        return croped_diff_imgs, croped_diff_areas


    def describe_changes(self, cropped_diff_imgs):
        content = self.llmdescriptor.prepare_content(croped_diff_imgs= cropped_diff_imgs)
        response = self.llmdescriptor.get_image_description(content)
        return response
        

# Example usage
if __name__ == "__main__":
    detector = ChangeDetection()
    pdfutils = PdfUtils()
    
    # # Load the images
    # img1_path = r"D:\\Purna_Office\Soulpage_Docs\\Req-5_WebMD_Change_Detection_system\\Client_samples_about usecase\\uploadFile.jpeg"
    # img2_path = r"D:\\Purna_Office\Soulpage_Docs\\Req-5_WebMD_Change_Detection_system\\Client_samples_about usecase\\uploadFileNoError.jpeg"

    # # # Compute differences
    # # thresh_img = detector.compute_difference(img1_path, img2_path)
    # # cv2.imwrite("sample.png", thresh_img)

    # # # Find changes
    # # bounding_boxes, areas = detector.find_changes(thresh_img)

    # # # Visualize changes
    # # output_image = detector.visualize_changes(img1_path, bounding_boxes, areas)
    # # cv2.imwrite("sample1.png", output_image)

    # # # Save or display the output image
    # # cv2.imwrite("output_with_changes.jpg", cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR))
    # # print(f"Bounding Boxes: {bounding_boxes}")
    # # print(f"Areas: {areas}")

    # # # Crop the changes
    # # cropped_changes, cropped_areas = detector.crop_changes(img1_path, img2_path, bounding_boxes, areas)

    # # # # describe the changes
    # # # response = detector.describe_changes(cropped_changes)
    # # # print("Final response")
    # # # print(response)

    pdf_path = r"synthetic_samples\set5\Original.pdf"
    pdf_path1 = r"synthetic_samples\set5\Modified.pdf"
    
    pdfutils._savepdf2img(pdfpath=pdf_path, folder="Pdf_Images1")
    pdfutils._savepdf2img(pdfpath=pdf_path1, folder="Pdf_Images2")

    # Compute differences
    if len(os.listdir("Pdf_Images1"))==len(os.listdir("Pdf_Images2")):
        for img1,img2 in zip(os.listdir("Pdf_Images1"), os.listdir("Pdf_Images2")):
            img1_path = os.path.join("Pdf_Images1", img1)
            img2_path = os.path.join("Pdf_Images2", img2)

            thresh_img = detector.compute_difference(img1_path, img2_path)
            print("diff image")
            cv2.imwrite("sample.png", thresh_img)

            # Find changes
            bounding_boxes, areas = detector.find_changes(thresh_img)

            # Visualize changes
            output_image = detector.visualize_changes(img1_path, bounding_boxes, areas)
            cv2.imwrite("sample1.png", output_image)

            # Save or display the output image
            cv2.imwrite("output_with_changes.jpg", cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR))
            print(f"Bounding Boxes: {bounding_boxes}")
            print(f"Areas: {areas}")

            # Crop the changes
            cropped_changes, cropped_areas = detector.crop_changes(img1_path, img2_path, bounding_boxes, areas)
    else:
        raise Exception("Both PDFs must have same no of pages")



# #### Assumptions:
# - pixel to pixel difference here
# - assumes both imgs are of same dimensions
# - both pdfs must have same no of pages
