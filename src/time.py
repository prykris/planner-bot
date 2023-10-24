import pytz


def set_datetime_timezone(dt: datetime, timezone: str) -> datetime:
    return pytz.utc.localize(dt, is_dst=None).astimezone(pytz.timezone(timezone))


def cast_and_convert_specific_dates(event_data: dict) -> None:
    date_keys = ["partial_begin", "total_begin", "peak_time", "total_end", "partial_end"]

    for key in date_keys:
        if key in event_data and isinstance(event_data[key], str):
            try:
                # Parse the value as a datetime in the event's time zone
                date_object = datetime.fromisoformat(event_data[key])

                event_data[key] = set_datetime_timezone(date_object, event_data["timezone"])
                event_data[f'{key}_current'] = set_datetime_timezone(date_object, "Europe/Riga")
                event_data[f'{key}_utc'] = date_object.isoformat()
            except ValueError:
                # If parsing fails, keep the original value
                pass