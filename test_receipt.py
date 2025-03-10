"""
A few tests to ensure the receipt is being parsed correctly.
These were comprehensize enough to be a proof of concept when beginning.
"""

__author__ = "Kevin Dougherty"

from receipt import Receipt

# Run `python -m pytest`

text = Receipt.get_receipt_text("/Users/kevindougherty/Documents/GitHub/expense_tracking/test.png")

def test_get_receipt_text():
    assert type(Receipt.get_receipt_text("/Users/kevindougherty/Documents/GitHub/expense_tracking/test.png")) == str

def test_get_store():
    assert Receipt.get_store(text = text) == "Target"

def test_get_items():
    assert Receipt.get_items(text = text)