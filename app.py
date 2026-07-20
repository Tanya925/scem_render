import os
from datetime import timedelta

from flask import Flask, session, request

# 匯入共用的資料庫連線設定與函式
from database import (
    DATABASE_PATH,
    get_db_connection,
    ensure_default_general_info,
    ensure_default_staff,
    ensure_default_projects,
    ensure_staff_directory_columns,
    ensure_home_activity_images,
    ensure_admin_table,
)

# 匯入各功能區的路由 Blueprint，之後會統一註冊到 Flask app 裡
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.public_routes import public_bp


# 建立 Flask 應用程式主體
app = Flask(
    __name__,
    template_folder="templates",  # 指定 HTML 模板資料夾位置
    static_folder="static"  # 指定靜態檔案資料夾位置，例如 css、js、圖片
)

secret_key = os.environ.get("SECRET_KEY", "").strip()

if not secret_key:
    raise RuntimeError("SECRET_KEY environment variable is required before starting the app.")

app.config["SECRET_KEY"] = secret_key
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# 把資料庫檔案路徑存進 Flask 設定中，方便之後其他檔案直接讀取
app.config["DATABASE"] = str(DATABASE_PATH)


# 把目前前台正在使用的語言與雙語欄位取值函式提供給所有模板共用。
# 這樣 index、staff、research、project_detail 就不需要各自重複寫一堆 if/else 判斷。
@app.context_processor
def inject_template_helpers():
    current_language = session.get("language", "en")

    # 根據目前語言設定，自動從 *_en / *_th 欄位中取出對應內容。
    # 如果目前語言的欄位是空的，會自動退回另一種語言，避免畫面整塊空白。
    def field_text(data, field_name):
        if data is None:
            return ""

        primary_key = f"{field_name}_{current_language}"
        fallback_key = f"{field_name}_{'th' if current_language == 'en' else 'en'}"

        try:
            primary_value = data[primary_key]
        except (KeyError, TypeError, IndexError):
            primary_value = ""

        try:
            fallback_value = data[fallback_key]
        except (KeyError, TypeError, IndexError):
            fallback_value = ""

        return primary_value or fallback_value or ""

    # 把 General Info 的長文字整理成：
    # 1. 區塊標題
    # 2. 該區塊底下的條列內容
    # 這樣首頁就能用更像正式網站的版型顯示，而不是單純把大段文字直接印出來。
    def format_general_content(raw_text):
        if not raw_text:
            return []

        lines = [line.strip() for line in raw_text.splitlines()]
        sections = []
        current_section = None

        for line in lines:
            if not line:
                continue

            # 把和卡片標題重複的第一行略過，避免首頁出現兩次 Details and Works。
            if line in {"Details and Works", "รายละเอียดและผลงาน"}:
                continue

            if line.startswith("-"):
                if current_section is None:
                    current_section = {"title": "", "items": []}
                    sections.append(current_section)

                current_section["items"].append(line.lstrip("-").strip())
            else:
                current_section = {"title": line, "items": []}
                sections.append(current_section)

        return sections

    def overview_image_for_title(title):
        if not title:
            return None

        normalized_title = " ".join(title.lower().split())
        image_map = {
            "logistics/ supply chain strategy development": {
                "en": "EN_Logistics_ Supply Chain Strategy Development.png",
                "th": "TH_Logistics_ Supply Chain Strategy Development.png",
            },
            "การพัฒนากลยุทธ์ด้านโลจิสติกส์และโซ่อุปทาน": {
                "en": "EN_Logistics_ Supply Chain Strategy Development.png",
                "th": "TH_Logistics_ Supply Chain Strategy Development.png",
            },
            "industrial logistics": {
                "en": "EN_Industrial Logistics.png",
                "th": "TH_Industrial Logistics.png",
            },
            "โลจิสติกส์อุตสาหกรรม": {
                "en": "EN_Industrial Logistics.png",
                "th": "TH_Industrial Logistics.png",
            },
        }

        image_options = image_map.get(normalized_title)
        if not image_options:
            return None

        return image_options.get(current_language) or image_options.get("en")

    return {
        "current_language": current_language,
        "field_text": field_text,
        "format_general_content": format_general_content,
        "overview_image_for_title": overview_image_for_title,
        "current_path": request.path,
    }


# 啟動網站前先測試一次資料庫是否可以正常連上(方便 debug)
def test_db_connection():
    try:
        connection = get_db_connection()
        connection.close()
        return True
    except Exception as error:
        print(f"資料庫連線失敗：{error}")
        return False


def initialize_app_data():
    if test_db_connection():
        print("SQLite 資料庫連線成功")
        ensure_default_general_info()  # 確保 general_info 表中至少存在一筆資料，避免第一次查詢時拿到空值
        ensure_home_activity_images()  # 確保首頁活動照片清單存在，讓首頁輪播與後台管理都能直接使用
        ensure_staff_directory_columns()  # 確保現有 staff 表已補上 category / department 等 staff 目錄欄位
        ensure_default_staff()  # 確保 staff 表中至少存在一批預設人物資料，方便後續管理與前台顯示
        ensure_default_projects()  # 確保 projects 表中至少存在一批預設專案資料，方便直接測試 research 與 project detail
        ensure_admin_table()  # 確保 admin 表存在，讓新環境至少有可登入的預設管理帳號
    else:
        print("SQLite 資料庫連線失敗，請先檢查 scem.db 是否存在")



# 註冊前台、登入驗證、後台管理三組路由
app.register_blueprint(public_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
initialize_app_data()


if __name__ == "__main__":
    # 直接執行 app.py 時，以開發模式啟動網站
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "3000")),
        debug=False
    )
