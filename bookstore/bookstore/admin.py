from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import TheLoai
from bookstore import app, db


admin = Admin(app, name="E-commerce Website", template_mode="bootstrap4")


class TheLoaiView(ModelView):
    column_list = ["ma_the_loai", "ten_the_loai"]
    column_searchable_list = ["ma_the_loai", "ten_the_loai"]


admin.add_view(TheLoaiView(TheLoai, db.session))
