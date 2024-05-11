import hashlib
import json
import cloudinary.uploader
from houselandapp import db, fernet, es, index_name
from models import *
from sqlalchemy import extract, func, or_, and_
from avatar_generator import Avatar
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import requests
from securable_data import *
from flask import jsonify
from datetime import datetime
from collections import Counter
from underthesea import word_tokenize

load_dotenv()

def write_json_file(path, data):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    file.close()


def read_json_file(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)
    

def get_status_by_id(id):
    message = read_json_file(f'{app.root_path}/data/message.json')
    for m in message:
        if m['id'] == id:
            return m
        
    return jsonify({
        "id": "",
        "is_true": "",
        "for": "",
        "content": "",
    })


def get_status_by_property(property):
    message = read_json_file(f'{app.root_path}/data/message.json')
    for m in message:
        if m['for'] == f"post_{property}":
            return m
        
    return jsonify({
        "id": "",
        "is_true": "",
        "for": "",
        "content": "",
    })


def auth_user(phone, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.phone.__eq__(phone.strip()),
                             User.password.__eq__(password)).first()


def set_login(user):
    u = User.query.get(user.id)
    save_log(post_id=None, user_id=u.id, date=datetime.now(), action=LogActionEnum.LOGIN)


def generate_avatar(name):
    res = cloudinary.uploader.upload(Avatar.generate(512, name, 'PNG'), folder="houselandavatar")
    return res['secure_url']


def update_user(phone, name, email, city=None, otp_code=None):
    user = get_user_by_username(phone)
    if user:
        user.name = name
        user.email = email
        user.active = True
        user.city = city if city else None
        user.otp_code = hash_kw(otp_code) if otp_code else None
        db.session.commit()
        return 1

    return None


def final_register(email, name=None):
    user = get_user_by_email(email)
    if user:
        user.active = True
        if name:
            user.avatar = generate_avatar(name)
        db.session.commit()
        return 0

    return 9


def find_user(phone):
    user = get_user_by_username(phone)
    if user and user.active and user.user_role != UserRoleEnum.WAITING_DELETE:
        return True
    return False


def update_otp(phone, otp):
    user = get_user_by_username(phone)
    if user:
        user.otp_code = hash_kw(otp)
        db.session.commit()
        return True
        
    return False


def update_otp_by_email(email, otp, phone=None):
    user = get_user_by_email(email)
    if user:
        if phone:
            user.phone = phone
        user.otp_code = hash_kw(otp)
        db.session.commit()
        return True
        
    return False


def register(phone, password, otp_code):
    user = get_user_by_username(phone)
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    if user and not user.active:
        user.password = password
        user.otp_code = hash_kw(otp_code)
    else:      
        u = User(password=password, phone=phone, otp_code=hash_kw(otp_code), active=False)
        db.session.add(u)
    db.session.commit()
    return 200


def register_by_email(name, email, avatar=None):
    if not avatar:
        avatar = generate_avatar(name)
    u = User(name=name, email=email, avatar=avatar, active=False)
    db.session.add(u)
    db.session.commit()


def change_avatar(user_id, image=None):
    user = get_user_by_id(user_id)
    if image:
        res = cloudinary.uploader.upload(image, folder="houselandavatar")
    else:
        avt = Avatar.generate(512, user.name, "PNG")
        public_id = user.avatar.split("/")[-1].split(".")[0]
        cloudinary.uploader.destroy(public_id)
        res = cloudinary.uploader.upload(avt, folder="houselandavatar")
    path = res['secure_url']
    user.avatar = path
    db.session.commit()


def update_user_info(id, name, description, city):
    user = get_user_by_id(id)
    user.name = name.strip()
    user.description = description
    user.city = city 
    db.session.commit()


def update_user_contact(id, email, phone):
    user = get_user_by_id(id)
    user.email = email if email else user.email       
    user.phone = phone if phone else user.phone
    db.session.commit()


def update_password(id, new_password):
    user = get_user_by_id(id)
    user.password = str(hashlib.md5(new_password.strip().encode('utf-8')).hexdigest())
    db.session.commit()


def register_broker(id):
    user = get_user_by_id(id)
    if user and user.user_role == UserRoleEnum.USER:
        user.user_role = UserRoleEnum.HALF_PUBLISHER
        db.session.commit()
        return 23
    else:
        return 9


def request_delete_user(id):
    user = get_user_by_id(id)
    user.active = False
    user.otp_code = hash_kw("00000")
    user.user_role == UserRoleEnum.WAITING_DELETE
    db.session.commit()


def load_user_by_kw(kw='all'):
    if kw == "all":
        return db.session.query(User.id, User.name, User.phone, User.email,
                            User.user_role, User.date_created, User.active)\
                    .order_by(User.date_created.desc()).all()
    if kw == "waiting":
        return db.session.query(User.id, User.name, User.phone, User.email,
                            User.user_role, User.date_created, User.active)\
                            .filter(User.user_role == UserRoleEnum.HALF_PUBLISHER)\
                    .order_by(User.date_created.desc()).all()
    if kw == "delete":
        return db.session.query(User.id, User.name, User.phone, User.email,
                            User.user_role, User.date_created, User.active)\
                            .filter(User.user_role == UserRoleEnum.WAITING_DELETE)\
                    .order_by(User.date_created.desc()).all()
    if kw == "restrict":
        return db.session.query(User.id, User.name, User.phone, User.email,
                            User.user_role, User.date_created, User.active)\
                            .filter(User.user_role == UserRoleEnum.RESTRICTED)\
                    .order_by(User.date_created.desc()).all()
    return User.query\
                    .order_by(User.date_created.desc()).all()


def recovery_user(id):
    user = User.query.get(id)
    user.active = True
    i = Identifier.query.get(id)
    if i:
        user.user_role = UserRoleEnum.PUBLISHER
    else:
        user.user_role = UserRoleEnum.USER
    db.session.commit()


def delete_user(id):
    user = get_user_by_id(id)
    posts, counts = load_posts(user_id=user.id)
    for p in posts:
        remove_post(p.id)
    i = Identifier.query.get(id)
    if i:
        db.session.delete(i)
    db.session.delete(user)
    db.session.commit()


def get_identifier(user_id):
    id = decrypt_data(user_id)
    return Identifier.query.get(id)


def get_identifier_by_id_code(id_code):
    return Identifier.query.filter(Identifier.id_code == id_code).first()


def add_identifier(user_id, id_code, full_name, gender, dob, address, register_date, at, expire_at):
    i = get_identifier_by_id_code(id_code)
    if i:
        recovery_user(user_id)
        return 29
    
    full_name = encrypt_data_no2(full_name)
    id_code = encrypt_data_no2(id_code)
    gender = True if gender.strip().lower()=="nữ" else False
    identifier = Identifier(user_id=user_id, id_code=id_code, full_name=full_name, gender=gender, 
                            dob=dob, address=address, register_date=register_date, at=at, expire_at=expire_at,
                            restrict_from=datetime.now(), restrict_to=datetime.now(), accept_at=None)
    db.session.add(identifier)
    db.session.commit()
    return 23


def edit_identifier(user_id, full_name, gender, dob, id_code, address, register_date, expire_at, at):
    u = get_user_by_id(user_id)
    if u.user_role == UserRoleEnum.HALF_PUBLISHER:
        u.user_role = UserRoleEnum.PUBLISHER
        i = get_identifier(user_id)
        i.full_name = encrypt_data_no2(full_name)
        gender = False if gender.strip().lower()=="nam" else True
        i.gender = gender
        i.dob = dob
        i.id_code = encrypt_data_no2(id_code)
        i.address = address
        i.register_date = register_date
        i.expire_at = expire_at
        i.at = at
        i.accept_at = datetime.now()
        db.session.commit()


def restrict_user(user_id, restrict_from, restrict_to):
    user = get_user_by_id(encrypt_data(user_id))
    i = get_identifier(encrypt_data(user_id))
    i.restrict_from = restrict_from
    i.restrict_to = restrict_to
    end = datetime.strptime(restrict_to, "%Y-%m-%dT%H:%M")
    if end > datetime.now():
        user.user_role = UserRoleEnum.RESTRICTED
    else:
        user.user_role = UserRoleEnum.PUBLISHER
    db.session.commit()


def handle_report(user_id, post_id, status):
    report = Reports.query.filter(Reports.user_id == user_id, Reports.post_id == post_id).first()
    if report:
        report.status = status
        report.date_handle = datetime.now()
        db.session.commit()


def load_reports(user_id):
    return Reports.query.filter(Reports.user_id == user_id).all()
    

def load_reports_by_post_id(post_id):
    return Reports.query.filter(Reports.post_id == post_id).all()


def load_categories(kw):
    return Category.query.filter(Category.id.startswith(kw.strip())).all()


def get_cate_name_by_id(cate_id):
    if cate_id != all:
        return Category.query.get(cate_id).name
    
    return ""


def get_cate_id_by_name(cate_name):
    return db.session.query(Category.id).filter(Category.name == cate_name).first()


def load_type_of_property(category_id):
    if category_id == 'all':
        return load_categories('DM')
    if not category_id.startswith("T"):
        return load_categories(category_id[2:4])

    return load_categories('CH')

def load_posts_by_status(status='All'):
    if status == "All":
        posts = db.session.query(Posts.id, Posts.title, Posts.created_at, Posts.updated_at,
                            Posts.status, User.avatar, User.name)\
                    .join(User, Posts.user_id == User.id)\
                    .order_by(Posts.created_at.desc()).all()
    elif status == "Đã bị ẩn":
        posts = db.session.query(Posts.id, Posts.title, Posts.created_at, Posts.updated_at,
                            Posts.status.value, User.avatar, User.name)\
                    .join(User, Posts.user_id == User.id)\
                    .filter(Posts.status == PostsStatusEnum.HIDDEN)\
                    .order_by(Posts.created_at.desc()).all()
    elif status == "Đã đăng":
        posts = db.session.query(Posts.id, Posts.title, Posts.created_at, Posts.updated_at,
                            Posts.status, User.avatar, User.name)\
                    .join(User, Posts.user_id == User.id)\
                    .filter(Posts.status == PostsStatusEnum.ACCEPTED)\
                    .order_by(Posts.created_at.desc()).all()
    elif status == "Đã hết hạn":
        posts = db.session.query(Posts.id, Posts.title, Posts.created_at, Posts.updated_at,
                            Posts.status, User.avatar, User.name)\
                    .join(User, Posts.user_id == User.id)\
                    .filter(Posts.expire_at < datetime.now())\
                    .order_by(Posts.created_at.desc()).all()
    elif status == "Đã cho thuê":
        posts =  db.session.query(Posts.id, Posts.title, Posts.created_at, Posts.updated_at,
                            Posts.status, User.avatar, User.name)\
                    .join(User, Posts.user_id == User.id)\
                    .filter(Posts.status == PostsStatusEnum.RENTED)\
                    .order_by(Posts.created_at.desc()).all()
    elif status == "Đã bán":
        posts = db.session.query(Posts.id, Posts.title, Posts.created_at, Posts.updated_at,
                            Posts.status, User.avatar, User.name)\
                    .join(User, Posts.user_id == User.id)\
                    .filter(Posts.status == PostsStatusEnum.SOLD)\
                    .order_by(Posts.created_at.desc()).all()
    else:
        posts = db.session.query(Posts.id, Posts.title, Posts.created_at, Posts.updated_at,
                            Posts.status, User.avatar, User.name)\
                    .join(User, Posts.user_id == User.id)\
                    .filter(Posts.status.in_((PostsStatusEnum.WAITING, PostsStatusEnum.EDITED)))\
                    .order_by(Posts.created_at.desc()).all()
        
    return posts


def load_posts_by_status_v2(status=PostsStatusEnum.ACCEPTED, user_id=None):
    if user_id:
        if status == PostsStatusEnum.WAITING:
            return Posts.query.filter(Posts.status.in_((PostsStatusEnum.WAITING, PostsStatusEnum.EDITED, PostsStatusEnum.HIDDEN)))\
                .filter(Posts.user_id == user_id).order_by(Posts.created_at.desc()).all()
        
        return Posts.query.filter(Posts.status == status)\
                .filter(Posts.user_id == user_id).order_by(Posts.created_at.desc()).all()
    
    return Posts.query.filter(Posts.status == status)\
                .order_by(Posts.created_at.desc()).all()


def get_last_post():
    return Posts.query.order_by(Posts.id.desc()).first()


def load_posts(page=1, cate_id='', address_kw='', area_kw=0, price_kw=0, user_id='', issale=0):
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size
    query = Posts.query.filter(Posts.status==PostsStatusEnum.ACCEPTED).filter(Posts.expire_at > datetime.now())

    if cate_id and cate_id != "all":
        query = query.filter(Posts.category_id == cate_id)   
    if issale == 0:
        query=query     
    elif issale == True:
        query = query.filter(Posts.issales == True)
    else :
        query = query.filter(Posts.issales == False)
    if address_kw:
        query = query.filter(Posts.address.contains(address_kw.strip()))
    if area_kw:
        query = query.filter(Posts.area.__ge__(area_kw))
    if price_kw:
        query = query.filter(Posts.price.__ge__(price_kw))
    if user_id:
        query = query.filter(Posts.user_id == user_id)

    if page == 0:
        return query.order_by(Posts.updated_at.desc()).all(), query.count()

    return query.order_by(Posts.updated_at.desc()).slice(start, end).all(), query.count()


def count_posts():
    return Posts.query.count()


def get_last_image():
    return Images.query.order_by(Images.id.desc()).first()


def get_post_by_id(post_id):
    return Posts.query.get(post_id)


def load_image():
    return Posts.query.filter(Posts.status==PostsStatusEnum.ACCEPTED)\
        .order_by(Posts.updated_at.desc()).all()


def delete_img_upload(post_id, img_list_id, commit=None):    
    if commit:
        for i in img_list_id:
            img = Images.query.get(int(i))
            db.session.delete(img)
        db.session.commit()
    else:
        for i in img_list_id:
            img = Images.query.get(i)
            post = Posts.query.get(post_id)
            post.images.remove(img)

def save_post(user_id, category_id, issales, address, type, area, price, bedrooms, \
              bathrooms, floor, policy, direction, furniture, title, expire_at, description, \
                images, location, status=PostsStatusEnum.WAITING):
    last_post = get_last_post()
    if last_post:
        id = last_post.id + 1
    else:
        id = 1
    if category_id and 'D0' in category_id or 'VP' in category_id:
         post = Posts(id=id, title=title, description=description, status=status, expire_at=expire_at, bedrooms=0,
                 bathrooms=0, floor=0, area=area, price=price, address=address, policy=policy, created_at=datetime.now(), updated_at=datetime.now(),
                 direction=direction, furniture='', type=type, issales=issales, user_id=user_id, category_id=category_id,
                 lat=float(location.split(",")[0].strip()),lon=float(location.split(",")[1].strip()))
    else:
        post = Posts(id=id, title=title, description=description, status=status, expire_at=expire_at, bedrooms=bedrooms,
                    bathrooms=bathrooms, floor=floor, area=area, price=price, address=address, policy=policy, created_at=datetime.now(), updated_at=datetime.now(),
                    direction=direction, furniture=furniture, type=type, issales=issales, user_id=user_id, category_id=category_id,
                    lat=float(location.split(",")[0].strip()),lon=float(location.split(",")[1].strip()))
    
    db.session.add(post)
    db.session.commit()
    if images:
        img_id = get_last_image().id
        for img in images:
            img_id = img_id + 1
            res = cloudinary.uploader.upload(img, folder="houselandimages")
            path = res['secure_url']
            image = Images(id=img_id, url=path, date_update=datetime.now(), post_id=id)
            db.session.add(image)

        db.session.commit()


def edit_post(id, category_id, issales, address, type, area, price, bedrooms, \
              bathrooms, floor, policy, direction, furniture, title, expire_at, \
                description, images, location, status):
    post = get_post_by_id(id)
    due = datetime.strptime(expire_at, "%Y-%m-%dT%H:%M")
    post.title = title
    post.description = description
    if status == 'sale':
        post.status = PostsStatusEnum.SOLD 
    elif status == 'rent':
        post.status = PostsStatusEnum.RENTED
    elif due < datetime.now():
        post.status = PostsStatusEnum.EXPIRED
    elif post.status in [PostsStatusEnum.EDITED, PostsStatusEnum.WAITING]:
        post.status = PostsStatusEnum.EDITED
    
    post.updated_at = datetime.now()
    post.expire_at = expire_at
    if category_id and 'D0' in category_id or 'VP' in category_id:
        post.bedrooms = 0
        post.bathrooms = 0
        post.floor = 0
        post.furniture = ''  
    else:
        post.bedrooms = bedrooms
        post.bathrooms = bathrooms
        post.floor = floor
        post.furniture = furniture
    post.area = area
    post.price = price
    post.address = address
    post.policy = policy
    post.direction = direction
    post.type = type
    post.issales = issales
    post.category_id = category_id
    post.lat=float(location.split(",")[0].strip())
    post.lon=float(location.split(",")[1].strip())
    if len(images) > 0 and images[0].filename != '':
        img_id = get_last_image().id + 1
        for img in images:
            res = cloudinary.uploader.upload(img)
            path = res['secure_url']
            image = Images(id=img_id, url=path, date_update=datetime.now())
            db.session.add(image)
            post.images.append(image)
    db.session.commit()

    if post.expire_at > datetime.now() and post.status == PostsStatusEnum.ACCEPTED:
        data = {
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "address": post.address.replace("~", ","),
            "location": {
                "lat": post.lat,
                "lon": post.lon
            },
            "price": compact_money(post.price),
            "area": post.area,
            "bedrooms": f"{post.bedrooms} phòng ngủ",
            "type_of": post.type,
            "furniture": post.furniture,
            "updated_at": post.updated_at,
            "category": post.category.name,
            "issales": "Mua Bán" if post.issales else "Cho Thuê",
            "image": post.images[0]
        }
        es.index(index=index_name, id=post.id, body=data)


def accept_post(id):
    post = Posts.query.get(id)
    post.status = PostsStatusEnum.ACCEPTED
    data = {
        "id": post.id,
        "title": post.title,
        "description": post.description,
        "address": post.address.replace("~", ","),
        "location": {
            "lat": post.lat,
            "lon": post.lon
        },
        "price": compact_money(post.price),
        "area": post.area,
        "bedrooms": f"{post.bedrooms} phòng ngủ",
        "type_of": post.type,
        "furniture": post.furniture,
        "updated_at": post.updated_at,
        "category": post.category.name,
        "issales": "Mua Bán" if post.issales else "Cho Thuê",
        "image": post.images[0]
    }
    es.index(index=index_name, id=post.id, body=data)
    post.created_at = datetime.now()
    post.updated_at = datetime.now()
    db.session.commit()


def hide_post(id):
    post = Posts.query.get(id)
    post.status = PostsStatusEnum.HIDDEN
    es.delete_by_query(index=index_name, body={
                    'query': {
                        'match': {
                            'id' : post.id
                        }
                    }
                })
    post.updated_at = datetime.now()
    db.session.commit()


def remove_post(id):
    post = Posts.query.get(id)
    es.delete_by_query(index=index_name, body={
                    'query': {
                        'match': {
                            'id' : post.id
                        }
                    }
                })
    db.session.delete(post)
    db.session.commit()


def recovery_post(id):
    post = Posts.query.get(id)
    post.status = PostsStatusEnum.ACCEPTED
    data = {
        "id": post.id,
        "title": post.title,
        "description": post.description,
        "address": post.address.replace("~", ","),
        "location": {
            "lat": post.lat,
            "lon": post.lon
        },
        "price": compact_money(post.price),
        "area": post.area,
        "bedrooms": f"{post.bedrooms} phòng ngủ",
        "type_of": post.type,
        "furniture": post.furniture,
        "updated_at": post.updated_at,
        "category": post.category.name,
        "issales": "Mua Bán" if post.issales else "Cho Thuê",
        "image": post.images[0]
    }
    es.index(index=index_name, id=post.id, body=data)
    post.updated_at = datetime.now()
    db.session.commit()


def get_log(post_id, user_id):
    return Logs.query.filter(Logs.post_id==post_id, Logs.user_id==user_id).order_by(Logs.date.desc()).first()


def get_logs(user_id, action):
    return Logs.query.filter(Logs.user_id==user_id, Logs.action==action).order_by(Logs.date.desc()).all()


def save_log(post_id=None, user_id=None, date=datetime.now(), action=LogActionEnum.VIEW):
    last_log = Logs.query.filter(Logs.post_id == post_id, Logs.user_id == user_id, Logs.action == action).first()
    if last_log:
        last_log.date = datetime.now()
    else:
        lg = Logs(post_id=post_id, user_id=user_id, date=date, action=action)
        db.session.add(lg)
    db.session.commit()


def delete_viewed_post(post_id, user_id):
    logs = Logs.query.filter(Logs.post_id == post_id, Logs.user_id==user_id, Logs.action==LogActionEnum.VIEW).all()
    for log in logs:
        db.session.delete(log)
    db.session.commit()


def delete_saved_post(post_id, user_id):
    logs = Logs.query.filter(Logs.post_id == post_id, Logs.user_id==user_id, Logs.action==LogActionEnum.SAVED).all()
    for log in logs:
        db.session.delete(log)
    db.session.commit()


def react_post(post_id, user_id):
    post = Posts.query.get(post_id)
    user = get_user_by_id(user_id)
    try:
        log = get_log(post.id, user.id)
        db.session.delete(log)
        db.session.commit()
        return -1
    except:
        save_log(post_id=post.id, user_id=user.id, date=datetime.now(), action=LogActionEnum.SAVED)
        return 1


def load_images_by_post_id(post_id):
    return Images.query.filter(Images.post_id == post_id).all()


def stats_category():
    return db.session.query(Category.id, Category.name, func.count(Posts.id)) \
        .join(Posts, Category.id.__eq__(Posts.category_id)) \
        .group_by(Category.id, Category.name).all()


def statistics(month=None):
    if month != 0:
        query = db.session.query(extract('day', Posts.created_at), func.count(Posts.id)) \
                            .filter(extract('month', Posts.created_at) == month)\
                            .group_by(func.day(Posts.created_at))
    else:
        query = db.session.query(extract('month', Posts.created_at), func.count(Posts.id)) \
                             .group_by(func.month(Posts.created_at))
    return query.all()


def stats_post():
    new_posts = Posts.query.filter(or_(Posts.status == PostsStatusEnum.WAITING, Posts.status == PostsStatusEnum.EDITED)).count()
    all_posts = count_posts()
    return new_posts, all_posts


def stats_user():
    today = datetime.today().date()
    new_users = User.query.filter(extract('year', User.date_created) == today.year,
                                  extract('month', User.date_created) == today.month,
                                  extract('day', User.date_created) == today.day).count()
    rank_users = db.session.query(User.avatar, User.name, func.count(Posts.id)) \
        .join(Posts, Posts.user_id.__eq__(User.id), isouter=True) \
        .group_by(User.avatar, User.name) \
        .order_by(func.count(Posts.id).desc()).all()
    all_user = User.query.count()
    return new_users, all_user, rank_users


def stats_report():
    new_reports = Reports.query.filter(Reports.status == "Chưa xử lý").count()
    all_reports = Reports.query.count()
    return new_reports, all_reports


def get_user_by_id(user_id):    
    id = decrypt_data(user_id)
    return User.query.get(id)


def get_user_by_username(phone):
    user = User.query.filter(User.phone.__eq__(phone.strip())).first()
    if user:
        return user
    return None


def get_user_by_email(email):
    user = User.query.filter(User.email.__eq__(email.strip())).first()
    if user:
        return user
    return None

def get_user_by_post_id(post_id):
    user_id = get_post_by_id(post_id).user_id
    user_id = encrypt_data(str(user_id))
    return get_user_by_id(user_id)


def reset_password(username, new_password):
    user = get_user_by_username(username)
    password = str(hashlib.md5(new_password.strip().encode('utf-8')).hexdigest())
    user.password = password
    db.session.commit()


def report(post_id, user_id, content):
    post = get_post_by_id(post_id)
    post.status = PostsStatusEnum.HIDDEN
    db.session.add(Reports(user_id=user_id, post_id=post_id, content=content, status="Chưa xử lý"))
    db.session.commit()


def count_bad_report(user_id):
    number = 0
    posts = Posts.query.filter(Posts.user_id == user_id).all()
    for p in posts:
        if p.user_report:
            for r in p.user_report:
                if r.status == "Đã ẩn bài viết":
                    number = number + 1
    return number


def count_new_message(user_id):
    conversations = load_conversation(user_id)
    last_messages = []
    count = 0
    for c in conversations:
        last_messages.append(get_the_last_message(c.id))
    for m in last_messages:
        if not m.is_seen and m.sent_from != user_id:
            count = count + 1
    return count


def load_conversation(user_id):
    return Conversation.query.filter(or_(Conversation.started_by == user_id,
                                     Conversation.receive_by == user_id))\
        .order_by(Conversation.updated_at.desc()).all()


def get_the_last_message(conversation_id):
    return Message.query.filter(Message.conversation_id == conversation_id)\
            .order_by(Message.created_at.desc()).first()


def update_messages(conversation_id, current_user_id = None):
    query = Message.query.filter(Message.conversation_id == conversation_id).all()
    for q in query:
        if not q.is_seen and q.sent_from == current_user_id:
            q.is_seen = False
        else:
            q.is_seen = True
    db.session.commit()


def load_messages(conversation_id):
    return Message.query.filter(Message.conversation_id == conversation_id).all()


def check_exists_conversation(user_send, user_receive):
    query = Conversation.query.filter(or_(and_(Conversation.started_by == user_send,
                                     Conversation.receive_by == user_receive),
                                          and_(Conversation.started_by == user_receive,
                                     Conversation.receive_by == user_send))).first()
    if query:
        return query
    return 0


def save_message(message, user_send_id, conversation_id, is_seen):
    m = Message(message=message, sent_from=user_send_id, created_at=datetime.now(), conversation_id=conversation_id, is_seen=is_seen)
    db.session.add(m)
    db.session.commit()
    conversation = Conversation.query.get(conversation_id)
    conversation.updated_at = datetime.now()
    db.session.commit()


def get_last_conversation():
    return Conversation.query.order_by(Conversation.id.desc()).first()


def get_conversation(id):
    return Conversation.query.get(id)


def new_conversation(started_by, receive_by):
    last_id = get_last_conversation()
    if last_id:
        new_id = last_id.id + 1
    else:
        new_id = 1
    c = Conversation(started_by=started_by, receive_by=receive_by, created_at=datetime.now(), id=new_id)
    db.session.add(c)
    db.session.commit()


def load_reviews(user_id):
    return UserReview.query.filter(UserReview.user_id == user_id).order_by(UserReview.review_at.desc()).all()


def load_publisher_reviews(publisher_id):
    return UserReview.query.filter(UserReview.publisher_id == publisher_id).order_by(UserReview.review_at.desc()).all()


def load_waiting_reviews(user_id):
    conversations = []
    
    for conversation in load_conversation(user_id):
        mess = get_the_last_message(conversation.id)
        if mess:
            conversations.append(conversation)
    
    return conversations


def review(user_id, publisher_id, star, content):
    if user_id != publisher_id:
        r = UserReview(user_id=user_id, publisher_id=publisher_id, rating=star, content=content, review_at=datetime.now())
        db.session.add(r)
        db.session.commit()


def generate_path(id, filename, surface): 
    filename = secure_filename(filename)
    refilename = f"{hash_kw(id)}_{surface}.jpg"
    path = os.path.join(app.config['UPLOAD_PATH'], refilename)

    return path


def id_recognize(path):
    files = {'image': open(path, 'rb').read()}
    headers = {
        'api-key': os.getenv('READER_API_KEY')
    }

    response = requests.post(os.getenv('ID_RECOGNITION_URL'), files=files, headers=headers)

    return json.loads(response.text)


def facematch(path_1, path_2):
    files = [
        ('file[]', open(path_1, 'rb')),
        ('file[]', open(path_2, 'rb'))
    ]
    headers = {
        'api-key': os.getenv('READER_API_KEY')
    }

    response = requests.post(os.getenv('FACEMATCH_URL'), files=files, headers=headers)

    return json.loads(response.text)


def idmatch(front,back):
    if front['data'][0]['type'].__eq__("chip_front") and back['data'][0]['type'].__eq__("chip_back"):
        if front['data'][0]['id'] == back['data'][0]['mrz_details']['id']:
            return 1
    elif front['data'][0]['type'].__eq__("old") and back['data'][0]['type'].__eq__("old_back"):
        return 0
    
    return -1


def remove_id_image(id):
    id_hash = hash_kw(id)
    user = get_user_by_id(encrypt_data(id))

    path_1 = os.path.join(app.config['UPLOAD_PATH'], f"{id_hash}_B.jpg")
    path_2 = os.path.join(app.config['UPLOAD_PATH'], f"{id_hash}_F.jpg")
    path_3 = os.path.join(app.config['UPLOAD_PATH'], f"{id_hash}_S.jpg")
    
    if user:
        os.remove(path_1)
        os.remove(path_2)
        os.remove(path_3)
        user.user_role = UserRoleEnum.USER
        i = get_identifier(id)
        if i:
            db.session.delete(i)
        db.session.commit()
        return 27
    return 9


def hash_kw(kw):
    return str(hashlib.md5(str(kw).encode("utf-8")).hexdigest())


def encrypt_data(data):
    encrypted_data = fernet.encrypt(str(data).encode("utf-8"))
    return encrypted_data.decode()


def decrypt_data(encrypted_data):
    decrypted_data = fernet.decrypt(str(encrypted_data)).decode('utf-8')
    return decrypted_data

def encrypt_data_no2 (plaintext):
    n = 280
    plainindex_range = []
    keyindex_rang = []
    ciphertext = ""
    index=0

    decode = create_decode()
    encode = create_encode()

    for p in plaintext:
        plainindex_range.append(decode[p])

    for k in vigenere_key:
        keyindex_rang.append(decode[k])

    while len(plainindex_range) != len(keyindex_rang):
        if len(plainindex_range) > len(keyindex_rang):
            keyindex_rang.append(keyindex_rang[index])
            index += 1
        else:
            temp = len(keyindex_rang) - 1
            keyindex_rang.remove(keyindex_rang[temp])

    for i in range(len(plainindex_range)):
        index = (plainindex_range[i]+keyindex_rang[i])%n
        ciphertext += encode[index]

    return ciphertext


def decrypt_data_no2 (ciphertext):
    n = 280
    cipherindex_range = []
    keyindex_rang = []
    plaintext = ""
    index=0

    decode = create_decode()
    encode = create_encode()

    for c in ciphertext:
        cipherindex_range.append(decode[c])

    for k in vigenere_key:
        keyindex_rang.append(decode[k])

    while len(cipherindex_range) != len(keyindex_rang):
        if len(cipherindex_range) > len(keyindex_rang):
            keyindex_rang.append(keyindex_rang[index])
            index += 1
        else:
            temp = len(keyindex_rang) - 1
            keyindex_rang.remove(keyindex_rang[temp])

    for i in range(len(cipherindex_range)):
        index = (cipherindex_range[i]-keyindex_rang[i])
        while index < 0:
            index += n
        plaintext += encode[index]

    return plaintext


def is_datetime(string):
    try: 
        datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        return True
    except Exception as error:
        print(error)
        return False
    

def compact_money(money):
    unit = ["VNĐ", "nghìn đồng", "triệu đồng", "tỷ đồng"]
    i = 0
    while(money >= 1000):
        if i == 3:
            break
        i = i + 1
        money = money/1000  
    

    return f"{round(money, 1)} {unit[i]}"


def decompact_money(money_string):
    unit = {
        'VNĐ': 1,
        'nghìn đồng': 1000,
        'triệu đồng': 1000000,
        'tỷ đồng': 1000000000
    }
    money = str(money_string).split(' ', 1)

    return float(money[0]) * unit[f'{money[1]}']


def check_expire_post():
    posts = Posts.query.all()
    if posts:
        for post in posts:    
            if post.expire_at < datetime.now():
                if post.status == PostsStatusEnum.ACCEPTED:
                    post.status = PostsStatusEnum.EXPIRED
                    db.session.commit()
                es.delete_by_query(index=index_name, body={
                    'query': {
                        'match': {
                            'id' : post.id
                        }
                    }
                })


def delete_account_not_active():
    users = User.query.filter(User.active == False).all()
    for u in users:
        if not u.active:
            delete_user(encrypt_data(u.id))


def query_max_price_area(issales, category_id):
    if category_id == 'all':
        category_id = 'DM'
    posts = Posts.query.filter(Posts.issales == issales).filter(Posts.category_id.startswith(category_id)).filter(Posts.status == PostsStatusEnum.ACCEPTED).all()
    price = [0]
    area = []
    if posts:
        for p in posts:
            price.append(p.price)
            area.append(p.area)
    return (compact_money(max(price)), max(area))


def convert_bedrooms(bedrooms):
    return float(bedrooms.split(" ")[0])


def sort_list_by_field(lists, field):    
    sort_units = {
        "Mặc định": 'default default',
        "Giá giảm dần": 'price descending',
        "Giá tăng dần": 'price ascending',
        "Diện tích giảm dần": 'area descending',
        "Diện tích tăng dần": 'area ascending',
        "Số phòng ngủ giảm dần": 'bedrooms descending',
        "Số phòng ngủ tăng dần": 'bedrooms ascending',
    }
    obj = sort_units[field.strip()]
    field = obj.split(' ')[0]
    option = obj.split(' ')[1]
    if field == 'price':
        lists.sort(key=lambda x: decompact_money(x[field]))
    elif field == 'bedrooms':
        lists.sort(key=lambda x: convert_bedrooms(x[field]))
    elif field == 'area':
        lists.sort(key=lambda x: float(x[field]))
    if option == "descending":        
        lists.reverse()


def filter_results_by_text(lists, field, value):
    try: 
        if float(value) >= 5:
            return list(filter(lambda x: float(str(x[field]).split(" ")[0]) >= 5, lists))
    except:
        return list(filter(lambda x: str(x[field]).__contains__(value), lists))


def filter_results_by_range(lists, field, min, max, max_str):
    if field == 'price':
        max_price = decompact_money(max_str)
        step = max_price/200
        return list(filter(lambda x: (float(min) * step) <= decompact_money(x[field]) <= (float(max) * step), lists))
    max_area = float(max_str)
    step = max_area/200
    return list(filter(lambda x: (float(min) * step) <= x[field] <= (float(max) * step), lists))
    

def increase_view(post_id):
    post = get_post_by_id(post_id)
    if post:
        post.view = post.view + 1
        db.session.commit()


def address_to_location(address):
    url = 'https://api.geoapify.com/v1/geocode/search'

    params = dict(
        text=address,
        apiKey='0995357a8a7342f49a53bf3405c86f79'
    )

    resp = requests.get(url=url, params=params)
    data = resp.json()

    return (data['features'][0]['properties']['lat'], data['features'][0]['properties']['lon'])


def count_request_user():
    register_total = User.query.filter(User.user_role == UserRoleEnum.HALF_PUBLISHER).count()
    delete_total = User.query.filter(User.user_role == UserRoleEnum.WAITING_DELETE).count()

    return [register_total, delete_total]


def count_new_notify():
    new_request_user = count_request_user()
    (new_posts, _) = stats_post()
    (new_reports, _) = stats_report()
    if all(user==0 for user in new_request_user) and new_posts == 0 and new_reports == 0:
        return False
    return True


