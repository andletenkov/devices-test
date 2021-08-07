import os
import pytest

from client import DeviceTestClient


@pytest.fixture(scope='session')
def device_client() -> DeviceTestClient:
    """
    Yields device testing client instance.
    """
    client = DeviceTestClient(
        os.getenv('DEVICE_APP_HOST', 'localhost'),
        int(os.getenv('DEVICE_APP_PORT', 5585))
    )
    yield client
    client.close()
