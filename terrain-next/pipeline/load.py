import json, os, glob
import numpy as np, pandas as pd
D = os.environ.get("TERRAIN_DATA", "/tmp/claude-0/-home-user-analytics/84cc0345-6edb-5ddf-94dc-f3c5bff7e35b/scratchpad/terrain-site/data")
def load_pins():
    states = list(json.load(open(f"{D}/pins/index.json")).keys())
    rows = []
    for s in states:
        a = json.load(open(f"{D}/pins/{s}.attr.json"))
        t = json.load(open(f"{D}/terrain/pin/{s}.json")) if os.path.exists(f"{D}/terrain/pin/{s}.json") else {}
        for pin, v in a.items():
            r = {**t.get(pin, {}), **v, "pin": pin, "slug": s}
            rows.append({k: x for k, x in r.items() if isinstance(x, (int, float, str)) or x is None})
    return pd.DataFrame(rows)
if __name__ == "__main__":
    df = load_pins()
    print(df.shape)
    print("PINs with >=1 listed store:", int((df.lfr_stores.fillna(0) >= 1).sum()), "stores total:", df.lfr_stores.fillna(0).sum())
    print("any_chain_stores>0:", int((df.get('any_chain_stores', pd.Series(0)).fillna(0) > 0).sum()))
    store_cols = [c for c in df.columns if c.startswith("store_")]
    print("chain columns:", store_cols)
    print(df[["lfr_stores","lfr_mt_stores","lfr_rss_stores","electronics_chain_stores","qc_dark_stores_mar2026"]].fillna(0).sum())
    print("missing share key fields:", df[["hh2020_est","affluent_hh","rwi_mean","built_s_2020_km2","nl_2023","pl_total"]].isna().mean().round(3).to_dict())
    df.to_parquet("pins.parquet")
