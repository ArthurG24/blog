from datetime import datetime
import os
from PIL import Image
import math

from flask import render_template, request, Markup

from init import app
from helpers import allowed_file, countup_filename
from models import db, Article

ARTICLES_PER_PAGE = 3

@app.route("/")
def index():
    page_selected = int(request.args.get("page", 1))  # We get the current page by looking at the URL
    nb_articles = Article.query.filter_by(posted=True).count()  # Get the total number of articles published
    nb_pages = math.ceil(nb_articles / ARTICLES_PER_PAGE)  # Calculate enough pages to fit all the articles
    total_pages = range(1, nb_pages + 1)  # This list represent the total of pages containing all the published articles
    # The start variable is used to query the db starting with the right article for each page
    start = (page_selected * ARTICLES_PER_PAGE) - ARTICLES_PER_PAGE

    displayed = 3  # Numbers of page buttons to display at the bottom
    
    # We use the two variables below to display the correct amount of buttons on each side of the page selected
    start_butt = math.ceil(displayed/2)
    end_butt = math.floor(displayed/2)


    # In the following conditions, the variable pages represents the nb of pages displayed each time (therefore, in most case it wont't be the total nb of pages)
    # If the page selected is getting close to the beginning, we still display n buttons so we have more to the right
    if page_selected < start_butt:  
        pages = total_pages[:displayed]
    
    # If the page selected is getting close to the end, we still display n buttons so we have more to the left
    elif page_selected > nb_pages - end_butt:  
        pages = total_pages[nb_pages - displayed:]

    # Else, we have the page selected right in the middle
    else:
        pages = total_pages[page_selected - start_butt:page_selected + end_butt]  

    # For each page, query the database, starting with the right article for each page
    list_posts = Article.query.filter_by(posted=True).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()

    return render_template("index.html", articles=list_posts, page_selected=int(page_selected), 
                            pages=pages, displayed=displayed, total=total_pages, start=start_butt, end=end_butt, nb_pages=nb_pages, Markup=Markup)


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
