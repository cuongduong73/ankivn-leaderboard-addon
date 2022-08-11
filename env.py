from decouple import config

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM = config("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = config("JWT_EXPIRE_MINUTES")

DATABASE_URL = config("DATABASE_URL").replace("://", "ql://", 1)