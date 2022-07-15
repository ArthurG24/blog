from flask import Flask
from models import db


app = Flask(__name__, static_folder="./static", template_folder="./templates")

app.config['TEMPLATES_AUTO_RELOAD'] = True  # Used for development - check for changes in templates and static on reload

app.config['UPLOAD_FOLDER'] = 'static/img/thumbs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

db.init_app(app)
