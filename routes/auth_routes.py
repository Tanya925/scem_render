# 主要功能：負責「後台登入身分驗證相關的網址」

from flask import Blueprint, render_template, session, redirect, url_for, request
from werkzeug.security import check_password_hash  # 用來比對使用者輸入密碼與資料庫中的加密密碼

from database import get_db_connection, ensure_admin_table  # 匯入共用的資料庫連線函式


# 後台登入相關路由，統一加上 /0630_SCEMadmin 前綴。
# auth_bp 是這個 Blueprint 的名稱。Blueprint功能是把一組路由集中管理，之後再統一註冊到 Flask app 裡
auth_bp = Blueprint("auth", __name__, url_prefix="/0630_SCEMadmin")


# 設定一個後台登入頁的網址(/0630_SCEMadmin/login)
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    ensure_admin_table()

    # 如果目前已經登入，就不需要再看登入頁，直接導向後台首頁
    if "admin_id" in session:
        return redirect(url_for("admin.dashboard"))

    # 預設先不顯示錯誤訊息，只有登入失敗時才會帶訊息回畫面
    error_message = None

    # 當使用者按下登入按鈕後，表單會以 POST 方式送到同一個網址
    if request.method == "POST":
        # 取得登入表單中輸入的帳號與密碼，並去掉前後空白
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # 如果帳號或密碼沒有填，就直接回登入頁並提示
        if not username or not password:
            error_message = "請輸入帳號與密碼"
            return render_template("admin_login.html", error_message=error_message)

        # 連接資料庫，查詢是否存在這個管理員帳號
        connection = get_db_connection()
        admin = connection.execute(
            "SELECT * FROM admin WHERE username = ?",
            (username,)
        ).fetchone()
        connection.close()

        # 比對結果分成兩種失敗情況：
        # 1. 查無此帳號
        # 2. 帳號存在，但密碼錯誤
        if admin is None or not check_password_hash(admin["password_hash"], password):
            error_message = "帳號或密碼錯誤"
            return render_template("admin_login.html", error_message=error_message)

        # 驗證成功後，把管理員資訊寫進 session，代表目前已登入
        session.permanent = True
        session["admin_id"] = admin["id"]
        session["admin_username"] = admin["username"]

        # 登入成功後，導向後台首頁
        return redirect(url_for("admin.dashboard"))

    # 第一次進入登入頁時，直接顯示表單畫面
    return render_template("admin_login.html", error_message=error_message)


# 設定一個後台登出頁的網址(/0630_SCEMadmin/logout)
@auth_bp.route("/logout")
def logout():
    # 清除目前使用者的 Session 資料。
    session.clear()

    # 登出完成後，跳回後台登入頁。
    # 要用 redirect() 搭配 url_for()，這樣網址才會改變
    # 寫成 auth.login 是因為在 Blueprint 建立時，第一個參數是 "auth"，所以這裡要用 auth.login 來指定 login() 函式
    return redirect(url_for("auth.login"))
