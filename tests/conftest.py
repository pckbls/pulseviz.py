import pytest
from .fake_simple_client import FakeSimpleRecordClient


@pytest.fixture
def fake_simple_record_client():
    yield FakeSimpleRecordClient(source='whatever')
