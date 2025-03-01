from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from receipt import Receipt
import os
import pandas as pd
import plotly
import plotly.express as px
import json
import plotly.io as pio

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
image_uploads = 'static/image_uploads'
app.config["UPLOAD_PATH"] = image_uploads

db = SQLAlchemy(app)

# TODO: Create a monthly spending chart that displays how much a person has spent that month
# TODO: Create a login page so we can have more than one user...this might be a bit harder than we thought because of the table relationships
# TODO: Add a check where if the stores name is in a receipt explicitly we use that as the stores name.

class ReceiptTable(db.Model):
    __tablename__ = 'receipt_table'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable = False)
    total = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    receipt_items = db.relationship('ItemTable', backref='receipt_table', cascade="all, delete-orphan")

class ItemTable(db.Model):
    __tablename__ = 'item_table'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(200), nullable = False)
    total = db.Column(db.String(200), nullable = False)
    category = db.Column(db.String(200), nullable = False)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipt_table.id', ondelete="CASCADE"))

@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        image = request.files.get('img')
        file_path = os.path.join(app.config["UPLOAD_PATH"], image.filename)
        image.save(file_path)
        text = Receipt.get_receipt_text(file_path)
        
        try:
            store = Receipt.get_store(text)
            amount = Receipt.get_total(text)["Total"]
            
        except:
            store = "Could not determine"
            amount = "0"
        finally:
            new_receipt = ReceiptTable(content = store, total = amount)
            db.session.add(new_receipt)
            db.session.commit()
            items_dict = Receipt.get_items(text)
            for item in items_dict:
                category = Receipt.get_item_category(item)
                new_item = ItemTable(item = item, total = items_dict[item], category = category, receipt_id = new_receipt.id)
                db.session.add(new_item)
                db.session.commit()
            
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue adding your task."
    else:
        receipts = ReceiptTable.query.order_by(ReceiptTable.date_created).all()
        
        unique_stores = {}
        for receipt in receipts:
            if receipt.content in unique_stores:
                unique_stores[receipt.content] += float(receipt.total)
            else:
                unique_stores[receipt.content] = float(receipt.total)

        unique_stores = pd.DataFrame.from_dict(unique_stores, orient='index', columns=["Total"])

        fig = px.bar(unique_stores, x=unique_stores.index, y="Total")
        fig.update_layout(title_text=None)
        plot_html = pio.to_html(fig, full_html=False)

        header = "Expenses by Store"

        return render_template("index.html", receipts=receipts, header=header, plot_html=plot_html)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = ReceiptTable.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that task."
    
@app.route('/update-store-name/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = ReceiptTable.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        task.total = request.form['total']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue updating the store name."
    else:
        return render_template('update-store-name.html', task=task)
    
@app.route('/items/<int:receipt_id>')
def items(receipt_id):
    receipt = ReceiptTable.query.get_or_404(receipt_id)
        
    categories = {}
    for item in receipt.receipt_items:
        if item.category != "Total":
            if item.category in categories:
                categories[item.category] += float(item.total)
            else:
                categories[item.category] = float(item.total)

    categories = pd.DataFrame.from_dict(categories, orient='index', columns=["Total"])

    fig = px.pie(categories, names=categories.index, values="Total")
    fig.update_layout(title_text=None)
    plot_html = pio.to_html(fig, full_html=False)

    header = "Expenses by Category"

    return render_template('items.html', receipt = receipt, plot_html=plot_html, header=header)

@app.route('/update-item/<int:id>', methods=['GET', 'POST'])
def update_item(id):
    item = ItemTable.query.get_or_404(id)

    if request.method == 'POST':
        item.item = request.form['content']
        item.total = request.form['total']
        item.category = request.form['category']
        try:
            db.session.commit()
            return redirect(url_for('items', receipt_id = item.receipt_id))
        except:
            return "There was an issue updating the item name or total."
    else:
        return render_template('update-item.html', item=item)
    
@app.route('/delete-item/<int:id>')
def delete_item(id):
    item_to_delete = ItemTable.query.get_or_404(id)

    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        return redirect(url_for('items', receipt_id = item_to_delete.receipt_id))
    except:
        return "There was a problem deleting that item."
    
@app.route('/add-item/<int:receipt_id>', methods=["POST", "GET"])
def add_item(receipt_id):
    if request.method == 'POST':
        new_item = ItemTable(item = request.form['content'], total = request.form['total'], category = request.form['category'], receipt_id = receipt_id)

        try:
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('items', receipt_id = new_item.receipt_id))
        except:
            return "There was a problem adding that item."

if __name__ == "__main__":
    app.run(debug=True)