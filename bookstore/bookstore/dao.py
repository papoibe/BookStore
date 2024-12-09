
import json
import hashlib
from models import *
from bookstore import db

def get_user_by_id(id):
    return User.query.get(id)
def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username),
                          User.password.__eq__(password))

    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()
def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = None
    if avatar:
        u = User(name=name, username=username, password=password, avatar=avatar)
    else:
        u = User(name=name, username=username, password=password)
    db.session.add(u)
    db.session.commit()

