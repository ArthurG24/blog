from datetime import datetime

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Used for development - check for changes in templates and static on reload

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime)
    posted = db.Column(db.Boolean, default=False)
    author = db.Column(db.String(50))
    img = db.Column(db.Text)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "GET":
        return render_template("create.html")

    else:
        pic = request.files["thumb"]
        date_selected = request.form.get("date")
        date_object = datetime.strptime(date_selected, "%Y-%m-%d").date()

        if request.form["submit_button"] == "Enregistrer":
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                author = "Arthur",  # To do
                img = pic.read()
            )
        else:
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                posted = True,
                author = "Arthur",  # To do
                img = pic.read()
            )


        db.session.add(article)
        db.session.commit()

        return "Added"