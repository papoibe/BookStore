from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    DateTime,
)
from sqlalchemy.orm import relationship
from bookstore import app, db
from enum import Enum as RoleEnum
from flask_login import UserMixin

class UserRole(RoleEnum):
    ADMIN = 1
    USER = 2
    KHO=3
    TAI_QUAY=4

class PhuongThucThanhToan(RoleEnum):
    ONLINE = 1
    TRUC_TIEP=2


class TheLoai(db.Model):
    ma_the_loai = Column(Integer, primary_key=True, autoincrement=True)
    ten_the_loai = Column(String(50))
    ma_sach = relationship("Sach", backref="the_loai", lazy=True)

    def __str__(self):
        return self.name


class TacGia(db.Model):
    ma_tac_gia = Column(Integer, primary_key=True, autoincrement=True)
    ten_tac_gia = Column(String(50))
    ma_sach = relationship("Sach", backref="tac_gia", lazy=True)

    def __str__(self):
        return self.name


class Sach(db.Model):
    ma_sach = Column(Integer, primary_key=True, autoincrement=True)
    ten_sach = Column(String(50), nullable=False, unique=True)
    gia = Column(Integer, default=0)
    so_luong = Column(Integer)
    image=Column(String(100))
    ma_the_loai = Column(Integer, ForeignKey(TheLoai.ma_the_loai))
    ma_tac_gia = Column(Integer, ForeignKey(TacGia.ma_tac_gia))
    chi_tiet_phieu_nhap = relationship("ChiTietPhieuNhap", backref="sach")
    chi_tiet_don_hang = relationship("ChiTietDonHang", backref="sach")
    chi_tiet_hoa_don = relationship("ChiTietHoaDon", backref="sach")
    def __str__(self):
        return self.name




class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    user_role = Column(Enum(UserRole))
    phieu_nhap_sach = relationship("PhieuNhapSach", backref="user", lazy=True)
    hoa_don = relationship("HoaDon", backref="user")
    don_hang = relationship("DonHang", backref="user")
    def __str__(self):
        return self.name


class PhieuNhapSach(db.Model):
    ma_phieu_nhap = Column(Integer, primary_key=True, autoincrement=True)
    ngay_nhap = Column(DateTime)
    ma_nhan_vien_nhap = Column(
        Integer, ForeignKey(User.id), nullable=False
    )
    chi_tiet_phieu_nhap = relationship("ChiTietPhieuNhap", backref="phieu_nhap_sach")

    def __str__(self):
        return self.name


class ChiTietPhieuNhap(db.Model):
    ma_phieu_nhap = Column(
        Integer, ForeignKey(PhieuNhapSach.ma_nhan_vien_nhap), primary_key=True
    )
    ma_sach = Column(Integer, ForeignKey(Sach.ma_sach), primary_key=True)
    so_luong = Column(Integer)

    def __str__(self):
        return self.name


class DonHang(db.Model):
    ma_don_hang = Column(Integer, primary_key=True, nullable=False)
    ma_khach_hang = Column(Integer, ForeignKey(User.id), nullable=False)
    phuong_thuc_thanh_toan = Column(Enum(PhuongThucThanhToan), nullable=False)
    ngay_tao = Column(DateTime)
    chi_tiet_don_hang = relationship("ChiTietDonHang", backref="don_hang")

    def __str__(self):
        return self.name


class ChiTietDonHang(db.Model):
    ma_don_hang = Column(Integer, ForeignKey(DonHang.ma_don_hang), primary_key=True)
    ma_sach = Column(Integer, ForeignKey(Sach.ma_sach), primary_key=True)
    so_luong = Column(Integer)
    gia = Column(Integer)

    def __str__(self):
        return self.name


class HoaDon(db.Model):
    ma_hoa_don = Column(Integer, primary_key=True, autoincrement=True)
    ma_nhan_vien = Column(Integer, ForeignKey(User.id), nullable=False)
    ngay_lap = Column(DateTime)
    chi_tiet_hoa_don = relationship("ChiTietHoaDon", backref="hoa_don")

    def __str__(self):
        return self.name


class ChiTietHoaDon(db.Model):
    ma_hoa_don = Column(Integer, ForeignKey(HoaDon.ma_hoa_don), primary_key=True)
    ma_sach = Column(Integer, ForeignKey(Sach.ma_sach), primary_key=True)
    so_luong = Column(Integer)
    gia = Column(Integer)

    def __str__(self):
        return self.name


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        import json

        #  --- Add tác giả ----
        # with open('data/tac_gia.json', encoding='utf-8') as f:
        #     tac_gia = json.load(f)
        #     for t in tac_gia :
        #         tac = TacGia(**t)
        #         db.session.add(tac)
        # db.session.commit()

        # --- Add thể loại ---
        # with open('data/the_loai.json', encoding='utf-8') as f:
        #     the_loai = json.load(f)
        #     for t in the_loai :
        #         the = TheLoai(**t)
        #         db.session.add(the)
        # db.session.commit()

        #  ----  Add Sach ---
        # with open("data/sach.json", encoding="utf-8") as f:
        #     sach = json.load(f)
        #     for s in sach:
        #         sach = Sach(**s)
        #         db.session.add(sach)
        # db.session.commit()

    # Add admin
        import hashlib

        u = User(username="admin",
                     password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
                     name="haunguyen",
                     user_role=UserRole.ADMIN)
        db.session.add(u)
        db.session.commit()