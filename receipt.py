"""
Parsing the receipt for text, store, items, item categories, and totals.
"""

__author__ = "Kevin Dougherty"

from PIL import Image
import pytesseract
from transformers import pipeline
import re
from preprocessing import Preprocessing

preprocessing = Preprocessing()

class Receipt():

    def get_receipt_text(receipt_img):
        """
        Extract text from receipt using OCR

        Inputs:
        receipt_img: str - path to the receipt (lies in the static/image_uploads folder)

        Outputs:
        text: str - the text from the receipt as outputted by pytesseract, used after functions in preprocessing class
        """
        img = Image.open(receipt_img)
        text = pytesseract.image_to_string(img)
        return text

    def get_store(text, store_list_personal = ["Target", "CVS", "Trader Joe's", "Chipotle"], store_list_general = preprocessing.file_to_list("brands.txt")):
        """
        We have two sets of stores. One set is extremely general that contains thousands of stores.
        The other set is personalized to each user of the platform. It is a small set of stores that user has shopped at
        recently/frequently. We will search through the personalized store list so the program runs faster. If I were to
        make a modification it would be to allow users to add their own stores to the platform to be used here.

        The general store list takes too long to parse and reduces the runtime of the app significantly.

        Parameters:
        text: str - string output we get from out get_receipt_text function
        store_list: list - list of stores that a person may shop at, stored in our stores.txt file
        """

        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        text = text.split(" ")
            
        for item in text:
            category = classifier(item, candidate_labels = store_list_personal)
            if category:
                return category["labels"][0]

    def get_items(text):
        """
        Determines the items on a receipt by matching a regex pattern

        Inputs:
        text: str - the text from the receipt
         
        Outputs:
        items: dict - returns the items and prices as a dictionary
        """
        text = text.split("\n")
        items = {}
        for line in text:
            amount = re.search(r"\d+\.\d{2}$", string=line)
            item = "".join(filter(str.isalpha, line.rsplit(" ", 1)[0]))
            if amount and len(item) != 0:
                items[item] = amount.group()
        return items

    def get_total(text):
        """
        Retrieves the total on the receipt.

        Inputs:
        text: str - the text from the receipt
         
        Outputs:
        totals: dict - returns a dictionary with the keys being Total and Subtotal and the values being the amounts for both
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
        """
        Retrieves the category of a single item

        Inputs:
        item: str - an item from the receipt
        categories: list - a predefined list of categories, future iterations of this project may allow users to input their own categories
        classifier: pipeline - a transformers pipeline that connects to BART to identify what category a receipt item is most likely a part of
        """
        category = classifier(item, candidate_labels = categories)
        return category["labels"][0]

    def __repr__(self):
        """
        Returns the receipt id as a string object.
        """
        return '<Receipt %r>' % self.id