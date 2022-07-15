from datetime import datetime, timedelta
import os

from helpers import app, db, allowed_file, countup_filename, Article, UPLOAD_FOLDER
from PIL import Image

from flask import render_template, request, Markup



@app.route("/")
def index():
    list_posts = Article.query.filter_by(posted=True).order_by(Article.date.desc()).all()

    return render_template("index.html", articles=list_posts, Markup=Markup)


@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "GET":
        return render_template("create.html")

    else:
        pic = request.files["thumb"]
        if pic and allowed_file(pic.filename):
            filename = countup_filename(pic.filename)
            img = Image.open(pic)
            img.thumbnail([500,500], Image.ANTIALIAS)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(os.path.join(UPLOAD_FOLDER, filename))
        else:
            print("error")
            # TO DO Error Page, Flask will raise an RequestEntityTooLarge exception if file too large (> 32 mb)

        date_object = datetime.strptime(request.form.get("date"), "%Y-%m-%d")

        if request.form["submit_button"] == "Enregistrer":
            date_object = date_object.replace(hour=datetime.today().hour, minute=datetime.today().minute)
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                posted = False,
                author = "Arthur",  # To do
                img = os.path.join(UPLOAD_FOLDER, filename),
            )

        else:
            date_object = date_object.replace(hour=datetime.today().hour, minute=datetime.today().minute)
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