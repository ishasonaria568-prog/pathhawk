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
[![CLI Only](https://img.shields.io/badge/architecture-100%25%20CLI%20Only-cyan.svg)](https://github.com/ishasonaria/pathhawk)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Tagline:** *Discover. Enumerate. Secure.*  
> **Author & Architect:** **ISHA SONARIA**  
> **Organization:** **Isha Sonaria Security Tools**  
> **Interface:** 100% Terminal CLI Only (No Web Server, No Browser, No GUI)

---

## 1. Project Introduction

**PathHawk** is a dedicated, 100% CLI-only web asset discovery and reconnaissance tool built from the ground up by **ISHA SONARIA**. Engineered specifically for security professionals, penetration testers, and security researchers operating on **Kali Linux, Debian, and Ubuntu**, PathHawk operates entirely inside the terminal without any web server, frontend dependencies, or browser requirements.

PathHawk provides high-speed multi-threaded directory enumeration, file discovery with extension permutations, DNS record lookups, subdomain mapping, controlled recursive crawling, and offline audit report exports (JSON, CSV, and standalone HTML files).

---

## 2. Core Features & Capabilities

- **100% Command-Line Interface**:
  - Pure terminal execution using Python, `typer`, `rich`, `httpx`, and `dnspython`.
  - Zero browser dependencies, no Node.js/npm runtimes, no local web dashboards.

- **Web Directory Enumeration (`pathhawk dir`)**:
  - Discover hidden directories and web routes using custom or built-in wordlists.
  - Filter by HTTP status codes (`-s 200,301,403`) and exclude noise codes (`-b 404,500`).
  - Response size filtering and size exclusion (`--exclude-size 0,42`).
  - Custom HTTP request methods (`GET`, `HEAD`, `POST`, `OPTIONS`).
  - Follow or report redirect destinations (`-r`).

- **Web File Enumeration (`pathhawk file`)**:
  - Discover sensitive or exposed files with custom extensions (`-x php,html,txt,json,js,bak`).
  - Automatic deduplication and intelligent file extension permutations.
  - Extracts HTML page `<title>` for fast visual identification.

- **DNS Reconnaissance & Subdomains (`pathhawk dns`)**:
  - Apex record queries: `A`, `AAAA`, `MX`, `NS`, `TXT`, `CNAME`, `SOA`.
  - Concurrent subdomain enumeration with custom or baseline dictionary wordlists.

- **Multi-Stage Combined Scan (`pathhawk scan`)**:
  - Executes directory enumeration, file discovery, and controlled recursion in a single pass.
  - Configurable maximum recursion depth (`--depth N`).
  - Visited-route memoization prevents infinite loops and circular requests.

- **Offline Audit Reporting (`pathhawk report`)**:
  - Generates offline JSON, CSV, or standalone HTML reports directly to the disk without launching any browser or server.
  - Reports include target information, configuration, timestamp, findings, response sizes, and latencies.

- **Responsible Security Safeguards**:
  - Refuses private/loopback targets (`localhost`, `127.0.0.1`, RFC1918) unless `--lab-mode` is explicitly provided.
  - Requires `--allow-public` confirmation for public internet targets.
  - Safe concurrency defaults (`--threads`) and rate-limiting delays (`--delay`).

---

## 3. Installation Guide (Kali Linux / Debian / Ubuntu)

### Quick Automated Installation

```bash
git clone https://github.com/ishasonaria/pathhawk.git
cd pathhawk
chmod +x install.sh
./install.sh
```

The installer verifies Python 3.10+, provisions an isolated virtual environment (`.venv`) complying with Kali Linux PEP 668 guidelines, installs all dependencies, and links the `pathhawk` executable into `~/.local/bin/`.

### Manual Virtual Environment Setup

```bash
# 1. Ensure Python 3.10+ and venv are installed
sudo apt update && sudo apt install -y python3 python3-venv python3-pip

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies and PathHawk
pip install --upgrade pip
pip install -r requirements.txt
pip install .

# 4. Verify installation
pathhawk --version
pathhawk --help
```

---

## 4. CLI Command Reference & Examples

### General Options

```bash
# Display version and developer information
pathhawk --version

# Display main help menu
pathhawk --help
```

### A. Directory Enumeration (`pathhawk dir`)

```bash
# Scan a local lab web server
pathhawk dir -u http://127.0.0.1:8000 --lab-mode

# Scan with custom wordlist and status code filter
pathhawk dir -u http://127.0.0.1:8000 -w wordlists/common_dirs.txt -s 200,301,403 --lab-mode

# Scan an authorized public domain with rate limiting and thread control
pathhawk dir -u https://target.example --allow-public -t 20 --delay 0.1 -o scan_dirs.json
```

### B. File Discovery (`pathhawk file`)

```bash
# Search for files with specific extensions
pathhawk file -u http://127.0.0.1:8000 -w wordlists/common_files.txt -x php,txt,html,json --lab-mode

# Filter out empty responses and export to CSV
pathhawk file -u http://127.0.0.1:8000 -x env,bak,conf,sql -o discovered_files.csv --format csv --lab-mode
```

### C. DNS Reconnaissance (`pathhawk dns`)

```bash
# Retrieve common DNS records (A, AAAA, MX, NS, TXT, CNAME) and discover subdomains
pathhawk dns -d example.local -w wordlists/subdomains.txt

# Fast DNS inventory with 30 threads
pathhawk dns -d example.local -t 30 -o subdomains.json
```

### D. Comprehensive Combined Scan (`pathhawk scan`)

```bash
# Run directory and file discovery with controlled recursion depth
pathhawk scan -u http://127.0.0.1:8000 --depth 2 -x php,txt,html --lab-mode -o combined.json
```

### E. Standalone Report Conversion (`pathhawk report`)

```bash
# Convert a raw JSON scan result to a standalone offline HTML audit report
pathhawk report -i results.json --format html -o audit_report.html

# Convert JSON findings to CSV for spreadsheet review
pathhawk report -i results.json --format csv -o audit_report.csv
```

---

## 5. Project Architecture

```text
pathhawk/
├── bin/
│   └── pathhawk          # Direct executable launcher
├── pathhawk/
│   ├── __init__.py       # Package metadata and version info
│   ├── banner.py         # Terminal banner & developer attribution
│   ├── cli.py            # Typer CLI application and command routers
│   ├── config.py         # ScanConfig and ScanResult dataclasses
│   ├── core/
│   │   ├── engine.py     # ThreadPoolExecutor concurrency manager
│   │   ├── requester.py  # HTTPX client with retries and timing
│   │   ├── validator.py  # URL sanitation and target guardrails
│   │   └── filters.py    # Status code and response size filters
│   ├── modules/
│   │   ├── directory.py  # Directory discovery implementation
│   │   ├── file_enum.py  # File & extension permutations
│   │   ├── dns_enum.py   # DNS record and subdomain enumerator
│   │   ├── recursive.py  # Depth-controlled recursive crawler
│   │   └── combined.py   # Multi-stage combined discovery coordinator
│   ├── reporting/
│   │   ├── json_report.py # Structured JSON exporter
│   │   ├── csv_report.py  # Spreadsheet CSV exporter
│   │   └── html_report.py # Standalone offline HTML audit report generator
│   └── utils/
│       ├── formatter.py  # Terminal formatting & Rich color scheme
│       ├── logger.py     # Logging helpers
│       └── wordlists.py  # Wordlist loader & built-in dictionaries
├── wordlists/            # Curated default dictionaries
├── tests/                # Automated pytest suite (unit and live socket tests)
├── docs/                 # Documentation and sample offline report templates
├── install.sh            # Automated Kali/Debian/Ubuntu installation script
├── uninstall.sh          # Clean uninstaller script
├── requirements.txt      # Python dependencies
├── pyproject.toml        # PEP 517 build configuration
├── LICENSE               # MIT License
└── README.md             # Complete user and technical documentation
```

---

## 6. Running the Automated Test Suite

PathHawk includes 21 comprehensive automated tests covering unit logic, CLI invocations, error handling, safety checks, and integration against live local HTTP socket test servers:

```bash
# Run tests with pytest
python3 -m pytest tests/ -v
```

All 21 test cases verify:
- CLI flags (`--version`, `--help`, missing arguments)
- Target safety guardrails (`--lab-mode` and `--allow-public`)
- Missing wordlist error handling
- URL normalization and RFC-compliant domain validation
- Response status code and size filtering
- Live mock server directory discovery
- Live mock server file and extension permutations
- Live mock server recursive traversal
- DNS record extraction and mock lookup
- JSON, CSV, and offline HTML report generation

---

## 7. Troubleshooting

- **`externally-managed-environment` on Kali Linux**:  
  Kali Linux follows PEP 668. Always install PathHawk inside a virtual environment using `./install.sh` or `python3 -m venv .venv && source .venv/bin/activate`.
- **Target blocked: `private/loopback address space`**:  
  When testing local containers, VMs, or localhost, supply the `--lab-mode` flag.
- **Target blocked: `public Internet system`**:  
  When assessing an authorized public host, supply the `--allow-public` flag.

---

## 8. Uninstallation

To remove PathHawk and its virtual environment cleanly without affecting generated reports or custom wordlists:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

---

## 9. License & Credits

Developed by **ISHA SONARIA**  
Organization: **Isha Sonaria Security Tools**  
Licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
