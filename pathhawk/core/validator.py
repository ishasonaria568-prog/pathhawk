"""
Target and URL validation safeguards for PathHawk.
Developed by ISHA SONARIA.
"""

import ipaddress
import re
from urllib.parse import urlparse
from typing import Tuple


def normalize_target_url(url: str) -> str:
    """Normalize a target URL by adding default scheme and stripping trailing slash."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL target: {url}")

    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
    return normalized


def is_private_or_loopback(hostname_or_ip: str) -> bool:
    """Check if target host resolves to localhost, private IP, or RFC1918 range."""
    # Check common localhost strings
    hostname = hostname_or_ip.lower().split(":")[0]
    if hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        return True

    # Try parsing as IP address directly
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        pass

    return False


def validate_target(target: str, allow_public: bool = False, lab_mode: bool = False) -> Tuple[bool, str]:
    """
    Validate target and apply responsible-use safeguards.
    - If lab_mode is False and target is localhost/private IP -> blocked unless lab_mode=True
    - If allow_public is False and target is public -> blocked unless allow_public=True
    """
    try:
        norm_url = normalize_target_url(target)
        parsed = urlparse(norm_url)
        host = parsed.hostname or parsed.netloc
    except Exception as e:
        return False, f"Malformed target URL '{target}': {e}"

    is_internal = is_private_or_loopback(host)

    if is_internal and not lab_mode:
        return False, (
            f"Target host '{host}' is in private/loopback address space. "
            f"To assess local educational labs or sandbox environments, provide the '--lab-mode' flag."
        )

    if not is_internal and not allow_public:
        return False, (
            f"Target host '{host}' appears to be a public Internet system. "
            f"To confirm you have authorized written permission to assess this target, "
            f"provide the '--allow-public' flag."
        )

    return True, norm_url


def validate_domain(domain: str) -> bool:
    """Validate RFC-compliant domain name format."""
    domain = domain.strip().lower()
    pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})+$"
    return bool(re.match(pattern, domain))
