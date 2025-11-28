from datetime import datetime, date, timedelta
import os
import shutil
import tempfile
import pytz

from playwright.sync_api import sync_playwright
from pydantic_settings import BaseSettings
from icalendar import Calendar, Event
from timelength import TimeLength


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


def build_event(selected_day: date, start_time: str, duration: str) -> Event:
    dt_obj_time = datetime.strptime(start_time, '%I:%M %p')
    dt_obj_merged = datetime.combine(selected_day, dt_obj_time.time())
    dtstart = budapest_tz.localize(dt_obj_merged)

    event = Event()
    event.add('summary', 'Busy')
    event.add('dtstart', dtstart)
    event.add('dtend', dtstart + TimeLength(duration).result.delta)

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

            today = date.today()
            for i in range(7):
                selected_day = (today + timedelta(days=i))
                print(selected_day)
                page.locator(f"#header_{selected_day}").click()
                start_times = page.locator("div.KSLGX.RRC0b").all_inner_texts()
                print(start_times)
                durations = page.locator("div.YeV_D.RRC0b").all_inner_texts()
                print(durations)
                assert len(start_times) == len(durations)

                for j in range(len(start_times)):
                    if "day" not in durations[j]:
                        event = build_event(selected_day, start_times[j], durations[j])
                        calendar.add_component(event)

            browser.close()

        finally:
            with open(settings.filename, "wb") as f:
                f.write(calendar.to_ical())
            shutil.rmtree(user_data_dir)


if __name__ == "__main__":
    main()
