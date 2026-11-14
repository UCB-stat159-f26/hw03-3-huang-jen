import socket
import matplotlib
import pytest

matplotlib.use("Agg")

def _no_network(*args, **kwargs):
    raise AssertionError("Automated tests must not contact live servers.")

@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    """Fail immediately if any test attempts to hit a live server."""
    monkeypatch.setattr(socket.socket, "connect", _no_network)
    monkeypatch.setattr(socket, "create_connection", _no_network)