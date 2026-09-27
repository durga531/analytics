import sys, copy, io
sys.path.insert(0, "/home/user/render")
from pptx import Presentation
from lib import shp, set_paras, pos, fill, clone, delete, copy_slide_shapes, move_slide, waterfall, page_numbers

SRC = "/home/user/render/original_Independent_POV.pptx"
OUT = sys.argv[1]
prs = Presentation(SRC)
S = list(prs.slides)  # original order, 0-based: S[0]=cover ... S[13]=sources

# ---------- structural work first: two new slides cloned from the (unedited) choices slide ----------
q1 = copy_slide_shapes(prs, S[12])      # becomes the Q1 FY27 stress-test slide
qs = copy_slide_shapes(prs, S[12])      # becomes the "questions to test" slide
# current order: 0..13 original, 14=q1, 15=qs. Target: q1 after profitability (index 4), qs before sources.
move_slide(prs, 14, 4)                  # q1 -> position 5
move_slide(prs, 15, 14)                 # qs -> position 15 (before sources, now at 15)

SO = lambda sh, t: set_paras(sh, [["SO WHAT   ", t]])

# ============ Slide 1: cover ============
s = S[0]
set_paras(shp(s, 2), ["V-Guard: making", "breadth pay"])
set_paras(shp(s, 3), ["Where the next ₹150-200 crore of segment profit can come from, read from the outside in"])
set_paras(shp(s, 6), ["V-GUARD IN FOUR NUMBERS"])
set_paras(shp(s, 8), ["Revenue FY26, up 7.0%; 12.8% a year since FY19"])
set_paras(shp(s, 11), ["Gross margin FY26, up 6.4 points since FY19, highest among listed electrical peers"])
set_paras(shp(s, 13), ["10.5%"])
set_paras(shp(s, 14), ["EBITDA margin in Q1 FY27, from 8.4% a year earlier; 8.8% in FY26, 8.5% in FY19"])
set_paras(shp(s, 17), ["Revenue from outside the South in FY26; it was 39% in FY19"])
set_paras(shp(s, 19), ["Sources: V-Guard Q4 FY20-FY26 and Q1 FY27 earnings presentations; Atomberg DRHP (Aug 2026) peer benchmark"])

# ============ Slide 2: executive summary ============
s = S[1]
set_paras(shp(s, 2), ["V-Guard has the best gross margin among listed electrical peers and Q1 FY27 showed it can convert it; keeping that needs fewer, deeper bets"])
set_paras(shp(s, 10), ["Operating leverage has arrived; is it structural?",
                       "Gross margin rose 6.4 points since FY19 but overheads took 6.1, so EBITDA moved only from 8.5% to 8.8% by FY26. Q1 FY27 reached 10.5% on flat gross margin, helped by an ad-spend cut."])
set_paras(shp(s, 12), ["Profit comes from one business",
                       "Electronics is 27% of revenue and 48% of segment profit. Consumer Durables and Sunflame are 31% of revenue and 6% of profit; the FY26 drop in Consumer Durables erased 70% of Electricals' gain."])
set_paras(shp(s, 16), ["The push north has paused; the headroom has not",
                       "Non-South outgrew South every year from FY20 to FY25, then lagged. On an illustrative spend index, V-Guard earns ₹4.6 of every ₹10,000 households spend outside the South, against ₹11.5 in the rest of the South."])
set_paras(shp(s, 18), ["Four battles set the next five years",
                       "BLDC fans on the general-trade shelf; water heating plus purifier service; wires against a ₹1,800 crore entrant; rooftop solar, where the model chosen matters more than the market's size."])
set_paras(shp(s, 21), ["Segment profit, ₹ crore; base case"])
tm = dict(tmpl_rect=shp(s, 26), tmpl_val=shp(s, 27), tmpl_cat=shp(s, 28), tmpl_conn=shp(s, 25))
old = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
waterfall(s, [("FY26", 613, "total", "613"),
              ("Consumer Durables to 5-6% margin", 63, "inc", "+63"),
              ("Sunflame to pre-deal margin", 18, "inc", "+18"),
              ("Non-South at half the rest-of-South depth", 72, "inc", "+72"),
              ("Base case", 766, "total", "766")],
          x0=8.45, step=0.905, bw=0.51, base_y=4.68, scale=0.002385, val_w=0.91, cat_w=0.91, cat_y=4.73,
          colors={0: "012169", 4: "0076A8"}, **tm)
for i in old:
    delete(shp(s, i))
set_paras(shp(s, 42), ["+25% base case; +34% (₹819 cr) at stretch, before solar or service"])
SO(shp(s, 43), "Q1 FY27 shows the margin lever works. The harder call is which few categories get the next rupee of capital and management time.")
set_paras(shp(s, 3), ["Sources: V-Guard earnings presentations FY19-Q1 FY27 and call transcripts; prospectuses of Atomberg, Veegaland, RentoMojo, Sathya, Moneyview, Svatantra; MoSPI HCES 2023-24; Business Standard (3 Sep 2026)",
                      "Notes: Segment profit = segment results before unallocated items. Base: CD at 5-6% (its FY20-21 peak), Sunflame at its pre-deal margin, non-South at half rest-of-South depth. Stretch: CD 8%, Sunflame pre-deal profit. Illustrative on FY26 revenue"])

# ============ Slide 3: demand backdrop ============
s = S[2]
bar, lab = shp(s, 44), shp(s, 45)
pos(bar, y=4.62 - 0.19, h=0.19)
pos(lab, y=4.62 - 0.19 - 0.19)
set_paras(lab, ["32L"])
set_paras(shp(s, 50), ["PM Surya Ghar households benefiting (lakh). BEE fan star thresholds reset from Jan 2026; TPW next (M)"])

# ============ Slide 4: profitability FY19-FY26 ============
s = S[3]
set_paras(shp(s, 2), ["Since FY19 V-Guard has added 6.4 points of gross margin and kept only 0.3 at EBITDA; Q1 FY27 is the first quarter to break the pattern"])
set_paras(shp(s, 35), ["Q1 FY27 broke the pattern",
                       "EBITDA 10.5% vs 8.4% a year earlier on flat 36.9% gross margin; overheads fell from 28.5% to 26.4% of revenue."])
pos(shp(s, 35), h=0.78)
SO(shp(s, 38), "The margin lever has moved from the factory to the field, and Q1 FY27 shows it can move. Each point of overhead is worth about ₹60 crore of EBITDA.")
set_paras(shp(s, 3), ["Sources: V-Guard Q4 FY20, FY21, FY23, FY24, FY25, FY26 earnings presentations (consolidated) and Q1 FY27 results (29 Jul 2026); Screener.in for ROCE and fixed assets; V-Guard Q1 FY27 call transcript (30 Jul 2026)",
                      "Notes: FY24 on the restated basis in the FY25 presentation. Overheads = employee cost + other expenditure (includes advertising). Gross margin excludes in-house conversion cost, so insourcing lifts both gross margin and overheads"])

# ============ Slide 5 (new): Q1 FY27 stress test ============
s = q1
set_paras(shp(s, 4), ["PROFITABILITY | Q1 FY27 STRESS TEST"])
set_paras(shp(s, 2), ["Q1 FY27 lifted EBITDA margin 2.1 points with no help from gross margin; the largest single driver, lower ad spend, is a choice that can reverse"])
set_paras(shp(s, 5), ["EBITDA margin bridge, Q1 FY26 to Q1 FY27"])
set_paras(shp(s, 7), ["% of revenue; gross margin flat at 36.9%"])
tm = dict(tmpl_rect=shp(s, 12), tmpl_val=shp(s, 13), tmpl_cat=shp(s, 14), tmpl_conn=shp(s, 11))
waterfall(s, [("Q1 FY26", 8.4, "total", "8.4%"),
              ("Employee cost 9.6% to 9.1%", 0.5, "inc", "+0.5"),
              ("A&P 3.0% to 2.2%", 0.8, "inc", "+0.8"),
              ("Other overheads (D)", 0.8, "inc", "+0.8"),
              ("Q1 FY27", 10.5, "total", "10.5%")],
          x0=0.73, step=0.86, bw=0.48, base_y=5.38, scale=0.2667, val_w=0.88, cat_w=0.86, cat_y=5.43,
          colors={0: "012169", 4: "0076A8"}, **tm)
for i in range(8, 27):
    delete(shp(s, i))
set_paras(shp(s, 28), ["Which parts can last"])
set_paras(shp(s, 30), ["Driver"]); set_paras(shp(s, 31), ["What happened"]); set_paras(shp(s, 32), ["Durable?"]); set_paras(shp(s, 33), ["Test in FY27"])
rows = [
    (36, 37, 38, 39, "Revenue +23.5%", "About 14% price and 9% volume (M); the South gave 73% of the increase (D)", "Price-led, in a strong southern summer", "Unit volume growth in Q2-Q3"),
    (42, 43, 44, 45, "Employee cost +0.5 pt", "Cost grew 17.7% against revenue 23.5%", "Partly: leverage on price, not volume", "Cost per unit sold"),
    (48, 49, 50, 51, "A&P +0.8 pt", "Cut from 3.0% to 2.2% of revenue, lower in rupees too (D)", "A choice; it can reverse", "A&P in ₹ behind BLDC, water, solar"),
    (54, 55, 56, 57, "Other overheads +0.8 pt", "Freight, power and fixed costs spread over a peak quarter", "Partly seasonal", "Same ratio in Q3, a normal season"),
    (60, 61, 62, 63, "Net cash ₹231 cr to ₹670 cr", "20 of 29 days of working-capital release came from supplier credit on domestic copper", "Management expects it to normalise (M)", "Working-capital days at Q4 FY27"),
]
for a, b, c, d, ta, tb, tc, td in rows:
    set_paras(shp(s, a), [ta]); set_paras(shp(s, b), [tb]); set_paras(shp(s, c), [tc]); set_paras(shp(s, d), [td])
SO(shp(s, 64), "Q1 FY27 proves the overhead lever exists. Whether it is structural shows in Q3 FY27: a normal season, without an ad cut or copper credit.")
set_paras(shp(s, 3), ["Sources: V-Guard Q1 FY27 results presentation (29 Jul 2026) pp.6-10 and earnings call (30 Jul 2026); V-Guard Q1 FY26 results",
                      "Notes: A&P sits inside other expenses; other overheads is the residual after employee cost and A&P, rounded. Working-capital days on company TTM basis, Mar-26 to Jun-26: receivables 33 to 22, inventory 98 to 100, payables 71 to 91"])

# ============ Slide 6: peer benchmark ============
s = S[4]
set_paras(shp(s, 2), ["V-Guard converts less of its gross margin into EBITDA than any listed electrical peer, and spreads an Atomberg-sized ad budget over 13 categories"])
set_paras(shp(s, 50), ["Widest gap in the peer set, partly by design",
                       "V-Guard absorbs 27.5 points; Havells 23.2. Insourcing inflates both lines, so EBITDA is the fair test: 8.8% vs Havells 9.9%."])
SO(shp(s, 53), "On EBITDA, the fair test, V-Guard's 8.8% trails Havells' 9.9% and Crompton's 10.2%; each point is about ₹60 crore. Q1 FY27's 10.5% shows the gap can close.")

# ============ Slide 7: segment economics ============
s = S[5]
set_paras(shp(s, 50), ["Consumer Durables grew 2.4x and earns less than in FY19",
                       "Profit fell from ₹32 crore to ₹26 crore. Q1 FY27 margin recovered to 3.6%, from -2.1% a year earlier."])

# ============ Slide 8: consumer vs peers, Sunflame ============
s = S[6]
set_paras(shp(s, 2), ["Consumer Durables earns 1.6% where established peers earn 7-13%, and Sunflame's profit is 2% of the ₹660 crore paid for it"])
cb = shp(s, 10)
pos(cb, y=5.70, h=0.42)
set_paras(cb, ["Base 5-6% (CD's own FY20-21 peak): +₹55-71 crore. Stretch 8%, still below Havells: +₹103 crore"])
set_paras(shp(s, 20), ["segment profit as a share of the ₹660 crore price in FY26, against 6.7% pre-tax on the numbers at purchase (EV/sales 1.9x)"])
set_paras(shp(s, 21), [["Management: ", "integration done; aim to restore pre-deal financial health in three to five years and build a ₹1,000 crore+ kitchen business. Q1 FY27: revenue +18.3%, margin 4.0%."]])
SO(shp(s, 22), "Consumer Durables needs a margin target before a growth target: 5-6% as the base, 8% as the stretch. Q1 FY27's 3.6%, up from -2.1%, is the first sign of repair.")
set_paras(shp(s, 3), ["Sources: Atomberg DRHP (Aug 2026), Exhibit 37(d), Redseer (segment revenue and results FY24-FY26); V-Guard Q4 FY25/FY26 presentations and Q1 FY27 results; Sharekhan note on the Sunflame deal (13 Dec 2022); V-Guard Q1 FY27 call",
                      "Notes: Peer segments: Crompton, Havells and Orient ECD; Atomberg consumer appliances; RR Kabel FMEG. Cost allocation differs by company. Sunflame FY22 is PBT before the deal; FY24-FY26 segment results. 2.0% is a profit yield on the price, not a return on capital"])

# ============ Slide 9: how share-takers win ============
s = S[7]
set_paras(shp(s, 11), ["ROUTE-LED", "Wire counters, electricians, breadth, dealer credit"])
set_paras(shp(s, 12), ["DEMAND-LED", "Ad spend, R&D, online reach, premium price"])

# ============ Slide 10: geography ============
s = S[8]
set_paras(shp(s, 13), ["V-Guard revenue per ₹10,000 of household spending (index)"])
SO(shp(s, 39), "On this index, three-quarters of rest-of-South depth in states already served is worth about ₹2,500 crore of revenue; where to place counters needs internal data.")

# ============ Slide 11: where to play ============
s = S[9]
set_paras(shp(s, 64), ["THE MISSING BOX", "Rooftop solar and storage",
                       "The only large, fast pool next to a franchise V-Guard already leads; worth funding only in the model that earns its capital."])

# ============ Slide 12: consumer battles ============
s = S[10]
set_paras(shp(s, 5), ["BATTLE 1  |  BLDC FANS", "Motor efficiency is table stakes; the shelf race is on"])
set_paras(shp(s, 13), [["₹1,707  ", "a year saved at ~13 hours' daily use; ~₹700 at 8 hours (D)"]])
set_paras(shp(s, 19), [["Jan 2026  ", "BEE fan star thresholds reset; TPW next (M)"]])
set_paras(shp(s, 41), [["WHAT WINNING LOOKS LIKE  ", "A purifier business judged on year-2 and year-3 renewal and service gross profit, sold and serviced by installers who already fit heaters and batteries (hypothesis)."]])
set_paras(shp(s, 3), ["Sources: Atomberg DRHP (Aug 2026), Redseer: pp.194-208 (BLDC share, TCO, channel mix, demand by region), p.211 (purifier pool incl. services), pp.220-221 (purifier specialist gross margins); V-Guard Q4 FY26 call (BLDC ~40% of ceiling fans) and Q4 FY26 presentation (shares)",
                      "Notes: Market BLDC share covers all fans; V-Guard's covers ceiling fans. ₹1,707 uses Redseer's 346 vs 145 kWh a year (~13 hours a day at ~₹8.5/kWh). Purifier service pool = total pool incl. services (₹117 bn) less product market (₹65 bn). FY31P is Redseer's projection"])

# ============ Slide 13: electrical and energy battles ============
s = S[11]
set_paras(shp(s, 26), ["PM Surya Ghar households benefiting"])
set_paras(shp(s, 28), ["Lakh, cumulative; systems: 26 lakh (Mar-26), ~40 lakh (Jul-26)"])
set_paras(shp(s, 31), [["5.1 lakh  ", "systems installed in July 2026 alone"]])
set_paras(shp(s, 37), [["₹28,024 cr  ", "subsidy paid; scheme target date Mar-27"]])
set_paras(shp(s, 41), [["WHAT WINNING LOOKS LIKE  ", "Pick the model on return, not size: installer-led retail, financed retail or tenders carry different margin, working capital and service risk. Build on the inverter and battery franchise."]])
SO(shp(s, 42), "Defend wires with the electrician. In solar, choose the model that earns its capital before funding scale.")
set_paras(shp(s, 3), ["Sources: Business Standard (3 Sep 2026) on Ultravolt; V-Guard Q4 FY26 presentation (shares, network) and Q4 FY26 / Q1 FY27 calls; pv magazine (5 Aug 2026) and SolarQuarter (25 Mar 2026) on PM Surya Ghar; Havells Q4 FY26 information update",
                      "Notes: V-Guard wire revenue inferred from its own market size (₹21-25k cr, 65-70% organised) and share (8-9%). PM Surya Ghar households exceed systems because shared systems serve several homes; the 1-crore target date is Mar-27"])

# ============ Slide 14: choices ============
s = S[12]
set_paras(shp(s, 2), ["Three quantified levers add ₹145-160 crore of segment profit on today's revenue, about ₹200 crore at stretch; solar and service come on top"])
tm = dict(tmpl_rect=shp(s, 12), tmpl_val=shp(s, 13), tmpl_cat=shp(s, 14), tmpl_conn=shp(s, 11))
waterfall(s, [("FY26", 613, "total", "613"),
              ("CD to 5-6%", 63, "inc", "+63"),
              ("Sunflame pre-deal margin", 18, "inc", "+18"),
              ("Non-South depth", 72, "inc", "+72"),
              ("Base case", 766, "total", "766"),
              ("Stretch levers", 53, "inc", "+53"),
              ("Stretch", 819, "total", "819")],
          x0=0.62, step=0.60, bw=0.42, base_y=5.38, scale=0.00323, val_w=0.62, cat_w=0.62, cat_y=5.43,
          colors={0: "012169", 4: "0076A8", 5: "F2B27A", 6: "66ADCB"}, **tm)
for i in range(8, 27):
    delete(shp(s, i))
set_paras(shp(s, 37), ["Base 5-6% by FY28, stretch 8%; prune sub-scale SKUs; lead with BLDC fans and heaters; restore Sunflame's margin"])
set_paras(shp(s, 38), ["CD 1.6% vs peers 7-13%; Q1 FY27 3.6%; Sunflame earns 2% of its price"])
set_paras(shp(s, 44), ["₹156 cr spread over 13 categories; Q1 FY27 A&P cut to 2.2%"])
set_paras(shp(s, 50), ["₹4.6 vs ₹11.5 per ₹10,000 of spend (index)"])
set_paras(shp(s, 51), ["Depth by state; revenue per counter"])
set_paras(shp(s, 60), ["Choose energy and service models on return"])
set_paras(shp(s, 61), ["Solar and storage via retail, finance or tender only where the model earns its capital; purifier AMC judged on renewal"])
set_paras(shp(s, 62), ["~50 lakh PM Surya Ghar households; tender ~40% below retail per kW (D); service ~45% of purifier pool"])
set_paras(shp(s, 63), ["Contribution per system; AMC renewal rate"])
SO(shp(s, 64), "₹670 crore of net cash gives capacity for all five, but ₹150-170 crore of FY27 capex is committed and part of the cash is supplier credit. Focus is the constraint.")
set_paras(shp(s, 3), ["Sources: Analysis of V-Guard Q4 FY26 and Q1 FY27 disclosures and calls (FY27 capex guidance); Atomberg DRHP peer benchmark; HCES 2023-24; Business Standard; pv magazine",
                      "Notes: Base: CD at 5-6% (its FY20-FY21 peak) on FY26 revenue of ₹1,616 cr; Sunflame at its FY22 margin (12.6%) on FY26 revenue; non-South +₹696 cr revenue at the FY26 average segment margin of 10.3%. Stretch: CD 8%; Sunflame FY22 PBT of ₹44 cr. Levers sized independently; choices 2, 4 and 5 not sized"])

# ============ Slide 15 (new): questions to test ============
s = qs
set_paras(shp(s, 4), ["NEXT STEP | WHAT TO TEST WITH INTERNAL DATA"])
set_paras(shp(s, 2), ["Five questions decide the plan, and each needs V-Guard's own data to settle"])
for i in range(5, 28):
    delete(shp(s, i))
k = 12.25 / 7.64
for sh in list(s.shapes):
    if sh.left >= int(5.1 * 914400) and sh.top >= int(1.5 * 914400) and sh.top < int(6.2 * 914400):
        x = sh.left / 914400; w = sh.width / 914400
        if sh.shape_type == 1 and sh.auto_shape_type is not None and "OVAL" in str(sh.auto_shape_type):
            pos(sh, x=0.54 + (x - 5.15) * k)
        else:
            pos(sh, x=0.54 + (x - 5.15) * k, w=w * k)
set_paras(shp(s, 28), ["The five questions"])
set_paras(shp(s, 30), ["Question"]); set_paras(shp(s, 31), ["Why it matters now"]); set_paras(shp(s, 32), ["Internal data that settles it"]); set_paras(shp(s, 33), ["Decision it informs"])
rows = [
    (36, 37, 38, 39, "Is Q1 FY27's 10.5% margin structural?", "Gross margin was flat; A&P was cut 0.8 points; supplier credit released working capital", "Monthly overheads by line; price, volume and mix by category; normalised working capital", "How much of the overhead gain to bank in the FY28 plan"),
    (42, 43, 44, 45, "Where exactly does Consumer Durables lose money?", "Its FY26 profit fell ₹43 crore and erased 70% of Electricals' gain", "Contribution by category and SKU after A&P, warranty and discounts: fans, heaters, coolers, kitchen", "Which SKUs to prune; the path to 5-6%"),
    (48, 49, 50, 51, "Where should the next 5,000 counters go?", "Non-South depth is under half of rest-of-South; public data stops at region level", "State x category sell-out, revenue per counter, value-weighted distribution", "Counter targets by state and category"),
    (54, 55, 56, 57, "Can the electrician defend southern wires without a price war?", "Wire volume is flat; Ultravolt targets 1 lakh+ retailers; Crompton Armor started in TN and KA", "Electrician enrolment and activity, categories per counter, dealer churn in TN, KA, Kerala", "Bundle design and electrician spend"),
    (60, 61, 62, 63, "Which solar and purifier models earn their capital?", "Tender price is ~40% below retail per kW; service is ~45% of the purifier pool", "Contribution and working capital per commissioned system; AMC renewal by cohort", "Retail, financed or tender; own or partner service"),
]
for a, b, c, d, ta, tb, tc, td in rows:
    set_paras(shp(s, a), [ta]); set_paras(shp(s, b), [tb]); set_paras(shp(s, c), [tc]); set_paras(shp(s, d), [td])
SO(shp(s, 64), "A four-to-six-week diagnostic on these five questions would turn this outside-in view into a costed plan.")
set_paras(shp(s, 3), ["Sources: Evidence as cited on the preceding pages; V-Guard Q1 FY27 results and call; FY26 segment results",
                      "Notes: Questions are the author's; none can be answered from public disclosures alone"])

# ============ Slide 16: sources ============
s = S[13]
set_paras(shp(s, 22), ["PM Surya Ghar systems, households and capacity"])
set_paras(shp(s, 38), ["Depth index is coarse",
                       "Region level only, 2023-24 spending on 2024 population; an index for direction, not a revenue forecast. Q1 FY27 is one quarter."])

page_numbers(prs)
prs.save(OUT)

# ---------- chart data: PM Surya Ghar households, Mar-26 = 32.4 lakh ----------
import zipfile, re, shutil, os, openpyxl
tmp = OUT + ".tmp"
zin = zipfile.ZipFile(OUT)
zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename == "ppt/charts/chart15.xml":
        x = data.decode("utf8")
        x = x.replace("<c:v>26</c:v>", "<c:v>32.4</c:v>", 1)
        x = x.replace("<c:v>Homes</c:v>", "<c:v>Households</c:v>")
        data = x.encode("utf8")
    if item.filename == "ppt/embeddings/Microsoft_Excel_Sheet15.xlsx":
        wb = openpyxl.load_workbook(io.BytesIO(data))
        ws = wb.worksheets[0]
        for row in ws.iter_rows():
            for c in row:
                if c.value == 26:
                    c.value = 32.4
                if c.value == "Homes":
                    c.value = "Households"
        b = io.BytesIO(); wb.save(b); data = b.getvalue()
    zout.writestr(item, data)
zout.close(); zin.close()
shutil.move(tmp, OUT)
print("saved", OUT)
