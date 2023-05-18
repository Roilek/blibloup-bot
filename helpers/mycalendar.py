import io

from icalendar import Calendar, Event
from datetime import datetime, timedelta

from telegram import InputFile


def create_event_ics(event_name: str, start_datetime: datetime, end_datetime: datetime):
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
    # with open('../resources/products/event.ics', 'wb') as f:
    #    f.write(cal.to_ical())

    file_buffer = io.BytesIO()
    file_buffer.write(cal.to_ical())
    file_buffer.seek(0)

    input_file = InputFile(file_buffer, filename='event.ics')

    return input_file


if __name__ == "__main__":
    # Example usage
    name = "My Event"
    start = datetime(2023, 5, 18, 10, 0, 0)
    end = datetime(2023, 5, 18, 12, 0, 0)

    create_event_ics(name, start, end)
