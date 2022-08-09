# This file is responsible for signing, encoding, decoding and returning JWTs

from datetime import datetime
import time
from jose import jwt
from ..env import JWT_SECRET, JWT_ALGORITHM
from ..models.auth_model import JWTPayloadSchema




def encodeJWT(username: str, duration_minutes: int = 10) -> dict[str, str]:
    payload = JWTPayloadSchema(username=username,
                               expired=(time.time() + 60 * duration_minutes)).dict()
    access_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return {"access_token": access_token}

def decodeJWT(token: str) -> JWTPayloadSchema:
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return JWTPayloadSchema(**decoded_token)
