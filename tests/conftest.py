import pytest
from swagmail import app


@pytest.fixture(scope='module')
def client():
    client = app.test_client()
    return client
