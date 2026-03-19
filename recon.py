#!/usr/bin/env python3
"""
ReconKit - Automated Reconnaissance Pipeline
Author: Abin A | github.com/abinsolo
"""

import os
import argparse
import datetime
import subprocess
import sys
from rich.console import Console
from modules import subdomains, probing, crawling, scanning, reporting

# Initialize rich console for styled output
console = Console()


# ----------------------------------------
# Tool validation
# Ensures required external tools are installed
# ----------------------------------------
def check_tools():
    required = [
        "subfinder", "httpx", "katana", "gau",
        "waybackurls", "hakrawler", "assetfinder", "nuclei"
    ]

    missing = []

    # Check each tool using `which`
    for tool in required:
        result = subprocess.run(f"which {tool}", shell=True, capture_output=True)
        if result.returncode != 0:
            missing.append(tool)

    # If any tool is missing → stop execution
    if missing:
        console.print(f"[red][!] Missing: {', '.join(missing)}[/red]")
        console.print("[yellow]Fix: source ~/.bashrc then re-run[/yellow]")
        sys.exit(1)

    console.log("[green][+][/green] All tools verified")


# ----------------------------------------
# Scope filtering
# Filters subdomains based on provided scope file
# ----------------------------------------
def apply_scope_filter(subdomain_file, scope_file):
    # If no scope file or file does not exist → skip
    if not scope_file or not os.path.exists(scope_file):
        return

    # Read scope domains and normalize
    scope_domains = [
        line.strip().lstrip("*.")
        for line in open(scope_file).readlines()
        if line.strip()
    ]

    # Read all discovered subdomains
    all_subs = open(subdomain_file).readlines()

    # Keep only subdomains that match scope
    in_scope = [
        sub for sub in all_subs
        if any(sub.strip().endswith(domain) for domain in scope_domains)
    ]

    # Overwrite file with filtered results
    with open(subdomain_file, "w") as f:
        f.writelines(in_scope)

    console.log(f"[green][+][/green] Scope: {len(in_scope)}/{len(all_subs)} in scope")


# ----------------------------------------
# Banner displayed on start
# ----------------------------------------
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
# Supports custom output directory if provided
# ----------------------------------------
def create_output_dir(domain, custom_dir=None):
    if custom_dir:
        # Use user-defined output directory
        path = custom_dir
    else:
        # Default: create timestamp-based directory
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"output/{domain}_{ts}"

    # Ensure directory exists
    os.makedirs(path, exist_ok=True)

    console.log(f"[green][+][/green] Output: {path}")
    return path


# ----------------------------------------
# Main execution pipeline
# ----------------------------------------
def main():
    # Display banner
    print(BANNER)

    # Verify required tools before execution
    check_tools()

    # -------------------------------
    # Argument parsing (CLI options)
    # -------------------------------
    parser = argparse.ArgumentParser(description="ReconKit by Abin A")

    # Target domain (required)
    parser.add_argument(
        "-d", "--domain",
        required=True,
        help="Target domain e.g. example.com"
    )

    # Optional flags to control pipeline
    parser.add_argument("--skip-amass", action="store_true", help="Skip Amass (faster)")
    parser.add_argument("--skip-js", action="store_true", help="Skip JS analysis")
    parser.add_argument("--quick", action="store_true", help="Subdomains + live hosts only")

    # Additional features from upstream
    parser.add_argument("--skip-scan", action="store_true", help="Skip Nuclei scan")
    parser.add_argument("--scope", help="Path to scope file")

    # 🔥 YOUR FEATURE: Custom output directory
    parser.add_argument("--output-dir", help="Custom output directory")

    args = parser.parse_args()

    domain = args.domain

    # Create output directory (custom or default)
    out = create_output_dir(domain, args.output_dir)

    console.print(f"\n[bold cyan]Target:[/bold cyan] {domain}\n")

    # -------------------------------
    # Phase 1: Subdomain Enumeration
    # -------------------------------
    subdomains.run_enum(domain, out, skip_amass=args.skip_amass)

    # Apply scope filtering if provided
    apply_scope_filter(f"{out}/all_subdomains.txt", args.scope)

    # -------------------------------
    # Phase 2: Live Host Probing
    # -------------------------------
    probing.probe(out)

    # -------------------------------
    # Phase 3: Crawling & Scanning
    # -------------------------------
    if not args.quick:
        crawling.crawl(domain, out, skip_js=args.skip_js)

        if not args.skip_scan:
            scanning.scan(out)

    # -------------------------------
    # Phase 4: Reporting
    # -------------------------------
    reporting.generate(domain, out)


# Entry point
if __name__ == "__main__":
    main()