import copy
import datetime
import math

from flask import render_template, request, redirect, session, jsonify, abort
from sqlalchemy import false

#Update

import dao
from bookstore import (
    app,
    admin,
    login,
)
from flask_login import login_user, logout_user, current_user,login_required

from models import Comment
from models import UserRole,ConFigRole,TrangThaiThanhToan
import cloudinary.uploader
from flask_login import UserMixin
from sqlalchemy.orm import relationship

@app.route('/history',methods=["GET", "POST"])
def history():
    if not current_user.is_authenticated:
        return render_template('history.html')
    dao.check_qua_han(current_user.id)
    data=dao.get_don_hang_by_ma_KH(current_user.id)

    if request.method=="POST":
        action = request.form.get("action")
        id=request.form.get("order_id")
        print(id)

        if action=="Pay":

            print("đã nhận")
            thanh_toan=dao.get_don_hang_by_id(id)
            thanh_toan.update_trang_thai_don(TrangThaiThanhToan.DA_THANH_TOAN)

        if action=="Cancel":

            print("đã hủy")
            huy=dao.get_don_hang_by_id(id)
            chi_tiet=dao.get_chi_tiet_by_ma_hoa_don(id)
            for c in chi_tiet:
                dao.get_sach_by_id(c[0]).cap_nhat_so_luong(int(c[1]))
            huy.update_trang_thai_don(TrangThaiThanhToan.HUY)

        data = dao.get_don_hang_by_ma_KH(current_user.id)
        return render_template('history.html', data=data)
    return render_template('history.html',data=data)


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
    if request.method == "POST":
        ma_sach = request.form.getlist("book[]")
        so_luong = request.form.getlist("quantity[]")
        ten_sach=request.form.getlist("book_name[]")

        action = request.form.get("action")  # Lấy giá trị action từ form

        # Nếu action là "export", thực hiện xuất CSV
        if action == "export":
            data = list(zip(ma_sach, ten_sach, so_luong))
            return dao.export_csv(data, f"bao_cao_{datetime.date.today()}.csv", type="kho")

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
                    ten_sach=ten_sach
                )
            if sach.get_so_luong() > dao.get_config_by_role(ConFigRole.NHAP_KHI_SO_LUONG_CON_IT_NHAT).value:
                flag = False
                err_msg = f"Mã:{sach.ma_sach}- {sach.ten_sach} chưa cần nhập"
                return render_template(
                    "kho.html", err_msg=err_msg, success_msg=success_msg,
                    ma_sach=ma_sach,
                    so_luong=so_luong,
                    ten_sach=ten_sach
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
                           ten_sach=ten_sach
                                   )
    return render_template("kho.html",
                        err_msg=err_msg, success_msg=success_msg,
                           ma_sach=ma_sach,
                           so_luong=so_luong,
                           ten_sach=ten_sach
                           )

@app.route("/tai_quay", methods=["get", "post"])
def tai_quay():
    err_msg = ""
    success_msg = ""
    ma_sach=[]
    ten_sach=[]
    so_luong=[]
    gia=[]
    thanh_tien=[]
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

        action = request.form.get("action")
        if action == "export":
            data = list(zip(ma_sach, ten_sach, so_luong,gia,thanh_tien))
            return dao.export_csv(data, f"phieu_thanh_toan_{datetime.date.today()}.csv", type="tai_quay")
        # vượt quá số lượng sách trong kho
        for i in range(len(ma_sach)):
            sach=dao.get_sach_by_id(ma_sach[i])
            if int(so_luong[i]) >  sach.so_luong:
                err_msg = f"Sách {sach.ten_sach} không đủ số lượng trong kho ({sach.so_luong})"
                return render_template(
                    "tai_quay.html",
                    err_msg=err_msg, success_msg=success_msg,
                    ma_sach=ma_sach,
                    so_luong=so_luong,
                    ten_sach=ten_sach,
                    gia=gia,
                    thanh_tien=thanh_tien,
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

    return render_template("tai_quay.html",
                           err_msg=err_msg, success_msg=success_msg,
                           ma_sach=ma_sach,
                           so_luong=so_luong,
                           ten_sach=ten_sach,
                           gia=gia,
                           thanh_tien=thanh_tien,
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



@app.route('/api/comments', methods=['post'])
@login_required
def add_comment():
     data = request.json
     content = data.get('content')
     ma_sach = data.get('ma_sach')

     try:
         comment = dao.add_comment(content=content,
                                   ma_sach=ma_sach,
                                   user_id=current_user.id)

         # Trả về kết quả thành công với thông tin comment
         return jsonify({
             'status': 200,
             'comment': {
                 'id': comment.id,
                 'content': comment.content,
                 'created_date': comment.created_date.strftime('%Y-%m-%d %H:%M:%S'),# Ngày tạo comment
                 'user': {
                     'username': current_user.username,
                     'avatar': current_user.avatar

                 }
             }
         })
     except Exception as ex:
         return jsonify({'status': 500, 'Chương trình bị lỗi': str(ex)}), 500




@app.route('/sach/<int:id>')
def details(id):
    sach = dao.load_sach_by_id(id)
    categories = dao.load_categories()
    if not sach:
        abort(404)

    comments = Comment.query.filter_by(ma_sach=id).order_by(Comment.created_date.desc()).all()
    return render_template('product-details.html',
                           sach=sach, categories=categories,
                           comments=comments)


@app.context_processor
def common_responce():
    return {
        'categories': dao.load_categories(),
        'cart_stats': dao.count_cart(session.get('cart'))
    }


@app.route('/cart')
def cart():
    return render_template('cart.html',
                           stats=dao.count_cart(session.get('cart')))


@app.route('/api/add-cart', methods=['post'])
def add_to_cart():
    data = request.json

    ma_sach = str(data.get('ma_sach'))
    ten_sach = data.get('ten_sach', '')
    gia = data.get('gia')

    cart = session.get('cart')
    if not cart:
        cart = {}

    if ma_sach in cart:
        cart[ma_sach]['quantity'] = cart[ma_sach]['quantity'] + 1
    else:
        cart[ma_sach] = {
            'id': ma_sach,
            'name': ten_sach,
            'price': gia,
            'quantity': 1
        }

    session['cart'] = cart

    return jsonify(dao.count_cart(cart))


@app.route('/api/pay', methods=['post'])
@login_required
def pay():
    try:
        cart = session.get('cart')
        if not cart:
            print("Giỏ hàng trống!")
            return jsonify({'code': 400, 'message': 'Giỏ hàng trống!'})

        # Gọi hàm thêm đơn hàng vào DB
        dao.add_receipt(cart, status=TrangThaiThanhToan.DA_THANH_TOAN)
        del session['cart']  # Xóa giỏ hàng sau khi thanh toán thành công
        return jsonify({'code': 200, 'message': 'Thanh toán thành công'})

    except Exception as e:
        print(f"Lỗi khi thêm đơn hàng: {e}")  # In lỗi ra console
        return jsonify({'code': 400, 'message': 'Thanh toán thất bại!'})


@app.route('/api/order', methods=['post'])
@login_required
def order():
    try:
        cart = session.get('cart')
        if not cart:
            print("Giỏ hàng trống!")
            return jsonify({'code': 400, 'message': 'Giỏ hàng trống!'})

        # Gọi hàm thêm đơn hàng vào DB
        dao.add_receipt(cart, status=TrangThaiThanhToan.DA_DAT)
        del session['cart']  # Xóa giỏ hàng sau khi thanh toán thành công
        return jsonify({'code': 200, 'message': 'Thanh toán thành công'})

    except Exception as e:
        print(f"Lỗi khi thêm đơn hàng: {e}")  # In lỗi ra console
        return jsonify({'code': 400, 'message': 'Thanh toán thất bại!'})


@app.route('/update-cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    product_id = data.get('id')
    quantity = data.get('quantity')

    if 'cart' in session:
        cart = session['cart']
        if product_id in cart:
            cart[product_id]['quantity'] = int(quantity)
            session['cart'] = cart
            return jsonify({'success': True})

    return jsonify({'success': False})


@app.route('/api/delete-cart/<product_id>', methods=['DELETE'])
def delete_cart(product_id):
    cart = session.get('cart', {})  # Lấy giỏ hàng từ session, mặc định là dictionary rỗng

    if product_id in cart:  # Kiểm tra nếu sản phẩm có trong giỏ hàng
        del cart[product_id]  # Xóa sản phẩm khỏi giỏ hàng

        session['cart'] = cart  # Cập nhật lại giỏ hàng trong session

        session['cart'] = cart  # Cập nhật lại giỏ hàng trong session

        # Trả về JSON với thông tin giỏ hàng đã được cập nhật và mã trạng thái
        return jsonify({
            'code': 200,
            'message': 'Cập nhật giỏ hàng thành công!',
            'cart': cart,
            'total_items': dao.count_cart(cart)  # Giả sử dao.count_cart trả về tổng số lượng sản phẩm trong giỏ
        })

    else:
        # Trả về JSON nếu sản phẩm không có trong giỏ hàng
        return jsonify({
            'code': 404,
            'message': 'Sản phẩm không có trong giỏ hàng!'
        })



if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
