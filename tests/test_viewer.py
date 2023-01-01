from loadwright import LoadTestViewer, read_loadwright_file, LoadTestRunner
from .test_io import FIXTURE
import pytest

def test_constructor():
    data = read_loadwright_file(FIXTURE)
    LoadTestViewer(data=data)

def _viewer():
    data = read_loadwright_file(FIXTURE)
    return LoadTestViewer(data=data)


@pytest.mark.asyncio
async def test_component_2(port=6001):
    async with LoadTestRunner.serve(_viewer, port=port) as host:
        await LoadTestRunner(host=host, headless=False, n_users=1).run()