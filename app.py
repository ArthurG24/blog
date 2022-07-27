from datetime import datetime
import os
from PIL import Image

from flask import Flask, render_template, request, session, redirect, flash, url_for, Markup
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash as hash, check_password_hash as check_hash

db = SQLAlchemy()

from helpers import allowed_file, countup_filename, page_list, buttons_range, ARTICLES_PER_PAGE, BUTTONS_DISPLAYED, CATEGORIES
from models import Article, Admin, Quote

# To execute from the terminal
def create_admin():
    admin = Admin(
        username = input("Username: "),
        author_name = input("Author name: "),
        email = input("Email: "),
        pwhash = hash(input("Password: ")),
    )

    db.session.add(admin)
    db.session.commit()

    print(admin.username)
    print(admin.author_name)
    print(admin.pwhash)


def create_app():
    app = Flask(__name__, static_folder="./static", template_folder="./templates")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # Used for development - check for changes in templates and static on reload
    app.config['UPLOAD_FOLDER'] = 'static/img/thumbs'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    Session(app)

    db.init_app(app)
    return app

app = create_app()
app.app_context().push()



@app.route("/")
def index():
    page_selected = int(request.args.get("page", 1))  # We get the current page by looking at the URL
    total_pages, nb_pages = page_list("posted") # A list of pages and its length

    # The start variable is used to query the db starting with the right article for each page
    start = (page_selected * ARTICLES_PER_PAGE) - ARTICLES_PER_PAGE
    
    # We use the two variables below to display the correct amount of buttons on each side of the page selected
    start_butt, end_butt = buttons_range()

    # In the following conditions, the variable pages represents the nb of pages displayed each time (therefore, in most case it wont't be the total nb of pages)
    # If the page selected is getting close to the beginning, we still display n buttons so we have more to the right
    if page_selected < start_butt:  
        pages = total_pages[:BUTTONS_DISPLAYED]
    
    # If the page selected is getting close to the end, we still display n buttons so we have more to the left
    elif page_selected > nb_pages - end_butt:  
        pages = total_pages[nb_pages - BUTTONS_DISPLAYED:]

    # Else, we have the page selected right in the middle
    else:
        pages = total_pages[page_selected - start_butt:page_selected + end_butt]  

    # For each page, query the database, starting with the right article for each page
    list_posts = Article.query.filter_by(posted=True).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()
    quote = Quote.query.order_by(func.random()).first()

    return render_template("index.html", articles=list_posts, page_selected=int(page_selected), 
                            pages=pages, displayed=BUTTONS_DISPLAYED, total=total_pages, start_butt=start_butt, end_butt=end_butt, quote=quote, Markup=Markup)


@app.route("/create", methods=["POST", "GET"])
def create():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")
    
    if request.method == "POST":
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

        date_object = date_object.replace(hour=datetime.today().hour, minute=datetime.today().minute)

        if request.form["submit_button"] == "Enregistrer":
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                category = request.form.get("category"),
                posted = False,
                author = session["user"].author_name,
                img = os.path.join(app.config['UPLOAD_FOLDER'], filename),
            )

            flash("Article archivé", "info-2")

        else:
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                category = request.form.get("category"),
                posted = True,
                author = session["user"].author_name,
                img = os.path.join(app.config['UPLOAD_FOLDER'], filename),
            )

            flash("Article posté", "info")


        db.session.add(article)
        db.session.commit()

        return redirect("/create")
    
    return render_template("create.html", categories=CATEGORIES)
        

@app.route("/article")
def article():
    article = Article.query.filter_by(id=request.args.get("id")).first()
    return render_template("display_article.html", article=article, Markup=Markup)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")

        if "@" in identifier:
            admin = Admin.query.filter_by(email=identifier).first()
        else:
            admin = Admin.query.filter_by(username=identifier).first()

        if admin and check_hash(admin.pwhash, request.form.get("password")):  # If username has been found and password correct
            session["user"] = admin  # then in Jinja, session.user.author_name will work

            return redirect("/admin")

        else:
            flash("Utilisateur ou mot de passe invalide", "error")
            return redirect("/login")

    return render_template("login.html")


@app.route("/admin")
def admin():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")
    session["lookup_edit"] = "both"  # Used for query articles by status, either posted, archived or both
    return render_template("admin.html")


@app.route("/password", methods=["POST", "GET"])
def modify_password():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")

    if request.method == "POST":
        old = request.form.get("old_password")
        new = request.form.get("new_password")
        
        admin = Admin.query.filter_by(id=session["user"].id).first()

        if check_hash(admin.pwhash, old):
            admin.pwhash = hash(new)
            db.session.commit()
            flash("Mot de passe changé !", "info")
            return redirect("/password")
        else:
            flash("Ancien mot de passe invalide", "error")
            return redirect("/password")
            
    return render_template("modify_password.html")


@app.route("/logout")
def logout():
    session["user"] = None

    return redirect("/")


@app.route("/list_edit", methods=["POST", "GET"])
def list_edit():
    
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")

    if request.method == "POST":
        session["lookup_edit"] = request.form.get("status")
        return redirect("/list_edit")

    page_selected = int(request.args.get("page", 1))  # We get the current page by looking at the URL
    total_pages, nb_pages = page_list(session["lookup_edit"])  # A list of pages and its length

    # The start variable is used to query the db starting with the right article for each page
    start = (page_selected * ARTICLES_PER_PAGE) - ARTICLES_PER_PAGE
    
    # We use the two variables below to display the correct amount of buttons on each side of the page selected
    start_butt, end_butt = buttons_range()

    # In the following conditions, the variable pages represents the nb of pages displayed each time (therefore, in most case it wont't be the total nb of pages)
    # If the page selected is getting close to the beginning, we still display n buttons so we have more to the right
    if page_selected < start_butt:  
        pages = total_pages[:BUTTONS_DISPLAYED]
    
    # If the page selected is getting close to the end, we still display n buttons so we have more to the left
    elif page_selected > nb_pages - end_butt:  
        pages = total_pages[nb_pages - BUTTONS_DISPLAYED:]

    # Else, we have the page selected right in the middle
    else:
        pages = total_pages[page_selected - start_butt:page_selected + end_butt]  

    # For each page, query the database, starting with the right article for each page
    if session["lookup_edit"] == "both":
        list_posts = Article.query.order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()
    elif session["lookup_edit"] == "posted":
        list_posts = Article.query.filter_by(posted=True).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()
    else:
        list_posts = Article.query.filter_by(posted=False).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()

    return render_template("list_edit.html", articles=list_posts, page_selected=int(page_selected), 
                            pages=pages, displayed=BUTTONS_DISPLAYED, total=total_pages, start_butt=start_butt, end_butt=end_butt, Markup=Markup, zip=zip)


@app.route("/edit_article", methods=["POST", "GET"])
def edit_article():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")

    if request.method == "POST":

        article = Article.query.filter_by(id=request.form.get("id")).first()

        pic = request.files["thumb"]
        if pic and allowed_file(pic.filename):
            filename = os.path.basename(article.img) # extract filename from path
            img = Image.open(pic)
            img.thumbnail([500,500], Image.ANTIALIAS)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            article.img = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
        date_object = datetime.strptime(request.form.get("date"), "%Y-%m-%d")
        date_object = date_object.replace(hour=datetime.today().hour, minute=datetime.today().minute)
        
        article.title = request.form.get("title")
        article.text = request.form.get("text")
        article.date = date_object
        article.category = request.form.get("category")

        if request.form["submit_button"] == "Enregistrer":
            article.posted = False
            flash("Article archivé", "info-2")
        else:
            article.posted = True
            flash("Article posté", "info")

        db.session.commit()

        return redirect(url_for("edit_article", id=article.id))

    article = Article.query.filter_by(id=request.args.get("id")).first()

    return render_template("edit_article.html", categories=CATEGORIES, article=article)


@app.route("/quote", methods=["POST", "GET"])
def quote():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")

    if request.method == "POST":
        if request.form.get("author"):
            quote = Quote(
                author = request.form.get("author"),
                text = request.form.get("text")
            )
        else:
            quote = Quote(text = request.form.get("text"))

        db.session.add(quote)
        db.session.commit()

        flash("Citation postée !", "info")

        return redirect("/quote")

    
    return render_template("quote.html")