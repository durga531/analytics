import sys
sys.path.insert(0, "/home/user/render")
from pptx import Presentation
from lib import shp, set_paras, pos, fill, clone, delete

SRC = "/home/user/render/original_Competitor_View.pptx"
OUT = sys.argv[1]
prs = Presentation(SRC)
S = list(prs.slides)
SO = lambda sh, t: set_paras(sh, [["SO WHAT   ", t]])


def notes(s, sources=None, note=None):
    sh = shp(s, 3)
    cur = [p.text for p in sh.text_frame.paragraphs]
    set_paras(sh, [sources or cur[0], note or cur[-1]])


# ---- 1 cover: lead with the four weapons ----
s = S[0]
set_paras(shp(s, 7), ["FOUR WEAPONS THAT CROSS CATEGORIES"])
set_paras(shp(s, 8), ["The route"])
set_paras(shp(s, 9), ["Electrician and counter reach carries new categories: Polycab Experts 2.5 lakh+; Ultravolt 1 lakh+ retailers"])
set_paras(shp(s, 11), ["The motor"])
set_paras(shp(s, 12), ["Own BLDC motors: Atomberg holds 40-45% of BLDC fan value and is not on V-Guard's competitor list"])
set_paras(shp(s, 14), ["The annuity"])
set_paras(shp(s, 15), ["Installed base and service: purifier specialists earn 52-60% gross margin against V-Guard's 36%"])
set_paras(shp(s, 17), ["The balance sheet"])
set_paras(shp(s, 18), ["Capital before customers: a ₹1,800 cr Ultravolt wire plant; Crompton's ~₹500 cr rooftop order book in a year"])
set_paras(shp(s, 20), ["Sources: V-Guard Q1 FY27 presentation and calls; Atomberg DRHP (Redseer); Crompton FY26 annual report; Business Standard (3 Sep 2026); brand web stores, 26-27 Sep 2026"])

# ---- 2 executive summary ----
s = S[1]
set_paras(shp(s, 8), ["An adjacency view shows more overlap than V-Guard's table names",
                      "V-Guard's market table names 28 rivals in 14 categories. It leaves out Atomberg (40-45% of BLDC fans), Crompton in wires and solar, and still lists \"HUL Pureit\", owned by A. O. Smith since Nov 2024. Rooftop solar has no row."])
set_paras(shp(s, 14), ["Solar is splitting into tender, financed and retail models",
                       "PM Surya Ghar covers ~50 lakh households (~40 lakh systems). Crompton built a ~₹500 cr order book in a year at tender prices ~40% below its own retail kit per kW; Exide solar passed ₹1,000 cr. V-Guard has chosen retail."])
set_paras(shp(s, 18), ["V-Guard has the technology; its price band sits lower",
                       "BLDC is ~40% of its ceiling fans against 17% for the market, yet its median price is 36-80% of rivals' in seven of eight frames, before adjusting for specification. 15-litre heaters sit at parity with the rivals sampled."])
set_paras(shp(s, 25), ["Energy storage and rooftop solar", "Next-generation battery; choose retail, financed or tender economics on return"])
set_paras(shp(s, 36), ["PREMIUMISE"])
set_paras(shp(s, 37), ["Where the product is already there", "BLDC fans, BLDC chimneys, purifier service: test price architecture on matched specs"])
SO(shp(s, 40), "Defending 16 fronts equally is the default. The evidence favours funding one, defending two and premiumising selectively where V-Guard already has the product.")
notes(s, note="Notes: (M) company-reported or management statement; (D) derived by the author from reported figures; (I) inference; (P) press or rating-agency report. Price position = V-Guard median selling price / median of rival brand medians in eight product frames, not adjusted for specification")

# ---- 3 six shifts ----
s = S[2]
set_paras(shp(s, 22), ["Households on PM Surya Ghar (lakh). Installs rose from 5,038 a day (Oct-25) to 16,328 (Jul-26); ₹28,024 cr paid out; target 1 crore by Mar-27"])
set_paras(shp(s, 26), ["Solar inverters and batteries; a B2C-only model forgoes tenders, by choice"])

# ---- 5 four weapons ----
s = S[4]
set_paras(shp(s, 63), ["Capabilities, not company types: one rival can carry several (I)"])

# ---- 6 top three rivals: replace the uninformative High/High/High row ----
s = S[5]
tmpl = shp(s, 29)
for lab, pill, x, txt in [(30, 31, 0.54, "same multi-category model, entering V-Guard's home states first"),
                          (55, 56, 4.66, "widest overlap at 12 fronts, with a stronger premium shelf"),
                          (80, 81, 8.78, "owns the electrician route V-Guard's wires and switches rely on")]:
    clone(s, tmpl, x=x, y=5.66, w=3.90, h=0.28, text=[["Threat (I)  ", txt]])
    delete(shp(s, lab)); delete(shp(s, pill))

# ---- 7 energy and electricals scorecard ----
s = S[6]
set_paras(shp(s, 28), ["No row; ~50 lakh households on PM Surya Ghar"])
set_paras(shp(s, 60), ["Crompton 1 HP ₹10,250; V-Guard not compared (no matched spec)"])

# ---- 8 consumer scorecard ----
s = S[7]
set_paras(shp(s, 2), ["Consumer and kitchen: V-Guard holds a top-3 position only in water heaters; elsewhere its price band sits 20-64% below rival medians while they launch feature-led premium models"])
notes(s, note="Notes: Price position = V-Guard median selling price vs median of rival brand medians in the same frame (see next slide), not adjusted for specification; rivals differ by frame. \"Listing\" = first appearance on the brand's store, a launch proxy. Pressure is the author's view (I)")

# ---- 9 price position ----
s = S[8]
set_paras(shp(s, 2), ["Across 923 SKUs in eight product frames, V-Guard's price band sits below rivals' in seven; the gap is not yet adjusted for specification, so it signals headroom, not pricing power"])
SO(shp(s, 91), "V-Guard's ranges sit in a lower price band everywhere except its strongest franchise. That is premiumisation headroom; a spec-matched price index is the test before any price move.")
notes(s, note="Notes: Selling price on each brand's own store; colour variants once. Index = V-Guard median / median of rival brand medians (rivals equally weighted; Sunflame excluded). Medians do not control for sweep, wattage, motor, IoT, capacity or warranty. Havells, Usha, Eureka Forbes, Pureit and Racold stores not readable by script (D)")

# ---- 12 rooftop solar: separate flows from stocks; frame the model choice ----
s = S[11]
set_paras(shp(s, 2), ["Rooftop solar is splitting into tender, financed and retail models: Crompton's tender-led ~₹500 cr order book was priced ~40% below its own retail kit per kW"])
set_paras(shp(s, 5), ["PM Surya Ghar households"])
set_paras(shp(s, 7), ["Lakh (Dec-24: systems); target 1 crore by Mar-27"])
set_paras(shp(s, 25), ["Solar scale: revenue and order book"])
set_paras(shp(s, 27), ["₹ cr; an order book is a stock, not revenue"])
k = 3.00 / 1256
rows = [(28, 29, 30, "Exide solar, revenue FY26", 1000, "1,000+", "005587"),
        (31, 32, 33, "V-Guard solar, revenue FY26", 500, "<500", "D9730D"),
        (34, 35, 36, "Havells Renewables, revenue in Q1 FY27 alone", 314, "314", "005587"),
        (37, 38, 39, "Crompton rooftop order book (a stock)", 500, "~500", "66ADCB")]
ys = [2.20, 2.82, 3.44, 4.06]
for (lab, bar, val, t, v, vt, col), y in zip(rows, ys):
    set_paras(shp(s, lab), [t]); pos(shp(s, lab), y=y)
    pos(shp(s, bar), y=y + 0.24, w=v * k); fill(shp(s, bar), col)
    set_paras(shp(s, val), [vt]); pos(shp(s, val), x=4.55 + v * k + 0.05, y=y + 0.22)
SO(shp(s, 56), "~50 lakh households (~40 lakh systems) are covered against a 1-crore target. V-Guard's retail stance is a choice: judge it on return per roof.")
notes(s, note="Notes: Households benefiting (Dec-24: installations). Havells Renewables incl. solar pumps and EV chargers, one quarter as reported. Tender ₹/kW = ₹445 cr / 77 MW; retail = listed 3 kW kit / 3 (D). An order book is a stock; revenue is a flow")

# ---- 13 house wires ----
s = S[12]
set_paras(shp(s, 5), ["Corporate W&C scale, FY26"])
set_paras(shp(s, 7), ["₹ cr; not category-comparable: rivals include power cables"])

# ---- 14 switches, pumps, lighting ----
s = S[13]
set_paras(shp(s, 37), ["Crompton Mini Master 1 HP sells at ₹10,250 (MRP ₹13,000); Havells 1 HP list ₹5,325-10,925 (May 2024). No spec-matched V-Guard price was found online."])

# ---- 16 water heaters ----
s = S[15]
set_paras(shp(s, 2), ["Water heaters are V-Guard's strongest consumer franchise and the only frame where its median matches the rivals sampled; Crompton is using the July 2026 star-rating reset to attack it"])
notes(s, note="Notes: Every 15-litre storage heater on each store, selling price, tick = median; rings = first listed Jul 2026 (Crompton) or Oct 2025 (V-Guard). Listing dates are a launch proxy. Racold, Havells and A. O. Smith prices could not be read, so parity is against the rivals sampled")

# ---- 17 water purifiers: drop the 62-80% "giveaway" arithmetic ----
s = S[16]
set_paras(shp(s, 2), ["In purifiers the profit sits in service: specialists earn 52-60% gross margins, so V-Guard's economics turn on year-2 and year-3 renewal, not first-sale units"])
set_paras(shp(s, 41), [["Year 3", "  the renewal that decides purifier economics: installed units x renewal rate x AMC price x service margin (I)"],
                        ["Not sized", "  V-Guard's AMC prices vary by model and page, with different coverage; the value of free service years is not estimated here"],
                        ["V-Guard lists model-specific AMCs; Livpure's annual contract is ₹5,499"]])
notes(s, note="Notes: Services ≈ ₹117 bn total less ₹64 bn product market (D). Gross margins mix FY25 and FY26 as marked. AMC coverage differs across V-Guard's plans, so free-service years are not valued")

# ---- 18 kitchen ----
s = S[17]
set_paras(shp(s, 2), ["Kitchen is a scale-and-availability game: V-Guard's medians sit at 36-64% of rivals' in stoves, mixers and chimneys, and the group runs two BLDC chimney ladders"])

# ---- 20 signposts ----
s = S[19]
set_paras(shp(s, 42), ["~50 lakh households (~40 lakh systems) against a 1-crore target"])
set_paras(shp(s, 43), ["50.06 lakh households (Aug-26); target Mar-27"])

# ---- 21 implications ----
s = S[20]
set_paras(shp(s, 2), ["Concentrate: fund energy storage, defend the southern electrical counter and the heater franchise, premiumise selectively where V-Guard has the product, and contain the rest"])
set_paras(shp(s, 15), ["Next-generation battery share of battery sales; contribution per solar system"])
set_paras(shp(s, 29), ["PREMIUMISE"])
set_paras(shp(s, 31), ["BLDC ~40% of its fans, yet median price 64% of rivals' and chimney index 64 before spec adjustment; service ~45% of the purifier pool"])
set_paras(shp(s, 33), ["Spec-matched price index; share of fans sold above ₹3,498; AMC renewal rate"])

# ---- 22 method ----
s = S[21]
set_paras(shp(s, 34), ["One week, not spec-adjusted", "Wires and seasonal goods move with copper and weather; medians do not control for features within a frame."])

prs.save(OUT)
print("saved", OUT)

# ---- post-fixes ----
from pptx.dml.color import RGBColor
prs = Presentation(OUT); S = list(prs.slides)
s = S[11]
base = shp(s, 28).text_frame.paragraphs[0].runs[0].font.color.rgb
shp(s, 31).text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor.from_string("D9730D")
shp(s, 37).text_frame.paragraphs[0].runs[0].font.color.rgb = base
s = S[20]
set_paras(shp(s, 25), ["Top-3 heater brand at parity with the rivals sampled; 40-45% of stabilizers; Crompton relaunched heaters in July and lists a stabilizer"])
prs.save(OUT)
print("post-fixes applied")
