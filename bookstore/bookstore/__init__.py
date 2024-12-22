from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager
import cloudinary

# Update
app= Flask(__name__)
app.secret_key = "%^$DSD^%^%^%^%^DSSD"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/bookstore?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE'] = 8

db=SQLAlchemy(app)
login = LoginManager(app)

so_luong_nhap_vao_kho_it_nhat=10
quy_dinh_de_duoc_nhap_vao_kho=10


cloudinary.config(cloud_name='dwmngambu',
                  api_key='392636472975875',

                  api_secret='w56y3d7LMkkD4WPbsnYcNHWB6UQ')