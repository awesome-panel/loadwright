"""Utility io functionality"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_loadwright_file(file: str | Path = "test_results/loadwright.csv") -> pd.DataFrame:
    """Returns the Loadwright csv file as a dataframe

    Args:
        file (str | Path, optional): The path to a Loadwright csv file.
            Defaults to "test_results/loadwright.csv".

    Returns:
        pd.DataFrame: A Pandas DataFrame
    """
    file = Path(file)
    return pd.read_csv(file, parse_dates=["start", "stop"], dtype={"user": "str"}, index_col=0)
