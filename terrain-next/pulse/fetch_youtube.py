#!/usr/bin/env python3
"""Brand Pulse, YouTube fetch. Standard library only.

usage: python3 fetch_youtube.py brands.json OUT_RAW.json [days=30]
The API key is never read here: the network proxy adds it as the X-goog-api-key header for www.googleapis.com.
Quota per run (default 10,000 units a day): one search (100 units) per brand, plus about 9 units per brand for
video statistics and comments. 15 brands use about 1,650 units.
"""
import json, sys, time, re, hashlib, datetime, urllib.request, urllib.parse
API = "https://www.googleapis.com/youtube/v3/"

def get(path, **q):
    url = API + path + "?" + urllib.parse.urlencode(q)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            if e.code in (403, 404) and "commentsDisabled" in body:
                return {"items": []}
            if attempt == 2:
                raise RuntimeError(f"{path} {e.code}: {body}")
            time.sleep(2 * (attempt + 1))

def clean(t):
    t = re.sub(r"\s+", " ", t or "").strip()
    return t

# giveaway and self-promotion comments say nothing about a brand
SPAM = re.compile(r"give ?away|winner|pin (me|my)|subscribe|my channel|whatsapp|telegram|\bdm\b|referral code|use code", re.I)

def attributed(text, title, brand, rivals):
    """A comment counts for a brand if it names the brand, or if the video is about this brand and no rival."""
    if re.search(brand, text, re.I):
        return True
    return bool(re.search(brand, title, re.I)) and not any(re.search(r, title, re.I) for r in rivals)

def main(brands_path, out, days=30):
    cfg = json.load(open(brands_path))
    since = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = {"fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes"), "days": days, "categories": {}}
    for cat, brands in cfg.items():
        result["categories"][cat] = {}
        for b in brands:
            rivals = [o["mention"] for o in brands if o is not b]
            s = get("search", part="snippet", q=b["q"], regionCode="IN", type="video", order="relevance",
                    publishedAfter=since, maxResults=25, safeSearch="none")
            ids = [i["id"]["videoId"] for i in s.get("items", []) if i.get("id", {}).get("videoId")]
            vids = []
            if ids:
                v = get("videos", part="snippet,statistics", id=",".join(ids))
                for it in v.get("items", []):
                    st, sn = it.get("statistics", {}), it.get("snippet", {})
                    own = any(re.search(p, sn.get("channelTitle", ""), re.I) for p in b.get("own", []))
                    vids.append({"id": it["id"], "title": sn.get("title", ""), "channel": sn.get("channelTitle"), "own": own, "published": sn.get("publishedAt"),
                                 "views": int(st.get("viewCount", 0) or 0), "likes": int(st.get("likeCount", 0) or 0),
                                 "comments": int(st.get("commentCount", 0) or 0)})
            # comments from the most-discussed independent videos
            earned = sorted([x for x in vids if not x["own"] and x["comments"] > 0], key=lambda x: -x["comments"])[:8]
            comments = []
            for x in earned:
                c = get("commentThreads", part="snippet", videoId=x["id"], maxResults=50, order="relevance", textFormat="plainText")
                for it in c.get("items", []):
                    sn = it["snippet"]["topLevelComment"]["snippet"]
                    t = clean(sn.get("textDisplay"))
                    if not (12 <= len(t) <= 400) or "http" in t.lower() or SPAM.search(t):
                        continue
                    if not attributed(t, x["title"], b["mention"], rivals):
                        continue
                    cid = hashlib.sha1((x["id"] + t).encode()).hexdigest()[:12]
                    comments.append({"id": cid, "v": x["id"], "t": t, "likes": int(sn.get("likeCount", 0) or 0)})
            result["categories"][cat][b["name"]] = {"query": b["q"], "videos": vids, "comments": comments}
            print(f"{cat:16s} {b['name']:18s} videos {len(vids):2d}  views {sum(x['views'] for x in vids):>12,}  comments {len(comments)}")
            time.sleep(0.5)
    json.dump(result, open(out, "w"), ensure_ascii=False)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 30)
