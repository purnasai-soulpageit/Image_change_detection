import os
import base64
import shutil
import numpy as np

from PIL import Image
from io import BytesIO
from pathlib import Path

from pdf2image import convert_from_path
from dotenv import load_dotenv

print(load_dotenv(Path("src\\.env")))

class ImageUtils():
    def __init__(self):
        pass

    def _read_image(self, img_path):
        """
        Reads and converts an image to RGB format.

        :param img_path: Path to the image file.
        :return: Image in RGB format.
        """
        try:
            image = Image.open(img_path).convert('RGB')
            return np.array(image)
        except Exception as e:
            raise ValueError(f"Error reading image {img_path}: {e}")
        
    def _pil2base64(self, pil_image):
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")  # Specify the format (e.g., PNG, JPEG)
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return encoded_image
    
class PdfUtils():
    def __init__(self):
        pass

    def _savepdf2img(self, pdfpath, folder=""):
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
        
        convert_from_path(pdfpath, 
                          output_folder=folder,
                          fmt=".png")



