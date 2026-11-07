import json, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score
df = pd.read_parquet("pins.parquet")
f0 = lambda c: df[c].astype(float).fillna(0) if c in df else pd.Series(0.0, index=df.index)
df["organised"] = f0("lfr_stores") + f0("any_chain_stores")
df["y"] = (df["organised"] >= 1).astype(int)
hh = f0("hh2020_est").clip(lower=1)
lg = lambda s: np.log1p(s.clip(lower=0))
X = pd.DataFrame({
  "log_hh": lg(f0("hh2020_est")), "log_affluent_hh": lg(f0("affluent_hh")), "log_upper_hh": lg(f0("upper_hh")),
  "affluent_share": f0("affluent_share"), "rwi_mean": df["rwi_mean"].astype(float),
  "log_density": lg(f0("pop_density")), "log_area": lg(f0("area_sqkm")),
  "log_built_km2": lg(f0("built_s_2020_km2")), "built_share": f0("built_share_of_area"), "built_height": df.get("built_height_m").astype(float) if "built_height_m" in df else 0,
  "built_m2_per_hh": f0("built_m2_per_hh"), "built_growth": df["built_growth_2015_20"].astype(float) if "built_growth_2015_20" in df else 0,
  "log_nl_2023": lg(f0("nl_2023")), "nl_growth": df["nl_growth_2019_2023"].astype(float),
  "ookla_fixed_per_1000hh": f0("ookla_fixed_devices_per_1000_hh"), "log_ookla_mobile_tests": lg(f0("ookla_mobile_tests")),
  "log_places_total": lg(f0("pl_total")), "places_per_lakh_hh": f0("pl_total_per_lakh_hh"),
  "log_apparel": lg(f0("pl_apparel_jewellery")), "log_grocery": lg(f0("pl_grocery_fmcg")), "log_hospitality": lg(f0("pl_hospitality")),
  "log_bfsi": lg(f0("pl_bfsi")), "log_health": lg(f0("pl_health")), "log_leisure": lg(f0("pl_leisure_personal")),
  "log_transit": lg(f0("pt_transit")), "log_stays": lg(f0("pt_stays")),
  "top_band_share": f0("ladder_q5_share"), "log_ec13_emp": lg(f0("ec13_emp_all")),
  "secc_salary_share": df["secc_rural_salary_any_share"].astype(float) if "secc_rural_salary_any_share" in df else np.nan,
})
groups = df["slug"].values
oof = np.zeros(len(df)); gkf = GroupKFold(n_splits=6)
params = dict(max_iter=400, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=40, l2_regularization=1.0, random_state=7)
for tr, te in gkf.split(X, df.y, groups):
    m = HistGradientBoostingClassifier(**params).fit(X.iloc[tr], df.y.iloc[tr])
    oof[te] = m.predict_proba(X.iloc[te])[:, 1]
auc = roc_auc_score(df.y, oof); ap = average_precision_score(df.y, oof)
print(f"spatial CV (held-out states): AUC {auc:.3f}, average precision {ap:.3f}, base rate {df.y.mean():.3f}")
# baseline: affluent households only
from sklearn.metrics import roc_auc_score as A
print("baseline AUC, affluent_hh only:", round(A(df.y, X.log_affluent_hh), 3), "; households only:", round(A(df.y, X.log_hh), 3))
full = HistGradientBoostingClassifier(**params).fit(X, df.y)
df["p_oof"] = oof
# permutation importance on a sample
from sklearn.inspection import permutation_importance
idx = np.random.RandomState(1).choice(len(df), 6000, replace=False)
pi = permutation_importance(full, X.iloc[idx], df.y.iloc[idx], n_repeats=3, random_state=1, scoring="roc_auc")
imp = sorted(zip(X.columns, pi.importances_mean), key=lambda t: -t[1])[:10]
print("top drivers:", [(n, round(v, 3)) for n, v in imp])
df["p_full"] = full.predict_proba(X)[:, 1]
X.to_parquet("X.parquet"); df.to_parquet("pins_scored.parquet")
json.dump({"auc": auc, "ap": ap, "base": df.y.mean(), "drivers": [(n, float(v)) for n, v in imp]}, open("model_metrics.json", "w"))
