import os, datetime
from rich.console import Console
from rich.panel import Panel
console = Console()
def safe_count(f):
    try: return len(open(f).readlines())
    except: return 0
def generate(domain, out):
    console.rule("[bold yellow]Phase 4 - Report Generation")
    subs  = safe_count(f"{out}/all_subdomains.txt")
    live  = safe_count(f"{out}/live_hosts.txt")
    urls  = safe_count(f"{out}/all_urls.txt")
    juicy = safe_count(f"{out}/juicy_endpoints.txt")
    report = f"""# ReconKit Report
**Target:** {domain}
**Date:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
## Summary
| Phase | Result |
|-------|--------|
| Subdomains Found | {subs} |
| Live Hosts | {live} |
| Total URLs | {urls} |
| Juicy Endpoints | {juicy} |
## Output Files
| File | Description |
|------|-------------|
| all_subdomains.txt | All discovered subdomains |
| live_hosts.txt | Live hosts with status + tech |
| all_urls.txt | All discovered URLs |
| juicy_endpoints.txt | API, admin, GraphQL endpoints |
| params.txt | Parameterised URLs |
| arjun_params.json | Hidden parameters |
| linkfinder_output.txt | Endpoints from JS files |

## Next Steps
1. Review juicy_endpoints.txt for GraphQL introspection
2. Check arjun_params.json for IDOR attack surface
3. Run parameterised URLs through Dalfox for XSS
4. Test auth endpoints for JWT weaknesses using jwt_tool
5. Manually check API endpoints for Business Logic flaws
"""
    with open(f"{out}/REPORT.md", "w") as f:
        f.write(report)
    console.print(Panel.fit(
        f"[bold green]Recon Complete![/bold green]\n\n"
        f"Target: {domain}\nSubdomains: {subs}\nLive: {live}\n"
        f"URLs: {urls}\nJuicy: {juicy}\n\n"
        f"[yellow]Report -> {out}/REPORT.md[/yellow]",
        title="[bold cyan]ReconKit[/bold cyan]", border_style="green"
    ))

