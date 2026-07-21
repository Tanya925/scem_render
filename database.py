# 主要功能：建立一個共用的 SQLite 連線函式，方便其他 route 直接匯入使用

from pathlib import Path  # 用來處理檔案路徑，方便找到專案中的資料庫位置
import re
import sqlite3  # SQLite 是這個專案目前使用的資料庫
from werkzeug.security import generate_password_hash


# 取得目前 database.py 所在的專案根目錄
BASE_DIR = Path(__file__).resolve().parent
# 指定 SQLite 資料庫檔案位置，其他檔案都會共用這個路徑
DATABASE_PATH = BASE_DIR / "scem.db"
AUDIO_BASE_DIR = BASE_DIR / "static" / "audio"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


# 這是首頁 General Info 的預設資料。
# 當 general_info 資料表中還沒有任何資料時，系統會自動建立這一筆，
# 讓後台打開時就能直接看到初始內容，也讓前台首頁一開始就有資料可顯示。
DEFAULT_GENERAL_INFO = {
    "page_title_en": "Supply Chain and Engineering Management Research Unit: CMU",
    "page_title_th": "หน่วยวิจัยการจัดการโซ่อุปทานและวิศวกรรม: CMU",
    "about_title_en": "About SCEM",
    "about_title_th": "เกี่ยวกับ SCEM",
    "about_content_en": """The Supply Chain and Engineering Management Research Unit (SCEM) focuses on research in logistics, supply chain management, and engineering management.

Its research activities cover logistics and supply chain strategy development, industrial logistics, supply chain improvement, simulation and optimization, productivity improvement, and sustainability development.""",
    "about_content_th": """หน่วยวิจัยการจัดการโซ่อุปทานและวิศวกรรม (SCEM) มุ่งเน้นการวิจัยด้านโลจิสติกส์ การจัดการโซ่อุปทาน และการจัดการวิศวกรรม

กิจกรรมวิจัยครอบคลุมการพัฒนากลยุทธ์ด้านโลจิสติกส์และโซ่อุปทาน โลจิสติกส์อุตสาหกรรม การปรับปรุงโซ่อุปทาน การจำลองและการหาค่าที่เหมาะสม การเพิ่มผลิตภาพ และการพัฒนาความยั่งยืน""",
    "content_en": """Details and Works

Logistics/ Supply Chain Strategy Development

- Roadmap design for Research and Innovation ecosystem for industries, government agencies, high-skill workforces, and university talents

- Strategy development and policy suggestion for Special Economic Corridors

- Logistics assessment for Greater Mekong Subregion (GMS) and ASEAN Economic Community (AEC)

- Feasibility study and economic impact assessment

Industrial Logistics

- Supply chain redesign for small Battery Electric Vehicle (BEV), agro and food industries, logistics industries

- Performance measurement for industrial logistics

- Logistics and supply chain improvement, simulation and optimization for industries

- Productivity improvement and engineering management for industries

- Sustainability development for industries

- Logistics and supply chain for Industry 4.0 and Industry 5.0""",
    "content_th": """รายละเอียดและผลงาน

การพัฒนากลยุทธ์ด้านโลจิสติกส์และโซ่อุปทาน

- การออกแบบแผนที่นำทางสำหรับระบบนิเวศการวิจัยและนวัตกรรมสำหรับภาคอุตสาหกรรม หน่วยงานภาครัฐ บุคลากรทักษะสูง และบุคลากรที่มีศักยภาพในมหาวิทยาลัย

- การพัฒนากลยุทธ์และการเสนอแนะเชิงนโยบายสำหรับระเบียงเศรษฐกิจพิเศษ

- การประเมินด้านโลจิสติกส์สำหรับอนุภูมิภาคลุ่มแม่น้ำโขง (GMS) และประชาคมเศรษฐกิจอาเซียน (AEC)

- การศึกษาความเป็นไปได้และการประเมินผลกระทบทางเศรษฐกิจ

โลจิสติกส์อุตสาหกรรม

- การออกแบบโซ่อุปทานใหม่สำหรับอุตสาหกรรมยานยนต์ไฟฟ้าแบตเตอรี่ขนาดเล็ก (BEV) อุตสาหกรรมการเกษตรและอาหาร และอุตสาหกรรมโลจิสติกส์

- การวัดผลการดำเนินงานด้านโลจิสติกส์อุตสาหกรรม

- การปรับปรุง การจำลอง และการหาค่าที่เหมาะสมด้านโลจิสติกส์และโซ่อุปทานสำหรับภาคอุตสาหกรรม

- การปรับปรุงผลิตภาพและการจัดการวิศวกรรมสำหรับภาคอุตสาหกรรม

- การพัฒนาความยั่งยืนสำหรับภาคอุตสาหกรรม

- โลจิสติกส์และโซ่อุปทานสำหรับอุตสาหกรรม 4.0 และอุตสาหกรรม 5.0""",
    "professors_title_en": "Professors",
    "professors_title_th": "ศาสตราจารย์",
    "advisors_title_en": "Advisors",
    "advisors_title_th": "ที่ปรึกษา",
    "research_team_title_en": "Research Team",
    "research_team_title_th": "ทีมวิจัย",
}


# 首頁活動照片預設清單。
# 目前會自動抓 uploads 裡你已放好的 Info1 ~ Info6 當作首頁輪播資料來源。
DEFAULT_HOME_ACTIVITY_IMAGES = [
    "Info1.jpg",
    "Info2.jpg",
    "Info3.jpg",
    "Info4.jpg",
    "Info5.jpg",
    "Info6.jpg",
]


# 這是目前預設的 staff 名單。
# 你提供的資料會先整理成系統內部使用的格式：
# Professors -> professor
# Advisors -> advisor
# Research Team -> research_team
DEFAULT_STAFF = [
    {
        "name_en": "Assoc. Prof. Sakgasem Ramingwong, Ph.D.",
        "name_th": "รศ.ดร.ศักดิ์เกษม ระมิงค์วงศ์",
        "position_en": "Leader",
        "position_th": "หัวหน้า",
        "department_en": "Department of Industrial Engineering",
        "department_th": "ภาควิชาวิศวกรรมอุตสาหการ",
        "staff_group": "professor",
        "sort_order": 1,
        "photo_filename": "pf1.jpeg",
        "profile_url": "https://ie.eng.cmu.ac.th/en/people/faculty/129",
        "audio_en_url": "/static/audio/EN/EN_Sakgasem Ramingwong.mp3",
        "audio_th_url": "/static/audio/TH/TH_Sakgasem Ramingwong.mp3",
    },
    {
        "name_en": "Asst. Prof. Korrakot Yaibuathet Tippayawong, D.Eng",
        "name_th": "ผศ.ดร.กรกฎ ใยบัวเทศ ทิพยาวงศ์",
        "position_en": "Member",
        "position_th": "สมาชิก",
        "department_en": "Department of Industrial Engineering",
        "department_th": "ภาควิชาวิศวกรรมอุตสาหการ",
        "staff_group": "professor",
        "sort_order": 5,
        "photo_filename": "pf2.jpeg",
        "profile_url": "https://ie.eng.cmu.ac.th/people/faculty/134",
        "audio_en_url": "",
        "audio_th_url": "",
    },
    {
        "name_en": "Assoc. Prof. Dr. Sermkiat Jomjunyong",
        "name_th": "รองศาสตราจารย์ ดร.เสริมเกียรติ จอมจันทร์ยอง",
        "position_en": "",
        "position_th": "",
        "department_en": "",
        "department_th": "",
        "staff_group": "advisor",
        "sort_order": 1,
        "photo_filename": "ad1.jpg",
        "profile_url": "",
        "audio_en_url": "",
        "audio_th_url": "",
    },
    {
        "name_en": "Prim Fongsamootr",
        "name_th": "พริม ฟองสมุทร",
        "position_en": "Member",
        "position_th": "สมาชิก",
        "department_en": "Department of Industrial Engineering",
        "department_th": "ภาควิชาวิศวกรรมอุตสาหการ",
        "staff_group": "professor",
        "sort_order": 13,
        "photo_filename": "M13.png",
        "profile_url": "/static/cv/CV_Prim Fongsamootr.pdf",
        "audio_en_url": "/static/audio/EN/EN_Prim Fongsamootr.mp3",
        "audio_th_url": "/static/audio/TH/TH_Prim Fongsamootr.mp3",
    },
]


STAFF_DIRECTORY_SECTIONS = [
    {"key": "advisor", "title_en": "ADVISOR", "title_th": "ที่ปรึกษา"},
    {"key": "member", "title_en": "MEMBER", "title_th": "สมาชิก"},
    {"key": "accba", "title_en": "ACCBA", "title_th": "ACCBA"},
    {"key": "researcher", "title_en": "RESEARCHER", "title_th": "นักวิจัย"},
]

STAFF_SECTION_ORDER = {
    section["key"]: index
    for index, section in enumerate(STAFF_DIRECTORY_SECTIONS)
}


STAFF_NAME_PREFIXES = (
    "assoc",
    "associate",
    "asst",
    "assistant",
    "miss",
    "mr",
    "mrs",
    "ms",
    "prof",
    "professor",
    "dr",
    "ph",
    "d",
    "eng",
    "phd",
    "deng",
)


# 這是目前預設的 research project 範例資料。
# 在專案初期先放兩筆示範資料，方便直接測試：
# 1. ongoing 專案，可進詳細頁
# 2. finished 專案，只顯示在研究列表，不提供詳細頁連結
DEFAULT_PROJECTS = [
    {
        "staff_name_en": "Assoc. Prof. Sakgasem Ramingwong, Ph.D.",
        "project_name_en": "Logistics Strategy Development",
        "project_name_th": "การพัฒนากลยุทธ์โลจิสติกส์",
        "title_en": "Logistics Strategy Development for Industrial and Regional Supply Chains",
        "title_th": "การพัฒนากลยุทธ์โลจิสติกส์สำหรับโซ่อุปทานภาคอุตสาหกรรมและระดับภูมิภาค",
        "duration_en": "2024 - 2026",
        "duration_th": "2567 - 2569",
        "funding_en": "CMU Research Fund",
        "funding_th": "ทุนวิจัยมหาวิทยาลัยเชียงใหม่",
        "objective_en": "To develop logistics strategy frameworks for industrial sectors and regional supply chain systems, with emphasis on long-term planning, ecosystem design, and policy support.",
        "objective_th": "เพื่อพัฒนากรอบกลยุทธ์ด้านโลจิสติกส์สำหรับภาคอุตสาหกรรมและระบบโซ่อุปทานระดับภูมิภาค โดยเน้นการวางแผนระยะยาว การออกแบบระบบนิเวศ และการสนับสนุนเชิงนโยบาย",
        "project_type": "ongoing",
    },
    {
        "staff_name_en": "Asst. Prof. Korrakot Yaibuathet Tippayawong, D.Eng",
        "project_name_en": "Industrial Logistics Performance Assessment",
        "project_name_th": "การประเมินประสิทธิภาพโลจิสติกส์อุตสาหกรรม",
        "title_en": "Industrial Logistics Performance Assessment for Manufacturing and Food Supply Networks",
        "title_th": "การประเมินประสิทธิภาพโลจิสติกส์อุตสาหกรรมสำหรับเครือข่ายการผลิตและห่วงโซ่อุปทานอาหาร",
        "duration_en": "2022 - 2024",
        "duration_th": "2565 - 2567",
        "funding_en": "Faculty Research Support Grant",
        "funding_th": "ทุนสนับสนุนงานวิจัยระดับคณะ",
        "objective_en": "To assess industrial logistics performance across manufacturing and food supply networks and identify improvement opportunities in transportation, inventory flow, and operational efficiency.",
        "objective_th": "เพื่อประเมินประสิทธิภาพด้านโลจิสติกส์อุตสาหกรรมในเครือข่ายการผลิตและห่วงโซ่อุปทานอาหาร พร้อมระบุแนวทางปรับปรุงด้านการขนส่ง การไหลของสินค้าคงคลัง และประสิทธิภาพการดำเนินงาน",
        "project_type": "finished",
    },
]


# 建立一個共用的 SQLite 連線函式
# 之後只要有任何 route 需要查資料庫，都直接匯入這個函式即可
def get_db_connection():
    # 根據設定好的資料庫路徑建立 SQLite 連線
    connection = sqlite3.connect(DATABASE_PATH)

    # 讓查詢結果可以用欄位名稱讀取，例如 row["username"]、row["title_en"]
    connection.row_factory = sqlite3.Row

    return connection


def ensure_general_info_table():
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS general_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_title_en TEXT NOT NULL,
            page_title_th TEXT NOT NULL,
            content_en TEXT,
            content_th TEXT,
            professors_title_en TEXT,
            professors_title_th TEXT,
            advisors_title_en TEXT,
            advisors_title_th TEXT,
            research_team_title_en TEXT,
            research_team_title_th TEXT
        )
        """
    )
    connection.commit()
    connection.close()


def ensure_staff_table():
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL,
            name_th TEXT NOT NULL,
            position_en TEXT,
            position_th TEXT,
            department_en TEXT,
            department_th TEXT,
            staff_group TEXT NOT NULL DEFAULT 'professor'
                CHECK (staff_group IN ('professor', 'advisor', 'research_team')),
            sort_order INTEGER NOT NULL DEFAULT 0,
            photo_filename TEXT,
            profile_url TEXT NOT NULL DEFAULT '',
            audio_en_url TEXT NOT NULL DEFAULT '',
            audio_th_url TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.commit()
    connection.close()


def ensure_admin_table():
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )

    admin_count = connection.execute(
        "SELECT COUNT(*) AS total FROM admin"
    ).fetchone()["total"]

    if admin_count == 0:
        connection.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
            (DEFAULT_ADMIN_USERNAME, generate_password_hash(DEFAULT_ADMIN_PASSWORD))
        )

    connection.commit()
    connection.close()


# 把 staff position 統一轉成小寫 key，方便後續判斷屬於哪一個大分組。
def normalize_staff_position(position_text):
    return (position_text or "").strip().lower()


def normalize_staff_audio_name(name_text):
    normalized = (name_text or "").strip().lower()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"\bassoc\.?\s+prof\.?\b", " ", normalized)
    normalized = re.sub(r"\basst\.?\s+prof\.?\b", " ", normalized)
    normalized = re.sub(r"\bassociate\s+professor\b", " ", normalized)
    normalized = re.sub(r"\bassistant\s+professor\b", " ", normalized)
    normalized = re.sub(r"\bprofessor\b", " ", normalized)
    normalized = re.sub(r"\bprof\.?\b", " ", normalized)
    normalized = re.sub(r"\bdr\.?\b", " ", normalized)
    normalized = re.sub(r"\bph\.?\s*d\.?\b", " ", normalized)
    normalized = re.sub(r"\bd\.?\s*eng\.?\b", " ", normalized)
    normalized = re.sub(r"[\._,\-\(\)/]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    tokens = []
    for token in normalized.split():
        compact_token = re.sub(r"[^a-z0-9]", "", token)

        if not compact_token:
            continue

        if compact_token in STAFF_NAME_PREFIXES:
            continue

        tokens.append(compact_token)

    return " ".join(tokens)


def build_staff_audio_lookup(language_code):
    language_dir = AUDIO_BASE_DIR / language_code.upper()

    if not language_dir.exists():
        return {}

    audio_lookup = {}

    for audio_file in language_dir.iterdir():
        if not audio_file.is_file():
            continue

        file_stem = audio_file.stem
        normalized_stem = re.sub(r"^(en|th)\s*[_\-\s]*", "", file_stem, flags=re.IGNORECASE)
        normalized_name = normalize_staff_audio_name(normalized_stem)

        if not normalized_name:
            continue

        audio_lookup[normalized_name] = f"/static/audio/{language_code.upper()}/{audio_file.name}"

    return audio_lookup


def resolve_existing_audio_url(audio_url):
    cleaned_url = (audio_url or "").strip()

    if not cleaned_url.startswith("/static/"):
        return ""

    relative_parts = cleaned_url.removeprefix("/static/").split("/")
    audio_path = BASE_DIR / "static"

    for part in relative_parts:
        audio_path = audio_path / part

    return cleaned_url if audio_path.exists() else ""


def attach_staff_audio_urls(staff_rows):
    if not staff_rows:
        return []

    audio_lookup_en = build_staff_audio_lookup("en")
    audio_lookup_th = build_staff_audio_lookup("th")
    enriched_staff_rows = []

    for staff in staff_rows:
        staff_data = dict(staff)
        normalized_name = normalize_staff_audio_name(staff_data.get("name_en", ""))
        fallback_audio_en_url = resolve_existing_audio_url(staff_data.get("audio_en_url", ""))
        fallback_audio_th_url = resolve_existing_audio_url(staff_data.get("audio_th_url", ""))

        if normalized_name:
            staff_data["audio_en_url"] = audio_lookup_en.get(
                normalized_name,
                fallback_audio_en_url,
            )
            staff_data["audio_th_url"] = audio_lookup_th.get(
                normalized_name,
                fallback_audio_th_url,
            )
        else:
            staff_data["audio_en_url"] = fallback_audio_en_url
            staff_data["audio_th_url"] = fallback_audio_th_url

        enriched_staff_rows.append(staff_data)

    return enriched_staff_rows


def sync_staff_audio_urls_in_db(connection):
    audio_lookup_en = build_staff_audio_lookup("en")
    audio_lookup_th = build_staff_audio_lookup("th")
    staff_rows = connection.execute(
        "SELECT id, name_en, audio_en_url, audio_th_url FROM staff"
    ).fetchall()

    for staff in staff_rows:
        normalized_name = normalize_staff_audio_name(staff["name_en"])
        resolved_audio_en_url = ""
        resolved_audio_th_url = ""

        if normalized_name:
            resolved_audio_en_url = audio_lookup_en.get(normalized_name, "")
            resolved_audio_th_url = audio_lookup_th.get(normalized_name, "")

        if not resolved_audio_en_url:
            resolved_audio_en_url = resolve_existing_audio_url(staff["audio_en_url"])

        if not resolved_audio_th_url:
            resolved_audio_th_url = resolve_existing_audio_url(staff["audio_th_url"])

        connection.execute(
            """
            UPDATE staff
            SET
                audio_en_url = ?,
                audio_th_url = ?
            WHERE id = ?
            """,
            (
                resolved_audio_en_url,
                resolved_audio_th_url,
                staff["id"],
            )
        )


# 根據 position 自動對應首頁要使用的 staff_group。
# 目前規則：
# Leader / Member -> professor
# Advisor -> advisor
# Researcher -> research_team
def derive_staff_group(position_en="", position_th=""):
    position_key = normalize_staff_position(position_en) or normalize_staff_position(position_th)

    position_map = {
        "leader": "professor",
        "member": "professor",
        "advisor": "advisor",
        "researcher": "research_team",
        "หัวหน้า": "professor",
        "สมาชิก": "professor",
        "ที่ปรึกษา": "advisor",
        "นักวิจัย": "research_team",
    }

    return position_map.get(position_key, "professor")


def derive_staff_directory_section(staff):
    position_key = normalize_staff_position(staff["position_en"] if "position_en" in staff.keys() else "")
    department_en = normalize_staff_position(staff["department_en"] if "department_en" in staff.keys() else "")

    if position_key == "advisor":
        return "advisor"

    if position_key == "researcher":
        return "researcher"

    if "business school" in department_en or department_en == "department of accounting":
        return "accba"

    return "member"


# 確保既有資料庫中的 staff 表已補上目前 staff 頁真正需要的欄位：
# position_en / position_th / department_en / department_th
# 這樣就不需要刪掉舊資料庫重建，也能直接升級目前的 scem.db。
def ensure_staff_directory_columns():
    ensure_staff_table()

    connection = get_db_connection()
    columns = connection.execute("PRAGMA table_info(staff)").fetchall()
    column_names = {column["name"] for column in columns}

    # 某些舊版資料庫可能還沒有 staff_group，
    # 這裡一起補上，避免後面 UPDATE staff_group 時直接報錯。
    if "staff_group" not in column_names:
        connection.execute(
            "ALTER TABLE staff ADD COLUMN staff_group TEXT NOT NULL DEFAULT 'professor'"
        )

    if "position_en" not in column_names and "category_en" in column_names:
        connection.execute("ALTER TABLE staff RENAME COLUMN category_en TO position_en")
        column_names.remove("category_en")
        column_names.add("position_en")

    if "position_th" not in column_names and "category_th" in column_names:
        connection.execute("ALTER TABLE staff RENAME COLUMN category_th TO position_th")
        column_names.remove("category_th")
        column_names.add("position_th")

    if "position_en" not in column_names:
        connection.execute("ALTER TABLE staff ADD COLUMN position_en TEXT")

    if "position_th" not in column_names:
        connection.execute("ALTER TABLE staff ADD COLUMN position_th TEXT")

    if "department_en" not in column_names:
        connection.execute("ALTER TABLE staff ADD COLUMN department_en TEXT")

    if "department_th" not in column_names:
        connection.execute("ALTER TABLE staff ADD COLUMN department_th TEXT")

    if "sort_order" not in column_names:
        connection.execute("ALTER TABLE staff ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0")

    if "audio_en_url" not in column_names:
        connection.execute("ALTER TABLE staff ADD COLUMN audio_en_url TEXT NOT NULL DEFAULT ''")

    if "audio_th_url" not in column_names:
        connection.execute("ALTER TABLE staff ADD COLUMN audio_th_url TEXT NOT NULL DEFAULT ''")

    for staff in DEFAULT_STAFF:
        connection.execute(
            """
            UPDATE staff
            SET
                name_th = COALESCE(NULLIF(TRIM(name_th), ''''), ?),
                position_en = COALESCE(NULLIF(TRIM(position_en), ''''), ?),
                position_th = COALESCE(NULLIF(TRIM(position_th), ''''), ?),
                department_en = COALESCE(NULLIF(TRIM(department_en), ''''), ?),
                department_th = COALESCE(NULLIF(TRIM(department_th), ''''), ?),
                staff_group = COALESCE(NULLIF(TRIM(staff_group), ''''), ?),
                sort_order = CASE WHEN COALESCE(sort_order, 0) = 0 THEN ? ELSE sort_order END,
                photo_filename = COALESCE(NULLIF(TRIM(photo_filename), ''''), ?),
                profile_url = COALESCE(NULLIF(TRIM(profile_url), ''''), ?),
                audio_en_url = COALESCE(NULLIF(TRIM(audio_en_url), ''''), ?),
                audio_th_url = COALESCE(NULLIF(TRIM(audio_th_url), ''''), ?)
            WHERE LOWER(TRIM(name_en)) = LOWER(TRIM(?))
            """,
            (
                staff["name_th"],
                staff["position_en"],
                staff["position_th"],
                staff["department_en"],
                staff["department_th"],
                derive_staff_group(staff["position_en"], staff["position_th"]),
                staff.get("sort_order", 0),
                staff.get("photo_filename", ""),
                staff.get("profile_url", ""),
                staff.get("audio_en_url", ""),
                staff.get("audio_th_url", ""),
                staff["name_en"],
            )
        )

    # 再補一次所有既有資料的 staff_group，
    # 讓後台與首頁分組都能依目前 position 正常運作。
    connection.execute(
        """
        UPDATE staff
        SET staff_group = CASE
            WHEN LOWER(COALESCE(position_en, '')) IN ('leader', 'member') THEN 'professor'
            WHEN LOWER(COALESCE(position_en, '')) = 'advisor' THEN 'advisor'
            WHEN LOWER(COALESCE(position_en, '')) = 'researcher' THEN 'research_team'
            WHEN COALESCE(position_th, '') IN ('หัวหน้า', 'สมาชิก') THEN 'professor'
            WHEN COALESCE(position_th, '') = 'ที่ปรึกษา' THEN 'advisor'
            WHEN COALESCE(position_th, '') = 'นักวิจัย' THEN 'research_team'
            ELSE COALESCE(NULLIF(staff_group, ''), 'professor')
        END
        """
    )

    sync_staff_audio_urls_in_db(connection)
    connection.commit()
    connection.close()


# 確保 general_info 表中至少存在一筆資料。
# 如果目前是空表，系統就會用上面的 DEFAULT_GENERAL_INFO 自動建立一筆初始資料。
def ensure_default_general_info():
    ensure_general_info_table()

    connection = get_db_connection()
    columns = connection.execute("PRAGMA table_info(general_info)").fetchall()
    column_names = {column["name"] for column in columns}

    if "about_title_en" not in column_names:
        connection.execute("ALTER TABLE general_info ADD COLUMN about_title_en TEXT")

    if "about_title_th" not in column_names:
        connection.execute("ALTER TABLE general_info ADD COLUMN about_title_th TEXT")

    if "about_content_en" not in column_names:
        connection.execute("ALTER TABLE general_info ADD COLUMN about_content_en TEXT")

    if "about_content_th" not in column_names:
        connection.execute("ALTER TABLE general_info ADD COLUMN about_content_th TEXT")

    general_info = connection.execute(
        "SELECT id FROM general_info LIMIT 1"
    ).fetchone()

    if general_info is None:
        connection.execute(
            """
            INSERT INTO general_info (
                page_title_en,
                page_title_th,
                about_title_en,
                about_title_th,
                about_content_en,
                about_content_th,
                content_en,
                content_th,
                professors_title_en,
                professors_title_th,
                advisors_title_en,
                advisors_title_th,
                research_team_title_en,
                research_team_title_th
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                DEFAULT_GENERAL_INFO["page_title_en"],
                DEFAULT_GENERAL_INFO["page_title_th"],
                DEFAULT_GENERAL_INFO["about_title_en"],
                DEFAULT_GENERAL_INFO["about_title_th"],
                DEFAULT_GENERAL_INFO["about_content_en"],
                DEFAULT_GENERAL_INFO["about_content_th"],
                DEFAULT_GENERAL_INFO["content_en"],
                DEFAULT_GENERAL_INFO["content_th"],
                DEFAULT_GENERAL_INFO["professors_title_en"],
                DEFAULT_GENERAL_INFO["professors_title_th"],
                DEFAULT_GENERAL_INFO["advisors_title_en"],
                DEFAULT_GENERAL_INFO["advisors_title_th"],
                DEFAULT_GENERAL_INFO["research_team_title_en"],
                DEFAULT_GENERAL_INFO["research_team_title_th"],
            )
        )
        connection.commit()
    else:
        connection.execute(
            """
            UPDATE general_info
            SET
                about_title_en = COALESCE(NULLIF(about_title_en, ''), ?),
                about_title_th = COALESCE(NULLIF(about_title_th, ''), ?),
                about_content_en = COALESCE(NULLIF(about_content_en, ''), ?),
                about_content_th = COALESCE(NULLIF(about_content_th, ''), ?)
            WHERE id = ?
            """,
            (
                DEFAULT_GENERAL_INFO["about_title_en"],
                DEFAULT_GENERAL_INFO["about_title_th"],
                DEFAULT_GENERAL_INFO["about_content_en"],
                DEFAULT_GENERAL_INFO["about_content_th"],
                general_info["id"],
            )
        )
        connection.commit()

    connection.close()


# 取得目前唯一的一筆 general_info 資料。
# 取資料前會先確保預設資料已存在，避免第一次查詢時拿到空值。
def get_general_info():
    ensure_default_general_info()

    connection = get_db_connection()
    general_info = connection.execute(
        "SELECT * FROM general_info ORDER BY id ASC LIMIT 1"
    ).fetchone()
    connection.close()

    return general_info


# 更新 general_info 表中的唯一一筆資料。
# 這個函式會接收整理好的表單資料，並把首頁所有固定文字一次更新。
def update_general_info(form_data):
    ensure_default_general_info()

    connection = get_db_connection()
    general_info = connection.execute(
        "SELECT id FROM general_info ORDER BY id ASC LIMIT 1"
    ).fetchone()

    connection.execute(
        """
        UPDATE general_info
        SET
            page_title_en = ?,
            page_title_th = ?,
            about_title_en = ?,
            about_title_th = ?,
            about_content_en = ?,
            about_content_th = ?,
            content_en = ?,
            content_th = ?,
            professors_title_en = ?,
            professors_title_th = ?,
            advisors_title_en = ?,
            advisors_title_th = ?,
            research_team_title_en = ?,
            research_team_title_th = ?
        WHERE id = ?
        """,
        (
            form_data["page_title_en"],
            form_data["page_title_th"],
            form_data["about_title_en"],
            form_data["about_title_th"],
            form_data["about_content_en"],
            form_data["about_content_th"],
            form_data["content_en"],
            form_data["content_th"],
            form_data["professors_title_en"],
            form_data["professors_title_th"],
            form_data["advisors_title_en"],
            form_data["advisors_title_th"],
            form_data["research_team_title_en"],
            form_data["research_team_title_th"],
            general_info["id"],
        )
    )
    connection.commit()
    connection.close()


# 確保首頁活動照片資料表存在，並在空表時寫入預設的 Info1 ~ Info6。
def ensure_home_activity_images():
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS home_activity_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE
        )
        """
    )

    image_count = connection.execute(
        "SELECT COUNT(*) AS total FROM home_activity_images"
    ).fetchone()["total"]

    if image_count == 0:
        for filename in DEFAULT_HOME_ACTIVITY_IMAGES:
            connection.execute(
                "INSERT OR IGNORE INTO home_activity_images (filename) VALUES (?)",
                (filename,)
            )
        connection.commit()

    connection.close()


# 取得首頁活動輪播要顯示的照片清單。
def get_home_activity_images():
    ensure_home_activity_images()

    connection = get_db_connection()
    image_rows = connection.execute(
        "SELECT * FROM home_activity_images ORDER BY id ASC"
    ).fetchall()
    connection.close()

    return image_rows


# 新增一張首頁活動照片，這裡先用檔名管理，實際圖片檔由 uploads 資料夾提供。
def add_home_activity_image(filename):
    ensure_home_activity_images()

    cleaned_filename = (filename or "").strip()
    if not cleaned_filename:
        return

    connection = get_db_connection()
    connection.execute(
        "INSERT OR IGNORE INTO home_activity_images (filename) VALUES (?)",
        (cleaned_filename,)
    )
    connection.commit()
    connection.close()


# 刪除指定的首頁活動照片。
def delete_home_activity_image(image_id):
    ensure_home_activity_images()

    connection = get_db_connection()
    connection.execute(
        "DELETE FROM home_activity_images WHERE id = ?",
        (image_id,)
    )
    connection.commit()
    connection.close()


# 確保 staff 表中至少存在一批預設人物資料。
# 如果目前 staff 還是空的，就會把 DEFAULT_STAFF 逐筆寫進資料庫。
def ensure_default_staff():
    ensure_staff_directory_columns()

    connection = get_db_connection()

    for staff in DEFAULT_STAFF:
        existing_staff = connection.execute(
            "SELECT id FROM staff WHERE LOWER(TRIM(name_en)) = LOWER(TRIM(?))",
            (staff["name_en"],)
        ).fetchone()

        if existing_staff is not None:
            continue

        connection.execute(
            """
            INSERT INTO staff (
                name_en,
                name_th,
                position_en,
                position_th,
                department_en,
                department_th,
                staff_group,
                sort_order,
                photo_filename,
                profile_url,
                audio_en_url,
                audio_th_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                staff["name_en"],
                staff["name_th"],
                staff["position_en"],
                staff["position_th"],
                staff["department_en"],
                staff["department_th"],
                staff["staff_group"],
                staff.get("sort_order", 0),
                staff["photo_filename"],
                staff["profile_url"],
                staff.get("audio_en_url", ""),
                staff.get("audio_th_url", ""),
            )
        )

    connection.commit()

    connection.close()


# 取得所有 staff 資料，後台管理頁會用這個函式列出完整名單。
# 依照前台 section 與排列順序顯示，方便管理者直接理解畫面順序。
def get_all_staff():
    ensure_default_staff()

    connection = get_db_connection()
    staff_list = connection.execute(
        """
        SELECT * FROM staff
        ORDER BY
            CASE
                WHEN LOWER(COALESCE(position_en, '')) = 'advisor' THEN 0
                WHEN LOWER(COALESCE(position_en, '')) = 'member'
                    AND (
                        LOWER(COALESCE(department_en, '')) LIKE '%business school%'
                        OR LOWER(COALESCE(department_en, '')) = 'department of accounting'
                    ) THEN 2
                WHEN LOWER(COALESCE(position_en, '')) = 'researcher' THEN 3
                ELSE 1
            END,
            sort_order ASC,
            id ASC
        """
    ).fetchall()
    connection.close()

    return attach_staff_audio_urls(staff_list)


# 根據 staff 編號取得單一人物資料。
# 後台編輯某一筆資料時，會用這個函式把原始內容帶回表單。
def get_staff_by_id(staff_id):
    ensure_staff_directory_columns()

    connection = get_db_connection()
    staff = connection.execute(
        "SELECT * FROM staff WHERE id = ?",
        (staff_id,)
    ).fetchone()
    connection.close()

    if staff is None:
        return None

    attached_staff = attach_staff_audio_urls([staff])
    return attached_staff[0] if attached_staff else None


# 新增一筆 staff 資料。
# 後台管理員在新增人物後，會把表單內容寫進 staff 表。
def create_staff(form_data):
    ensure_staff_directory_columns()

    staff_group = derive_staff_group(
        form_data["position_en"],
        form_data["position_th"],
    )

    connection = get_db_connection()
    connection.execute(
        """
        INSERT INTO staff (
            name_en,
            name_th,
            position_en,
            position_th,
            department_en,
            department_th,
            staff_group,
            sort_order,
            photo_filename,
            profile_url,
            audio_en_url,
            audio_th_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            form_data["name_en"],
            form_data["name_th"],
            form_data["position_en"],
            form_data["position_th"],
            form_data["department_en"],
            form_data["department_th"],
            staff_group,
            form_data.get("sort_order", 0),
            form_data["photo_filename"],
            form_data["profile_url"],
            form_data.get("audio_en_url", ""),
            form_data.get("audio_th_url", ""),
        )
    )
    connection.commit()
    connection.close()


# 更新既有的 staff 資料。
# 後台管理頁按下更新後，會把修改後內容寫回指定編號的人物資料。
def update_staff(staff_id, form_data):
    ensure_staff_directory_columns()

    staff_group = derive_staff_group(
        form_data["position_en"],
        form_data["position_th"],
    )

    connection = get_db_connection()
    connection.execute(
        """
        UPDATE staff
        SET
            name_en = ?,
            name_th = ?,
            position_en = ?,
            position_th = ?,
            department_en = ?,
            department_th = ?,
            staff_group = ?,
            sort_order = ?,
            photo_filename = ?,
            profile_url = ?,
            audio_en_url = ?,
            audio_th_url = ?
        WHERE id = ?
        """,
        (
            form_data["name_en"],
            form_data["name_th"],
            form_data["position_en"],
            form_data["position_th"],
            form_data["department_en"],
            form_data["department_th"],
            staff_group,
            form_data.get("sort_order", 0),
            form_data["photo_filename"],
            form_data["profile_url"],
            form_data.get("audio_en_url", ""),
            form_data.get("audio_th_url", ""),
            staff_id,
        )
    )
    connection.commit()
    connection.close()


# 刪除指定的 staff 資料。
# 後台管理頁按下刪除後，就會把這一筆人物資料從 staff 表移除。
def delete_staff(staff_id):
    ensure_staff_directory_columns()

    connection = get_db_connection()
    connection.execute(
        "DELETE FROM staff WHERE id = ?",
        (staff_id,)
    )
    connection.commit()
    connection.close()


# 取得前台要顯示的 staff 名單，並依人物分類分組。
# 目前規則很單純：只要人物資料存在於 staff 表中，就會顯示在前台。
def get_active_staff_grouped():
    ensure_default_staff()

    connection = get_db_connection()
    staff_rows = connection.execute(
        """
        SELECT * FROM staff
        ORDER BY sort_order ASC, id ASC
        """
    ).fetchall()
    connection.close()

    staff_rows = attach_staff_audio_urls(staff_rows)

    grouped_staff = {
        "professor": [],
        "advisor": [],
        "research_team": [],
    }

    for staff in staff_rows:
        grouped_staff[staff["staff_group"]].append(staff)

    return grouped_staff


def get_staff_directory():
    ensure_default_staff()

    connection = get_db_connection()
    staff_rows = connection.execute(
        """
        SELECT *
        FROM staff
        WHERE
            COALESCE(NULLIF(position_en, ''), NULLIF(position_th, '')) IS NOT NULL
            AND COALESCE(NULLIF(department_en, ''), NULLIF(department_th, '')) IS NOT NULL
        ORDER BY sort_order ASC, id ASC
        """
    ).fetchall()
    connection.close()

    return attach_staff_audio_urls(staff_rows)


def get_staff_directory_sections():
    staff_rows = get_staff_directory()
    grouped_staff = {
        section["key"]: []
        for section in STAFF_DIRECTORY_SECTIONS
    }

    for staff in staff_rows:
        grouped_staff[derive_staff_directory_section(staff)].append(staff)

    return [
        {
            "key": section["key"],
            "title_en": section["title_en"],
            "title_th": section["title_th"],
            "staff": grouped_staff[section["key"]],
        }
        for section in STAFF_DIRECTORY_SECTIONS
    ]


# 組出 staff 頁篩選器所需的 position 與 department 選單內容。
def get_staff_filter_options():
    staff_rows = get_staff_directory()

    positions = []
    departments = []
    seen_positions = set()
    seen_departments = set()

    default_positions = [
        {"value": "leader", "label_en": "Leader", "label_th": "หัวหน้า"},
        {"value": "advisor", "label_en": "Advisor", "label_th": "ที่ปรึกษา"},
        {"value": "researcher", "label_en": "Researcher", "label_th": "นักวิจัย"},
        {"value": "member", "label_en": "Member", "label_th": "สมาชิก"},
    ]

    default_departments = [
        {
            "value": "department of industrial engineering",
            "label_en": "Department of Industrial Engineering",
            "label_th": "ภาควิชาวิศวกรรมอุตสาหการ",
        },
        {
            "value": "senior retired lecturer",
            "label_en": "Senior Retired Lecturer",
            "label_th": "อาจารย์อาวุโสเกษียณอายุ",
        },
        {
            "value": "senior project manager",
            "label_en": "Senior Project Manager",
            "label_th": "ผู้จัดการโครงการอาวุโส",
        },
        {
            "value": "research assistant and project engineer",
            "label_en": "Research Assistant and Project Engineer",
            "label_th": "ผู้ช่วยวิจัยและวิศวกรโครงการ",
        },
        {
            "value": "research unit secretary",
            "label_en": "Research Unit Secretary",
            "label_th": "เลขานุการหน่วยวิจัย",
        },
        {
            "value": "department of management and entrepreneurship, business school",
            "label_en": "Department of Management and Entrepreneurship, Business School",
            "label_th": "ภาควิชาการจัดการและการเป็นผู้ประกอบการ คณะบริหารธุรกิจ",
        },
        {
            "value": "department of accounting",
            "label_en": "Department of Accounting",
            "label_th": "ภาควิชาการบัญชี",
        },
    ]

    for option in default_positions:
        positions.append(option)
        seen_positions.add(option["value"])

    for option in default_departments:
        departments.append(option)
        seen_departments.add(option["value"])

    for staff in staff_rows:
        position_key = (staff["position_en"] or staff["position_th"] or "").strip().lower()
        department_key = (staff["department_en"] or staff["department_th"] or "").strip().lower()

        if position_key and position_key not in seen_positions:
            positions.append({
                "value": position_key,
                "label_en": staff["position_en"] or staff["position_th"],
                "label_th": staff["position_th"] or staff["position_en"],
            })
            seen_positions.add(position_key)

        if department_key and department_key not in seen_departments:
            departments.append({
                "value": department_key,
                "label_en": staff["department_en"] or staff["department_th"],
                "label_th": staff["department_th"] or staff["department_en"],
            })
            seen_departments.add(department_key)

    return {
        "positions": positions,
        "departments": departments,
    }


# 取得可以被專案關聯使用的 staff 名單。
# 後台新增 project 時，管理員需要先選擇這個專案屬於哪位老師。
def get_staff_choices():
    connection = get_db_connection()
    staff_rows = connection.execute(
        "SELECT id, name_en FROM staff ORDER BY id ASC"
    ).fetchall()
    connection.close()

    return staff_rows


# 研究專案資料表。
# 這裡把 Ongoing / Finished 專案獨立管理，避免再依賴 staff 名單分類。
def ensure_research_projects_table():
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS research_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_type TEXT NOT NULL CHECK (project_type IN ('ongoing', 'finished')),
            sort_order INTEGER NOT NULL DEFAULT 0,
            year_en TEXT,
            year_th TEXT,
            title_en TEXT NOT NULL,
            title_th TEXT NOT NULL,
            leader_en TEXT,
            leader_th TEXT,
            deputy_en TEXT,
            deputy_th TEXT,
            researcher_en TEXT,
            researcher_th TEXT,
            engineer_en TEXT,
            engineer_th TEXT,
            description_en TEXT,
            description_th TEXT
        )
        """
    )
    connection.commit()
    connection.close()


# 舊函式名稱保留給 app.py 與既有呼叫點使用。
# 目前它只負責確保新的 research_projects 表存在。
def ensure_default_projects():
    ensure_research_projects_table()


# 取得所有 research project。
# 後台管理頁會用這個函式列出所有專案。
def get_all_projects():
    ensure_research_projects_table()

    connection = get_db_connection()
    projects = connection.execute(
        """
        SELECT *
        FROM research_projects
        ORDER BY CASE project_type WHEN 'ongoing' THEN 0 ELSE 1 END, sort_order ASC, id ASC
        """
    ).fetchall()
    connection.close()

    return projects


# 根據 project 編號取得單一專案資料。
# 後台編輯時與前台詳細頁都會用到這個函式。
def get_project_by_id(project_id):
    ensure_research_projects_table()

    connection = get_db_connection()
    project = connection.execute(
        """
        SELECT *
        FROM research_projects
        WHERE id = ?
        """,
        (project_id,)
    ).fetchone()
    connection.close()

    return project


def normalize_project_person_name(name):
    cleaned_name = (name or "").strip().lower()
    for character in [".", ",", " ", "\n", "\t", "(", ")"]:
        cleaned_name = cleaned_name.replace(character, "")
    return cleaned_name


# 根據 ongoing project 內的成員姓名，從 staff 表中找出對應照片。
# 詳細頁只需要照片檔名與姓名，不顯示 department / affiliation。
def get_project_team_profiles(project):
    ensure_staff_directory_columns()

    role_fields = {
        "leader": ("leader_en", "leader_th"),
        "deputy": ("deputy_en", "deputy_th"),
        "researcher": ("researcher_en", "researcher_th"),
        "engineer": ("engineer_en", "engineer_th"),
    }

    connection = get_db_connection()
    staff_rows = connection.execute(
        """
        SELECT name_en, name_th, photo_filename
        FROM staff
        """
    ).fetchall()
    connection.close()

    staff_lookup = {}
    for staff in staff_rows:
        for name_key in ("name_en", "name_th"):
            normalized_name = normalize_project_person_name(staff[name_key])
            if normalized_name:
                staff_lookup[normalized_name] = staff

    team_profiles = {}
    for role_key, project_name_fields in role_fields.items():
        matched_staff = None

        for project_name_field in project_name_fields:
            normalized_project_name = normalize_project_person_name(project[project_name_field])
            if normalized_project_name and normalized_project_name in staff_lookup:
                matched_staff = staff_lookup[normalized_project_name]
                break

        team_profiles[role_key] = matched_staff

    return team_profiles


# 新增一筆 project 資料。
# 後台新增專案時，會把表單內容寫進 research_projects 表。
def create_project(form_data):
    ensure_research_projects_table()

    connection = get_db_connection()
    connection.execute(
        """
        INSERT INTO research_projects (
            project_type,
            sort_order,
            year_en,
            year_th,
            title_en,
            title_th,
            leader_en,
            leader_th,
            deputy_en,
            deputy_th,
            researcher_en,
            researcher_th,
            engineer_en,
            engineer_th,
            description_en,
            description_th
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            form_data["project_type"],
            form_data.get("sort_order", 0),
            form_data["year_en"],
            form_data["year_th"],
            form_data["title_en"],
            form_data["title_th"],
            form_data["leader_en"],
            form_data["leader_th"],
            form_data["deputy_en"],
            form_data["deputy_th"],
            form_data["researcher_en"],
            form_data["researcher_th"],
            form_data["engineer_en"],
            form_data["engineer_th"],
            form_data["description_en"],
            form_data["description_th"],
        )
    )
    connection.commit()
    connection.close()


# 更新既有的 project 資料。
# 後台按下更新後，會把專案新內容寫回原本那一筆資料。
def update_project(project_id, form_data):
    ensure_research_projects_table()

    connection = get_db_connection()
    connection.execute(
        """
        UPDATE research_projects
        SET
            project_type = ?,
            sort_order = ?,
            year_en = ?,
            year_th = ?,
            title_en = ?,
            title_th = ?,
            leader_en = ?,
            leader_th = ?,
            deputy_en = ?,
            deputy_th = ?,
            researcher_en = ?,
            researcher_th = ?,
            engineer_en = ?,
            engineer_th = ?,
            description_en = ?,
            description_th = ?
        WHERE id = ?
        """,
        (
            form_data["project_type"],
            form_data.get("sort_order", 0),
            form_data["year_en"],
            form_data["year_th"],
            form_data["title_en"],
            form_data["title_th"],
            form_data["leader_en"],
            form_data["leader_th"],
            form_data["deputy_en"],
            form_data["deputy_th"],
            form_data["researcher_en"],
            form_data["researcher_th"],
            form_data["engineer_en"],
            form_data["engineer_th"],
            form_data["description_en"],
            form_data["description_th"],
            project_id,
        )
    )
    connection.commit()
    connection.close()


# 刪除指定的 project。
# 後台管理頁按下刪除時，會把這一筆專案從資料庫中移除。
def delete_project(project_id):
    ensure_research_projects_table()

    connection = get_db_connection()
    connection.execute(
        "DELETE FROM research_projects WHERE id = ?",
        (project_id,)
    )
    connection.commit()
    connection.close()


# 組出 /research 頁需要的資料結構。
# 會分成 ongoing 與 finished 兩區。
def get_research_projects():
    ensure_research_projects_table()

    connection = get_db_connection()
    rows = connection.execute(
        """
        SELECT *
        FROM research_projects
        ORDER BY CASE project_type WHEN 'ongoing' THEN 0 ELSE 1 END, sort_order ASC, id ASC
        """
    ).fetchall()
    connection.close()

    grouped_research = {
        "ongoing": [],
        "finished": [],
    }

    for row in rows:
        grouped_research[row["project_type"]].append(row)

    return grouped_research


# 舊版 research 分組資料函式的相容入口。
# 目前前台已改用 ongoing / finished 兩區，但保留舊名稱避免其他檔案引用時壞掉。
def get_research_groups():
    return get_research_projects()
