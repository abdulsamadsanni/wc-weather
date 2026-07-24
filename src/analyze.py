"""Step 4 - test whether temperature affects scoring, naive vs controlled.

A raw correlation of goals against temperature is confounded by era (scoring
fell for decades for tactical reasons), by which countries host, and by
altitude. This prints the naive estimate, then the estimate with era and host
fixed effects added, so the two can be compared directly. On the current data
neither is statistically significant, which is the reported result.
"""
from __future__ import annotations
import pathlib
import pandas as pd
import statsmodels.formula.api as smf

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"
FILE = DATA / "wc_matches_weather.csv"


def load() -> pd.DataFrame:
    if not FILE.exists():
        raise SystemExit("Run weather.py first to produce " + str(FILE))
    df = pd.read_csv(FILE, parse_dates=["date"])
    df = df.dropna(subset=["temp_c", "goals"]).copy()
    df["decade"] = (df["year"] // 10 * 10).astype(str)
    df["abslat"] = df["lat"].abs()
    return df


def main() -> None:
    df = load()
    print(f"Sample: {len(df)} matches with weather, "
          f"{df['year'].min()}-{df['year'].max()}\n")

    naive = smf.ols("goals ~ temp_c", data=df).fit()
    print("NAIVE  goals ~ temperature")
    print(f"  temp coef = {naive.params['temp_c']:+.4f} goals/degC "
          f"(p={naive.pvalues['temp_c']:.3f})\n")

    ctrl = smf.ols("goals ~ temp_c + humidity_pct + abslat + C(decade) "
                   "+ C(country)", data=df).fit()
    print("CONTROLLED  + decade + host + humidity + latitude")
    print(f"  temp coef = {ctrl.params['temp_c']:+.4f} goals/degC "
          f"(p={ctrl.pvalues['temp_c']:.3f})")
    print(f"  R^2 {naive.rsquared:.3f} -> {ctrl.rsquared:.3f}\n")

    shift = naive.params["temp_c"] - ctrl.params["temp_c"]
    print(f"Confounding moved the temperature effect by {shift:+.4f} "
          f"goals/degC once era and host are held constant.")
    print("That movement - not the raw number - is the result.\n")

    # compact summary block, mirrored in FINDINGS.md
    print("--- copy into FINDINGS.md ---")
    print(f"- Sample:        {len(df)} matches with weather")
    print(f"- Naive effect:  {naive.params['temp_c']:+.4f} goals per degC "
          f"(p = {naive.pvalues['temp_c']:.3f})")
    print(f"- Controlled:    {ctrl.params['temp_c']:+.4f} goals per degC "
          f"(p = {ctrl.pvalues['temp_c']:.3f})   (+ era, host, humidity, latitude)")
    print(f"- Confounding shifted the effect by {shift:+.4f} goals per degC")


if __name__ == "__main__":
    main()
