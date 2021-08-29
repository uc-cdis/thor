### config.py

# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>" pragma: allowlist secret

username = "username"  # pragma: allowlist secret

password = "password"  # pragma: allowlist secret

IPadd = "localhost"  # pragma: allowlist secret

portNum = "1234"  # pragma: allowlist secret

DBname = "ReleaseTask"  # pragma: allowlist secret

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

# print(DATABASE_URL)
