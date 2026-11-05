"""
DNS record resolution and subdomain discovery module for PathHawk.
Developed by ISHA SONARIA.
Organization: Isha Sonaria Security Tools
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Dict, List, Optional, Set
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
from rich.table import Table
from rich.text import Text

from pathhawk.config import ScanConfig, ScanResult
from pathhawk.utils.formatter import console
from pathhawk.utils.wordlists import get_default_wordlist, load_wordlist

STANDARD_RECORD_TYPES = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA"]


class DNSEnumerator:
    """Discovers DNS records and resolves subdomains for target domain inventory."""

    def __init__(self, config: ScanConfig):
        self.config = config
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = self.config.timeout
        self.resolver.lifetime = self.config.timeout

    def query_record(self, domain: str, rtype: str) -> List[str]:
        """Query standard DNS records (A, AAAA, MX, NS, TXT, CNAME, SOA) for a domain."""
        results: List[str] = []
        try:
            answers = self.resolver.resolve(domain, rtype)
            for rdata in answers:
                if rtype == "MX":
                    results.append(f"{rdata.preference} {rdata.exchange}")
                elif rtype == "TXT":
                    # Join TXT strings cleanly
                    txt_data = " ".join([b.decode("utf-8", errors="ignore") if isinstance(b, bytes) else str(b) for b in rdata.strings])
                    results.append(txt_data)
                elif rtype in ("CNAME", "NS"):
                    results.append(str(rdata.target).rstrip("."))
                else:
                    results.append(str(rdata))
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, dns.resolver.NoNameservers, Exception):
            pass
        return results

    def query_common_records(self, domain: str) -> Dict[str, List[str]]:
        """Query all standard record types for the apex domain."""
        records: Dict[str, List[str]] = {}
        for rtype in STANDARD_RECORD_TYPES:
            found = self.query_record(domain, rtype)
            if found:
                records[rtype] = found
        return records

    def _resolve_subdomain(self, fqdn: str) -> Optional[ScanResult]:
        """Attempt A or CNAME lookup for a subdomain candidate."""
        start_time = time.perf_counter()
        ip_addresses: List[str] = []
        cnames: List[str] = []

        try:
            answers = self.resolver.resolve(fqdn, "A")
            for rdata in answers:
                ip_addresses.append(str(rdata))
        except Exception:
            pass

        # Try CNAME if no direct A record
        if not ip_addresses:
            try:
                cname_answers = self.resolver.resolve(fqdn, "CNAME")
                for rdata in cname_answers:
                    cnames.append(str(rdata.target).rstrip("."))
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
        """Execute common DNS record enumeration and optional subdomain resolution."""
        if not self.config.domain:
            raise ValueError("Target domain is required for DNS enumeration.")

        clean_domain = self.config.domain.strip().lower()
        results: List[ScanResult] = []

        # 1. Query standard domain records first
        apex_records = self.query_common_records(clean_domain)
        if not self.config.silent and apex_records:
            table = Table(
                title=f"[bold bright_green]Apex DNS Records for {clean_domain}[/bold bright_green]",
                header_style="bold bright_cyan",
                border_style="cyan",
            )
            table.add_column("Type", style="bold yellow", width=8)
            table.add_column("Records / Values", style="bright_white")

            for rtype, vals in apex_records.items():
                for val in vals:
                    table.add_row(rtype, val)
                    results.append(
                        ScanResult(
                            url=f"{clean_domain} [{rtype}]",
                            status_code=200,
                            content_length=len(val),
                            response_time=0.0,
                            redirect_url=val,
                            title=f"Record {rtype}: {val}",
                            category="dns_record",
                        )
                    )
            console.print(table)
            console.print()

        # 2. Subdomain discovery
        if self.config.wordlist_path:
            subdomains = load_wordlist(self.config.wordlist_path)
        else:
            subdomains = get_default_wordlist("subdomains")

        fqdns: List[str] = [f"{sub.strip().rstrip('.')}.{clean_domain}" for sub in subdomains if sub.strip()]
        total = len(fqdns)

        if total > 0:
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
                                    line.append(f"{res.url:<32} ", style="bright_white")
                                    line.append(f"-> {res.redirect_url}", style="cyan")
                                    console.print(line)
                        except Exception:
                            continue

        results.sort(key=lambda r: r.url)
        return results
