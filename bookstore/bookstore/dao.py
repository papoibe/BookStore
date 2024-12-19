import json
import hashlib

from sqlalchemy.engine import result_tuple

from models import *
from bookstore import db


def get_user_by_id(id):
    return User.query.get(id)

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


def auth_user(username, password, user_role=None):
    password = str(hashlib.md5(password.encode("utf-8")).hexdigest())

    u = User.query.filter(
        User.username.__eq__(username), User.password.__eq__(password)
    )

    if user_role:
        u = u.filter(User.user_role.__eq__(user_role))

    return u.first()


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
    u = None
    if avatar:
        u = User(name=name, username=username, password=password, avatar=avatar)
    else:
        u = User(name=name, username=username, password=password)
    db.session.add(u)
    db.session.commit()


def get_sach_by_id(id):
    s = Sach.query.filter(Sach.ma_sach == id).first()
    return s


def add_phieu_nhap_sach(id, date):
    phieu = PhieuNhapSach(ma_nhan_vien_nhap=id, ngay_nhap=date)
    db.session.add(phieu)
    db.session.commit()
    return phieu.ma_phieu_nhap


def add_chi_tiet_phieu_nhap(id, ma_sach, so_luong):
    chi_tiet = ChiTietPhieuNhap(ma_phieu_nhap=id, ma_sach=ma_sach, so_luong=so_luong)

    # cập nhất số lượng sách
    sach = get_sach_by_id(ma_sach)
    sach.cap_nhat_so_luong(so_luong)

    db.session.add(chi_tiet)
    db.session.commit()


def add_hoa_don(id, date):
    hoadon = HoaDon(ma_nhan_vien=id, ngay_lap=date)
    db.session.add(hoadon)
    db.session.commit()
    return hoadon.ma_hoa_don


def add_chi_tiet_hoa_don(id, ma_sach, so_luong, gia):
    chi_tiet = ChiTietHoaDon(ma_hoa_don=id, ma_sach=ma_sach, so_luong=so_luong, gia=gia)
    db.session.add(chi_tiet)
    db.session.commit()

def load_sach_by_id(id):
    with open('data/products.json', encoding='utf-8') as f:
        sach = json.load(f)
        for p in sach:
            if p["id"] == id:
                return p

