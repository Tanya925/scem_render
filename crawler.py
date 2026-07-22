import csv
import re
import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from database import get_staff_scopus_targets, update_staff_scopus_metrics


SCOPUS_AUTHOR_URL_TEMPLATE = "https://www.scopus.com/authid/detail.uri?authorId={author_id}"
OUTPUT_FILE = Path("scopus_hindex_results.csv")


def build_author_url(author_id: str) -> str:
    return SCOPUS_AUTHOR_URL_TEMPLATE.format(author_id=author_id)


def extract_hindex_from_response(response_json: dict) -> int | None:
    try:
        return int(response_json["data"]["author"]["metrics"]["hindex"])
    except (KeyError, TypeError, ValueError):
        return None


def extract_hindex_from_text(page_text: str) -> int | None:
    patterns = [
        r"(\d+)\s*h-index",
        r"h-index\s*(\d+)",
        r"(\d+)\s*ดัชนี\s*h",
        r"ดัชนี\s*h\s*(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def get_scopus_targets() -> list[dict[str, str]]:
    return [
        {
            "staff_id": str(staff["id"]),
            "name": staff["name_en"] or staff["name_th"] or f"staff-{staff['id']}",
            "author_id": staff["scopus_author_id"],
        }
        for staff in get_staff_scopus_targets()
    ]


def wait_for_manual_verification(page, login_author_id: str) -> None:
    page.goto(build_author_url(login_author_id), wait_until="domcontentloaded")
    print("瀏覽器已開啟。請在視窗中完成 Scopus 驗證。")
    print("完成後停留在作者頁面，程式會自動繼續。")

    try:
        page.wait_for_url("**/authid/detail.uri**", timeout=240000)
        page.wait_for_load_state("networkidle", timeout=60000)
    except PlaywrightTimeoutError as error:
        raise RuntimeError(
            "等待驗證完成逾時。請確認你已在 4 分鐘內完成驗證，"
            "而且最後停留在作者頁面。"
        ) from error


def fetch_hindex_for_professor(page, professor: dict[str, str]) -> int:
    api_result: dict[str, int | None] = {"hindex": None}
    author_id = professor["author_id"]

    def handle_response(response) -> None:
        if "author-profile-api/author" not in response.url:
            return
        try:
            response_json = response.json()
        except Exception:
            return
        hindex = extract_hindex_from_response(response_json)
        if hindex is not None:
            api_result["hindex"] = hindex

    page.on("response", handle_response)

    try:
        page.goto(build_author_url(author_id), wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=60000)
        except PlaywrightTimeoutError:
            pass

        if api_result["hindex"] is not None:
            return int(api_result["hindex"])

        try:
            page.wait_for_selector("text=/h-index/i", timeout=15000)
        except PlaywrightTimeoutError:
            page.wait_for_selector("text=/ดัชนี h/i", timeout=15000)
        page_text = page.locator("body").inner_text()
        hindex = extract_hindex_from_text(page_text)
        if hindex is None:
            screenshot_path = Path(f"scopus_error_{author_id}.png")
            page.screenshot(path=str(screenshot_path), full_page=True)
            raise RuntimeError(
                "頁面上有 h-index 字樣，但沒有成功解析出數字。\n"
                f"已儲存畫面：{screenshot_path}"
            )
        return hindex
    except PlaywrightTimeoutError as error:
        screenshot_path = Path(f"scopus_error_{author_id}.png")
        page.screenshot(path=str(screenshot_path), full_page=True)
        raise RuntimeError(
            "等待作者頁資料逾時，可能是頁面太慢、驗證狀態失效，"
            "或被額外檢查攔住。\n"
            f"已儲存畫面：{screenshot_path}"
        ) from error
    finally:
        page.remove_listener("response", handle_response)


def write_results(rows: list[dict[str, str]]) -> None:
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["staff_id", "name", "author_id", "hindex", "status", "error"],
        )
        writer.writeheader()
        writer.writerows(rows)


def sync_results_to_database(rows: list[dict[str, str]]) -> None:
    successful_rows = [row for row in rows if row["status"] == "success"]
    update_staff_scopus_metrics(successful_rows)


def run_batch(page, targets: list[dict[str, str]], results: list[dict[str, str]]) -> None:
    total = len(targets)
    for index, professor in enumerate(targets, start=1):
        print(
            f"[{index}/{total}] "
            f"正在抓取 {professor['name']} ({professor['author_id']})"
        )

        row = {
            "staff_id": professor.get("staff_id", ""),
            "name": professor["name"],
            "author_id": professor["author_id"],
            "hindex": "",
            "status": "success",
            "error": "",
        }

        try:
            hindex = fetch_hindex_for_professor(page, professor)
            row["hindex"] = str(hindex)
            print(f"  h-index: {hindex}")
        except Exception as error:
            row["status"] = "failed"
            row["error"] = str(error)
            print("  抓取失敗：")
            print(f"  {error}")

        results.append(row)
        write_results(results)
        sync_results_to_database(results)
        time.sleep(2)


def fetch_all_hindexes() -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    targets = get_scopus_targets()

    if not targets:
        print("目前沒有設定 Scopus Author ID 的成員。")
        return results

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        wait_for_manual_verification(page, targets[0]["author_id"])

        print("開始第一輪抓取。")
        run_batch(page, targets, results)

        failed_professors = [
            professor
            for professor in targets
            if any(
                row["author_id"] == professor["author_id"] and row["status"] == "failed"
                for row in results
            )
        ]

        if failed_professors:
            print(f"第一輪有 {len(failed_professors)} 位失敗，開始重試一次。")
            results = [
                row for row in results
                if row["author_id"] not in {p["author_id"] for p in failed_professors}
            ]
            write_results(results)
            sync_results_to_database(results)
            run_batch(page, failed_professors, results)
        else:
            print("第一輪全部成功，不需要重試。")

        browser.close()

    sync_results_to_database(results)
    return results


if __name__ == "__main__":
    try:
        results = fetch_all_hindexes()
        success_count = sum(1 for row in results if row["status"] == "success")
        print(f"已完成，共成功 {success_count}/{len(results)} 位。")
        if results:
            print(f"結果已輸出到：{OUTPUT_FILE}")
            print("網站 staff 資料表中的 Scopus h-index 也已同步更新。")
    except Exception as error:
        print("執行失敗：")
        print(error)
