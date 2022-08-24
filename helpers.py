from models import Article, Quote
from flask import request, url_for
import os
import math
from werkzeug.security import generate_password_hash as hash, check_password_hash as check_hash
import random


CATEGORIES = ["Développement personnel", "Hi-tech", "Divers"]
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ARTICLES_PER_PAGE = 10
BUTTONS_DISPLAYED = 3 # Numbers of page buttons to display at the bottom of index


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def countup_filename(filename):
    extension = os.path.splitext(filename)[1]
    nb_rows = Article.query.count()

    return str(nb_rows).zfill(4) + extension


def page_list(status, keywords, category):
    # Get the total number of articles depending on the status
    if status == "all":
        nb_articles = Article.query.filter(Article.text.contains(keywords)).count()
    elif status == "posted":  # Index page will ALWAYS use this
        if category == "":
            nb_articles = Article.query.filter(Article.text.contains(keywords), Article.posted == True).count()
        else:
            nb_articles = Article.query.filter(Article.text.contains(keywords), Article.posted == True, Article.category == category).count()
    elif status == "scheduled":
        nb_articles = Article.query.filter(Article.text.contains(keywords), Article.scheduled == True).count()
    else:  # archived
        nb_articles = Article.query.filter(Article.text.contains(keywords), Article.posted == False, Article.scheduled == False).count()


    nb_pages = math.ceil(nb_articles / ARTICLES_PER_PAGE)  # Calculate enough pages to fit all the articles
    total_pages = range(1, nb_pages + 1)  # This list represent the total of pages containing all the published articles

    return total_pages, nb_pages  # Return the list of pages and its length


def page_list_quotes():
    # Get the total number of quotes
    nb_quotes = Quote.query.count()

    nb_pages = math.ceil(nb_quotes / ARTICLES_PER_PAGE)  # Calculate enough pages to fit all the quotes
    total_pages = range(1, nb_pages + 1)  # This list represent the total of pages containing all the quotes

    return total_pages, nb_pages  # Return the list of pages and its length


def buttons_range(): 
    # Used to display the correct amount of buttons on each side of the page selected
    return math.ceil(BUTTONS_DISPLAYED/2), math.floor(BUTTONS_DISPLAYED/2)


def generate_code():
    code = ''.join(random.sample([str(x) for x in range(10)], 4))
    hashed_code = hash(code)
    return code, hashed_code


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)