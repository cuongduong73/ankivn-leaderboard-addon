from decouple import config

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM = config("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = config("JWT_EXPIRE_MINUTES")

MIN_ADDON_VERSION = config("MIN_ADDON_VERSION")

DATABASE_URL = config("DATABASE_URL").replace("://", "ql://", 1)
#DATABASE_URL = config("DATABASE_URL")