# TERRAIN Next

TERRAIN Next is an add-on build of TERRAIN. It adds four things to the published app without changing its stories or data:

1. **Store classes.** Every PIN code is graded A to D by a store-readiness model. The model is trained on where organised stores already are. Gaps are Class A or B PINs with no organised store within 3 km.
2. **Today.** Daily temperature and rain for all 780 districts, with rule-based alerts and a playbook of what to do.
3. **Zoom and touch.**
   - Suggestions to drill in or out as you zoom.
   - Pinch, double-tap and keyboard zoom.
   - 44 px zoom buttons on touch screens.
   - A one-time gesture hint.
   - On phones, a tap keeps you on the map.
4. **Pulse.**
   - National attention and voice for 15 brands in paints, two-wheelers and quick commerce, from YouTube.
   - A district map of where each category's demand sits.
   - See `pulse/README.md`.

The published app is a private claude.ai artifact: https://claude.ai/artifact/JLopDiRL6rkfhAxDNHc8bo. The original TERRAIN link is unchanged.

## Folders

| Folder | What it holds |
|---|---|
| `pipeline/` | `load.py` joins every state's PIN files. `model.py` trains the readiness model and validates it on held-out states. `classes.py` writes the class files the app reads (`data/next/...`). |
| `weather/` | `refresh_weather.py` is the daily job (standard library only). It reads `district_points.json` (district centre points, built by `centroids.mjs`) and `district_meta.json` (names, households, population-weighted elevation, 1991-2020 monthly normals). |
| `pulse/` | Brand Pulse: the YouTube fetch, hand labels, analyst reads, aggregation and the district context file. |
| `addon/` | `plus.js` and `plus.css` are the add-on. `terrain-hooks.diff` holds the small hooks added to the app's `terrain.js`: a public map handle, a render event, a robustness score on the Priority rank, and phone tap behaviour. |

## Rebuild the classes

The class pipeline needs the published data files (`data/pins/*.attr.json` and `data/terrain/pin/*.json`) in a local folder.

    pip install pandas pyarrow scikit-learn
    export TERRAIN_DATA=/path/to/site/data NEXT_OUT=/path/to/site/data/next
    cd pipeline && python3 load.py && python3 model.py && python3 classes.py

`model.py` prints the held-out AUC. At the time of this build it was 0.932 (average precision 0.725, base rate 0.130). The baselines it beats:

- 0.867 from upper-wealth households alone;
- 0.676 from total households alone.

## Daily weather

    python3 weather/refresh_weather.py /path/to/site/data/next/today/weather.json

Sources and handling:

- **Forecast:** Open-Meteo (CC BY 4.0). The free tier is for non-commercial use; commercial deployment needs an Open-Meteo subscription.
- **Elevation:** temperatures are downscaled to each district's population-weighted elevation.
- **Thresholds:** stated in the script header. They are planning signals, not official warnings.

A scheduled task runs this every morning and republishes `data/next/today/weather.json` to the artifact.
