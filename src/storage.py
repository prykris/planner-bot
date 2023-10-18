import json
from json import JSONDecodeError

from prompts import Language


def save_credentials(username_: str, password_: str, language: Language, filename='credentials.json') -> None:
    with open(f'../{filename}', 'w') as f:
        json.dump({"email": username_, "password": password_, "language": language.value}, f)


def load_credentials(filename='credentials.json') -> (str, str):
    try:
        with open(f'../{filename}', 'r') as f:
            data = json.load(f)
            return data["email"], data["password"], Language(data["language"])
    except KeyError as e:
        print(f'Akreditācijas failā iztrūka informācija, fails tiks ignorēts un dati tiks pieprasīti atkārtoti')
    except JSONDecodeError as e:
        print('Akreditācijas failu neizdevās ielādēt, iespējams fails ir tukšs')

    return None, None, None
