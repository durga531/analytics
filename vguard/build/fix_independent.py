import sys
sys.path.insert(0, "/home/user/render")
from pptx import Presentation
from lib import shp, set_paras, pos
P = sys.argv[1]
prs = Presentation(P); S = list(prs.slides)
s = S[1]
set_paras(shp(s, 16), ["The push north has paused; the headroom has not",
    "Non-South outgrew South every year from FY20 to FY25, then lagged. On a spend index, V-Guard earns ₹4.6 per ₹10,000 of household spend outside the South vs ₹11.5 in the rest of the South."])
set_paras(shp(s, 42), ["+25% base case; +34% at stretch; solar, service extra"])
s = S[7]
set_paras(shp(s, 3), ["Sources: Atomberg DRHP (Aug 2026), Exhibit 37(d), Redseer; V-Guard Q4 FY25/FY26 presentations, Q1 FY27 results and call; Sharekhan note on the Sunflame deal (13 Dec 2022)",
    "Notes: Peer segments: Crompton, Havells, Orient ECD; Atomberg consumer appliances; RR Kabel FMEG; allocation differs. Sunflame FY22 is pre-deal PBT, later years segment results. 2.0% is a profit yield on the price, not a return on capital"])
s = S[10]
set_paras(shp(s, 69), ["Inverters  4-6% > 5-7%"])
s = S[11]
set_paras(shp(s, 3), ["Sources: Atomberg DRHP (Aug 2026), Redseer pp.194-211, 220-221 (BLDC, TCO, channels, regions, purifier pool and margins); V-Guard Q4 FY26 call and presentation",
    "Notes: Market BLDC share covers all fans; V-Guard's covers ceiling fans. ₹1,707 uses Redseer's 346 vs 145 kWh a year (~13 hours a day at ~₹8.5/kWh). Service pool = ₹117 bn incl. services less ₹65 bn product. FY31P is Redseer's projection"])
s = S[12]
set_paras(shp(s, 26), ["PM Surya Ghar households"])
set_paras(shp(s, 28), ["Lakh; systems: 26 (Mar-26), ~40 (Jul-26)"])
prs.save(P)
