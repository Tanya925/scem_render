from pathlib import Path
import re
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "scem.db"
AUDIO_BASE_DIR = BASE_DIR / "static" / "audio"

STAFF_NAME_PREFIXES = {
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
}


def normalize_staff_audio_name(name_text: str) -> str:
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
        if compact_token and compact_token not in STAFF_NAME_PREFIXES:
            tokens.append(compact_token)

    return " ".join(tokens)


def build_staff_audio_lookup(language_code: str) -> dict[str, str]:
    language_dir = AUDIO_BASE_DIR / language_code.upper()
    audio_lookup: dict[str, str] = {}

    if not language_dir.exists():
        return audio_lookup

    for audio_file in language_dir.iterdir():
        if not audio_file.is_file():
            continue

        normalized_stem = re.sub(
            r"^(en|th)\s*[_\-\s]*",
            "",
            audio_file.stem,
            flags=re.IGNORECASE,
        )
        normalized_name = normalize_staff_audio_name(normalized_stem)

        if normalized_name:
            audio_lookup[normalized_name] = (
                f"/static/audio/{language_code.upper()}/{audio_file.name}"
            )

    return audio_lookup


def main() -> None:
    audio_lookup_en = build_staff_audio_lookup("en")
    audio_lookup_th = build_staff_audio_lookup("th")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    staff_rows = connection.execute(
        "SELECT id, name_en FROM staff ORDER BY id ASC"
    ).fetchall()

    for staff in staff_rows:
        normalized_name = normalize_staff_audio_name(staff["name_en"])
        audio_en_url = audio_lookup_en.get(normalized_name, "")
        audio_th_url = audio_lookup_th.get(normalized_name, "")

        connection.execute(
            """
            UPDATE staff
            SET
                audio_en_url = ?,
                audio_th_url = ?
            WHERE id = ?
            """,
            (audio_en_url, audio_th_url, staff["id"]),
        )

    connection.commit()

    rows_with_audio = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM staff
        WHERE COALESCE(audio_en_url, '') <> ''
           OR COALESCE(audio_th_url, '') <> ''
        """
    ).fetchone()["total"]

    connection.close()
    print(f"rows_with_audio={rows_with_audio}")


if __name__ == "__main__":
    main()
