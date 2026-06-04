import os
from typing import List
from PIL import Image
from pdf2image import convert_from_path

class DocumentParser:
    def __init__(self):
        pass

    def extract_images_from_file(self, file_path: str) -> List[Image.Image]:
        """
        Loads a document (PDF or image) and returns a list of PIL Images.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            # Convert PDF pages to images
            # Note: poppler must be installed on the system for pdf2image to work
            return convert_from_path(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            # Open single image
            img = Image.open(file_path)
            # Convert to RGB to ensure compatibility
            return [img.convert("RGB")]
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
