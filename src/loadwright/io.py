import pandas as pd
def read_loadwright_file(file="test_results/loadwright.csv")->pd.DataFrame:
    return pd.read_csv(file, parse_dates=["start", "stop"], dtype={"user": "str"}, index_col=0)