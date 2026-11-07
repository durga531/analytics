/* All extraction is local and runs only when the user clicks Export. */
function capturePage() {
  if (!['amazon.in', 'www.amazon.in'].includes(location.hostname) || location.protocol !== 'https:') {
    throw new Error('Open a normal https://www.amazon.in page first.');
  }
  if (document.querySelector('#ap_email, #ap_password, #captchacharacters, #auth-mfa-otpcode') || location.pathname.includes('/ap/')) {
    throw new Error('This is a sign-in or challenge page. Open an accessible product or search page.');
  }
  const searchCards = [...document.querySelectorAll('[data-component-type="s-search-result"][data-asin]')];
  const reviewCards = [...document.querySelectorAll('[data-hook="review"]')];
  const isSearch = location.pathname === '/s' && searchCards.length > 0;
  const cards = isSearch ? searchCards : reviewCards;
  const asinMatch = location.pathname.match(/\/(?:dp|product-reviews|gp\/product)\/([A-Z0-9]{10})(?:\/|$)/i);
  const asin = asinMatch ? asinMatch[1].toUpperCase() : null;
  const isProductPage = !isSearch && !!asin && /\/(?:dp|gp\/product)\//i.test(location.pathname);
  if (!cards.length && !isProductPage) throw new Error('No supported product/review cards are loaded on this page.');
  if (!isSearch && !asin) throw new Error('Cannot identify the ASIN from this URL.');
  // Product summary: the facts Amazon shows for all buyers, not just the loaded reviews. Text only; parsed in Python.
  const squash = (t) => (t || '').replace(/\s+/g, ' ').trim();
  const first = (selectors, attr) => {
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      const value = el && squash(attr ? el.getAttribute(attr) : el.textContent);
      if (value) return value;
    }
    return null;
  };
  // Shortest element whose whole text matches, so a phrase split across tags ("1K+ bought" + "in past month") is found.
  const findText = (re) => {
    let best = null;
    for (const el of document.querySelectorAll('span, div, a, p')) {
      const value = squash(el.textContent);
      if (value.length < 100 && re.test(value) && (!best || value.length < best.length)) best = value;
    }
    return best;
  };
  const product = isProductPage ? (() => {
    const histRoot = document.querySelector('#histogramTable, #cm_cr_dp_d_rating_histogram, [data-hook="cr-histogram"]');
    const histogram = histRoot ? [...histRoot.querySelectorAll('li, tr, a, [aria-label]')].map(el => squash((el.getAttribute('aria-label') || '') + ' ' + el.textContent)).filter(t => /[1-5]\s*star/i.test(t) && /\d\s*(?:%|percent)/i.test(t)).slice(0, 20) : [];
    const aspects = [...document.querySelectorAll('[data-hook="cr-insights-widget-aspects"] [aria-label], #cr-product-insights-cards [aria-label], [data-hook="cr-insights-aspect"]')].map(el => squash(el.getAttribute('aria-label') || el.textContent)).filter(Boolean).slice(0, 30);
    const out = {
      title: first(['#productTitle']),
      byline: first(['#bylineInfo']),
      rating_text: first(['#acrPopover .a-icon-alt', '[data-hook="rating-out-of-text"]', '#averageCustomerReviews .a-icon-alt']) || first(['#acrPopover'], 'title'),
      ratings_count_text: first(['#acrCustomerReviewText', '[data-hook="total-review-count"]']),
      histogram_text: histogram,
      price_text: first(['#corePriceDisplay_desktop_feature_div .priceToPay .a-offscreen', '#corePriceDisplay_desktop_feature_div .a-price .a-offscreen', '#corePrice_feature_div .a-price .a-offscreen', '#apex_desktop .a-price .a-offscreen', '.priceToPay .a-offscreen']),
      mrp_text: first(['#corePriceDisplay_desktop_feature_div .basisPrice .a-offscreen', '.basisPrice .a-offscreen', '#apex_desktop .a-text-price .a-offscreen']),
      bought_text: findText(/bought in (?:the )?past month/i),
      customers_say: first(['[data-hook="cr-insights-widget-summary"]', '#product-summary p', '[data-hook="cr-product-insights-summary"]']),
      aspects
    };
    out.fields_found = Object.keys(out).filter(k => Array.isArray(out[k]) ? out[k].length : out[k]);
    return out;
  })() : null;
  const cleanNode = (node) => {
    const clone = node.cloneNode(true);
    clone.querySelectorAll('script,style,form,input,textarea,iframe,object,embed').forEach(el => el.remove());
    for (const el of [clone, ...clone.querySelectorAll('*')]) {
      for (const attribute of [...el.attributes]) {
        if (/^on/i.test(attribute.name) || attribute.name === 'src' || attribute.name === 'srcset') el.removeAttribute(attribute.name);
      }
      if (el.hasAttribute('href')) {
        try {
          const link = new URL(el.getAttribute('href'), location.origin);
          el.setAttribute('href', link.origin + link.pathname + link.search);
        } catch { el.removeAttribute('href'); }
      }
    }
    return clone.outerHTML;
  };
  const title = document.querySelector('#productTitle');
  // No account header, addresses, cookies, session storage, or full-page HTML.
  const safeUrl = new URL(location.origin + location.pathname);
  for (const key of ['k', 'page', 'pageNumber', 'sortBy']) {
    if (new URL(location.href).searchParams.has(key)) safeUrl.searchParams.set(key, new URL(location.href).searchParams.get(key));
  }
  return {
    format: 'amazon-research-capture-v2',
    kind: isSearch ? 'search' : cards.length ? 'reviews' : 'product',
    product,
    url: safeUrl.href,
    captured_at: new Date().toISOString(),
    query: new URL(location.href).searchParams.get('k'),
    asin,
    card_count: cards.length,
    scope: isSearch ? 'loaded_search_cards' : location.pathname.includes('/product-reviews/') ? 'manual_review_page_nonexhaustive' : 'featured_nonrepresentative',
    html: '<!doctype html><html><body>' + (title ? cleanNode(title) : '') + cards.map(cleanNode).join('\n') + '</body></html>'
  };
}

document.getElementById('capture').addEventListener('click', async () => {
  const status = document.getElementById('status');
  try {
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    if (!tab || typeof tab.id !== 'number') throw new Error('No active tab.');
    const [{result}] = await chrome.scripting.executeScript({target: {tabId: tab.id}, func: capturePage});
    if (!result) throw new Error('Page capture returned no data.');
    const blob = new Blob([JSON.stringify(result, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'amazon-' + (result.asin || 'search') + '-' + Date.now() + '.json';
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
    const found = result.product ? ' Product facts found: ' + result.product.fields_found.length + ' of 10.' : '';
    status.textContent = 'Exported ' + result.card_count + ' loaded cards.' + found + ' Import this JSON with amazon-research import-capture.';
  } catch (error) {
    status.textContent = String(error.message || error);
  }
});
