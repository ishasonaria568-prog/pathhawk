"""
Combined discovery scanner coordinating directory, file, and recursive discovery.
Developed by ISHA SONARIA.
Organization: Isha Sonaria Security Tools
"""

from typing import List
from urllib.parse import urlparse

from pathhawk.config import ScanConfig, ScanResult
from pathhawk.modules.directory import DirectoryEnumerator
from pathhawk.modules.file_enum import FileEnumerator
from pathhawk.modules.recursive import RecursiveScanner
from pathhawk.utils.formatter import console


class CombinedScanner:
    """Coordinates multi-faceted reconnaissance: directory enumeration, file hunting, and recursive discovery."""

    def __init__(self, config: ScanConfig):
        self.config = config

    def run(self) -> List[ScanResult]:
        """Execute full combined web discovery."""
        combined_results: List[ScanResult] = []
        seen_urls = set()

        if not self.config.target_url:
            raise ValueError("Target URL is required for combined discovery.")

        # Phase 1: Directory Enumeration
        if not self.config.silent:
            console.print("[bold bright_green][Phase 1][/bold bright_green] [cyan]Initiating directory discovery...[/cyan]")

        dir_enum = DirectoryEnumerator(self.config)
        dir_results = dir_enum.run()
        for r in dir_results:
            if r.url not in seen_urls:
                seen_urls.add(r.url)
                combined_results.append(r)

        # Phase 2: Sensitive File Discovery
        if not self.config.silent:
            console.print()
            console.print("[bold bright_green][Phase 2][/bold bright_green] [cyan]Initiating web file enumeration...[/cyan]")

        file_enum = FileEnumerator(self.config)
        file_results = file_enum.run()
        for r in file_results:
            if r.url not in seen_urls:
                seen_urls.add(r.url)
                combined_results.append(r)

        # Phase 3: Recursive Discovery (if depth > 1)
        if self.config.max_depth > 1:
            if not self.config.silent:
                console.print()
                console.print(f"[bold bright_green][Phase 3][/bold bright_green] [cyan]Initiating controlled recursion (depth {self.config.max_depth})...[/cyan]")

            rec_scanner = RecursiveScanner(self.config)
            rec_results = rec_scanner.run()
            for r in rec_results:
                if r.url not in seen_urls:
                    seen_urls.add(r.url)
                    combined_results.append(r)

        combined_results.sort(key=lambda r: (r.status_code, r.url))
        return combined_results
