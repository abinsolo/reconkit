#!/bin/bash
echo "[*] Installing Go tools..."
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/tomnomnom/assetfinder@latest
go install github.com/tomnomnom/waybackurls@latest
go install github.com/hakluke/hakrawler@latest
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/owasp-amass/amass/v4/...@master

echo "[*] Installing Python tools..."
pip3 install arjun paramspider --break-system-packages
echo "[*] Cloning LinkFinder..."
git clone https://github.com/GerbenJavado/LinkFinder.git 2>/dev/null
pip3 install -r LinkFinder/requirements.txt --break-system-packages
echo "[*] Installing Python dependencies..."
pip3 install -r requirements.txt --break-system-packages
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
source ~/.bashrc
echo "[+] Done! All tools installed."
