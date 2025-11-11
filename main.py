import datetime
import os
import shutil
import tempfile
from playwright.sync_api import sync_playwright


def get_secret_url():
    secret_url = os.environ.get("SECRET_URL")

    if not secret_url and os.path.exists("secret_url.txt"):
        with open("secret_url.txt", "r", encoding="utf-8") as f:
            secret_url = f.read().strip()

    if not secret_url:
        raise RuntimeError(
            "Secret URL not found. Set SECRET_URL env variable or create secret_url.txt."
        )

    return secret_url

def main():
    url = get_secret_url()
    print("Loaded secret URL (not printing for security).")

    with sync_playwright() as p:
        # Create an isolated temp profile
        user_data_dir = tempfile.mkdtemp()

        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=True,
                channel="msedge"
            )

            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")

            today = datetime.date.today()
            for i in range(7):
                page.locator(f"#header_{today + datetime.timedelta(days=i)}").click()
                start_times = page.locator("div.KSLGX.RRC0b").all_inner_texts()
                print(start_times)
                durations = page.locator("div.YeV_D.RRC0b").all_inner_texts()
                print(durations)
                assert len(start_times) == len(durations)

            browser.close()

        finally:
            shutil.rmtree(user_data_dir)


if __name__ == "__main__":
    main()
