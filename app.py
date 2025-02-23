from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from receipt import Receipt
import os


# https://www.youtube.com/watch?v=Z1RJmh_OqeA

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
image_uploads = 'static/image_uploads'
app.config["UPLOAD_PATH"] = image_uploads

db = SQLAlchemy(app)

class ReceiptTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable = False)
    total = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        image = request.files.get('img')
        file_path = os.path.join(app.config["UPLOAD_PATH"], image.filename)
        image.save(file_path)

        
        try:
            store = Receipt.get_store(file_path)
            amount = Receipt.get_total(file_path)["Total"]

        except:
            store = "Could not determine"
            amount = "Could not determine"
        finally:
            new_task = ReceiptTable(content = store, total = amount)
            
        try:
            db.session.add(new_task)
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

if __name__ == "__main__":
    app.run(debug=True)