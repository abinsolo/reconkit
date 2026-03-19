import subprocess, os
from rich.console import Console
console = Console()

def run(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        console.log(f"[red]Error:[/red] {e}")
        return ""

def run_enum(domain, out, skip_amass=False):
    console.rule("[bold yellow]Phase 1 - Subdomain Enumeration")
    run(f"subfinder -d {domain} -silent -o {out}/subfinder.txt")
    console.log("[green][+][/green] Subfinder done")
    run(f"assetfinder --subs-only {domain} > {out}/assetfinder.txt")
    console.log("[green][+][/green] Assetfinder done")
    if not skip_amass:
        run(f"amass enum -d {domain} -passive -o {out}/amass.txt")
        console.log("[green][+][/green] Amass done")
    run(f"cat {out}/subfinder.txt {out}/assetfinder.txt {out}/amass.txt "
        f"2>/dev/null | sort -u > {out}/all_subdomains.txt")
    count = 0
    if os.path.exists(f"{out}/all_subdomains.txt"):
        count = len(open(f"{out}/all_subdomains.txt").readlines())
    console.log(f"[bold green][+] Unique subdomains: {count}")
    return count
