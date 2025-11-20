import os
import time
import smtplib
from email.message import EmailMessage
import requests

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory,
    send_file,
)
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image
from requests.exceptions import RequestException  # ★ 누락되었던 부분 추가

# ---------------------------
# Flask 앱 / DB 설정
# ---------------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"  # 적당한 랜덤 값으로 바꿔도 됨이다.
# 이메일/SMTP 설정
app.config["SMTP_HOST"] = os.getenv("SMTP_HOST", "smtp.gmail.com")
app.config["SMTP_PORT"] = int(os.getenv("SMTP_PORT", "587"))
app.config["SMTP_USER"] = os.getenv("SMTP_USER", "")
app.config["SMTP_PASSWORD"] = os.getenv("SMTP_PASSWORD", "")
app.config["SMTP_SENDER"] = os.getenv("SMTP_SENDER", app.config["SMTP_USER"])
app.config["BASE_URL"] = os.getenv("BASE_URL", "http://127.0.0.1:5000")

# MariaDB 연결 설정
app.config["MYSQL_HOST"] = "211.253.27.46"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "gkrcjf0821"
app.config["MYSQL_DB"] = "mozik_db"
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"  # auth.py에서 dict 접근 쓸 거면 주석 해제하면 됨이다.

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# 세션 설정: 브라우저를 닫으면 세션이 사라지도록 설정
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# 브라우저 세션 쿠키 (만료 시간 없음 = 브라우저를 닫으면 사라짐)

# ---------------------------
# 업로드 폴더 설정
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 모자이크 API 서버 주소
# 같은 Flask 앱의 /api/mosaic 엔드포인트를 호출하는 구조이다.
MOSAIC_API_URL = "http://127.0.0.1:5000/api/mosaic"


# ---------------------------
# 기본 라우트 (홈 = base.html)
# ---------------------------
@app.route("/")
def home():
    return render_template("base.html")


# ---------------------------
# 동영상 업로드 / 모자이크 처리 라우트
# ---------------------------
@app.route("/video", methods=["GET", "POST"])
def upload_video():
    # 로그인 여부 확인
    if "user_id" not in session:
        return redirect(url_for("login"))

    # GET 요청이면 동영상 업로드 폼만 보여준다.
    if request.method == "GET":
        return render_template("video.html")

    # POST 요청 (폼에서 파일 업로드)
    if "file" not in request.files:
        return "파일이 전송되지 않았음이다.", 400

    file = request.files["file"]

    if file.filename == "":
        return "선택된 파일이 없음이다.", 400

    # 파일 이름 안전하게 변환 후 저장
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    # ---------------------------
    # 모자이크 API 호출
    # ---------------------------
    try:
        with open(input_path, "rb") as f:
            resp = requests.post(
                MOSAIC_API_URL,
                files={"file": f},
                timeout=60,
            )
    except RequestException as e:
        app.logger.exception("모자이크 API 서버 호출 중 예외 발생")
        return f"모자이크 API 서버 호출 중 예외 발생: {e}", 502

    # 정상 응답(200)이 아니면 실패로 처리한다.
    if resp.status_code != 200:
        app.logger.error(
            "모자이크 API 호출 실패: status=%s, body=%s",
            resp.status_code,
            resp.text[:200],
        )
        return (
            f"모자이크 API 호출 실패임이다. "
            f"status={resp.status_code}, body={resp.text}",
            502,
        )

    # 모자이크 API가 이미지 바이너리를 바로 돌려준다고 가정한다.
    out_name = "mosaic_" + filename
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], out_name)
    with open(output_path, "wb") as out_f:
        out_f.write(resp.content)

    # 작업 기록 DB에 저장
    user_id = session.get("user_id")
    blur_strength = request.form.get("blur_strength", "0")
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO job_history (user_id, original_filename, output_filename, blur_strength, status) VALUES (%s, %s, %s, %s, %s)",
            (user_id, filename, out_name, blur_strength, "success"),
        )
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        app.logger.error(f"작업 기록 저장 실패: {e}")

    # 결과 페이지 렌더링 (모자이크된 이미지 보여주기)
    return render_template(
        "result.html",
        image_url=url_for("uploaded_file", filename=out_name),
    )


# ---------------------------
# 사진 업로드 / 모자이크 처리 라우트
# ---------------------------
@app.route("/image", methods=["GET", "POST"])
def upload_image():
    # 로그인 여부 확인
    if "user_id" not in session:
        return redirect(url_for("login"))

    # GET 요청이면 사진 업로드 폼만 보여준다.
    if request.method == "GET":
        return render_template("image.html")

    # POST 요청 (폼에서 파일 업로드)
    if "file" not in request.files:
        return "파일이 전송되지 않았음이다.", 400

    file = request.files["file"]

    if file.filename == "":
        return "선택된 파일이 없음이다.", 400

    # 파일 이름 안전하게 변환 후 저장
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    # ---------------------------
    # 모자이크 API 호출
    # ---------------------------
    try:
        with open(input_path, "rb") as f:
            resp = requests.post(
                MOSAIC_API_URL,
                files={"file": f},
                timeout=60,
            )
    except RequestException as e:
        app.logger.exception("모자이크 API 서버 호출 중 예외 발생")
        return f"모자이크 API 서버 호출 중 예외 발생: {e}", 502

    # 정상 응답(200)이 아니면 실패로 처리한다.
    if resp.status_code != 200:
        app.logger.error(
            "모자이크 API 호출 실패: status=%s, body=%s",
            resp.status_code,
            resp.text[:200],
        )
        return (
            f"모자이크 API 호출 실패임이다. "
            f"status={resp.status_code}, body={resp.text}",
            502,
        )

    # 모자이크 API가 이미지 바이너리를 바로 돌려준다고 가정한다.
    out_name = "mosaic_" + filename
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], out_name)
    with open(output_path, "wb") as out_f:
        out_f.write(resp.content)

    # 작업 기록 DB에 저장
    user_id = session.get("user_id")
    blur_strength = request.form.get("blur_strength", "0")
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO job_history (user_id, original_filename, output_filename, blur_strength, status) VALUES (%s, %s, %s, %s, %s)",
            (user_id, filename, out_name, blur_strength, "success"),
        )
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        app.logger.error(f"작업 기록 저장 실패: {e}")

    # 결과 페이지 렌더링 (모자이크된 이미지 보여주기)
    return render_template(
        "result.html",
        image_url=url_for("uploaded_file", filename=out_name),
    )


# ---------------------------
# 내부 모자이크 API (테스트용)
# ---------------------------
@app.route("/api/mosaic", methods=["POST"])
def api_mosaic():
    """
    업로드된 이미지를 받아서 모자이크 처리 후 다시 돌려주는 API이다.
    지금은 테스트용으로 '원본 그대로' 돌려준다.
    나중에 여기 안에 실제 모자이크 처리 코드를 넣으면 된다.
    """
    if "file" not in request.files:
        return "file 필드가 없음이다.", 400

    up_file = request.files["file"]
    if up_file.filename == "":
        return "파일명이 비어 있음이다.", 400

    try:
        # 업로드된 파일을 PIL 이미지로 열기
        img = Image.open(up_file.stream).convert("RGB")

        # TODO: 여기에서 img에 모자이크 처리 로직을 적용하면 됨이다.
        # 예: img = do_mosaic(img)

        # 다시 바이너리로 변환해서 응답
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return send_file(buf, mimetype="image/jpeg")
    except Exception as e:
        return f"모자이크 처리 중 오류 발생임이다: {e}", 500


# 업로드된 파일을 직접 서빙하는 라우트
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------------------------
# 인증 / 기타 라우트 가져오기
# ---------------------------
def send_reset_email(to_email: str, token: str) -> None:
    """
    비밀번호 재설정 링크를 포함한 이메일을 발송한다.
    SMTP 설정이 비어 있으면 로깅만 수행한다.
    """
    reset_url = f"{app.config['BASE_URL']}/reset-password/{token}"
    subject = "[Mozik] 비밀번호 재설정 안내"
    body = (
        "안녕하세요.\n\n"
        "요청하신 비밀번호 재설정 링크는 아래와 같습니다.\n"
        f"{reset_url}\n\n"
        "본인이 요청하지 않았다면 이 메일을 무시하세요.\n"
        "링크는 1시간 후 만료됩니다.\n"
    )

    if not app.config["SMTP_USER"] or not app.config["SMTP_PASSWORD"]:
        app.logger.warning("SMTP 설정이 비어 있어 이메일을 보내지 못했습니다.")
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = app.config["SMTP_SENDER"]
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(app.config["SMTP_HOST"], app.config["SMTP_PORT"]) as smtp:
            smtp.starttls()
            smtp.login(app.config["SMTP_USER"], app.config["SMTP_PASSWORD"])
            smtp.send_message(message)
    except Exception as exc:
        app.logger.exception("비밀번호 재설정 메일 전송 실패: %s", exc)


from auth import *  # auth.py에서 /signup, /login, /logout 등을 정의한다고 가정함이다.


# ---------------------------
# 작업 기록 조회 라우트
# ---------------------------
@app.route("/history")
def history():
    # 로그인 여부 확인
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    
    # 사용자 정보 조회
    user_info = {
        "id": user_id,
        "email": "",
        "name": "사용자",
        "plan": "Free",
        "credits": 0,
    }
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id, email, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        user_data = cur.fetchone()
        if user_data:
            # 이메일에서 이름 추출 (이메일 앞부분 사용)
            email = user_data[1] if user_data[1] else ""
            user_name = email.split("@")[0] if email else "사용자"
            user_info = {
                "id": user_data[0],
                "email": email,
                "name": user_name,
                "plan": "Free",  # 기본값
                "credits": 0,  # 기본값
            }
        cur.close()
    except Exception as e:
        app.logger.error(f"사용자 정보 조회 실패: {e}")
        # 기본값 유지
    
    # 필터 파라미터
    filter_type = request.args.get("filter", "all")  # all, editing, completed
    date_filter = request.args.get("date", "all")  # all, 24h, week, month
    tab_type = request.args.get("tab", "all")  # all, video, image
    
    # 사용자의 작업 기록 조회
    try:
        cur = mysql.connection.cursor()
        
        # 기본 쿼리
        query = "SELECT id, original_filename, output_filename, blur_strength, status, created_at FROM job_history WHERE user_id = %s"
        params = [user_id]
        
        # 상태 필터
        if filter_type == "editing":
            query += " AND status = 'processing'"
        elif filter_type == "completed":
            query += " AND status = 'success'"
        
        # 날짜 필터
        if date_filter == "24h":
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)"
        elif date_filter == "week":
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        elif date_filter == "month":
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
        
        # 파일 타입 필터 (파일 확장자로 판단)
        if tab_type == "video":
            query += " AND (original_filename LIKE '%.mp4' OR original_filename LIKE '%.avi' OR original_filename LIKE '%.mov' OR original_filename LIKE '%.mkv' OR original_filename LIKE '%.MP4' OR original_filename LIKE '%.AVI' OR original_filename LIKE '%.MOV' OR original_filename LIKE '%.MKV')"
        elif tab_type == "image":
            query += " AND (original_filename LIKE '%.jpg' OR original_filename LIKE '%.jpeg' OR original_filename LIKE '%.png' OR original_filename LIKE '%.gif' OR original_filename LIKE '%.JPG' OR original_filename LIKE '%.JPEG' OR original_filename LIKE '%.PNG' OR original_filename LIKE '%.GIF')"
        
        query += " ORDER BY created_at DESC"
        
        try:
            cur.execute(query, tuple(params))
            jobs = cur.fetchall()
        except Exception as query_error:
            app.logger.error(f"SQL 쿼리 실행 실패: {query_error}")
            app.logger.error(f"쿼리: {query}")
            app.logger.error(f"파라미터: {params}")
            jobs = []
        finally:
            cur.close()
        
        # 튜플을 딕셔너리 형태로 변환
        job_list = []
        for job in jobs:
            try:
                # 파일 타입 판단
                filename = job[1] if job[1] else ""
                file_type = "image" if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']) else "video"
                
                job_list.append({
                    "id": job[0],
                    "original_filename": job[1] if job[1] else "알 수 없음",
                    "output_filename": job[2] if job[2] else "",
                    "blur_strength": job[3] if job[3] is not None else "0",
                    "status": job[4] if job[4] else "unknown",
                    "created_at": job[5],  # datetime 객체 또는 None
                    "file_type": file_type,
                })
            except Exception as job_error:
                app.logger.error(f"작업 데이터 변환 실패: {job_error}")
                continue
    except Exception as e:
        app.logger.error(f"작업 기록 조회 실패: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        job_list = []
    
    # 기본값 보장
    filter_type = filter_type or "all"
    date_filter = date_filter or "all"
    tab_type = tab_type or "all"
    
    try:
        return render_template(
            "history.html",
            jobs=job_list,
            user_info=user_info,
            filter_type=filter_type,
            date_filter=date_filter,
            tab_type=tab_type,
        )
    except Exception as template_error:
        import traceback
        error_msg = traceback.format_exc()
        app.logger.error(f"템플릿 렌더링 실패: {error_msg}")
        app.logger.error(f"user_info: {user_info}")
        app.logger.error(f"jobs count: {len(job_list)}")
        raise


# ---------------------------
# 마이페이지 라우트
# ---------------------------
@app.route("/mypage")
def mypage():
    # 로그인 여부 확인
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    
    # 사용자 정보 조회
    user_info = {
        "id": user_id,
        "email": "",
        "name": "사용자",
        "plan": "Free",
        "credits": 0,
        "face_image": None,
    }
    try:
        cur = mysql.connection.cursor()
        # face_image 컬럼이 있는지 확인하고 조회
        cur.execute("SHOW COLUMNS FROM users LIKE 'face_image'")
        has_face_image = cur.fetchone()
        
        if has_face_image:
            cur.execute(
                "SELECT id, email, face_image FROM users WHERE id = %s",
                (user_id,),
            )
        else:
            cur.execute(
                "SELECT id, email FROM users WHERE id = %s",
                (user_id,),
            )
        
        user_data = cur.fetchone()
        if user_data:
            email = user_data[1] if user_data[1] else ""
            user_name = email.split("@")[0] if email else "사용자"
            face_image = user_data[2] if has_face_image and len(user_data) > 2 else None
            user_info = {
                "id": user_data[0],
                "email": email,
                "name": user_name,
                "plan": "Free",
                "credits": 0,
                "face_image": face_image,
            }
        cur.close()
    except Exception as e:
        app.logger.error(f"사용자 정보 조회 실패: {e}")
    
    return render_template("mypage.html", user_info=user_info, messages=[])


@app.route("/change_email", methods=["POST"])
def change_email():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    new_email = request.form.get("new_email", "").strip()
    password = request.form.get("password", "")
    
    messages = []
    
    if not new_email or not password:
        messages.append({"type": "error", "text": "이메일과 비밀번호를 모두 입력해주세요."})
        return render_template("mypage.html", user_info={"id": user_id, "email": "", "name": "사용자"}, messages=messages)
    
    try:
        cur = mysql.connection.cursor()
        
        # 현재 비밀번호 확인
        cur.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user or not bcrypt.check_password_hash(user[0], password):
            messages.append({"type": "error", "text": "비밀번호가 올바르지 않습니다."})
            cur.close()
            return render_template("mypage.html", user_info={"id": user_id, "email": "", "name": "사용자"}, messages=messages)
        
        # 이메일 중복 확인
        cur.execute("SELECT id FROM users WHERE email = %s AND id != %s", (new_email, user_id))
        if cur.fetchone():
            messages.append({"type": "error", "text": "이미 사용 중인 이메일입니다."})
            cur.close()
            return render_template("mypage.html", user_info={"id": user_id, "email": "", "name": "사용자"}, messages=messages)
        
        # 이메일 변경
        cur.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, user_id))
        mysql.connection.commit()
        messages.append({"type": "success", "text": "이메일이 성공적으로 변경되었습니다."})
        cur.close()
    except Exception as e:
        mysql.connection.rollback()
        app.logger.error(f"이메일 변경 실패: {e}")
        messages.append({"type": "error", "text": f"이메일 변경 중 오류가 발생했습니다: {e}"})
    
    # 사용자 정보 다시 조회
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, email, COALESCE(face_image, '') as face_image FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        if user_data:
            email = user_data[1] if user_data[1] else ""
            user_name = email.split("@")[0] if email else "사용자"
            face_image = user_data[2] if len(user_data) > 2 and user_data[2] else None
            user_info = {
                "id": user_data[0],
                "email": email,
                "name": user_name,
                "plan": "Free",
                "credits": 0,
                "face_image": face_image,
            }
        else:
            user_info = {"id": user_id, "email": new_email, "name": new_email.split("@")[0] if new_email else "사용자", "face_image": None}
        cur.close()
    except Exception as e:
        app.logger.error(f"사용자 정보 조회 실패: {e}")
        user_info = {"id": user_id, "email": new_email, "name": new_email.split("@")[0] if new_email else "사용자", "face_image": None}
    
    return render_template("mypage.html", user_info=user_info, messages=messages)


@app.route("/change_password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")
    
    messages = []
    
    if not current_password or not new_password or not confirm_password:
        messages.append({"type": "error", "text": "모든 필드를 입력해주세요."})
        return render_template("mypage.html", user_info={"id": user_id, "email": "", "name": "사용자"}, messages=messages)
    
    if new_password != confirm_password:
        messages.append({"type": "error", "text": "새 비밀번호가 일치하지 않습니다."})
        return render_template("mypage.html", user_info={"id": user_id, "email": "", "name": "사용자"}, messages=messages)
    
    try:
        cur = mysql.connection.cursor()
        
        # 현재 비밀번호 확인
        cur.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user or not bcrypt.check_password_hash(user[0], current_password):
            messages.append({"type": "error", "text": "현재 비밀번호가 올바르지 않습니다."})
            cur.close()
            return render_template("mypage.html", user_info={"id": user_id, "email": "", "name": "사용자"}, messages=messages)
        
        # 비밀번호 변경
        hashed_pw = bcrypt.generate_password_hash(new_password).decode("utf-8")
        cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_pw, user_id))
        mysql.connection.commit()
        messages.append({"type": "success", "text": "비밀번호가 성공적으로 변경되었습니다."})
        cur.close()
    except Exception as e:
        mysql.connection.rollback()
        app.logger.error(f"비밀번호 변경 실패: {e}")
        messages.append({"type": "error", "text": f"비밀번호 변경 중 오류가 발생했습니다: {e}"})
    
    # 사용자 정보 다시 조회
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, email, COALESCE(face_image, '') as face_image FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        if user_data:
            email = user_data[1] if user_data[1] else ""
            user_name = email.split("@")[0] if email else "사용자"
            face_image = user_data[2] if len(user_data) > 2 and user_data[2] else None
            user_info = {
                "id": user_data[0],
                "email": email,
                "name": user_name,
                "plan": "Free",
                "credits": 0,
                "face_image": face_image,
            }
        else:
            user_info = {"id": user_id, "email": "", "name": "사용자", "face_image": None}
        cur.close()
    except Exception as e:
        app.logger.error(f"사용자 정보 조회 실패: {e}")
        user_info = {"id": user_id, "email": "", "name": "사용자", "face_image": None}
    
    return render_template("mypage.html", user_info=user_info, messages=messages)


@app.route("/register_face", methods=["POST"])
def register_face():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    messages = []
    
    # 얼굴 등록은 선택사항이므로 파일이 없어도 에러를 발생시키지 않음
    if "face_image" not in request.files:
        messages.append({"type": "error", "text": "파일이 선택되지 않았습니다."})
        # 사용자 정보 다시 조회
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, email, COALESCE(face_image, '') as face_image FROM users WHERE id = %s", (user_id,))
            user_data = cur.fetchone()
            if user_data:
                email = user_data[1] if user_data[1] else ""
                user_name = email.split("@")[0] if email else "사용자"
                face_image = user_data[2] if len(user_data) > 2 and user_data[2] else None
                user_info = {
                    "id": user_data[0],
                    "email": email,
                    "name": user_name,
                    "plan": "Free",
                    "credits": 0,
                    "face_image": face_image,
                }
            else:
                user_info = {"id": user_id, "email": "", "name": "사용자", "face_image": None}
            cur.close()
        except Exception as e:
            app.logger.error(f"사용자 정보 조회 실패: {e}")
            user_info = {"id": user_id, "email": "", "name": "사용자", "face_image": None}
        return render_template("mypage.html", user_info=user_info, messages=messages)
    
    file = request.files["face_image"]
    if file.filename == "":
        # 파일이 선택되지 않았지만 선택사항이므로 성공 메시지와 함께 반환
        messages.append({"type": "success", "text": "변경사항이 없습니다."})
        # 사용자 정보 다시 조회
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, email, COALESCE(face_image, '') as face_image FROM users WHERE id = %s", (user_id,))
            user_data = cur.fetchone()
            if user_data:
                email = user_data[1] if user_data[1] else ""
                user_name = email.split("@")[0] if email else "사용자"
                face_image = user_data[2] if len(user_data) > 2 and user_data[2] else None
                user_info = {
                    "id": user_data[0],
                    "email": email,
                    "name": user_name,
                    "plan": "Free",
                    "credits": 0,
                    "face_image": face_image,
                }
            else:
                user_info = {"id": user_id, "email": "", "name": "사용자", "face_image": None}
            cur.close()
        except Exception as e:
            app.logger.error(f"사용자 정보 조회 실패: {e}")
            user_info = {"id": user_id, "email": "", "name": "사용자", "face_image": None}
        return render_template("mypage.html", user_info=user_info, messages=messages)
    
    try:
        # 파일 저장
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"face_{user_id}_{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # DB에 파일명 저장 (users 테이블에 face_image 컬럼이 있다고 가정)
        cur = mysql.connection.cursor()
        # 만약 컬럼이 없다면 ALTER TABLE users ADD COLUMN face_image VARCHAR(255) NULL; 실행 필요
        cur.execute("UPDATE users SET face_image = %s WHERE id = %s", (filename, user_id))
        mysql.connection.commit()
        cur.close()
        
        messages.append({"type": "success", "text": "얼굴 사진이 성공적으로 등록되었습니다."})
    except Exception as e:
        mysql.connection.rollback()
        app.logger.error(f"얼굴 등록 실패: {e}")
        messages.append({"type": "error", "text": f"얼굴 등록 중 오류가 발생했습니다: {e}"})
    
    # 사용자 정보 다시 조회
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, email, face_image FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        if user_data:
            email = user_data[1] if user_data[1] else ""
            user_name = email.split("@")[0] if email else "사용자"
            face_image = user_data[2] if len(user_data) > 2 else None
            user_info = {
                "id": user_data[0],
                "email": email,
                "name": user_name,
                "plan": "Free",
                "credits": 0,
                "face_image": face_image,
            }
        else:
            user_info = {"id": user_id, "email": "", "name": "사용자", "face_image": filename if 'filename' in locals() else None}
        cur.close()
    except Exception as e:
        app.logger.error(f"사용자 정보 조회 실패: {e}")
        user_info = {"id": user_id, "email": "", "name": "사용자", "face_image": filename if 'filename' in locals() else None}
    
    return render_template("mypage.html", user_info=user_info, messages=messages)


@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    password = request.form.get("password", "")
    
    messages = []
    
    if not password:
        messages.append({"type": "error", "text": "비밀번호를 입력해주세요."})
        return render_template("mypage.html", user_info={"id": user_id, "email": "", "name": "사용자"}, messages=messages)
    
    try:
        cur = mysql.connection.cursor()
        
        # 비밀번호 확인
        cur.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user or not bcrypt.check_password_hash(user[0], password):
            messages.append({"type": "error", "text": "비밀번호가 올바르지 않습니다."})
            cur.close()
            return render_template("mypage.html", user_info={"id": user_id, "email": "", "name": "사용자"}, messages=messages)
        
        # 계정 삭제 (CASCADE로 관련 데이터도 삭제됨)
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        mysql.connection.commit()
        cur.close()
        
        # 세션 삭제
        session.clear()
        return redirect(url_for("login"))
    except Exception as e:
        mysql.connection.rollback()
        app.logger.error(f"계정 삭제 실패: {e}")
        messages.append({"type": "error", "text": f"계정 삭제 중 오류가 발생했습니다: {e}"})
        return render_template("mypage.html", user_info={"id": user_id, "email": "", "name": "사용자"}, messages=messages)


# ---------------------------
# 앱 실행 (개발용)
# ---------------------------
# 에러 핸들러 추가
@app.errorhandler(500)
def internal_error(error):
    import traceback
    error_msg = traceback.format_exc()
    app.logger.error(f"Internal Server Error: {error_msg}")
    return f"<h1>Internal Server Error</h1><pre>{error_msg}</pre>", 500

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    error_msg = traceback.format_exc()
    app.logger.error(f"Unhandled Exception: {error_msg}")
    return f"<h1>Error</h1><pre>{error_msg}</pre>", 500

if __name__ == "__main__":
    # ⚠ 여기서 app.run 과 MOSAIC_API_URL(127.0.0.1:5000/api/mosaic)을 같이 쓰면
    # 단일 프로세스/단일 스레드일 때 자기 자신을 다시 호출해서 막힐 수 있음이다.
    # 개발할 때는 api_mosaic 를 직접 호출하거나, 포트를 다르게 써도 됨이다.
    app.run(host="0.0.0.0", port=5000, debug=True)
