"""Step 5 - regenerate the data embedded in viz/index.html.

Re-run after weather.py so the hosted visualization can show pipeline-baked
temperatures instantly (the viz also fetches weather live on hover, so this is
optional). Injects matches, the era arc, and the verified-conditions dict.
"""
from __future__ import annotations
import json, pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
WEATHER = ROOT / "data/wc_matches_weather.csv"
PLAIN = ROOT / "data/wc_matches.csv"
TEMPLATE = ROOT / "viz/index_template.html"
OUT = ROOT / "viz/index.html"

# documented extreme-heat matches, cross-checked against contemporary reporting
VERIFIED = {
    "2014-06-22|United States|Portugal": {
        "temp": "30-32\u00b0C (86-90\u00b0F)", "humidity": "66-70%",
        "note": "Manaus, in the Amazon. Triggered the first-ever World Cup "
                "cooling break (39'). Portugal visibly wilted; USA drew 2-2."},
    "2014-06-29|Netherlands|Mexico": {
        "temp": "32\u00b0C (90\u00b0F)", "humidity": "68%",
        "note": "Fortaleza. First cooling break in a World Cup knockout match "
                "(32'). Netherlands came from behind to win 2-1."},
    "2022-11-20|Qatar|Ecuador": {
        "temp": "~21\u00b0C on pitch (\u224830\u00b0C+ outside)", "humidity": "controlled",
        "note": "The whole tournament was moved to November to dodge Qatar's "
                "40\u00b0C+ summer; stadiums were air-conditioned to ~21\u00b0C."},
}


def main() -> None:
    src = WEATHER if WEATHER.exists() else PLAIN
    df = pd.read_csv(src, parse_dates=["date"]).dropna(subset=["goals"])
    recs = []
    for _, r in df.iterrows():
        rec = {"y": int(r["year"]), "d": r["date"].strftime("%Y-%m-%d"),
               "h": r["home_team"], "a": r["away_team"],
               "hs": int(r["home_score"]), "as": int(r["away_score"]),
               "g": int(r["goals"]), "c": r["city"], "co": r["country"],
               "lat": round(float(r["lat"]), 2), "lon": round(float(r["lon"]), 2),
               "n": bool(r["neutral"])}
        if "temp_c" in df.columns and pd.notna(r.get("temp_c")):
            rec["t"] = float(r["temp_c"])
            if pd.notna(r.get("humidity_pct")):
                rec["hu"] = int(r["humidity_pct"])
        recs.append(rec)
    era = df.groupby("year")["goals"].mean().round(3).to_dict()
    html = TEMPLATE.read_text()
    html = html.replace("/*__DATA__*/[]", json.dumps(recs, separators=(",", ":")))
    html = html.replace("/*__ERA__*/{}",
                        json.dumps({str(k): v for k, v in era.items()},
                                   separators=(",", ":")))
    html = html.replace("/*__VERIFIED__*/{}",
                        json.dumps(VERIFIED, separators=(",", ":")))
    OUT.write_text(html)
    print(f"Wrote {OUT} with {len(recs)} matches "
          f"({'with baked temps' if src is WEATHER else 'live-fetch weather'})")


if __name__ == "__main__":
    main()
