import time

import pytest
from fastapi.testclient import TestClient

from guesthouse.app import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        # TODO: Proper way to check if chproxy has started.
        time.sleep(0.5)
        yield c
