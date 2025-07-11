from datetime import datetime, timedelta
import os
from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, render_template, request, session, redirect, flash, url_for, Markup
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from sqlalchemy import func
from werkzeug.security import generate_password_hash as hash, check_password_hash as check_hash
# from flask_sessionstore import Session
from flask_session_captcha import FlaskSessionCaptcha

db = SQLAlchemy()

from helpers import *
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
    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["MAIL_SERVER"] = "smtp.ionos.fr"
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = "login@coolmorning.fr"
    app.config['MAIL_PASSWORD'] = "CS50iscool2022"
    app.config['MAIL_USE_SSL'] = True
    app.config['CAPTCHA_ENABLE'] = True
    app.config['CAPTCHA_LENGTH'] = 5
    app.config['CAPTCHA_WIDTH'] = 160
    app.config['CAPTCHA_HEIGHT'] = 60
    
    Session(app)

    db.init_app(app)
    return app

app = create_app()
app.app_context().push()
mail = Mail(app)
captcha = FlaskSessionCaptcha(app)



def check_schedule():
    with app.app_context():

        articles = Article.query.filter_by(scheduled=True).all()

        if articles:
            for article in articles:
                if article.date <= datetime.now():
                    article.posted = True
                    article.scheduled = False

            db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(check_schedule, 'interval', minutes=5)
scheduler.start()



@app.context_processor
def inject_categories():
    return dict(categories=CATEGORIES)


@app.errorhandler(413)
def request_entity_too_large(error):
    flash("Fichier trop volumineux", "error")
    return redirect(redirect_url())


@app.errorhandler(500)  # Key error when session["..."] doesn't exist
def key_error(error):
    session["user"] = None
    session["temp_user"] = None 
    session["code"] = None
    return redirect("/login")


@app.route("/")
def index():
    if request.args.get("q"):
        q = request.args.get("q")
    else:
        q = ""

    if request.args.get("c"):
        c = request.args.get("c")
    else:
        c = ""

    page_selected = int(request.args.get("page", 1))  # We get the current page by looking at the URL
    total_pages, nb_pages = page_list("posted", q, c) # A list of pages and its length

    # The start variable is used to query the db starting with the right article for each page
    start = (page_selected * ARTICLES_PER_PAGE) - ARTICLES_PER_PAGE
    
    # We use the two variables below to display the correct amount of buttons on each side of the page selected
    start_butt, end_butt = buttons_range()

    # In the following conditions, the variable pages represents the nb of pages displayed each time 
    # (therefore, in most case it wont't be the total nb of pages)

    # If the page selected is getting close to the beginning, we still display n buttons so we have more to the right
    if page_selected < start_butt:  
        pages = total_pages[:BUTTONS_DISPLAYED]
    
    # If the page selected is getting close to the end, we still display n buttons so we have more to the left
    elif page_selected > nb_pages - end_butt:  
        if nb_pages <= 2:
            pages = total_pages
        else:
            pages = total_pages[nb_pages - BUTTONS_DISPLAYED:]

    # Else, we have the page selected right in the middle
    else:
        pages = total_pages[page_selected - start_butt:page_selected + end_butt]  

    # For each page, query the database, starting with the right article for each page
    if c == "":
        list_posts = Article.query.filter(Article.posted == True, Article.text.contains(q)).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()
    else:
        list_posts = Article.query.filter(Article.posted == True, Article.text.contains(q), Article.category == c).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()
    quote = Quote.query.order_by(func.random()).first()

    return render_template("index.html", articles=list_posts, page_selected=int(page_selected), 
                            pages=pages, displayed=BUTTONS_DISPLAYED, total=total_pages, 
                            start_butt=start_butt, end_butt=end_butt, quote=quote, q=q, c=c, Markup=Markup)


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
            flash("Erreur de fichier", "error")
            return redirect("/create")

        date_object = datetime.strptime(request.form.get("date"), "%Y-%m-%dT%H:%M")

        if request.form["submit_button"] == "Enregistrer":
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                category = request.form.get("category"),
                posted = False,
                scheduled = False,
                author = session["user"].author_name,
                img = os.path.join(app.config['UPLOAD_FOLDER'], filename),
            )

            flash("Article archivé", "info-2")

        elif request.form["submit_button"] == "Programmer":
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                category = request.form.get("category"),
                posted = False,
                scheduled = True,
                author = session["user"].author_name,
                img = os.path.join(app.config['UPLOAD_FOLDER'], filename),
            )

            flash("Article programmé", "info-2")

        else:
            article = Article(
                title = request.form.get("title"),
                text = request.form.get("text"),
                date = date_object,
                category = request.form.get("category"),
                posted = True,
                scheduled = False,
                author = session["user"].author_name,
                img = os.path.join(app.config['UPLOAD_FOLDER'], filename),
            )

            flash("Article posté", "info")


        db.session.add(article)
        db.session.commit()

        return redirect("/create")
    
    return render_template("create.html")
        

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

        if admin and check_hash(admin.pwhash, request.form.get("password")):  # If username has been found and password is correct
            
            app.permanent_session_lifetime = timedelta(minutes=5)

            # Send verification code by email
            session["temp_user"] = admin

            code, session["code"] = generate_code()

            msg = Message("Code de confirmation", sender = "login@coolmorning.fr", recipients = [admin.email])
            msg.body = f"Le code de confirmation est : {code}"
            mail.send(msg)


            # Display page to input verification code
            return render_template("confirm_login.html")

        else:
            flash("Utilisateur ou mot de passe invalide", "error")
            return redirect("/login")

    if session["user"]:
        flash("Vous êtes déjà connecté", "info")
        return redirect("/admin")

    return render_template("login.html")


@app.route("/confirm_login", methods=["POST", "GET"])
def confirm_login():
    if request.method == "POST":

        if check_hash(session["code"], request.form.get("confirm_code")):
            session["user"] = session["temp_user"] # then in Jinja, use session.user.author_name
            session["temp_user"] = None
            app.permanent_session_lifetime = timedelta(minutes=50000)
            return redirect("/admin")
        else:
            flash("Code invalide", "error")
            return render_template("confirm_login.html")


    else:  # If session["temp_user"] doesn't exist
        if session["user"]:
            flash("Vous êtes déjà connecté", "info")
            return redirect("/admin")

        return redirect("/login")


@app.route("/admin")
def admin():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")
    session["lookup_status"] = "all"  # Used for query articles by status, either posted, archived or both
    session["lookup_keywords"] = ""
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


@app.route("/list_edit")
def list_edit():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")

    if request.args.get("keywords"):
        q = request.args.get("keywords")
    else:
        q = ""

    if request.args.get("status"):
        s = request.args.get("status")
    else:
        s = "all"

    page_selected = int(request.args.get("page", 1))  # We get the current page by looking at the URL
    total_pages, nb_pages = page_list(s, q, "")  # A list of pages and its length

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
        if nb_pages <= 2:
            pages = total_pages
        else: 
            pages = total_pages[nb_pages - BUTTONS_DISPLAYED:]

    # Else, we have the page selected right in the middle
    else:
        pages = total_pages[page_selected - start_butt:page_selected + end_butt]  

    # For each page, query the database, starting with the right article for each page
    if s == "all":
        list_posts = Article.query.filter(Article.text.contains(q)).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()
    elif s == "posted":
        list_posts = Article.query.filter(Article.posted == True, Article.text.contains(q)).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()
    elif s == "scheduled":
        list_posts = Article.query.filter(Article.posted == False, Article.scheduled == True, Article.text.contains(q)).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()
    else:  # archived
        list_posts = Article.query.filter(Article.posted == False, Article.scheduled == False, Article.text.contains(q)).order_by(Article.date.desc()).offset(start).limit(ARTICLES_PER_PAGE).all()

    return render_template("list_edit.html", articles=list_posts, page_selected=int(page_selected), 
                            pages=pages, displayed=BUTTONS_DISPLAYED, total=total_pages, start_butt=start_butt, end_butt=end_butt, q=q, s=s, Markup=Markup, zip=zip)


@app.route("/edit_article", methods=["POST", "GET"])
def edit_article():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")

    if request.method == "POST":

        article = Article.query.filter_by(id=request.form.get("id")).first()

        pic = request.files["thumb"]
        if pic:
            if allowed_file(pic.filename):
                filename = os.path.basename(article.img) # extract filename from path
                img = Image.open(pic)
                img.thumbnail([500,500], Image.ANTIALIAS)
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("Erreur de fichier", "error")
                return redirect("/edit_article")

            article.img = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
        date_object = datetime.strptime(request.form.get("date"), "%Y-%m-%dT%H:%M")
        
        article.title = request.form.get("title")
        article.text = request.form.get("text")
        article.date = date_object
        article.category = request.form.get("category")

        if request.form["submit_button"] == "Enregistrer":
            article.posted = False
            article.scheduled = False
            flash("Article archivé", "info-2")
        elif request.form["submit_button"] == "Programmer":
            article.posted = False
            article.scheduled = True
            flash("Article programmé", "info-2")
        else:
            article.scheduled = False
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


@app.route("/delete_article")
def delete_article():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")
    id = int(request.args.get("id"))
    Article.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect("/list_edit")


@app.route("/list_quote", )
def list_quotes():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")

    page_selected = int(request.args.get("page", 1))  # We get the current page by looking at the URL
    total_pages, nb_pages = page_list_quotes()  # A list of pages and its length

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
    list_quotes = Quote.query.offset(start).limit(ARTICLES_PER_PAGE).all()

    return render_template("list_quote.html", quotes=list_quotes, page_selected=int(page_selected), 
                            pages=pages, displayed=BUTTONS_DISPLAYED, total=total_pages, start_butt=start_butt, end_butt=end_butt, Markup=Markup)


@app.route("/delete_quote")
def delete_quote():
    if session["user"] == None:
        flash("Vous devez être connecté", "error")
        return redirect("/login")
        
    id = int(request.args.get("id"))
    Quote.query.filter_by(id=id).delete()
    db.session.commit()

    flash("Citation supprimée", "info")
    return redirect("/list_quote")


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        if captcha.validate():
            email = request.form.get("email")
            message = request.form.get("message")

            msg = Message(f"Message de {email}", sender = "no-reply@coolmorning.fr", recipients = ["arthurgouzy@gmail.com"])
            msg.body = message
            mail.send(msg)
        else:
            flash("Complètez le captcha", "error")
            return render_template("contact.html")


        flash("Message envoyé", "info")
        return render_template("contact.html")

    return render_template("contact.html")