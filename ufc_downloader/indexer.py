"""
Query the SportsDB for all UFC events in the current year and cache them.
"""

import datetime
import json
import logging
import os

import requests

# Initialize logger
logger = logging.getLogger(__name__)

SPORTSDB_QUERY_TEMPLATE = (
    "https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4443&s={year}"
)


def update_index(force_update: bool = False, freshness_days: int = 7) -> bool:
    try:
        # Get the current year
        current_year = datetime.datetime.now().year
        events_filename = f"events_{current_year}.json"
        # Check if the events file has been modified within the specified freshness period
        if not force_update:
            try:
                file_mod_time = datetime.datetime.fromtimestamp(
                    os.path.getmtime(events_filename)
                )
                freshness_delta = datetime.timedelta(days=freshness_days)
                if file_mod_time > datetime.datetime.now() - freshness_delta:
                    logger.info(
                        f"{events_filename} has been modified within the last {freshness_days} days. Skipping update."
                    )
                    return True
            except FileNotFoundError:
                # File does not exist, proceed with update
                pass

        # Query the SportsDB
        response = requests.get(SPORTSDB_QUERY_TEMPLATE.format(year=current_year))

        if response.status_code != 200:
            logger.error(
                f"Failed to retrieve events: {response.status_code}, Response: {response.text}"
            )
            return False

        events = response.json().get("events", [])

        # Dump the events to file
        with open(events_filename, "w") as file:
            json.dump(events, file)

        return True

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False


def read_index() -> list:
    try:
        current_year = datetime.datetime.now().year
        events_filename = f"events_{current_year}.json"

        with open(events_filename, "r") as file:
            events = json.load(file)

        return events

    except FileNotFoundError:
        logger.error(f"{events_filename} does not exist.")
        return []

    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from {events_filename}.")
        return []

    except Exception as e:
        logger.error(f"An error occurred while reading the index: {e}")
        return []


def read_index_events_by_titles():
    """Map titles to events"""
    events = read_index()
    events_by_titles = {
        event["strEvent"]: event for event in events if "strEvent" in event
    }
    return events_by_titles
