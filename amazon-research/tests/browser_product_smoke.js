// Real-browser check of the extension's capturePage() on a SYNTHETIC Amazon.in product page.
// Usage: node tests/browser_product_smoke.js browser_capture/popup.js /tmp/capture.json  (needs Node and Playwright)
const { chromium } = require('playwright');
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const fn = src.slice(src.indexOf('function capturePage()'), src.indexOf("document.getElementById('capture')"));
// SYNTHETIC page shaped like an Amazon.in product page; invented product and numbers.
const page = `<!doctype html><html><body>
<span id="productTitle"> Example Breezo 1200 mm BLDC Ceiling Fan </span>
<a id="bylineInfo">Visit the Breezo Store</a>
<div id="averageCustomerReviews"><span id="acrPopover" title="4.2 out of 5 stars"><i><span class="a-icon-alt">4.2 out of 5 stars</span></i></span>
<span id="acrCustomerReviewText">12,345 ratings</span></div>
<div id="corePriceDisplay_desktop_feature_div"><span class="a-price priceToPay"><span class="a-offscreen">₹2,499.00</span></span>
<span class="basisPrice">M.R.P.: <span class="a-price a-text-price"><span class="a-offscreen">₹3,990.00</span></span></span></div>
<div id="social-proofing-faceout-title-tk_bought"><span>1K+ bought</span> <span>in past month</span></div>

<ul id="histogramTable"><li><a aria-label="61 percent of reviews have 5 stars">5 star 61%</a></li><li><a aria-label="20 percent of reviews have 4 stars">4 star 20%</a></li>
<li><a>3 star 7%</a></li><li><a>2 star 4%</a></li><li><a>1 star 8%</a></li></ul>
<div data-hook="cr-insights-widget-summary"><p>Customers like the airflow; some mention remote problems.</p></div>
</body></html>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.route('https://www.amazon.in/**', r => r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: page }));
  await p.goto('https://www.amazon.in/dp/B0SYNTH001/ref=xyz?th=1');
  const res = await p.evaluate(`(${fn.trim()})()`);
  fs.writeFileSync(process.argv[3], JSON.stringify(res, null, 2));
  console.log(res.format, res.kind, res.asin, 'cards', res.card_count, 'found', res.product.fields_found.join(','));
  console.log(JSON.stringify(res.product.histogram_text));
  await b.close();
})();
