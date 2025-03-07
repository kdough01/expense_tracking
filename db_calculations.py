"""
Calculations performed after querying a database.
"""

__author__ = "Kevin Dougherty"

def index_calculations(db):
    """
    Calculates the receipt totals, and determines the unique stores,
    and unique categories from the Receipts datatable.

    Inputs:
    db: SQL DB - database to get the information from

    Outputs:
    [0]: receipt_totals: list - totals from each of the receipts in the order they appear in the DB
    [1]: unique_stores: dict - keys are the stores, values are the totals calculated by adding all the items that are not categorized as Total
    [2]: unique_categories: dict - keys are the categories, values are the totals calculated by adding all the items that are not categorized as Total
    """

    receipt_totals = []
    unique_stores = {}
    unique_categories = {}

    for receipt in db:
        item_sum = 0

        for item in receipt.receipt_items:
            if item.category != "Total":
                item_sum += float(item.total)

                if item.category in unique_categories:
                    unique_categories[item.category] += float(item.total)

                else:
                    unique_categories[item.category] = float(item.total)

        if receipt.content in unique_stores:
            unique_stores[receipt.content] += item_sum

        else:
            unique_stores[receipt.content] = item_sum

        receipt_totals.append(item_sum)

    return receipt_totals, unique_stores, unique_categories

def items_calculations(db):
    """
    Calculates the totals from the unique categories on a receipt.

    Inputs:
    db: SQL DB - database to get the information from

    Outputs:
    [0]: categories: dict - keys are the categories, values are the totals
    [1]: receipt_total: float - represents the total amount of a receipt
    """
     
    categories = {}
    receipt_total = 0

    for item in db.receipt_items:
        if item.category != "Total":
            receipt_total += float(item.total)

            if item.category in categories:
                categories[item.category] += float(item.total)

            else:
                categories[item.category] = float(item.total)

    return categories, receipt_total