import sys
from models import Admin

username = sys.argv[1]
author_name = sys.argv[2]
password = sys.argv[3]

admin = Admin(
    username = username,
    author_name = author_name,
    password = password,
)