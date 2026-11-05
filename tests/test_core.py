from pathlib import Path
import pytest
from pathhawk.core.validator import is_private_or_loopback, normalize_target_url, validate_domain, validate_target
from pathhawk.core.filters import ResultFilter
from pathhawk.config import ScanConfig, ScanResult
from pathhawk.utils.wordlists import load_wordlist, get_default_wordlist


def test_normalize_target_url():
    assert normalize_target_url("example.com") == "https://example.com"
    assert normalize_target_url("http://example.com/") == "http://example.com"
    assert normalize_target_url("https://example.com/app/") == "https://example.com/app"


def test_is_private_or_loopback():
    assert is_private_or_loopback("localhost") is True
    assert is_private_or_loopback("127.0.0.1") is True
    assert is_private_or_loopback("127.0.0.1:8080") is True
    assert is_private_or_loopback("192.168.1.50") is True
    assert is_private_or_loopback("10.0.0.1") is True
    assert is_private_or_loopback("172.16.0.1") is True
    assert is_private_or_loopback("8.8.8.8") is False
    assert is_private_or_loopback("example.com") is False


def test_validate_target_safeguards():
    # Localhost rejected without lab_mode
    valid, msg = validate_target("http://127.0.0.1:8000", allow_public=False, lab_mode=False)
    assert valid is False
    assert "private/loopback" in msg

    # Localhost allowed with lab_mode
    valid, url = validate_target("http://127.0.0.1:8000", allow_public=False, lab_mode=True)
    assert valid is True
    assert url == "http://127.0.0.1:8000"

    # Public target rejected without allow_public
    valid, msg = validate_target("https://example.com", allow_public=False, lab_mode=False)
    assert valid is False
    assert "public Internet system" in msg

    # Public target allowed with allow_public
    valid, url = validate_target("https://example.com", allow_public=True, lab_mode=False)
    assert valid is True
    assert url == "https://example.com"


def test_validate_domain():
    assert validate_domain("example.com") is True
    assert validate_domain("sub.lab.internal.local") is True
    assert validate_domain("not a domain") is False
    assert validate_domain("-invalid.com") is False


def test_result_filter():
    config = ScanConfig(
        status_codes={200, 301},
        excluded_status_codes={404},
        min_size=10,
        max_size=1000,
        exclude_sizes={50},
    )
    r_filter = ResultFilter(config)

    res_ok = ScanResult(url="https://test/ok", status_code=200, content_length=100, response_time=0.1)
    assert r_filter.should_include(res_ok) is True

    res_excluded_code = ScanResult(url="https://test/404", status_code=404, content_length=100, response_time=0.1)
    assert r_filter.should_include(res_excluded_code) is False

    res_not_in_allowed = ScanResult(url="https://test/403", status_code=403, content_length=100, response_time=0.1)
    assert r_filter.should_include(res_not_in_allowed) is False

    res_too_small = ScanResult(url="https://test/small", status_code=200, content_length=5, response_time=0.1)
    assert r_filter.should_include(res_too_small) is False

    res_excluded_size = ScanResult(url="https://test/size", status_code=200, content_length=50, response_time=0.1)
    assert r_filter.should_include(res_excluded_size) is False


def test_wordlist_handling(tmp_path: Path):
    sample_file = tmp_path / "test_words.txt"
    sample_file.write_text("# Comment line\nadmin\n\nlogin\nadmin\napi\n", encoding="utf-8")

    words = load_wordlist(sample_file)
    # Deduplicated, comments and blanks removed
    assert words == ["admin", "login", "api"]

    defaults = get_default_wordlist("paths")
    assert "admin" in defaults
    assert "login" in defaults
