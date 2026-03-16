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
    count = 0
    if os.path.exists(f"{out}/live_hosts.txt"):
        count = len(open(f"{out}/live_hosts.txt").readlines())
    console.log(f"[bold green][+] Live hosts found: {count}")
    return count
