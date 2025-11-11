import yaml
import pytest
from icalendar import Calendar

from main import build_event


@pytest.mark.parametrize("date,events", [
    (day['date'], day['events'])
    for day in yaml.safe_load(open('contract1.yaml'))['schedule']
])
def test_schedule_day(date, events):
    """Test each day's schedule as a separate test case."""

    calendar = Calendar()

    for event in events:
        event = build_event(date.strftime('%Y-%m-%d'), event['time'])
        calendar.add_component(event)

    print(calendar.to_ical().decode("utf-8"))
