# 主要功能：管理後台相關頁面的網址

from functools import wraps  # 用來建立可重複使用的登入檢查裝飾器
import json
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, render_template, session, redirect, url_for, request  # render_template 是用來回傳 HTML 頁面的
from werkzeug.utils import secure_filename

from database import (
    get_general_info,
    update_general_info,
    get_home_activity_images,
    add_home_activity_image,
    delete_home_activity_image,
    get_all_staff,
    get_staff_by_id,
    create_staff,
    update_staff,
    delete_staff,
    parse_project_custom_fields,
    get_all_projects,
    get_project_by_id,
    create_project,
    update_project,
    delete_project,
)  # 匯入 General Info 與 Staff 需要的資料庫操作函式


# 後台管理頁路由，統一在網址加上 /0630_SCEMadmin 前綴。
# admin_bp 是這個 Blueprint 的名稱。Blueprint功能是把一組路由集中管理，之後再統一註冊到 Flask app 裡
admin_bp = Blueprint("admin", __name__, url_prefix="/0630_SCEMadmin")

STATIC_FOLDER = Path(__file__).resolve().parent.parent / "static"
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
PDF_EXTENSIONS = {"pdf"}
AUDIO_EXTENSIONS = {"mp3", "m4a", "wav", "ogg", "aac"}


def save_uploaded_file(uploaded_file, folder_name, allowed_extensions):
    if not uploaded_file or not uploaded_file.filename:
        return ""

    raw_filename = uploaded_file.filename
    cleaned_filename = secure_filename(raw_filename)
    extension = raw_filename.rsplit(".", 1)[-1].lower() if "." in raw_filename else ""

    if extension not in allowed_extensions:
        return ""

    safe_stem = Path(cleaned_filename).stem or "uploaded-file"
    saved_filename = f"{safe_stem}-{uuid4().hex[:8]}.{extension}"
    target_folder = STATIC_FOLDER / folder_name
    target_folder.mkdir(parents=True, exist_ok=True)
    uploaded_file.save(target_folder / saved_filename)

    return saved_filename


# 建立一個登入檢查 "裝飾器"！
# 只要把 @login_required 放在某個後台 route 上，就能限制「必須登入後才能進入」
def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        
        # 如果 session 中沒有 admin_id，代表目前尚未登入
        if "admin_id" not in session:
            return redirect(url_for("auth.login"))

        # 已登入的情況下，正常執行原本的 route 函式
        return view_function(*args, **kwargs)

    return wrapped_view


# 這是 route 裝飾器。意思是：當使用者進入 /0630_SCEMadmin/dashboard 時，執行下面的 dashboard() 函式
# 而因為前面有設定：url_prefix="/0630_SCEMadmin"，所以這裡實際的網址為 /0630_SCEMadmin/dashboard
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    # 從 session 中取出目前登入的管理員帳號名稱
    # 這樣後台首頁就可以顯示「目前是哪位管理員登入中」
    admin_username = session.get("admin_username", "Admin")

    # 回傳後台首頁的 html，並把 admin_username 一起傳進模板
    # 也就是當打開：http://127.0.0.1:5000/0630_SCEMadmin/dashboard，Flask 會去找：templates/admin_dashboard.html，然後顯示它
    return render_template("admin_dashboard.html", admin_username=admin_username)


# 設定一個後台 General Info 的網址(/0630_SCEMadmin/general-info)
# 這個頁面同時支援：
# 1. GET：讀出目前資料並顯示表單
# 2. POST：接收表單送出的新內容並更新資料庫
@admin_bp.route("/general-info", methods=["GET", "POST"])
@login_required
def general_info():
    # 預設先不顯示成功訊息，只有真正儲存後才顯示
    success_message = None

    # 當管理員按下 Save 送出表單時，會進到 POST 流程
    if request.method == "POST":
        action = request.form.get("form_action", "save_text").strip()

        if action == "add_activity_image":
            uploaded_filename = save_uploaded_file(
                request.files.get("activity_image_file"),
                "uploads",
                IMAGE_EXTENSIONS,
            )

            if uploaded_filename:
                add_home_activity_image(uploaded_filename)
                success_message = "Activity image added successfully."
            else:
                success_message = "Please upload a JPG, PNG, GIF, or WEBP image."
        elif action == "delete_activity_image":
            image_id = request.form.get("image_id", type=int)
            if image_id:
                delete_home_activity_image(image_id)
                success_message = "Activity image deleted successfully."
        else:
            current_general_info = get_general_info()
            # 把表單欄位整理成字典，後面可以直接交給 update_general_info() 更新資料庫
            form_data = {
                "page_title_en": request.form.get("page_title_en", "").strip(),
                "page_title_th": request.form.get("page_title_th", "").strip(),
                "about_title_en": request.form.get("about_title_en", "").strip(),
                "about_title_th": request.form.get("about_title_th", "").strip(),
                "about_content_en": request.form.get("about_content_en", "").strip(),
                "about_content_th": request.form.get("about_content_th", "").strip(),
                "content_en": request.form.get("content_en", "").strip(),
                "content_th": request.form.get("content_th", "").strip(),
                "professors_title_en": current_general_info["professors_title_en"],
                "professors_title_th": current_general_info["professors_title_th"],
                "advisors_title_en": current_general_info["advisors_title_en"],
                "advisors_title_th": current_general_info["advisors_title_th"],
                "research_team_title_en": current_general_info["research_team_title_en"],
                "research_team_title_th": current_general_info["research_team_title_th"],
            }

            # 把更新後的資料寫回 general_info 表
            update_general_info(form_data)
            success_message = "General Info saved successfully."

    # 不論是第一次進頁面，還是儲存完之後，都重新抓最新資料回來顯示在表單上
    general_info_data = get_general_info()
    activity_images = get_home_activity_images()

    # 回傳後台編輯 General Info 的頁面，並把目前資料與成功訊息傳進模板
    return render_template(
        "admin_general_info.html",
        general_info=general_info_data,
        activity_images=activity_images,
        success_message=success_message
    )


# 設定一個後台 Staff / Researcher 的網址(/0630_SCEMadmin/staff)
@admin_bp.route("/staff", methods=["GET", "POST"])
@login_required
def staff():
    # 預設是新增模式，因此沒有正在編輯的 staff 資料
    editing_staff = None
    success_message = None

    # 如果網址有帶 edit_id，代表管理員想編輯某一筆既有資料
    edit_id = request.args.get("edit_id", type=int)
    if edit_id:
        editing_staff = get_staff_by_id(edit_id)

    # 後台按下新增或更新後，會走到 POST 流程
    if request.method == "POST":
        form_action = request.form.get("form_action", "save_staff").strip()

        if form_action == "delete_staff":
            delete_staff_id = request.form.get("delete_staff_id", type=int)

            if delete_staff_id:
                delete_staff(delete_staff_id)
                success_message = "Staff deleted successfully."

            staff_list = get_all_staff()
            return render_template(
                "admin_staff.html",
                staff_list=staff_list,
                success_message=success_message,
                editing_staff=None,
            )

        staff_id = request.form.get("staff_id", type=int)
        existing_staff = get_staff_by_id(staff_id) if staff_id else None
        uploaded_photo_filename = save_uploaded_file(
            request.files.get("photo_file"),
            "uploads",
            IMAGE_EXTENSIONS,
        )
        uploaded_profile_pdf = save_uploaded_file(
            request.files.get("profile_pdf_file"),
            "cv",
            PDF_EXTENSIONS,
        )
        uploaded_audio_en = save_uploaded_file(
            request.files.get("audio_en_file"),
            "audio/EN",
            AUDIO_EXTENSIONS,
        )
        uploaded_audio_th = save_uploaded_file(
            request.files.get("audio_th_file"),
            "audio/TH",
            AUDIO_EXTENSIONS,
        )

        profile_url = request.form.get("profile_url", "").strip()
        if uploaded_profile_pdf:
            profile_url = f"/static/cv/{uploaded_profile_pdf}"

        audio_en_url = existing_staff["audio_en_url"] if existing_staff else ""
        audio_th_url = existing_staff["audio_th_url"] if existing_staff else ""
        if uploaded_audio_en:
            audio_en_url = f"/static/audio/EN/{uploaded_audio_en}"
        if uploaded_audio_th:
            audio_th_url = f"/static/audio/TH/{uploaded_audio_th}"

        # 把表單內容先整理成共用格式，後面新增和更新都能直接使用
        form_data = {
            "name_en": request.form.get("name_en", "").strip(),
            "name_th": request.form.get("name_th", "").strip(),
            "position_en": request.form.get("position_en", "").strip(),
            "position_th": request.form.get("position_th", "").strip(),
            "department_en": request.form.get("department_en", "").strip(),
            "department_th": request.form.get("department_th", "").strip(),
            "sort_order": request.form.get("sort_order", type=int) or 0,
            "photo_filename": uploaded_photo_filename or (existing_staff["photo_filename"] if existing_staff else ""),
            "profile_url": profile_url,
            "scopus_author_id": request.form.get("scopus_author_id", "").strip(),
            "scopus_hindex": existing_staff["scopus_hindex"] if existing_staff else None,
            "audio_en_url": audio_en_url,
            "audio_th_url": audio_th_url,
        }

        # 如果表單中有 staff_id，代表這次是更新既有資料，不是新增
        if staff_id:
            update_staff(staff_id, form_data)
            success_message = "Staff updated successfully."
        else:
            create_staff(form_data)
            success_message = "Staff created successfully."

        editing_staff = None

    # 重新抓取最新的 staff 清單，顯示在後台頁面下方
    staff_list = get_all_staff()

    # 把後台管理頁需要的資料全部傳進模板：
    # 1. 現有 staff 清單
    # 2. 是否有成功訊息
    # 3. 是否正在編輯某一筆資料
    return render_template(
        "admin_staff.html",
        staff_list=staff_list,
        success_message=success_message,
        editing_staff=editing_staff,
    )


# 設定一個後台 Research Projects 的網址(/0630_SCEMadmin/projects)
@admin_bp.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    # 預設是新增模式，因此先不指定正在編輯哪一筆專案
    editing_project = None
    editing_custom_team_fields = []
    editing_custom_detail_fields = []
    success_message = None

    # 如果網址有帶 edit_id，代表管理員要編輯既有專案
    edit_id = request.args.get("edit_id", type=int)
    if edit_id:
        editing_project = get_project_by_id(edit_id)
        editing_custom_team_fields = parse_project_custom_fields(
            editing_project["custom_team_fields_json"]
        )
        editing_custom_detail_fields = parse_project_custom_fields(
            editing_project["custom_detail_fields_json"]
        )

    # 後台按下新增或更新後，會走 POST 流程
    if request.method == "POST":
        form_action = request.form.get("form_action", "save_project").strip()

        if form_action == "delete_project":
            delete_project_id = request.form.get("delete_project_id", type=int)

            if delete_project_id:
                delete_project(delete_project_id)
                success_message = "Project deleted successfully."

            project_list = get_all_projects()
            return render_template(
                "admin_projects.html",
                project_list=project_list,
                editing_project=None,
                editing_custom_team_fields=[],
                editing_custom_detail_fields=[],
                success_message=success_message,
            )

        project_id = request.form.get("project_id", type=int)
        existing_project = get_project_by_id(project_id) if project_id else None
        uploaded_leader_photo = save_uploaded_file(
            request.files.get("leader_photo_file"),
            "uploads",
            IMAGE_EXTENSIONS,
        )
        uploaded_deputy_photo = save_uploaded_file(
            request.files.get("deputy_photo_file"),
            "uploads",
            IMAGE_EXTENSIONS,
        )
        uploaded_coordinator_photo = save_uploaded_file(
            request.files.get("coordinator_photo_file"),
            "uploads",
            IMAGE_EXTENSIONS,
        )
        uploaded_advisor_photo = save_uploaded_file(
            request.files.get("advisor_photo_file"),
            "uploads",
            IMAGE_EXTENSIONS,
        )

        custom_team_labels_en = request.form.getlist("custom_team_label_en[]")
        custom_team_labels_th = request.form.getlist("custom_team_label_th[]")
        custom_team_values_en = request.form.getlist("custom_team_value_en[]")
        custom_team_values_th = request.form.getlist("custom_team_value_th[]")
        custom_team_existing_photos = request.form.getlist("custom_team_existing_photo[]")
        custom_team_uploaded_photos = request.files.getlist("custom_team_photo_file[]")

        custom_team_fields = []
        custom_team_field_count = max(
            len(custom_team_labels_en),
            len(custom_team_labels_th),
            len(custom_team_values_en),
            len(custom_team_values_th),
            len(custom_team_existing_photos),
            len(custom_team_uploaded_photos),
        )
        for index in range(custom_team_field_count):
            label_en = custom_team_labels_en[index].strip() if index < len(custom_team_labels_en) else ""
            label_th = custom_team_labels_th[index].strip() if index < len(custom_team_labels_th) else ""
            value_en = custom_team_values_en[index].strip() if index < len(custom_team_values_en) else ""
            value_th = custom_team_values_th[index].strip() if index < len(custom_team_values_th) else ""
            existing_photo = custom_team_existing_photos[index].strip() if index < len(custom_team_existing_photos) else ""
            uploaded_file = custom_team_uploaded_photos[index] if index < len(custom_team_uploaded_photos) else None
            uploaded_photo = save_uploaded_file(
                uploaded_file,
                "uploads",
                IMAGE_EXTENSIONS,
            )

            if label_en or label_th or value_en or value_th or existing_photo or uploaded_photo:
                custom_team_fields.append({
                    "label_en": label_en,
                    "label_th": label_th,
                    "value_en": value_en,
                    "value_th": value_th,
                    "photo_filename": uploaded_photo or existing_photo,
                })

        custom_detail_labels_en = request.form.getlist("custom_detail_label_en[]")
        custom_detail_labels_th = request.form.getlist("custom_detail_label_th[]")
        custom_detail_values_en = request.form.getlist("custom_detail_value_en[]")
        custom_detail_values_th = request.form.getlist("custom_detail_value_th[]")

        custom_detail_fields = []
        custom_detail_field_count = max(
            len(custom_detail_labels_en),
            len(custom_detail_labels_th),
            len(custom_detail_values_en),
            len(custom_detail_values_th),
        )
        for index in range(custom_detail_field_count):
            label_en = custom_detail_labels_en[index].strip() if index < len(custom_detail_labels_en) else ""
            label_th = custom_detail_labels_th[index].strip() if index < len(custom_detail_labels_th) else ""
            value_en = custom_detail_values_en[index].strip() if index < len(custom_detail_values_en) else ""
            value_th = custom_detail_values_th[index].strip() if index < len(custom_detail_values_th) else ""

            if label_en or label_th or value_en or value_th:
                custom_detail_fields.append({
                    "label_en": label_en,
                    "label_th": label_th,
                    "value_en": value_en,
                    "value_th": value_th,
                })

        form_data = {
            "sort_order": existing_project["sort_order"] if existing_project else 0,
            "project_type": request.form.get("project_type", "ongoing").strip(),
            "year_en": request.form.get("year_en", "").strip(),
            "year_th": request.form.get("year_th", "").strip(),
            "title_en": request.form.get("title_en", "").strip(),
            "title_th": request.form.get("title_th", "").strip(),
            "leader_en": request.form.get("leader_en", "").strip(),
            "leader_th": request.form.get("leader_th", "").strip(),
            "leader_photo_filename": uploaded_leader_photo or (existing_project["leader_photo_filename"] if existing_project else ""),
            "deputy_en": request.form.get("deputy_en", "").strip(),
            "deputy_th": request.form.get("deputy_th", "").strip(),
            "deputy_photo_filename": uploaded_deputy_photo or (existing_project["deputy_photo_filename"] if existing_project else ""),
            "coordinator_en": request.form.get("coordinator_en", "").strip(),
            "coordinator_th": request.form.get("coordinator_th", "").strip(),
            "coordinator_photo_filename": uploaded_coordinator_photo or (existing_project["coordinator_photo_filename"] if existing_project else ""),
            "advisor_en": request.form.get("advisor_en", "").strip(),
            "advisor_th": request.form.get("advisor_th", "").strip(),
            "advisor_photo_filename": uploaded_advisor_photo or (existing_project["advisor_photo_filename"] if existing_project else ""),
            "researcher_en": request.form.get("researcher_en", "").strip(),
            "researcher_th": request.form.get("researcher_th", "").strip(),
            "engineer_en": request.form.get("engineer_en", "").strip(),
            "engineer_th": request.form.get("engineer_th", "").strip(),
            "assistant_en": request.form.get("assistant_en", "").strip(),
            "assistant_th": request.form.get("assistant_th", "").strip(),
            "duration_en": request.form.get("duration_en", "").strip(),
            "duration_th": request.form.get("duration_th", "").strip(),
            "lead_unit_en": request.form.get("lead_unit_en", "").strip(),
            "lead_unit_th": request.form.get("lead_unit_th", "").strip(),
            "partner_en": request.form.get("partner_en", "").strip(),
            "partner_th": request.form.get("partner_th", "").strip(),
            "funding_en": request.form.get("funding_en", "").strip(),
            "funding_th": request.form.get("funding_th", "").strip(),
            "budget_en": request.form.get("budget_en", "").strip(),
            "budget_th": request.form.get("budget_th", "").strip(),
            "collaboration_details_en": request.form.get("collaboration_details_en", "").strip(),
            "collaboration_details_th": request.form.get("collaboration_details_th", "").strip(),
            "custom_team_fields_json": json.dumps(custom_team_fields, ensure_ascii=False),
            "custom_detail_fields_json": json.dumps(custom_detail_fields, ensure_ascii=False),
            "notes": request.form.get("notes", "").strip(),
            "description_en": request.form.get("description_en", "").strip(),
            "description_th": request.form.get("description_th", "").strip(),
            "project_type": request.form.get("project_type", "ongoing").strip(),
        }

        if project_id:
            update_project(project_id, form_data)
            success_message = "Project updated successfully."
        else:
            create_project(form_data)
            success_message = "Project created successfully."

        editing_project = None

    # 抓取目前所有 project，顯示在後台清單中
    project_list = get_all_projects()

    # 回傳後台管理 Projects 的頁面，並把表單與清單所需資料一起帶進模板
    return render_template(
        "admin_projects.html",
        project_list=project_list,
        editing_project=editing_project,
        editing_custom_team_fields=editing_custom_team_fields,
        editing_custom_detail_fields=editing_custom_detail_fields,
        success_message=success_message,
    )
