from icalendar import Calendar, Event
from datetime import datetime, timedelta


def create_event_ics(event_name, start_datetime, end_datetime):
    cal = Calendar()
    event = Event()

    # Set event name
    event.add('summary', event_name)

    # Set start and end date/time
    event.add('dtstart', start_datetime)
    event.add('dtend', end_datetime)

    # Set event as an all-day event (optional)
    # event.add('dtstart', start_datetime.date())
    # event.add('dtend', end_datetime.date() + timedelta(days=1))
    # event.add('X-MICROSOFT-CDO-ALLDAYEVENT', 'TRUE')

    cal.add_component(event)

    # Save the calendar to an .ics file
    with open('event.ics', 'wb') as f:
        f.write(cal.to_ical())


# Example usage
event_name = "My Event"
start_datetime = datetime(2023, 5, 18, 10, 0, 0)
end_datetime = datetime(2023, 5, 18, 12, 0, 0)

create_event_ics(event_name, start_datetime, end_datetime)
