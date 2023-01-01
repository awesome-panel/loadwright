# conftest.py
"""Shared configuration and fixtures for testing Panel"""
import panel as pn
import pytest

PORT = [6000]

@pytest.fixture
def port():
    PORT[0] += 1
    return PORT[0]

@pytest.fixture(autouse=True)
def server_cleanup():
    """
    Clean up server state after each test.
    """
    try:
        yield
    finally:
        pn.state.kill_all_servers()
        pn.state._indicators.clear()
        pn.state._locations.clear()
        pn.state._templates.clear()
        pn.state._views.clear()
        pn.state._loaded.clear()
        pn.state.cache.clear()
        pn.state._scheduled.clear()
        if pn.state._thread_pool is not None:
            pn.state._thread_pool.shutdown(wait=False)
            pn.state._thread_pool = None
