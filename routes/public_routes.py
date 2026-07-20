# 主要功能：負責「前台網站的網址」

from flask import Blueprint, render_template, abort, session, redirect, url_for, request

from database import (
    get_general_info,
    get_home_activity_images,
    get_active_staff_grouped,
    get_staff_directory_sections,
    get_staff_filter_options,
    get_research_projects,
    get_project_by_id,
    get_project_team_profiles,
)  # 匯入首頁、staff、research、project detail 需要的資料讀取函式


# 前台網站路由，負責一般訪客會看到的頁面。
# public_bp 是這個 Blueprint 的名稱。Blueprint功能是把一組路由集中管理，之後再統一註冊到 Flask app 裡
public_bp = Blueprint("public", __name__)


# 切換前台語言。
# 目前先提供 en / th 兩種模式，切換後會把選擇記到 session，
# 讓使用者之後切到其他前台頁面時也能維持相同語言。
@public_bp.route("/language/<lang_code>")
def change_language(lang_code):
    if lang_code not in {"en", "th"}:
        lang_code = "en"

    session["language"] = lang_code

    next_url = request.args.get("next", "").strip()
    if next_url.startswith("/"):
        return redirect(next_url)

    return redirect(url_for("public.index"))


# 設定首頁 General Info 的網址(/)
@public_bp.route("/")
def index():
    # 先從資料庫抓出目前首頁要顯示的 General Info 內容
    general_info_data = get_general_info()
    home_activity_images = get_home_activity_images()

    # 抓出所有要在前台顯示的 staff，並依 professor / advisor / research_team 分組
    grouped_staff = get_active_staff_grouped()

    # 回傳首頁 General Info 頁面，並把首頁文字與人物資料一起傳給模板
    return render_template(
        "index.html",
        general_info=general_info_data,
        home_activity_images=home_activity_images,
        grouped_staff=grouped_staff,
    )


# 設定一個前台 Staff / Researcher 的網址(/staff)
@public_bp.route("/staff")
def staff():
    # 抓出 staff 頁要正式展示的人物清單。
    # 目前這份清單會依資料是否整理完成來決定是否出現。
    staff_sections = get_staff_directory_sections()

    # 準備 position / department 篩選器選項。
    filter_options = get_staff_filter_options()

    # 回傳 Staff / Researcher 頁面，並把人物資料與篩選器一起傳進模板
    return render_template(
        "staff.html",
        staff_sections=staff_sections,
        filter_options=filter_options,
    )


# 設定一個前台 Research Projects 的網址(/research)
@public_bp.route("/research")
def research():
    # 依照目前的資料規則，把 research 頁拆成兩個區塊：ongoing 與 finished。
    research_projects = get_research_projects()

    # 回傳 research 頁面，讓模板依教授分組顯示所有專案
    return render_template("research.html", research_projects=research_projects)


# 設定一個「動態網址」
# 負責單一 ongoing Project 的詳細資料頁
@public_bp.route("/project/<int:project_id>")
def project_detail(project_id):
    # 先根據 project_id 抓出這一筆專案資料
    project = get_project_by_id(project_id)

    # 如果查不到資料，或該專案不是 ongoing，就不允許進入詳細頁
    if project is None or project["project_type"] != "ongoing":
        abort(404)

    project_team_profiles = get_project_team_profiles(project)

    # 回傳專案詳細頁，並把這筆專案的完整內容傳進模板
    return render_template(
        "project_detail.html",
        project=project,
        project_team_profiles=project_team_profiles,
    )
