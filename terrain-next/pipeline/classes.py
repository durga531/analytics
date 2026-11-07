import json, os, numpy as np, pandas as pd
OUT = os.environ.get("NEXT_OUT", "../site/data/next")
os.makedirs(f"{OUT}/pin_class", exist_ok=True)
df = pd.read_parquet("pins_scored.parquet"); X = pd.read_parquet("X.parquet")
met = json.load(open("model_metrics.json"))
CUTS = {"A": 0.6, "B": 0.3, "C": 0.1}
p = df.p_oof.values
df["cls"] = np.where(p >= CUTS["A"], "A", np.where(p >= CUTS["B"], "B", np.where(p >= CUTS["C"], "C", "D")))
df["score"] = np.round(p * 100).astype(int)
GAP_KM = 3.0
km = np.fmin(df.km_to_lfr_popwt.astype(float).fillna(999), df.km_to_electronics_chain_popwt.astype(float).fillna(999))
df["km_near"] = km
df["svc"] = np.where(df.y == 1, 2, np.where(km <= GAP_KM, 1, 0))  # 2 in PIN, 1 within 3 km, 0 gap
# national percentile of each explanatory feature, for "what stands out"
WHY = {"log_bfsi": "banks and finance outlets", "log_places_total": "commercial places", "built_height": "taller buildings",
       "built_m2_per_hh": "built space per household", "log_ookla_mobile_tests": "mobile data activity", "rwi_mean": "relative wealth",
       "secc_salary_share": "salaried households", "log_apparel": "apparel and jewellery shops", "log_density": "population density",
       "log_affluent_hh": "upper-wealth households", "log_hospitality": "hotels and restaurants", "log_transit": "transit stops",
       "ookla_fixed_per_1000hh": "home broadband", "log_nl_2023": "night-time activity", "top_band_share": "share in the top wealth band"}
pct = X[list(WHY)].rank(pct=True)
codes = list(WHY)
def why_row(i):
    r = pct.iloc[i]
    top = r.sort_values(ascending=False).head(3)
    return [[codes.index(k), int(round(v * 100))] for k, v in top.items() if not np.isnan(v)]
whys = [why_row(i) for i in range(len(df))]
df["why"] = whys
# per-state compact files
for s, g in df.groupby("slug"):
    out = {r.pin: [r.cls, int(r.score), int(r.svc), int(r.organised), (None if r.km_near >= 999 else round(float(r.km_near), 1)), r.why] for r in g.itertuples()}
    json.dump(out, open(f"{OUT}/pin_class/{s}.json", "w"), separators=(",", ":"))
# district roll-up keyed by soi_district_objectid
df["did"] = df.soi_district_objectid.astype("Int64").astype(str)
def roll(g):
    a = g[g.cls == "A"]; b = g[g.cls == "B"]
    ua = a[a.svc == 0]; ub = b[b.svc == 0]
    return pd.Series({"a": len(a), "b": len(b), "c": int((g.cls == "C").sum()), "d": int((g.cls == "D").sum()),
                      "ua": len(ua), "ub": len(ub),
                      "ua_aff": float(ua.affluent_hh.sum()), "uab_aff": float(ua.affluent_hh.sum() + ub.affluent_hh.sum()),
                      "a_aff": float(a.affluent_hh.sum()), "aff": float(g.affluent_hh.sum())})
dist = df.groupby("did").apply(roll)
dist["a_share_aff"] = (dist.a_aff / dist.aff.replace(0, np.nan)).round(3)
json.dump({k: {c: (None if pd.isna(v) else (round(v) if isinstance(v, float) and c.endswith("aff") else v)) for c, v in row.items()} for k, row in dist.iterrows()},
          open(f"{OUT}/district_class.json", "w"), separators=(",", ":"))
# class summary
g = df.groupby("cls")
summ = {c: {"pins": int(len(x)), "hh": float(x.hh2020_est.sum()), "aff": float(x.affluent_hh.sum()), "served_rate": float(x.y.mean()),
            "stores": float(x.organised.sum()), "nearby_rate": float((x.svc == 1).mean()), "gap": int((x.svc == 0).sum()), "gap_aff": float(x[x.svc == 0].affluent_hh.sum())} for c, x in g}
meta = {"cuts": CUTS, "auc": met["auc"], "ap": met["ap"], "base_rate": met["base"], "pins": len(df), "why_codes": [WHY[k] for k in codes],
        "summary": summ, "aff_total": float(df.affluent_hh.sum()),
        "formats": {"A": "Flagship and large formats: premium supermarket, category flagship, mall anchor",
                    "B": "Standard formats: supermarket or specialty store",
                    "C": "Compact formats: small store, franchise, shop-in-shop, or quick commerce first",
                    "D": "Distribution before stores: wholesale, kirana and rural partners"},
        "target": "PIN has at least one listed modern-trade (MT or RSS) store or one of 12 tracked chain stores",
        "method": "Gradient-boosted classifier on 29 open-data features (households, wealth, built form, night lights, mobile and broadband activity, commercial places, transit, census salary share). Each PIN is scored by a model trained on the other states (6-fold, grouped by state), so no PIN is scored by a model that saw its own state. Classes cut the score at 0.60, 0.30 and 0.10.",
        "label": "model", "gap_km": GAP_KM, "service": ["gap: no organised store within 3 km (population-weighted)", "served nearby: a store within 3 km", "store in this PIN"]}
json.dump(meta, open(f"{OUT}/class_meta.json", "w"), indent=1)
# top unserved Class A nationally
ua = df[(df.cls == "A") & (df.svc == 0)].sort_values("affluent_hh", ascending=False)
print("Top unserved Class A PINs:\n", ua[["pin", "office_name", "district_name", "state_name", "score", "affluent_hh", "hh2020_est"]].head(15).to_string(index=False))
print("\nDelhi classes:", df[df.slug == "delhi"].groupby("cls").agg(pins=("pin", "size"), served=("y", "mean")).round(2).to_dict())
print("files:", len(os.listdir(f"{OUT}/pin_class")), "size MB:", round(sum(os.path.getsize(f"{OUT}/pin_class/{f}") for f in os.listdir(f"{OUT}/pin_class")) / 1e6, 2))

# national list of gap PINs in Class A and B, with names, for the shortlist and CSV export
gap = df[df.cls.isin(["A", "B"]) & (df.svc == 0)].sort_values(["cls", "affluent_hh"], ascending=[True, False])
rows = [[r.pin, r.office_name, r.district_name, r.state_name, r.slug, str(r.did), r.cls, int(r.score), round(float(r.affluent_hh or 0)),
         round(float(r.hh2020_est or 0)), (None if r.km_near >= 999 else round(float(r.km_near), 1))] for r in gap.itertuples()]
json.dump({"cols": ["pin", "office", "district", "state", "slug", "did", "cls", "score", "aff_hh", "hh", "km_nearest_store"], "rows": rows},
          open(f"{OUT}/class_gaps.json", "w"), separators=(",", ":"))
print("gap list rows:", len(rows))
