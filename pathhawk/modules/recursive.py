"""
Controlled recursive discovery module for PathHawk.
Developed by ISHA SONARIA.
"""

from typing import List, Set
from urllib.parse import urlparse

from pathhawk.config import ScanConfig, ScanResult
from pathhawk.core.engine import ScanEngine
from pathhawk.utils.formatter import console
from pathhawk.utils.wordlists import get_default_wordlist, load_wordlist


class RecursiveScanner:
    """Performs controlled recursive path enumeration with depth caps and cycle avoidance."""

    def __init__(self, config: ScanConfig):
        self.config = config
        self.max_depth = max(1, config.max_depth)
        self.visited_paths: Set[str] = set()

    def run(self) -> List[ScanResult]:
        """Execute depth-controlled recursive enumeration."""
        if not self.config.target_url:
            raise ValueError("Target URL is required for recursive scan.")

        if self.config.wordlist_path:
            words = load_wordlist(self.config.wordlist_path)
        else:
            words = get_default_wordlist("paths")

        all_results: List[ScanResult] = []
        base_url = self.config.target_url.rstrip("/")

        # Queue contains tuples of (current_url_prefix, current_depth)
        queue = [(base_url, 0)]
        self.visited_paths.add(urlparse(base_url).path or "/")

        while queue:
            current_prefix, depth = queue.pop(0)

            if depth >= self.max_depth:
                continue

            if not self.config.silent:
                console.print(
                    f"[bold cyan][*] Recursing into:[/bold cyan] [bright_white]{current_prefix}[/bright_white] "
                    f"[dim](depth {depth + 1}/{self.max_depth})[/dim]"
                )

            urls_to_test: List[str] = []
            for word in words:
                clean = word.strip().lstrip("/")
                if not clean:
                    continue
                test_url = f"{current_prefix}/{clean}/"
                urls_to_test.append(test_url)

            engine = ScanEngine(self.config)
            findings = engine.scan_urls(
                urls_to_test,
                description=f"Depth {depth + 1}: {urlparse(current_prefix).path or '/'}",
            )

            for res in findings:
                res.category = "recursive"
                res.depth = depth + 1
                all_results.append(res)

                # If directory found (200, 301, 302, 401, 403), consider for next depth
                if res.status_code in (200, 301, 302, 403):
                    next_path = urlparse(res.url).path.rstrip("/")
                    if next_path and next_path not in self.visited_paths:
                        self.visited_paths.add(next_path)
                        clean_url = res.url.rstrip("/")
                        queue.append((clean_url, depth + 1))

        return all_results
