from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.sqla import ModelView
from models import *
from bookstore import app, db,dao
from flask_login import current_user, logout_user
from flask_admin import BaseView, expose
from flask import redirect,request
import hashlib
from  sqlalchemy import func

class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render('admin/index.html',books=dao.stats_sach())
admin = Admin(app, name="E-commerce Website", template_mode="bootstrap4",index_view=MyAdminIndexView())

class UserView(ModelView):
    column_list = ["id","username","name","user_role"]
    column_searchable_list = ["id","username","user_role"]
    form_excluded_columns = ["phieu_nhap_sach", "don_hang", "hoa_don","comments"]

    # xử lý băm mật khẩu trước khi lưu
    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password = hashlib.md5(model.password.encode('utf-8')).hexdigest()
        super(UserView, self).on_model_change(form, model, is_created)


class SachView(ModelView):
    column_list = ["ma_sach","ten_sach","gia","so_luong","image","ma_the_loai",
                   "ma_tac_gia"]
    column_searchable_list = ["ma_sach","ten_sach"]
    form_excluded_columns = ["chi_tiet_phieu_nhap", "chi_tiet_don_hang", "chi_tiet_hoa_don"]

class TheLoaiView(ModelView):
    column_list = ["ma_the_loai", "ten_the_loai"]
    column_searchable_list = ["ma_the_loai", "ten_the_loai"]
    form_excluded_columns = ["ma_sach"]
    form_columns = ["ten_the_loai"]

class TacGiaView(ModelView):
    column_list = ["ma_tac_gia","ten_tac_gia"]
    column_searchable_list = ["ma_tac_gia","ten_tac_gia"]
    form_columns = ["ten_tac_gia"]

class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/login')

class FrequencyView(MyView):
    @expose("/")
    def index(self):
        selected_month = request.args.get("month")
        selected_month_onl = request.args.get("month_onl")
        action=request.args.get("action")
        # xử lý giá trị
        if selected_month == "None":
            selected_month = None

        if selected_month_onl=="None":
            selected_month_onl=None


        if not selected_month:
            year, month_value = (0, 0)
        if not selected_month_onl:
            year_onl, month_value_onl = (0, 0)


        if selected_month:
            year, month_value = map(int, selected_month.split('-'))

        if selected_month_onl:
            year_onl, month_value_onl = map(int, selected_month_onl.split('-'))

        stats = dao.fre_month(month=month_value, year=year)
        stats_onl = dao.fre_month_onl(month=month_value_onl, year=year_onl)
        if action == "export":
            return dao.export_csv(stats, f"tan_suat_cua_hang_{selected_month}.csv",type="fre")
        if action == "export_onl":
            return dao.export_csv(stats_onl, f"tan_suat_online_{selected_month_onl}.csv",type="fre")

        return self.render(
            'admin/frequency.html',
            stats=stats,
            stats_onl=stats_onl,
            selected_month=selected_month,
            selected_month_onl=selected_month_onl
        )

class RevenueView(MyView):
    @expose("/")
    def index(self):
        selected_month = request.args.get("month")
        selected_month_onl = request.args.get("month_onl")
        action = request.args.get("action")
        # xử lý giá trị
        if selected_month == "None":
            selected_month = None

        if selected_month_onl == "None":
            selected_month_onl = None

        if not selected_month:
            year, month_value = (0, 0)
        if not selected_month_onl:
            year_onl, month_value_onl = (0, 0)

        if selected_month:
            year, month_value = map(int, selected_month.split('-'))

        if selected_month_onl:
            year_onl, month_value_onl = map(int, selected_month_onl.split('-'))

        stats = dao.revenue_stats(month=month_value, year=year)
        stats_onl = dao.revenue_stats_onl(month=month_value_onl, year=year_onl)
        if action == "export":
            return dao.export_csv(stats, f"doanh_thu_cua_hang_{selected_month}.csv",type="revenue")
        if action == "export_onl":
            return dao.export_csv(stats_onl, f"doanh_thu_online_{selected_month_onl}.csv",type="revenue")
        print(type(stats))
        return self.render(
        'admin/revenue.html',
            stats=stats,
            stats_onl=stats_onl,
            selected_month=selected_month,
            selected_month_onl=selected_month_onl
        )

class ConFigView(MyView):
    @expose("/",methods=["get", "post"])
    def index(self):
        if request.method == "POST":
            ids =request.form.getlist("id[]")
            so_luong = request.form.getlist("quantity[]")
            for i, id in enumerate(ids):
                new_quantity = so_luong[i]
                dao.get_config_by_id(id).update_value(int(new_quantity))
            return  self.render('admin/config.html',configs=dao.config())
        return self.render('admin/config.html',configs=dao.config())



admin.add_view(UserView(User,db.session))
admin.add_view(SachView(Sach,db.session))
admin.add_view(TheLoaiView(TheLoai, db.session))
admin.add_view(TacGiaView(TacGia,db.session))
admin.add_view(FrequencyView(name='Tần suất bán'))
admin.add_view(RevenueView(name='Doanh thu'))
admin.add_view(ConFigView(name='Quy định'))
admin.add_view(LogoutView(name='Đăng xuất'))