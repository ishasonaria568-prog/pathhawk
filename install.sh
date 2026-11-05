#!/usr/bin/env bash
# ==============================================================================
# PathHawk Automated Installer for Kali Linux, Debian, & Ubuntu
# Developed by ISHA SONARIA | Isha Sonaria Security Tools
# ==============================================================================

set -e

GREEN="\033[1;32m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

echo -e "${CYAN}"
echo "=========================================================="
echo "      PathHawk Installer - Developed by ISHA SONARIA     "
echo "               Discover. Enumerate. Secure.               "
echo "=========================================================="
echo -e "${RESET}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[-] Python 3 is required but was not found. Please install Python 3.10+${RESET}"
    exit 1
fi

echo -e "${GREEN}[+] Detected Python version: $(python3 --version)${RESET}"

# Upgrade pip and install wheel
echo -e "${CYAN}[*] Ensuring pip and setuptools are present...${RESET}"
python3 -m pip install --upgrade pip setuptools wheel --quiet 2>/dev/null || true

# Install dependencies and PathHawk
echo -e "${CYAN}[*] Installing PathHawk and requirements...${RESET}"
python3 -m pip install -r requirements.txt --quiet
python3 -m pip install . --quiet

echo -e "${GREEN}[+] PathHawk installed successfully!${RESET}"
echo -e "${CYAN}[*] Verification:${RESET}"
pathhawk --version || python3 -m pathhawk.cli --version

echo ""
echo -e "${GREEN}[+] You can now run 'pathhawk --help' anywhere on your system.${RESET}"
