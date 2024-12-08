
import json
import hashlib
from models import *
from bookstore import db

def get_user_by_id(id):
    return User.query.get(id)


