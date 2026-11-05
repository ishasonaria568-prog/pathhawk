#!/usr/bin/env bash
# ==============================================================================
# PathHawk Clean Uninstaller
# Developed by ISHA SONARIA | Isha Sonaria Security Tools
# ==============================================================================

set -e

RED="\033[1;31m"
GREEN="\033[1;32m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RESET="\033[0m"

echo -e "${RED}"
echo "=========================================================="
echo "      PathHawk Uninstaller - ISHA SONARIA Tools          "
echo "=========================================================="
echo -e "${RESET}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
USER_BIN="${HOME}/.local/bin/pathhawk"

# 1. Remove virtual environment if present
if [ -d "${VENV_DIR}" ]; then
    echo -e "${CYAN}[*] Removing virtual environment (${VENV_DIR})...${RESET}"
    rm -rf "${VENV_DIR}"
    echo -e "${GREEN}[+] Virtual environment removed.${RESET}"
fi

# 2. Uninstall pip package if installed in user/system environment
if command -v pip &>/dev/null; then
    echo -e "${CYAN}[*] Uninstalling pathhawk python package...${RESET}"
    pip uninstall -y pathhawk 2>/dev/null || true
fi

# 3. Remove user bin wrapper
if [ -f "${USER_BIN}" ]; then
    echo -e "${CYAN}[*] Removing ${USER_BIN}...${RESET}"
    rm -f "${USER_BIN}"
    echo -e "${GREEN}[+] Binary wrapper removed.${RESET}"
fi

# 4. Clean build artifacts and pycache without touching reports or custom wordlists
echo -e "${CYAN}[*] Cleaning python cache files...${RESET}"
find "${SCRIPT_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${SCRIPT_DIR}" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "${SCRIPT_DIR}" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

echo ""
echo -e "${GREEN}[+] PathHawk has been completely uninstalled.${RESET}"
echo -e "${YELLOW}[!] Notice: Custom wordlists in 'wordlists/' and scan reports were preserved.${RESET}"
