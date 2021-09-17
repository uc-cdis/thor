import os
import cdislogging


logger = cdislogging.get_logger(__name__, log_level=os.environ.get("LOGLEVEL", "info"))
