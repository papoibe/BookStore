from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    DateTime,
)
from sqlalchemy.dialects.mssql.information_schema import mssql_temp_table_columns
from sqlalchemy.orm import relationship
from bookstore import app, db
from enum import Enum as PyEnum


class VaiTro(PyEnum):
    NHAN_VIEN_KHO = "Nhân viên kho"
    QUAN_LY = "Quản lý"
    NHAN_VIEN_TAI_QUAY = "Nhân viên tại quầy"


class PhuongThucThanhToan(PyEnum):
    THANH_TOAN_ONLINE = " Thanh toán online"
    THANH_TOAN_TRUC_TIEP = "Thanh toán trực tiếp"


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
    ma_the_loai = Column(Integer, ForeignKey(TheLoai.ma_the_loai))
    ma_tac_gia = Column(Integer, ForeignKey(TacGia.ma_tac_gia))
    chi_tiet_phieu_nhap = relationship("ChiTietPhieuNhap", backref="sach")
    chi_tiet_don_hang = relationship("ChiTietDonHang", backref="sach")

    def __str__(self):
        return self.name


class KhachHang(db.Model):
    ma_khach_hang = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True)
    password = Column(String(50), nullable=False)
    ten = Column(String(50), nullable=False)
    dia_chi = Column(String(50))
    so_dien_thoai = Column(String(10))
    don_hang = relationship("DonHang", backref="khac_hang")

    def __str__(self):
        return self.name


class NhanVien(db.Model):
    ma_nhan_vien = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50))
    password = Column(String(50), nullable=False)
    ten_nhan_vien = Column(String(50), nullable=False)
    vai_tro = Column(Enum(VaiTro))
    phieu_nhap_sach = relationship("PhieuNhapSach", backref="nhan_vien", lazy=True)
    hoa_don = relationship("HoaDon", backref="nhan_vien")

    def __str__(self):
        return self.name


class PhieuNhapSach(db.Model):
    ma_phieu_nhap = Column(Integer, primary_key=True, autoincrement=True)
    ngay_nhap = Column(DateTime)
    ma_nhan_vien_nhap = Column(
        Integer, ForeignKey(NhanVien.ma_nhan_vien), nullable=False
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
    ma_khach_hang = Column(Integer, ForeignKey(KhachHang.ma_khach_hang), nullable=False)
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
    ma_nhan_vien = Column(Integer, ForeignKey(NhanVien.ma_nhan_vien), nullable=False)
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
        with open('data/the_loai.json', encoding='utf-8') as f:
            the_loai = json.load(f)
            for t in the_loai :
                the = TheLoai(**t)
                db.session.add(the)
        db.session.commit()

        #  ----  Add Sach ---
        # with open("data/sach.json", encoding="utf-8") as f:
        #     sach = json.load(f)
        #     for s in sach:
        #         sach = Sach(**s)
        #         db.session.add(sach)
        # db.session.commit()

    # Add admin
    #     import hashlib
    #
    #     u = NhanVien(username="admin",
    #                  password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
    #                  ten_nhan_vien="haunguyen",
    #                  vai_tro=VaiTro.QUAN_LY)
    #     db.session.add(u)
    #     db.session.commit()