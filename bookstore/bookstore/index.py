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


@app.route("/login", methods=['get', 'post'])
def login_process():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        u = dao.auth_user(username=username, password=password)
        if u:
            login_user(u)
            return redirect('/')

    return render_template('login.html')


@app.route('/register', methods=['get', 'post'])
def register_process():
    err_msg = ''
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password.__eq__(confirm):
            data = request.form.copy()
            del data['confirm']

            avatar = request.files.get('avatar')
            dao.add_user(avatar=avatar, **data)

            return redirect('/login')
        else:
            err_msg = 'Mật khẩu không khớp!'

    return render_template('register.html', err_msg=err_msg)

@app.route('/logout')
def logout_my_user():
    logout_user()
    return redirect('/login')

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
