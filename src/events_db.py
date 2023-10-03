import json
import os
from datetime import datetime

import pytz
from typing import Any

from jinja2 import Template


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


def events(file_path, min_population=None, min_obscuration=None):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        sessions_directory = os.path.join("..\\sessions", os.path.splitext(os.path.basename(file_path))[0])

        if isinstance(data, list):
            for obj in data:
                if min_population is not None and obj["population"] <= min_population:
                    continue

                if min_obscuration is not None and obj["obscuration"] <= min_obscuration:
                    continue

                cast_and_convert_specific_dates(obj)

                metadata_, metadata_file = metadata(sessions_directory, obj)

                yield obj, metadata_, metadata_file
        else:
            raise ValueError("JSON data is not an array.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


def metadata(session_dir: str, event: dict) -> tuple[dict[str, str | Any] | Any, str]:
    # Ensure the session directory exists; create it if not
    os.makedirs(session_dir, exist_ok=True)

    session_file = os.path.join(session_dir, f"{event['id']}_metadata.json")

    if os.path.exists(session_file):
        # If the file already exists, read and return its contents
        with open(session_file, "r") as file:
            session_metadata = json.load(file)
    else:
        # If the file doesn't exist, create it and initialize metadata
        session_metadata = {
            "city_id": event["id"],
            "status": "Pending",
            "notes": ""
        }
        with open(session_file, "w") as file:
            json.dump(session_metadata, file)

    return session_metadata, session_file


def name(event: dict) -> str:
    return f"🌑✨ 2024 Total Solar Eclipse {event['city_ascii']}, {event['admin_name']} ✨🌑"


def read_details_template(file_path) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        template_script = file.read()
    return template_script


def details(event: dict) -> str:
    # Convert admin_name to a hashtag format
    hashtag = '#'.join(word.capitalize() for word in event["admin_name"].split()) + 'SolarEclipse'

    # Create the event details string
    return Template(read_details_template('../templates/details.txt')).render(
        domain='absoluteeclipse.com',
        hashtag=hashtag,
        partial_begin=event["partial_begin"],
        peak_time=event["peak_time"],
        partial_end=event["partial_end"],
        city=event["city_ascii"],
        state=event["admin_name"],
    ).lstrip('\n')
