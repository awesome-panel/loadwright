from loadwright import read_loadwright_file
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
FIXTURE = ROOT/"loadwright_fixture.csv"

def test_read_loadwright_file():
    data = read_loadwright_file(FIXTURE)
    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    assert data.user.dtype=="object"
    assert data.start.dtype=="<M8[ns]"
    assert data.stop.dtype=="<M8[ns]"
    assert set(data.columns)=={'event', 'user', 'start', 'stop', 'start_seconds', 'stop_seconds', 'duration'}