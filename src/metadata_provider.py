import json
import os
from abc import ABC, abstractmethod


class MetadataProvider(ABC):

    @abstractmethod
    def read(self, event: dict) -> dict:
        pass

    @abstractmethod
    def save(self, event: dict, metadata: dict):
        pass


class LocalMetadataProvider(MetadataProvider):
    def __init__(self, sessions_directory: str):
        self.cached = None
        self.sessions_directory = sessions_directory

        # Ensure the session directory exists; create it if not
        os.makedirs(sessions_directory, exist_ok=True)

        # Load data from individual files and merge it into a single file
        self.load_and_merge()

    def load_and_merge(self):
        # Load data from the single file (if it exists)
        single_file_path = os.path.join(self.sessions_directory, "metadata.json")
        data_map = {}

        if os.path.exists(single_file_path):
            with open(single_file_path, "r") as file:
                data_map = json.load(file)

        # Load data from individual files and prepare a list of files to be deleted
        files_to_delete = []

        for filename in os.listdir(self.sessions_directory):
            if filename.endswith(".json") and filename != "metadata.json":
                with open(os.path.join(self.sessions_directory, filename), "r") as file:
                    metadata_object = json.load(file)

                data_map[metadata_object['city_id']] = metadata_object
                files_to_delete.append(filename)  # Prepare to delete individual files

        # Save the merged data back to the single file
        with open(single_file_path, "w") as file:
            json.dump(data_map, file, indent=4)

        # Delete individual files
        for filename in files_to_delete:
            os.remove(os.path.join(self.sessions_directory, filename))

        self.cached = data_map

    def filepath_for_event(self, event: dict) -> str:
        return os.path.join(self.sessions_directory, f"{event['id']}_metadata.json")

    def read(self, event: dict) -> dict:
        return self.cached.get(str(event['id']), {"city_id": event["id"], "status": "Pending", "notes": ""})

    def save(self, event: dict, metadata: dict):
        self.cached[event['id']] = metadata
        single_file_path = os.path.join(self.sessions_directory, "metadata.json")

        with open(single_file_path, "w") as file:
            json.dump(self.cached, file)
