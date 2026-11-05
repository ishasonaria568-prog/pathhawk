"""
Filtering logic for HTTP responses in PathHawk.
Developed by ISHA SONARIA.
"""

from typing import Optional
from pathhawk.config import ScanConfig, ScanResult


class ResultFilter:
    """Evaluates whether an HTTP response matches configured filter criteria."""

    def __init__(self, config: ScanConfig):
        self.config = config

    def should_include(self, result: ScanResult) -> bool:
        # Check excluded status codes
        if result.status_code in self.config.excluded_status_codes:
            return False

        # Check allowed status codes
        if self.config.status_codes and result.status_code not in self.config.status_codes:
            return False

        # Check excluded sizes
        if result.content_length in self.config.exclude_sizes:
            return False

        # Check min size
        if self.config.min_size is not None and result.content_length < self.config.min_size:
            return False

        # Check max size
        if self.config.max_size is not None and result.content_length > self.config.max_size:
            return False

        return True
