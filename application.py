from datetime import datetime
import os
from PIL import Image
import math

from flask import render_template, request, Markup

from init import app
from helpers import allowed_file, countup_filename
from models import db, Article

ARTICLES_PER_PAGE = 10

@app.route("/")
def index():
    page_selected = int(request.args.get("page", 1))

    nb_articles = Article.query.filter_by(posted=True).count()

    nb_pages = math.ceil(nb_articles / ARTICLES_PER_PAGE)

    pages = range(1, nb_pages + 1)
    
    start = (page_selected * ARTICLES_PER_PAGE) - ARTICLES_PER_PAGE

    list_posts = Article.query.filter_by(posted=True).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()

    return render_template("index.html", articles=list_posts, page_selected=int(page_selected), pages=pages, Markup=Markup)


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
                img = os.path.join(app.config['UPLOAD_FOLDER'], filename),
            )

        else:
            date_object = date_object.replace(hour=datetime.today().hour, minute=datetime.today().minute)
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                posted = True,
                author = "Arthur",  # To do
                img = os.path.join(app.config['UPLOAD_FOLDER'], filename),
            )


        db.session.add(article)
        db.session.commit()

        return "Added"


@app.route("/article")
def article():
    article = Article.query.filter_by(id=request.args.get("id")).first()
    return render_template("display_article.html", article=article, Markup=Markup)
