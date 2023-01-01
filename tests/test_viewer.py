"""We can view the results of a Loadwright load test"""
import pytest

from loadwright import LoadTestRunner, LoadTestViewer

from .test_io import FIXTURE


def test_constructor():
    """We can construct a LoadTestViewer"""
    LoadTestViewer(data=FIXTURE)


def _viewer():
    return LoadTestViewer(data=FIXTURE)


@pytest.mark.asyncio
async def test_component_2(port=6001):
    """A User can load the LoadTestViewer"""
    async with LoadTestRunner.serve(_viewer, port=port) as host:
        await LoadTestRunner(host=host, headless=False, n_users=1).run()
