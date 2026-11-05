"""
CSV report generation for PathHawk.
Developed by ISHA SONARIA.
"""

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from pathhawk import __author__, __title__, __version__
from pathhawk.config import ScanConfig, ScanResult


def generate_csv_report(config: ScanConfig, results: List[ScanResult], output_path: Path) -> Path:
    """Export scan results into a formatted CSV report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # File header with metadata comments
        writer.writerow([f"# {__title__} v{__version__} - Report"])
        writer.writerow([f"# Developer: {__author__}"])
        writer.writerow([f"# Generated: {datetime.now(timezone.utc).isoformat()}"])
        writer.writerow([f"# Target: {config.target_url or config.domain}"])
        writer.writerow([])

        # Table headers
        writer.writerow([
            "Category",
            "Status Code",
            "URL / Host",
            "Content Length (Bytes)",
            "Response Time (ms)",
            "Redirect URL",
            "Page Title",
            "Depth",
        ])

        for r in results:
            writer.writerow([
                r.category,
                r.status_code,
                r.url,
                r.content_length,
                round(r.response_time * 1000, 2),
                r.redirect_url or "",
                r.title or "",
                r.depth,
            ])

    return output_path
