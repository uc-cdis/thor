# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>" pragma: allowlist secret
import os

username = os.environ["username"]  # pragma: allowlist secret

password = os.environ["password"]  # pragma: allowlist secret

IPadd = os.environ["IPadd"]  # pragma: allowlist secret

portNum = os.environ["portNum"]  # pragma: allowlist secret

DBname = os.environ["DBname"]  # pragma: allowlist secret

DATABASE_URL = (
    "postgresql+psycopg2://"  # pragma: allowlist secret
    + username  # pragma: allowlist secret
    + ":"
    + password  # pragma: allowlist secret
    + "@"
    + IPadd  # pragma: allowlist secret
    + ":"
    + portNum  # pragma: allowlist secret
    + "/"
    + DBname  # pragma: allowlist secret
)

if __name__ == "__main__":
    print(DATABASE_URL)
