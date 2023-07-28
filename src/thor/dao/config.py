# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>" pragma: allowlist secret
from dotenv import dotenv_values
from starlette.config import Config
from starlette.datastructures import Secret
import os
print(f"Env var DEVELOPMENT is set to {os.getenv('DEVELOPMENT')}")
if os.getenv("DEVELOPMENT") == "true":
    config = dotenv_values("thor.env")
else:
    config = dotenv_values("/src/thor.env")

DB_HOST = config.get("DB_HOST", None)
DB_PORT = config.get("DB_PORT", None)
DB_USER = config.get("DB_USER", None)
DB_PASSWORD = config.get("DB_PASSWORD", "")
DB_DATABASE = config.get("DB_DATABASE", None)

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
