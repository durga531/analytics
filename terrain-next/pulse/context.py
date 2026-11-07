#!/usr/bin/env python3
"""Brand Pulse, local context. Writes the few district fields the Pulse view maps, so the page
does not load TERRAIN's 5 MB district file. Standard library only.

usage: python3 context.py TERRAIN_DATA/terrain/districts.json OUT/context.json
"""
import json, sys

FIELDS = [  # key, TERRAIN field, label, unit
    ("hh", "hh2020_est", "Households", "count"),
    ("aff", "affluent_hh", "Upper-wealth households", "count"),
    ("v2w", "vahan_2w_per_1000_hh", "Two-wheeler registrations per 1,000 households, last 12 months", "rate"),
    ("v2wy", "vahan_2w_yoy", "Two-wheeler registrations, change on a year earlier", "share"),
    ("ev", "vahan_ev_share_ttm", "Electric share of two-wheeler registrations, last 12 months", "share"),
    ("bld", "built_add_m2_per_hh", "New built-up area per household, 2015 to 2020, m²", "rate"),
    ("rera", "rera_residential_per_lakh_hh", "Registered housing projects per lakh households", "rate"),
    ("pmo", "clim_paint_window_months", "Months a year dry and mild enough to paint outside", "months"),
    ("qc", "qc_dark_stores_mar2026", "Quick-commerce dark stores, March 2026", "count"),
    ("qcp", "qc_platforms", "Quick-commerce platforms present", "count"),
]

def main(src, out):
    d = json.load(open(src))
    rows = {}
    for k, v in d.items():
        r = []
        for _, f, _, _ in FIELDS:
            x = v.get(f)
            r.append(None if not isinstance(x, (int, float)) else round(x, 4 if abs(x) < 10 else 1))
        rows[k] = r
    json.dump({"fields": [[a, c, u] for a, _, c, u in FIELDS], "source": {a: f for a, f, _, _ in FIELDS}, "d": rows},
              open(out, "w"), ensure_ascii=False, separators=(",", ":"))
    # the white space quick commerce leaves: upper-wealth homes in districts with no dark store
    ix = [a for a, *_ in FIELDS]
    un = sorted(((v.get("affluent_hh") or 0, v.get("district") or k, v.get("state") or "") for k, v in d.items()
                 if not v.get("qc_dark_stores_mar2026")), reverse=True)[:8]
    print("largest upper-wealth districts with no dark store:", [(n, s, round(a)) for a, n, s in un])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
