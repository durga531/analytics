/* TERRAIN Next add-on.
   1. Store classes: every PIN graded A to D by a store-readiness model trained on where organised stores already are,
      with "gap" PINs (no organised store within 3 km) highlighted, a scoped shortlist and CSV export.
   2. Today: daily temperature and rain for all 780 districts, rule-based alerts and a playbook of what to do.
   3. Zoom and touch: suggestions to drill in or out as you zoom, a one-time gesture hint on touch screens,
      keyboard focus on the map, bigger zoom buttons for fingers.
   4. Pulse: what India watches and says about brands in three categories (YouTube, national), with a map of
      where each category's demand sits (district data already in TERRAIN).
   Talks to the app only through window.TERRAIN and the "terrain:render" event. */
(function () {
  "use strict";
  const $ = (s, r) => (r || document).querySelector(s);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = (n, d) => (n == null || isNaN(n) ? "n/a" : Number(n).toLocaleString("en-IN", { maximumFractionDigits: d || 0, minimumFractionDigits: d || 0 }));
  const size = (n) => (n == null || isNaN(n) ? "n/a" : n >= 1e7 ? fmt(n / 1e7, 1) + " crore" : n >= 1e5 ? fmt(n / 1e5, 1) + " lakh" : fmt(n));
  const pct = (x) => (x == null || isNaN(x) ? "n/a" : Math.round(100 * x) + "%");
  const slug = (s) => String(s || "").toLowerCase().replace(/&/g, " ").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  const cache = {};
  const getJSON = (u) => (cache[u] = cache[u] || fetch(u).then((r) => { if (!r.ok) throw new Error(u + " " + r.status); return r.json(); }));

  const CLASS = {
    A: { color: "#7d2f00", name: "Class A", line: "Ready for flagship formats" },
    B: { color: "#d04a02", name: "Class B", line: "Ready for standard formats" },
    C: { color: "#f2a35b", name: "Class C", line: "Compact formats" },
    D: { color: "#ece6dc", name: "Class D", line: "Distribution first" },
  };
  const GAP = "#0e7c93";
  const SVC = ["gap: no organised store within 3 km", "served nearby: an organised store within 3 km", "has an organised store in this PIN"];
  const FLAG = {
    rain_extreme: { label: "Extremely heavy rain", color: "#0b3c7d", group: "rain", pri: 1 },
    rain_very_heavy: { label: "Very heavy rain", color: "#1f5fae", group: "rain", pri: 2 },
    heat_extreme: { label: "Extreme heat", color: "#7a1608", group: "heat", pri: 3 },
    rain_heavy: { label: "Heavy rain", color: "#4f8fd6", group: "rain", pri: 4 },
    heat: { label: "Heat", color: "#c8410a", group: "heat", pri: 5 },
    humid_heat: { label: "Humid heat", color: "#e8892b", group: "heat", pri: 6 },
    cold: { label: "Cold", color: "#6a51a3", group: "cold", pri: 7 },
    wet_week: { label: "Wetter week than normal", color: "#a7c8ec", group: "rain", pri: 8 },
    dry_window: { label: "Seven dry, mild days", color: "#bfdcae", group: "dry", pri: 9 },
    warming: { label: "Warming against last week", color: null, group: "shift", pri: 10 },
    cooling: { label: "Cooling against last week", color: null, group: "shift", pri: 11 },
  };
  const PLAY = {
    rain: "Expect lower store footfall and slower deliveries for one to three days. Shift effort to home delivery and quick commerce; stock rainwear, umbrellas, mosquito repellent and ready-to-eat food; plan staff travel and keep stock above flood level.",
    heat: "Cooling and hydration demand rises: air conditioners, fans, coolers, beverages, ice cream, oral rehydration, sunscreen. Move deliveries and field work to the morning and protect staff from heat.",
    cold: "Heaters, geysers, winter wear and hot beverages move. Evening footfall falls in hill towns; trade earlier in the day.",
    dry: "A good window for exterior painting, waterproofing, construction starts, outdoor events and brand activations.",
    shift: "Temperatures are moving by 3 C or more against last week; rebalance seasonal ranges and in-store displays.",
  };
  const NONE = "#f1ede6";

  const VOICE = { c: "Consumer", t: "Trade", i: "Investor", a: "Ad reaction" };
  const PRAMP = ["#efedf5", "#dadaeb", "#bcbddc", "#9e9ac8", "#756bb1", "#54278f"];
  const PCAT = {
    "Paints": { m: [["bld", "New building"], ["aff", "Upper-wealth homes"]], why: "Paint demand follows new building and repainting by wealthier homes." },
    "Two-wheelers": { m: [["v2w", "Registrations"], ["ev", "Electric share"]], why: "Registrations show where two-wheelers sell; electric share shows where Ather and the EV ranges compete." },
    "Quick commerce": { m: [["qc", "Dark stores"], ["unserved", "No dark store yet"]], why: "Dark stores show where quick commerce already delivers; upper-wealth homes in districts without one show where it could go next." },
  };
  const NX = { mode: null, pulse: null, pctx: null, pcat: "Two-wheelers", pmetric: {}, popen: null, meta: null, dclass: null, gaps: null, weather: null, wmetric: "alerts", pinState: null, pinClass: {}, sel: null, chipKey: null };

  function ready(fn) {
    const t0 = Date.now();
    (function poll() {
      const T = window.TERRAIN, m = T && T.map;
      if (m && m.getLayer && m.getLayer("s-line")) return fn(T, m);
      if (Date.now() - t0 > 60000) return;
      setTimeout(poll, 250);
    })();
  }

  ready(function (T, map) {
    // ---------------- shell: buttons, drawer, legend, tip, chip, hint
    const right = $("#top .right");
    const mk = (id, dot, label, title) => { // eslint-disable-line
      const b = document.createElement("button");
      b.className = "nxBtn"; b.id = id; b.type = "button"; b.setAttribute("aria-pressed", "false"); b.title = title;
      b.innerHTML = `<span class="dot" style="background:${dot}"></span><span class="nxL">${label}</span>`;
      right.insertBefore(b, right.firstChild);
      return b;
    };
    const btnToday = mk("nxToday", "#4f8fd6", "Today", "Today: temperature and rain for every district, alerts and what to do");
    const btnClass = mk("nxClass", CLASS.A.color, "Classes", "Store classes: every PIN graded A to D for organised retail, with gaps highlighted");
    right.insertBefore(btnClass, btnToday);
    const btnPulse = mk("nxPulse", "#756bb1", "Pulse", "Brand Pulse: what India watches and says about brands in paints, two-wheelers and quick commerce, and where each category's demand sits");
    right.insertBefore(btnPulse, btnToday.nextSibling);
    const centre = $("#centre");
    const drawer = document.createElement("aside");
    drawer.id = "nxDrawer"; drawer.className = "nxD hidden"; drawer.setAttribute("role", "dialog"); drawer.setAttribute("aria-modal", "false");
    const leftPane = $("#left");
    const dock = () => { const host = window.innerWidth > 900 && leftPane ? leftPane : centre; if (drawer.parentNode !== host) host.appendChild(drawer); drawer.classList.toggle("docked", host === leftPane); };
    dock(); window.addEventListener("resize", dock);
    const legend = document.createElement("div"); legend.id = "nxLegend"; legend.className = "hidden"; centre.appendChild(legend);
    const tip = document.createElement("div"); tip.id = "nxTip"; tip.className = "hidden"; centre.appendChild(tip);
    const chip = document.createElement("div"); chip.id = "nxChip"; chip.className = "hidden"; chip.setAttribute("role", "status"); centre.appendChild(chip);
    const hint = document.createElement("div"); hint.id = "nxHint"; hint.className = "hidden"; hint.setAttribute("role", "status"); centre.appendChild(hint);

    // ---------------- map layers (inserted under the state borders, above the app's fills)
    const empty = { type: "FeatureCollection", features: [] };
    map.addSource("nx-pins", { type: "geojson", data: empty });
    map.addLayer({ id: "nx-d-fill", type: "fill", source: "districts", paint: { "fill-color": NONE, "fill-opacity": 1 }, layout: { visibility: "none" } }, "s-line");
    map.addLayer({ id: "nx-d-line", type: "line", source: "districts", paint: { "line-color": "#ffffff", "line-width": 0.4 }, layout: { visibility: "none" } }, "s-line");
    map.addLayer({ id: "nx-p-fill", type: "fill", source: "nx-pins", paint: { "fill-color": ["get", "_c"], "fill-opacity": 1 }, layout: { visibility: "none" } }, "s-line");
    map.addLayer({ id: "nx-p-line", type: "line", source: "nx-pins", paint: { "line-color": "#ffffff", "line-width": 0.4 }, layout: { visibility: "none" } }, "s-line");
    map.addLayer({ id: "nx-p-gap", type: "line", source: "nx-pins", filter: ["==", ["get", "_g"], 1], paint: { "line-color": GAP, "line-width": ["interpolate", ["linear"], ["zoom"], 5, 1.2, 10, 2.6] }, layout: { visibility: "none" } }, "s-line");
    map.addLayer({ id: "nx-p-sel", type: "line", source: "nx-pins", filter: ["==", ["get", "pincode"], ""], paint: { "line-color": "#1d1d1b", "line-width": 3 }, layout: { visibility: "none" } });
    const NXL = ["nx-d-fill", "nx-d-line", "nx-p-fill", "nx-p-line", "nx-p-gap", "nx-p-sel"];
    const vis = (ids, on) => ids.forEach((id) => map.setLayoutProperty(id, "visibility", on ? "visible" : "none"));

    // ---------------- mode switching
    function setMode(m) {
      NX.mode = NX.mode === m ? null : m;
      btnClass.setAttribute("aria-pressed", String(NX.mode === "class"));
      btnToday.setAttribute("aria-pressed", String(NX.mode === "today"));
      btnPulse.setAttribute("aria-pressed", String(NX.mode === "pulse"));
      document.body.classList.toggle("nx-on", !!NX.mode);
      const home = $("#home"); if (NX.mode && home) home.classList.add("hidden");
      tip.classList.add("hidden");
      if (!NX.mode) { vis(NXL, false); drawer.classList.add("hidden"); legend.classList.add("hidden"); return; }
      drawer.classList.remove("hidden");
      drawer.innerHTML = `<div class="nxHead"><div class="nxKick">Loading</div><h2>One moment</h2><button class="nxX" aria-label="Close">×</button></div>`;
      wireClose();
      (NX.mode === "class" ? loadClass() : NX.mode === "pulse" ? loadPulse() : loadToday()).then(refresh).catch((e) => {
        drawer.innerHTML = `<div class="nxHead"><div class="nxKick">Could not load</div><h2>This view needs data that did not arrive.</h2><button class="nxX" aria-label="Close">×</button></div><div class="nxBody"><p>${esc(e.message)}</p><div class="nxActions"><button class="primary" id="nxRetry">Retry</button></div></div>`;
        wireClose(); const r = $("#nxRetry"); if (r) r.onclick = () => { const m2 = NX.mode; NX.mode = null; Object.keys(cache).forEach((k) => delete cache[k]); setMode(m2); };
      });
    }
    function wireClose() {
      const x = drawer.querySelector(".nxX"); if (x) x.onclick = (e) => { e.stopPropagation(); setMode(NX.mode); };
      const h = drawer.querySelector(".nxHead");
      if (h && window.innerWidth <= 900) { h.setAttribute("role", "button"); h.setAttribute("aria-label", "Expand or shrink this panel"); h.onclick = () => drawer.classList.toggle("tall"); }
    }
    btnClass.onclick = () => setMode("class");
    btnToday.onclick = () => setMode("today");
    btnPulse.onclick = () => setMode("pulse");
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && NX.mode && !e.defaultPrevented) setMode(NX.mode); });
    window.addEventListener("terrain:render", () => { if (NX.mode) refresh(); });

    const loadClass = () => Promise.all([getJSON("data/next/class_meta.json"), getJSON("data/next/district_class.json"), getJSON("data/next/class_gaps.json")]).then(([m, d, g]) => { NX.meta = m; NX.dclass = d; NX.gaps = g; });
    const loadToday = () => getJSON("data/next/today/weather.json").then((w) => { NX.weather = w; });
    const loadPulse = () => Promise.all([getJSON("data/next/pulse/brand_pulse.json"), getJSON("data/next/pulse/context.json"), getJSON("data/next/today/district_meta.json")]).then(([p, c, m]) => { NX.pulse = p; NX.pctx = c; NX.dmeta = NX.dmeta || m; });
    const S = () => T.S || {};
    const districtName = (id) => { const f = map.querySourceFeatures("districts", { filter: ["==", ["get", "objectid"], Number(id)] })[0]; return f ? f.properties.district : null; };

    function refresh() {
      if (NX.mode === "class") return renderClass();
      if (NX.mode === "today") return renderToday();
      if (NX.mode === "pulse") return renderPulse();
    }

    // ---------------- store classes
    function toIndia() { const s = S(); s.state = null; s.district = null; s.micro = null; s.pin = null; return T.setLevel("national"); }
    function scope() {
      const s = S();
      if (s.level === "national") return { kind: "india", label: "India" };
      if (s.district != null) return { kind: "district", did: String(s.district), state: s.state, label: districtName(s.district) || "this district" };
      if (s.state) return { kind: "state", state: s.state, label: s.state };
      return { kind: "india", label: "India" };
    }
    function gapRows(sc) {
      const c = NX.gaps.cols, ix = (k) => c.indexOf(k);
      return NX.gaps.rows.filter((r) => sc.kind === "india" || (sc.kind === "state" ? r[ix("state")] === sc.state || r[ix("slug")] === slug(sc.state) : r[ix("did")] === sc.did))
        .map((r) => Object.fromEntries(c.map((k, i) => [k, r[i]])));
    }
    async function showPins(state) {
      const sl = slug(state);
      if (NX.pinState !== sl) {
        const [topo, cls] = await Promise.all([getJSON(`data/pins/${sl}.topo.json`), getJSON(`data/next/pin_class/${sl}.json`)]);
        const obj = topo.objects[Object.keys(topo.objects)[0]];
        const fc = topojson.feature(topo, obj);
        fc.features.forEach((f) => {
          const k = cls[f.properties.pincode];
          f.properties._k = k ? k[0] : "";
          f.properties._c = k ? CLASS[k[0]].color : NONE;
          f.properties._g = k && (k[0] === "A" || k[0] === "B") && k[2] === 0 ? 1 : 0;
        });
        NX.pinClass = cls; NX.pinFC = fc; NX.pinState = sl;
        map.getSource("nx-pins").setData(fc);
      }
    }
    function districtRamp(vals) {
      const nz = vals.filter((v) => v > 0).sort((a, b) => a - b);
      const q = (p) => nz[Math.min(nz.length - 1, Math.floor(p * nz.length))] || 0;
      return [q(0.2), q(0.4), q(0.6), q(0.8)];
    }
    const TEAL = ["#e3f1f3", "#a8d5dc", "#5fb0bf", "#1f8599", "#0b4f5e"];
    async function renderClass() {
      const sc = scope(), m = NX.meta, s = m.summary, total = m.aff_total;
      const atPin = sc.kind === "district";
      if (atPin) {
        await showPins(sc.state);
        vis(["nx-d-fill", "nx-d-line"], false); vis(["nx-p-fill", "nx-p-line", "nx-p-gap", "nx-p-sel"], true);
      } else {
        const ids = Object.keys(NX.dclass), vals = ids.map((k) => NX.dclass[k].uab_aff || 0), br = districtRamp(vals);
        const expr = ["match", ["get", "objectid"]];
        ids.forEach((k, i) => { const v = vals[i]; expr.push(Number(k), v <= 0 ? NONE : TEAL[v < br[0] ? 0 : v < br[1] ? 1 : v < br[2] ? 2 : v < br[3] ? 3 : 4]); });
        expr.push(NONE);
        map.setPaintProperty("nx-d-fill", "fill-color", expr);
        vis(["nx-p-fill", "nx-p-line", "nx-p-gap", "nx-p-sel"], false); vis(["nx-d-fill", "nx-d-line"], true);
        NX.dBreaks = br;
      }
      // legend
      legend.classList.remove("hidden");
      legend.innerHTML = atPin
        ? `<div class="t">Store class by PIN <span class="nxTag model">model</span></div>` + Object.keys(CLASS).map((k) => `<div class="row"><span class="sw" style="background:${CLASS[k].color}"></span>${CLASS[k].name}: ${CLASS[k].line}</div>`).join("") + `<div class="row"><span class="sw" style="background:#fff;border:2px solid ${GAP}"></span>Gap: Class A or B with no organised store within 3 km</div>`
        : `<div class="t">Upper-wealth households in gap PINs <span class="nxTag model">model</span></div><div class="ramp">${TEAL.map((c) => `<span style="background:${c}"></span>`).join("")}</div><div class="ticks"><span>fewer</span><span>${size(NX.dBreaks[3])}+</span></div><div class="nxNote" style="margin-top:4px">Class A and B PINs with no organised store within 3 km. Grey: none. Click a district to see its PINs.</div>`;
      // drawer
      const rows = gapRows(sc);
      const scopeTot = sc.kind === "india" ? null : rows.reduce((a, r) => a + (r.aff_hh || 0), 0);
      const aShare = s.A.aff / total;
      const head = sc.kind === "india"
        ? `Class A markets are ${pct(s.A.pins / m.pins)} of PINs but hold ${pct(aShare)} of India's upper-wealth households. ${fmt(s.A.gap)} of them have no organised store within 3 km.`
        : rows.length
          ? `${esc(sc.label)}: ${fmt(rows.length)} Class A or B ${rows.length === 1 ? "PIN" : "PINs"} with no organised store within 3 km, home to ${size(scopeTot)} upper-wealth households.`
          : `${esc(sc.label)}: every Class A and B PIN already has an organised store within 3 km.`;
      const table = `<table class="nxCls">${Object.keys(CLASS).map((k) => `<tr class="top"><td><span class="k"><span class="sw" style="background:${CLASS[k].color}"></span>${CLASS[k].name}</span></td><td class="n">${fmt(s[k].pins)} PINs<div class="f">${size(s[k].aff)} upper-wealth</div></td><td class="n">${pct(s[k].served_rate)}<div class="f">have a store</div></td><td class="n">${fmt(s[k].gap)}<div class="f">gaps</div></td></tr><tr><td colspan="4" class="fmt">${esc(m.formats[k])}</td></tr>`).join("")}</table>`;
      const list = rows.slice(0, 15).map((r, i) => `<li tabindex="0" data-pin="${esc(r.pin)}" data-did="${esc(r.did)}"><span class="r">${i + 1}</span><span class="m"><span class="t">${esc(r.office)} · ${esc(r.pin)}</span><br><span class="s">${esc(r.district)}, ${esc(r.state)} · Class ${r.cls} · ${r.km_nearest_store == null ? "no store data" : fmt(r.km_nearest_store, 1) + " km to nearest store"}</span></span><span class="v">${size(r.aff_hh)}</span></li>`).join("");
      drawer.innerHTML = `<div class="nxHead"><div class="nxKick">Store classes · ${esc(sc.label)}</div><h2>${head}</h2><button class="nxX" aria-label="Close">×</button></div>
        <div class="nxBody">
          <p class="nxNote" style="margin-top:0">Every PIN is graded by a store-readiness model trained on where organised stores already are <span class="nxTag model">model</span>. Tested on states it never saw: it ranks a PIN with a store above one without ${Math.round(m.auc * 100)}% of the time (AUC ${m.auc.toFixed(2)}).</p>
          ${sc.kind === "india" ? `<h3>The four classes</h3>${table}` : ""}
          <h3>${sc.kind === "india" ? "Largest gaps in India" : "Largest gaps here"}</h3>
          ${rows.length ? `<ol class="nxList">${list}</ol>` : `<p class="nxNote">No Class A or B gaps in ${esc(sc.label)}: every ready PIN has an organised store within 3 km.</p>`}
          <div class="nxActions">${rows.length ? `<button class="primary" id="nxCsv">Download ${rows.length === 1 ? "this gap" : "all " + fmt(rows.length) + " gaps"} (CSV)</button>` : ""}${sc.kind !== "india" ? `<button id="nxIndia">Back to India</button>` : ""}</div>
          ${sc.kind === "india" ? `<p class="nxNote">Click a district on the map, or a row above, to see its PINs graded A to D. Gap PINs carry a teal outline.</p>` : ""}
          <h3>How to read this</h3>
          <div class="nxBound"><p><b>Can say:</b> which PINs look like places that already have organised stores, tested on states the model never saw.</p><p><b>Cannot say:</b> sales potential or whether a store would be profitable. The model learns where stores are today, not where they succeed, and it has not yet been tested on stores that opened later.</p></div>
          <p class="nxNote">${esc(m.method)} The target is "${esc(m.target)}". A gap means no organised store within 3 km, measured from where people live. Stores are counted from the listed universe only, and some stores are placed at PIN or city centres, so check a gap on the ground before acting; dense metro PINs need the most care.</p>
        </div>`;
      wireClose();
      drawer.querySelectorAll(".nxList li").forEach((li) => {
        const go = () => focusPin(li.dataset.pin, li.dataset.did);
        li.onclick = go; li.onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } };
      });
      const c = $("#nxCsv"); if (c) c.onclick = () => download(`terrain-gaps-${slug(sc.label)}.csv`, toCSV(rows));
      const b = $("#nxIndia"); if (b) b.onclick = toIndia;
    }
    async function focusPin(pin, did) {
      if (String(S().district) !== String(did)) { await T.selectDistrict(did); await new Promise((r) => setTimeout(r, 700)); }
      await showPins(S().state);
      const f = NX.pinFC && NX.pinFC.features.find((x) => x.properties.pincode === pin);
      if (!f) return;
      const bb = bbox(f.geometry);
      map.fitBounds(bb, { padding: 80, maxZoom: 12.5, duration: 900 });
      map.setFilter("nx-p-sel", ["==", ["get", "pincode"], pin]);
      NX.sel = pin;
    }
    function bbox(g) {
      let x0 = 180, y0 = 90, x1 = -180, y1 = -90;
      const walk = (c) => { if (typeof c[0] === "number") { x0 = Math.min(x0, c[0]); x1 = Math.max(x1, c[0]); y0 = Math.min(y0, c[1]); y1 = Math.max(y1, c[1]); } else c.forEach(walk); };
      walk(g.coordinates); return [[x0, y0], [x1, y1]];
    }
    function toCSV(rows) {
      const cols = ["pin", "office", "district", "state", "cls", "score", "aff_hh", "hh", "km_nearest_store"];
      const q = (v) => (v == null ? "" : /[",\n]/.test(String(v)) ? '"' + String(v).replace(/"/g, '""') + '"' : String(v));
      return [cols.join(",")].concat(rows.map((r) => cols.map((k) => q(r[k])).join(","))).join("\n") + "\n";
    }
    async function download(name, text) {
      try {
        const c = window.claude && window.claude.use ? await window.claude.use("downloads") : null;
        if (c) { await c.save({ filename: name, data: text }); return; }
      } catch (e) { if (e && e.code && e.code !== "unavailable") return; }
      const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([text], { type: "text/csv" })); a.download = name; document.body.appendChild(a); a.click(); a.remove();
    }

    // ---------------- today
    const primary = (flags) => flags.filter((f) => FLAG[f] && FLAG[f].color).sort((a, b) => FLAG[a].pri - FLAG[b].pri)[0];
    const TEMP = ["#2c7bb6", "#abd9e9", "#ffffbf", "#fdae61", "#f46d43", "#d73027", "#a50026"], TBR = [15, 22, 28, 33, 37, 41];
    const RAIN = ["#f1ede6", "#c6dbef", "#9ecae1", "#6baed6", "#3182bd", "#08519c"], RBR = [1, 10, 35, 65, 115];
    const pick = (v, br, pal) => { let i = 0; while (i < br.length && v >= br[i]) i++; return pal[i]; };
    function renderToday() {
      const w = NX.weather, D = w.districts, ids = Object.keys(D);
      const expr = ["match", ["get", "objectid"]];
      ids.forEach((k) => {
        const d = D[k]; let c = NONE;
        if (NX.wmetric === "alerts") { const p = primary(d.flags); c = p ? FLAG[p].color : NONE; }
        else if (NX.wmetric === "tmax") c = d.tx[0] == null ? NONE : pick(d.tx[0], TBR, TEMP);
        else c = pick((d.pr[0] || 0) + (d.pr[1] || 0) + (d.pr[2] || 0), RBR, RAIN);
        expr.push(Number(k), c);
      });
      expr.push(NONE);
      map.setPaintProperty("nx-d-fill", "fill-color", expr);
      vis(["nx-p-fill", "nx-p-line", "nx-p-gap", "nx-p-sel"], false); vis(["nx-d-fill", "nx-d-line"], true);
      legend.classList.remove("hidden");
      if (NX.wmetric === "alerts") {
        const on = Object.keys(FLAG).filter((f) => FLAG[f].color && w.counts[f]);
        legend.innerHTML = `<div class="t">Today's alerts <span class="nxTag directional">directional</span></div>` + (on.length ? on.map((f) => `<div class="row"><span class="sw" style="background:${FLAG[f].color}"></span>${FLAG[f].label}</div>`).join("") : "") + `<div class="row"><span class="sw" style="background:${NONE};border:1px solid #ddd"></span>No alert</div>`;
      } else if (NX.wmetric === "tmax") {
        legend.innerHTML = `<div class="t">Maximum temperature today, °C</div><div class="ramp">${TEMP.map((c) => `<span style="background:${c}"></span>`).join("")}</div><div class="ticks"><span>&lt;15</span><span>28</span><span>41+</span></div>`;
      } else {
        legend.innerHTML = `<div class="t">Rain over the next 3 days, mm</div><div class="ramp">${RAIN.map((c) => `<span style="background:${c}"></span>`).join("")}</div><div class="ticks"><span>0</span><span>35</span><span>115+</span></div>`;
      }
      const ist = new Date(w.built_utc).toLocaleString("en-IN", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", day: "numeric", month: "short" });
      const day = new Date(w.today + "T00:00:00+05:30").toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", timeZone: "Asia/Kolkata" });
      const groups = {};
      Object.keys(FLAG).forEach((f) => {
        const c = w.counts[f]; if (!c) return;
        const g = FLAG[f].group; groups[g] = groups[g] || { flags: [], hh: 0, aff: 0, ids: new Set() };
        groups[g].flags.push(f);
        ids.forEach((k) => { if (D[k].flags.includes(f) && !groups[g].ids.has(k)) { groups[g].ids.add(k); } });
      });
      const order = ["rain", "heat", "cold", "dry", "shift"];
      const META = NX.dmeta || {};
      const cards = order.filter((g) => groups[g]).map((g) => {
        const G = groups[g], arr = [...G.ids];
        const hh = arr.reduce((a, k) => a + ((META[k] && META[k].hh) || 0), 0);
        const top = arr.sort((a, b) => ((META[b] && META[b].hh) || 0) - ((META[a] && META[a].hh) || 0)).slice(0, 5);
        const title = G.flags.map((f) => FLAG[f].label).join(" · ");
        const col = FLAG[G.flags[0]].color || "#c9c4ba";
        return `<div class="nxCard"><div class="h"><span class="sw" style="background:${col}"></span>${esc(title)}<span class="c">${fmt(arr.length)} districts${hh ? " · " + size(hh) + " homes" : ""}</span></div><p>${PLAY[g]}</p><div class="places">${top.map((k) => `<button data-did="${k}">${esc((META[k] && META[k].n) || k)}</button>`).join(", ")}</div></div>`;
      }).join("");
      const sel = S().district != null && D[String(S().district)] ? String(S().district) : null;
      const headline = (() => {
        const bits = [];
        const tot = (g) => groups[g] ? groups[g].ids.size : 0;
        if (tot("rain")) bits.push(`rain alerts in ${fmt(tot("rain"))} districts`);
        if (tot("heat")) bits.push(`heat in ${fmt(tot("heat"))}`);
        if (tot("cold")) bits.push(`cold in ${fmt(tot("cold"))}`);
        if (tot("dry")) bits.push(`a dry, mild week in ${fmt(tot("dry"))}`);
        return bits.length ? "Across India today: " + bits.join(", ") + "." : "No weather alerts across India today.";
      })();
      drawer.innerHTML = `<div class="nxHead"><div class="nxKick">Today · ${esc(day)}</div><h2>${esc(headline)}</h2><button class="nxX" aria-label="Close">×</button></div>
        <div class="nxBody">
          <div class="nxSeg" role="group" aria-label="Colour the map by">${[["alerts", "Alerts"], ["tmax", "Max °C"], ["rain", "Rain, 3 days"]].map(([k, l]) => `<button data-m="${k}" aria-pressed="${NX.wmetric === k}">${l}</button>`).join("")}</div>
          ${sel ? districtWeek(sel) : `<p class="nxNote" style="margin-top:0">Click any district for its 7-day outlook.</p>`}
          <h3>Today's playbook <span class="nxTag rule">rule-based</span></h3>
          ${cards || `<p class="nxNote">Nothing unusual anywhere today.</p>`}
          <p class="nxNote">Forecast for each district's centre from Open-Meteo, refreshed every morning (last update ${esc(ist)} IST). Alerts use stated thresholds: IMD rain categories (64.5, 115.6 and 204.5 mm a day), heat at 40 °C (45 °C extreme; 30 °C plus a 4.5 °C jump in hills), cold at a 10 °C minimum, feels-like 41 °C for humid heat, and seven days under 2 mm at 12 to 35 °C for the dry window. Planning signals, not official warnings; suggestions are rules, not a demand forecast.</p>
        </div>`;
      wireClose();
      drawer.querySelectorAll(".nxSeg button").forEach((b) => (b.onclick = () => { NX.wmetric = b.dataset.m; renderToday(); }));
      drawer.querySelectorAll(".places button").forEach((b) => (b.onclick = () => T.selectDistrict(b.dataset.did)));
    }
    function districtWeek(k) {
      const d = NX.weather.districts[k], M = (NX.dmeta || {})[k] || {};
      const days = NX.weather.days.map((x) => new Date(x + "T00:00:00+05:30").toLocaleDateString("en-IN", { weekday: "short", timeZone: "Asia/Kolkata" }));
      const row = (l, a, f) => `<tr><td class="l">${l}</td>${a.map((v) => `<td>${v == null ? "n/a" : f(v)}</td>`).join("")}</tr>`;
      const flags = d.flags.map((f) => FLAG[f] ? FLAG[f].label : f);
      return `<h3>${esc(M.n || "This district")}, next 7 days</h3>
        <table class="nxWeek"><tr><th></th>${days.map((x) => `<th>${x}</th>`).join("")}</tr>
        ${row("Max °C", d.tx, (v) => Math.round(v))}${row("Min °C", d.tn, (v) => Math.round(v))}${row("Feels", d.at, (v) => Math.round(v))}${row("Rain mm", d.pr, (v) => (v < 1 ? "0" : Math.round(v)))}${row("Chance", d.pp, (v) => v + "%")}</table>
        <p class="nxNote">${flags.length ? "Signals: " + esc(flags.join(", ")) + "." : "No alert signals."} Last 7 days: ${fmt(d.pr7_past)} mm of rain; next 7 days: ${fmt(d.pr7_next)} mm${d.pr7_norm != null ? " against a normal of about " + fmt(d.pr7_norm) + " mm" : ""}.${M.hh ? " " + size(M.hh) + " households." : ""}</p>`;
    }
    getJSON("data/next/today/district_meta.json").then((m) => (NX.dmeta = m)).catch(() => {});
    // ---------------- Pulse: national brand attention and voice, local category demand
    const ctxIx = (k) => NX.pctx.fields.findIndex((f) => f[0] === k);
    function ctxVal(id, k) {
      const r = NX.pctx.d[id]; if (!r) return null;
      if (k === "unserved") { const q = r[ctxIx("qc")]; return q ? 0 : r[ctxIx("aff")]; }
      return r[ctxIx(k)];
    }
    function ctxLabel(k) { return k === "unserved" ? "Upper-wealth households in districts with no dark store" : NX.pctx.fields[ctxIx(k)][1]; }
    function ctxFmt(k, v) {
      if (v == null) return "n/a";
      const u = k === "unserved" ? "count" : NX.pctx.fields[ctxIx(k)][2];
      return u === "count" ? size(v) : u === "share" ? (Math.abs(v) < 0.1 ? fmt(100 * v, 1) + "%" : pct(v)) : u === "months" ? fmt(v) + " months" : fmt(v, v < 10 ? 1 : 0);
    }
    const sortedCache = {};
    function ctxSorted(k) { return (sortedCache[k] = sortedCache[k] || Object.keys(NX.pctx.d).map((id) => ctxVal(id, k)).filter((v) => v != null && v > 0).sort((a, b) => a - b)); }
    function ctxRank(k, v) { const a = ctxSorted(k); if (v == null || v <= 0 || !a.length) return null; let lo = 0; while (lo < a.length && a[lo] <= v) lo++; return Math.max(1, Math.round(100 * (1 - lo / a.length)) || 1); }
    function ctxBreaks(k) { const a = ctxSorted(k), q = (p) => a[Math.min(a.length - 1, Math.floor(p * a.length))]; return [q(0.2), q(0.4), q(0.6), q(0.8), q(0.95)]; }
    function renderPulse() {
      const P = NX.pulse, cats = Object.keys(P.categories);
      if (!P.categories[NX.pcat]) NX.pcat = cats[0];
      const C = P.categories[NX.pcat], cfg = PCAT[NX.pcat] || { m: [] };
      const mk2 = NX.pmetric[NX.pcat] || (cfg.m[0] && cfg.m[0][0]);
      // map
      if (mk2) {
        const br = ctxBreaks(mk2), expr = ["match", ["get", "objectid"]];
        Object.keys(NX.pctx.d).forEach((id) => { const v = ctxVal(id, mk2); expr.push(Number(id), v == null || v <= 0 ? NONE : pick(v, br, PRAMP)); });
        expr.push(NONE);
        map.setPaintProperty("nx-d-fill", "fill-color", expr);
        vis(["nx-p-fill", "nx-p-line", "nx-p-gap", "nx-p-sel"], false); vis(["nx-d-fill", "nx-d-line"], true);
        legend.classList.remove("hidden");
        legend.innerHTML = `<div class="t">${esc(ctxLabel(mk2))}</div><div class="ramp">${PRAMP.map((c) => `<span style="background:${c}"></span>`).join("")}</div><div class="ticks"><span>${ctxFmt(mk2, br[0])}</span><span>${ctxFmt(mk2, br[2])}</span><span>${ctxFmt(mk2, br[4])}+</span></div><div class="row"><span class="sw" style="background:${NONE};border:1px solid #ddd"></span>${mk2 === "unserved" ? "Has a dark store, or no data" : mk2 === "qc" ? "No dark store" : "No data"}</div>`;
      }
      // brand rows
      const B = C.brands, names = Object.keys(B).sort((a, b) => (B[b].earned_share || 0) - (B[a].earned_share || 0));
      const maxS = Math.max(...names.map((n) => B[n].earned_share || 0), 0.01);
      const voiceCell = (b) => {
        const c = b.consumer;
        if (c.net == null) return `<span class="pv mut" title="${c.n} consumer ${c.n === 1 ? "comment" : "comments"} in the labelled sample; ${NX.pulse.method.min_read} or more are needed to read a tone">Too few to read</span>`;
        const n = Math.round(100 * c.net), cls = n > 10 ? "pos" : n < -10 ? "neg" : "mid";
        return `<span class="pv ${cls}" title="Of ${c.n} consumer comments: ${c.pos} positive, ${c.neg} negative, ${c.n - c.pos - c.neg} neutral or questions">${n > 0 ? "+" : ""}${n} <span class="mut">net · ${c.n} read</span></span>`;
      };
      const rows = names.map((n) => {
        const b = B[n], open = NX.popen === n;
        const worry = b.worry || (b.consumer.neg_themes[0] && b.consumer.n >= 4 && b.consumer.neg_themes[0][0] !== "brand and other" ? b.consumer.neg_themes[0][0] : "");
        return `<li class="pRow${open ? " open" : ""}" data-b="${esc(n)}" tabindex="0" role="button" aria-expanded="${open}">
          <div class="pTop"><span class="pN">${esc(n)}</span>${voiceCell(b)}</div>
          <div class="pBar" title="${pct(b.earned_share)} of independent views in this category: ${size(b.earned_views)} views on ${b.videos} videos from channels other than the brand's own"><span style="width:${Math.max(2, 100 * (b.earned_share || 0) / maxS)}%"></span><em>${b.earned_share != null && b.earned_share < 0.01 ? "&lt;1%" : pct(b.earned_share)}</em></div>
          ${worry ? `<div class="pW">Main worry: ${esc(worry)}</div>` : ""}
          ${open ? brandDetail(n, b) : ""}</li>`;
      }).join("");
      // local context
      const sel = S().district != null && NX.pctx.d[String(S().district)] ? String(S().district) : null;
      const top = Object.keys(NX.pctx.d).map((id) => [id, ctxVal(id, mk2)]).filter((x) => x[1] > 0).sort((a, b) => b[1] - a[1]).slice(0, 6);
      const M = NX.dmeta || {};
      const local = sel ? localCard(sel, cfg) : `<p class="nxNote" style="margin-top:0">Click a district to see this category's numbers there.</p>`;
      const fetched = new Date(P.fetched_utc).toLocaleDateString("en-IN", { day: "numeric", month: "short", timeZone: "Asia/Kolkata" });
      drawer.innerHTML = `<div class="nxHead"><div class="nxKick">Pulse · YouTube, ${P.days} days to ${esc(fetched)}</div><h2>${esc(C.head || NX.pcat)}</h2><button class="nxX" aria-label="Close">×</button></div>
        <div class="nxBody">
          <div class="nxSeg" role="group" aria-label="Category">${cats.map((k) => `<button data-c="${esc(k)}" aria-pressed="${k === NX.pcat}">${esc(k)}</button>`).join("")}</div>
          <p class="pRead">${esc(C.read)}</p>
          <h3>Brands <span class="nxTag directional" title="National only. Samples are small and comment sections lean toward reviews and complaints: read the direction, not the decimal.">directional</span></h3>
          <div class="pKey"><span>Share of independent views</span><span>Consumer tone</span></div>
          <ul class="pList">${rows}</ul>
          <p class="nxNote" style="margin-top:4px">Tap a brand for what people say, who is saying it and the source videos.</p>
          <h3>Where this category's demand sits <span class="nxTag rule">TERRAIN data</span></h3>
          <p class="nxNote" style="margin-top:0">${esc(cfg.why)}</p>
          <div class="nxSeg" role="group" aria-label="Colour the map by">${cfg.m.map(([k, l]) => `<button data-m="${k}" aria-pressed="${k === mk2}">${esc(l)}</button>`).join("")}</div>
          ${local}
          <ol class="nxList">${top.map(([id, v], i) => `<li data-did="${id}" tabindex="0"><span class="r">${i + 1}</span><span class="m"><span class="t">${esc((M[id] && M[id].n) || districtName(id) || id)}</span> <span class="s">${esc((M[id] && M[id].s) || "")}</span></span><span class="v">${ctxFmt(mk2, v)}</span></li>`).join("")}</ol>
          <div class="nxBound"><p><b>Can say:</b> which brands draw independent attention on YouTube this month, who is talking and what they praise or complain about, nationally.</p><p><b>Cannot say:</b> market share, sales, or how any district or state feels. YouTube comments carry no location, samples are small, and comment sections lean toward reviews and complaints.</p></div>
          <p class="nxNote">${esc(P.source)} Comments were read in the original language (Hindi, Hinglish, Tamil, Telugu, Kannada, Malayalam, Bengali) and labelled by hand for who is speaking, tone and topic; quotes are English paraphrases. Views on a brand's own channel count as owned, everything else as independent. YouTube comments carry no location, so brand reads are national; the map is TERRAIN's district data. Labelled ${esc(P.labelled)}.</p>
        </div>`;
      wireClose();
      drawer.querySelectorAll(".nxSeg button[data-c]").forEach((b) => (b.onclick = () => { NX.pcat = b.dataset.c; NX.popen = null; renderPulse(); }));
      drawer.querySelectorAll(".nxSeg button[data-m]").forEach((b) => (b.onclick = () => { NX.pmetric[NX.pcat] = b.dataset.m; renderPulse(); }));
      drawer.querySelectorAll(".pRow").forEach((li) => {
        const go = (e) => { if (e.target.closest("a")) return; NX.popen = NX.popen === li.dataset.b ? null : li.dataset.b; renderPulse(); const el = drawer.querySelector(`.pRow[data-b="${CSS.escape(li.dataset.b)}"]`); if (el && el.scrollIntoView) el.scrollIntoView({ block: "nearest" }); };
        li.onclick = go; li.onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(e); } };
      });
      drawer.querySelectorAll(".nxList li[data-did]").forEach((li) => { li.onclick = () => T.selectDistrict(li.dataset.did); li.onkeydown = (e) => { if (e.key === "Enter") T.selectDistrict(li.dataset.did); }; });
    }
    function brandDetail(n, b) {
      const v = b.voice, tot = Object.values(v).reduce((a, x) => a + x, 0);
      const VC = { consumers: "#756bb1", trade: "#e8892b", investors: "#4f8fd6", "ad and content reactions": "#9e9ac8" };
      const mix = tot ? `<div class="pMix" title="Who is talking, among ${tot} relevant comments of ${b.labelled} read">${Object.keys(v).filter((k) => v[k]).map((k) => `<span style="flex:${v[k]};background:${VC[k]}" title="${esc(k)}: ${v[k]}"></span>`).join("")}</div><div class="pMixK">${Object.keys(v).filter((k) => v[k]).map((k) => `<span><i style="background:${VC[k]}"></i>${esc(k)} ${v[k]}</span>`).join("")}</div>` : `<p class="nxNote">None of the ${b.labelled} comments read were about the brand.</p>`;
      const q = (b.quotes || []).map((x) => `<blockquote class="${x.s === "+" ? "pos" : x.s === "-" ? "neg" : ""}">“${esc(x.text)}”<cite>${esc(VOICE[x.voice] || "")} · <a href="https://www.youtube.com/watch?v=${encodeURIComponent(x.v)}" target="_blank" rel="noopener noreferrer">source video</a></cite></blockquote>`).join("");
      const conc = b.top1_share != null && b.top1_share >= 0.5 ? ` One video is ${pct(b.top1_share)} of these.` : "";
      const owned = b.owned_views ? `${size(b.owned_views)} views on its own channel; ` : "";
      const topv = (b.top_earned || [])[0];
      return `<div class="pDet">
        <p>${esc(b.read)}</p>
        ${q}
        <div class="pSub">Who is talking</div>${mix}
        <p class="nxNote">${owned}${size(b.earned_views)} independent views on ${b.videos} videos.${conc}${topv ? ` Most watched independent video: <a href="https://www.youtube.com/watch?v=${encodeURIComponent(topv.id)}" target="_blank" rel="noopener noreferrer">${esc(topv.title)}</a> (${esc(topv.channel)}, ${size(topv.views)} views).` : ""}</p>
      </div>`;
    }
    function localCard(id, cfg) {
      const M = (NX.dmeta || {})[id] || {};
      const rowsFor = { "Paints": ["bld", "rera", "aff", "pmo"], "Two-wheelers": ["v2w", "v2wy", "ev", "hh"], "Quick commerce": ["qc", "qcp", "aff", "hh"] }[NX.pcat] || [];
      const line = (k) => { const v = ctxVal(id, k), r = ["v2wy"].includes(k) ? null : ctxRank(k, v); return `<tr><td class="l">${esc(ctxLabel(k))}</td><td class="n">${ctxFmt(k, v)}${r ? `<span class="mut"> · top ${r}%</span>` : ""}</td></tr>`; };
      let extra = "";
      if (NX.pcat === "Paints" && NX.weather && NX.weather.districts[id] && NX.weather.districts[id].flags.includes("dry_window")) extra = `<p class="nxNote">Today: seven dry, mild days ahead here, a good window for exterior painting.</p>`;
      if (NX.pcat === "Quick commerce" && !ctxVal(id, "qc") && ctxVal(id, "aff") > 0) extra = `<p class="nxNote">No dark store recorded here in March 2026, against ${size(ctxVal(id, "aff"))} upper-wealth households. Other explanations: the store list may be incomplete, or orders may be served from a store across the district line. Next check: the platforms' own delivery coverage for a few PIN codes here.</p>`;
      return `<div class="pLocal"><div class="pSub">${esc(M.n || districtName(id) || "This district")}${M.s ? `, ${esc(M.s)}` : ""}</div><table class="pT">${rowsFor.map(line).join("")}</table>${extra}</div>`;
    }


    // ---------------- hover and tap cards for add-on layers
    function place(e) {
      const r = centre.getBoundingClientRect(), x = e.point.x + 14, y = e.point.y + 14;
      tip.style.left = Math.min(x, r.width - 300) + "px"; tip.style.top = Math.min(y, r.height - 160) + "px";
    }
    function pinCard(p) {
      const k = NX.pinClass[p.pincode]; if (!k) return `<b>PIN ${esc(p.pincode)}</b><br><span class="mut">Not graded</span>`;
      const why = (k[5] || []).map(([c, v]) => `${esc(NX.meta.why_codes[c])} (top ${100 - v + 1}%)`).join(", ");
      return `<b>PIN ${esc(p.pincode)}</b><div class="big">${CLASS[k[0]].name}</div><span class="mut">Readiness ${k[1]} of 100 · ${k[2] === 2 ? fmt(k[3]) + " organised " + (k[3] === 1 ? "store" : "stores") + " in this PIN" : esc(SVC[k[2]]) + (k[4] != null ? "; homes here are " + fmt(k[4], 1) + " km from one on average" : "")}</span>${why ? `<br>Stands out on: ${why}` : ""}<div class="act">${esc(NX.meta.formats[k[0]])}</div>`;
    }
    function districtCard(id) {
      if (NX.mode === "class") {
        const d = NX.dclass[id]; const n = districtName(id) || "District";
        if (!d) return `<b>${esc(n)}</b>`;
        return `<b>${esc(n)}</b><div class="big">${size(d.uab_aff)}</div><span class="mut">upper-wealth households in ${fmt(d.ua + d.ub)} gap ${d.ua + d.ub === 1 ? "PIN" : "PINs"} (Class A ${fmt(d.ua)}, B ${fmt(d.ub)})</span><br>Class A PINs: ${fmt(d.a)} · B: ${fmt(d.b)}<div class="act">Click to see every PIN here graded A to D</div>`;
      }
      if (NX.mode === "pulse") {
        const M = (NX.dmeta || {})[id] || {}, k = NX.pmetric[NX.pcat] || PCAT[NX.pcat].m[0][0], v = ctxVal(id, k), r = ctxRank(k, v);
        return `<b>${esc(M.n || districtName(id) || "District")}</b>${M.s ? `<span class="mut"> · ${esc(M.s)}</span>` : ""}<div class="big">${ctxFmt(k, v)}</div><span class="mut">${esc(ctxLabel(k))}${r ? ` · top ${r}% of districts` : ""}</span><div class="act">Click for this district's ${esc(NX.pcat.toLowerCase())} numbers</div>`;
      }
      const d = NX.weather.districts[id], M = (NX.dmeta || {})[id] || {}; if (!d) return "";
      const p = primary(d.flags);
      return `<b>${esc(M.n || districtName(id) || "District")}</b>${M.s ? `<span class="mut"> · ${esc(M.s)}</span>` : ""}<div class="big">${d.tx[0] == null ? "n/a" : Math.round(d.tx[0]) + "°"} <span class="mut" style="font-size:12px;font-weight:400">/ ${d.tn[0] == null ? "n/a" : Math.round(d.tn[0]) + "°"} · feels ${d.at[0] == null ? "n/a" : Math.round(d.at[0]) + "°"}</span></div>Rain next 3 days: ${fmt((d.pr[0] || 0) + (d.pr[1] || 0) + (d.pr[2] || 0))} mm${p ? `<br><b>${esc(FLAG[p].label)}</b>` : ""}<div class="act">Click for the 7-day outlook and what to do</div>`;
    }
    const coarse = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;
    map.on("mousemove", "nx-p-fill", (e) => { if (coarse || NX.mode !== "class") return; tip.innerHTML = pinCard(e.features[0].properties); tip.classList.remove("hidden"); place(e); });
    map.on("mousemove", "nx-d-fill", (e) => { if (coarse || !NX.mode) return; const id = String(e.features[0].properties.objectid); const h = districtCard(id); if (!h) return; tip.innerHTML = h; tip.classList.remove("hidden"); place(e); });
    ["nx-p-fill", "nx-d-fill"].forEach((l) => map.on("mouseleave", l, () => tip.classList.add("hidden")));
    map.on("click", "nx-p-fill", (e) => {
      if (NX.mode !== "class") return;
      const p = e.features[0].properties; map.setFilter("nx-p-sel", ["==", ["get", "pincode"], p.pincode]);
      if (coarse) { tip.innerHTML = pinCard(p); tip.style.left = "12px"; tip.style.top = "12px"; tip.classList.remove("hidden"); setTimeout(() => tip.classList.add("hidden"), 6000); }
    });

    // ---------------- zoom: suggestions to drill in or out, keyboard focus, touch hint
    const canvas = map.getCanvas(); canvas.setAttribute("tabindex", "0"); canvas.setAttribute("aria-label", "Map of India. Use plus and minus to zoom, arrow keys to move.");
    if (map.keyboard && map.keyboard.enable) map.keyboard.enable();
    if (map.touchZoomRotate && map.touchZoomRotate.enable) { map.touchZoomRotate.enable(); map.touchZoomRotate.disableRotation(); }
    if (map.doubleClickZoom && map.doubleClickZoom.enable) map.doubleClickZoom.enable();
    function suggest(key, text, label, act) {
      if (NX.chipKey === key && !chip.classList.contains("hidden")) return;
      if (!key.startsWith("pick-") && store.get("nx-chip-off-" + key)) return;
      NX.chipKey = key;
      chip.innerHTML = `<span>${esc(text)}</span><button class="go" type="button">${esc(label)}</button><button class="no" type="button" aria-label="Dismiss">×</button>`;
      chip.classList.remove("hidden");
      chip.querySelector(".go").onclick = () => { chip.classList.add("hidden"); act(); };
      chip.querySelector(".no").onclick = () => { chip.classList.add("hidden"); store.set("nx-chip-off-" + key, "1"); };
    }
    map.on("moveend", (e) => {
      if (!e.originalEvent) return; // only react to the user's own zooming and panning
      const s = S(), z = map.getZoom(), c = map.project(map.getCenter());
      const under = map.queryRenderedFeatures([[c.x - 2, c.y - 2], [c.x + 2, c.y + 2]], { layers: ["d-fill", "nx-d-fill"].filter((l) => map.getLayer(l) && map.getLayoutProperty(l, "visibility") !== "none") })[0];
      const did = under && under.properties.objectid, dn = under && under.properties.district;
      if ((s.level === "national" || s.level === "state") && z >= 6.4 && did != null && String(did) !== String(s.district)) return suggest("in-d-" + did, `Zoomed in on ${dn}.`, "Open district", () => T.selectDistrict(did));
      if (s.level === "district" && z >= 9.6) return suggest("in-pin", "Close enough for PIN codes.", "Show PIN codes", () => T.setLevel("pin"));
      if ((s.level === "district" || s.level === "micro" || s.level === "pin") && z <= 5.2) return suggest("out-india", "Zoomed out to the country.", "Back to India", toIndia);
      chip.classList.add("hidden");
    });
    if (coarse && !store.get("nx-hint-touch")) {
      hint.innerHTML = "Pinch to zoom · drag to move · double-tap to zoom in · tap a place to see it";
      hint.classList.remove("hidden");
      const off = () => { hint.classList.add("hidden"); store.set("nx-hint-touch", "1"); };
      setTimeout(off, 6000); map.once("touchstart", () => setTimeout(off, 1500));
    }
    window.addEventListener("terrain:picked", (ev) => {
      const nm = (ev.detail && ev.detail.name) || "this place";
      suggest("pick-" + Date.now(), `Selected ${nm}.`, "See details", () => T.showPane && T.showPane("right"));
    });
    window.TERRAIN_NEXT = { setMode, refresh, state: NX };
  });
})();
