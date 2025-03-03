from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime
from receipt import Receipt
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from preprocessing import Preprocessing
import cv2

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
image_uploads = 'static/image_uploads'
app.config["UPLOAD_PATH"] = image_uploads
app.config["SECRET_KEY"] = "secret_key"

# TODO: Create a monthly spending chart that displays how much a person has spent that month
# TODO: Add a check where if the stores name is in a receipt explicitly we use that as the stores name.
# TODO: I need a way to manually add a receipt in case someone doesn't have a picture of their receipt
# TODO: Make sure the chart labels/axes' labels are all correct

db = SQLAlchemy(app)
"""
When we load the site it should take us to the login page automatically. There should be a button "Don't have a site, sign up!" This would take us to the sign up page.
The old root path should now be the root path to the user id whose session it is. When a user clicks "Expense Tracker Home" it should take them to the home page of their Expense
Tracker.
"""

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

preprocessing = Preprocessing()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable = False, unique = True)
    password = db.Column(db.String(80), nullable = False)
    user_receipts = db.relationship('ReceiptTable', backref='user', cascade="all, delete-orphan")

class ReceiptTable(db.Model):
    __tablename__ = 'receipt_table'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable = False)
    total = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    receipt_items = db.relationship('ItemTable', backref='receipt_table', cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))

class ItemTable(db.Model):
    __tablename__ = 'item_table'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(200), nullable = False)
    total = db.Column(db.String(200), nullable = False)
    category = db.Column(db.String(200), nullable = False)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipt_table.id', ondelete="CASCADE"))

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username = username.data).first()

        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

@app.route('/', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index', user_id = user.id))
    return render_template('login.html', form=form)

@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')
    return render_template('register.html', form=form)

@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home/<int:user_id>', methods=["POST", "GET"])
@login_required
def index(user_id):
    if request.method == "POST":
        image = request.files.get('img')
        file_path = os.path.join(app.config["UPLOAD_PATH"], image.filename)
        image.save(file_path)

        image = cv2.imread(file_path)
        image = preprocessing.grayscale(image)
        image = preprocessing.noise_removal(image)
        image = preprocessing.thick_font(image)
        image = preprocessing.remove_borders(image)
        cv2.imwrite(file_path, image)

        text = Receipt.get_receipt_text(file_path)
        
        try:
            store = Receipt.get_store(text)
            amount = Receipt.get_total(text)["Total"]
            
        except:
            store = "Could not determine"
            amount = "0"
        finally:
            new_receipt = ReceiptTable(content = store, total = amount, user_id = user_id)
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
            return redirect(url_for('index', user_id = user_id))
        except:
            return "There was an issue adding your receipt."
    else:
        receipts = ReceiptTable.query.filter_by(user_id=user_id).order_by(ReceiptTable.date_created).all()
        receipt_totals = []
        unique_stores = {}
        unique_categories = {}
        for receipt in receipts:
            if receipt.content in unique_stores:
                unique_stores[receipt.content] += float(receipt.total)
            else:
                unique_stores[receipt.content] = float(receipt.total)

            item_sum = 0
            for item in receipt.receipt_items:
                if item.category != "Total":
                    item_sum += float(item.total)
                    if item.category in unique_categories:
                        unique_categories[item.category] += float(item.total)
                    else:
                        unique_categories[item.category] = float(item.total)
            receipt_totals.append(item_sum)

        receipt_total = sum(receipt_totals)

        unique_stores = pd.DataFrame.from_dict(unique_stores, orient='index', columns=["Total"])
        unique_categories = pd.DataFrame.from_dict(unique_categories, orient='index', columns=["Total"])

        fig = px.bar(unique_stores, x=unique_stores.index, y="Total")
        fig.update_layout(title_text=None)
        expenses_by_store = pio.to_html(fig, full_html=False)

        fig = px.bar(unique_categories, x=unique_categories.index, y="Total")
        fig.update_layout(title_text=None)
        expenses_by_category = pio.to_html(fig, full_html=False)

        expenses_by_store_header = "Expenses by Store"
        expenses_by_category_header = "Expenses by Category"

        return render_template("index.html", receipts=receipts, expenses_by_store_header=expenses_by_store_header, expenses_by_store=expenses_by_store, user_id = user_id, expenses_by_category=expenses_by_category, expenses_by_category_header=expenses_by_category_header, receipt_totals=receipt_totals, receipt_total=receipt_total)

@app.route('/delete<int:user_id>/<int:receipt_id>')
def delete(user_id, receipt_id):
    task_to_delete = ReceiptTable.query.filter_by(id=receipt_id, user_id=user_id).first_or_404()

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('index', user_id=user_id, receipt_id=receipt_id))
    except:
        return "There was a problem deleting that task."
    
@app.route('/update-store-name/<int:user_id>/<int:receipt_id>', methods=['GET', 'POST'])
def update(user_id, receipt_id):
    task = ReceiptTable.query.filter_by(id=receipt_id, user_id=user_id).first_or_404()

    if request.method == 'POST':
        task.content = request.form['content']
        task.total = request.form['total']
        try:
            db.session.commit()
            return redirect(url_for('index', user_id=user_id))
        except:
            return "There was an issue updating the store name."
    else:
        return render_template('update-store-name.html', task=task, user_id=user_id, receipt_id=receipt_id)
    
@app.route('/items/<int:user_id>/<int:receipt_id>')
def items(user_id, receipt_id):
    receipt = ReceiptTable.query.filter_by(id=receipt_id, user_id=user_id).first_or_404()
        
    categories = {}
    receipt_total = 0
    for item in receipt.receipt_items:
        if item.category != "Total":
            receipt_total += float(item.total)
            if item.category in categories:
                categories[item.category] += float(item.total)
            else:
                categories[item.category] = float(item.total)

    categories = pd.DataFrame.from_dict(categories, orient='index', columns=["Total"])

    fig = px.pie(categories, names=categories.index, values="Total")
    fig.update_layout(title_text=None)
    plot_html = pio.to_html(fig, full_html=False)

    header = "Expenses by Category"

    return render_template('items.html', receipt = receipt, plot_html=plot_html, header=header, user_id=user_id, receipt_id=receipt_id, receipt_total=receipt_total)

@app.route('/update-item/<int:user_id>/<int:item_id>', methods=['GET', 'POST'])
def update_item(user_id, item_id):
    item = ItemTable.query.get_or_404(item_id)
    receipt_id = item.receipt_id

    if request.method == 'POST':
        item.item = request.form['content']
        item.total = request.form['total']
        item.category = request.form['category']
        try:
            db.session.commit()
            return redirect(url_for('items', receipt_id = receipt_id, user_id=user_id))
        except:
            return "There was an issue updating the item name or total."
    else:
        return render_template('update-item.html', item=item, user_id=user_id, receipt_id=receipt_id)
    
@app.route('/delete-item/<int:user_id>/<int:item_id>')
def delete_item(user_id, item_id):
    item_to_delete = ItemTable.query.get_or_404(item_id)
    receipt_id = item_to_delete.receipt_id

    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        return redirect(url_for('items', receipt_id = receipt_id, user_id=user_id))
    except:
        return "There was a problem deleting that item."
    
@app.route('/add-item/<int:user_id>/<int:receipt_id>', methods=["POST", "GET"])
def add_item(user_id, receipt_id):
    if request.method == 'POST':
        if request.form['total'] == "":
            return "Please enter a valid number for item amount."

        try:
            new_item = ItemTable(item = request.form['content'], total = float(request.form['total']), category = request.form['category'], receipt_id = receipt_id)
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('items', receipt_id = receipt_id, user_id=user_id, item_id = new_item.id))
        except:
            return "There was a problem adding that item."

if __name__ == "__main__":
    app.run(debug=True)