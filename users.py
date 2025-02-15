# User - stores information pertaining to a specific user like personalized store list and all of their receipt information
# Password - stores usernames and passwords, so when a user logs, information from the User class about them will be pulled up automatically


class User():

    def __init__(self, user):
        self.user = user
        self.receipts = {}
        self.personalized_categories = []
        self.personalized_stores = []

    def add_receipt(self, store, date, items):
        """
        key: store and date
        value: dictionary of items and amounts

        Ex: {Target 12/20/24: {shampoo: 4.99, milk: 2.50, eggs: 4.29}}

        store: str - name of store
        date: str - date from receipt
        items: dict - keys are items and values are amounts
        """
        self.receipts[f"{store} {date}"] = items
        return

    def delete_receipt(self, store, date):
        """
        key: store and date
        value: dictionary of items and amounts

        Ex: {Target 12/20/24: {shampoo: 4.99, milk: 2.50, eggs: 4.29}}

        store: str - name of store
        date: str - date from receipt
        """
        del self.receipts[f"{store} {date}"]
        return

    def add_category(self, category):
        """
        category: str - name of category to be added
        """
        self.personalized_categories += category
        return

    def remove_category():
        pass

    def rename_category():
        pass

    def add_store(self, store):
        self.personalized_stores += store

    def remove_store():
        pass