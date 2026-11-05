import json
from pathlib import Path
from pathhawk.config import ScanConfig, ScanResult
from pathhawk.reporting.json_report import generate_json_report
from pathhawk.reporting.csv_report import generate_csv_report
from pathhawk.reporting.html_report import generate_html_report


def test_json_reporting(tmp_path: Path):
    out = tmp_path / "report.json"
    config = ScanConfig(target_url="https://lab.test", lab_mode=True)
    results = [
        ScanResult(url="https://lab.test/admin/", status_code=200, content_length=150, response_time=0.05, category="directory"),
        ScanResult(url="https://lab.test/config.php", status_code=403, content_length=45, response_time=0.03, category="file"),
    ]

    generated = generate_json_report(config, results, out)
    assert generated.is_file()

    with open(generated, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["metadata"]["tool"] == "PathHawk"
    assert data["metadata"]["developer"] == "ISHA SONARIA"
    assert data["summary"]["total_findings"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["url"] == "https://lab.test/admin/"


def test_csv_reporting(tmp_path: Path):
    out = tmp_path / "report.csv"
    config = ScanConfig(target_url="https://lab.test", lab_mode=True)
    results = [
        ScanResult(url="https://lab.test/admin/", status_code=200, content_length=150, response_time=0.05, category="directory"),
    ]

    generated = generate_csv_report(config, results, out)
    assert generated.is_file()
    content = generated.read_text(encoding="utf-8")
    assert "ISHA SONARIA" in content
    assert "https://lab.test/admin/" in content


def test_html_reporting(tmp_path: Path):
    out = tmp_path / "report.html"
    config = ScanConfig(target_url="https://lab.test", lab_mode=True)
    results = [
        ScanResult(url="https://lab.test/admin/", status_code=200, content_length=150, response_time=0.05, category="directory"),
    ]

    generated = generate_html_report(config, results, out)
    assert generated.is_file()
    content = generated.read_text(encoding="utf-8")
    assert "ISHA SONARIA" in content
    assert "PathHawk" in content
    assert "badge-success" in content
    assert "https://lab.test/admin/" in content
