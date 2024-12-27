import json
import hashlib
import pandas as pd
from sqlalchemy.engine import result_tuple


from flask import make_response
from models import *
from bookstore import db
from sqlalchemy import  extract,func

def get_user_by_id(id):
    return User.query.get(id)

def get_config_by_role(role):
    return db.session.query(ConFig).filter(ConFig.name==role).first()

def get_config_by_id(id):
    return ConFig.query.get(id)

# đang tạo load sach cho index sach
def load_sach(q=None, cate_id=None, page=None):

    query = Sach.query
    if q:
        query = query.filter(Sach.ten_sach.contains(q))
    if cate_id:
        query = query.filter(Sach.ma_the_loai.__eq__(cate_id))

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
    return Sach.query.get_or_404(id)

def add_comment(content, ma_sach, user_id):
    try:
        c = Comment(content=content.strip(),
                   ma_sach=ma_sach,
                   user_id=user_id,
                   created_date=datetime.now())
        db.session.add(c)
        db.session.commit()
        return c
    except Exception as e:
        db.session.rollback()
        raise e

def stats_sach():
    return db.session.query(TheLoai.ma_the_loai, TheLoai.ten_the_loai, func.count(Sach.ma_sach))\
        .join(Sach, Sach.ma_the_loai.__eq__(TheLoai.ma_the_loai), isouter=True).group_by(TheLoai.ma_the_loai).all()

def fre_month(month,year):
    data = (
        db.session.query(
            Sach.ten_sach,
            TheLoai.ten_the_loai,  # Giả định TheLoai có trường 'ten_the_loai'
            func.sum(ChiTietHoaDon.so_luong).label("tong_so_luong"),
        )
        .join(ChiTietHoaDon, Sach.ma_sach == ChiTietHoaDon.ma_sach)
        .join(HoaDon, ChiTietHoaDon.ma_hoa_don == HoaDon.ma_hoa_don)
        .join(TheLoai, Sach.ma_the_loai == TheLoai.ma_the_loai)
        .filter(
            extract("month", HoaDon.ngay_lap) == month,
            extract("year", HoaDon.ngay_lap) == year
        )
        .group_by(Sach.ten_sach, TheLoai.ten_the_loai)
    )

    return data.all()

def fre_month_onl(month,year):
    data = (
        db.session.query(
            Sach.ten_sach,
            TheLoai.ten_the_loai,
            func.sum(ChiTietDonHang.so_luong).label("tong_so_luong"),
        )
        .join(ChiTietDonHang, Sach.ma_sach == ChiTietDonHang.ma_sach)
        .join(DonHang, ChiTietDonHang.ma_don_hang == DonHang.ma_don_hang)
        .join(TheLoai, Sach.ma_the_loai == TheLoai.ma_the_loai)
        .filter(
            extract("month", DonHang.ngay_tao) == month,
            extract("year", DonHang.ngay_tao) == year,
            DonHang.trang_thai_thanh_toan==TrangThaiThanhToan.DA_THANH_TOAN

        )
        .group_by(Sach.ten_sach, TheLoai.ten_the_loai)
    )

    return data.all()

def revenue_stats(month,year):
    data = (
        db.session.query(
            TheLoai.ten_the_loai,
            func.sum(ChiTietHoaDon.so_luong*ChiTietHoaDon.gia)
        )
        .join(Sach,Sach.ma_the_loai==TheLoai.ma_the_loai)
        .join(ChiTietHoaDon, Sach.ma_sach == ChiTietHoaDon.ma_sach)
        .join(HoaDon, ChiTietHoaDon.ma_hoa_don == HoaDon.ma_hoa_don)
        .filter(
            extract("month", HoaDon.ngay_lap) == month,
            extract("year", HoaDon.ngay_lap) == year
        )
        .group_by(TheLoai.ma_the_loai,TheLoai.ten_the_loai)
    )

    return data.all()

def revenue_stats_onl(month,year):
    data = (
        db.session.query(
            TheLoai.ten_the_loai,
            func.sum(ChiTietDonHang.so_luong * ChiTietDonHang.gia)
        )
        .join(Sach, Sach.ma_sach == ChiTietDonHang.ma_sach)
        .join(TheLoai, Sach.ma_the_loai == TheLoai.ma_the_loai)
        .join(DonHang, ChiTietDonHang.ma_don_hang == DonHang.ma_don_hang)
        .filter(
            extract("month", DonHang.ngay_tao) == month,
            extract("year", DonHang.ngay_tao) == year,
            DonHang.trang_thai_thanh_toan == TrangThaiThanhToan.DA_THANH_TOAN,
        )
        .group_by(TheLoai.ten_the_loai)
    )

    return data.all()

def load_categories():
    return TheLoai.query.all()

def get_don_hang_by_ma_KH(id):
    return db.session.query(
        DonHang.ma_don_hang,
        DonHang.ngay_tao,
        DonHang.trang_thai_thanh_toan
    ).filter(DonHang.ma_khach_hang==id).all()
def check_qua_han(id):
    data = db.session.query(DonHang).filter(DonHang.ma_khach_hang == id).all()
    for d in data:
        if (datetime.now()-d.ngay_tao).days > get_config_by_role(ConFigRole.QUA_HAN).value:
            d.update_trang_thai_don(TrangThaiThanhToan.HUY)
def get_don_hang_by_id(id):
    return db.session.query(DonHang).filter(DonHang.ma_don_hang == id).first()


def config():
    data = db.session.query(ConFig.id, ConFig.name, ConFig.value).all()

    # Chuyển đổi enum thành chuỗi tên và tạo tuple mới
    formatted_data = [(id, role.name, value) for id, role, value in data]

    return formatted_data

# Xuất báo cáo
def export_csv(data, filename,type):
        # Chuyển dữ liệu thành DataFrame
        if type=="fre":
            df = pd.DataFrame(data, columns=["Tên sách", "Tên thể loại", "Số lượng"])
        if type=="revenue":
            df = pd.DataFrame(data, columns=["Tên thể loại","Doanh thu"])
        if type=="kho":
            df= pd.DataFrame(data, columns=["Mã sách","Tên sách", "Số lượng"])
        if type=="tai_quay":
            df = pd.DataFrame(data, columns=["Mã sách", "Tên sách", "Số lượng","Giá","Thành tiền"])
        # Chuyển DataFrame thành CSV với BOM
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")

        # Tạo response để tải file
        response = make_response(csv_data)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        return response

def count_cart(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }


def add_receipt(cart, status):
    if not cart:
        raise ValueError("Giỏ hàng trống.")

    if cart:
        receipt = DonHang(
            ma_khach_hang=current_user.id,
            ngay_tao=datetime.now(),
            trang_thai_thanh_toan=status
        )
        db.session.add(receipt)
        db.session.flush()  # Đẩy dữ liệu tạm để lấy ma_don_hang

        for c in cart.values():
            d = ChiTietDonHang(
                ma_don_hang=receipt.ma_don_hang,
                ma_sach=c['id'],
                so_luong=c['quantity'],
                gia=c['price']
            )
            sach=get_sach_by_id(c['id'])
            sach.thanh_toan(c['quantity'])
        db.session.add(d)
    db.session.commit()

if __name__=='__main__':
    print(fre_month_onl(12,2024))


