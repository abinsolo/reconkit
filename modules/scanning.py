import subprocess, os
from rich.console import Console
console = Console()

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return r.stdout.strip()
    except Exception as e:
        console.log(f'[red]Error:[/red] {e}')
        return ''

def scan(out):
    console.rule('[bold yellow]Phase 5 - Vulnerability Scanning')
    if not os.path.exists(f'{out}/live_hosts.txt'):
        console.log('[red][!] live_hosts.txt not found — skipping[/red]')
        return 0
    run(
        f'nuclei -l {out}/live_hosts.txt '
        f'-tags cve,misconfig,exposure,takeover '
        f'-severity medium,high,critical '
        f'-silent -o {out}/nuclei_findings.txt'
    )
    count = len(open(f'{out}/nuclei_findings.txt').readlines()) \
            if os.path.exists(f'{out}/nuclei_findings.txt') else 0
    console.log(f'[bold green][+] Nuclei findings: {count}')
    return count










































