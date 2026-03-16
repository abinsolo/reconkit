#!/usr/bin/env python3
"""
ReconKit - Automated Reconnaissance Pipeline
Author: Abin A | github.com/abinsolo
"""
import os, argparse, datetime
from rich.console import Console
from modules import subdomains, probing, crawling, reporting
console = Console()

BANNER = """
██████╗ ███████╗ ██████╗ ██████╗ ███╗  ██╗██╗  ██╗██╗████████╗
██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗ ██║██║ ██╔╝██║╚══██╔══╝
██████╔╝█████╗  ██║     ██║   ██║██╔██╗██║█████╔╝ ██║   ██║
██╔══██╗██╔══╝  ██║     ██║   ██║██║╚████║██╔═██╗ ██║   ██║
██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚███║██║  ██╗██║   ██║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚══╝╚═╝  ╚═╝╚═╝   ╚═╝
          Automated Recon Pipeline | by Abin A
"""

def create_output_dir(domain):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"output/{domain}_{ts}"
    os.makedirs(path, exist_ok=True)
    console.log(f"[green][+][/green] Output: {path}")
    return path

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="ReconKit by Abin A")
    parser.add_argument("-d", "--domain",   required=True,       help="Target domain e.g. example.com")
    parser.add_argument("--skip-amass",     action="store_true", help="Skip Amass (much faster)")
    parser.add_argument("--skip-js",        action="store_true", help="Skip JS / LinkFinder analysis")
    parser.add_argument("--quick",          action="store_true", help="Subdomains + live hosts only")
    args = parser.parse_args()
    domain = args.domain
    out = create_output_dir(domain)
    console.print(f"\n[bold cyan]Target:[/bold cyan] {domain}\n")
    subdomains.run_enum(domain, out,skip_amass=args.skip_amass)
    probing.probe(out)
    if not args.quick:
        crawling.crawl(domain, out, skip_js=args.skip_js)
    reporting.generate(domain, out)

if __name__ == "__main__":
    main()
