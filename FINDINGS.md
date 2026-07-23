# Findings

A plain-language summary of what this project found across every World Cup match
from 1930 to 2026 (1,068 matches with results, geocoded to 179 host cities).
Data snapshot: mid-2026, while the 2026 tournament is still in progress, so the
totals grow as more matches are played.

## The question

It is widely assumed that heat slows football: players tire, the game opens up
or shuts down, scorelines change. This project tests that assumption honestly,
separating a real climate effect from things that only look like one.

## Headline

**Scoring at the World Cup is driven by era, not weather.** The intuitive
"hot-weather football" story fails twice: geography shows no effect, and the real
per-match temperature shows no effect either, before or after controlling for
the era in which a match was played.

## 1. Era dominates

Goals per match have swung enormously over time for tactical reasons that have
nothing to do with weather:

| Tournament | Goals / match |
|---|---|
| 1954 (Switzerland) | 5.38 (peak) |
| 1990 (Italy) | 2.21 (trough) |
| Modern era (2010-2022) | ~2.57 |

That is a **59% decline** from peak to trough. Decade alone explains about 8.5%
of the match-to-match variance in goals, which is large for a single factor in
noisy sports data.

## 2. Geography shows no signal

Using how far a match is played from the equator as a crude climate proxy:

- Raw association with goals: **+0.004 goals per degree of latitude, p = 0.36**
  (not significant).
- After controlling for era: still not significant (p = 0.53).
- Era explains roughly **106 times more** of the variance in goals than latitude.

So geography, on its own, carries no detectable scoring signal.

## 3. Temperature shows no signal either

Latitude is only a proxy. The real test uses the actual per-match temperature
from the Open-Meteo weather join, on the 1,014 matches from 1950 onward that have
weather data:

```
Sample:        1,014 matches with weather
Naive effect:  +0.003 goals per degC (p = 0.77)
Controlled:    +0.023 goals per degC (p = 0.19)   (+ era, host, humidity, latitude)
Confounding shifted the effect by -0.020 goals per degC
```

**Reading this:** the naive effect is essentially zero and not significant
(p = 0.77). Controlling for era, host, humidity and latitude nudges the estimate
up slightly, but it is still not significant (p = 0.19), so there is **no
detectable effect of temperature on goals in either direction.** If anything the
controlled coefficient leans faintly positive, the opposite of the "heat slows
the game" intuition, but the p-value forbids reading anything into that.

The point is the process, not a headline number: the naive-to-controlled shift
shows that era does move the estimate, it just never moves it far enough to
matter. A clean null from a rigorous test is a legitimate, defensible result.

## Limitations

- **Goals is a coarse outcome.** Heat likely affects distance covered, sprint
  counts and second-half fade long before it changes the scoreline. Detecting
  that needs event-level data (StatsBomb / Opta), which is the natural next step.
- The weather archive starts in 1940, so the 1930-1938 tournaments are excluded
  from the temperature model rather than estimated.
- Per-match weather is summarised over an afternoon-to-evening kickoff window,
  not the exact kickoff time, which the base dataset does not record.

## What this project demonstrates

A reproducible pipeline from raw data to result; offline geocoding to full
coverage; a real weather API integrated two ways (a cached batch pipeline and a
live in-browser join in the visualization); leakage-aware joins; confounder
control with fixed-effects regression; and a front end that states its own
limits instead of overselling a finding.
