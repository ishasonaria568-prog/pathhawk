"""
Wordlist loader and generator utilities for PathHawk.
Developed by ISHA SONARIA.
"""

from pathlib import Path
from typing import Iterable, List, Set


DEFAULT_PATHS = [
    "admin",
    "administrator",
    "login",
    "api",
    "v1",
    "v2",
    "dashboard",
    "backup",
    "config",
    "uploads",
    "static",
    "assets",
    "docs",
    "private",
    "dev",
    "staging",
    "server-status",
    ".git",
    ".env",
    "robots.txt",
    "sitemap.xml",
    "portal",
    "manage",
    "console",
    "health",
    "metrics",
]

DEFAULT_FILES = [
    "index",
    "login",
    "admin",
    "config",
    "database",
    "db",
    "settings",
    "app",
    "api",
    "backup",
    "dump",
    "user",
    "users",
    "test",
    "info",
    "version",
]

DEFAULT_SUBDOMAINS = [
    "www",
    "mail",
    "remote",
    "blog",
    "webmail",
    "server",
    "ns1",
    "ns2",
    "smtp",
    "secure",
    "vpn",
    "api",
    "dev",
    "staging",
    "app",
    "portal",
    "admin",
    "internal",
    "test",
    "demo",
    "beta",
]


def load_wordlist(file_path: Path) -> List[str]:
    """Load items from a wordlist file, ignoring comments and blank lines."""
    if not file_path.is_file():
        raise FileNotFoundError(f"Wordlist file not found: {file_path}")

    words: List[str] = []
    seen: Set[str] = set()

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            clean = line.strip()
            if clean and not clean.startswith("#") and clean not in seen:
                seen.add(clean)
                words.append(clean)

    return words


def get_default_wordlist(category: str = "paths") -> List[str]:
    """Provide built-in curated baseline wordlists if no custom file is supplied."""
    if category == "paths":
        return list(DEFAULT_PATHS)
    elif category == "files":
        return list(DEFAULT_FILES)
    elif category == "subdomains":
        return list(DEFAULT_SUBDOMAINS)
    return list(DEFAULT_PATHS)
