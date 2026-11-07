#!/usr/bin/env python3
"""Brand Pulse, aggregate. Standard library only.

usage: python3 aggregate_pulse.py RAW.json LABELS.txt QUOTES.json OUT.json
RAW is fetch_youtube.py output. LABELS has one line per labelled comment under a "## Brand" header:
    <id> <voice> [<sentiment> <theme>]
QUOTES (pulse_reads.json) holds the analyst read per category and brand, and quotes paraphrased in English. Raw comment text is never written to OUT.
"""
import json, sys, collections

VOICES = {"c": "consumers", "t": "trade", "i": "investors", "a": "ad and content reactions"}
THEMES = {"q": "quality and reliability", "p": "price, offers and schemes", "s": "service, delivery and parts",
          "d": "design and features", "o": "brand and other"}
MIN_READ = 8   # fewer consumer comments than this: shown as too few to read

def read_labels(path):
    out, brand = {}, None
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("## "):
            brand = line[3:].strip(); out[brand] = {}
        elif line and not line.startswith("#") and brand:
            parts = line.split()
            out[brand][parts[0]] = parts[1:]
    return out

def main(raw_p, lab_p, quotes_p, out_p):
    raw, labels, quotes = json.load(open(raw_p)), read_labels(lab_p), json.load(open(quotes_p))
    res = {"fetched_utc": raw["fetched_utc"], "days": raw["days"], "labelled": lab_p.rsplit("/", 1)[-1].split(".")[0],
           "source": "YouTube Data API v3: the 25 most relevant videos per brand in India over the window, "
                     "their view counts, and comments on the most-discussed independent videos.",
           "method": {"voices": VOICES, "themes": THEMES, "min_read": MIN_READ,
                      "net": "consumer comments: (positive minus negative) divided by all consumer comments"},
           "categories": {}}
    for cat, brands in raw["categories"].items():
        tot_earned = sum(x["views"] for b in brands.values() for x in b["videos"] if not x["own"])
        tot_own = sum(x["views"] for b in brands.values() for x in b["videos"] if x["own"])
        cat_out = {"earned_views": tot_earned, "owned_views": tot_own, "head": quotes.get("_" + cat, {}).get("head", ""),
                   "read": quotes.get("_" + cat, {}).get("read", ""), "brands": {}}
        for name, b in brands.items():
            lab = labels.get(name, {})
            earned = sum(x["views"] for x in b["videos"] if not x["own"])
            owned = sum(x["views"] for x in b["videos"] if x["own"])
            n_lab = len(lab)
            rel = {k: v for k, v in lab.items() if v and v[0] != "x"}
            voice = collections.Counter(v[0] for v in rel.values())
            cons = [v for v in rel.values() if v[0] == "c" and len(v) == 3]
            pos = sum(1 for v in cons if v[1] == "+"); neg = sum(1 for v in cons if v[1] == "-")
            th_neg = collections.Counter(v[2] for v in cons if v[1] == "-")
            th_pos = collections.Counter(v[2] for v in cons if v[1] == "+")
            ads = [v for v in rel.values() if v[0] == "a" and len(v) == 3]
            inv = [v for v in rel.values() if v[0] == "i" and len(v) == 3]
            q = quotes.get(name, {})
            cat_out["brands"][name] = {
                "videos": len(b["videos"]), "earned_views": earned, "owned_views": owned,
                "earned_share": round(earned / tot_earned, 4) if tot_earned else None,
                "own_channel_share": round(owned / (owned + earned), 4) if owned + earned else None,
                "comments_fetched": len(b["comments"]), "labelled": n_lab, "relevant": len(rel),
                "voice": {VOICES[k]: voice.get(k, 0) for k in VOICES},
                "consumer": {"n": len(cons), "pos": pos, "neg": neg,
                             "net": round((pos - neg) / len(cons), 2) if len(cons) >= MIN_READ else None,
                             "neg_themes": [[THEMES[k], n] for k, n in th_neg.most_common(3)],
                             "pos_themes": [[THEMES[k], n] for k, n in th_pos.most_common(3)]},
                "ad_reaction": {"n": len(ads), "pos": sum(1 for v in ads if v[1] == "+"), "neg": sum(1 for v in ads if v[1] == "-")},
                "investor": {"n": len(inv), "pos": sum(1 for v in inv if v[1] == "+"), "neg": sum(1 for v in inv if v[1] == "-")},
                "top1_share": round(max([x["views"] for x in b["videos"] if not x["own"]] or [0]) / earned, 2) if earned else None,
                "read": q.get("read", ""), "worry": q.get("worry", ""), "quotes": q.get("quotes", []),
                "top_earned": [{"id": x["id"], "title": x["title"][:90], "channel": x["channel"], "views": x["views"]}
                               for x in sorted([x for x in b["videos"] if not x["own"]], key=lambda x: -x["views"])[:3]],
            }
        res["categories"][cat] = cat_out
    json.dump(res, open(out_p, "w"), ensure_ascii=False, separators=(",", ":"))
    for cat, c in res["categories"].items():
        print(f"\n{cat}: earned {c['earned_views']/1e6:.2f}M, owned {c['owned_views']/1e6:.2f}M")
        for n, b in c["brands"].items():
            cs = b["consumer"]
            print(f"  {n:17s} earned {b['earned_views']/1e6:6.2f}M share {b['earned_share']*100:5.1f}%  own-chan {(b['own_channel_share'] or 0)*100:5.1f}%  "
                  f"rel {b['relevant']:2d}/{b['labelled']:2d} voice {b['voice']}  cons n={cs['n']:2d} +{cs['pos']} -{cs['neg']} net {cs['net']}  neg {cs['neg_themes'][:2]}")

if __name__ == "__main__":
    main(*sys.argv[1:5])
