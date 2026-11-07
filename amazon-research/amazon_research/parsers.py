"""Pure HTML parsers: useful for HTTP, real browsers, and saved-page captures."""
import re
from datetime import datetime
from urllib.parse import parse_qs, urlsplit
from bs4 import BeautifulSoup
from .models import AccessProblem, ProductCard, Review, amazon_url, now, valid_asin


def text(node):
    return node.get_text(" ", strip=True) if node else ""


def soup_of(html):
    return BeautifulSoup(html, "html.parser")


def check_access(html, url="https://www.amazon.in/", status=200):
    if status in {401, 403, 407, 429, 503}:
        labels = {401: "login_required", 403: "access_denied", 407: "proxy_auth_required", 429: "rate_limited", 503: "service_unavailable"}
        raise AccessProblem(labels[status], f"Amazon returned HTTP {status}. Collection stopped; no automatic retry.", status)
    if status >= 400:
        raise AccessProblem("http_error", f"HTTP {status}", status)
    soup = soup_of(html)
    path = urlsplit(url).path.lower()
    page_text = text(soup).lower()
    title = text(soup.title).lower()
    if soup.select_one('form[action*="validateCaptcha"], input#captchacharacters, input[name="cvf_captcha_input"]') or "robot check" in title or "enter the characters you see below" in page_text:
        raise AccessProblem("captcha", "A CAPTCHA/robot check was returned. Stop and use normal browsing.")
    if "we limit review access" in page_text or "restore the full reviews experience" in page_text:
        raise AccessProblem("review_access_restricted", "The account's review access is restricted.")
    if "/ap/signin" in path or soup.select_one('form[name="signIn"], input#ap_email, input#ap_password'):
        raise AccessProblem("login_required", "A sign-in page was returned instead of review data. Use your own visible browser/session.")
    if soup.select_one('input#auth-mfa-otpcode') or "/ap/mfa" in path:
        raise AccessProblem("mfa_required", "MFA requires the account owner's interaction.")
    if "sorry, we just need to make sure you're not a robot" in page_text or "automated access to amazon data" in page_text or "access denied" in title:
        raise AccessProblem("access_denied", "An Amazon access/challenge page was returned.")
    return soup


def amount(value):
    match = re.search(r"(?<!\d)(\d[\d,]*(?:\.\d{1,2})?)", str(value).replace("\xa0", " "))
    return float(match.group(1).replace(",", "")) if match else None


def count(value):
    value = str(value).strip().lower()
    if value in {"one person found this helpful", "one person found this helpful.", "one"}:
        return 1
    # Use a labelled number where present; avoid interpreting a star rating as a count.
    match = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*(k|m|lakh|lac|crore)?", value)
    if not match:
        return None
    scale = {None: 1, "k": 1000, "m": 1000000, "lakh": 100000, "lac": 100000, "crore": 10000000}[match.group(2)]
    return int(float(match.group(1).replace(",", "")) * scale)


def stars(value):
    match = re.search(r"([0-5](?:[.,]\d+)?)\s*(?:out of 5|of 5|/5)", str(value), re.I)
    if not match:
        return None
    result = float(match.group(1).replace(",", "."))
    return result if 0 <= result <= 5 else None


def infer_brand(title):
    # Explicitly an inference; multiword brands can be supplied in brands.json.
    return title.split()[0].strip("®™:,-") if title.strip() else None


def parse_search(html, page=1, brands=None):
    soup = check_access(html)
    cards = soup.select('[data-component-type="s-search-result"][data-asin]')
    rows = []
    for position, card in enumerate(cards, 1):
        asin = card.get("data-asin", "").strip()
        if not re.fullmatch(r"[A-Za-z0-9]{10}", asin):
            continue
        heading = card.select_one("h2")
        name = (heading.get("aria-label") or text(heading)) if heading else ""
        if not name:
            continue
        price = amount(text(card.select_one('.a-price:not(.a-text-price) .a-offscreen')))
        if price is None:
            whole = text(card.select_one('.a-price:not(.a-text-price) .a-price-whole')).rstrip(".")
            fraction = text(card.select_one('.a-price:not(.a-text-price) .a-price-fraction'))
            price = amount(whole + ("." + fraction if fraction else ""))
        mrp = amount(text(card.select_one('.a-price.a-text-price .a-offscreen')))
        # Broken MRP remains visible; never turn it into a misleading discount.
        discount = round((mrp - price) / mrp * 100, 2) if mrp and price is not None and mrp >= price else None
        rating = stars(text(card.select_one('[data-cy="reviews-block"] .a-icon-alt, .a-icon-star-small .a-icon-alt, .a-icon-star .a-icon-alt')))
        review_count = None
        for link in card.select('a[href*="customerReviews"], a[href*="product-reviews"], a[aria-label]'):
            label = link.get("aria-label", "")
            if re.search(r"\b(ratings?|reviews?)\b", label, re.I) and "out of 5" not in label:
                review_count = count(label)
            elif "customerReviews" in link.get("href", "") or "product-reviews" in link.get("href", ""):
                candidate = text(link.select_one(".s-underline-text")) or text(link)
                if candidate and "out of 5" not in candidate:
                    review_count = count(candidate)
            if review_count is not None:
                break
        card_text = text(card)
        ad = card.select_one('[data-component-type="s-sponsored-label-info-icon"], .puis-sponsored-label-text, .s-sponsored-label-text, [data-sponsored="true"]')
        # Positive evidence => true. Absence does not prove an organic slot.
        sponsored = True if ad or re.search(r"\bSponsored\b", card_text, re.I) else None
        brand = infer_brand(name)
        for known in sorted(brands or [], key=len, reverse=True):
            if name.casefold().startswith(known.casefold() + " "):
                brand = known
                break
        rows.append(ProductCard(asin.upper(), name, brand, price, mrp, discount, rating, review_count, sponsored, page, position, f"https://www.amazon.in/dp/{asin.upper()}"))
    if not rows and not re.search(r"no results for|did not match any products|no results found", text(soup), re.I):
        raise AccessProblem("parse_empty", "No product cards matched. Possible changed markup, incomplete load, or an unrecognized access page.")
    return rows


def posted_date(raw):
    match = re.search(r"\bon\s+(\d{1,2}\s+\w+\s+\d{4}|\w+\s+\d{1,2},?\s+\d{4})", raw, re.I)
    if not match:
        return None
    value = match.group(1).replace(",", "")
    for fmt in ("%d %B %Y", "%B %d %Y", "%d %b %Y", "%b %d %Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def parse_reviews(html, asin, product_name=""):
    asin = valid_asin(asin)
    soup = check_access(html)
    product_name = product_name or text(soup.select_one('#productTitle, [data-hook="product-link"]'))
    rows = []
    seen = set()
    for node in soup.select('[data-hook="review"]'):
        review_id = node.get("id", "") or node.get("data-review-id", "")
        if not review_id:
            link = node.select_one('a[href*="/customer-reviews/"]')
            match = re.search(r"/customer-reviews/([A-Za-z0-9]+)", link.get("href", "")) if link else None
            review_id = match.group(1) if match else ""
        if not review_id or review_id in seen:
            continue
        seen.add(review_id)
        title_node = node.select_one('[data-hook="review-title"]')
        if title_node:
            title_node = soup_of(str(title_node))
            for icon in title_node.select('.a-icon-alt, i, [aria-hidden="true"]'):
                icon.decompose()
        title = text(title_node)
        body = text(node.select_one('[data-hook="review-body"]'))
        body = re.sub(r"\s*(Read more|Read less)\s*$", "", body, flags=re.I).strip()
        raw_date = text(node.select_one('[data-hook="review-date"]'))
        country_match = re.search(r"Reviewed in (.+?) on ", raw_date)
        rating = stars(text(node.select_one('[data-hook="review-star-rating"] .a-icon-alt, [data-hook="cmps-review-star-rating"] .a-icon-alt, [data-hook="review-star-rating"], [data-hook="cmps-review-star-rating"]')))
        helpful_node = node.select_one('[data-hook="helpful-vote-statement"]')
        helpful = count(text(helpful_node)) if helpful_node else None
        verified_node = node.select_one('[data-hook="avp-badge"]')
        # Missing badge = unknown; an absent badge is not proof of non-purchase.
        verified = 1 if verified_node and "verified purchase" in text(verified_node).lower() else None
        rows.append(Review(review_id, asin, product_name, rating, title, body, text(node.select_one('.a-profile-name')), posted_date(raw_date), verified, helpful, now(), raw_date, country_match.group(1) if country_match else None, text(node.select_one('[data-hook="format-strip"]')) or None))
    return rows


def next_page(html):
    soup = soup_of(html)
    link = soup.select_one('li.a-last:not(.a-disabled) a, a.s-pagination-next:not(.s-pagination-disabled)')
    if not link or not link.get("href"):
        return None
    return amazon_url(link["href"])


def page_number(url, default=1):
    query = parse_qs(urlsplit(url).query)
    try:
        return max(1, int((query.get("pageNumber") or query.get("page") or [default])[0]))
    except (ValueError, TypeError):
        return default


def parse_product_summary(product):
    """Normalize the product facts captured by the browser extension (text in, numbers out).
    Unknown stays None: a missing field is never read as zero."""
    product = product or {}
    histogram = {}
    for line in product.get("histogram_text") or []:
        m = re.search(r"([1-5])\s*stars?\b.*?(\d{1,3})\s*(?:%|percent)", line, re.I)
        if m:
            star, pct = m.group(1), m.group(2)
        else:
            m = re.search(r"(\d{1,3})\s*(?:%|percent).*?([1-5])\s*stars?\b", line, re.I)
            if not m:
                continue
            pct, star = m.group(1), m.group(2)
        if 0 <= int(pct) <= 100:
            histogram.setdefault(int(star), int(pct))
    bought = product.get("bought_text")
    bought_floor = count(bought.split("bought")[0]) if bought and "bought" in bought.lower() else None
    ratings = count(product.get("ratings_count_text") or "") if product.get("ratings_count_text") else None
    return {
        "title": product.get("title"),
        "byline": product.get("byline"),
        "rating": stars(product.get("rating_text") or ""),
        "ratings_count": ratings,
        "histogram": dict(sorted(histogram.items(), reverse=True)) or None,
        "price_inr": amount(product["price_text"]) if product.get("price_text") else None,
        "mrp_inr": amount(product["mrp_text"]) if product.get("mrp_text") else None,
        "bought_past_month_floor": bought_floor,
        "customers_say": product.get("customers_say"),
        "aspects": product.get("aspects") or [],
        "fields_found": product.get("fields_found") or [],
    }
