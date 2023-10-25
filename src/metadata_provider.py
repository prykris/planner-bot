import json
import os
import shutil
import tempfile
from abc import ABC, abstractmethod


class MetadataProvider(ABC):

    @abstractmethod
    def read(self, event: dict) -> dict:
        pass

    @abstractmethod
    def save(self, event: dict, metadata: dict):
        pass


def save_to_file(data, file_path):
    json.dump(data, open(file_path, "w"))


class LocalMetadataProvider(MetadataProvider):
    def __init__(self, sessions_directory: str):
        self.cached = None
        self.sessions_directory = sessions_directory

        os.makedirs(sessions_directory, exist_ok=True)

        self.load_and_merge()

    def load_and_merge(self):
        single_file_path = os.path.join(self.sessions_directory, "metadata.json")
        backup_path = single_file_path + ".bak"
        data_map = {}

        if os.path.exists(single_file_path):
            try:
                with open(single_file_path, "r") as file:
                    data_map = json.load(file)
            except Exception as e:
                print(f"Error loading {single_file_path}: {e}")
                if os.path.exists(backup_path):
                    print("Loading from backup...")
                    shutil.copy(backup_path, single_file_path)
                    with open(single_file_path, "r") as backup_file:
                        data_map = json.load(backup_file)

        for filename in os.listdir(self.sessions_directory):
            if filename.endswith(".json") and filename != "metadata.json":
                with open(os.path.join(self.sessions_directory, filename), "r") as file:
                    metadata_object = json.load(file)

                data_map[metadata_object['city_id']] = metadata_object
                os.remove(os.path.join(self.sessions_directory, filename))

        self.cached = data_map

        save_to_file(data_map, single_file_path)  # Save merged data

    def save(self, event: dict, metadata: dict):
        event_id = str(event['id'])
        event_file_path = os.path.join(self.sessions_directory, f"{event_id}.json")

        save_to_file(metadata, event_file_path)

        self.cached[event_id] = metadata

    def read(self, event: dict) -> dict:
        return self.cached.get(str(event['id']), {"city_id": event["id"], "status": "Pending", "notes": ""})
