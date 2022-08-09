from decouple import config

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

DB_FILE = config("database")