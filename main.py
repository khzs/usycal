import datetime
import os
import shutil
import tempfile
import pytz

from playwright.sync_api import sync_playwright
from pydantic_settings import BaseSettings
from icalendar import Calendar, Event


class Settings(BaseSettings):
    filename: str = "calendar.ics"
    calendar_name: str = "Work"

settings = Settings()
budapest_tz = pytz.timezone("Europe/Budapest")


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


def build_event(selected_day: str, start_time: str) -> Event:
    dt_obj_start = datetime.datetime.strptime(f"{selected_day} {start_time}", '%Y-%m-%d %I:%M %p')
    aware_dtstart = budapest_tz.localize(dt_obj_start)

    event = Event()
    event.add('summary', 'Busy')
    event.add('dtstart', aware_dtstart)
    event.add('dtend', aware_dtstart + datetime.timedelta(hours=1))
    return event


def main():
    url = get_secret_url()
    print("Loaded secret URL (not printing for security).")

    # todo : read all events up until yesterday and carry them over

    if os.path.exists(settings.filename):
        os.remove(settings.filename)

    calendar = Calendar()
    calendar.add('version', '2.0')
    calendar.add('x-wr-calname', settings.calendar_name)

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
                selected_day = (today + datetime.timedelta(days=i))
                print(selected_day)
                page.locator(f"#header_{selected_day}").click()
                start_times = page.locator("div.KSLGX.RRC0b").all_inner_texts()
                print(start_times)
                durations = page.locator("div.YeV_D.RRC0b").all_inner_texts()
                print(durations)
                assert len(start_times) == len(durations)

                for j in range(len(start_times)):
                    event = build_event(selected_day.strftime('%Y-%m-%d'), start_times[j])
                    calendar.add_component(event)
                




            browser.close()

        finally:
            with open(settings.filename, "wb") as f:
                f.write(calendar.to_ical())
            shutil.rmtree(user_data_dir)


if __name__ == "__main__":
    main()
