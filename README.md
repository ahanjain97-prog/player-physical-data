# Player Physical Data

A single-page site for browsing tracking data across MLS NEXT Pro, USL Championship and
USL League One, 2024–2026. Search a player, get a physical capability card: every metric
percentile-ranked against players in the **same league, same season, same position group**.

**Live:** https://ahanjain97-prog.github.io/player-physical-data/

## What's in it

2,079 player-seasons with a complete physical block, drawn from seven Wyscout exports.

| League | 2024 | 2025 | 2026 |
|---|---:|---:|---:|
| MLS NEXT Pro | 116 | 358 | 383 |
| USL Championship | — | 431 | 380 |
| USL League One | — | 172 | 239 |

Rows without a complete set of fourteen physical metrics are dropped rather than ranked on
gaps. Position groups are CB, FB, MID (DM/CM/AM) and FWD (W/CF), plus GK.

## Why percentiles, and only within a league-season

Tracking baselines move between seasons by more than players do. Measured on the same
players, same league, 2025 → 2026:

- **Max Speed** median rose ~1.2 km/h in all three leagues simultaneously — a measurement
  change, not a fitness change.
- **High Acceleration Count** median in USL Championship went 28.8 → 39.4 (+37%).
- MLS NEXT Pro 2024 → 2025 acceleration counts jumped ~64%.

So a raw 2025 number cannot be read against a raw 2026 number. Percentiles inside one
league-season-position pool are the only stable unit.

## How reliable is any of it

Two different questions, measured separately.

**Repeatability** — year-over-year correlation for the same player, **compared within his own
position group** (n = 367 repeat players). **Team share** — the variance inside a
league-season-position pool explained by which club he plays for, corrected against a
permuted-label baseline (raw eta² sits near 29% on noise alone at these pool sizes).

| Metric | r | Team share | Reads as |
|---|---:|---:|---|
| Sprint Count Per 90 | 0.49 | 12% | player capability |
| Sprinting Distance Per 90 | 0.45 | 12% | player capability |
| HSR Count Per 90 | 0.40 | 14% | player capability |
| Running Distance Per 90 | 0.42 | 16% | mixed |
| High Intensity Count Per 90 | 0.45 | 17% | mixed |
| HSR Distance Per 90 | 0.41 | 17% | mixed |
| High Intensity Distance Per 90 | 0.43 | 18% | mixed |
| High Deceleration Count Per 90 | 0.44 | 21% | team / role |
| Meters Per Minute | 0.42 | 22% | team / role |
| Distance Per 90 | 0.42 | 23% | team / role |
| Medium Acceleration Count Per 90 | 0.43 | 24% | team / role |
| Medium Deceleration Count Per 90 | 0.46 | 26% | team / role |
| High Acceleration Count Per 90 | 0.50 | 28% | team / role |
| **Max Speed** | **0.25** | 17% | **unreliable** |

Sprint count and sprint distance are the closest thing here to a measure of the athlete:
they repeat as well as anything and are least explained by the club. Distance per 90 and
meters per minute are reliable but describe the job more than the player. High acceleration
count repeats best of all yet is the most club-explained figure on the card — it reads as
team tempo.

A caution worth repeating: pooled across all positions, Distance Per 90 correlates at 0.86
year-over-year, which looks excellent. Almost all of that is position — centre backs stay
centre backs. Compare like-for-like within a position group and it falls to 0.42.

## Rebuilding after new exports

```
pip install openpyxl
# drop the xlsx files into ./exports using the names in build/build_data.py
python build/build_data.py
```

That regenerates `site_data.json` and rewrites `index.html` from `index_tpl.html`.
Edit `index_tpl.html`, never `index.html` — the latter is generated and holds the inlined data.

## Layout

```
index.html         generated, self-contained, deployed by Pages
index_tpl.html     the page source, with a __DATA__ placeholder
site_data.json     generated dataset (also inlined into index.html)
build/build_data.py  reads the xlsx exports, computes percentiles
exports/           source xlsx files (git-ignored)
```

Source data is Wyscout. The exports are not committed.
