from app import db

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    posted = db.Column(db.Boolean, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    img = db.Column(db.String, nullable=False)
    

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    author_name = db.Column(db.String(50), nullable=False)
    pwhash = db.Column(db.String(100), nullable=False)