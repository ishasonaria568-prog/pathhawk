# PathHawk – Advanced Web Asset Discovery & Reconnaissance Tool

```text
 ██████╗  █████╗ ████████╗██╗  ██╗██╗  ██╗ █████╗ ██╗    ██╗██╗  ██╗
 ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║██║  ██║██╔══██╗██║    ██║██║ ██╔╝
 ██████╔╝███████║   ██║   ███████║███████║███████║██║ █╗ ██║█████╔╝ 
 ██╔═══╝ ██╔══██║   ██║   ██╔══██║██╔══██║██╔══██║██║███╗██║██╔═██╗ 
 ██║     ██║  ██║   ██║   ██║  ██║██║  ██║██║  ██║╚███╔███╔╝██║  ██╗
 ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝
```

[![Version](https://img.shields.io/badge/version-1.0.0-00d8ff.svg)](https://github.com/ishasonaria/pathhawk)
[![Developer](https://img.shields.io/badge/developer-ISHA%20SONARIA-00ff88.svg)](https://github.com/ishasonaria)
[![Organization](https://img.shields.io/badge/organization-Isha%20Sonaria%20Security%20Tools-white.svg)](https://github.com/ishasonaria)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Tagline:** *Discover. Enumerate. Secure.*  
> **Author & Architect:** **ISHA SONARIA**  
> **Organization:** **Isha Sonaria Security Tools**

---

## 1. Project Introduction

**PathHawk** is a professional, high-performance, command-line web asset discovery and reconnaissance utility architected from the ground up by **ISHA SONARIA**. Engineered for security auditors, penetration testers, and DevSecOps practitioners performing authorized evaluations, PathHawk provides an independent, modular alternative to legacy brute-forcing utilities.

PathHawk features a terminal-optimized design with green-and-cyan telemetry, multi-threaded request multiplexing, granular HTTP/size filters, depth-bounded recursive scanning, DNS subdomain inventory discovery, and multi-format reporting (JSON, CSV, and interactive HTML dashboards).

---

## 2. Key Features

- **Web Directory Enumeration (`pathhawk dir`)**:
  - Discover hidden directories, routes, and API endpoints.
  - Custom or baseline wordlists with deduplication and comment filtering.
  - Multi-status filtering (`--status 200,301,403`) and code exclusions (`--exclude-status 404,500`).
  - Response size filtering and size exclusion (`--exclude-size 0,42`).
  - Custom HTTP request methods (`GET`, `HEAD`, `POST`, `OPTIONS`).
  - Follow or report redirect destinations.

- **Web File Enumeration (`pathhawk file`)**:
  - Discover exposed sensitive files across custom extensions (`-x php,html,txt,json,js,bak`).
  - Intelligent extension permutations and duplicate URL elimination.
  - Extracts and displays HTML `<title>` tags for immediate situational context.

- **DNS & Subdomain Inventory (`pathhawk dns`)**:
  - DNS-based subdomain discovery utilizing `dnspython`.
  - Resolves A and CNAME records concurrently.
  - Export resolved infrastructure targets directly to audit reports.

- **Controlled Recursive Discovery (`pathhawk scan`)**:
  - Depth-bounded recursive crawler (`--depth N`).
  - Path memoization prevents circular scans and duplicate requests.
  - Safe recursion avoiding infinite directory loops.

- **Multi-Format Audit Reporting (`pathhawk report`)**:
  - **JSON**: Machine-parsable output for automated CI/CD security pipelines.
  - **CSV**: Spreadsheet-ready table for compliance documentation.
  - **HTML**: Standalone, dark-themed responsive executive dashboard with status code metrics and clickable assets.

- **Responsible-Use Safeguards**:
  - Requires `--lab-mode` to run scans against local/private network addresses (localhost, RFC1918).
  - Requires `--allow-public` confirmation for scans targeting public internet domains.
  - Configurable rate limiting (`--delay`) and connection concurrency (`--threads`).

---

## 3. Installation Guide

### Kali Linux & Debian / Ubuntu

#### Option A: Quick Global Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/ishasonaria/pathhawk.git
cd pathhawk

# Install required system packages
sudo apt update && sudo apt install -y python3 python3-pip

# Install PathHawk
pip install .

# Verify installation
pathhawk --version
pathhawk --help
```

#### Option B: Virtual Environment Setup (Isolated)

```bash
# Clone the repository
git clone https://github.com/ishasonaria/pathhawk.git
cd pathhawk

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies and package
pip install -r requirements.txt
pip install -e .

# Run PathHawk inside virtualenv
pathhawk --help
```

---

### Windows (PowerShell)

```powershell
# Clone the repository
git clone https://github.com/ishasonaria/pathhawk.git
cd pathhawk

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements and package
pip install -r requirements.txt
pip install -e .

# Verify
pathhawk --version
```

---

## 4. CLI Command Reference & Examples

### A. Directory Enumeration (`pathhawk dir`)

```bash
# Scan a local lab target with default wordlist
pathhawk dir -u http://127.0.0.1:8000 --lab-mode

# Scan with custom wordlist and filter status codes
pathhawk dir -u http://127.0.0.1:8000 -w wordlists/common_dirs.txt -s 200,301,403 --lab-mode

# Scan authorized public domain with custom threads and rate limit delay
pathhawk dir -u https://example.com --allow-public -t 20 --delay 0.1 -o results.json
```

### B. File Discovery (`pathhawk file`)

```bash
# Search for files with specific extensions
pathhawk file -u http://127.0.0.1:8000 -w wordlists/common_files.txt -x php,txt,html,json --lab-mode

# Export findings to an HTML report
pathhawk file -u http://127.0.0.1:8000 -x conf,env,bak,sql -o audit_files.html --format html --lab-mode
```

### C. DNS & Subdomain Discovery (`pathhawk dns`)

```bash
# Discover active subdomains using the included wordlist
pathhawk dns -d example.local -w wordlists/subdomains.txt -t 25

# Save resolved subdomains to CSV
pathhawk dns -d example.local -o subdomains.csv --format csv
```

### D. Controlled Recursive Discovery (`pathhawk scan`)

```bash
# Perform recursive scan up to 2 levels deep
pathhawk scan -u http://127.0.0.1:8000 -w wordlists/common_dirs.txt --depth 2 --lab-mode

# Export full recursive findings to JSON
pathhawk scan -u http://127.0.0.1:8000 --depth 3 -o recursive_audit.json --lab-mode
```

### E. Standalone Report Conversion (`pathhawk report`)

```bash
# Convert existing JSON scan report to an interactive HTML report
pathhawk report -i results.json -f html -o audit_report.html

# Convert JSON scan report to CSV
pathhawk report -i results.json -f csv -o audit_report.csv
```

---

## 5. Architecture & Project Layout

```text
pathhawk/
├── __init__.py           # Package metadata and version info
├── cli.py                # Typer CLI application and command routers
├── banner.py             # ASCII banner & developer attribution
├── config.py             # ScanConfig and ScanResult dataclasses
├── core/
│   ├── engine.py         # ThreadPoolExecutor concurrency manager
│   ├── requester.py      # HTTPX client with retries and timing
│   ├── validator.py      # URL sanitation and responsible-use verification
│   └── filters.py        # Status code and response size filters
├── modules/
│   ├── directory.py      # Directory discovery implementation
│   ├── file_enum.py      # File & extension permutations
│   ├── dns_enum.py       # dnspython DNS resolver
│   └── recursive.py      # Controlled recursive scanner
├── reporting/
│   ├── json_report.py    # Structured JSON exporter
│   ├── csv_report.py     # Spreadsheet CSV exporter
│   └── html_report.py    # Standalone HTML audit report generator
└── utils/
    ├── formatter.py      # Terminal formatting & Rich color scheme
    ├── logger.py         # Logging helper utilities
    └── wordlists.py      # Wordlist loader & default wordlists
```

---

## 6. Running the Test Suite

PathHawk includes comprehensive unit and integration tests (including tests executing against local socket test servers):

```bash
# Run all tests with pytest
python3 -m pytest tests/ -v
```

All 12 automated test cases verify:
- URL normalization and scheme handling
- Target authorization safeguards (RFC1918 / localhost / public gates)
- Status code and byte size filters
- Wordlist parsing and deduplication
- Live server directory enumeration
- Live server file discovery and extension matching
- Live server recursive path discovery
- JSON, CSV, and HTML report integrity

---

## 7. Security and Responsible-Use Disclaimer

**PathHawk** is developed by **ISHA SONARIA** strictly for authorized defensive security assessments, research, educational lab training, and infrastructure owned by the operator or assessed with explicit written authorization.

- **Non-Aggressive Design**: PathHawk does not contain exploit modules, brute-force credential stuffing, authentication bypasses, or denial-of-service components.
- **Fail-Safe Target Guardrails**: Localhost and private subnet assessments require the `--lab-mode` flag. Public domain assessments require the `--allow-public` flag to affirm authorized testing.
- **Operator Liability**: The author and maintainers assume no liability for misuse, unauthorized testing, or violations of applicable local or international cybersecurity laws.

---

## 8. Uninstallation

```bash
pip uninstall pathhawk -y
```

---

## 9. License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.  
Copyright (c) 2026 **ISHA SONARIA** (Isha Sonaria Security Tools).
