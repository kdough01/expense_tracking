"""
This module transforms the image to make it more readable.
"""

__author__ = "Kevin Dougherty"

import numpy as np
import cv2

class Preprocessing():
    """
    A small class to preprocess text so a user is able to take a picture of their own
    receipt and upload it.
    """

    def file_to_list(self, filename):
        """
        Converts a file to a list

        Inputs:
        filename: str - name of the file to be converted to a list
        """
        file_list = []
        with open(filename, "r") as file:
            for line in file:
                file_list.append(line)

        return file_list

    def grayscale(self, image):
        """
        Converts the image to a grayscale to help reduce unnecessary colors
        the camera may pick up. We convert the image to black and white here
        to make it as clear as possible for the comptuer to read.

        Inputs:
        image: numpy.ndarray - img = cv2.imread(image_file) is the line of code used to create the argument

        Outputs:
        im_bw: numpy.ndarray - the resulting black and white image
        """ 

        # gray-scale image
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # black and white output
        thresh, im_bw = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)

        return im_bw
    
    def noise_removal(self, image):
        """
        Removes noise from an image. For example, printed text may have small
        dots or imperfections that may make it more difficult for the computer
        to accurately read.

        Inputs:
        image: numpy.ndarray - accepts an image, used after the grayscale function

        Outputs:
        image: numpy.ndarray - returns an image with the background noise removed/significantly reduced
        """

        kernel = np.ones((1, 1), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        image = cv2.medianBlur(image, 3)

        return image
    
    def thick_font(self, image):
        """
        Boldens the font, and makes it thicker and easier for the computer to see and read.
        Oftentimes receipts have thin text making them hard to read. This thickens the font.

        Inputs:
        image: numpy.ndarray - accepts an image, used after the noise_removal function

        Outputs:
        image: numpy.ndarray - returns an image with thicker font
        """
        image = cv2.bitwise_not(image)
        kernel = np.ones((2,2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        image = cv2.bitwise_not(image)
        return image
    
    def remove_borders(self, image):
        """
        If a user takes a picture of a receipt this accurately identifies the edges of the receipt
        and crops the image so only the receipt is left.

        Inputs:
        image: numpy.ndarray - accepts an image, used after the thick_font function

        Outputs:
        image: numpy.ndarray - returns a cropped image with only the receipt showing
        """
        contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cntsSorted = sorted(contours, key=lambda x:cv2.contourArea(x))
        cnt = cntsSorted[-1]
        x, y, w, h = cv2.boundingRect(cnt)
        crop = image[y:y+h, x:x+w]
        return crop