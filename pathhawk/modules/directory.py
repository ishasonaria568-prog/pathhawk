"""
Directory enumeration module for PathHawk.
Developed by ISHA SONARIA.
"""

from typing import List, Optional
from urllib.parse import urljoin

from pathhawk.config import ScanConfig, ScanResult
from pathhawk.core.engine import ScanEngine
from pathhawk.utils.wordlists import get_default_wordlist, load_wordlist


class DirectoryEnumerator:
    """Discovers accessible directories on target web applications."""

    def __init__(self, config: ScanConfig):
        self.config = config

    def run(self) -> List[ScanResult]:
        """Execute web directory enumeration."""
        if not self.config.target_url:
            raise ValueError("Target URL is required for directory enumeration.")

        # Load wordlist or use default
        if self.config.wordlist_path:
            words = load_wordlist(self.config.wordlist_path)
        else:
            words = get_default_wordlist("paths")

        target_base = self.config.target_url.rstrip("/") + "/"
        urls_to_test: List[str] = []

        for word in words:
            clean_word = word.strip().lstrip("/")
            if not clean_word:
                continue
            # Check directory path with trailing slash and without
            urls_to_test.append(f"{target_base}{clean_word}/")

        engine = ScanEngine(self.config)
        results = engine.scan_urls(urls_to_test, description="Enumerating directories")
        for r in results:
            r.category = "directory"

        return results
