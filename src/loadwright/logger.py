import time
from typing import Dict
import datetime
import pandas as pd
import param
from pathlib import Path
from contextlib import contextmanager

TEST_RESULTS_PATH = "test_results"
TEST_RESULTS_FILE  = "loadwright.csv"

class Logger(param.Parameterized):
    results: Dict = param.List(class_=dict)
    path: str = param.String(TEST_RESULTS_PATH)
    file: str = param.String(TEST_RESULTS_FILE)
    auto_save: str = param.Boolean(True)
    auto_archive: str = param.Boolean(True)

    def __init__(self, **params):
        super().__init__(**params)

        self.reset()

    @contextmanager
    def event(self, name: str, user: str, **kwargs):
        start = time.time()
        if not self._start:
            self._start = start
        yield
        stop = time.time()
        result = {
            "event": name,
            "user": user,
            "start": pd.to_datetime(start, unit="s"),
            "stop": pd.to_datetime(stop, unit="s"),
            "start_seconds": start - self._start,
            "stop_seconds": stop - self._start,
            "duration": stop - start,
            **kwargs,
        }
        self.results.append(result)
        if self.auto_save:
            self.save()
            if self.auto_archive:
                self.archive()

    @property
    def data(self) -> pd.DataFrame:
        return pd.DataFrame(self.results)

    def reset(self):
        self.results = []
        self._start = None

    def save(self):
        path = Path(self.path)
        path.mkdir(parents=True, exist_ok=True)
        file = path / self.file
        self.data.to_csv(file, index=True)

    def archive(self):
        data = self.data
        now = data.start.min()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename, extension = self.file.split(".")
        path = Path(self.path)
        file = path/"archive"/f"{filename}_{timestamp}.{extension}"
        file.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(file, index=True)