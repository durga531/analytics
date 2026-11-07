"""Local, versioned English baseline. Scores are not calibrated probabilities."""
from collections import defaultdict
import hashlib
import json
import re
from langdetect import DetectorFactory, detect_langs
from langdetect.lang_detect_exception import LangDetectException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .models import now
from .storage import digest

DetectorFactory.seed = 0
DEFAULT_ASPECTS = {
    "noise": [r"\bnois\w*",r"\bquiet\w*",r"\bsilent\w*",r"\brattl\w*",r"\bhumm?ing\b"],
    "airflow": [r"\bair\s*(flow|delivery|throw)\b",r"\bbreeze\b",r"\bcooling\b",r"\bspeed\b"],
    "build_quality": [r"\bbuild\b",r"\bquality\b",r"\bplastic\b",r"\bbroke\w*",r"\bdurab\w*",r"\bwobbl\w*",r"\bmotor\b"],
    "power_efficiency": [r"\bpower\b",r"\belectric\w*",r"\benergy\b",r"\bwatts?\b",r"\bbldc\b"],
    "installation": [r"\binstall\w*",r"\bfitting\b",r"\belectrician\b"],
    "service_warranty": [r"\bservice\b",r"\bwarranty\b",r"\bsupport\b",r"\brepair\w*"],
    "delivery": [r"\bdelivery\b",r"\bpackag\w*",r"\bshipping\b",r"\barrived\b"],
    "value": [r"\bprice\b",r"\bvalue\b",r"\bmoney\b",r"\bexpensive\b",r"\bworth\b"],
    "controls": [r"\bremote\b",r"\bcontrols?\b",r"\bapp\b",r"\bbuttons?\b"]
}
DOMAIN_LEXICON = {"noisy":-2.0,"quiet":1.5,"silent":1.5,"rattling":-2.0,"wobbling":-2.0,"flimsy":-2.0,"durable":1.5,"overpriced":-2.0,"unresponsive":-2.0,"defective":-2.5}


def version_for(aspects, language):
    config = json.dumps({"aspects":aspects,"domain_lexicon":DOMAIN_LEXICON,"language":language},sort_keys=True)
    return "vader-3.3.2-personal-v1-" + hashlib.sha256(config.encode()).hexdigest()[:10]


def label(score):
    return "positive" if score >= .05 else "negative" if score <= -.05 else "neutral"


def score_reviews(db, aspects_path=None, language="auto"):
    aspects = json.loads(open(aspects_path,encoding="utf-8").read()) if aspects_path else DEFAULT_ASPECTS
    compiled = {aspect:[re.compile(pattern,re.I) for pattern in patterns] for aspect,patterns in aspects.items()}
    analyzer = SentimentIntensityAnalyzer()
    analyzer.lexicon.update(DOMAIN_LEXICON)
    version = version_for(aspects,language)
    totals = defaultdict(int)
    # Iterate independently of the write cursor; work remains bounded per review.
    rows = db.execute("SELECT * FROM reviews").fetchall()
    for row in rows:
        body = row["body"].strip()
        flags = []
        detected,probability = None,None
        if language == "en":
            detected,probability = "en",None
            flags.append("english_assumed_by_operator")
        elif body:
            try:
                candidate = detect_langs(body)[0]
                detected,probability = candidate.lang,candidate.prob
            except LangDetectException:
                pass
        status = "empty_body" if not body else "scored" if detected == "en" and (language == "en" or (probability or 0) >= .8) else "needs_language_review"
        if len(body) < 40:
            flags.append("short_text")
        if row["review_date"] is None:
            flags.append("missing_review_date")
        if row["verified"] != 1:
            flags.append("no_verified_purchase_badge_recorded")
        if db.execute("SELECT COUNT(DISTINCT asin) FROM review_observations WHERE review_id=?",(row["review_id"],)).fetchone()[0] > 1:
            flags.append("review_observed_under_multiple_asins")
        score = analyzer.polarity_scores(body)["compound"] if status == "scored" else None
        sentiment_label = label(score) if score is not None else "unscored"
        if score is not None and row["rating"] is not None and ((row["rating"] <= 2 and score >= .3) or (row["rating"] >= 4 and score <= -.3)):
            flags.append("text_rating_disagreement")
        by_aspect = defaultdict(list)
        if status == "scored":
            # Sentence/contrast clauses limit sentiment bleeding across aspects.
            # Still a heuristic: conjunction, sarcasm and implicit aspects need review.
            clauses = re.split(r"(?<=[.!?;])\s+|\bbut\b|\bhowever\b|\bwhereas\b",body,flags=re.I)
            for clause in clauses:
                clause = clause.strip()
                if not clause:
                    continue
                for aspect,patterns in compiled.items():
                    if any(pattern.search(clause) for pattern in patterns):
                        by_aspect[aspect].append({"text":clause,"score":analyzer.polarity_scores(clause)["compound"]})
        with db:
            db.execute("DELETE FROM review_aspects WHERE review_id=? AND scorer_version=?",(row["review_id"],version))
            db.execute("""INSERT OR REPLACE INTO review_sentiment VALUES (?,?,?,?,?,?,?,?,?,?,?)""",(row["review_id"],version,digest(body),score,sentiment_label,status,detected,probability,json.dumps(sorted(by_aspect)),json.dumps(flags),now()))
            for aspect,evidence in by_aspect.items():
                db.execute("INSERT INTO review_aspects VALUES (?,?,?,?,?)",(row["review_id"],version,aspect,sum(e["score"] for e in evidence)/len(evidence),json.dumps(evidence,ensure_ascii=False)))
        totals[status] += 1
    return {"scorer_version":version,"processed":len(rows),**totals}
