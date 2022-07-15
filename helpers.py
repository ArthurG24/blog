from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os
from PIL import Image


app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True  # Used for development - check for changes in templates and static on reload

UPLOAD_FOLDER = 'static/img/thumbs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    posted = db.Column(db.Boolean, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    img = db.Column(db.String, nullable=False)




def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def countup_filename(filename):
    extension = os.path.splitext(filename)[1]
    nb_rows = Article.query.count()

    return str(nb_rows).zfill(4) + extension