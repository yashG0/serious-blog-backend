from os import getenv
from jose import jwt

SECRET_KEY = getenv("SECRET_KEY_JWT", "my-secret-key")
ALGORITH = getenv("ALGORITH", "HS256")


def create_access_token(data: dict) -> str:
    encode_data = jwt.encode(data, key=SECRET_KEY, algorithm=ALGORITH)
    return encode_data


def verify_token(token: str) -> dict:
    decode_data = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITH)
    return decode_data
