"""
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
from preprocessing import Preprocessing
import cv2

# First we will need to do a lot of preprocessing an image that may pass through (see preprocessing.py)

preprocessing = Preprocessing()

class Receipt():

    def get_receipt_text(receipt_img):
        """
        Extract text from receipt
        """
        img = Image.open(receipt_img)
        text = pytesseract.image_to_string(img)
        return text

    def get_store(text, store_list_personal = ["Target", "CVS", "Trader Joe's"], store_list_general = preprocessing.file_to_list("brands.txt")):
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
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        text = text.split(" ")
        """for item in text:
            category = classifier(item, candidate_labels = store_list_personal)
            if category:
                return category["labels"][0]"""
            
        for item in text:
            category = classifier(item, candidate_labels = store_list_personal)
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
            amount = re.search(r"\d+\.\d{2}$", string=line)
            item = "".join(filter(str.isalpha, line.rsplit(" ", 1)[0]))
            if amount and len(item) != 0:
                items[item] = amount.group()
        return items

    def get_total(text):
        """
        Takes in the text from the receipt and returns the total and subtotal as a dictionary
        """
        text = text.split("\n")
        totals = {}
        for line in text:
            if "subtotal" in line.lower():
                amount = re.search(r"\d+\.\d{2}$", string=line)
                totals["SubTotal"] = amount.group()
            if "total" in line.lower():
                amount = re.search(r"\d+\.\d{2}$", string=line)
                totals["Total"] = amount.group()
        return totals
    
    def get_item_categories(items, categories = ["Health", "Food", "Clothes", "Miscellaneous", "Electronics", "Hygiene", "Tax", "Discount", "Total"]):
        """
        Function to categorize items on a receipt.

        Parameters:
        items: dict - items from the receipt
        categories: list - pre-specified categories, can be changed
        classifier: pipeline - model that we will use to classify the items, defaulted to BART
        """
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        categorized_items_dict = {}
        items = items.keys()
        for item in items:
            category = classifier(item, candidate_labels = categories)
            categorized_items_dict[item] = category["labels"][0]

        return categorized_items_dict
    
    def get_item_category(item, categories = ["Health", "Food", "Clothes", "Miscellaneous", "Electronics", "Hygiene", "Tax", "Discount", "Total"], classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")):
        category = classifier(item, candidate_labels = categories)
        return category["labels"][0]

    def __repr__(self):
        return '<Receipt %r>' % self.id
    
# text = Receipt.get_receipt_text("/Users/kevindougherty/Documents/GitHub/expense_tracking/test.png")
# items = Receipt.get_items(text)
# print(items.keys())
# print(Receipt.get_item_categories(items=items))

if __name__ == "__main__":
    img = cv2.imread("/Users/kevindougherty/Documents/GitHub/expense_tracking/IMG_6008.jpeg")
    img = preprocessing.grayscale(img)
    img = preprocessing.noise_removal(img)
    img = preprocessing.thick_font(img)
    img = preprocessing.remove_borders(img)
    cv2.imwrite('img.jpg', img)
    R = Receipt
    text = R.get_receipt_text("img.jpg")
    print(text)
    print(R.get_store(text))
    items_dict = Receipt.get_items(text)
    print(items_dict)
    for item in items_dict:
        category = Receipt.get_item_category(item)
        print(category)