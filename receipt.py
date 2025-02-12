"""
Use pytessaract to read receipt and parse information.
https://pypi.org/project/pytesseract/

For now, we are going to assume the receipt is able to be easily read and we don't have to do any preprocessing.

The goal will be to get each receipt in the form of a dataframe with columns:
["Receipt Number", "Store", "Category", "Item", "Price", "Quantity"]

Receipt Number: unique ID representing that receipt, we could actually store the name of the store in this as the first four digits (ex: Target may be 0000, Whole Foods might be 0001)
Store: name of store
Category: this will be initialized to None here, and we will pass our df into the categories module to identify the category for each item
Item: whatever the name of the item is on the receipt
Price: the price of the item on the receipt
Quantity: if there are duplicates of the item on the receipt we will just increment this value
"""

from PIL import Image#, ImageFilter, ImageEnhance
import pytesseract
# import numpy as np
# import cv2
from transformers import pipeline
import re

# First we will need to do a lot of preprocessing an image that may pass through (see preprocessing.py)

def get_receipt_text(receipt_img):
    """
    Extract text from receipt
    """
    img = Image.open(receipt_img)
    text = pytesseract.image_to_string(img)
    return text

def file_to_list(filename):
    file_list = []
    with open(filename, "r") as file:
        for line in file:
            file_list.append(line)

    return file_list

def get_store(text, store_list_personal, store_list_general = file_to_list("brands.txt"), classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")):
    """
    We have two sets of stores. One set is extremely general that contains thousands of stores.
    The other set is personalized to each user of the platform. It is a small set of stores that user has shopped at
    recently/frequently. We will search through the personalized store list first, then the general one. If no store is found
    we will ask the user to input the name of the store and add it to their personalized set of stores.

    We're going to have a predefined set of stores here to look for and each time a new store
    is added/identified, it will be added to the predefined set of stores to look through.

    Parameters:
    text: str - string output we get from out get_receipt_text function
    store_list: list - list of stores that a person may shop at, stored in our stores.txt file
    """
    # This currently ALWAYS returns a value from the personalized list
    text = text.split(" ")
    """for item in text:
        category = classifier(item, candidate_labels = store_list_personal)
        if category:
            return category["labels"][0]"""
        
    for item in text:
        category = classifier(item, candidate_labels = store_list_general)
        if category:
            return category["labels"][0]

    # I think it would be ideal if a user could upload a list of places they frequently shop at and
    # then we first look through this list before searching the larger stores list
    # Did confirm this is SIGNIFICANTLY faster

def get_items(text):
    """
    Takes in text from the receipt and returns the items and prices as a dictionary
    """
    text = text.split("\n")
    # print(text)
    items = {}
    for line in text:
        if bool(re.search(r"\d+\.\d{2}$", string=line)):
            items["".join(filter(str.isalpha, line.rsplit(" ", 1)[0]))] = float(line.rsplit(" ", 1)[1])
    return items

def get_total(text):
    """
    Takes in the text from the receipt and returns the total and subtotal as a dictionary
    """
    text = text.split("\n")
    totals = {}
    for line in text:
        if "subtotal" in line.lower():
            totals["SubTotal"] = line.split(" ")[-1]
        if "total" in line.lower():
            totals["Total"] = line.split(" ")[-1]
    return totals