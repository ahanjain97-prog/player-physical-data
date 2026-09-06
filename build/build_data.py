"""
Build the site dataset from Wyscout xlsx exports.

Usage:
    python build/build_data.py path/to/exports   # folder holding the xlsx files
    python build/build_data.py                   # defaults to ./exports

Each export must be a Wyscout "Search results" xlsx containing the physical
columns (Total Distance per 90 ... Count HI per 90). Name the files by league
and season so SOURCES below can pick them up.

Writes site_data.json, then inlines it into index.html via index_tpl.html.
"""
import json
import os
import sys
import collections

import openpyxl

# filename -> (league, season)
SOURCES = [
    ("mlsnp 24.xlsx", "MLS NEXT Pro", "2024"),
    ("mlsnp 25.xlsx", "MLS NEXT Pro", "2025"),
    ("mlsnp 26.xlsx", "MLS NEXT Pro", "2026"),
    ("usl c 25.xlsx", "USL Championship", "2025"),
    ("usl c 26.xlsx", "USL Championship", "2026"),
    ("usl l1 25.xlsx", "USL League One", "2025"),
    ("usl l1 26.xlsx", "USL League One", "2026"),
]

A2 = "²"

# (display group, display label, Wyscout column)
METRICS = [
    ("Volume", "Distance Per 90", "Total Distance per 90"),
    ("Volume", "Running Distance Per 90 (15-20)", "Running Distance per 90 (15-20 km/h)"),
    ("Volume", "Meters Per Minute", "Meter/Min"),
    ("Repeated Efforts", "High Intensity Distance Per 90", "HI Distance per 90 (+20 km/h)"),
    ("Repeated Efforts", "HSR Distance Per 90 (20-25)", "HSR Distance per 90 (20-25 km/h)"),
    ("Repeated Efforts", "Sprinting Distance Per 90 (+25)", "Sprinting Distance per 90 (+25 km/h)"),
    ("Repeated Efforts", "High Intensity Count Per 90", "Count HI per 90 (+20 km/h)"),
    ("Repeated Efforts", "HSR Count Per 90", "Count HSR per 90 (20-25 km/h)"),
    ("Repeated Efforts", "Sprint Count Per 90", "Count Sprint per 90 (+25 km/h)"),
    ("Top Speed", "Max Speed (km/h)", "Max Speed (km/h)"),
    ("Accel / Decel", "High Acceleration Count Per 90",
     "Count High Acceleration per 90 (+3 m/s" + A2 + ")"),
    ("Accel / Decel", "Medium Acceleration Count Per 90",
     "Count Medium Acceleration per 90 (1.5 m/s" + A2 + " to 3 m/s" + A2 + ")"),
    ("Accel / Decel", "High Deceleration Count Per 90",
     "Count High Deceleration per 90 (-3 m/s" + A2 + ")"),
    ("Accel / Decel", "Medium Deceleration Count Per 90",
     "Count Medium Deceleration per 90 (-1.5 m/s" + A2 + " to -3 m/s" + A2 + ")"),
]

# Wyscout primary position code -> general position group
POSITION_GROUP = {
    "GK": "GK",
    "CB": "CB", "LCB": "CB", "RCB": "CB",
    "LB": "FB", "RB": "FB", "LWB": "FB", "RWB": "FB",
    "DMF": "MID", "LDMF": "MID", "RDMF": "MID", "LCMF": "MID", "RCMF": "MID",
    "AMF": "MID", "LAMF": "MID", "RAMF": "MID",
    "LW": "FWD", "RW": "FWD", "LWF": "FWD", "RWF": "FWD", "CF": "FWD",
}
GROUP_ORDER = ["CB", "FB", "MID", "FWD", "GK"]
GROUP_NAMES = {"CB": "Centre Backs", "FB": "Full Backs", "MID": "Midfielders",
               "FWD": "Forwards", "GK": "Goalkeepers"}


def num(v):
    """Float or None. Wyscout writes blanks as '' and numbers as strings."""
    try:
        f = float(v)
        return f if f == f else None
    except (TypeError, ValueError):
        return None


def load(folder):
    """Read every source workbook, keeping only rows with a complete physical block."""
    records = []
    for filename, league, season in SOURCES:
        path = os.path.join(folder, filename)
        if not os.path.exists(path):
            print("  missing, skipped: %s" % filename)
            continue
        sheet = openpyxl.load_workbook(path, data_only=True).active
        rows = list(sheet.iter_rows(values_only=True))
        header = [str(h) for h in rows[0]]
        col = {}
        for j, h in enumerate(header):
            col.setdefault(h, j)  # first occurrence: the GK duplicate columns are ignored

        kept = 0
        for row in rows[1:]:
            values = {label: num(row[col[src]]) for _, label, src in METRICS}
            if any(v is None for v in values.values()):
                continue  # partial tracking coverage: drop rather than rank on gaps
            primary = str(row[col["Position"]] or "").split(",")[0].strip()
            if primary not in POSITION_GROUP:
                continue
            age = num(row[col["Age"]])
            records.append({
                "name": str(row[col["Player"]] or "").strip(),
                # team during the season, not the player's club today
                "team": str(row[col["Team within selected timeframe"]] or row[col["Team"]] or "").strip(),
                "league": league,
                "season": season,
                "pos": str(row[col["Position"]] or "").strip(),
                "grp": POSITION_GROUP[primary],
                "age": int(age) if age else None,
                "mins": int(num(row[col["Minutes played"]]) or 0),
                "mp": int(num(row[col["Matches played"]]) or 0),
                "metrics": values,
            })
            kept += 1
        print("  %-16s %s %s  ->  %d rows with full tracking data" % (filename, league, season, kept))
    return records


def add_percentiles(records):
    """Percentile-rank each metric inside its own league + season + position pool."""
    labels = [label for _, label, _ in METRICS]
    pools = collections.defaultdict(list)
    for r in records:
        pools[(r["league"], r["season"], r["grp"])].append(r)

    for members in pools.values():
        n = len(members)
        for label in labels:
            ordered = sorted(m["metrics"][label] for m in members)
            for m in members:
                v = m["metrics"][label]
                below = sum(1 for x in ordered if x < v)
                equal = sum(1 for x in ordered if x == v)
                m.setdefault("pct", {})[label] = round(100 * (below + 0.5 * equal) / n)
        for m in members:
            m["pool"] = n
    return pools


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "exports"
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isabs(folder):
        folder = os.path.join(here, folder)

    print("reading exports from %s" % folder)
    records = load(folder)
    if not records:
        sys.exit("no rows loaded - check the export folder and SOURCES filenames")
    pools = add_percentiles(records)

    print("\npool depth (league x season x position group)")
    print("%-24s%s" % ("", "".join("%7s" % g for g in GROUP_ORDER)))
    for league in ["MLS NEXT Pro", "USL Championship", "USL League One"]:
        for season in ["2024", "2025", "2026"]:
            if not any(k[0] == league and k[1] == season for k in pools):
                continue
            counts = "".join("%7d" % len(pools.get((league, season, g), [])) for g in GROUP_ORDER)
            print("%-24s%s" % (league + " " + season, counts))

    leagues = ["MLS NEXT Pro", "USL Championship", "USL League One"]
    seasons = ["2024", "2025", "2026"]
    labels = [label for _, label, _ in METRICS]

    rows = []
    for r in sorted(records, key=lambda x: (x["name"], x["season"])):
        rows.append([
            r["name"], r["team"], leagues.index(r["league"]), seasons.index(r["season"]),
            r["pos"], GROUP_ORDER.index(r["grp"]), r["age"], r["mins"], r["mp"], r["pool"],
            [round(r["metrics"][l], 1) for l in labels],
            [r["pct"][l] for l in labels],
        ])

    payload = {
        "leagues": leagues,
        "seasons": seasons,
        "groups": [{"k": g, "n": GROUP_NAMES[g]} for g in GROUP_ORDER],
        "metrics": [{"g": g, "l": l} for g, l, _ in METRICS],
        "fields": ["name", "team", "lg", "sn", "pos", "grp", "age", "mins", "mp", "pool", "raw", "pct"],
        "rows": rows,
    }
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    data_path = os.path.join(here, "site_data.json")
    with open(data_path, "w", encoding="utf-8") as fh:
        fh.write(blob)

    template = os.path.join(here, "index_tpl.html")
    with open(template, encoding="utf-8") as fh:
        html = fh.read()
    if "__DATA__" not in html:
        sys.exit("index_tpl.html has no __DATA__ placeholder")
    if "</script>" in blob:
        sys.exit("data contains </script> - would break the inline block")
    with open(os.path.join(here, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html.replace("__DATA__", blob))

    print("\n%d player-seasons -> index.html (%.0f KB)"
          % (len(rows), os.path.getsize(os.path.join(here, "index.html")) / 1024))


if __name__ == "__main__":
    main()
