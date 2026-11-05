"""
Logger utilities for PathHawk.
Developed by ISHA SONARIA.
"""

from rich.console import Console

console = Console()


def log_info(msg: str):
    console.print(f"[bold cyan][*][/bold cyan] {msg}")


def log_success(msg: str):
    console.print(f"[bold bright_green][+][/bold bright_green] {msg}")


def log_warning(msg: str):
    console.print(f"[bold yellow][!][/bold yellow] {msg}")


def log_error(msg: str):
    console.print(f"[bold red][-][/bold red] {msg}")
