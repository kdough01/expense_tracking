"""
Use pytessaract to read receipt and parse information.
https://pypi.org/project/pytesseract/
"""

from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import numpy as np
import cv2

# First we will need to do a lot of preprocessing an image that may pass through

def transform():
    """
    https://pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
    """

img = Image.open('test.png')

# Extract text from image
text = pytesseract.image_to_string(img)

print(text)