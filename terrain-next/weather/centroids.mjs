import fs from 'fs';
import * as topo from 'topojson-client';
import * as d3 from 'd3';
const D = process.argv[2], OUT = process.argv[3];
const t = JSON.parse(fs.readFileSync(D + '/districts.topo.json'));
const name = Object.keys(t.objects)[0];
const fc = topo.feature(t, t.objects[name]);
const props0 = fc.features[0].properties; console.error('object', name, 'props', JSON.stringify(props0).slice(0, 200), 'n', fc.features.length);
const out = {};
for (const f of fc.features) {
  const p = f.properties || {}; const id = String(p.objectid ?? p.OBJECTID ?? p.id ?? f.id);
  // largest polygon centroid, so island chains and exclaves do not pull the point into the sea
  let geom = f.geometry; let best = geom;
  if (geom.type === 'MultiPolygon') { let a = -1; for (const poly of geom.coordinates) { const g = { type: 'Polygon', coordinates: poly }; const ar = d3.geoArea(g); if (ar > a) { a = ar; best = g; } } }
  let c = d3.geoCentroid(best);
  if (!d3.geoContains(best, c)) { const b = d3.geoBounds(best); c = [(b[0][0] + b[1][0]) / 2, (b[0][1] + b[1][1]) / 2]; }
  out[id] = [Math.round(c[0] * 1e4) / 1e4, Math.round(c[1] * 1e4) / 1e4];
}
fs.writeFileSync(OUT, JSON.stringify(out));
console.error('wrote', Object.keys(out).length);
