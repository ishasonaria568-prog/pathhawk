"""
JSON report generation for PathHawk.
Developed by ISHA SONARIA.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List

from pathhawk import __author__, __organization__, __tagline__, __title__, __version__
from pathhawk.config import ScanConfig, ScanResult


def generate_json_report(config: ScanConfig, results: List[ScanResult], output_path: Path) -> Path:
    """Export scan results into a structured JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report_data: Dict[str, Any] = {
        "metadata": {
            "tool": __title__,
            "version": __version__,
            "developer": __author__,
            "organization": __organization__,
            "tagline": __tagline__,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "target": {
            "url": config.target_url,
            "domain": config.domain,
            "lab_mode": config.lab_mode,
            "allow_public": config.allow_public,
        },
        "configuration": {
            "threads": config.threads,
            "timeout": config.timeout,
            "http_method": config.http_method,
            "follow_redirects": config.follow_redirects,
            "extensions": config.extensions,
            "max_depth": config.max_depth,
            "status_filter": list(config.status_codes) if config.status_codes else [],
        },
        "summary": {
            "total_findings": len(results),
            "status_breakdown": {},
        },
        "results": [
            {
                "url": r.url,
                "status_code": r.status_code,
                "content_length": r.content_length,
                "response_time_ms": round(r.response_time * 1000, 2),
                "redirect_url": r.redirect_url,
                "title": r.title,
                "category": r.category,
                "depth": r.depth,
                "lines_count": r.lines_count,
                "words_count": r.words_count,
            }
            for r in results
        ],
    }

    # Populate status breakdown
    for r in results:
        code_str = str(r.status_code)
        report_data["summary"]["status_breakdown"][code_str] = (
            report_data["summary"]["status_breakdown"].get(code_str, 0) + 1
        )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    return output_path
