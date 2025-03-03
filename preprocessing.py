"""
We should first focus on getting a function that accepts an online receipt rather than a screenshot of a receipt.

There is a lot of preprocessing that needs to be done with images, this file will attempt to pre-process for receipts.
For best results, you can use an online receipt and screenshot it to upload.

This module will just be to transform the image to make it more readable. Parsing the receipt for text will be in the receipt.py file
"""

import numpy as np
import cv2

class Preprocessing():
    def file_to_list(self, filename):
        file_list = []
        with open(filename, "r") as file:
            for line in file:
                file_list.append(line)

        return file_list

    def grayscale(self, image):
        """
        Takes in an image, in the form img = cv2.imread(image_file)
        """ 

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh, im_bw = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)

        return im_bw
    
    def noise_removal(self, image):
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        image = cv2.medianBlur(image, 3)
        return image
    
    def thick_font(self, image):
        image = cv2.bitwise_not(image)
        kernel = np.ones((2,2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        image = cv2.bitwise_not(image)
        return image
    
    def remove_borders(self, image):
        contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cntsSorted = sorted(contours, key=lambda x:cv2.contourArea(x))
        cnt = cntsSorted[-1]
        x, y, w, h = cv2.boundingRect(cnt)
        crop = image[y:y+h, x:x+w]
        return crop