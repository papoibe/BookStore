from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager
import cloudinary

# Update
app= Flask(__name__)
app.secret_key = "%^$DSD^%^%^%^%^DSSD"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/bookstoree?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE'] = 8

db=SQLAlchemy(app)
login = LoginManager(app)

cloudinary.config(cloud_name='dwmngambu',
                  api_key='392636472975875',

                  api_secret='w56y3d7LMkkD4WPbsnYcNHWB6UQ')