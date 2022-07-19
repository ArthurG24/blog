from init import db

def add_table():
    db.create_all()

add_table()