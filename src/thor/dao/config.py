# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>" pragma: allowlist secret

username = "postgres"  # pragma: allowlist secret

password = ""  # pragma: allowlist secret

IPadd = "localhost"  # pragma: allowlist secret

portNum = "5432"  # pragma: allowlist secret

DBname = "thor_test_tmp"  # pragma: allowlist secret

RELEASE_DATABASE_URL = (
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
