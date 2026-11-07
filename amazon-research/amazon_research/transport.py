"""Bounded sequential transports. Challenge pages terminate the run."""
from contextlib import ExitStack
import os
from pathlib import Path
import time
import httpx
from .models import AccessProblem, amazon_url
from .parsers import check_access


class Transport:
    def __init__(self, engine="http", profile=None, delay=8, headless=False, timeout=30):
        if delay < 3:
            raise ValueError("Use at least three seconds between requests")
        self.engine, self.profile, self.delay = engine, profile, delay
        self.headless, self.timeout = headless, timeout
        self.stack = ExitStack()
        self.last_request = None

    def __enter__(self):
        try:
            if self.engine == "http":
                self.client = self.stack.enter_context(httpx.Client(timeout=self.timeout, follow_redirects=False, headers={"User-Agent":"AmazonPersonalResearch/0.1 (bounded personal product research)", "Accept-Language":"en-IN,en;q=0.9"}))
            else:
                if not self.profile:
                    raise ValueError("A dedicated --profile directory is required for browser engines")
                directory = Path(self.profile).expanduser().resolve()
                directory.mkdir(parents=True, exist_ok=True, mode=0o700)
                if os.name != "nt":
                    directory.chmod(0o700)
                if self.engine == "camoufox":
                    from camoufox.sync_api import Camoufox
                    self.context = self.stack.enter_context(Camoufox(persistent_context=True, user_data_dir=str(directory), headless=self.headless, locale="en-IN"))
                else:
                    from playwright.sync_api import sync_playwright
                    playwright = self.stack.enter_context(sync_playwright())
                    self.context = playwright.chromium.launch_persistent_context(str(directory), headless=self.headless, locale="en-IN")
                    self.stack.callback(self.context.close)
                self.page = self.context.new_page()
            return self
        except Exception as exc:
            self.stack.close()
            if isinstance(exc,(ImportError,ValueError,AccessProblem)):
                raise
            raise AccessProblem("browser_setup_error",f"Browser could not start: {exc}") from exc

    def __exit__(self, *args):
        return self.stack.__exit__(*args)

    def fetch(self, url, kind=None):
        url = amazon_url(url)
        if self.last_request is not None:
            time.sleep(max(0, self.delay - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        try:
            if self.engine == "http":
                # Validate every redirect; never follow a URL into another service.
                for _ in range(6):
                    response = self.client.get(url)
                    if response.status_code in {301,302,303,307,308} and response.headers.get("location"):
                        from urllib.parse import urljoin
                        url = amazon_url(urljoin(url, response.headers["location"]))
                        continue
                    html, status, final_url = response.text, response.status_code, str(response.url)
                    break
                else:
                    raise AccessProblem("redirect_loop", "Too many redirects")
            else:
                response = self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
                final_url = amazon_url(self.page.url)
                status = response.status if response else 200
                # Allow rendered cards/reviews to arrive; a missing selector is
                # subsequently classified rather than silently exported as zero.
                check_access(self.page.content(), final_url, status)
                selector = '[data-component-type="s-search-result"]' if kind == "search" else '[data-hook="review"], #productTitle'
                try:
                    self.page.locator(selector).first.wait_for(timeout=5000)
                except Exception as exc:
                    from playwright.sync_api import TimeoutError as BrowserTimeout
                    if not isinstance(exc, BrowserTimeout):
                        raise
                html = self.page.content()
            check_access(html, final_url, status)
            return html, status, final_url
        except httpx.HTTPError as exc:
            raise AccessProblem("network_error", str(exc)) from exc
        except Exception as exc:
            if isinstance(exc,(AccessProblem,ValueError)):
                raise
            raise AccessProblem("browser_error",str(exc)) from exc

    def prepare_session(self):
        if self.engine == "http":
            raise ValueError("Choose chromium or camoufox for a visible session")
        if self.headless:
            raise ValueError("Session preparation needs a visible browser")
        self.page.goto("https://www.amazon.in/", wait_until="domcontentloaded")
        print("Use this dedicated browser to sign in yourself and set your delivery location.")
        print("Your password/OTP is never requested by this program. Close any challenge normally.")
        input("When finished, press Enter here to close and save the local session: ")
