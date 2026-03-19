#!/usr/bin/env python3
"""
ReconKit - Automated Reconnaissance Pipeline
Author: Abin A | github.com/abinsolo
"""
import os, argparse, datetime
from rich.console import Console
from modules import subdomains, probing, crawling, reporting

# Initialize rich console for styled output
console = Console()

# Banner displayed when tool starts
BANNER = """
██████╗ ███████╗ ██████╗ ██████╗ ███╗  ██╗██╗  ██╗██╗████████╗
██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗ ██║██║ ██╔╝██║╚══██╔══╝
██████╔╝█████╗  ██║     ██║   ██║██╔██╗██║█████╔╝ ██║   ██║
██╔══██╗██╔══╝  ██║     ██║   ██║██║╚████║██╔═██╗ ██║   ██║
██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚███║██║  ██╗██║   ██║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚══╝╚═╝  ╚═╝╚═╝   ╚═╝
          Automated Recon Pipeline | by Abin A
"""

# ----------------------------------------
# Create output directory
# Supports custom directory if provided
# ----------------------------------------
def create_output_dir(domain, custom_dir=None):
    # If user provides custom directory → use it
    if custom_dir:
        path = custom_dir
    else:
        # Otherwise create timestamped directory
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"output/{domain}_{ts}"
        
    # Create directory if it does not exist
    os.makedirs(path, exist_ok=True)
    
    console.log(f"[green][+][/green] Output: {path}")
    return path

def main():
    # Print banner
    print(BANNER)
    
    # ----------------------------------------
    # Argument parsing (CLI options)
    # ----------------------------------------
    parser = argparse.ArgumentParser(description="ReconKit by Abin A")
    
    # domain
    parser.add_argument("-d", "--domain",   required=True,       help="Target domain e.g. example.com")
    
    # optional files for controlling pipeline behavious
    parser.add_argument("--skip-amass",     action="store_true", help="Skip Amass (much faster)")
    parser.add_argument("--skip-js",        action="store_true", help="Skip JS / LinkFinder analysis")
    parser.add_argument("--quick",          action="store_true", help="Subdomains + live hosts only")
    
    #Custom output directory
    parser.add_argument("--output-dir",help="Specify custom output directory")
    
    # Parse arguments
    args = parser.parse_args()
    domain = args.domain
    
    # Create output directory (custom or default)
    out = create_output_dir(domain)
    console.print(f"\n[bold cyan]Target:[/bold cyan] {domain}\n")
    
    # ----------------------------------------
    # Phase 1: Subdomain Enumeration
    # ----------------------------------------
    subdomains.run_enum(domain, out,skip_amass=args.skip_amass)
    
    # ----------------------------------------
    # Phase 2: Live Host Probing
    # ----------------------------------------
    probing.probe(out)
    
    # ----------------------------------------
    # Phase 3: Crawling + JS analysis (optional)
    # ----------------------------------------
    if not args.quick:
        crawling.crawl(domain, out, skip_js=args.skip_js)
    
    # ----------------------------------------
    # Phase 4: Report Generation
    # ----------------------------------------
    reporting.generate(domain, out)

if __name__ == "__main__":
    main()
