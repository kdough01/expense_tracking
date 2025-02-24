from app import app, ReceiptTable, ItemTable

with app.app_context():
    items = ItemTable.query.all()

    for item in items:
        print(item.id)
        print(item.receipt_id)