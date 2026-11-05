#!/usr/bin/env bash
# ==============================================================================
# PathHawk Automated Installer for Kali Linux, Debian, & Ubuntu
# Developed by ISHA SONARIA | Isha Sonaria Security Tools
# 100% CLI-Only Architecture
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

# 1. Verify Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[-] Error: Python 3 is required but was not found. Please install Python 3.10+${RESET}"
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${GREEN}[+] Detected Python version: ${PY_VER}${RESET}"

# 2. Check and initialize isolated virtual environment (recommended for Kali Linux PEP 668 compliance)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

echo -e "${CYAN}[*] Setting up Python virtual environment in ${VENV_DIR}...${RESET}"

if ! python3 -m venv "${VENV_DIR}" 2>/dev/null; then
    echo -e "${YELLOW}[!] Notice: 'python3 -m venv' unavailable. Installing using user environment or ensure python3-venv is installed.${RESET}"
    python3 -m pip install --upgrade pip setuptools wheel --quiet 2>/dev/null || true
    python3 -m pip install -r "${SCRIPT_DIR}/requirements.txt" --quiet
    python3 -m pip install "${SCRIPT_DIR}" --quiet
    INSTALL_TARGET="system"
else
    # Inside virtual environment
    source "${VENV_DIR}/bin/activate"
    echo -e "${GREEN}[+] Virtual environment activated.${RESET}"
    pip install --upgrade pip setuptools wheel --quiet
    pip install -r "${SCRIPT_DIR}/requirements.txt" --quiet
    pip install "${SCRIPT_DIR}" --quiet
    INSTALL_TARGET="venv"
fi

# 3. Create or symlink the global pathhawk wrapper for user convenience
USER_BIN_DIR="${HOME}/.local/bin"
mkdir -p "${USER_BIN_DIR}"

if [ "${INSTALL_TARGET}" = "venv" ]; then
    cat << 'EOF' > "${USER_BIN_DIR}/pathhawk"
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Locate installation venv
if [ -f "${HOME}/pathhawk/.venv/bin/pathhawk" ]; then
    exec "${HOME}/pathhawk/.venv/bin/pathhawk" "$@"
elif [ -f "$(dirname $(readlink -f $0))/../../.venv/bin/pathhawk" ]; then
    exec "$(dirname $(readlink -f $0))/../../.venv/bin/pathhawk" "$@"
else
    # Fallback directly to python execution
    python3 -m pathhawk.cli "$@"
fi
EOF
    chmod +x "${USER_BIN_DIR}/pathhawk"
fi

echo ""
echo -e "${GREEN}[+] PathHawk CLI installed successfully!${RESET}"
echo -e "${CYAN}==========================================================${RESET}"
echo -e "${GREEN}Developer    :${RESET} ISHA SONARIA"
echo -e "${GREEN}Organization :${RESET} Isha Sonaria Security Tools"
echo -e "${GREEN}Version      :${RESET} 1.0.0"
echo -e "${CYAN}==========================================================${RESET}"
echo ""
echo -e "${YELLOW}Usage Instructions:${RESET}"
if [ "${INSTALL_TARGET}" = "venv" ]; then
    echo -e "  1. Activate virtual environment:  ${CYAN}source .venv/bin/activate${RESET}"
    echo -e "  2. Or run directly:               ${CYAN}python3 bin/pathhawk --help${RESET}"
fi
echo -e "  3. Verify installation:           ${CYAN}pathhawk --version${RESET}"
echo -e "  4. Directory reconnaissance:      ${CYAN}pathhawk dir -u https://target.local --lab-mode${RESET}"
echo ""
