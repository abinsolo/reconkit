# ReconKit
> Automated Reconnaissance Pipeline for Bug Bounty & Penetration Testing
> Built by Abin A - chains the best open-source recon tools into one
clean automated pipeline with structured output and reporting.
## Phases
| # | Phase | Tools |
|---|-----------------------|-------------------------------------|
| 1 | Subdomain Enumeration | Subfinder, Amass, Assetfinder |
| 2 | Live Host Probing | HTTPX |
| 3 | URL Discovery | GAU, Waybackurls, Katana, Hakrawler |
| 4 | JS Analysis | LinkFinder |
| 5 | Parameter Discovery | ParamSpider, Arjun |
| 6 | Report Generation | Custom Markdown Report |
## Installation
git clone https://github.com/abinsolo/reconkit
cd reconkit
chmod +x install.sh && ./install.sh
pip3 install -r requirements.txt
## Usage
python3 recon.py -d target.com # Full recon
python3 recon.py -d target.com --quick # Fast mode
python3 recon.py -d target.com --skip-amass
python3 recon.py -d target.com --skip-js
## Example Output
[+] Unique subdomains: 47
[+] Live hosts found: 23
[+] Total URLs: 1,842
[+] Juicy endpoints: 34
## Legal
Only use on targets you have explicit permission to test.
## Author
Abin A - Bug Bounty Researcher | Penetration Tester
LinkedIn: linkedin.com/in/abin-a-937196382
