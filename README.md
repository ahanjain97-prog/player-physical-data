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

Year-over-year correlation for the same player, **compared within his own position group**
(n = 290 repeat players):

| Metric | r |
|---|---:|
| Distance Per 90 / Meters Per Minute | 0.43 |
| High Intensity / HSR distance & counts | 0.47 – 0.56 |
| Sprint distance & count | 0.47 – 0.57 |
| High Acceleration Count | 0.57 |
| **Max Speed** | **0.22** |

A caution worth repeating: pooled across all positions, Distance Per 90 correlates at 0.86
year-over-year, which looks excellent. Almost all of that is position — centre backs stay
centre backs. Compare like-for-like within a position group and it falls to 0.43. The
metrics flagged with △ on the card are the least reproducible.

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
