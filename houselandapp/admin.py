import math
from math import ceil
from flask_mail import Message
from flask_admin.contrib.sqla import ModelView
from houselandapp import app, dao, db, mail, socketio
from flask import redirect, url_for, jsonify, request, abort, flash
from flask_login import current_user, logout_user
from flask_admin import Admin, expose, BaseView, AdminIndexView
from models import UserRoleEnum, Posts, Reports, User
from flask_socketio import emit
import random, string
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from gettext import gettext
from datetime import datetime

class AuthenticatedIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


@app.route("/api/stats_post/<int:month>", methods=["POST"])
def stats_posts(month):
    try:
        result = dao.statistics(month)
        data = []
        for r in result:
            data.append({
                'param_1': r[0],
                'param_2': r[1]
            })
        return jsonify({
            "status": 200,
            "message": "successful",
            "data": data
        })
    except:
        return jsonify({
            "status": 500,
            "message": "failed",
            "data": []
        })


@app.route("/api/status_posts/<string:status>", methods=["POST"])
def json_posts(status):
    try:
        result = dao.load_posts_by_status(status)
        data = []
        for r in result:
            data.append({
                'id': r[0],
                'title': r[1],
                'created_date': r[2],
                'updated_date': r[3],
                'status': r[4].value,
                'avatar': r[5],
                'username': r[6]
            })
        return jsonify({
            "status": 200,
            "message": "successful",
            "data": data
        })
    except:
        return jsonify({
            "status": 500,
            "message": "failed",
            "data": []
        })


def send_message(email, subject, msg_body, name):
    msg = Message(subject=subject,
                  sender='afforda2002@gmail.com', recipients=[email])
    msg.body = "Xin chào, " + name + ".\n\n" + msg_body + "\n\nTrân trọng!"
    mail.send(msg)


@app.route("/api/handle_report/<int:user_report_id>/<string:action_name>/<int:post_id>", methods=["POST"])
def handle_report_by_id(user_report_id, action_name, post_id):
    try:
        user = dao.get_user_by_post_id(post_id)
        post = dao.get_post_by_id(post_id)
        if action_name == "hide":
            dao.hide_post(post_id)
            dao.handle_report(user_report_id, post_id, "Đã ẩn bài viết")
            subject = "[Thông báo] Bài viết của bạn đã bị ẩn!"
            msg_body = "Chúng tôi đã nhận báo cáo rằng bài viết của bạn bị vi phạm về nội dung.\n" \
                       "Sau quá trình xem xét, Afforda rất tiếc phải thông báo rằng bài viết của bạn đã bị ẩn do có nội dung không hợp lệ!\nChúng tôi rất tiếc về việc này!\n" \
                       f"Để biết thêm chi tiết vui lòng liên hệ qua email này hoặc hotline 0399411749!\n\nThông tin bài viết:\nTiêu đề: \"{post.title}\" \nMã bài viết: {post.id}"
            send_message(user.email, subject, msg_body, user.name)
        if action_name == "recovery":
            dao.recovery_post(post_id)
            dao.handle_report(user_report_id, post_id, "Đã khôi phục")
            subject = "[Thông báo] Bài viết của bạn đã được khôi phục!"
            msg_body = "Chúng tôi đã nhận báo cáo rằng bài viết của bạn bị vi phạm về nội dung.\n" \
                       "Sau khi xem xét, Afforda rất hân hạnh thông báo rằng bài viết của bạn đã được khôi phục do báo cáo sai!\n" \
                       f"Chúng tôi xin lỗi vì sự bất tiện này!\n\nThông tin bài viết:\nTiêu đề: \"{post.title}\" \nMã bài viết: {post.id}"
            send_message(user.email, subject, msg_body, user.name)
        return jsonify({
            "status": 200,
            "message": "successful",
            "id": post_id
        })
    except Exception as err:
        print(err)
        return jsonify({
            "status": 500,
            "message": "error",
            "id": post_id
        })


@app.route("/api/action_post/<string:action_name>/<int:post_id>", methods=["POST"])
def action_posts(action_name, post_id):
    try:
        user = dao.get_user_by_post_id(post_id)
        post = dao.get_post_by_id(post_id)
        if action_name == "accept":
            dao.accept_post(post_id)
            subject = "[Thông báo] Bài viết của bạn đã  được duyệt!"
            msg_body = f"Sau khi xem xét, Afforda rất hân hạnh thông báo rằng bài viết của bạn đã được duyệt!\n\nThông tin bài viết:\nTiêu đề: \"{post.title}\" \nMã bài viết: {post.id}"
            send_message(user.email, subject, msg_body, user.name)
        if action_name == "hide":
            dao.hide_post(post_id)
            subject = "[Thông báo] Bài viết của bạn đã bị ẩn!"
            msg_body = "Chúng tôi đã nhận báo cáo rằng bài viết của bạn bị vi phạm về nội dung.\n" \
                       "Sau quá trình xem xét, Afforda rất tiếc phải thông báo rằng bài viết của bạn đã bị ẩn do có nội dung không hợp lệ!\nChúng tôi rất tiếc về việc này!\n" \
                       f"Để biết thêm chi tiết vui lòng liên hệ qua email này hoặc hotline 0399411749!\n\nThông tin bài viết:\nTiêu đề: \"{post.title}\" \nMã bài viết: {post.id}"
            send_message(user.email, subject, msg_body, user.name)

        if action_name == "delete":
            dao.remove_post(post_id)
            subject = "[Thông báo] Bài viết của bạn đã bị xóa!"
            msg_body = "Chúng tôi đã nhận báo cáo rằng bài viết của bạn bị vi phạm về nội dung.\n" \
                       "Sau khi xem xét, Afforda rất tiếc phải thông báo rằng bài viết của bạn đã bị xóa vì thực sự vi phạm về nội dung!\n" \
                       f"Chúng tôi rất tiếc về việc này!\n\nThông tin bài viết:\nTiêu đề: \"{post.title}\" \nMã bài viết: {post.id}"
            send_message(user.email, subject, msg_body, user.name)
        if action_name == "recovery":
            dao.recovery_post(post_id)
            subject = "[Thông báo] Bài viết của bạn đã được khôi phục!"
            msg_body = "Chúng tôi đã nhận báo cáo rằng bài viết của bạn bị vi phạm về nội dung.\n" \
                       "Sau khi xem xét, Afforda rất hân hạnh thông báo rằng bài viết của bạn đã được khôi phục do báo cáo sai!\n" \
                       f"Chúng tôi xin lỗi vì sự bất tiện này!\n\nThông tin bài viết:\nTiêu đề: \"{post.title}\" \nMã bài viết: {post.id}"
            send_message(user.email, subject, msg_body, user.name)
        return jsonify({
            "status": 200,
            "message": "successful",
            "id": post_id
        })
    except Exception as error:
        print(error)
        return jsonify({
            "status": 500,
            "message": "error",
            "id": post_id
        })


@app.route("/api/load_user_by_user_role/<string:user_role>", methods=["POST"])
def json_users(user_role):
    try:
        result = dao.load_user_by_kw(user_role)
        data = []
        if result:
            for r in result:
                number_bad_report = dao.count_bad_report(r.id)
                data.append({
                    'id': dao.encrypt_data(str(r.id)),
                    'name': r.name,
                    'phone': r.phone,
                    'email': r.email,
                    'user_role': str(r.user_role).split(".")[-1],
                    'date_created': r.date_created,
                    'active': r.active,
                    'number_bad_report': number_bad_report
                })
            return jsonify({
                "status": 200,
                "message": "successful",
                "data": data
            })
        else:
            return jsonify({
            "status": 500,
            "message": "failed",
            "data": []
        })
    except Exception as error:
        print(error)
        return jsonify({
            "status": 500,
            "message": "failed",
            "data": []
        })


@app.route("/api/admin/action_user/<string:id>/<string:action>", methods=["POST"])
def action_users(id, action):
    if request.method == "POST":
        data = {
            "code": 400,
            'message': "Bad Request!"
        }
        user = dao.get_user_by_id(id)
        if action == "reset" and user:
            new_pass=''
            for _ in range(0,8):
                new_pass = new_pass + (random.choice(string.ascii_lowercase+string.ascii_uppercase+string.digits))
            try:
                dao.reset_password(user.phone, new_pass)
                subject = "Cập nhật mật khẩu mới cho tài khoản của bạn trên Afforda.com.vn!"
                msg_body = f"Mật khẩu mới của bạn là: {new_pass}\n\nBạn có thể đăng nhập vào Afforda.com.vn bằng số điện thoại đã đăng ký và mật khẩu mà chúng tôi cấp. \nVui lòng đổi mật khẩu và không chuyển tiếp email này!"
                send_message(user.email, subject, msg_body, user.name)
                data = {
                    "code": 200,
                    'message': "Successfully!"
                }
            except Exception as error:
                print(error)

        if action == "delete" and user:
            try:
                dao.delete_user(id)
                subject = "[Thông báo] Giải quyết yêu cầu xóa tài khoản của bạn trên Afforda.com.vn!"
                msg_body = f"Afforda.com.vn cảm ơn bạn đã đồng hành với chúng tôi trong suốt thời gian qua!\nChúng tôi rất tiếc khi phải thông báo rằng tài khoản {user.name} đã bị xóa khỏi hệ thống! \n\nKính chào và hẹn gặp lại!"
                send_message(user.email, subject, msg_body, user.name)
                data = {
                    "code": 200,
                    'message': "Successfully!"
                }
            except Exception as error:
                print(error)

        if action == "recover" and user:
            try:
                dao.recovery_user(user.id)
                subject = "[Thông báo] Giải quyết yêu cầu xóa tài khoản của bạn trên Afforda.com.vn!"
                msg_body = f"Afforda.com.vn cảm ơn bạn đã tiếp tục lựa chọn Afforda!\nChúng tôi hân hạnh thông báo rằng tài khoản {user.name} đã được phục hồi! \n\nBạn có thể sử dụng các dịch vụ được cho phép trên Afforda.com.vn!"
                send_message(user.email, subject, msg_body, user.name)
                data = {
                    "code": 200,
                    'message': "Successfully!"
                }
            except Exception as error:
                print(error)        
        
        return jsonify(data)
    else:
        abort(404)        


class MyAdminView(AuthenticatedIndexView):
    @expose('/')
    def index(self):
        user_badges = dao.count_request_user()
        is_new_user = all(item == 0 for item in user_badges)
        new_chat = dao.count_new_message(current_user.id)
        stats = []
        (new_posts, all_posts) = dao.stats_post()
        (new_users, all_users, recently_user) = dao.stats_user()
        (new_reports, all_reports) = dao.stats_report()
        stats.append(new_posts)
        stats.append(all_posts)
        stats.append(new_users)
        stats.append(all_users)
        stats.append(new_reports)
        stats.append(all_reports)
        stats.append(recently_user)
        for user in dao.load_user_by_kw('restrict'):
            iden = dao.get_identifier(dao.encrypt_data(user.id))
            if iden and iden.restrict_to < datetime.now():
                dao.recovery_user(user.id)
                subject = "[Thông báo] Khôi phục quyền đăng bài viết trên Afforda.com.vn!"
                msg_body = f"Afforda.com.vn xin thông báo: Tài khoản của bạn đã khôi phục quyền đăng bài viết trên website của chúng tôi!\nRất hân hạnh khi tiếp tục hợp tác cùng nhau!"
                send_message(user.email, subject, msg_body, user.name)


        return self.render('admin/index.html', stats=stats, is_new_user=is_new_user, new_chat=new_chat)


class PostsView(AuthenticatedModelView):
    can_view_details = True
    can_create = False
    column_display_pk = True
    page_size = 8
    details_modal = True
    can_edit = False
    column_exclude_list = ['description']

    @expose('/')
    def index_view(self):      
        user_badges = dao.count_request_user()
        is_new_user = all(item == 0 for item in user_badges)
        new_chat = dao.count_new_message(current_user.id)
        stats = []
        (new_posts, all_posts) = dao.stats_post()
        (new_users, all_users, recently_user) = dao.stats_user()
        (new_reports, all_reports) = dao.stats_report()
        stats.append(new_posts)
        stats.append(all_posts)
        stats.append(new_users)
        stats.append(all_users)
        stats.append(new_reports)

        return self.render(
            'admin/posts.html', new_chat=new_chat, is_new_user=is_new_user, stats=stats
        )


class ReportView(AuthenticatedModelView):
    can_view_details = True
    can_create = False
    column_display_pk = True
    page_size = 8
    details_modal = False
    can_edit = False
    column_hide_backrefs = False
    can_delete = False
    column_list = ('post_id', 'user_id', 'content', 'date_report', 'status', 'date_handle')
    column_sortable_list = ['date_report', 'date_handle', 'status','post_id', 'user_id']
    

    @expose('/details/')
    def details_view(self):
        return_url = get_redirect_target() or self.get_url('.index_view')
        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)
        
        model = self.get_one(id)
        if model is None:
            flash(gettext('Record does not exist.'), 'error')
            return redirect(return_url)
        return redirect(f"/posts/{model.post_id}")


class UserView(AuthenticatedModelView):
    can_view_details = True
    can_create = False
    column_display_pk = True
    page_size = 8
    details_modal = True
    can_edit = True
    column_hide_backrefs = False
    can_delete = True
    column_exclude_list = ['password']  

    @expose('/')
    def index_view(self):
        new_requests = dao.count_request_user()         
        user_badges = dao.count_request_user()
        is_new_user = all(item == 0 for item in user_badges)
        new_chat = dao.count_new_message(current_user.id)
        stats = []
        (new_posts, all_posts) = dao.stats_post()
        (new_users, all_users, recently_user) = dao.stats_user()
        (new_reports, all_reports) = dao.stats_report()
        stats.append(new_posts)
        stats.append(all_posts)
        stats.append(new_users)
        stats.append(all_users)
        stats.append(new_reports)

        data = dao.load_user_by_kw()
        return self.render(
            'admin/user.html',
            data=data, new_requests=new_requests, is_new_user=is_new_user, stats=stats, new_chat=new_chat
        )


class ChatVew(AuthenticatedView):
    @expose('/')
    def index(self):
        return redirect(url_for('chat'))


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect(url_for("login_register"))


class ExitView(AuthenticatedView):
    @expose('/')
    def index(self):
        return redirect(url_for('home'))


admin = Admin(app=app, name='QUẢN LÝ BÀI VIẾT', template_mode='bootstrap4', index_view=MyAdminView())
admin.add_view(UserView(User, db.session, name="Tài khoản", endpoint="users"))
admin.add_view(PostsView(Posts, db.session, name="Tin đăng", endpoint="posts"))
admin.add_view(ReportView(Reports, db.session, name="Báo cáo", endpoint="report"))
admin.add_view(ChatVew(name="Tin nhắn"))
admin.add_view(LogoutView(name="Đăng xuất"))
admin.add_view(ExitView(name="Thoát"))


@socketio.on('handle_notify')
def handle_notify(data):
    if data['type'] == 'report':
        (new_reports, _) = dao.stats_report()
        emit('handle_notify', {
            'type': data['type'],
            'new_reports': new_reports
        }, broadcast=True)
    elif data['type'] == 'report':
        (new_posts, _) = dao.stats_post()
        emit('handle_notify', {
            'type': data['type'],
            'new_posts': new_posts
        }, broadcast=True)
    elif data['type'] == 'register_user':
        (new_users, _, _) = dao.stats_user()
        emit('handle_notify', {
            'type': data['type'],
            'new_users': new_users
        }, broadcast=True)
    else:
        emit('handle_notify', {
            'type': data['type']
        }, broadcast=True)

