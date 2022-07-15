from models import Article
import os

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def countup_filename(filename):
    extension = os.path.splitext(filename)[1]
    nb_rows = Article.query.count()

    return str(nb_rows).zfill(4) + extension
