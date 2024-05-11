from houselandapp import app, mail, dao, login, admin, oauth, es, index_name
import math
from datetime import datetime

from flask import render_template, request, redirect, jsonify, url_for, session, abort
from flask_mail import Mail, Message
from flask_socketio import send, emit, join_room, leave_room
import requests
from houselandapp import socketio
from models import UserRoleEnum, LogActionEnum, PostsStatusEnum
from flask_login import login_user, logout_user, login_required, current_user
import hashlib
from functools import wraps
from random import *
import re
import http, json

otp = randint(000000, 999999)
parameters = {
    'issales': 'true',
    'q': '',
    'address': 'Toàn quốc',
    'min_price': 0,
    'max_price': 300
}

def check_password(string):
    return re.fullmatch(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$", string)


def check_email(string):
    return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', string)


def generate_otp():
    return randint(100000, 999999)


def standardize_phone(phone_number):
    return '84'+ str(phone_number[1:])


def send_otp(phone, code):    
    formatted_phone_number = standardize_phone(phone)
    conn = http.client.HTTPSConnection("k283m1.api.infobip.com")
    payload = json.dumps({
        "messages": [
            {
                "destinations": [{"to":formatted_phone_number}],
                "from": "ServiceSMS",
                "text": f"Welcome to Afforda Website!\nYour verification code is {code}."
            }
        ]
    })
    headers = {
        'Authorization': 'App 5c73e3b108588250107a8e879d138321-4bf7b1eb-b601-4407-bd41-bb86e550f776',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    conn.request("POST", "/sms/2/text/advanced", payload, headers)
    return conn.getresponse().status


def send_message(email, name, otp_code=None):
    msg = Message(subject='OTP Code Verification From Afforda Website',
                sender='afforda2002@gmail.com', recipients=[email])
    if otp_code:
        msg.body = "Hello, " + name + ".\n\nYour OTP code: " + str(otp_code)
    else:
        msg.body = "Hello, " + name + ".\n\nYour OTP code: " + str(otp)
        
    mail.send(msg)


@app.route("/api/register/<string:phone>", methods=["POST"])
def api_get_opt(phone):
    """
        Function is step 1 of Register process: Get OTP code
    """
    data = request.json
    
    phone_number = phone      
    password = data.get('password')      
    re_password = data.get('re_password')   
    is_valid = check_password(password)
    is_exists_user = dao.find_user(phone_number)
    if is_valid and password == re_password and not is_exists_user:   
        otp_code = generate_otp()        
        # print(otp_code)
        status = send_otp(phone_number, otp_code)
        # status = 200
        
        if status == 200:
            status = dao.register(phone_number, password, str(otp_code))      
    elif is_exists_user:
        status = 401
    else:
        status = 402
    response_data = {'phone_number': phone_number, "password":password, "re_password":re_password, "status": status}
    return jsonify(response_data)


@app.route("/api/verify_otp_code/<string:action>", methods=["POST"])
def verify_otp(action):
    """
        Function is step 2 of Register process: Verify OTP code
    """
    if action == "back":
        phone = request.json.get('phone-number')
        user = dao.get_user_by_username(phone)
    if action == "cancel":        
        email = request.json.get('email')
        user = dao.get_user_by_email(email)
        
    name = request.json.get('name')
    typed_otp = request.json.get('typed-otp')
    typed_otp = dao.hash_kw(typed_otp)

    if user and (typed_otp == user.otp_code):
        if action == "back":
            return jsonify({
                "status": 200,
                "message": "successful",        
                "user_id": user.id
            })
        if action == "cancel":
            try:
                dao.final_register(email, name)
                return jsonify({
                    "status": 201,
                    "message": "successful_1",        
                    "user_id": user.id
                })
            except Exception as error:
                print(error)                
    
    return jsonify({
            "status": 400,
            "message": "failed",
            "user_id": None
        })
    

@app.route("/api/register", methods=["POST"])
def api_register():
    """
        Function is step 3 of Register process: Fill information
    """
    err_msg = dao.get_status_by_id(-1)
    name = request.json.get('name') if 'name' in request.json else None
    phone = request.json.get('phone') if 'phone' in request.json else None
    email = request.json.get('email') if 'email' in request.json else None
    city = request.json.get('city') if 'city' in request.json else None
    
    if city == "":
        err_msg = dao.get_status_by_id(13)
        return jsonify({
            "status": 400,
            "message": err_msg
        })
    if not email:
        err_msg = dao.get_status_by_id(6)
        return jsonify({
            "status": 400,
            "message": err_msg
        })
    if email:
        user = dao.get_user_by_email(email)
        if user and user.active:
            err_msg = dao.get_status_by_id(14)
            return jsonify({
                "status": 400,
                "message": err_msg
            })
    if name is None or name == "":
        err_msg = dao.get_status_by_id(5)
        return jsonify({
            "status": 400,
            "message": err_msg
        })
    if len(name) > 40:
        err_msg = dao.get_status_by_id(1)
        return jsonify({
            "status": 400,
            "message": err_msg
        })
    if phone is None or len(phone) != 10:
        err_msg = dao.get_status_by_id(2)
        return jsonify({
            "status": 400,
            "message": err_msg
        })
    
    try:
        otp_code = generate_otp()
        dao.update_user(phone, name, email, city, otp_code)        
        send_message(email, name, otp_code)
        return jsonify({
            "status": 200,
            "message": "successful"
        })
    except Exception as error:
        print(error)
        err_msg = dao.get_status_by_id(9)
        return jsonify({
                "status": 400,
                "message": err_msg
            })
    

def annonymous_user(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect("/")

        return f(*args, **kwargs)

    return decorated_func


@annonymous_user
@app.route("/login_register", methods=["POST", "GET"])
def login_register():
    """
        Function login to website
    """
    err_msg = dao.get_status_by_id(-1)
    if request.method == 'POST':
        if 'cancel' in request.form:
            user = dao.get_user_by_username(request.form['r_phone'])
            if user and not user.active:
                dao.delete_user(user.id)

        if 'login' in request.form:
            username = request.form['username']
            password = request.form['password']

            user = dao.auth_user(username, password)
            if user and user.active:
                dao.set_login(user)
                login_user(user=user)
                url_next = request.args.get('next')
                if not url_next and user.user_role == UserRoleEnum.ADMIN:
                    return redirect('/admin')

                return redirect(url_next if url_next else '/')
            else:
                err_msg = dao.get_status_by_id(10)

    return render_template('login.html', err_msg=err_msg)


@app.route('/login/google')
def google_login():
    """
        Function login to website using google account
    """
    google = oauth.create_client('google')
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/login/google_authorize')
def google_authorize():
    try:
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        u_email = user_info.email
        user = dao.get_user_by_email(u_email)        
        if user and user.active and (user.password or user.user_role == UserRoleEnum.WAITING_DELETE):
            err_msg = dao.get_status_by_id(14)
            return render_template("login.html", err_msg=err_msg)
        if not user or not user.phone:
            dao.register_by_email(user_info['name'], u_email, user_info['picture'])
            return redirect(url_for("verify_phone", email=u_email))
        
        if user and user.active and user.phone:
            dao.set_login(user)
            login_user(user=user)
            url_next = request.args.get('next')
            return redirect(url_next if url_next else '/')
        

    except Exception as error:
        print(error)    
    return redirect(url_for('login_register'))


@app.route("/login/google_authorize/verify_phone", methods=["GET", "POST"])
def verify_phone():
    err_msg = dao.get_status_by_id(-1)
    email = request.args.get("email")
    user = dao.get_user_by_email(email)
    if request.method == "POST":
        if "phone" in request.form:
            phone = request.form['phone']
            if len(phone) == 10 and phone.isdigit():
                user_t = dao.get_user_by_username(phone)
                if not user_t:     
                    otp_code = generate_otp()
                    try:
                        dao.update_otp_by_email(email, otp_code, phone)
                        send_otp(phone, otp_code)
                        # print(otp_code)
                    except Exception as error:
                        err_msg = dao.get_status_by_id(9)
                        print(error)
                
                else:       
                    err_msg = dao.get_status_by_id(8)
            else:
                err_msg = dao.get_status_by_id(2)
        elif 'ip_1' in request.form:
            otp_string = ''
            for i in range(1, 7):
                f_str = 'ip_' + str(i)
                otp_string += request.form[f_str]
            otp_string = dao.hash_kw(otp_string)
            if user and not user.active and user.otp_code == otp_string:
                try: 
                    dao.final_register(email)
                    user = dao.get_user_by_email(email)

                    dao.set_login(user)
                    login_user(user=user)
                    return redirect("/")
                except Exception as err:
                    print(err)
                    err_msg = dao.get_status_by_id(9)
            else:
                    err_msg = dao.get_status_by_id(9)

    return render_template("verify_contact.html", user=user, err_msg=err_msg)


@app.route("/login_register/forgot_password/forgot_password_otp/<string:phone>", methods=["POST", "GET"])
def forgot_password_otp(phone):
    """
        Function verify OTP code when reset password
    """
    err_msg = -1
    if request.method == 'POST':
        user = dao.get_user_by_username(phone)
        otp_string = ''
        for i in range(1, 7):
            f_str = 'ip_' + str(i)
            otp_string += request.form[f_str]
        otp_string = dao.hash_kw(otp_string)
        if user and user.active and user.otp_code == otp_string:
            user = dao.read_json_file(f'{app.root_path}/data/reset_password.json')
            try:
                dao.reset_password(username=user['username'],
                                   new_password=user['password'])
            except:
                err_msg = -2
            else:
                return redirect(url_for('login_register'))
        else:
            err_msg = 0

    return render_template('otpVerification.html', err_msg=err_msg)


@app.route("/login_register/forgot_password", methods=["POST", "GET"])
def forgot_password():
    """
        Function reset password
    """
    err_msg = -1
    if request.method == 'POST':
        phone = request.form['username']
        password = request.form['password']
        confirm_password = request.form['re_password']
        is_valid = check_password(password)
        user = dao.get_user_by_username(phone)
        if password.__eq__(confirm_password) and user and user.active and is_valid:
            dao.write_json_file(f'{app.root_path}/data/reset_password.json', {
                'username': phone,
                'password': password
            })
            otp = generate_otp()            
            status = send_otp(phone, otp)
            if status == 200:
                try:
                    dao.update_otp(phone, otp)
                    return redirect(url_for('forgot_password_otp', phone=phone))
                except:
                    err_msg = -4
            else:
                err_msg = -4   
        elif user is None:
            err_msg = -2
        elif not password.__eq__(confirm_password):
            err_msg = -3
        elif not is_valid :
            err_msg = -5
    return render_template('forgot.html', err_msg=err_msg)


@app.route("/logout")
def logout_my_user():
    """
        Function logout user
    """
    logout_user()
    return redirect('/login_register')


@login_required
@app.route("/profile/<string:user_id>", methods=["POST", "GET"])
def profile(user_id):
    user = dao.get_user_by_id(user_id)
    if user:
        posts = []
        saved_posts = []
        err_msg = 0
        if request.method == "POST":
            if "delete" in request.form:
                id = request.form['delete']
                try:
                    dao.remove_post(id)
                    err_msg = 1
                except:
                    err_msg = -1
            if "remove" in request.form:
                id = request.form['remove']
                try:
                    dao.delete_saved_post(id, user.id)
                    err_msg = 1
                except:
                    err_msg = -1
            if 'remove_viewed' in request.form:
                id = request.form['remove_viewed']
                try:
                    dao.delete_viewed_post(id, user.id)
                    err_msg = 1
                except Exception as err:
                    print(err)
                    err_msg = -1
            

        if user:
            posts = dao.load_posts_by_status_v2(user_id=user.id)
            for l in dao.get_logs(user.id, LogActionEnum.SAVED):
                saved_posts.append(dao.get_post_by_id(l.post_id))
            waiting_posts = dao.load_posts_by_status_v2(PostsStatusEnum.WAITING, user_id=current_user.id)
            expired_posts = dao.load_posts_by_status_v2(PostsStatusEnum.EXPIRED, user_id=current_user.id)
            viewed_list = []
            for log in dao.get_logs(user.id, LogActionEnum.VIEW):
                p_log = dao.get_post_by_id(log.post_id)
                if not p_log in viewed_list:
                    viewed_list.append(p_log)
            for p in posts:
                p.address = p.address.replace("~", ",")
            for p in saved_posts:
                p.address = p.address.replace("~", ",")
            for p in waiting_posts:
                p.address = p.address.replace("~", ",")
            for p in expired_posts:
                p.address = p.address.replace("~", ",")
        else:
            return abort(404)
        rating = 0
        user_reviews = dao.load_publisher_reviews(user.id)
        if user_reviews:
            for r in user_reviews:
                rating = rating + r.rating
            rating = float(rating)/float(user_reviews.__len__())
        return render_template("profile.html", posts=posts, user_id=user_id, expired_posts=expired_posts,
                            user=user, waiting_posts=waiting_posts, viewed_list=viewed_list,
                            saved_posts=saved_posts, err_msg=err_msg, rating=rating)
    return abort(404)


@app.route("/profile/edit_profile/verify_contact", methods=["POST", "GET"])
def verify_contact():
    """
        Function verify OTP code when edit profile
    """
    err_msg = -1
    if request.method == 'POST' and "verify" in request.form:
        value = request.args.get('value',None)
        type = request.args.get('type',None)
        id = request.args.get('id',None)
        user = dao.get_user_by_id(id)
        otp_string = ''
        for i in range(1, 7):
            f_str = 'ip_' + str(i)
            otp_string += request.form[f_str]
        
        if user and user.otp_code == dao.hash_kw(otp_string) and value and type:
            try:
                if type == "email":                    
                    dao.update_user_contact(id, value, None)
                if type == "phone":                    
                    dao.update_user_contact(id, None, value)
                url = f"/profile/edit_profile/{id}"
                return redirect(url)
            except Exception as error:
                print(error)
                err_msg = -2
        else:
            err_msg = 0

    return render_template('verify_contact.html', err_msg=err_msg)


@login_required
@app.route("/profile/edit_profile/<string:user_id>", methods=["POST", "GET"])
def edit_profile(user_id):
    if current_user.user_role == UserRoleEnum.ADMIN or str(current_user.id) == dao.decrypt_data(user_id):
        ifull_name = None
        iid_code = None
        status = dao.get_status_by_id(-1)
        user = dao.get_user_by_id(user_id)
        id = dao.hash_kw(user.id)

        if request.method == "POST":
            if "delete-avatar" in request.form:
                status = dao.get_status_by_id(-1)
                try:
                    dao.change_avatar(user_id)
                    status = dao.get_status_by_id(15)
                except:
                    status = dao.get_status_by_id(9)
            if "edit-avatar" in request.files:
                status = dao.get_status_by_id(-1)
                try:
                    image = request.files.get('edit-avatar')
                    dao.change_avatar(user_id, image)
                    status = dao.get_status_by_id(15)
                except Exception as error:
                    print(error)
                    status = dao.get_status_by_id(9)
            if "change-info" in request.form:
                status = dao.get_status_by_id(-1)
                name = request.form['name'] if 'name' in request.form else None
                description = request.form['description'] if 'description' in request.form else None
                city = request.form['province'] if 'province' in request.form else None
                if name is None or name == "":
                    status=dao.get_status_by_id(5)
                else:
                    try:
                        dao.update_user_info(user_id, name, description, city)
                        status=dao.get_status_by_id(15)
                    except Exception as error:
                        print(error)
                        status = dao.get_status_by_id(9)
            if "change-contact" in request.form:
                status = dao.get_status_by_id(-1)
                email = request.form['email'] if 'email' in request.form else None
                phone = request.form['phone'] if 'phone' in request.form else None
                            
                if phone != user.phone:
                    if len(phone) == 10 and not dao.get_user_by_username(phone):
                        otp_code = generate_otp()
                        dao.update_otp_by_email(user.email, otp_code)
                        send_otp(phone, otp_code)
                        return redirect(url_for('verify_contact', name=user.name, type='phone', id=user_id, value=phone))
                    elif len(phone) != 10:
                        status=dao.get_status_by_id(2)
                        return render_template("edit_profile.html", status=status, id=id, user_role=str(user.user_role))
                    elif dao.get_user_by_username(phone):
                        status=dao.get_status_by_id(8)
                        return render_template("edit_profile.html", status=status, id=id, user_role=str(user.user_role))
                if email != user.email:
                    if check_email(email) and not dao.get_user_by_email(email):
                        otp_code = generate_otp()
                        dao.update_otp(user.phone, otp_code)
                        send_message(email, user.name, otp_code)                    
                        return redirect(url_for('verify_contact', name=user.name, type='email', id=user_id, value=email))
                    if not check_email(email):
                        status=dao.get_status_by_id(6)
                        return render_template("edit_profile.html", status=status, id=id, user_role=str(user.user_role))
                    if dao.get_user_by_email(email):
                        status=dao.get_status_by_id(14)
                        return render_template("edit_profile.html", status=status, id=id, user_role=str(user.user_role))
            if "change-password" in request.form:
                password = request.form['old-password'] if "old-password" in request.form else None
                new_password = request.form['new-password'] if "new-password" in request.form else None
                re_new_password = request.form['re-new-password'] if "re-new-password" in request.form else None

                if password and new_password and re_new_password:
                    pwd = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
                    if pwd == user.password and check_password(new_password) and new_password==re_new_password:
                        try:
                            dao.update_password(user.id, new_password)
                            status=dao.get_status_by_id(15)
                        except Exception as error:
                            print(error)
                            status = dao.get_status_by_id(9)
                    elif pwd != user.password:
                        status = dao.get_status_by_id(16)
                    elif not check_password(new_password):
                        status = dao.get_status_by_id(17)  
                    elif new_password != re_new_password:
                        status = dao.get_status_by_id(18)    
            if "register" in request.form:
                selfie = request.files.get("selfie-image") if "selfie-image" in request.files else None
                front = request.files.get("front-id-image") if "front-id-image" in request.files else None
                back = request.files.get("back-id-image") if "back-id-image" in request.files else None
                agree = request.form['agree'] if 'agree' in request.form else None
                if user.email and user.phone:
                    if not agree:
                        status = dao.get_status_by_id(24)
                    elif not selfie:
                        status = dao.get_status_by_id(19)
                    elif not front:
                        status = dao.get_status_by_id(20)
                    elif not back:
                        status = dao.get_status_by_id(21)
                    else:
                        try:
                            front_path = dao.generate_path(user.id, front.filename, "F")
                            front.save(front_path)                
                            back_path = dao.generate_path(user.id, back.filename, "B")
                            back.save(back_path)
                            selfie_path = dao.generate_path(user.id, selfie.filename, "S")
                            selfie.save(selfie_path)
                                                
                            front_data = dao.id_recognize(front_path)
                            if front_data['errorCode'] != 0:
                                status = dao.get_status_by_id(20)
                            else:
                                back_data = dao.id_recognize(back_path)
                                if back_data['errorCode'] != 0:
                                    status = dao.get_status_by_id(21)
                                else:                                        
                                    check_id = dao.idmatch(front_data, back_data)
                                    if check_id == -1:
                                        status = dao.get_status_by_id(22)
                                    else:                
                                        is_match = dao.facematch(selfie_path,front_path)
                                        print(is_match)
                                        if not is_match['code'] == '200' or is_match['data']['similarity'] < 80:
                                            status = dao.get_status_by_id(19)
                                        elif is_match['code'] == '200' and is_match['data']['similarity'] >= 80:
                                            full_name = front_data['data'][0]['name']
                                            dob =  datetime.strptime(front_data['data'][0]['dob'], f"%d/%m/%Y").strftime('%Y-%m-%d')
                                            address = front_data['data'][0]['address']
                                            id_code = front_data['data'][0]['id']
                                            register_date = datetime.strptime(back_data['data'][0]['issue_date'], f"%d/%m/%Y").strftime('%Y-%m-%d')
                                            if front_data['data'][0]['type'].__eq__("chip_front"):
                                                gender = front_data['data'][0]['sex']
                                                at = 'CỤC TRƯỞNG CỤC CẢNH SÁT QUẢN LÝ HÀNH CHÍNH VỀ TRẬT TỰ XÃ HỘI'
                                                expire_at = datetime.strptime(front_data['data'][0]['doe'], f"%d/%m/%Y").strftime('%Y-%m-%d')
                                            else:
                                                gender = ''
                                                at = ''
                                                r_date = datetime.strptime(register_date, f'%Y-%m-%d')
                                                expire_at = r_date.replace(year=r_date.year+15).strftime('%Y-%m-%d')
                                            code = dao.register_broker(user_id)
                                            if code == 23:
                                                code = dao.add_identifier(user.id, id_code, full_name, gender, dob, address, register_date, at, expire_at)
                                            status = dao.get_status_by_id(code)
                        except Exception as error:
                            print(error)       
                            dao.recovery_user(user.id)
                            status = dao.get_status_by_id(9) 
                else:
                    status = dao.get_status_by_id(25)
            if "cancel" in request.form:
                try:
                    dao.remove_id_image(user.id)
                    status = dao.get_status_by_id(27)
                    subject = "[Thông báo] Kết quả đăng ký trở thành nhà môi giới trên Afforda.com.vn!"
                    msg_body = "Afforda.com.vn rất tiếc vì hồ sơ của bạn không hợp lệ!\nNếu muốn biết thêm chi tiết vui lòng liên hệ hotline 0399411749!"
                    admin.send_message(user.email, subject, msg_body, full_name)
                except Exception as error:
                    print(error)
                    status = dao.get_status_by_id(9)
            if "accept" in request.form:
                full_name = request.form["r_name"] if 'r_name' in request.form else None
                gender = request.form["r_gender"] if 'r_gender' in request.form else None
                dob = request.form["r_dob"] if 'r_dob' in request.form else None
                address = request.form["r_address"] if 'r_address' in request.form else None
                id_code = request.form["r_id_code"] if 'r_id_code' in request.form else None
                register_date = request.form["r_register_date"] if 'r_register_date' in request.form else None
                expire_at = request.form["r_expire_date"] if 'r_expire_date' in request.form else None
                at = request.form["r_at"] if 'r_at' in request.form else None
                genders = ['Nam', 'Nữ']

                if full_name and gender.strip() in genders \
                    and dao.is_datetime(dob) and address \
                    and id_code and dao.is_datetime(register_date) \
                    and dao.is_datetime(expire_at) and at:
                    try:
                        dao.edit_identifier(user_id, full_name, gender, dob, id_code, address, register_date, expire_at, at)
                        subject = "[Thông báo] Kết quả đăng ký trở thành nhà môi giới trên Afforda.com.vn!"
                        msg_body = "Afforda.com.vn chúc mừng bạn đã trở thành nhà môi giới trên website của chúng tôi!\nKể từ bây giờ bạn có thể đăng các bản tin trên Afforda.com.vn!"
                        admin.send_message(user.email, subject, msg_body, full_name)
                        
                    except Exception as error:
                        print(error)
            if 'restrict' in request.form:
                restrict_from = request.form.get('start', None)
                restrict_to = request.form.get('end', None)
                if restrict_from and restrict_to:                    
                    start = datetime.strptime(restrict_from, "%Y-%m-%dT%H:%M")
                    end = datetime.strptime(restrict_to, "%Y-%m-%dT%H:%M")
                    if (end - start).total_seconds() < 0:
                        status = dao.get_status_by_id(50)
                    else:
                        try:
                            dao.restrict_user(user.id, restrict_from, restrict_to)
                            status = dao.get_status_by_id(49)
                            new_user = dao.get_user_by_id(user_id)
                            if new_user.user_role == UserRoleEnum.RESTRICTED:
                                subject = "[Thông báo] Tướt quyền đăng bài viết ngắn hạn trên Afforda.com.vn!"
                                msg_body = f"Afforda.com.vn rất tiếc phải thông báo rằng: Tài khoản của bạn đã bị cấm đăng bài từ thời điểm {start} đến thời điểm {end} trên website của chúng tôi!Sau khoảng thời gian trên tài khoản của bạn sẽ được khôi phục!\nVì chúng tôi đã nhận nhiều báo cáo về các bài viết mà tài khoản của bạn đăng tải!"
                            else:
                                subject = "[Thông báo] Khôi phục quyền đăng bài viết trên Afforda.com.vn!"
                                msg_body = f"Afforda.com.vn xin thông báo: Tài khoản của bạn đã khôi phục quyền đăng bài viết trên website của chúng tôi!\nRất hân hạnh khi tiếp tục hợp tác cùng nhau!"
                            admin.send_message(user.email, subject, msg_body, user.name)
                        except Exception as err:
                            print(err)
                            status = dao.get_status_by_id(9)

        identifier = dao.get_identifier(user_id)
        if identifier:
            ifull_name = dao.decrypt_data_no2(identifier.full_name)
            iid_code = dao.decrypt_data_no2(identifier.id_code)
            print(identifier)
        return render_template("edit_profile.html", ifull_name=ifull_name, iid_code=iid_code,
                            status=status, 
                            id=id, 
                            user_role=str(user.user_role),
                            user=user,
                            identifier=identifier)
    else:
        abort(404)


@app.route("/api/load_posts")
def load_posts():
    data = []
    (posts, len_post) = dao.load_posts(page=0)
    for p in posts:
        data.append({
            'id': p.id,
            'category': p.category.name,
            'date_update': str(p.updated_at),
            'user': {
                'name': p.user.name,
                'avatar': p.user.avatar
            },
            'address': p.address.replace("~", ","),
            'price': p.price,
            'title': p.title,
            'description': p.description,
            'area': p.area,
            'number_of_bedroom': p.bedrooms,
            'number_of_wc': p.bathrooms,
            'floor': p.floor,
            'policy': p.policy,
            'direction': p.direction,
            'furniture':p.furniture,
            'image': p.images[0].url if p.images else "https://res.cloudinary.com/doaux2ndg/image/upload/v1670076213/FlightMangement/icon-web_fgxmmq.png"
        })
                

    return jsonify(data)


@app.route("/api/load_images")
def load_image():
    data = []
    for p in dao.load_image():
        for img in p.images:
            data.append({
                'id': p.id,
                'images': {
                    'url': img.url,
                    'date_update': str(p.updated_at)
                }
            })
            break

    return jsonify(data)


@app.route("/api/load_hint_post/<int:post_id>")
def load_hint_post(post_id):
    data = []
    p = dao.get_post_by_id(post_id)
    str_array = p.address.replace("~", ",").split(", ")
    str_array.reverse()
    str_address = p.address.replace("~", ",")
    (posts, len_post) = dao.load_posts(page=0, cate_id=p.category_id, address_kw=str_address, issale=p.issales)
    post_hint_list = posts
    post_hint_len = len_post
    str_address = str_array[0] + ", " + str_array[1] + ", " + str_array[2]
    (posts, len_post) = dao.load_posts(page=0, cate_id=p.category_id, address_kw=str_address, issale=p.issales)
    post_hint_list += posts
    post_hint_len = post_hint_len + len_post
    str_address = str_array[0] + ", " + str_array[1]
    (posts, len_post) = dao.load_posts(page=0, cate_id=p.category_id, address_kw=str_address, issale=p.issales)
    post_hint_list += posts
    post_hint_len += len_post
    str_address = str_array[0]
    (posts, len_post) = dao.load_posts(page=0, cate_id=p.category_id, address_kw=str_address, issale=p.issales)
    post_hint_list += posts
    post_hint_len += len_post
    
    post_hint_list = [post for post in post_hint_list if post.id != post_id]
    post_hint_list.sort(key = lambda post: math.sqrt(math.pow((post.lat - p.lat), 2) + math.pow((post.lon - p.lon), 2)))
        
        
    for post in post_hint_list:
        data.append({
            'id': post.id,
            'address': post.address,
            'price': post.price,
            'title': post.title,
            'area': post.area,
            'image': post.images[0].url
        })
            

    return jsonify(data)


@app.route("/api/react_post/<int:post_id>", methods=["POST"])
def react_post(post_id):
    try:
        result = dao.react_post(post_id, dao.encrypt_data(current_user.id))
        return jsonify({
            "status": 200,
            "message": "successful",
            "data": {
                "post_id": post_id,
                "result": result
            }
        })
    except:
        return jsonify({
            "status": 500,
            "message": "failed",
            "data": {
                "post_id": post_id,
                "result": 0
            }
        })


@app.route("/api/report_post/<int:post_id>/<string:content>", methods=["POST"])
def report(post_id, content):
    try:
        post = dao.get_post_by_id(post_id)
        author = dao.get_user_by_id(dao.encrypt_data(post.user_id))
        dao.report(user_id=current_user.id, post_id=post_id, content=content)
        subject = "[Thông báo] Bài viết của bạn đã bị ẩn!"
        msg_body = "Chúng tôi đã nhận báo cáo rằng bài viết của bạn bị vi phạm về nội dung.\n" \
                    "Trong quá trình xem xét, Afforda rất tiếc phải thông báo rằng bài viết của bạn đã bị ẩn cho tới khi có thông báo mới!\n" \
                    f"Chúng tôi rất tiếc về việc này!\n\nThông tin bài viết:\nTiêu đề: \"{post.title}\" \nMã bài viết: {post.id}"
        msg = Message(subject=subject,
                  sender='afforda2002@gmail.com', recipients=[author.email])
        msg.body = "Xin chào, " + author.name + ".\n\n" + msg_body + "\n\nTrân trọng!"
        mail.send(msg)
        return jsonify({
            "status": 200,
            "message": "successful",
            "data": {
                "post_id": post_id
            }
        })
    except:
        return jsonify({
            "status": 500,
            "message": "failed",
            "data": {
                "post_id": post_id
            }
        })
    

@app.route("/api/category/<string:category_id>", methods=["POST"])
def api_load_category_by_id(category_id):
    data = []

    for item in dao.load_type_of_property(category_id):
        data.append({
            'category_id': item.id,
            'category_name': item.name
        })
    if data:    
        return jsonify({
            'code': 200,
            'message': 'Successfully',
            'data': data
        })
    
    return jsonify({
            'code': 400,
            'message': 'Bad Request',
            'data': []
        })


@app.route("/<string:issales>/<string:cate_id>", methods=["GET","POST"])
def category_details(issales, cate_id):
    category_detail_parameters = {
        'max_price': 0,
        'max_area': 0,
        'categories': None,
        'category_id': cate_id,
        'issale': issales,
        'category_name': None,
        'page': int(request.args.get('page', 1)),
        'sort': request.args.get('sort', None),
        'location': request.args.get('address', None),
        'min_price': request.args.get('min-price', '0'),
        'chose_max_price': request.args.get('max-price', '200'),
        'min_area': request.args.get('min-area', '0'),
        'chose_max_area': request.args.get('max-area', '200'),
        'bedrooms': request.args.get('bedrooms', '0'),
        'type_of': request.args.get('type-of', 'all')
    }

    viewed_list = []
    if current_user.is_authenticated:
        for log in dao.get_logs(current_user.id, LogActionEnum.VIEW):
            p_log = dao.get_post_by_id(log.post_id)
            if not p_log in viewed_list:
                viewed_list.append(p_log)
    results = []
    q = request.args.get('q', None)
    issale = True if issales == "sales" else False
    (category_detail_parameters['max_price'], category_detail_parameters['max_area']) = dao.query_max_price_area(issale, cate_id)
    parameters['q'] = q if q else ''
    parameters['issales'] = 'true' if issale else 'false'
    must = [{"match": {"issales": 'Mua Bán' if issale else 'Cho Thuê'}}]
    if cate_id == "all":
        category_detail_parameters['category_name'] = "Mua Bán" if issale else "Cho Thuê"
    else:
        category_detail_parameters['category_name'] = dao.get_cate_name_by_id(cate_id)
        must.append({"match":{"category": category_detail_parameters['category_name']}})

    if q:
        must.append({"multi_match": {"query": q, "fields": ["category",'type_of','title']}})
    if category_detail_parameters['location']:
        lat = float(category_detail_parameters['location'].split(" ")[0])
        lon = float(category_detail_parameters['location'].split(" ")[1])
        query = {
            "query": {
                "bool": {
                    "must": must,
                    "filter": {
                        "geo_distance": {
                            "distance": "100km", 
                            "location": {"lat": lat, "lon": lon}
                        }
                    }
                }
            },
            "sort": [
                {
                    "_geo_distance": {
                        "location": {"lat": lat, "lon": lon}, 
                        "order": "asc", 
                        "unit": "km", 
                        "mode": "min", 
                        "distance_type": "arc" 
                    }
                }
            ]
        }
    else:
        query = {
            "query": {
                "bool": {
                    "must": must
                }
            }
        }
    resp = es.search(index=index_name,body=query, size=1000)
    for hit in resp['hits']['hits']:
        results.append(hit['_source'])

    length = (len(results)) 
    
    if category_detail_parameters['sort']:
        dao.sort_list_by_field(results, category_detail_parameters['sort'])
    if category_detail_parameters['min_price'] != '0' or category_detail_parameters['chose_max_price'] != '200':
        results = dao.filter_results_by_range(results, 'price', category_detail_parameters['min_price'], 
                                              category_detail_parameters['chose_max_price'], 
                                              category_detail_parameters['max_price'])
    if category_detail_parameters['min_area'] != '0' or category_detail_parameters['chose_max_area'] != '200':
        results = dao.filter_results_by_range(results, 'area', category_detail_parameters['min_area'], 
                                              category_detail_parameters['chose_max_area'], 
                                              category_detail_parameters['max_area'])
    if category_detail_parameters['bedrooms'] != '0':
        results = dao.filter_results_by_text(results, 'bedrooms', category_detail_parameters['bedrooms'])
    if category_detail_parameters['type_of'] != 'all':
        results = dao.filter_results_by_text(results, 'type_of', category_detail_parameters['type_of'])
    start = (category_detail_parameters['page'] - 1) * 12
    end = start + 12
    results = results[start:end]
    category_detail_parameters['categories'] = dao.load_type_of_property(cate_id)
    if not issale:
        category_detail_parameters['categories'].append(dao.load_categories("T0")[0])
    
    return render_template('category.html', results=results, length=length, viewed_list=viewed_list,
                           page=int(category_detail_parameters['page']), 
                           pages=math.ceil(length / 12), category_detail_parameters=category_detail_parameters)


@app.route("/posts/<string:post_id>", methods=["POST", "GET"])
def details(post_id):
    p = dao.get_post_by_id(post_id)
    if p and p.status == PostsStatusEnum.ACCEPTED or p.user_id == current_user.id or current_user.user_role == UserRoleEnum.ADMIN:
        author_posts = dao.load_posts(user_id=p.user_id)[0]
        author_posts = [post for post in author_posts if post.id != post_id]
        viewed_list = []
        all_reports = dao.load_reports_by_post_id(p.id)
        usr_reports = [dao.get_user_by_id(dao.encrypt_data(str(report.user_id))) for report in all_reports]
        if current_user.is_authenticated:
            for log in dao.get_logs(current_user.id, LogActionEnum.VIEW):
                p_log = dao.get_post_by_id(log.post_id)
                if not p_log in viewed_list:
                    viewed_list.append(p_log)      
        p.address = p.address.replace("~", ",")
        n_images = len(p.images)
        cate_name = dao.get_cate_name_by_id(p.category_id)
        author_id = dao.encrypt_data(str(p.user_id))
        author = dao.get_user_by_id(author_id)
        expire_at = p.expire_at
        duration = (expire_at - datetime.now()).days
        issales = "Cho thuê" if not p.issales else "Cần bán"
        dao.increase_view(p.id)
        if current_user.is_authenticated:
            dao.save_log(post_id=p.id, user_id=current_user.id, action=LogActionEnum.VIEW)

        return render_template('post_details.html', post=p, n_images=n_images, duration=duration, issales=issales,
                            cate_name=cate_name, author=author, author_id=author_id, author_posts=author_posts,
                            viewed_list=viewed_list, all_reports=all_reports, usr_reports=usr_reports)
    else:
        abort(404)


@app.route("/api/post/check_properties", methods=['POST'])
def api_check_properties():
    data = request.json
    post_id = data.get('post_id')
    if post_id:
        post = dao.get_post_by_id(post_id)
    if not post or post.status not in [PostsStatusEnum.EXPIRED, PostsStatusEnum.ACCEPTED, PostsStatusEnum.RENTED, PostsStatusEnum.SOLD]:
        compulsory = ['category', 'is_sale', 'address', 'street', 'cate-prop', 'area', 'price', 'policy', 'title', 'expire-at', 'description']
        category_id = data.get('category')
        if category_id and not 'D0' in category_id and not 'VP' in category_id:
            compulsory.append("bedrooms")
            compulsory.append("bathrooms") 
        for item in compulsory:
            if not item in data:
                return dao.get_status_by_property(item)
            value = data.get(item)
            if not value.strip():
                return dao.get_status_by_property(item)
            if (item == "area" or item == "price") and str(value) == '0':
                return dao.get_status_by_property(item)
        images = data.get('images')
        post_images = dao.load_images_by_post_id(post_id)
        if not images and post_id == '-1' :
            return dao.get_status_by_id(43)
        if not images and post_id != '-1' and not post_images:
            return dao.get_status_by_id(43)
        type_property = data.get('cate-prop')
        kw = category_id[2:4]  
        if not kw in dao.get_cate_id_by_name(type_property).id:
            return dao.get_status_by_id(46)
    
    expire_date = datetime.strptime(data.get('expire-at'),"%Y-%m-%dT%H:%M")
    if expire_date < datetime.now():
        return dao.get_status_by_id(41)
    return dao.get_status_by_id(44)


@login_required
@app.route("/post", methods=["POST", "GET"])
def post():
    status = dao.get_status_by_id(-1)
    expire = None
    if current_user.user_role == UserRoleEnum.RESTRICTED:
        restrict_to = dao.get_identifier(dao.encrypt_data(current_user.id)).restrict_to
        if restrict_to < datetime.now():
            expire = None
        else:
            expire = restrict_to
    if request.method == "POST":        
        category_id = request.form['category'] if 'category' in request.form else None
        issales = request.form['is_sale'] if 'is_sale' in request.form else None
        address = request.form['address'] if 'address' in request.form else None
        street = request.form['street'] if 'street' in request.form else None
        type = request.form['cate-prop'] if 'cate-prop' in request.form else None
        area = request.form['area'] if 'area' in request.form else None
        price = request.form['price'] if 'price' in request.form else None
        policy = request.form['policy'] if 'policy' in request.form else None
        title = request.form['title'] if 'title' in request.form else None
        expire_at = request.form['expire-at'] if 'expire-at' in request.form else None
        description = request.form['description'] if 'description' in request.form else None
        bedrooms = request.form['bedrooms'] if 'bedrooms' in request.form else None
        bathrooms = request.form['bathrooms'] if 'bathrooms' in request.form else None
        floor = request.form['floor'] if 'floor' in request.form else None
        direction = request.form['direction'] if 'direction' in request.form else None
        furniture = request.form['furniture'] if 'furniture' in request.form else None
        user_id = current_user.id
        images = request.files.getlist('images')
        location = request.form.get('location', None)
        
        try:
            address = street.replace(",", "~") + ", " + address
            issales = True if issales and issales == "yes" else False
            dao.save_post(user_id, category_id, issales, address, type,
                          area, price, bedrooms, bathrooms, floor, policy,
                          direction, furniture, title, expire_at, description, 
                          images, location)
            status = dao.get_status_by_id(44)
        except Exception as error:
            print(error)
            status = dao.get_status_by_id(9)

    return render_template('post.html', status=status, expire=expire)


img_list_id = []

@app.route("/edit/<int:post_id>", methods=["POST", "GET"])
def edit_post(post_id):    
    post = dao.get_post_by_id(post_id)
    if post and (current_user.id == post.user_id or current_user.user_role == UserRoleEnum.ADMIN):
        if post.status in [PostsStatusEnum.EXPIRED, PostsStatusEnum.ACCEPTED, PostsStatusEnum.SOLD, PostsStatusEnum.RENTED]:
            status = dao.get_status_by_id(47)
        else:
            status = dao.get_status_by_id(-1)
        user_id = dao.encrypt_data(post.user_id)
        category = dao.load_categories(post.category_id)[0]
        address_arr = post.address.split(", ")
        address_arr[0] = address_arr[0].replace("~", ",")
        if request.method == "POST":
            if "delete-img" in request.form:
                img_id = request.form['delete-img']
                img_list_id.append(img_id)
                dao.delete_img_upload(post_id, img_list_id)
            if "cancel" in request.form:
                img_list_id.clear()
                return redirect(f"/profile/{user_id}")
            if "submit" in request.form:
                category_id = request.form['category'] if 'category' in request.form else post.category_id
                issales = request.form['is_sale'] if 'is_sale' in request.form else post.issales
                address = request.form['address'] if 'address' in request.form else address_arr[1]+", "+address_arr[2]+", " + address_arr[3]
                street = request.form['street'] if 'street' in request.form else address_arr[0]
                type = request.form['cate-prop'] if 'cate-prop' in request.form else post.type
                area = request.form['area'] if 'area' in request.form else post.area
                price = request.form['price'] if 'price' in request.form else post.price
                policy = request.form['policy'] if 'policy' in request.form else post.policy
                title = request.form['title'] if 'title' in request.form else post.title
                expire_at = request.form['expire-at'] if 'expire-at' in request.form else post.expire_at
                description = request.form['description'] if 'description' in request.form else post.description
                bedrooms = request.form['bedrooms'] if 'bedrooms' in request.form else post.bedrooms
                bathrooms = request.form['bathrooms'] if 'bathrooms' in request.form else post.bathrooms
                floor = request.form['floor'] if 'floor' in request.form else post.floor
                direction = request.form['direction'] if 'direction' in request.form else post.direction
                furniture = request.form['furniture'] if 'furniture' in request.form else post.furniture
                user_id = current_user.id
                images = request.files.getlist('images')
                status_post = request.form['status'] if 'status' in request.form else post.status.value
                location = request.form.get('location', f"{post.lat}, {post.lon}")

                if len(post.images) == len(img_list_id) and images[0].filename == '':
                    img_list_id.clear()
                    status = dao.get_status_by_id(43)
                    return render_template("edit.html", post=post, category=category,
                            address_arr=address_arr, status=status)
                
                try:
                    address = street.replace(",","~") + ", " + address
                    issales = True if issales or issales == "yes" else False
                    dao.delete_img_upload(post_id, img_list_id, commit=True)
                    dao.edit_post(post.id, category_id, issales, address, type,
                                area, price, bedrooms, bathrooms, floor, policy,
                                direction, furniture, title, expire_at, description, 
                                images, location, status_post)
                
                    post = dao.get_post_by_id(post_id)
                    if post.status == PostsStatusEnum.ACCEPTED or post.status == PostsStatusEnum.SOLD or post.status == PostsStatusEnum.RENTED:
                        status = dao.get_status_by_id(48)
                    else:
                        status = dao.get_status_by_id(45)
                    category = dao.load_categories(category_id)[0]
                    address_arr = post.address.split(",")
                    address_arr[0] = address_arr[0].replace("~", ",")
                    img_list_id.clear()
                except Exception as error:
                    print(error)
                    status = dao.get_status_by_id(9)
        print(status['content'])        
        print(category)               
        return render_template("edit.html", post=post, category=category,
                            address_arr=address_arr, status=status)
    else:
        abort(404)


def login_admin():
    username = request.form['email']
    password = request.form['password']

    u = dao.auth_user(username=username, password=password)
    if u:
        dao.set_login(u)
        login_user(user=u)

    return redirect('/admin')


@login_required
@app.route("/chat", methods=["POST", "GET"])
def chat():
    conversations = dao.load_conversation(current_user.id)
    last_messages = []
    for c in conversations:
        last_messages.append(dao.get_the_last_message(c.id))
    return render_template("chat.html",
                           conversations=conversations,
                           num_conversations=len(conversations),
                           last_messages=last_messages,
                           user_send_id=current_user.id,
                           user_send_avatar=current_user.avatar)


@login_required
@app.route("/chat/<int:conversation_id>", methods=["POST", "GET"])
def chat_detail(conversation_id):
    conversation = dao.get_conversation(conversation_id)
    if conversation and current_user.is_authenticated:
        dao.update_messages(conversation_id, current_user.id)
        number_new_messages = dao.count_new_message(current_user.id)    
        conversations = dao.load_conversation(current_user.id)
        last_messages = []
        for c in conversations:
            last_messages.append(dao.get_the_last_message(c.id))

        return render_template("chat_detail.html",
                            conversations=conversations,
                            num_conversations=len(conversations),
                           last_messages=last_messages,
                           conversation=conversation,
                           number_new_messages=number_new_messages,
                           user_send_id=current_user.id,
                           user_send_avatar=current_user.avatar)
    return abort(404)


@app.route("/api/conversations/<int:conversation_id>", methods=["POST"])
def api_chat(conversation_id):
    data = []
    messages = dao.load_messages(conversation_id)
    for m in messages:
        sender = dao.get_user_by_id(dao.encrypt_data(m.sent_from))
        data.append({
            'message': m.message,
            'sent_from': m.sent_from,
            'time': m.created_at,
            'sender_avatar': sender.avatar,
            'is_seen': m.is_seen,
            'room_id':m.conversation_id
        })

    return jsonify(data)


@socketio.on("connect")
def handle_connect():
    print('Client connected')


@socketio.on('message')
def handle_message(data):
    if data['msg']:
        emit('message',{'room_id': data['room'],
            'msg': data['msg'],
            'user_send_id': data['userSendId'],
            'user_send_avatar': data['userSendAvatar'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'receiver': data['receiver'],
            'sender': data['sender']},
            broadcast=True)
        
        dao.save_message(data['msg'], data['userSendId'], data['room'], data['isSeen'])


@socketio.on('changeBadge')
def handle_badge(data):
    conversation_id = data['conversationId']
    conversation = dao.get_conversation(conversation_id)
    dao.update_messages(conversation_id, current_user.id)
    emit("changeBadge", {
        'current_user_id': data['currentUser'],
        'number_bagdes' : dao.count_new_message(current_user.id),
        'sender': conversation.started_by,
        'receiver': conversation.receive_by,
        'last_sent_id': dao.get_the_last_message(conversation.id).sent_from
    }, broadcast=True)


@socketio.on('join')
def join(data):
    join_room(data['room'])


@socketio.on('leave')
def leave(data):
    leave_room(data['room'])


@app.route("/api/check_conversation/<int:sender>/<int:receiver>", methods=["POST"])
def create_conversation(sender, receiver):
    conversation = dao.check_exists_conversation(sender, receiver)
    if conversation != 0:
        return jsonify({
            'sender': conversation.started_by,
            'receiver': conversation.receive_by,
            'conversation_id': conversation.id,
            'status': 'exist'
        })
    dao.new_conversation(sender, receiver)
    conversation = dao.check_exists_conversation(sender, receiver)
    return jsonify({
        'sender': conversation.started_by,
        'receiver': conversation.receive_by,
        'conversation_id': conversation.id,
        'status': 'create'
    })


@login_required
@app.route("/review/<string:user_id>", methods=["POST", "GET"])
def review(user_id):
    user = dao.get_user_by_id(user_id)
    if user:
        accept_review = False
        err_msg = 0
        if request.method == "POST":
            if "review-btn" in request.form and current_user.id != user.id:
                star = request.form['rate']
                content = request.form['content']
                try:
                    dao.review(current_user.id, user.id, star, content)
                    err_msg = 1
                    return redirect(f'/review/{user_id}')
                except:
                    err_msg = -1
        rating = 0
        user_reviews = dao.load_publisher_reviews(user.id)
        if user_reviews:
            for r in user_reviews:
                rating = rating + r.rating
            rating = float(rating)/float(user_reviews.__len__())
        reviewed_list = dao.load_reviews(user_id=user.id)
        waiting_reviews = dao.load_waiting_reviews(current_user.id)
        user_id_list = []
        for item in waiting_reviews:
            if item.user_send.id == current_user.id:
                user_id_list.append(dao.encrypt_data(item.user_receive.id))
            else:
                user_id_list.append(dao.encrypt_data(item.user_send.id))
            accept_review = True
        
        return render_template("review_user.html", reviewed_list=reviewed_list, user_id=user_id, 
                               user_reviews=user_reviews, waiting_reviews=waiting_reviews, user=user, 
                               err_msg=err_msg, user_id_list=user_id_list, rating=rating, accept_review=accept_review)
    return abort(404)


@app.route("/", methods=["POST", "GET"])
def home():
    parameters['issales'] = "true"
    page_sales = request.args.get('page', 1)
    page_rents = request.args.get('page', 1)
    viewed_list = []
    if current_user.is_authenticated:
        for log in dao.get_logs(current_user.id, LogActionEnum.VIEW):
            p = dao.get_post_by_id(log.post_id)
            if not p in viewed_list:
                viewed_list.append(p)            

    (posts, posts_len) = dao.load_posts(page=int(page_sales), issale=True)
    (rent_posts, rent_posts_len) = dao.load_posts(page=int(page_rents), issale=False)
    for p in posts:
        p.address = p.address.replace("~", ",")
    for p in rent_posts:
        p.address = p.address.replace("~", ",")

    return render_template('index.html', posts=posts, page_sales=int(page_sales),
                           pages_sales=math.ceil(posts_len / app.config['PAGE_SIZE']), 
                           rent_posts=rent_posts, page_rents=int(page_rents),
                           pages_rents=math.ceil(rent_posts_len / app.config['PAGE_SIZE']),
                           viewed_list=viewed_list)


@app.context_processor
def common_data():        
    accommodation = dao.load_categories("T0")
    sales_cate = dao.load_categories("DM")
    rent_cate = sales_cate.copy()
    rent_cate.append(accommodation[0])
    admin = UserRoleEnum.ADMIN
    half_publisher = UserRoleEnum.HALF_PUBLISHER
    publisher = UserRoleEnum.PUBLISHER
    restricted = UserRoleEnum.RESTRICTED
    report_list = []  
    saved_list = []
    number_new_messages = 0
    is_new_notify = None
    respone = es.search(index=index_name, query={
        "match_all": {}
    })
    
    if len(respone['hits']['hits']) == 0:
        for p in dao.load_posts(page=0)[0]:
            doc = {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "address": p.address.replace("~", ","),
                "location": {
                    "lat": p.lat,
                    "lon": p.lon
                },
                "price": dao.compact_money(p.price),
                "area": p.area,
                "bedrooms": f"{p.bedrooms} phòng ngủ",
                "type_of": p.type,
                "furniture": p.furniture,
                "updated_at": p.updated_at,
                "category": p.category.name,
                "issales": "Mua Bán" if p.issales else "Cho Thuê",
                "image": p.images[0].url if p.images else "https://res.cloudinary.com/doaux2ndg/image/upload/v1670076213/FlightMangement/icon-web_fgxmmq.png"
                }
            es.index(index=index_name, id=p.id, document=doc)

    try:
        dao.check_expire_post()
        dao.delete_account_not_active()
    except Exception as error:
        print(error)
        
    if current_user.is_authenticated: 
        en_id = dao.encrypt_data(str(current_user.id))
        for r in dao.load_reports(current_user.id):
            report_list.append(dao.get_post_by_id(r.post_id))
        for s in dao.get_logs(current_user.id, LogActionEnum.SAVED):
            saved_list.append(dao.get_post_by_id(s.post_id))
        number_new_messages = dao.count_new_message(current_user.id)
        if current_user.user_role == UserRoleEnum.ADMIN:
            is_new_notify = dao.count_new_notify()
    else:
        en_id = ""
    
    return {
        'sales_cate': sales_cate,
        'rent_cate': rent_cate,
        'admin': admin,
        'current_user_id': en_id,
        'half_publisher': half_publisher,
        'restricted': restricted,
        'publisher': publisher,
        'report_list': report_list,
        'parameters':parameters,
        'saved_list': saved_list,
        'number_new_messages': number_new_messages,
        'is_new_notify': is_new_notify
    }


@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(dao.encrypt_data(user_id))


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app=app, debug=True, allow_unsafe_werkzeug=True)