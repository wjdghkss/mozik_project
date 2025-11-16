from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask import session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MariaDB 연결
app.config['MYSQL_HOST'] = '211.253.27.46'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2025'
app.config['MYSQL_DB'] = 'mozik_db'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# 세션 설정
app.config['SESSION_TYPE'] = 'filesystem'

# 라우터 등록
from auth import *
from mosaic_api import *

@app.route('/')
def home():
    return "Flask server is running!"
