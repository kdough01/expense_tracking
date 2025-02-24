from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from receipt import Receipt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
image_uploads = 'static/image_uploads'
app.config["UPLOAD_PATH"] = image_uploads

db = SQLAlchemy(app)

# TODO: Create a pie-chart of spending by category to display on each receipt page
# TODO: Allow users to change the category of an item, as well as the name of an item
# TODO: Stop having it load the transformers all the time, it loads them three times every time it reloads/refreshes and slows down everything on my computer
# TODO: Create a monthly spending chart that displays how much a person has spent that month
# TODO: Create a login page so we can have more than one user...this might be a bit harder than we thought because of the table relationships

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
            amount = "Could not determine"
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
        tasks = ReceiptTable.query.order_by(ReceiptTable.date_created).all()
        return render_template("index.html", tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = ReceiptTable.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that task."
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = ReceiptTable.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue updating your task."
    else:
        return render_template('update.html', task=task)
    
@app.route('/items/<int:receipt_id>')
def items(receipt_id):
    receipt = ReceiptTable.query.get_or_404(receipt_id)
    return render_template('items.html', receipt = receipt)

if __name__ == "__main__":
    app.run(debug=True)