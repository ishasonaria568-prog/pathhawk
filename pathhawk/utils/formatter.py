"""
Terminal output formatting and color schemes for PathHawk.
Developed by ISHA SONARIA.
"""

from rich.console import Console
from rich.table import Table
from rich.text import Text
from pathhawk.config import ScanResult

console = Console()


def get_status_style(status_code: int) -> str:
    """Return an appropriate terminal color style for an HTTP status code."""
    if 200 <= status_code < 300:
        return "bold bright_green"
    elif 300 <= status_code < 400:
        return "bold bright_cyan"
    elif status_code == 401 or status_code == 403:
        return "bold yellow"
    elif 400 <= status_code < 500:
        return "dim red"
    elif 500 <= status_code < 600:
        return "bold bright_red"
    return "white"


def format_size(bytes_length: int) -> str:
    """Format byte size in human-friendly units."""
    if bytes_length < 1024:
        return f"{bytes_length} B"
    elif bytes_length < 1024 * 1024:
        return f"{bytes_length / 1024:.1f} KB"
    else:
        return f"{bytes_length / (1024 * 1024):.2f} MB"


def print_result_line(result: ScanResult) -> None:
    """Print an individual discovery finding cleanly in real-time."""
    status_style = get_status_style(result.status_code)

    status_str = f"[{result.status_code}]"
    size_str = format_size(result.content_length)
    time_str = f"{result.response_time * 1000:.0f}ms"

    line = Text()
    line.append(f"{status_str:<7}", style=status_style)
    line.append(f"{size_str:>9} ", style="cyan")
    line.append(f"({time_str:>6}) ", style="bright_black")
    line.append(f"{result.url}", style="bright_white")

    if result.redirect_url:
        line.append(f" -> {result.redirect_url}", style="italic bright_cyan")

    if result.title:
        line.append(f" | Title: {result.title}", style="dim green")

    console.print(line)


def create_results_table(title: str = "PathHawk Discovery Findings") -> Table:
    """Create a clean Rich table for summary findings."""
    table = Table(
        title=title,
        title_style="bold bright_green",
        header_style="bold bright_cyan",
        border_style="cyan",
        show_lines=False,
    )
    table.add_column("Status", justify="center", width=8)
    table.add_column("Size", justify="right", width=10)
    table.add_column("Time", justify="right", width=8)
    table.add_column("Discovered Target", justify="left")
    table.add_column("Redirect / Notes", justify="left", style="dim")
    return table
