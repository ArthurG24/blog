from models import Article
import os
import math

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ARTICLES_PER_PAGE = 3
BUTTONS_DISPLAYED = 3 # Numbers of page buttons to display at the bottom of index


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def countup_filename(filename):
    extension = os.path.splitext(filename)[1]
    nb_rows = Article.query.count()

    return str(nb_rows).zfill(4) + extension


def page_list():
    nb_articles = Article.query.filter_by(posted=True).count()  # Get the total number of articles published
    nb_pages = math.ceil(nb_articles / ARTICLES_PER_PAGE)  # Calculate enough pages to fit all the articles
    total_pages = range(1, nb_pages + 1)  # This list represent the total of pages containing all the published articles

    return total_pages, nb_pages  # Return the list of pages and its length


def buttons_range(): 
    # Used to display the correct amount of buttons on each side of the page selected
    return math.ceil(BUTTONS_DISPLAYED/2), math.floor(BUTTONS_DISPLAYED/2)