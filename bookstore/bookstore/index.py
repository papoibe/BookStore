import copy
import math

from flask import render_template, request, redirect, session, jsonify, abort
from sqlalchemy import false

#Update

import dao
from bookstore import (
    app,
    admin,
    login
)
from flask_login import login_user, logout_user, current_user
from models import UserRole,ConFigRole
import cloudinary.uploader
from flask_login import UserMixin
from sqlalchemy.orm import relationship



@app.route('/')
def index():
    q = request.args.get("q")
    cate_id = request.args.get("ma_the_loai")
    page = request.args.get("page")

    sach = dao.load_sach(q=q, cate_id=cate_id, page= page)
    categories = dao.load_categories()
    total = dao.count_sach()
    return render_template('index.html', sach=sach, categories=categories, pages=math.ceil(total/app.config['PAGE_SIZE']))


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/login", methods=["get", "post"])
def login_process():
    if current_user.is_authenticated:
        if current_user.get_role() == UserRole.ADMIN:
            return redirect("/admin")
        if current_user.get_role() == UserRole.KHO:
            return redirect("/kho")
        if current_user.get_role() == UserRole.TAI_QUAY:
            return redirect("/tai_quay")
        return redirect("/")
    if request.method.__eq__("POST"):
        username = request.form.get("username")
        password = request.form.get("password")

        user = dao.auth_user(username, password)
        if user:
            login_user(user)
            if user.get_role() == UserRole.ADMIN:
                return redirect("/admin")
            if user.get_role() == UserRole.KHO:
                return redirect("/kho")
            if user.get_role() == UserRole.TAI_QUAY:
                return redirect("/tai_quay")
            else:
                return redirect("/")
    return render_template("login.html")


@app.route("/kho", methods=["get", "post"])
def kho():
    err_msg = ""
    success_msg = ""
    ma_sach=[]
    so_luong=[]
    ten_sach=[]
    date=""
    if request.method == "POST":
        ma_sach = request.form.getlist("book[]")
        so_luong = request.form.getlist("quantity[]")
        ten_sach=request.form.getlist("book_name[]")
        date = request.form.get("date")
        ## Kiểm tra hợp lệ trước khi nhập
        if not date:
            err_msg = "Chưa nhập ngày"
            return render_template(
                "kho.html", err_msg=err_msg, success_msg=success_msg,
                ma_sach=ma_sach,
                so_luong=so_luong,
                ten_sach=ten_sach,
                date=date
            )
        flag = True

        for i in range(len(ma_sach)):
            sach = dao.get_sach_by_id(ma_sach[i])

            if int(so_luong[i]) < dao.get_config_by_role(ConFigRole.NHAP_TOI_THIEU).value:
                flag = False
                err_msg = (f"Mã:{sach.ma_sach}- {sach.ten_sach} nhập chưa đạt lượng sách tối thiểu"
                           f" ({dao.get_config_by_role(ConFigRole.NHAP_TOI_THIEU).value}).")
                return render_template(
                    "kho.html", err_msg=err_msg, success_msg=success_msg,
                    ma_sach=ma_sach,
                    so_luong=so_luong,
                    ten_sach=ten_sach,
                    date=date
                )
            if sach.get_so_luong() > dao.get_config_by_role(ConFigRole.NHAP_KHI_SO_LUONG_CON_IT_NHAT).value:
                flag = False
                err_msg = f"Mã:{sach.ma_sach}- {sach.ten_sach} chưa cần nhập"
                return render_template(
                    "kho.html", err_msg=err_msg, success_msg=success_msg,
                    ma_sach=ma_sach,
                    so_luong=so_luong,
                    ten_sach=ten_sach,
                    date=date
                )

        # Nhập sách
        if flag == True:
            id = dao.add_phieu_nhap_sach(
                current_user.get_id(), request.form.get("date")
            )
            for i in range(len(ma_sach)):
                dao.add_chi_tiet_phieu_nhap(int(id), ma_sach[i], int(so_luong[i]))
        success_msg = "Nhập phiếu thành công!"
        return render_template("kho.html",
                        err_msg=err_msg, success_msg=success_msg,
                           ma_sach=ma_sach,
                           so_luong=so_luong,
                           ten_sach=ten_sach,
                           date=date)
    return render_template("kho.html",
                        err_msg=err_msg, success_msg=success_msg,
                           ma_sach=ma_sach,
                           so_luong=so_luong,
                           ten_sach=ten_sach,
                           date=date)

@app.route("/tai_quay", methods=["get", "post"])
def tai_quay():
    err_msg = ""
    success_msg = ""
    ma_sach=[]
    ten_sach=[]
    so_luong=[]
    gia=[]
    thanh_tien=[]
    date=""
    totalQuantity=0
    totalAmount=0
    if request.method == "POST":
        date = request.form.get("date")
        ma_sach = request.form.getlist("book[]")
        ten_sach = request.form.getlist("book_name[]")
        so_luong = request.form.getlist("quantity[]")
        gia = request.form.getlist("price[]")
        thanh_tien= request.form.getlist("total[]")
        totalQuantity=request.form.get("totalQuantity")
        totalAmount=request.form.get("totalAmount")
        if not date:
            err_msg = "Chưa nhập ngày"
            return render_template(
                "tai_quay.html",
                err_msg=err_msg, success_msg=success_msg,
                ma_sach=ma_sach,
                so_luong=so_luong,
                ten_sach=ten_sach,
                gia=gia,
                thanh_tien=thanh_tien,
                date=date,
                totalQuantity=totalQuantity,
                totalAmount=totalAmount
            )

        id = dao.add_hoa_don(current_user.get_id(), date)
        for i in range(len(ma_sach)):
            dao.add_chi_tiet_hoa_don(
                int(id), int(ma_sach[i]), int(so_luong[i]), int(gia[i])
            )
            dao.get_sach_by_id(ma_sach[i]).thanh_toan(int(so_luong[i]))
        success_msg = "Nhập phiếu thành công!"
        print(totalQuantity)
        print(totalAmount)
    return render_template("tai_quay.html",
                           err_msg=err_msg, success_msg=success_msg,
                           ma_sach=ma_sach,
                           so_luong=so_luong,
                           ten_sach=ten_sach,
                           gia=gia,
                           thanh_tien=thanh_tien,
                           date=date,
                           totalQuantity=totalQuantity,
                           totalAmount=totalAmount
                           )


@app.route("/api/sach", methods=["POST"])
def get_sach_info():
    data = request.get_json()
    ma_sach = data.get("ma_sach")

    sach = dao.get_sach_by_id(ma_sach)
    if sach:
        return jsonify(
            {"success": True, "ten_sach": sach.get_ten_sach(), "gia": sach.get_gia()}
        )
    return jsonify({"success": False, "message": "Không tìm thấy sách"}), 404

@app.route("/register", methods=["get", "post"])
def register_process():
    err_msg = ""
    if request.method.__eq__("POST"):
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password.__eq__(confirm):
            data = request.form.copy()
            del data["confirm"]

            avatar = request.files.get("avatar")
            dao.add_user(avatar=avatar, **data)

            return redirect("/login")
        else:
            err_msg = "Mật khẩu không khớp!"

    return render_template("register.html", err_msg=err_msg)

@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect("/login")


@app.route('/sach/<int:id>')
def details(id):
    sach = dao.load_sach_by_id(id)
    categories = dao.load_categories()
    if not sach:
        abort(404)
    return render_template('product-details.html', sach=sach, categories=categories)


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)

