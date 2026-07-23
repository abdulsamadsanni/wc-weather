"""Step 2 - attach lat/lon to each host city, fully offline.

geonamescache ships a city database, so no API call or key is needed. A small
alias table covers names the dataset spells differently (Cologne, Seville, the
Qatar venues, the US stadium towns, etc.) to reach 100% coverage.
"""
from __future__ import annotations
import pathlib
import pandas as pd
import geonamescache

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"

ALIAS = {
    "Al Khor": (25.68, 51.50), "Al Rayyan": (25.29, 51.42), "Lusail": (25.42, 51.49),
    "Cologne": (50.94, 6.96), "Frankfurt": (50.11, 8.68), "Nuremberg": (49.45, 11.08),
    "East Rutherford": (40.81, -74.10), "Foxborough": (42.07, -71.25),
    "Washington, D.C.": (38.90, -77.04), "Ekaterinburg": (56.84, 60.61),
    "Nizhny Novgorod": (56.33, 44.00), "Rostov-on-Don": (47.23, 39.72),
    "Gothenburg": (57.71, 11.97), "Nelspruit": (-25.47, 30.97),
    "Nezahualcóyotl": (19.40, -99.01), "Querétaro": (20.59, -100.39),
    "Seville": (37.39, -5.99),
}


def _build_lookup() -> dict[str, tuple[float, float]]:
    cities = geonamescache.GeonamesCache().get_cities()
    best: dict[str, tuple[float, float, int]] = {}
    for c in cities.values():
        nm, pop = c["name"], c["population"]
        if nm not in best or pop > best[nm][2]:
            best[nm] = (c["latitude"], c["longitude"], pop)
    return {k: (v[0], v[1]) for k, v in best.items()}


def geocode(df: pd.DataFrame) -> pd.DataFrame:
    lookup = _build_lookup()
    def find(city: str):
        if city in ALIAS:
            return ALIAS[city]
        return lookup.get(city, (None, None))
    df = df.copy()
    df["lat"], df["lon"] = zip(*df["city"].map(find))
    missing = df[df["lat"].isna()]["city"].unique()
    if len(missing):
        print(f"WARN ungeocoded cities: {sorted(missing)}")
    return df.dropna(subset=["lat", "lon"]).reset_index(drop=True)


if __name__ == "__main__":
    wc = pd.read_csv(DATA / "wc_matches_raw.csv", parse_dates=["date"])
    wc = geocode(wc)
    wc.to_csv(DATA / "wc_matches.csv", index=False)
    print(f"Geocoded {len(wc)} matches across {wc['city'].nunique()} cities")
