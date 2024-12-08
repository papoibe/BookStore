import math

from Tools.scripts.var_access_benchmark import read_dict
from flask import render_template, request, redirect
import dao
from bookstore import app, admin, login
from flask_login import login_user, logout_user, current_user
import cloudinary.uploader


@app.route('/')
def home():
    return render_template('index.html')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/login', methods=['get', 'post'])
def login_my_user():
    if request.method.__eq__('username'):
        username = request.form.get('username')
        password = request.form.get('password')
        if username.__eq__("admin") and password.__eq__("123"):
            return redirect('/')
    return render_template('login.html')


@app.route('/register', methods=["get", "post"])
def register_user():
    err_msg = None
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password.__eq__(confirm):
            ava_path = None
            name = request.form.get('name')
            username = request.form.get('username')
            avatar = request.files.get('avatar')
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                ava_path = res['secure_url']
            dao.add_user(name=name, username=username, password=password, avatar=ava_path)
            return redirect('/login')
        else:
            err_msg = "Mật khẩu không khớp!"
    return render_template('register.html', err_msg=err_msg)


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
