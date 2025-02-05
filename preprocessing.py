"""
We should first focus on getting a function that accepts an online receipt rather than a screenshot of a receipt.

There is a lot of preprocessing that needs to be done with images, this file will attempt to pre-process for receipts.
For best results, you can use an online receipt and screenshot it to upload.

This module will just be to transform the image to make it more readable. Parsing the receipt for text will be in the receipt.py file
"""

from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import numpy as np
import cv2

# print(pytesseract.image_to_string(Image.open('test.png')))

# https://pyimagesearch.com/2021/11/22/improving-ocr-results-with-basic-image-processing/

# https://pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/