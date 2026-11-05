"""
Core multi-threaded execution engine for PathHawk.
Developed by ISHA SONARIA.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from typing import Callable, Iterable, List, Optional
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from pathhawk.config import ScanConfig, ScanResult
from pathhawk.core.filters import ResultFilter
from pathhawk.core.requester import Requester
from pathhawk.utils.formatter import console, print_result_line


class ScanEngine:
    """Coordinates concurrent requests, rate limits, progress bars, and filters."""

    def __init__(self, config: ScanConfig):
        self.config = config
        self.filter = ResultFilter(config)
        self.requester = Requester(config)
        self.lock = threading.Lock()
        self.interrupted = False

    def scan_urls(
        self,
        urls: Iterable[str],
        callback: Optional[Callable[[ScanResult], None]] = None,
        description: str = "Scanning targets",
    ) -> List[ScanResult]:
        """Scan a list of URLs concurrently using ThreadPoolExecutor."""
        url_list = list(urls)
        total = len(url_list)
        results: List[ScanResult] = []

        if total == 0:
            return results

        progress = Progress(
            SpinnerColumn("dots", style="bright_cyan"),
            TextColumn("[bold bright_green]{task.description}[/bold bright_green]"),
            BarColumn(complete_style="bright_cyan", finished_style="bright_green"),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=console,
            transient=True,
            disable=self.config.silent,
        )

        try:
            with progress:
                task_id: TaskID = progress.add_task(description, total=total)

                with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
                    futures = {
                        executor.submit(self.requester.request, url): url for url in url_list
                    }

                    for future in as_completed(futures):
                        if self.interrupted:
                            break

                        progress.advance(task_id, 1)
                        try:
                            res = future.result()
                            if res and self.filter.should_include(res):
                                with self.lock:
                                    results.append(res)
                                    if not self.config.silent:
                                        print_result_line(res)
                                    if callback:
                                        callback(res)
                        except Exception:
                            continue

        except KeyboardInterrupt:
            self.interrupted = True
            console.print("\n[bold red][!] Interrupted by user. Cleaning up jobs...[/bold red]")
        finally:
            self.requester.close()

        # Sort results by status code then URL
        results.sort(key=lambda r: (r.status_code, r.url))
        return results
