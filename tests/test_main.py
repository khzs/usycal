import yaml
import pytest
from icalendar import Calendar
from timelength import TimeLength

from main import build_event


@pytest.mark.parametrize("date,events", [
    (day['date'], day['events'])
    for day in yaml.safe_load(open('tests/contract1.yaml'))['schedule']
])
def test_schedule_day(date, events):
    """Test each day's schedule as a separate test case."""

    calendar = Calendar()

    for event in events:
        if "day" not in event['duration']:
            ical_event = build_event(date, event['time'], event['duration'])
            calendar.add_component(ical_event)

    print(calendar.to_ical().decode("utf-8"))


@pytest.mark.parametrize("date,events", [
    (day['date'], day['events'])
    for day in yaml.safe_load(open('tests/contract1.yaml'))['schedule']
])
def test_duration(date, events):
    """Test each day's schedule as a separate test case."""

    for event in events:
        tl = TimeLength(event['duration'])
        print(tl.result.delta)

