from sqlalchemy import Column, Integer, Boolean, Float, String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship, backref
from houselandapp import db, app
from enum import Enum as SystemEnum
from flask_login import UserMixin
from datetime import datetime
import hashlib

class UserRoleEnum(SystemEnum):
    USER = 2
    ADMIN = 1
    HALF_PUBLISHER=3
    PUBLISHER=4
    WAITING_DELETE=5
    RESTRICTED = 6


class PostsStatusEnum(SystemEnum):
    WAITING = 'Chờ duyệt'
    EDITED = 'Đã chỉnh sửa'
    ACCEPTED = 'Đã được duyệt'
    HIDDEN = 'Đã bị ẩn'
    EXPIRED = 'Đã hết hạn'
    RENTED = 'Đã cho thuê'
    SOLD = 'Đã bán'


class LogActionEnum(SystemEnum):
    LOGIN = 'Đã đăng nhập'
    VIEW = 'Đã xem'
    SAVED = 'Đã lưu'



class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class Conversation(BaseModel):
    __tablename__ = 'conservation'

    started_by = Column(Integer, ForeignKey('user.id', ondelete='SET NULL'), nullable=False)
    receive_by = Column(Integer, ForeignKey('user.id', ondelete='SET NULL'), nullable=False)
    created_at = Column(db.DateTime(), default=datetime.now())
    updated_at = Column(db.DateTime())

    user_send = relationship("User", foreign_keys=[started_by],
                                passive_deletes=True, cascade="all, delete")
    user_receive = relationship("User", foreign_keys=[receive_by],
                              passive_deletes=True, cascade="all, delete")

    messages = relationship('Message', backref='conversation', lazy='dynamic')


class Message(BaseModel):
    __tablename__ = 'message'

    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime(), default=datetime.now())
    is_seen = Column(Boolean, nullable=False, default=False)
    sent_from = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conservation.id', ondelete='CASCADE'), nullable=False)

    def __str__(self):
        return self.content


class Identifier(db.Model):
    __tablename__ = 'identifier'

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    id_code = Column(String(100), unique=True)
    full_name = Column(Text)
    gender = Column(Boolean)
    dob = Column(DateTime)
    address = Column(String(100))
    register_date = Column(DateTime)
    at = Column(String(200))
    expire_at = Column(DateTime)
    restrict_from = Column(DateTime, default=datetime.now())
    restrict_to = Column(DateTime, default=datetime.now())
    accept_at = Column(DateTime, default=datetime.now())

class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    name = Column(String(40)) 
    phone = Column(String(10), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(100))
    avatar = Column(Text)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER)
    active = Column(Boolean, default=True)
    date_created = Column(DateTime, default=datetime.now())
    city = Column(String(200))
    description = Column(db.Text)
    otp_code = Column(String(32))

    posts = relationship('Posts', backref='user', lazy=False)

    reports = relationship('Reports', backref=backref("User", lazy=True), cascade="all, delete")

    message = relationship('Message', backref=backref("User", lazy=True), cascade="all, delete")

    user_review= relationship("UserReview", primaryjoin="UserReview.user_id==User.id",
                                     backref="user_review", lazy=True, cascade="all, delete")
    
    publisher_review = relationship("UserReview", primaryjoin="UserReview.publisher_id==User.id",
                                    backref="publisher_review", lazy=True, cascade="all, delete")
    
    logs = relationship('Logs', backref=(backref('User', lazy=True)), cascade='all, delete')

    def __str__(self):
        return self.name
    

class UserReview(BaseModel):
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'))
    publisher_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'))
    rating = Column(Integer)
    content = Column(Text)
    review_at = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content
    

class Category(db.Model):
    __tablename__ = 'category'

    id = Column(String(5), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    posts = relationship('Posts', backref='category', lazy=False)

    def __str__(self):
        return self.name


class Posts(BaseModel):
    __tablename__ = 'posts'

    title = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(Enum(PostsStatusEnum), nullable=False)
    updated_at = Column(DateTime, default=datetime.now())
    created_at = Column(DateTime, default=datetime.now())
    expire_at = Column(DateTime, nullable=False)
    view = Column(Integer, default=0)
    
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    floor = Column(Integer)
    
    area = Column(Float, default=0)
    price = Column(Float, default=0)
    address = Column(Text, nullable=False)
    lat = Column(Float)
    lon = Column(Float)
    policy = Column(String(50), nullable=False)
    direction = Column(String(8))
    furniture = Column(String(100))
    type = Column(String(100))
    issales = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'))
    category_id = Column(String(5), ForeignKey(Category.id), nullable=False)

    logs = relationship('Logs', backref=backref('posts', lazy=True))
    user_report = relationship('Reports', backref=backref('posts', lazy=True))
    images = relationship('Images', backref='posts', lazy=False)
    

    def __str__(self):
        return self.title

    def to_lower(self):
        return self.address.lower()


class Reports(db.Model):
    __tablename__ = 'reports'
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    post_id = Column(Integer, ForeignKey(Posts.id, ondelete='CASCADE'), primary_key=True)
    content = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    date_report = Column(DateTime, nullable=False, default=datetime.now())
    date_handle = Column(DateTime)

    def __str__(self):
        return self.id


class Images(BaseModel):
    __tablename__ = 'images'

    url = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey(Posts.id, ondelete='CASCADE'))
    date_update = Column(DateTime, nullable=False)

    def __str__(self):
        return self.url
    

class Logs(BaseModel):
    __tablename__ = 'logs'
    post_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    date = Column(DateTime, default=datetime.now())
    action = Column(Enum(LogActionEnum))

    def __str__(self) -> str:
        return self.action


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.session.commit()

        db.create_all()
        db.session.commit()
