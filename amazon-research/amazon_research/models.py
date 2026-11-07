from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import re
from urllib.parse import urljoin, urlsplit

SEARCH_FIELDS = ["asin", "title", "brand_guess", "price_inr", "mrp_inr", "discount_pct", "rating", "review_count", "sponsored", "page", "position", "url"]
REVIEW_FIELDS = ["review_id", "asin", "product_name", "rating", "title", "body", "author", "review_date", "verified", "helpful_votes", "scraped_at"]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def valid_asin(value):
    value = str(value).strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{10}", value):
        raise ValueError(f"Invalid ASIN: {value!r}; expected ten letters/digits")
    return value


def amazon_url(value):
    """Allow only the intended marketplace, including redirects and next links."""
    value = urljoin("https://www.amazon.in/", value)
    parsed = urlsplit(value)
    if parsed.scheme != "https" or parsed.hostname not in {"www.amazon.in", "amazon.in"} or parsed.username or parsed.password or parsed.port not in {None, 443}:
        raise ValueError("Expected an HTTPS amazon.in URL")
    return value


@dataclass
class ProductCard:
    asin: str
    title: str
    brand_guess: str | None
    price_inr: float | None
    mrp_inr: float | None
    discount_pct: float | None
    rating: float | None
    review_count: int | None
    sponsored: bool | None
    page: int
    position: int
    url: str

    def as_dict(self):
        return asdict(self)


@dataclass
class Review:
    review_id: str
    asin: str
    product_name: str
    rating: float | None
    title: str
    body: str
    author: str
    review_date: str | None
    verified: int | None
    helpful_votes: int | None
    scraped_at: str
    review_date_raw: str = ""
    country: str | None = None
    variant: str | None = None

    def as_dict(self):
        return {k: getattr(self, k) for k in REVIEW_FIELDS}


class AccessProblem(RuntimeError):
    def __init__(self, status, message, http_status=None):
        super().__init__(message)
        self.status = status
        self.http_status = http_status
