"""Step 3 - join real per-match weather from the Open-Meteo archive.

Free, no API key, global coverage back to 1940. For each match this pulls hourly
temperature / humidity / apparent-temperature and summarise the afternoon-to-
evening window, when World Cup matches are played.

1930-1939 predate the archive and come back as NaN, so those tournaments are
excluded from the weather analysis rather than guessed.
"""
from __future__ import annotations
import time, json, pathlib
import pandas as pd
import requests

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"
ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
CACHE = DATA / "_weather_cache.json"
KICKOFF_WINDOW = range(14, 22)  # 14:00-21:00 local


def _cache() -> dict:
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def _fetch_one(lat: float, lon: float, date: str) -> dict:
    r = requests.get(ARCHIVE, params={
        "latitude": lat, "longitude": lon,
        "start_date": date, "end_date": date,
        "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature",
        "timezone": "auto",
    }, timeout=30)
    r.raise_for_status()
    h = r.json().get("hourly", {})
    if not h.get("time"):
        return {}
    rows = list(zip(h["time"], h["temperature_2m"],
                    h["relative_humidity_2m"], h["apparent_temperature"]))
    win = [x for x in rows if int(x[0][11:13]) in KICKOFF_WINDOW] or rows
    temps = [x[1] for x in win if x[1] is not None]
    hums = [x[2] for x in win if x[2] is not None]
    app = [x[3] for x in win if x[3] is not None]
    return {
        "temp_c": round(sum(temps) / len(temps), 1) if temps else None,
        "temp_max_c": round(max(temps), 1) if temps else None,
        "humidity_pct": round(sum(hums) / len(hums)) if hums else None,
        "feels_c": round(max(app), 1) if app else None,
    }


def enrich(df: pd.DataFrame, polite: float = 0.3) -> pd.DataFrame:
    cache = _cache()
    out = []
    for i, row in df.iterrows():
        date = pd.to_datetime(row["date"]).strftime("%Y-%m-%d")
        if int(date[:4]) < 1940:
            out.append({}); continue
        key = f"{row['lat']:.2f},{row['lon']:.2f},{date}"
        if key not in cache:
            try:
                cache[key] = _fetch_one(row["lat"], row["lon"], date)
            except Exception as e:
                print(f"  fail {key}: {e}"); cache[key] = {}
            time.sleep(polite)
            if i % 25 == 0:
                CACHE.write_text(json.dumps(cache))
                print(f"  {i}/{len(df)} fetched")
        out.append(cache[key])
    CACHE.write_text(json.dumps(cache))
    return pd.concat([df.reset_index(drop=True), pd.DataFrame(out)], axis=1)


if __name__ == "__main__":
    wc = pd.read_csv(DATA / "wc_matches.csv", parse_dates=["date"])
    wc = enrich(wc)
    wc.to_csv(DATA / "wc_matches_weather.csv", index=False)
    got = wc["temp_c"].notna().mean()
    print(f"Weather attached to {got:.0%} of matches "
          f"-> data/wc_matches_weather.csv")
