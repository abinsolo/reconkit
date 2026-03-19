#!/bin/bash
# ----------------------------------------
# Install required Go-based tools
# ----------------------------------------
echo "[*] Installing Go tools..."
install_go_tool() {
    TOOL=$1
    CMD=$2

    if command -v "$CMD" >/dev/null 2>&1; then
        echo "[✓] $CMD already installed, skipping..."
    else
        echo "[+] Installing $CMD..."
        go install "$TOOL"
    fi
}

install_go_tool github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest subfinder
install_go_tool github.com/projectdiscovery/httpx/cmd/httpx@latest httpx
install_go_tool github.com/projectdiscovery/katana/cmd/katana@latest katana
install_go_tool github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest nuclei
install_go_tool github.com/tomnomnom/assetfinder@latest assetfinder
install_go_tool github.com/tomnomnom/waybackurls@latest waybackurls
install_go_tool github.com/hakluke/hakrawler@latest hakrawler
install_go_tool github.com/lc/gau/v2/cmd/gau@latest gau
install_go_tool github.com/owasp-amass/amass/v4/...@master amass

# ----------------------------------------
# Install required Python-based tools
# ----------------------------------------
echo "[*] Installing Python tools..."
# Function to install Python packages only if not already installed
install_python_tool() {
    TOOL=$1

    if pip3 show "$TOOL" >/dev/null 2>&1; then
        echo "[✓] $TOOL already installed, skipping..."
    else
        echo "[+] Installing $TOOL..."
        pip3 install "$TOOL" --break-system-packages
    fi
}

# Install required Python tools
install_python_tool arjun
install_python_tool paramspider


# ----------------------------------------
# Clone external dependencies (LinkFinder)
# ----------------------------------------
echo "[*] Cloning LinkFinder..."

if [ -d "LinkFinder" ]; then
    echo "[✓] LinkFinder already exists, skipping..."
else
    git clone https://github.com/GerbenJavado/LinkFinder.git
fi

# ----------------------------------------
# Install Python dependencies
# ----------------------------------------
echo "[*] Installing LinkFinder dependencies..."
pip3 install -r LinkFinder/requirements.txt --break-system-packages

echo "[*] Installing project dependencies..."
pip3 install -r requirements.txt --break-system-packages


# ----------------------------------------
# Add Go binary path to PATH (only once)
# ----------------------------------------

# Avoid duplicate PATH entry
if ! grep -q 'go env GOPATH' ~/.bashrc; then
    echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
fi

# Reload shell configuration
source ~/.bashrc


echo "[+] Done! All tools installed."
