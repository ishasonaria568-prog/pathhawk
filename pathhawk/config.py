"""
Configuration models and defaults for PathHawk.
Developed by ISHA SONARIA.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ScanConfig:
    # Target options
    target_url: Optional[str] = None
    domain: Optional[str] = None
    wordlist_path: Optional[Path] = None

    # Discovery options
    extensions: List[str] = field(default_factory=list)
    recursive: bool = False
    max_depth: int = 1
    http_method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    user_agent: str = "PathHawk/1.0.0 (+https://github.com/ishasonaria/pathhawk - Authorized Assessment)"
    follow_redirects: bool = False

    # Filters
    status_codes: Set[int] = field(default_factory=lambda: {200, 204, 301, 302, 307, 308, 401, 403})
    excluded_status_codes: Set[int] = field(default_factory=set)
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    exclude_sizes: Set[int] = field(default_factory=set)

    # Concurrency and Network
    threads: int = 15
    timeout: float = 8.0
    retries: int = 2
    delay: float = 0.0  # Rate limiting delay in seconds between requests

    # Responsible safeguards
    allow_public: bool = False
    lab_mode: bool = False
    silent: bool = False

    # Reporting
    output_file: Optional[Path] = None
    report_format: str = "json"  # json, csv, html


@dataclass
class ScanResult:
    url: str
    status_code: int
    content_length: int
    response_time: float
    redirect_url: Optional[str] = None
    title: Optional[str] = None
    content_type: Optional[str] = None
    category: str = "path"  # 'path', 'file', 'subdomain'
    depth: int = 0
    words_count: int = 0
    lines_count: int = 0
