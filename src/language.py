from enum import Enum


class Language(Enum):
    Latvian = 1
    English = 2

    def __str__(self):
        return 'Latviešu' if self.value == 1 else 'Angļu'