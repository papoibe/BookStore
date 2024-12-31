from datetime import datetime
from email.policy import default
from idlelib.multicall import r

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    DateTime,
)
#Update

from sqlalchemy.orm import relationship, backref
from bookstore import app, db
from enum import Enum as RoleEnum
from flask_login import UserMixin, current_user



class UserRole(RoleEnum):
    ADMIN = 1
    USER = 2
    KHO = 3
    TAI_QUAY = 4

class TrangThaiThanhToan(RoleEnum):
    DA_THANH_TOAN=1
    DA_DAT=2
    HUY=3

class ConFigRole(RoleEnum):
    NHAP_TOI_THIEU=1
    NHAP_KHI_SO_LUONG_CON_IT_NHAT=2
    QUA_HAN=3
class TheLoai(db.Model):
    __table_args__ = {'extend_existing': True} #nếu lỗi
    ma_the_loai = Column(Integer, primary_key=True, autoincrement=True)
    ten_the_loai = Column(String(50))
    ma_sach = relationship("Sach", backref="the_loai", lazy=True)

    def __str__(self):
        return str(self.ten_the_loai)


class TacGia(db.Model):
    ma_tac_gia = Column(Integer, primary_key=True, autoincrement=True)
    ten_tac_gia = Column(String(50))
    ma_sach = relationship("Sach", backref="tac_gia", lazy=True)

    def __str__(self):
        return str(self.ma_tac_gia)


class Sach(db.Model):
    ma_sach = Column(Integer, primary_key=True, autoincrement=True)
    ten_sach = Column(String(50), nullable=False, unique=True)
    gia = Column(Integer, default=0)
    so_luong = Column(Integer)
    image = Column(String(300))
    ma_the_loai = Column(Integer, ForeignKey(TheLoai.ma_the_loai))
    ma_tac_gia = Column(Integer, ForeignKey(TacGia.ma_tac_gia))
    chi_tiet_phieu_nhap = relationship("ChiTietPhieuNhap", backref="sach")
    chi_tiet_don_hang = relationship("ChiTietDonHang", backref="sach")
    chi_tiet_hoa_don = relationship("ChiTietHoaDon", backref="sach")
    comments = relationship('Comment', backref ='sach', lazy = True)

    def __str__(self):
        return str(self.ma_sach)

    def get_ma_sach(self):
        return self.ma_sach

    def get_ten_sach(self):
        return self.ten_sach

    def get_so_luong(self):
        return self.so_luong

    def get_gia(self):
        return self.gia

    def cap_nhat_so_luong(self, so_luong):
        self.so_luong = self.so_luong + so_luong
        db.session.add(self)
        db.session.commit()

    def thanh_toan(self, so_luong):
        self.so_luong = self.so_luong - so_luong
        db.session.add(self)  # Đảm bảo đối tượng này được theo dõi
        db.session.commit()

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(
        String(100),
        default="https://res.cloudinary.com/dwmngambu/image/upload/v1733643897/boy_egj6vb.png",
    )
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    phieu_nhap_sach = relationship("PhieuNhapSach", backref="user", lazy=True)
    hoa_don = relationship("HoaDon", backref="user")
    don_hang = relationship("DonHang", backref="user")
    comments = relationship('Comment', backref='user', lazy= True)

    def __str__(self):
        return str(self.id)

    def get_role(self):
        return self.user_role

    def get_id(self):
        return self.id


class PhieuNhapSach(db.Model):
    ma_phieu_nhap = Column(Integer, primary_key=True, autoincrement=True)
    ngay_nhap = Column(DateTime)
    ma_nhan_vien_nhap = Column(Integer, ForeignKey(User.id), nullable=False)
    chi_tiet_phieu_nhap = relationship("ChiTietPhieuNhap", backref="phieu_nhap_sach")

    def __str__(self):
        return str(self.ma_phieu_nhap)


class ChiTietPhieuNhap(db.Model):
    ma_phieu_nhap = Column(
        Integer, ForeignKey(PhieuNhapSach.ma_phieu_nhap), primary_key=True
    )
    ma_sach = Column(Integer, ForeignKey(Sach.ma_sach), primary_key=True)
    so_luong = Column(Integer)

    def __str__(self):
        return str(self.ma_phieu_nhap)


class DonHang(db.Model):
    ma_don_hang = Column(Integer, primary_key=True, nullable=False)
    ma_khach_hang = Column(Integer, ForeignKey(User.id), nullable=False)
    ngay_tao = Column(DateTime, default=datetime.now)
    trang_thai_thanh_toan=Column(Enum(TrangThaiThanhToan),nullable=False)
    chi_tiet_don_hang = relationship("ChiTietDonHang", backref="don_hang")

    def __str__(self):
        return str(self.ma_don_hang)

    def update_trang_thai_don(self,value):
        self.trang_thai_thanh_toan=value
        db.session.add(self)
        db.session.commit()

class ChiTietDonHang(db.Model):
    ma_don_hang = Column(Integer, ForeignKey(DonHang.ma_don_hang), primary_key=True)
    ma_sach = Column(Integer, ForeignKey(Sach.ma_sach), primary_key=True)
    so_luong = Column(Integer, nullable=False)
    gia = Column(Integer, nullable=False)

    def __str__(self):
        return self.name


class HoaDon(db.Model):
    ma_hoa_don = Column(Integer, primary_key=True, autoincrement=True)
    ma_nhan_vien = Column(Integer, ForeignKey(User.id), nullable=False)
    ngay_lap = Column(DateTime)
    chi_tiet_hoa_don = relationship("ChiTietHoaDon", backref="hoa_don")

    def __str__(self):
        return str(self.ma_hoa_don)


class ChiTietHoaDon(db.Model):
    ma_hoa_don = Column(Integer, ForeignKey(HoaDon.ma_hoa_don), primary_key=True)
    ma_sach = Column(Integer, ForeignKey(Sach.ma_sach), primary_key=True)
    so_luong = Column(Integer)
    gia = Column(Integer)

    def __str__(self):
        return str(self.ma_hoa_don)


class Comment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)  # Thêm primary key
    content = Column(String(255), nullable = False)
    ma_sach = Column(Integer, ForeignKey(Sach.ma_sach), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable = False)
    created_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content


class ConFig(db.Model):
    id=Column(Integer,primary_key=True,autoincrement=True)
    name=Column(Enum(ConFigRole))
    value=Column(Integer)

    def update_value(self,new_value):
        self.value = new_value
        db.session.add(self)  # Đảm bảo đối tượng này được theo dõi
        db.session.commit()  #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # import json
        #
        # #  --- Add tác giả ----
        # with open('data/tac_gia.json', encoding='utf-8') as f:
        #     tac_gia = json.load(f)
        #     for t in tac_gia :
        #         tac = TacGia(**t)
        #         db.session.add(tac)
        # db.session.commit()
        #
        # # --- Add thể loại ---
        # with open('data/the_loai.json', encoding='utf-8') as f:
        #     the_loai = json.load(f)
        #     for t in the_loai :
        #         the = TheLoai(**t)
        #         db.session.add(the)
        # db.session.commit()
        #
        # #  ----  Add Sach ---
        # with open("data/sach.json", encoding="utf-8") as f:
        #     sach = json.load(f)
        #     for s in sach:
        #         sach = Sach(**s)
        #         db.session.add(sach)
        # db.session.commit()
        #
        # # Add admin
        # import hashlib
        #
        # u = User(username="admin",
        #              password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
        #              name="haunguyen",
        #              user_role=UserRole.ADMIN)
        # db.session.add(u)
        # db.session.commit()
        #
        # c1 = ConFig(name=ConFigRole.NHAP_TOI_THIEU, value=10)
        # c2= ConFig(name=ConFigRole.NHAP_KHI_SO_LUONG_CON_IT_NHAT, value=10)
        # c3=ConFig(name=ConFigRole.QUA_HAN,value=2)
        #
        # db.session.add(c1)
        # db.session.add(c2)
        # db.session.add(c3)
        # db.session.commit()
