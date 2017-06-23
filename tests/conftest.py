import pytest
from .fake_simple_client import FakeSimpleRecordClient


def pytest_addoption(parser):
    parser.addoption('--visualizer',
                     action='store',
                     default=None,
                     help='which visualizer type to choose for rendering tests')
    parser.addoption('--signal-generator',
                     action='store',
                     default=None,
                     help='which signal generator to choose for rendering tests')


@pytest.fixture
def fake_simple_record_client():
    yield FakeSimpleRecordClient(source='whatever')
