"""
Banner and branding display for PathHawk.
Developed by ISHA SONARIA.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from pathhawk import __author__, __organization__, __tagline__, __title__, __version__

console = Console()

ASCII_BANNER = r"""
 ██████╗  █████╗ ████████╗██╗  ██╗██╗  ██╗ █████╗ ██╗    ██╗██╗  ██╗
 ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║██║  ██║██╔══██╗██║    ██║██║ ██╔╝
 ██████╔╝███████║   ██║   ███████║███████║███████║██║ █╗ ██║█████╔╝ 
 ██╔═══╝ ██╔══██║   ██║   ██╔══██║██╔══██║██╔══██║██║███╗██║██╔═██╗ 
 ██║     ██║  ██║   ██║   ██║  ██║██║  ██║██║  ██║╚███╔███╔╝██║  ██╗
 ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝
"""


def get_banner_text() -> str:
    return ASCII_BANNER


def display_banner(suppress: bool = False) -> None:
    """Display the official PathHawk startup banner with developer credits."""
    if suppress:
        return

    banner_text = Text(ASCII_BANNER, style="bold bright_cyan")

    info_text = Text()
    info_text.append(f"  {__title__}", style="bold bright_green")
    info_text.append(" - Advanced Web Asset Discovery & Reconnaissance Tool\n", style="bright_white")
    info_text.append("  Developer    : ", style="cyan")
    info_text.append(f"{__author__}\n", style="bold bright_white")
    info_text.append("  Organization : ", style="cyan")
    info_text.append(f"{__organization__}\n", style="white")
    info_text.append("  Tagline      : ", style="cyan")
    info_text.append(f"{__tagline__}\n", style="italic yellow")
    info_text.append("  Version      : ", style="cyan")
    info_text.append(f"v{__version__}\n", style="bold green")
    info_text.append("  Authorization: ", style="red")
    info_text.append("Authorized security assessments & owned environments only.\n", style="bold red")

    panel = Panel(
        info_text,
        title="[bold green]PATHHAWK RECON ENGINE[/bold green]",
        subtitle="[bold cyan]Isha Sonaria Security Tools[/bold cyan]",
        border_style="bright_cyan",
        expand=False,
    )

    console.print(banner_text)
    console.print(panel)
    console.print()


def display_disclaimer():
    """Display the formal ethical authorization notice."""
    disclaimer = (
        "[bold red][!] LEGAL & ETHICAL NOTICE:[/bold red] "
        "[white]PathHawk is developed by ISHA SONARIA strictly for authorized educational security labs, "
        "defensive reconnaissance, and systems you own or have explicit written permission to assess. "
        "Unauthorized testing against third-party systems is prohibited.[/white]"
    )
    console.print(disclaimer)
    console.print()
