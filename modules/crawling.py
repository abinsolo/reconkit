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
def crawl(domain, out, skip_js=False):
    console.rule("[bold yellow]Phase 3 - URL & Parameter Discovery")
    run(f"gau {domain} --blacklist png,jpg,gif,svg,woff,css > {out}/gau_urls.txt")
    console.log("[green][+][/green] GAU done")
    run(f"echo {domain} | waybackurls > {out}/wayback_urls.txt")
    console.log("[green][+][/green] Waybackurls done")
    run(f"katana -list {out}/live_hosts.txt -silent -jc -d 3 -o {out}/katana_urls.txt")
    console.log("[green][+][/green] Katana done")
    run(f"cat {out}/live_hosts.txt | hakrawler -subs > {out}/hakrawler_urls.txt")
    console.log("[green][+][/green] Hakrawler done") 
    run(f"cat {out}/gau_urls.txt {out}/wayback_urls.txt "
        f"{out}/katana_urls.txt {out}/hakrawler_urls.txt "
        f"2>/dev/null | sort -u > {out}/all_urls.txt")
    run(f"cat {out}/all_urls.txt | grep -E '\.js$|/api/|/admin|/graphql|/v1/|/v2/' "
        f"> {out}/juicy_endpoints.txt")
    console.log("[green][+][/green] Juicy endpoints extracted")
    run(f"paramspider -d {domain} -o {out}/params.txt")
    console.log("[green][+][/green] ParamSpider done")
    run(f"arjun -i {out}/live_hosts.txt --stable -oJ {out}/arjun_params.json")
    console.log("[green][+][/green] Arjun done")
    if not skip_js:
        js_file = f"{out}/js_files.txt"
        run(f"cat {out}/all_urls.txt | grep '\.js$' | sort -u > {js_file}")
        run(f"cat {js_file} | while read url; do "
            f"python3 ~/LinkFinder/linkfinder.py -i $url -o cli 2>/dev/null; "
            f"done > {out}/linkfinder_output.txt")
        console.log("[green][+][/green] LinkFinder JS analysis done")
    url_count = len(open(f"{out}/all_urls.txt").readlines()) if os.path.exists(f"{out}/all_urls.txt") else 0
    juicy_count = len(open(f"{out}/juicy_endpoints.txt").readlines()) if os.path.exists(f"{out}/juicy_endpoints.txt") else 0
    console.log(f"[bold green][+] Total URLs: {url_count} | Juicy: {juicy_count}")
    return url_count, juicy_count 
