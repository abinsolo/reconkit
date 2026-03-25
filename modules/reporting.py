import os, datetime
from rich.console import Console
from rich.panel import Panel
console = Console()

def safe_count(f):
    try:
        return len(open(f).readlines())
    except:
        return 0

def generate(domain, out):
    console.rule("[bold yellow]Phase 4 - Report Generation")
    subs    = safe_count(f"{out}/all_subdomains.txt")
    live    = safe_count(f"{out}/live_hosts.txt")
    urls    = safe_count(f"{out}/all_urls.txt")
    juicy   = safe_count(f"{out}/juicy_endpoints.txt")
    secrets = safe_count(f"{out}/js_secrets.txt")
    takeover= safe_count(f"{out}/potential__takeover.txt")
    nuclei  = safe_count(f"{out}/nuclei_findings.txt")
    api_findings= max(0, safe_count(f"{out}/api_surface.md") - 1)
    triage_tier  = ''
    if os.path.exists(f'{out}/TRIAGE_REPORT.md'):
        content = open(f'{out}/TRIAGE_REPORT.md').read()
        for t in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            if t in content:
                triage_tier = t
                break
    

    report = f"""# ReconKit Report
**Target:** {domain}
**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
| Phase | Result |
|-------|--------|
| Subdomains Found | {subs} |
| Live Hosts | {live} |
| Total URLs | {urls} |
| Juicy Endpoints | {juicy} |
| JS Secrets Found | {secrets} |
| Takeover Candidtes | {takeover} |
| Nuclei Findings | {nuclei} |
| API Endpoints Mapped | {api_findings} |

## Next Steps

### Immediate — Check These First
1. Review `js_secrets.json` — verify each secret is real and not a test key
2. Investigate `potential_takeover.txt` — check each CNAME manually for unclaimed services
3. Review `nuclei_findings.txt` — manually verify every HIGH and CRITICAL finding

### API Attack Surface
4. Open `api_surface.json` — check for GraphQL introspection enabled endpoints
5. Run schema enumeration on any enabled GraphQL endpoint
6. Test REST endpoints in `api_surface.md` for unauthenticated access
7. Check OpenAPI specs for undocumented or deprecated endpoints

### Parameter Testing
8. Run Dalfox on `param_urls.txt` for XSS
9. Check `arjun_params.json` for IDOR attack surface — enumerate object IDs
10. Test auth endpoints with `jwt_tool` for JWT weaknesses

### Manual Review
11. Read `juicy_endpoints.txt` — manually test each /admin, /graphql, /api endpoint
12. Check `s3_candidates.txt` through S3Scanner for public read/write access
13. Look for business logic flaws on order, loyalty, and payment endpoints

### Reporting
14. For any confirmed finding — document full reproduction steps before reporting
15. Check program scope in `scope_intigriti.txt` or `scope_hackerone.txt` before submitting
"""
    with open(f"{out}/REPORT.md", "w") as f:
        f.write(report)

    console.print(Panel.fit(
        f"[bold green]Recon Complete![/bold green]\n\n"
        f"Target: {domain}\nSubdomains: {subs}\nLive: {live}\n"
        f"URLs: {urls}\nJuicy: {juicy}\n\n"
        f"[yellow]Report -> {out}/REPORT.md[/yellow]",
        title="[bold cyan]ReconKit[/bold cyan]",
        border_style="green"
    ))

    takeover = safe_count(f"{out}/potential_takeover.txt")
    nuclei   = safe_count(f"{out}/nuclei_findings.txt")
    generate_html(domain, out, subs, live, urls, juicy, takeover, nuclei, secrets, api_findings, triage_tier)


def generate_html(domain, out, subs, live, urls, juicy, takeover=0, nuclei=0, secrets=0, api_findings=0, triage_tier=''):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def badge(n, w=5, c=20):
        if n == 0: return "#4ade80"
        if n < w:  return "#fbbf24"
        return "#f87171"

    html = (
        "<!DOCTYPE html><html><head>"
        "<title>ReconKit Report</title>"
        "<style>"
        "body{background:#050810;color:#e2e8f0;font-family:monospace;padding:2rem}"
        "h1{color:#22d3ee} h2{color:#fbbf24}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0}"
        "th{background:#111827;color:#22d3ee;padding:10px;border:1px solid #1e2d45}"
        "td{padding:10px;border:1px solid #1e2d45}"
        "</style></head><body>"
        f"<h1>ReconKit Report</h1>"
        f"<p><b>Target:</b> {domain} | <b>Date:</b> {date}</p>"
        "<h2>Summary</h2><table>"
        "<tr><th>Phase</th><th>Count</th><th>Status</th></tr>"
        f"<tr><td>Subdomains</td><td>{subs}</td><td style='color:#4ade80'>&#10003;</td></tr>"
        f"<tr><td>Live Hosts</td><td>{live}</td><td style='color:#4ade80'>&#10003;</td></tr>"
        f"<tr><td>URLs</td><td>{urls}</td><td style='color:#4ade80'>&#10003;</td></tr>"
        f"<tr><td>Juicy Endpoints</td><td>{juicy}</td>"
        f"<tr><td>JS Secrets</td><td>{secrets}</td>"
        f"<td style='color:{badge(secrets,1,5)}'>"
        f"{'INVESTIGATE' if secrets > 0 else 'Clean'}</td></tr>"
        f"<td style='color:{badge(juicy)}'>{'Review' if juicy > 0 else 'Clean'}</td></tr>"
        f"<tr><td>Takeover Candidates</td><td>{takeover}</td>"
        f"<td style='color:{badge(takeover,1,5)}'>{'INVESTIGATE' if takeover > 0 else 'Clean'}</td></tr>"
        f"<tr><td>Nuclei Findings</td><td>{nuclei}</td>"
        f"<td style='color:{badge(nuclei,1,10)}'>{'FINDINGS' if nuclei > 0 else 'Clean'}</td></tr>"
        f"<tr><td>API Endpoints Mapped</td><td>{api_findings}</td>"
        f"<td style='color:{badge(api_findings,1,5)}'>"
        f"{'REVIEW' if api_findings > 0 else 'None found'}</td></tr>"
        "</table></body></html>"
    )

    with open(f"{out}/REPORT.html", "w") as f:
        f.write(html)
    console.log(f"[green][+][/green] HTML report -> {out}/REPORT.html")
