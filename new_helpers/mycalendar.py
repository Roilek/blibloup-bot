from datetime import datetime


def build_ics_event(summary: str, start_datetime: datetime, end_datetime: datetime, location=None, description=None) -> str:
    event = f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//My Calendar//EN\nBEGIN:VEVENT\n"
    event += f"SUMMARY:{summary}\n"
    event += f"DTSTART:{start_datetime.strftime('%Y%m%dT%H%M%S')}\n"
    event += f"DTEND:{end_datetime.strftime('%Y%m%dT%H%M%S')}\n"
    if location:
        event += f"LOCATION:{location}\n"
    if description:
        event += f"DESCRIPTION:{description}\n"
    event += "END:VEVENT\nEND:VCALENDAR"
    return event

# save the ics file
def save_ics_event(event, filename):
    with open(filename, 'w') as f:
        f.write(event)

# create a calendar event
def create_event_ics(event_name, start_datetime, end_datetime, location=None, description=None):
    event = build_ics_event(event_name, start_datetime, end_datetime, location, description)
    save_ics_event(event, 'event.ics')
    return 'event.ics'

