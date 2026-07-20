-- SCEM website database schema

CREATE TABLE IF NOT EXISTS general_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_title_en TEXT NOT NULL,
    page_title_th TEXT NOT NULL,
    about_title_en TEXT,
    about_title_th TEXT,
    about_content_en TEXT,
    about_content_th TEXT,
    content_en TEXT,
    content_th TEXT,
    professors_title_en TEXT,
    professors_title_th TEXT,
    advisors_title_en TEXT,
    advisors_title_th TEXT,
    research_team_title_en TEXT,
    research_team_title_th TEXT
);

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
);

CREATE TABLE IF NOT EXISTS home_activity_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE
);

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
);

CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);
