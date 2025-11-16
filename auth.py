from app import app, mysql, bcrypt
from flask import request, jsonify, session, render_template, redirect, url_for


# 🎯 로그인 페이지 (GET)
@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


# 🎯 로그인 처리 (POST)
@app.route("/login", methods=["POST"])
def login():
    data = request.form   # ← HTML Form 방식
    username = data.get('username')
    password = data.get('password')

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, password FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()

    if user and bcrypt.check_password_hash(user[1], password):
        session['user_id'] = user[0]
        return redirect("/dashboard")   # 로그인 성공 시 페이지 이동
    else:
        return render_template("login.html", error="아이디 또는 비밀번호가 틀렸습니다")


# 🎯 회원가입 페이지 (GET)
@app.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")


# 🎯 회원가입 처리 (POST)
@app.route("/signup", methods=["POST"])
def register():
    data = request.form   # ← HTML Form 방식
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_pw)
        )
        mysql.connection.commit()
        return redirect("/login")     # 성공 시 로그인 페이지로 이동
    except Exception as e:
        return render_template("signup.html", error=str(e))
    finally:
        cur.close()
