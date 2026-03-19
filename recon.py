#!/usr/bin/env python3
"""
ReconKit - Automated Reconnaissance Pipeline
Author: Abin A | github.com/abinsolo
"""
import os, argparse, datetime, subprocess, sys
from rich.console import Console
from modules import subdomains, probing, crawling, scanning, reporting

console = Console()

# -------------------------------
# Tool validation
# -------------------------------
def check_tools():
    required = [
        "subfinder", "httpx", "katana", "gau",
        "waybackurls", "hakrawler", "assetfinder", "nuclei"
    ]
    missing = []
    for tool in required:
        r = subprocess.run(f"which {tool}", shell=True, capture_output=True)
        if r.returncode != 0:
            missing.append(tool)

    if missing:
        console.print(f"[red][!] Missing: {', '.join(missing)}[/red]")
        console.print("[yellow]Fix: source ~/.bashrc then re-run[/yellow]")
        sys.exit(1)

    console.log("[green][+][/green] All tools verified")


# -------------------------------
# Scope filtering
# -------------------------------
def apply_scope_filter(subdomain_file, scope_file):
    if not scope_file or not os.path.exists(scope_file):
        return

    scope_domains = [
        l.strip().lstrip("*.") for l in open(scope_file).readlines() if l.strip()
    ]

    all_subs = open(subdomain_file).readlines()

    in_scope = [
        s for s in all_subs
        if any(s.strip().endswith(d) for d in scope_domains)
    ]

    with open(subdomain_file, "w") as f:
        f.writelines(in_scope)

    console.log(f"[green][+][/green] Scope: {len(in_scope)}/{len(all_subs)} in scope")


# -------------------------------
# Banner
# -------------------------------
BANNER = """
██████╗ ███████╗ ██████╗ ██████╗ ███╗  ██╗██╗  ██╗██╗████████╗
██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗ ██║██║ ██╔╝██║╚══██╔══╝
██████╔╝█████╗  ██║     ██║   ██║██╔██╗██║█████╔╝ ██║   ██║
██╔══██╗██╔══╝  ██║     ██║   ██║██║╚████║██╔═██╗ ██║   ██║
██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚███║██║  ██╗██║   ██║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚══╝╚═╝  ╚═╝╚═╝   ╚═╝
          Automated Recon Pipeline | by Abin A
"""


# -------------------------------
# Output directory
# -------------------------------
def create_output_dir(domain, custom_dir=None):
    if custom_dir:
        path = custom_dir
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"output/{domain}_{ts}"

    os.makedirs(path, exist_ok=True)
    console.log(f"[green][+][/green] Output: {path}")
    return path


def main():
    print(BANNER)

    check_tools()

    parser = argparse.ArgumentParser(description="ReconKit by Abin A")

    parser.add_argument("-d", "--domain", required=True, help="Target domain")

    parser.add_argument("--skip-amass", action="store_true")
    parser.add_argument("--skip-js", action="store_true")
    parser.add_argument("--quick", action="store_true")

    parser.add_argument("--skip-scan", action="store_true", help="Skip Nuclei scan")
    parser.add_argument("--scope", help="Scope file")

    # CUSTOM DIR FEATURE
    parser.add_argument("--output-dir", help="Custom output directory")

    args = parser.parse_args()

    domain = args.domain

    # USE CUSTOM DIR
    out = create_output_dir(domain, args.output_dir)

    console.print(f"\n[bold cyan]Target:[/bold cyan] {domain}\n")

    # Phase 1
    subdomains.run_enum(domain, out, skip_amass=args.skip_amass)

    apply_scope_filter(f"{out}/all_subdomains.txt", args.scope)

    # Phase 2
    probing.probe(out)

    # Phase 3
    if not args.quick:
        crawling.crawl(domain, out, skip_js=args.skip_js)

        if not args.skip_scan:
            scanning.scan(out)

    # Phase 4
    reporting.generate(domain, out)


if __name__ == "__main__":
    main()