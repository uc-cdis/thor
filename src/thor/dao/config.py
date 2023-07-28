# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>" pragma: allowlist secret
from starlette.config import Config
from starlette.datastructures import Secret
import os
print(f"Env var DEVELOPMENT is set to {os.getenv('DEVELOPMENT')}")
if os.getenv("DEVELOPMENT") == "true":
    config = Config("thor.env", keep_comments=False)
else:
    config = Config("/src/thor.env", keep_comments=False)

DB_HOST = config("DB_HOST", default=None)
DB_PORT = config("DB_PORT", cast=int, default=None)
DB_USER = config("DB_USER", default=None)
DB_PASSWORD = config("DB_PASSWORD", cast=Secret, default="")
DB_DATABASE = config("DB_DATABASE", default=None)

DATABASE_URL = (
    "postgresql+psycopg2://"  # pragma: allowlist secret
    + DB_USER  # pragma: allowlist secret
    + ":"
    + str(DB_PASSWORD)  # pragma: allowlist secret
    + "@"
    + DB_HOST  # pragma: allowlist secret
    + ":5432"
    + "/"
    + DB_DATABASE  # pragma: allowlist secret
)

if __name__ == "__main__":
    print(DATABASE_URL)
