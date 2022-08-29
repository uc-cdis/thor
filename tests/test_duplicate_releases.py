# test_run_task.py
from requests import request
import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import clear_tables
from thor.dao.release_dao import create_release

client = TestClient(app)


@pytest.mark.parametrize("release_name", ["release_dup_test"])
def test_duplicate_releases(release_name):
    """
    Tests the running of one task to make sure that it is run properly. 
    """
    clear_tables()

    first_rid = create_release(release_name, "PENDING")
    assert first_rid != None

    with pytest.raises(Exception):
        second_rid = create_release(release_name, "PENDING")
        assert second_rid == None
