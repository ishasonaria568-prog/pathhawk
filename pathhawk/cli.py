"""
Command-line interface for PathHawk.
Developed and branded by ISHA SONARIA.
Organization: Isha Sonaria Security Tools
"""

import json
from pathlib import Path
import sys
from typing import List, Optional
import typer
from rich.console import Console

from pathhawk import __author__, __organization__, __tagline__, __title__, __version__
from pathhawk.banner import display_banner, display_disclaimer
from pathhawk.config import ScanConfig, ScanResult
from pathhawk.core.validator import validate_domain, validate_target
from pathhawk.modules.directory import DirectoryEnumerator
from pathhawk.modules.dns_enum import DNSEnumerator
from pathhawk.modules.file_enum import FileEnumerator
from pathhawk.modules.recursive import RecursiveScanner
from pathhawk.reporting.csv_report import generate_csv_report
from pathhawk.reporting.html_report import generate_html_report
from pathhawk.reporting.json_report import generate_json_report
from pathhawk.utils.formatter import create_results_table, print_result_line
from pathhawk.utils.logger import log_error, log_info, log_success, log_warning

app = typer.Typer(
    name="pathhawk",
    help=f"{__title__} v{__version__} - Professional Web Content Discovery & Reconnaissance Tool.\nDeveloped by {__author__} ({__organization__}).",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()


def parse_status_codes(codes_str: Optional[str]) -> set[int]:
    """Parse comma-separated HTTP status codes."""
    if not codes_str:
        return {200, 204, 301, 302, 307, 308, 401, 403}
    result = set()
    for part in codes_str.split(","):
        part = part.strip()
        if part.isdigit():
            result.add(int(part))
    return result


def parse_sizes(sizes_str: Optional[str]) -> set[int]:
    """Parse comma-separated size exclusions."""
    if not sizes_str:
        return set()
    result = set()
    for part in sizes_str.split(","):
        part = part.strip()
        if part.isdigit():
            result.add(int(part))
    return result


def export_report_if_requested(config: ScanConfig, results: List[ScanResult]):
    """Export results to requested format if output file is specified."""
    if not config.output_file:
        return

    fmt = config.report_format.lower()
    path = config.output_file

    if fmt == "html" or path.suffix == ".html":
        out = generate_html_report(config, results, path)
        log_success(f"HTML audit report generated: [bright_white]{out}[/bright_white]")
    elif fmt == "csv" or path.suffix == ".csv":
        out = generate_csv_report(config, results, path)
        log_success(f"CSV report saved: [bright_white]{out}[/bright_white]")
    else:
        out = generate_json_report(config, results, path)
        log_success(f"JSON report saved: [bright_white]{out}[/bright_white]")


def version_callback(value: bool):
    if value:
        console.print(f"[bold bright_green]{__title__}[/bold bright_green] version [cyan]{__version__}[/cyan]")
        console.print(f"Developed by [bold white]{__author__}[/bold white] | [dim]{__organization__}[/dim]")
        console.print(f"Tagline: [italic yellow]{__tagline__}[/italic yellow]")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Display PathHawk version and developer information.", callback=version_callback, is_eager=True
    )
):
    pass


@app.command(name="dir", help="Discover web directories and endpoints on an authorized target.")
def directory_cmd(
    url: str = typer.Option(..., "-u", "--url", help="Target URL (e.g. https://lab.target.local)"),
    wordlist: Optional[Path] = typer.Option(None, "-w", "--wordlist", help="Path to custom wordlist file"),
    status: Optional[str] = typer.Option(None, "-s", "--status", help="Comma-separated status codes to show (default: 200,204,301,302,307,308,401,403)"),
    exclude_status: Optional[str] = typer.Option(None, "-b", "--exclude-status", help="Comma-separated status codes to exclude (e.g. 404,500)"),
    exclude_size: Optional[str] = typer.Option(None, "--exclude-size", help="Comma-separated response byte sizes to filter out"),
    threads: int = typer.Option(15, "-t", "--threads", help="Number of concurrent worker threads"),
    timeout: float = typer.Option(8.0, "--timeout", help="HTTP request timeout in seconds"),
    method: str = typer.Option("GET", "-m", "--method", help="HTTP request method (GET, HEAD, POST, OPTIONS)"),
    follow_redirects: bool = typer.Option(False, "-r", "--redirect", help="Follow HTTP redirects"),
    delay: float = typer.Option(0.0, "--delay", help="Delay between requests in seconds (rate limiting)"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output report file path"),
    format: str = typer.Option("json", "--format", help="Output format: json, csv, html"),
    lab_mode: bool = typer.Option(False, "--lab-mode", help="Authorize scanning local/private test environments (127.0.0.1, RFC1918)"),
    allow_public: bool = typer.Option(False, "--allow-public", help="Confirm explicit authorization for public domain targets"),
    silent: bool = typer.Option(False, "--silent", help="Suppress banner and non-finding messages"),
):
    display_banner(suppress=silent)
    if not silent:
        display_disclaimer()

    is_valid, validated_or_err = validate_target(url, allow_public=allow_public, lab_mode=lab_mode)
    if not is_valid:
        log_error(f"Target validation failed: {validated_or_err}")
        raise typer.Exit(code=1)

    config = ScanConfig(
        target_url=validated_or_err,
        wordlist_path=wordlist,
        status_codes=parse_status_codes(status),
        excluded_status_codes=parse_status_codes(exclude_status) if exclude_status else set(),
        exclude_sizes=parse_sizes(exclude_size),
        threads=threads,
        timeout=timeout,
        http_method=method,
        follow_redirects=follow_redirects,
        delay=delay,
        output_file=output,
        report_format=format,
        lab_mode=lab_mode,
        allow_public=allow_public,
        silent=silent,
    )

    if not silent:
        log_info(f"Target URL: [bold white]{config.target_url}[/bold white]")
        log_info(f"Threads: [cyan]{threads}[/cyan] | Timeout: [cyan]{timeout}s[/cyan] | Method: [cyan]{method}[/cyan]")
        console.print()

    enumerator = DirectoryEnumerator(config)
    results = enumerator.run()

    if not silent:
        console.print()
        log_success(f"Directory discovery completed. Discovered [bold bright_green]{len(results)}[/bold bright_green] matching endpoints.")

    export_report_if_requested(config, results)


@app.command(name="file", help="Enumerate accessible web files and extensions on target.")
def file_cmd(
    url: str = typer.Option(..., "-u", "--url", help="Target URL (e.g. https://lab.target.local)"),
    wordlist: Optional[Path] = typer.Option(None, "-w", "--wordlist", help="Base file names wordlist"),
    extensions: str = typer.Option("php,txt,html,json,js", "-x", "--extensions", help="Comma-separated file extensions to test"),
    status: Optional[str] = typer.Option(None, "-s", "--status", help="Comma-separated status codes to show"),
    exclude_status: Optional[str] = typer.Option(None, "-b", "--exclude-status", help="Comma-separated status codes to exclude"),
    threads: int = typer.Option(15, "-t", "--threads", help="Number of concurrent worker threads"),
    timeout: float = typer.Option(8.0, "--timeout", help="HTTP request timeout in seconds"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output report file path"),
    format: str = typer.Option("json", "--format", help="Output format: json, csv, html"),
    lab_mode: bool = typer.Option(False, "--lab-mode", help="Authorize scanning local/private test environments"),
    allow_public: bool = typer.Option(False, "--allow-public", help="Confirm explicit authorization for public domain targets"),
    silent: bool = typer.Option(False, "--silent", help="Suppress banner and non-finding messages"),
):
    display_banner(suppress=silent)
    if not silent:
        display_disclaimer()

    is_valid, validated_or_err = validate_target(url, allow_public=allow_public, lab_mode=lab_mode)
    if not is_valid:
        log_error(f"Target validation failed: {validated_or_err}")
        raise typer.Exit(code=1)

    ext_list = [e.strip().lstrip(".") for e in extensions.split(",") if e.strip()]

    config = ScanConfig(
        target_url=validated_or_err,
        wordlist_path=wordlist,
        extensions=ext_list,
        status_codes=parse_status_codes(status),
        excluded_status_codes=parse_status_codes(exclude_status) if exclude_status else set(),
        threads=threads,
        timeout=timeout,
        output_file=output,
        report_format=format,
        lab_mode=lab_mode,
        allow_public=allow_public,
        silent=silent,
    )

    if not silent:
        log_info(f"Target: [bold white]{config.target_url}[/bold white]")
        log_info(f"Extensions: [cyan]{', '.join(ext_list)}[/cyan]")
        console.print()

    enumerator = FileEnumerator(config)
    results = enumerator.run()

    if not silent:
        console.print()
        log_success(f"File enumeration completed. Discovered [bold bright_green]{len(results)}[/bold bright_green] matching files.")

    export_report_if_requested(config, results)


@app.command(name="dns", help="Resolve subdomains and DNS records for an authorized domain.")
def dns_cmd(
    domain: str = typer.Option(..., "-d", "--domain", help="Target domain (e.g. example.local)"),
    wordlist: Optional[Path] = typer.Option(None, "-w", "--wordlist", help="Subdomain wordlist"),
    threads: int = typer.Option(15, "-t", "--threads", help="Concurrent resolution threads"),
    timeout: float = typer.Option(4.0, "--timeout", help="DNS query timeout in seconds"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output report file path"),
    format: str = typer.Option("json", "--format", help="Output format: json, csv, html"),
    silent: bool = typer.Option(False, "--silent", help="Suppress banner and non-finding messages"),
):
    display_banner(suppress=silent)
    if not silent:
        display_disclaimer()

    if not validate_domain(domain):
        log_error(f"Invalid domain name format: '{domain}'")
        raise typer.Exit(code=1)

    config = ScanConfig(
        domain=domain,
        wordlist_path=wordlist,
        threads=threads,
        timeout=timeout,
        output_file=output,
        report_format=format,
        silent=silent,
    )

    if not silent:
        log_info(f"Target Domain: [bold white]{domain}[/bold white]")
        console.print()

    enumerator = DNSEnumerator(config)
    results = enumerator.run()

    if not silent:
        console.print()
        log_success(f"DNS enumeration completed. Resolved [bold bright_green]{len(results)}[/bold bright_green] active hosts.")

    export_report_if_requested(config, results)


@app.command(name="scan", help="Run combined and recursive content discovery.")
def scan_cmd(
    url: str = typer.Option(..., "-u", "--url", help="Target URL"),
    wordlist: Optional[Path] = typer.Option(None, "-w", "--wordlist", help="Wordlist for recursive directory discovery"),
    depth: int = typer.Option(2, "--depth", help="Maximum recursion depth (default: 2)"),
    status: Optional[str] = typer.Option(None, "-s", "--status", help="Comma-separated status codes to show"),
    threads: int = typer.Option(15, "-t", "--threads", help="Worker threads"),
    timeout: float = typer.Option(8.0, "--timeout", help="Timeout per request"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output report file path"),
    format: str = typer.Option("json", "--format", help="Output format: json, csv, html"),
    lab_mode: bool = typer.Option(False, "--lab-mode", help="Authorize scanning local/private test environments"),
    allow_public: bool = typer.Option(False, "--allow-public", help="Confirm explicit authorization for public domain targets"),
    silent: bool = typer.Option(False, "--silent", help="Suppress banner and non-finding messages"),
):
    display_banner(suppress=silent)
    if not silent:
        display_disclaimer()

    is_valid, validated_or_err = validate_target(url, allow_public=allow_public, lab_mode=lab_mode)
    if not is_valid:
        log_error(f"Target validation failed: {validated_or_err}")
        raise typer.Exit(code=1)

    config = ScanConfig(
        target_url=validated_or_err,
        wordlist_path=wordlist,
        max_depth=depth,
        status_codes=parse_status_codes(status),
        threads=threads,
        timeout=timeout,
        output_file=output,
        report_format=format,
        lab_mode=lab_mode,
        allow_public=allow_public,
        silent=silent,
    )

    if not silent:
        log_info(f"Target URL: [bold white]{config.target_url}[/bold white]")
        log_info(f"Max recursion depth: [cyan]{depth}[/cyan]")
        console.print()

    scanner = RecursiveScanner(config)
    results = scanner.run()

    if not silent:
        console.print()
        log_success(f"Recursive scan completed. Found [bold bright_green]{len(results)}[/bold bright_green] total assets.")

    export_report_if_requested(config, results)


@app.command(name="report", help="Convert an existing JSON results file into an HTML or CSV report.")
def report_cmd(
    input_file: Path = typer.Option(..., "-i", "--input", help="Path to input PathHawk JSON results file"),
    format: str = typer.Option("html", "-f", "--format", help="Target output format: html, csv"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file path (default: input with new extension)"),
):
    display_banner()

    if not input_file.is_file():
        log_error(f"Input file not found: {input_file}")
        raise typer.Exit(code=1)

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log_error(f"Could not parse JSON file: {e}")
        raise typer.Exit(code=1)

    target_url = data.get("target", {}).get("url")
    target_domain = data.get("target", {}).get("domain")

    config = ScanConfig(
        target_url=target_url,
        domain=target_domain,
    )

    results: List[ScanResult] = []
    for item in data.get("results", []):
        results.append(
            ScanResult(
                url=item.get("url", ""),
                status_code=item.get("status_code", 200),
                content_length=item.get("content_length", 0),
                response_time=item.get("response_time_ms", 0) / 1000.0,
                redirect_url=item.get("redirect_url"),
                title=item.get("title"),
                category=item.get("category", "path"),
                depth=item.get("depth", 0),
                words_count=item.get("words_count", 0),
                lines_count=item.get("lines_count", 0),
            )
        )

    out_path = output or input_file.with_suffix(f".{format.lower()}")

    if format.lower() == "html":
        gen_path = generate_html_report(config, results, out_path)
        log_success(f"Converted report to HTML: [bold bright_white]{gen_path}[/bold bright_white]")
    elif format.lower() == "csv":
        gen_path = generate_csv_report(config, results, out_path)
        log_success(f"Converted report to CSV: [bold bright_white]{gen_path}[/bold bright_white]")
    else:
        log_error(f"Unsupported format '{format}'. Supported formats are: html, csv")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
