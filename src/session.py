from typing import List, Callable

from event_data_providers import EventDataProvider
from metadata_provider import MetadataProvider
from time_utils import cast_and_convert_specific_dates


def create_status_filter(status: str):
    def status_filter(_, metadata) -> bool:
        return metadata.get("status") == status

    return status_filter


def create_city_filter(city: str) -> Callable[[dict, dict], bool]:
    def city_filter(event, _) -> bool:
        return event.get("city") == city

    return city_filter


def create_state_filter(state: str) -> Callable[[dict, dict], bool]:
    def state_filter(event, _) -> bool:
        return event.get("state") == state

    return state_filter


class Session:
    def __init__(self, event_provider: EventDataProvider, metadata_provider: MetadataProvider):
        self.event_provider = event_provider
        self.metadata_provider = metadata_provider

    def all_events(self):
        return self.get_filtered_events()

    def cancelled_events(self):
        return self.get_filtered_events([create_status_filter("Cancelled")])

    def pending_events(self):
        return self.get_filtered_events([create_status_filter("Pending")])

    def accepted_events(self):
        return self.get_filtered_events([create_status_filter("Submitted")])

    def __iter__(self, filters: List[Callable[[dict, dict], bool]] = None):
        for event in self.event_provider.read():
            cast_and_convert_specific_dates(event)

            event_metadata = self.metadata_provider.read(event)

            if filters is None or all(filter_func(event, event_metadata) for filter_func in filters):
                yield event, self.metadata_provider.read(event)

    def get_filtered_events(self, filters: List[Callable[[dict, dict], bool]] = None):
        filtered_events = []

        for event, event_metadata in self:
            if filters is None or all(filter_func(event, event_metadata) for filter_func in filters):
                filtered_events.append((event, event_metadata))

        return filtered_events
