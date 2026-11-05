"""
Web file enumeration module with extension mutations for PathHawk.
Developed by ISHA SONARIA.
"""

from typing import List, Set
from pathhawk.config import ScanConfig, ScanResult
from pathhawk.core.engine import ScanEngine
from pathhawk.utils.wordlists import get_default_wordlist, load_wordlist


class FileEnumerator:
    """Discovers accessible files with custom extensions across target web applications."""

    def __init__(self, config: ScanConfig):
        self.config = config

    def run(self) -> List[ScanResult]:
        """Execute web file enumeration with extension permutations."""
        if not self.config.target_url:
            raise ValueError("Target URL is required for file enumeration.")

        if self.config.wordlist_path:
            words = load_wordlist(self.config.wordlist_path)
        else:
            words = get_default_wordlist("files")

        target_base = self.config.target_url.rstrip("/") + "/"
        extensions = self.config.extensions or ["txt", "html", "php", "js", "json"]

        urls_to_test: List[str] = []
        seen: Set[str] = set()

        for word in words:
            clean_word = word.strip().lstrip("/")
            if not clean_word:
                continue

            # Check raw filename if it already contains an extension
            if "." in clean_word:
                url = f"{target_base}{clean_word}"
                if url not in seen:
                    seen.add(url)
                    urls_to_test.append(url)
            else:
                for ext in extensions:
                    clean_ext = ext.lstrip(".")
                    url = f"{target_base}{clean_word}.{clean_ext}"
                    if url not in seen:
                        seen.add(url)
                        urls_to_test.append(url)

        engine = ScanEngine(self.config)
        results = engine.scan_urls(urls_to_test, description="Enumerating web files")
        for r in results:
            r.category = "file"

        return results
