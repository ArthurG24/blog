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
    date = db.Column(db.DateTime, default=datetime.now)
    posted = db.Column(db.Boolean, default=False)
    author = db.Column(db.String(50))
    thumb_img = db.Column(db.Text)
    thumb_mimetype = db.Column(db.Text)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=["POST", "GET"])
def create():
    x = 10

    if request.method == "GET":
        return render_template("create.html")

    else:
        # pic = request.files["thumb"]
        print(str(request.files))
        article = Article(title = request.form.get("title"))
        db.session.add(article)
        db.session.commit()

        return "Added"