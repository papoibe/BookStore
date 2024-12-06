import math
from flask import render_template, request, redirect
import dao
from bookstore import app,admin, login
from flask_login import login_user, logout_user, current_user
import cloudinary.uploader

@app.route('/')
def home():
    return render_template('index.html')

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)