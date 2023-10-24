import json
from abc import ABC
from typing import List


class EventDataProvider(ABC):

    def read(self) -> List[dict]:
        pass


class LocalEventDataProvider(EventDataProvider):

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.cached = None

    def read(self, fresh: bool = False) -> List[dict]:
        if fresh or self.cached is None:
            self.cached = self._read()

        return self.cached

    def _read(self):
        with open(self.file_path, "r") as file:
            return json.load(file)
