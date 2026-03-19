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
def probe(out):
    console.rule("[bold yellow]Phase 2 - Live Host Probing")
    run(f"httpx -l {out}/all_subdomains.txt -silent "
        f"-status-code -title -tech-detect -p 80,443 -mc 200,301,302,403 "
        f"-o {out}/live_hosts.txt")
    run(f"httpx -l {out}/all_subdomains.txt "
        f"-silent -mc 404 "
        f"-o {out}/potential_takeover.txt"
    )
    takeover_count = 0
    if os.path.exists(f"{out}/potential_takeover.txt"):
        takeover_count = len(open(f"{out}/potential_takeover.txt").readlines())
    if takeover_count > 0:
        console.log(f"[red][!] Takeover candidates: {takeover_count}[/red]")
    else:
        console.log("[green][+][/green] No takeover candidates")
    count = 0
    if os.path.exists(f"{out}/live_hosts.txt"):
        count = len(open(f"{out}/live_hosts.txt").readlines())
    console.log(f"[bold green][+] Live hosts found: {count}")
    return count
