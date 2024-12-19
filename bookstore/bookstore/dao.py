
import json
import hashlib
from models import *
from bookstore import db


# đang tạo load sach cho index sach
def load_sach(q=None, cate_id=None, page=None):
    with open('data/sach.json', encoding='utf-8') as f:
        sach = json.load(f)
        if q:
            sach = [p for p in sach if p["name"].find(q)>=0]
        if cate_id:
            sach = [p for p in sach if p["category_id"].__eq__(int(cate_id))]
        return sach

    query = Sach.query

    if q:
        query = query.filter(Sach.name.contains(q))
    if cate_id:
        query = query.filter(Sach.category_id.__eq__(cate_id))

    if page:
        page_size = app.config['PAGE_SIZE']
        start = (int(page)-1)*page_size
        query = query.slice(start, start+page_size)

    return query.all()


def count_sach():
    return Sach.query.count()



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

def load_sach_by_id(id):
    with open('data/products.json', encoding='utf-8') as f:
        sach = json.load(f)
        for p in sach:
            if p["id"] == id:
                return p
