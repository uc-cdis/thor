# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>" pragma: allowlist secret
import os
from thor import load_env_vars

username = load_env_vars.username  # pragma: allowlist secret

password = load_env_vars.password  # pragma: allowlist secret

IPadd = load_env_vars.IPadd  # pragma: allowlist secret

portNum = load_env_vars.portNum  # pragma: allowlist secret

DBname = load_env_vars.DBname  # pragma: allowlist secret

# username = os.environ["username"]  # pragma: allowlist secret

# password = os.environ["password"]  # pragma: allowlist secret

# IPadd = os.environ["IPadd"]  # pragma: allowlist secret

# portNum = os.environ["portNum"]  # pragma: allowlist secret

# DBname = os.environ["DBname"]  # pragma: allowlist secret

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
