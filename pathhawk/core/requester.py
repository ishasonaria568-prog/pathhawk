"""
HTTP requester client for PathHawk.
Developed by ISHA SONARIA.
"""

import time
from typing import Optional
import httpx

from pathhawk.config import ScanConfig, ScanResult


class Requester:
    """Safe, persistent, and configurable HTTP requester."""

    def __init__(self, config: ScanConfig):
        self.config = config
        headers = dict(self.config.headers)
        if "User-Agent" not in headers:
            headers["User-Agent"] = self.config.user_agent

        self.client = httpx.Client(
            headers=headers,
            timeout=self.config.timeout,
            follow_redirects=self.config.follow_redirects,
            verify=False,  # Allow self-signed certificates in authorized lab environments
            limits=httpx.Limits(max_keepalive_connections=self.config.threads, max_connections=self.config.threads * 2),
        )

    def request(self, url: str, method: Optional[str] = None) -> Optional[ScanResult]:
        """Execute a single HTTP request with retries and timing."""
        http_method = (method or self.config.http_method).upper()

        if self.config.delay > 0:
            time.sleep(self.config.delay)

        for attempt in range(self.config.retries + 1):
            try:
                start_time = time.perf_counter()
                resp = self.client.request(http_method, url)
                elapsed = time.perf_counter() - start_time

                redirect_to = None
                if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
                    redirect_to = resp.headers.get("location")

                # Extract basic title if HTML
                title = None
                content_type = resp.headers.get("content-type", "").lower()
                if "html" in content_type and resp.content:
                    try:
                        text = resp.text[:2048]
                        if "<title>" in text and "</title>" in text:
                            title = text.split("<title>")[1].split("</title>")[0].strip()
                    except Exception:
                        pass

                raw_bytes = resp.content
                lines_count = raw_bytes.count(b"\n")
                words_count = len(raw_bytes.split())

                return ScanResult(
                    url=str(resp.url),
                    status_code=resp.status_code,
                    content_length=len(raw_bytes),
                    response_time=elapsed,
                    redirect_url=redirect_to,
                    title=title,
                    content_type=content_type,
                    lines_count=lines_count,
                    words_count=words_count,
                )
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError):
                if attempt == self.config.retries:
                    return None
                time.sleep(0.15)
            except Exception:
                return None

        return None

    def close(self):
        """Close HTTP client session."""
        self.client.close()
