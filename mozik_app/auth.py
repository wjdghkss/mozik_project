from app import app, mysql, bcrypt
from flask import request, jsonify, session

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                    (username, email, hashed_pw))
        mysql.connection.commit()
        return jsonify({"message": "회원가입 성공"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, password FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()

    if user and bcrypt.check_password_hash(user[1], password):
        session['user_id'] = user[0]
        return jsonify({"message": "로그인 성공"})
    else:
        return jsonify({"error": "아이디 또는 비밀번호가 틀렸습니다"}), 401
