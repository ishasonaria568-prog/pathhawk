"""
DNS record resolution and subdomain discovery module for PathHawk.
Developed by ISHA SONARIA.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Optional, Set
import dns.resolver
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
from pathhawk.utils.formatter import console
from pathhawk.utils.wordlists import get_default_wordlist, load_wordlist
from rich.text import Text


class DNSEnumerator:
    """Discovers and resolves subdomains and records for target domain inventory."""

    def __init__(self, config: ScanConfig):
        self.config = config
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = self.config.timeout
        self.resolver.lifetime = self.config.timeout

    def _resolve_subdomain(self, fqdn: str) -> Optional[ScanResult]:
        """Attempt A, CNAME, or AAAA DNS lookup for a fully qualified domain."""
        start_time = time.perf_counter()
        ip_addresses: List[str] = []
        cnames: List[str] = []

        try:
            answers = self.resolver.resolve(fqdn, "A")
            for rdata in answers:
                ip_addresses.append(str(rdata))
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, Exception):
            pass

        # Try CNAME if no direct A record
        if not ip_addresses:
            try:
                cname_answers = self.resolver.resolve(fqdn, "CNAME")
                for rdata in cname_answers:
                    cnames.append(str(rdata.target))
            except Exception:
                pass

        elapsed = time.perf_counter() - start_time

        if ip_addresses or cnames:
            resolved_info = ", ".join(ip_addresses) if ip_addresses else f"CNAME: {', '.join(cnames)}"
            return ScanResult(
                url=fqdn,
                status_code=200,
                content_length=len(resolved_info),
                response_time=elapsed,
                redirect_url=resolved_info,
                title=f"DNS Resolved: {resolved_info}",
                category="dns",
            )
        return None

    def run(self) -> List[ScanResult]:
        """Execute subdomain discovery and DNS resolution."""
        if not self.config.domain:
            raise ValueError("Target domain is required for DNS enumeration.")

        clean_domain = self.config.domain.strip().lower()

        if self.config.wordlist_path:
            subdomains = load_wordlist(self.config.wordlist_path)
        else:
            subdomains = get_default_wordlist("subdomains")

        fqdns: List[str] = [f"{sub.strip().rstrip('.')}.{clean_domain}" for sub in subdomains if sub.strip()]
        results: List[ScanResult] = []

        total = len(fqdns)
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

        with progress:
            task_id: TaskID = progress.add_task("Resolving subdomains", total=total)

            with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
                futures = {executor.submit(self._resolve_subdomain, fqdn): fqdn for fqdn in fqdns}

                for future in as_completed(futures):
                    progress.advance(task_id, 1)
                    try:
                        res = future.result()
                        if res:
                            results.append(res)
                            if not self.config.silent:
                                line = Text()
                                line.append("[DNS]   ", style="bold bright_green")
                                line.append(f"{res.url:<30} ", style="bright_white")
                                line.append(f"-> {res.redirect_url}", style="cyan")
                                console.print(line)
                    except Exception:
                        continue

        results.sort(key=lambda r: r.url)
        return results
