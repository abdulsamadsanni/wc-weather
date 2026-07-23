"""Step 1 - load World Cup matches from the public international-results dataset.

Source: github.com/martj42/international_results (CC0). ~49k internationals
since 1872; we keep only tournament == "FIFA World Cup". The file is fetched
with requests (which bundles its own CA certificates) rather than pandas' URL
reader, to avoid Windows certificate-store SSL errors under some setups.
"""
from __future__ import annotations
import io, pathlib
import requests
import pandas as pd

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(exist_ok=True)
RESULTS_URL = ("https://raw.githubusercontent.com/martj42/"
               "international_results/master/results.csv")


def load_world_cup() -> pd.DataFrame:
    csv_text = requests.get(RESULTS_URL, timeout=30).text
    df = pd.read_csv(io.StringIO(csv_text), parse_dates=["date"])
    wc = df[df["tournament"] == "FIFA World Cup"].copy()
    wc["year"] = wc["date"].dt.year
    wc["month"] = wc["date"].dt.month
    wc["goals"] = (wc["home_score"] + wc["away_score"]).astype("Int64")
    wc = wc.dropna(subset=["home_score", "away_score"]).reset_index(drop=True)
    return wc


if __name__ == "__main__":
    wc = load_world_cup()
    wc.to_csv(DATA / "wc_matches_raw.csv", index=False)
    print(f"Loaded {len(wc)} World Cup matches, "
          f"{wc['year'].min()}-{wc['year'].max()}")
