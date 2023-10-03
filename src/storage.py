import json


def save_credentials(username_: str, password_: str, filename='credentials.json') -> None:
    with open(f'../{filename}', 'w') as f:
        json.dump({"email": username_, "password": password_}, f)


def load_credentials(filename='credentials.json') -> (str, str):
    try:
        with open(f'../{filename}', 'r') as f:
            data = json.load(f)
            return data["email"], data["password"]
    except FileNotFoundError:
        return None, None