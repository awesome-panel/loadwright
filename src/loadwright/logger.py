"""Functionality for logging LoadTestRunner events"""
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List

import pandas as pd
import param

TEST_RESULTS_PATH = "test_results"
TEST_RESULTS_FILE = "loadwright.csv"


class Logger(param.Parameterized):
    """Used to log events while running a LoadTestRunner"""

    results: List[Dict] = param.List(
        class_=dict, doc="A list of results. Each result is a dictionary"
    )
    path: str = param.String(
        TEST_RESULTS_PATH, doc=f"The path to log to. Defaults to {TEST_RESULTS_PATH}"
    )
    file: str = param.String(
        TEST_RESULTS_FILE, doc=f"The file to log to. Defaults to {TEST_RESULTS_FILE}"
    )
    auto_save: str = param.Boolean(
        True, doc="""Whether or not to save automatically when logging an event"""
    )
    auto_archive: str = param.Boolean(
        True, doc="""Whether or not to save automatically to the archive when logging an event"""
    )

    def __init__(self, **params):
        super().__init__(**params)

        self._start = None
        self.reset()

    @contextmanager
    def event(self, name: str, user: str, **kwargs):
        """Log an event

        Args:
            name (str): The name of the event
            user (str): The name of the user triggering the event
        """
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
        """Returns the results as a DataFrame"""
        return pd.DataFrame(self.results)

    def reset(self):
        """Resets the results to the empty list"""
        self.results = []
        self._start = None

    def save(self):
        """Saves the results to self.path / self.file"""
        path = Path(self.path)
        path.mkdir(parents=True, exist_ok=True)
        file = path / self.file
        self.data.to_csv(file, index=True)

    def archive(self):
        """Archives the results to self.path / "archive" / self.file_{now}"""
        data = self.data
        now = data.start.min()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename, extension = self.file.split(".")
        path = Path(self.path)
        file = path / "archive" / f"{filename}_{timestamp}.{extension}"
        file.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(file, index=True)
