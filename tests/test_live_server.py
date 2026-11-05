import http.server
import socketserver
import threading
from pathlib import Path
import pytest
from pathhawk.config import ScanConfig
from pathhawk.modules.directory import DirectoryEnumerator
from pathhawk.modules.file_enum import FileEnumerator
from pathhawk.modules.recursive import RecursiveScanner


class MockLabServerHandler(http.server.SimpleHTTPRequestHandler):
    """Mock HTTP server simulating an authorized educational web environment."""

    def do_GET(self):
        path = self.path

        if path == "/admin/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><head><title>Admin Portal</title></head><body>Admin Section</body></html>")
        elif path == "/admin/config/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><head><title>Admin Config</title></head><body>Config Data</body></html>")
        elif path == "/login/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><head><title>Login</title></head><body>Login Page</body></html>")
        elif path == "/secret/":
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden Area")
        elif path == "/old/":
            self.send_response(301)
            self.send_header("Location", "/new/")
            self.end_headers()
        elif path == "/config.php":
            self.send_response(200)
            self.send_header("Content-Type", "application/x-httpd-php")
            self.end_headers()
            self.wfile.write(b"<?php $db = 'secret'; ?>")
        elif path == "/robots.txt":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"User-agent: *\nDisallow: /admin/")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def log_message(self, format, *args):
        # Silence server request logs during test runs
        pass


@pytest.fixture(scope="module")
def mock_server():
    server = socketserver.TCPServer(("127.0.0.1", 0), MockLabServerHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    yield base_url
    server.shutdown()
    server.server_close()


def test_directory_enumeration_against_server(mock_server, tmp_path: Path):
    wfile = tmp_path / "dirs.txt"
    wfile.write_text("admin\nlogin\nsecret\nnotfound\n", encoding="utf-8")

    config = ScanConfig(
        target_url=mock_server,
        wordlist_path=wfile,
        status_codes={200, 403},
        threads=4,
        lab_mode=True,
        silent=True,
    )
    enumerator = DirectoryEnumerator(config)
    results = enumerator.run()

    found_urls = {r.url for r in results}
    assert f"{mock_server}/admin/" in found_urls
    assert f"{mock_server}/login/" in found_urls
    assert f"{mock_server}/secret/" in found_urls
    assert f"{mock_server}/notfound/" not in found_urls


def test_file_enumeration_against_server(mock_server, tmp_path: Path):
    wfile = tmp_path / "files.txt"
    wfile.write_text("config\nrobots\nmissing\n", encoding="utf-8")

    config = ScanConfig(
        target_url=mock_server,
        wordlist_path=wfile,
        extensions=["php", "txt"],
        status_codes={200},
        threads=4,
        lab_mode=True,
        silent=True,
    )
    enumerator = FileEnumerator(config)
    results = enumerator.run()

    found_urls = {r.url for r in results}
    assert f"{mock_server}/config.php" in found_urls
    assert f"{mock_server}/robots.txt" in found_urls
    assert f"{mock_server}/missing.php" not in found_urls


def test_recursive_enumeration_against_server(mock_server, tmp_path: Path):
    wfile = tmp_path / "recursive_words.txt"
    wfile.write_text("admin\nconfig\n", encoding="utf-8")

    config = ScanConfig(
        target_url=mock_server,
        wordlist_path=wfile,
        max_depth=2,
        status_codes={200},
        threads=4,
        lab_mode=True,
        silent=True,
    )
    scanner = RecursiveScanner(config)
    results = scanner.run()

    found_urls = {r.url for r in results}
    assert f"{mock_server}/admin/" in found_urls
    assert f"{mock_server}/admin/config/" in found_urls
