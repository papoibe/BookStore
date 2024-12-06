
import json
import hashlib
from models import *
from bookstore import db

def get_user_by_id(user_id):
    if NhanVien.query.get(user_id):
        return  NhanVien.query.get(user_id)
    return KhachHang.query.get(user_id)
