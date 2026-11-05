from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from typer.testing import CliRunner

from pathhawk.cli import app
from pathhawk.config import ScanConfig, ScanResult
from pathhawk.core.validator import validate_domain, validate_target
from pathhawk.modules.dns_enum import DNSEnumerator

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "PathHawk version 1.0.0" in result.output
    assert "ISHA SONARIA" in result.output


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "dir" in result.output
    assert "file" in result.output
    assert "dns" in result.output
    assert "scan" in result.output
    assert "report" in result.output


def test_cli_dir_missing_url():
    result = runner.invoke(app, ["dir"])
    assert result.exit_code != 0
    assert "Missing option" in result.output or "Error" in result.output


def test_cli_dir_invalid_target_safety():
    # Attempting to scan a public URL without --allow-public must fail safely
    result = runner.invoke(app, ["dir", "-u", "https://unauthorized-public-site.com"])
    assert result.exit_code != 0
    assert "public Internet system" in result.output


def test_cli_dir_local_target_safety():
    # Attempting to scan localhost without --lab-mode must fail safely
    result = runner.invoke(app, ["dir", "-u", "http://127.0.0.1:8000"])
    assert result.exit_code != 0
    assert "private/loopback" in result.output


def test_cli_dir_missing_wordlist_fails(tmp_path: Path):
    non_existent = tmp_path / "does_not_exist.txt"
    result = runner.invoke(app, ["dir", "-u", "http://127.0.0.1:8000", "-w", str(non_existent), "--lab-mode"])
    # Should catch FileNotFoundError or return non-zero
    assert result.exit_code != 0


def test_cli_dns_invalid_domain():
    result = runner.invoke(app, ["dns", "-d", "not_a_valid_domain!!"])
    assert result.exit_code != 0
    assert "Invalid domain" in result.output


def test_cli_report_missing_file(tmp_path: Path):
    missing_file = tmp_path / "absent.json"
    result = runner.invoke(app, ["report", "-i", str(missing_file)])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_dns_records_mock():
    config = ScanConfig(domain="example.com", threads=2, timeout=2.0)
    enumerator = DNSEnumerator(config)

    with patch.object(enumerator.resolver, "resolve") as mock_resolve:
        mock_a = MagicMock()
        mock_a.__str__.return_value = "93.184.216.34"
        mock_resolve.return_value = [mock_a]

        records = enumerator.query_record("example.com", "A")
        assert "93.184.216.34" in records
