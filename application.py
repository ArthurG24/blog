from datetime import datetime
import os
from werkzeug.utils import secure_filename


from flask import Flask, render_template, request, Markup
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

UPLOAD_FOLDER = 'static/img/thumbs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['TEMPLATES_AUTO_RELOAD'] = True  # Used for development - check for changes in templates and static on reload

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

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


@app.route("/")
def index():
    list_texts = []
    list_posts = Article.query.filter_by(posted=True).all()

    for post in list_posts:
        list_texts.append(Markup(post.text))

    return render_template("index.html", articles=list_posts, texts=list_texts, zip=zip)


@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "GET":
        return render_template("create.html")

    else:
        pic = request.files["thumb"]
        if pic and allowed_file(pic.filename):
            filename = secure_filename(pic.filename)
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(os.path.join(UPLOAD_FOLDER, filename))
        else:
            print("error")
            # TO DO Error Page, Flask will raise an RequestEntityTooLarge exception if file too large (> 32 mb)

        date_object = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()

        if request.form["submit_button"] == "Enregistrer":
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                posted = False,
                author = "Arthur",  # To do
                img = os.path.join(UPLOAD_FOLDER, filename),
            )
        else:
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                posted = True,
                author = "Arthur",  # To do
                img = os.path.join(UPLOAD_FOLDER, filename),
            )


        db.session.add(article)
        db.session.commit()

        return "Added"