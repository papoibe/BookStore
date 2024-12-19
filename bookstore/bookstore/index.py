import copy
import math

<<<<<<< HEAD
from Tools.scripts.var_access_benchmark import read_dict
from flask import render_template, request, redirect, session, jsonify
from sqlalchemy import false

=======
from flask import render_template, request, redirect
>>>>>>> 9e9ddbeb9000382b18ab542741d9eb30a0b5d5b9
import dao
from bookstore import (
    app,
    admin,
    login,
    so_luong_nhap_vao_kho_it_nhat,
    quy_dinh_de_duoc_nhap_vao_kho,
)
from flask_login import login_user, logout_user, current_user
from models import UserRole
import cloudinary.uploader
from flask_login import UserMixin
from sqlalchemy.orm import relationship

<<<<<<< HEAD

@app.route("/")
def home():
    return render_template("index.html")
=======
@app.route('/')
def index():
    q = request.args.get("q")
    cate_id = request.args.get("ma_the_loai")
    page = request.args.get("page")
    sach = dao.load_sach(q=q, cate_id=cate_id, page=page)
    total = dao.count_sach()
    return render_template('index.html', sach=sach, pages=math.ceil(total/app.config['PAGE_SIZE']))
>>>>>>> 9e9ddbeb9000382b18ab542741d9eb30a0b5d5b9


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/login", methods=["get", "post"])
def login_process():
    # if current_user.is_authenticated:
    #     return redirect("/")
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
    if request.method == "POST":
        ma_sach = request.form.getlist("book[]")
        so_luong = request.form.getlist("quantity[]")

        ## Kiểm tra hợp lệ trước khi nhập

        flag = True

        for i in range(len(ma_sach)):
            sach = dao.get_sach_by_id(ma_sach[i])
            if sach == None:
                false = False
                err_msg = "Sách không tồn tại"
                return render_template(
                    "kho.html", err_msg=err_msg, success_msg=success_msg
                )
            if int(so_luong[i]) < so_luong_nhap_vao_kho_it_nhat:
                flag = False
                err_msg = "Chưa đạt lượng sách tối thiểu"
                return render_template(
                    "kho.html", err_msg=err_msg, success_msg=success_msg
                )
            if sach.get_so_luong() > quy_dinh_de_duoc_nhap_vao_kho:
                flag = False
                err_msg = "Chưa cần nhập sách"
                return render_template(
                    "kho.html", err_msg=err_msg, success_msg=success_msg
                )
        # Nhập sách
        if flag == True:
            id = dao.add_phieu_nhap_sach(
                current_user.get_id(), request.form.get("date")
            )
            for i in range(len(ma_sach)):
                dao.add_chi_tiet_phieu_nhap(int(id), ma_sach[i], int(so_luong[i]))
        success_msg = "Nhập phiếu thành công!"
    return render_template("kho.html", err_msg=err_msg, success_msg=success_msg)


@app.route("/tai_quay", methods=["get", "post"])
def tai_quay():
    err_msg = ""
    success_msg = ""
    if request.method == "POST":
        date = request.form.get("date")
        if not date:
            err_msg = "Chưa nhập ngày"
            return render_template(
                "tai_quay.html", err_msg=err_msg, success_msg=success_msg
            )
        ma_sach = request.form.getlist("book[]")
        so_luong = request.form.getlist("quantity[]")
        gia = request.form.getlist("price[]")
        id = dao.add_hoa_don(current_user.get_id(), date)
        for i in range(len(ma_sach)):
            dao.add_chi_tiet_hoa_don(
                int(id), int(ma_sach[i]), int(so_luong[i]), int(gia[i])
            )
        success_msg = "Nhập phiếu thành công!"

    return render_template("tai_quay.html", err_msg=err_msg, success_msg=success_msg)


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
    return render_template('product-details.html', sach = sach)




if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
