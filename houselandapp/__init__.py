from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_mail import Mail
from flask_socketio import SocketIO
import cloudinary
from authlib.integrations.flask_client import OAuth
from cryptography.fernet import Fernet
from werkzeug.utils import secure_filename
from elasticsearch import Elasticsearch

app = Flask(__name__)
oauth = OAuth(app)


app.secret_key = '$#&*&%$(*&^(*^*&%^%$#^%&^%*&56547648764%$#^%$&^'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:10102002@localhost/house_land_db?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'afforda2002@gmail.com'
app.config['MAIL_PASSWORD'] = 'vijxvvelqybqziym'
app.config['MAIL_USE_SSL'] = True
app.config['PAGE_SIZE'] = 8
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['MAX_CONTENT_LENGTH'] = 5242880
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
app.config['UPLOAD_PATH'] = 'houselandapp\\static\\uploads'
app.config['ELASTIC_PASSWORD'] = 'elastic'
app.config['GOOGLE_CLIENT_ID'] = "262961868820-v1rc6jpg7a0d7ie04e1jaeugpbpmfl9h.apps.googleusercontent.com"
app.config['GOOGLE_CLIENT_SECRET'] = "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"


oauth.register(
    name = 'google',
    client_id = app.config["GOOGLE_CLIENT_ID"],
    client_secret = app.config["GOOGLE_CLIENT_SECRET"],
    client_kwargs = {'scope': 'openid email profile'},
    server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration'
)

db = SQLAlchemy(app=app)
login = LoginManager(app=app)
mail = Mail(app)
socketio = SocketIO(app)
es = Elasticsearch("https://1b3416f1a7e84732b3f4b3d3a61672e3.us-central1.gcp.cloud.es.io:9243", api_key='YWFhME5wQUJDUTNteEtZNDBOTXY6V3c1cDdoTm9SZU9EYjRVcnlLLVBidw==')
index_name = "house_land_index"
if not es.indices.exists(index=index_name):
    # es.indices.delete(index=index_name)
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "id": {"type":"integer"},
                "title": {"type": "text"},
                "description": {"type": "text"},
                "address": {"type": "text"},
                "location": {
                    "type": "geo_point"
                },
                "price": {"type": "text"},
                "area": {"type": "text"},
                "bedrooms": {"type": "text"},
                "type_of": {"type": "text"},
                "furniture": {"type": "text"},
                "updated_at": {"type": "text"},
                "category": {"type": "text"},
                "issales": {"type": "text"},
                "image": {"type": "text"}
            }
        }
    }

    es.indices.create(index=index_name, body=settings) 
    
cloudinary.config(cloud_name='di4bpbe6z', api_key='345262598919953', api_secret='DihDgpCcIDzgAunCIw8Gy90MuGw')


def get_locale():
    return 'vi'


babel = Babel(app)
babel.init_app(app, locale_selector=get_locale)

encryption_key = Fernet.generate_key()
fernet = Fernet(encryption_key)